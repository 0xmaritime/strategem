"""Strategem Core - LLM Inference Layer (Mechanical Only)

This module contains ONLY the mechanical LLM client functionality.
No analytical types, no framework-specific concepts, no decision semantics.

It provides:
- API client for OpenRouter
- Response parsing (JSON/YAML)
- Retry logic
- Prompt loading

Version-specific prompt handling (e.g., DecisionFocus injection) is handled
by the version-specific layer (v1/ or v2/), not here.
"""

import json
import re
from typing import Optional, Type, TypeVar
from pathlib import Path
import requests
import yaml
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMError(Exception):
    """Error during LLM inference (mechanical only)"""

    pass


class LLMInferenceClient:
    """
    Mechanical LLM client for OpenRouter API.

    Responsibilities:
    - Load prompts from templates
    - Make HTTP requests to OpenRouter
    - Parse structured responses (JSON/YAML)
    - Retry on failure

    NOT responsible for:
    - Decision-specific prompt formatting (handled by v1/v2)
    - Analytical type mapping (handled by v1/v2)
    - Framework-specific logic (handled by v1/v2)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float,
        max_tokens: int,
    ):
        """Initialize LLM client with configuration"""
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        if not self.api_key:
            raise LLMError("OpenRouter API key not configured")

    def load_prompt_template(self, prompt_path: Path) -> str:
        """Load prompt template from file (mechanical only)"""
        return prompt_path.read_text()

    def format_prompt(self, template: str, context: str, **kwargs) -> str:
        """
        Format prompt template with context and optional variables.

        This is mechanical string replacement.
        Version-specific formatting (e.g., DecisionFocus) is handled
        by passing formatted strings from v1/v2 layer.

        Args:
            template: Prompt template string
            context: Problem context content
            **kwargs: Optional additional variables for template substitution

        Returns:
            Formatted prompt string
        """
        formatted = template.replace("{context}", context)

        for key, value in kwargs.items():
            formatted = formatted.replace(f"{{{key}}}", str(value))

        return formatted

    def call_api(self, system_prompt: str, user_prompt: str) -> str:
        """
        Make request to OpenRouter API (mechanical only).

        Args:
            system_prompt: System prompt for the LLM
            user_prompt: User prompt for the LLM

        Returns:
            Raw response text from LLM

        Raises:
            LLMError: If API request fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise LLMError(f"API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise LLMError(f"Unexpected API response format: {e}")

    def parse_response(
        self,
        response_text: str,
        response_model: Type[T],
    ) -> T:
        """
        Parse structured response from LLM (mechanical only).

        Handles JSON and YAML formats, with fallback to custom parsing.
        Version-specific models are passed in from v1/v2 layer.

        Args:
            response_text: Raw response text from LLM
            response_model: Pydantic model to parse response into

        Returns:
            Parsed response as specified model type

        Raises:
            LLMError: If parsing fails
        """
        # Try JSON extraction from markdown code blocks
        json_data = self._extract_json_from_markdown(response_text)
        if json_data:
            data = self._convert_keys_to_snake_case(json_data)
            return response_model(**data)

        # Clean markdown formatting
        cleaned = self._extract_yaml_section(response_text)

        # Try PyYAML parsing
        try:
            data = yaml.safe_load(cleaned)
            if isinstance(data, dict):
                data = self._convert_keys_to_snake_case(data)
                return response_model(**data)
        except Exception:
            pass

        # Fallback to custom YAML parser
        try:
            data = self._yaml_to_dict(cleaned)
            data = self._convert_keys_to_snake_case(data)
            return response_model(**data)
        except Exception as e:
            raise LLMError(f"Failed to parse response: {e}")

    def run_analysis(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        max_retries: int = 1,
    ) -> T:
        """
        Run complete LLM analysis with retry logic (mechanical only).

        Args:
            system_prompt: System prompt for the LLM
            user_prompt: User prompt for the LLM
            response_model: Pydantic model to parse response into
            max_retries: Number of retries on failure

        Returns:
            Parsed response as specified model type

        Raises:
            LLMError: If all attempts fail
        """
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                response_text = self.call_api(system_prompt, user_prompt)
                return self.parse_response(response_text, response_model)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    continue
                raise LLMError(
                    f"Analysis failed after {max_retries + 1} attempts: {last_error}"
                )

        raise LLMError("Analysis failed unexpectedly")

    # Private helper methods (mechanical only)

    def _extract_json_from_markdown(self, text: str) -> Optional[dict]:
        """Extract JSON from markdown code blocks"""
        json_block_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
        matches = re.findall(json_block_pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

        # Try to find JSON object directly
        start = text.find("{")
        while start != -1:
            count = 0
            for i in range(start, len(text)):
                if text[i] == "{":
                    count += 1
                elif text[i] == "}":
                    count -= 1
                    if count == 0:
                        json_str = text[start : i + 1]
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            break
            start = text.find("{", start + 1)

        return None

    def _extract_yaml_section(self, text: str) -> str:
        """Extract and clean YAML-like content from response"""
        lines = text.split("\n")
        cleaned_lines = []
        in_code_block = False

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                cleaned_lines.append(line)
            else:
                cleaned_line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
                cleaned_lines.append(cleaned_line)

        return "\n".join(cleaned_lines)

    def _convert_keys_to_snake_case(self, data: dict) -> dict:
        """Convert PascalCase keys to snake_case (mechanical only)"""

        def to_snake_case(key: str) -> str:
            s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", key)
            return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

        if not isinstance(data, dict):
            return data

        result = {}
        for key, value in data.items():
            new_key = key

            if isinstance(value, dict):
                converted_nested = {}
                for nested_key, nested_value in value.items():
                    converted_nested[to_snake_case(nested_key)] = nested_value
                result[new_key] = converted_nested
            elif isinstance(value, list):
                result[new_key] = [
                    self._convert_keys_to_snake_case(item)
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[new_key] = value

        return result

    def _yaml_to_dict(self, yaml_text: str) -> dict:
        """Custom YAML parser for simple structures (mechanical only)"""
        result = {}
        current_section = None
        lines = yaml_text.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                i += 1
                continue

            if ":" in stripped:
                parts = stripped.split(":", 1)
                key = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else None
                indent = len(line) - len(line.lstrip())

                if indent == 0:
                    if value:
                        result[key] = value
                        current_section = None
                    else:
                        result[key] = {}
                        current_section = key
                        j = i + 1
                        while j < len(lines):
                            next_line = lines[j]
                            next_indent = len(next_line) - len(next_line.lstrip())
                            next_stripped = next_line.strip()

                            if not next_stripped:
                                j += 1
                                continue

                            if next_indent <= indent and next_stripped:
                                break

                            if next_indent > indent and ":" in next_stripped:
                                nested_parts = next_stripped.split(":", 1)
                                nested_key = nested_parts[0].strip()
                                nested_value = (
                                    nested_parts[1].strip()
                                    if len(nested_parts) > 1
                                    else None
                                )
                                if nested_value:
                                    result[key][nested_key] = nested_value
                                else:
                                    result[key][nested_key] = []
                                    k = j + 1
                                    while k < len(lines):
                                        list_line = lines[k]
                                        list_stripped = list_line.strip()
                                        list_indent = len(list_line) - len(
                                            list_line.lstrip()
                                        )

                                        if not list_stripped:
                                            k += 1
                                            continue

                                        if (
                                            list_indent <= next_indent
                                            and list_stripped
                                            and not list_stripped.startswith("-")
                                        ):
                                            break

                                        if list_stripped.startswith("-"):
                                            item = list_stripped[1:].strip()
                                            if item:
                                                result[key][nested_key].append(item)
                                        k += 1
                            j += 1
                        i = j - 1
                else:
                    if current_section and value:
                        result[current_section][key] = value

            i += 1

        return result
