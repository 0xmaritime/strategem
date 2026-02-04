"""Strategem V1 - LLM Layer (V1 Specific)

This layer wraps the core LLM client and handles V1-specific prompt formatting,
such as DecisionFocus injection. The mechanical LLM operations are delegated
to strategem.core.LLMInferenceClient.
"""

from typing import Optional, Type, TypeVar
from pathlib import Path
from pydantic import BaseModel

from strategem.core import LLMInferenceClient, LLMError, config


T = TypeVar("T", bound=BaseModel)


class V1LLMInferenceLayer:
    """
    V1-specific LLM inference layer.

    Wraps the core LLM client and handles V1-specific:
    - System prompt loading
    - DecisionFocus prompt formatting
    - Exploratory mode support

    All mechanical LLM operations are delegated to core.LLMInferenceClient.
    """

    def __init__(self):
        """Initialize V1 LLM layer with core client"""
        self.core_client = LLMInferenceClient(
            api_key=config.OPENROUTER_API_KEY,
            base_url=config.OPENROUTER_BASE_URL,
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
        )

        # V1-specific prompts directory
        self.prompts_dir = config.PROMPTS_DIR

    def _load_system_prompt(self) -> str:
        """Load V1 system prompt"""
        system_prompt_path = self.prompts_dir / "system.txt"
        return system_prompt_path.read_text()

    def _load_user_prompt(
        self,
        prompt_name: str,
        context: str,
        decision_focus=None,
    ) -> str:
        """
        Load and format V1 user prompt template.

        V1: Frameworks adapt to context, not the other way around.
        If decision_focus is None, use exploratory prompts where available.
        """
        # For decision-bound frameworks without decision focus, use exploratory version
        if not decision_focus and prompt_name == "porter":
            prompt_name = "porter_exploratory"

        prompt_path = self.prompts_dir / f"{prompt_name}.txt"
        template = prompt_path.read_text()

        # Replace context placeholder
        formatted = template.replace("{context}", context)

        # Replace DecisionFocus placeholders if decision_focus is provided
        if decision_focus:
            # These placeholders are expected in decision-bound prompts like porter.txt
            formatted = formatted.replace(
                "{decision_question}", decision_focus.decision_question
            )
            formatted = formatted.replace(
                "{decision_type}", decision_focus.decision_type
            )
            formatted = formatted.replace(
                "{options}", ", ".join(decision_focus.options)
            )
            # Extract target system title from first line of context or use default
            target_title = context.split("\n")[0][:50] if context else "Target System"
            formatted = formatted.replace("{target_system_title}", target_title)
        else:
            # Replace placeholders with default values for exploratory mode
            target_title = context.split("\n")[0][:50] if context else "Target System"
            formatted = formatted.replace("{target_system_title}", target_title)

        return formatted

    def run_analysis(
        self,
        prompt_name: str,
        context: str,
        response_model: Type[T],
        max_retries: int = 1,
        decision_focus=None,
    ) -> T:
        """
        Run V1 analysis using specified prompt template.

        Args:
            prompt_name: Name of prompt template (porter, systems_dynamics)
            context: The problem context to analyze
            response_model: Pydantic model for parsing response
            max_retries: Number of retries on failure
            decision_focus: Optional DecisionFocus for decision-bound frameworks

        Returns:
            Parsed response as specified model type
        """
        system_prompt = self._load_system_prompt()
        user_prompt = self._load_user_prompt(prompt_name, context, decision_focus)

        try:
            return self.core_client.run_analysis(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=response_model,
                max_retries=max_retries,
            )
        except LLMError as e:
            # Re-raise with V1-specific context
            raise LLMError(f"V1 analysis failed: {e}")


# Backward compatibility alias
LLMInferenceLayer = V1LLMInferenceLayer


__all__ = [
    "V1LLMInferenceLayer",
    "LLMInferenceLayer",  # Backward compatibility
]
