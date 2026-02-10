"""Strategem V2 - LLM Inference Layer (V2 Specific)

This layer wraps core LLM client and handles V2-specific prompt formatting.
V2: Decision is OPTIONAL. Frameworks can analyze with or without decision context.
"""

from typing import Optional, Type
from pathlib import Path
import json
import re

from strategem.core import LLMInferenceClient, LLMError, config
from .normalization import V2ResponseNormalizer


class V2LLMInferenceLayer:
    """
    V2-specific LLM inference layer.

    Wraps core LLM client and handles V2-specific:
    - Decision context injection (OPTIONAL)
    - Option-aware prompt formatting (when options present)
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

        V2: Decision is OPTIONAL. Options are OPTIONAL.
        Frameworks analyze based on provided context.
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

        V2: Decision context is OPTIONAL. Options are OPTIONAL.

        Args:
            prompt_name: Name of prompt template
            context: The problem context to analyze
            decision_question: The decision question (optional)
            decision_type: Type of decision (optional)
            options: List of options being analyzed (optional)
            response_model: Pydantic model for parsing response
            max_retries: Number of retries on failure

        Returns:
            Parsed response as specified model type
        """
        import sys

        system_prompt = self._load_system_prompt()
        user_prompt = self._load_user_prompt(
            prompt_name, context, decision_question, decision_type, options
        )

        try:
            print("=" * 80, file=sys.stderr)
            print(f"V2 DEBUG - Calling LLM for {prompt_name}", file=sys.stderr)
            print("=" * 80, file=sys.stderr)

            # Call API directly to capture raw response
            raw_response = self.core_client.call_api(
                system_prompt=system_prompt, user_prompt=user_prompt
            )

            print("=" * 80, file=sys.stderr)
            print(f"V2 DEBUG - Raw LLM Output for {prompt_name}:", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            print(raw_response, file=sys.stderr)
            print("=" * 80, file=sys.stderr)

            # V2: Normalize response before Pydantic validation
            json_data = self._extract_json_from_response(raw_response)
            if json_data:
                normalized_data = V2ResponseNormalizer.normalize_response(
                    json_data, prompt_name
                )
                print(
                    f"V2 DEBUG - Normalized data keys: {list(normalized_data.keys())}",
                    file=sys.stderr,
                )

                # Use safe validation with detailed error reporting
                result = V2ResponseNormalizer.safe_validate(
                    response_model, normalized_data, prompt_name
                )
                return result
            else:
                print(
                    f"V2 DEBUG - No JSON found in response, using fallback parsing",
                    file=sys.stderr,
                )

            # Fallback: use core client's parsing
            result = self.core_client.parse_response(
                response_text=raw_response, response_model=response_model
            )
            return result

        except (LLMError, ValueError) as e:
            print("=" * 80, file=sys.stderr)
            print(f"V2 DEBUG - Exception for {prompt_name}:", file=sys.stderr)
            print(f"Error: {e}", file=sys.stderr)
            print(f"Error Type: {type(e).__name__}", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            raise LLMError(f"V2 analysis failed: {e}")

    def _extract_json_from_response(self, response_text: str) -> Optional[dict]:
        """
        Extract JSON from LLM response.

        Handles JSON in markdown code blocks and direct JSON.
        """
        # Try JSON in markdown code blocks
        json_block_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
        matches = re.findall(json_block_pattern, response_text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

        # Try to find JSON object directly
        start = response_text.find("{")
        if start != -1:
            count = 0
            for i in range(start, len(response_text)):
                if response_text[i] == "{":
                    count += 1
                elif response_text[i] == "}":
                    count -= 1
                    if count == 0:
                        json_str = response_text[start : i + 1]
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            break

        return None


__all__ = ["V2LLMInferenceLayer"]
