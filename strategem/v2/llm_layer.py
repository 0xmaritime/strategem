"""Strategem V2 - LLM Inference Layer (V2 Specific)

This layer wraps the core LLM client and handles V2-specific prompt formatting.
V2: Decision is REQUIRED, not optional. All frameworks are option-aware.
"""

from typing import Optional, Type
from pathlib import Path

from strategem.core import LLMInferenceClient, LLMError, config


class V2LLMInferenceLayer:
    """
    V2-specific LLM inference layer.

    Wraps the core LLM client and handles V2-specific:
    - Decision context injection (REQUIRED)
    - Option-aware prompt formatting
    - Framework contract enforcement
    """

    def __init__(self):
        """Initialize V2 LLM layer with core client"""
        self.core_client = LLMInferenceClient(
            api_key=config.OPENROUTER_API_KEY,
            base_url=config.OPENROUTER_BASE_URL,
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
        )

        self.prompts_dir = config.PROMPTS_DIR

    def _load_system_prompt(self) -> str:
        """Load V2 system prompt (same as V1 for now)"""
        system_prompt_path = self.prompts_dir / "system.txt"
        return system_prompt_path.read_text()

    def _load_user_prompt(
        self,
        prompt_name: str,
        context: str,
        decision_question: str,
        decision_type: str,
        options: list,
    ) -> str:
        """
        Load and format V2 user prompt template.

        V2: Decision is REQUIRED. Options are REQUIRED.
        All frameworks must be option-aware.
        """
        prompt_path = self.prompts_dir / f"{prompt_name}.txt"
        template = prompt_path.read_text()

        formatted = template.replace("{context}", context)
        formatted = formatted.replace("{decision_question}", decision_question)
        formatted = formatted.replace("{decision_type}", decision_type)
        formatted = formatted.replace("{options}", ", ".join(options))

        target_title = context.split("\n")[0][:50] if context else "Target System"
        formatted = formatted.replace("{target_system_title}", target_title)

        return formatted

    def run_analysis(
        self,
        prompt_name: str,
        context: str,
        decision_question: str,
        decision_type: str,
        options: list,
        response_model: Type,
        max_retries: int = 1,
    ) -> Type:
        """
        Run V2 analysis using specified prompt template.

        V2: Decision context is REQUIRED. Options are REQUIRED.

        Args:
            prompt_name: Name of prompt template
            context: The problem context to analyze
            decision_question: The decision question
            decision_type: Type of decision
            options: List of options being analyzed
            response_model: Pydantic model for parsing response
            max_retries: Number of retries on failure

        Returns:
            Parsed response as specified model type
        """
        system_prompt = self._load_system_prompt()
        user_prompt = self._load_user_prompt(
            prompt_name, context, decision_question, decision_type, options
        )

        try:
            return self.core_client.run_analysis(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=response_model,
                max_retries=max_retries,
            )
        except LLMError as e:
            raise LLMError(f"V2 analysis failed: {e}")


__all__ = ["V2LLMInferenceLayer"]
