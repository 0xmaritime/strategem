"""Strategem V2 - Analysis Orchestrator (V2 Compliant)"""

import uuid
from typing import List, Optional, Type, Dict, Any

from .models import (
    Decision,
    Option,
    AnalyticalClaim,
    FrameworkResult,
    AnalysisResult,
    FrameworkContract,
    FrameworkExecutionStatus,
    PorterAnalysisV2,
    SystemsDynamicsAnalysisV2,
    OptionEffect,
    Assumption,
    Unknown,
)
from .llm_layer import V2LLMInferenceLayer, LLMError
from strategem.core import config, generate_id


class V2AnalysisOrchestrator:
    """
    Orchestrates V2 analysis workflow.

    V2 Requirements:
    - Decision context is REQUIRED (no inference)
    - All frameworks must be option-aware
    - All claims must specify affected_options
    - Framework disagreement is valid and expected
    """

    def __init__(self):
        self.llm = V2LLMInferenceLayer()
        self._frameworks: Dict[str, FrameworkContract] = {}
        self._framework_models: Dict[str, Type] = {}

        self._register_default_frameworks()

    def _register_default_frameworks(self):
        """Register default V2 frameworks"""
        from .frameworks.porter_v2 import PORTER_V2_FRAMEWORK
        from .frameworks.systems_dynamics_v2 import SYSTEMS_DYNAMICS_V2_FRAMEWORK

        self.register_framework(PORTER_V2_FRAMEWORK, PorterAnalysisV2)
        self.register_framework(
            SYSTEMS_DYNAMICS_V2_FRAMEWORK, SystemsDynamicsAnalysisV2
        )

    def register_framework(self, framework: FrameworkContract, response_model: Type):
        """
        Register a V2 analytical framework.

        V2: Framework must adhere to FrameworkContract.
        Must be option-aware and decision-bound.
        """
        self._frameworks[framework.name] = framework
        self._framework_models[framework.name] = response_model

    def validate_decision_context(
        self, decision: Decision, options: List[Option]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate decision context.

        V2: Decision is REQUIRED. Options are REQUIRED.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not decision.decision_question:
            return False, "Decision question is required in V2"

        if not options or len(options) < 2:
            return False, "V2 requires at least 2 options to analyze"

        return True, None

    def validate_claim_option_awareness(
        self, claim: AnalyticalClaim, valid_options: List[str]
    ) -> bool:
        """
        Validate that a claim is option-aware.

        V2: All claims MUST specify affected_options.
        "all" or empty affected_options is invalid.
        """
        if not claim.affected_options:
            return False

        if len(claim.affected_options) == 1 and claim.affected_options[0] == "all":
            return False

        for option in claim.affected_options:
            if option not in valid_options:
                return False

        return True

    def run_framework(
        self,
        framework_name: str,
        decision: Decision,
        options: List[Option],
        context: str,
    ) -> FrameworkResult:
        """
        Run a single V2 framework.

        V2: Decision context is required. Framework must be option-aware.
        """
        if framework_name not in self._frameworks:
            return FrameworkResult(
                framework_name=framework_name,
                success=False,
                execution_status=FrameworkExecutionStatus.FAILED,
                execution_reason=f"Unknown framework: {framework_name}",
            )

        framework = self._frameworks[framework_name]
        response_model = framework.response_model

        option_names = [opt.name for opt in options]

        try:
            result = self.llm.run_analysis(
                prompt_name=framework.prompt_template.replace(".txt", ""),
                context=context,
                decision_question=decision.decision_question,
                decision_type=decision.decision_type.value,
                options=option_names,
                response_model=response_model,
                max_retries=config.MAX_RETRIES,
            )

            # Extract claims and other data with validation error handling
            claims = []
            assumptions = []
            unknowns = []

            try:
                if hasattr(result, "option_aware_claims"):
                    claims = result.option_aware_claims
                elif hasattr(result, "option_aware_aims"):
                    claims = result.option_aware_aims
            except Exception as e:
                pass

            try:
                if hasattr(result, "shared_assumptions"):
                    assumptions.extend(result.shared_assumptions)
            except Exception as e:
                pass

            try:
                if hasattr(result, "shared_unknowns"):
                    unknowns.extend(result.shared_unknowns)
            except Exception as e:
                pass

            return FrameworkResult(
                framework_name=framework_name,
                success=True,
                execution_status=FrameworkExecutionStatus.SUCCESSFUL,
                result=result,
                claims=claims,
                assumptions=assumptions,
                unknowns=unknowns,
            )

        except Exception as e:
            return FrameworkResult(
                framework_name=framework_name,
                success=False,
                execution_status=FrameworkExecutionStatus.FAILED,
                execution_reason=str(e),
            )

    def run_full_analysis(
        self,
        decision: Decision,
        options: List[Option],
        context: str,
        frameworks: Optional[List[str]] = None,
    ) -> AnalysisResult:
        """
        Run complete V2 analysis.

        V2: Decision context is REQUIRED. Options are REQUIRED.
        All frameworks are option-aware.

        Args:
            decision: Decision context (REQUIRED in V2)
            options: List of options being analyzed (REQUIRED in V2)
            context: Problem context material
            frameworks: List of framework names to run (default: all registered)

        Returns:
            Complete V2 analysis result
        """
        analysis_id = generate_id()

        is_valid, error = self.validate_decision_context(decision, options)
        if not is_valid:
            raise ValueError(f"Invalid decision context: {error}")

        if frameworks is None:
            frameworks = list(self._frameworks.keys())

        option_names = [opt.name for opt in options]

        framework_results = []
        for framework_name in frameworks:
            result = self.run_framework(framework_name, decision, options, context)
            framework_results.append(result)

        from .tension_mapper import V2TensionMapper
        from .artefact_generator import V2ArtefactGenerator

        tension_mapper = V2TensionMapper()
        artefact_generator = V2ArtefactGenerator()

        tension_map = None
        if len(framework_results) >= 2:
            tension_map = tension_mapper.map_framework_tensions(framework_results)

        artefacts = artefact_generator.generate_all_artefacts(
            analysis_id, decision, options, framework_results, tension_map
        )

        sensitivity_triggers = artefact_generator.generate_sensitivity_triggers(
            framework_results
        )

        return AnalysisResult(
            analysis_id=analysis_id,
            decision=decision,
            options_analyzed=option_names,
            framework_results=framework_results,
            tension_map=tension_map,
            sensitivity_triggers=sensitivity_triggers,
        )

    def list_available_frameworks(self) -> List[FrameworkContract]:
        """List all registered V2 frameworks"""
        return list(self._frameworks.values())


__all__ = ["V2AnalysisOrchestrator"]
