"""Strategem Core - Analysis Orchestrator (V1 Compliant)"""

import uuid
from typing import List, Optional, Type, Tuple
from pydantic import BaseModel
from .models import (
    ProblemContext,
    AnalysisResult,
    PorterAnalysis,
    SystemsDynamicsAnalysis,
    AnalysisFramework,
    FrameworkResult,
    PORTER_FRAMEWORK,
    SYSTEMS_DYNAMICS_FRAMEWORK,
    DecisionFocus,
    DecisionFocusStatus,
    AnalyticalClaim,
    ClaimType,
    FrameworkExecutionStatus,
    AnalysisSufficiencySummary,
    DecisionBindingStatus,
    CoverageStatus,
    AnalysisSufficiencyStatus,
)
from .llm_layer import LLMInferenceLayer, LLMError
from .config import config
from .decision_focus_extractor import DecisionFocusExtractor


class AnalysisOrchestrator:
    """
    Orchestrates the analysis workflow using configurable frameworks.

    Frameworks are swappable without touching orchestration logic.
    Framework disagreement is a valid and expected system outcome.
    """

    def __init__(self):
        self.llm = LLMInferenceLayer()
        self.decision_focus_extractor = DecisionFocusExtractor()
        # Register default frameworks
        self._frameworks = {
            "porter": PORTER_FRAMEWORK,
            "systems_dynamics": SYSTEMS_DYNAMICS_FRAMEWORK,
        }
        # Map framework names to their response models
        self._framework_models = {
            "porter": PorterAnalysis,
            "systems_dynamics": SystemsDynamicsAnalysis,
        }

    def validate_decision_focus(
        self, context: ProblemContext
    ) -> Tuple[DecisionFocusStatus, Optional[DecisionFocus]]:
        """
        Validate or extract decision focus from problem context.

        V1 Requirement: Every analysis run must have a decision focus with:
        - a decision_question
        - >=2 options
        - a bounded decision_scope

        Args:
            context: The problem context to validate

        Returns:
            Tuple of (status, decision_focus)
            - status: EXPLICIT, DERIVED, or INSUFFICIENT
            - decision_focus: DecisionFocus object if EXPLICIT or DERIVED, None if INSUFFICIENT
        """
        return self.decision_focus_extractor.extract(context)

    def validate_claims_option_binding(
        self, claims: List[AnalyticalClaim], options: List[str]
    ) -> List[AnalyticalClaim]:
        """
        Validate and enforce claim-option binding rules.

        V1 Requirements:
        - If claim_type = option_specific → exactly 1 option required
        - If comparative → >=2 options required
        - If system_level → explicitly labeled "all"

        Invalid claims are either rejected or reclassified.

        Args:
            claims: List of claims to validate
            options: List of valid decision options

        Returns:
            List of valid claims only
        """
        valid_claims = []
        rejected_claims = []

        for claim in claims:
            claim_type = claim.claim_type
            applicable_options = (
                claim.applicable_options if claim.applicable_options else []
            )

            if claim_type == ClaimType.OPTION_SPECIFIC:
                if len(applicable_options) != 1:
                    rejected_claims.append(
                        (claim, "option_specific claims must have exactly 1 option")
                    )
                    continue

            elif claim_type == ClaimType.COMPARATIVE:
                if len(applicable_options) < 2:
                    rejected_claims.append(
                        (claim, "comparative claims must have >=2 options")
                    )
                    continue

            elif claim_type == ClaimType.SYSTEM_LEVEL:
                if applicable_options != ["all"]:
                    rejected_claims.append(
                        (claim, "system_level claims must use ['all']")
                    )
                    continue

            valid_claims.append(claim)

        return valid_claims

    def validate_framework_sufficiency(
        self, framework_result: FrameworkResult, context: ProblemContext
    ) -> FrameworkResult:
        """
        Validate framework execution sufficiency.

        V1 Requirement: A framework is successful ONLY if it produces at least one:
        - option-specific claim
        - comparative claim
        - system-level constraint that affects decision space

        Otherwise, it MUST be marked insufficient.

        Args:
            framework_result: The framework result to validate
            context: The problem context

        Returns:
            FrameworkResult with updated execution_status
        """
        if not framework_result.success:
            return FrameworkResult(
                framework_name=framework_result.framework_name,
                success=False,
                execution_status=FrameworkExecutionStatus.FAILED,
                execution_reason=framework_result.error_message,
            )

        # Check if framework produced any meaningful output
        claims = framework_result.claims
        valid_claims = self.validate_claims_option_binding(
            claims, context.decision_focus.options if context.decision_focus else []
        )

        if not valid_claims:
            # No valid claims produced
            return FrameworkResult(
                framework_name=framework_result.framework_name,
                success=True,
                result=framework_result.result,
                execution_status=FrameworkExecutionStatus.INSUFFICIENT,
                execution_reason="Framework produced no valid claims affecting the decision space",
                claims=[],
            )

        # Framework produced at least one valid claim
        framework_result.claims = valid_claims
        framework_result.execution_status = FrameworkExecutionStatus.SUCCESSFUL

        return framework_result

    def compute_analysis_sufficiency(
        self, result: AnalysisResult
    ) -> AnalysisSufficiencySummary:
        """
        Compute analysis sufficiency summary.

        V1 Requirement: Descriptive summary of completeness without evaluation.

        Args:
            result: The analysis result to evaluate

        Returns:
            AnalysisSufficiencySummary describing completeness
        """
        # Decision binding status
        decision_binding = DecisionBindingStatus.INSUFFICIENT
        if result.problem_context.decision_focus:
            decision_binding = DecisionBindingStatus.EXPLICIT

        # Option coverage
        option_coverage = CoverageStatus.COMPLETE
        if result.problem_context.decision_focus:
            options = result.problem_context.decision_focus.options
            # Check if each option has at least one claim
            option_claim_map = {opt: False for opt in options}

            all_claims = []
            for fw_result in result.framework_results:
                all_claims.extend(fw_result.claims)

            for claim in all_claims:
                for opt in claim.applicable_options:
                    if opt in option_claim_map:
                        option_claim_map[opt] = True

            uncovered_options = [
                opt for opt, covered in option_claim_map.items() if not covered
            ]
            if uncovered_options:
                option_coverage = CoverageStatus.PARTIAL

        # Framework coverage
        framework_coverage = CoverageStatus.COMPLETE
        if result.framework_results:
            successful_frameworks = sum(
                1
                for fw in result.framework_results
                if fw.execution_status == FrameworkExecutionStatus.SUCCESSFUL
            )
            total_frameworks = len(result.framework_results)

            if successful_frameworks < total_frameworks:
                framework_coverage = CoverageStatus.PARTIAL

        # Overall status
        if decision_binding == DecisionBindingStatus.INSUFFICIENT:
            overall_status = AnalysisSufficiencyStatus.EXPLORATORY_ONLY
        elif (
            option_coverage == CoverageStatus.PARTIAL
            or framework_coverage == CoverageStatus.PARTIAL
        ):
            overall_status = AnalysisSufficiencyStatus.CONSTRAINED
        else:
            overall_status = AnalysisSufficiencyStatus.SUFFICIENT

        return AnalysisSufficiencySummary(
            decision_binding=decision_binding,
            option_coverage=option_coverage,
            framework_coverage=framework_coverage,
            overall_status=overall_status,
        )

    def register_framework(
        self, name: str, framework: AnalysisFramework, response_model: Type[BaseModel]
    ):
        """
        Register a new analytical framework.

        This enables extending the system without modifying orchestration logic.

        Args:
            name: Framework identifier
            framework: The framework configuration
            response_model: Pydantic model for parsing responses
        """
        self._frameworks[name] = framework
        self._framework_models[name] = response_model

    def run_framework(
        self, framework_name: str, context: ProblemContext
    ) -> FrameworkResult:
        """
        Run a single analytical framework.

        Args:
            framework_name: Name of the framework to run
            context: The problem context to analyze

        Returns:
            FrameworkResult containing success/failure and parsed result
        """
        if framework_name not in self._frameworks:
            return FrameworkResult(
                framework_name=framework_name,
                success=False,
                execution_status=FrameworkExecutionStatus.FAILED,
                execution_reason=f"Unknown framework: {framework_name}",
                error_message=f"Unknown framework: {framework_name}",
            )

        framework = self._frameworks[framework_name]
        response_model = self._framework_models[framework_name]

        # V1 Compliance: Check if DecisionFocus is required but missing
        if framework.requires_decision_focus and not context.decision_focus:
            return FrameworkResult(
                framework_name=framework_name,
                success=False,
                execution_status=FrameworkExecutionStatus.FAILED,
                execution_reason=f"Framework '{framework_name}' requires DecisionFocus but none was provided. "
                f"Please specify: decision_question, decision_type, and options.",
                error_message=f"Framework '{framework_name}' requires DecisionFocus but none was provided. "
                f"Please specify: decision_question, decision_type, and options.",
            )

        try:
            result = self.llm.run_analysis(
                prompt_name=framework.prompt_template.replace(".txt", ""),
                context=context.structured_content or context.raw_content,
                response_model=response_model,
                max_retries=config.MAX_RETRIES,
                decision_focus=context.decision_focus,
            )

            # Extract claims from result if available
            claims = []
            if hasattr(result, "claims"):
                claims = result.claims
            elif hasattr(result, "option_aware_claims"):
                claims = result.option_aware_claims

            # Set default execution status (will be validated later)
            return FrameworkResult(
                framework_name=framework_name,
                success=True,
                result=result,
                execution_status=FrameworkExecutionStatus.SUCCESSFUL,
                claims=claims,
            )
        except LLMError as e:
            return FrameworkResult(
                framework_name=framework_name,
                success=False,
                execution_status=FrameworkExecutionStatus.FAILED,
                execution_reason=str(e),
                error_message=str(e),
            )

    def run_analysis_with_frameworks(
        self,
        context: ProblemContext,
        frameworks: List[str],
    ) -> AnalysisResult:
        """
        Run analysis with specified frameworks.

        This is the primary V1 method - frameworks are explicitly specified
        and can be swapped without code changes.

        Args:
            context: The problem context to analyze
            frameworks: List of framework names to apply

        Returns:
            Complete analysis result with all framework outputs
        """
        analysis_id = str(uuid.uuid4())

        # V1: Validate decision focus
        decision_status, decision_focus = self.validate_decision_focus(context)

        # If decision focus insufficient, add it to context or abort
        if decision_status == DecisionFocusStatus.INSUFFICIENT:
            # V1 requirement: abort or downgrade to exploratory_predecision
            # For now, we'll downgrade
            context.decision_focus = None

        # Run all specified frameworks independently
        framework_results = []
        porter_result = None
        systems_result = None
        porter_error = None
        systems_error = None

        for framework_name in frameworks:
            result = self.run_framework(framework_name, context)

            # V1: Validate framework sufficiency
            result = self.validate_framework_sufficiency(result, context)
            framework_results.append(result)

            # Maintain backward compatibility
            if framework_name == "porter":
                if result.success:
                    porter_result = result.result
                else:
                    porter_error = result.error_message
            elif framework_name == "systems_dynamics":
                if result.success:
                    systems_result = result.result
                else:
                    systems_error = result.error_message

        analysis_result = AnalysisResult(
            id=analysis_id,
            problem_context=context,
            porter_analysis=porter_result,
            systems_analysis=systems_result,
            porter_error=porter_error,
            systems_error=systems_error,
            framework_results=framework_results,
        )

        # V1: Compute analysis sufficiency summary
        analysis_sufficiency = self.compute_analysis_sufficiency(analysis_result)
        analysis_result.analysis_sufficiency = analysis_sufficiency

        return analysis_result

    def run_porter_analysis(self, context: ProblemContext) -> tuple:
        """
        Run Porter's Five Forces analysis.

        LEGACY METHOD: Maintained for backward compatibility.
        New code should use run_framework() or run_analysis_with_frameworks().

        Returns:
            Tuple of (analysis_result, error_message)
        """
        result = self.run_framework("porter", context)
        if result.success:
            return result.result, None
        else:
            return None, result.error_message

    def run_systems_analysis(self, context: ProblemContext) -> tuple:
        """
        Run Systems Dynamics analysis.

        LEGACY METHOD: Maintained for backward compatibility.
        New code should use run_framework() or run_analysis_with_frameworks().

        Returns:
            Tuple of (analysis_result, error_message)
        """
        result = self.run_framework("systems_dynamics", context)
        if result.success:
            return result.result, None
        else:
            return None, result.error_message

    def run_full_analysis(
        self, context: ProblemContext, frameworks: Optional[List[str]] = None
    ) -> AnalysisResult:
        """
        Run complete analysis with specified frameworks.

        Args:
            context: The problem context to analyze
            frameworks: List of framework names to apply (default: ["porter", "systems_dynamics"])

        Returns:
            Complete analysis result
        """
        if frameworks is None:
            frameworks = ["porter", "systems_dynamics"]

        return self.run_analysis_with_frameworks(context, frameworks)

    def list_available_frameworks(self) -> List[AnalysisFramework]:
        """List all registered analytical frameworks."""
        return list(self._frameworks.values())
