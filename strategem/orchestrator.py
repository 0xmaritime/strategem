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

    def infer_decision_binding(
        self, context: ProblemContext
    ) -> Tuple[DecisionBindingStatus, Optional[DecisionFocus]]:
        """
        Infer decision binding status from problem context.

        V1: Decision Focus is inferred, not required.
        Structured decision-focus forms are optional hints, never epistemic authorities.

        Decision Context = PRESENT if ALL of following are true:
        1. Choice Intent is Present (verbs: choose, decide, defend, compare)
        2. Multiple Alternatives Exist (≥2 materially distinct options)
        3. Decision Ownership Exists (role, committee, or actor)

        Only when choice intent is genuinely unclear may we enter exploratory mode.

        Args:
            context: The problem context to analyze

        Returns:
            Tuple of (status, decision_focus)
            - status: DECISION_CONTEXT_PRESENT or GENUINELY_AMBIGUOUS
            - decision_focus: DecisionFocus object if inferred/present, None if ambiguous
        """
        # V1: Use the extractor directly
        decision_focus = self.decision_focus_extractor.extract(context)

        # Determine binding status
        if decision_focus:
            return DecisionBindingStatus.DECISION_CONTEXT_PRESENT, decision_focus
        else:
            return DecisionBindingStatus.GENUINELY_AMBIGUOUS, None

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
        Compute analysis sufficiency summary (V1).

        Allowed status values:
        - decision_relevant_reasoning_produced: Decision context present, analysis produced
        - decision_relevant_but_constrained: Decision context present but partial
        - exploratory_pre_decision: No decision context, exploratory only

        Args:
            result: The analysis result to evaluate

        Returns:
            AnalysisSufficiencySummary describing completeness
        """
        # Decision binding status (V1: use new enum values)
        decision_binding = DecisionBindingStatus.DECISION_CONTEXT_PRESENT
        if not result.problem_context.decision_focus:
            # No decision focus - exploratory mode
            decision_binding = DecisionBindingStatus.GENUINELY_AMBIGUOUS

        # Option coverage
        option_coverage = CoverageStatus.NOT_APPLICABLE
        if result.problem_context.decision_focus:
            options = result.problem_context.decision_focus.options
            if not options or len(options) == 0:
                option_coverage = CoverageStatus.NOT_APPLICABLE
            else:
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
                else:
                    option_coverage = CoverageStatus.COMPLETE

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

        # Overall status (V1: use new status values)
        if decision_binding == DecisionBindingStatus.GENUINELY_AMBIGUOUS:
            overall_status = AnalysisSufficiencyStatus.EXPLORATORY_PRE_DECISION
        elif (
            option_coverage == CoverageStatus.PARTIAL
            or framework_coverage == CoverageStatus.PARTIAL
        ):
            overall_status = AnalysisSufficiencyStatus.DECISION_RELEVANT_BUT_CONSTRAINED
        else:
            overall_status = (
                AnalysisSufficiencyStatus.DECISION_RELEVANT_REASONING_PRODUCED
            )

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

        V1: Frameworks MUST NOT block analysis due to missing forms.
        Decision Focus is inferred, not required.

        If a framework cannot meaningfully contribute:
        - It is marked as "non-contributory"
        - This is surfaced in limitations
        - Analysis does NOT halt

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

        # V1: Do NOT block frameworks for missing decision focus
        # Decision Focus is an optional hint, not a requirement
        # Frameworks may run with or without it, depending on context

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

        V1: This is the primary V1 method - frameworks are explicitly specified
        and can be swapped without code changes.

        Decision Focus is inferred, not required. Analysis runs unless genuinely ambiguous.

        Args:
            context: The problem context to analyze
            frameworks: List of framework names to apply

        Returns:
            Complete analysis result with all framework outputs
        """
        analysis_id = str(uuid.uuid4())

        # V1: Infer decision binding (not validate)
        decision_binding, decision_focus = self.infer_decision_binding(context)

        # V1: Add inferred decision focus to context if available
        # This is an optional enhancement, not a requirement
        if decision_focus and not context.decision_focus:
            context.decision_focus = decision_focus
        else:
            decision_binding = DecisionBindingStatus.GENUINELY_AMBIGUOUS

        # V1: Run all specified frameworks independently
        # Do NOT block analysis due to missing forms or informal phrasing
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
