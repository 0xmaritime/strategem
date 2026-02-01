"""Strategem Core - Analysis Orchestrator"""

import uuid
from .models import (
    ProblemContext,
    AnalysisResult,
    PorterAnalysis,
    SystemsDynamicsAnalysis,
)
from .llm_layer import LLMInferenceLayer, LLMError
from .config import config


class AnalysisOrchestrator:
    """Orchestrates the analysis workflow"""

    def __init__(self):
        self.llm = LLMInferenceLayer()

    def run_porter_analysis(self, context: ProblemContext) -> tuple:
        """
        Run Porter's Five Forces analysis.

        Returns:
            Tuple of (analysis_result, error_message)
        """
        try:
            result = self.llm.run_analysis(
                prompt_name="porter",
                context=context.structured_content or context.raw_content,
                response_model=PorterAnalysis,
                max_retries=config.MAX_RETRIES,
            )
            return result, None
        except LLMError as e:
            return None, str(e)

    def run_systems_analysis(self, context: ProblemContext) -> tuple:
        """
        Run Systems Dynamics analysis.

        Returns:
            Tuple of (analysis_result, error_message)
        """
        try:
            result = self.llm.run_analysis(
                prompt_name="systems_dynamics",
                context=context.structured_content or context.raw_content,
                response_model=SystemsDynamicsAnalysis,
                max_retries=config.MAX_RETRIES,
            )
            return result, None
        except LLMError as e:
            return None, str(e)

    def run_full_analysis(self, context: ProblemContext) -> AnalysisResult:
        """
        Run complete analysis with both frameworks.

        Args:
            context: The problem context to analyze

        Returns:
            Complete analysis result
        """
        analysis_id = str(uuid.uuid4())

        # Run Porter analysis
        porter_result, porter_error = self.run_porter_analysis(context)

        # Run Systems Dynamics analysis
        systems_result, systems_error = self.run_systems_analysis(context)

        return AnalysisResult(
            id=analysis_id,
            problem_context=context,
            porter_analysis=porter_result,
            systems_analysis=systems_result,
            porter_error=porter_error,
            systems_error=systems_error,
        )
