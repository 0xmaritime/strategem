"""Strategem Core - Analysis Orchestrator (V1 Compliant)"""

import uuid
from typing import List, Optional, Type
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
)
from .llm_layer import LLMInferenceLayer, LLMError
from .config import config


class AnalysisOrchestrator:
    """
    Orchestrates the analysis workflow using configurable frameworks.

    Frameworks are swappable without touching orchestration logic.
    Framework disagreement is a valid and expected system outcome.
    """

    def __init__(self):
        self.llm = LLMInferenceLayer()
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
                error_message=f"Unknown framework: {framework_name}",
            )

        framework = self._frameworks[framework_name]
        response_model = self._framework_models[framework_name]

        # V1 Compliance: Check if DecisionFocus is required but missing
        if framework.requires_decision_focus and not context.decision_focus:
            return FrameworkResult(
                framework_name=framework_name,
                success=False,
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
            return FrameworkResult(
                framework_name=framework_name, success=True, result=result
            )
        except LLMError as e:
            return FrameworkResult(
                framework_name=framework_name, success=False, error_message=str(e)
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

        # Run all specified frameworks independently
        framework_results = []
        porter_result = None
        systems_result = None
        porter_error = None
        systems_error = None

        for framework_name in frameworks:
            result = self.run_framework(framework_name, context)
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

        return AnalysisResult(
            id=analysis_id,
            problem_context=context,
            porter_analysis=porter_result,
            systems_analysis=systems_result,
            porter_error=porter_error,
            systems_error=systems_error,
            framework_results=framework_results,
        )

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
