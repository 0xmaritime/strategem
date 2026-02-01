"""Strategem Core - LLM Inference Layer"""

import json
import re
from typing import Optional, Type, TypeVar
import requests
import yaml
from pydantic import BaseModel

from .config import config

T = TypeVar("T", bound=BaseModel)


class LLMError(Exception):
    """Error during LLM inference"""

    pass


class LLMInferenceLayer:
    """Layer for interacting with OpenRouter API"""

    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.base_url = config.OPENROUTER_BASE_URL
        self.model = config.LLM_MODEL
        self.temperature = config.LLM_TEMPERATURE
        self.max_tokens = config.LLM_MAX_TOKENS

        if not self.api_key:
            raise LLMError(
                "OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable."
            )

    def _load_system_prompt(self) -> str:
        """Load the common system prompt"""
        system_prompt_path = config.PROMPTS_DIR / "system.txt"
        return system_prompt_path.read_text()

    def _load_user_prompt(self, prompt_name: str, context: str) -> str:
        """Load and format a user prompt template"""
        prompt_path = config.PROMPTS_DIR / f"{prompt_name}.txt"
        template = prompt_path.read_text()
        return template.replace("{context}", context)

    def _make_request(self, system_prompt: str, user_prompt: str) -> str:
        """Make request to OpenRouter API"""
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

    def _clean_markdown_formatting(self, text: str) -> str:
        """Remove markdown formatting like **bold** from keys"""
        # Remove ** wrappers around keys and values
        cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        return cleaned

    def _extract_yaml_section(self, text: str) -> str:
        """Extract structured YAML-like content from response"""
        # Try to find content between markers or just clean up the text
        lines = text.split("\n")
        cleaned_lines = []
        in_code_block = False

        for line in lines:
            stripped = line.strip()

            # Handle markdown code blocks
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue

            # Skip code block markers
            if in_code_block:
                cleaned_lines.append(line)
            else:
                # Clean markdown bold formatting from the line
                cleaned_line = self._clean_markdown_formatting(line)
                cleaned_lines.append(cleaned_line)

        return "\n".join(cleaned_lines)

    def _extract_json_from_text(self, text: str) -> Optional[dict]:
        """Try to extract JSON from text, handling various formats"""
        # First, try to find JSON in code blocks
        json_block_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
        matches = re.findall(json_block_pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

        # Try to find JSON object directly in text using a more robust pattern
        # Match outermost braces by counting
        start = text.find("{")
        while start != -1:
            # Find matching closing brace
            count = 0
            for i in range(start, len(text)):
                if text[i] == "{":
                    count += 1
                elif text[i] == "}":
                    count -= 1
                    if count == 0:
                        # Found matching brace
                        json_str = text[start : i + 1]
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            break
            # Move to next opening brace
            start = text.find("{", start + 1)

        return None

    def _convert_keys_to_snake_case(self, data: dict) -> dict:
        """Convert nested dictionary keys from PascalCase to snake_case.

        Top-level keys are kept as-is (they match Pydantic aliases),
        only nested ForceAnalysis keys (Level, Rationale, etc.) are converted.
        """

        def to_snake_case(key: str) -> str:
            """Convert PascalCase or camelCase to snake_case"""
            import re

            # Handle consecutive capitals (e.g., 'AWS' -> 'aws')
            s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", key)
            # Handle remaining capitals
            return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

        if not isinstance(data, dict):
            return data

        result = {}
        for key, value in data.items():
            # Keep top-level key as-is (Pydantic aliases match PascalCase)
            new_key = key

            if isinstance(value, dict):
                # Convert nested keys to snake_case for ForceAnalysis fields
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
        """Convert simple YAML-like text to dict"""
        result = {}
        current_section = None
        current_list = None
        lines = yaml_text.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                i += 1
                continue

            # Check for section header (key without value, or key with colon)
            if ":" in stripped:
                parts = stripped.split(":", 1)
                key = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else None

                # Count indentation to determine nesting
                indent = len(line) - len(line.lstrip())

                if indent == 0:
                    # Top level key
                    if value:
                        result[key] = value
                        current_section = None
                        current_list = None
                    else:
                        # This is a section header
                        result[key] = {}
                        current_section = key
                        current_list = None

                        # Look ahead for nested content
                        j = i + 1
                        while j < len(lines):
                            next_line = lines[j]
                            next_indent = len(next_line) - len(next_line.lstrip())
                            next_stripped = next_line.strip()

                            if not next_stripped:
                                j += 1
                                continue

                            if next_indent <= indent and next_stripped:
                                # End of this section
                                break

                            if next_indent > indent:
                                # Nested content
                                if ":" in next_stripped:
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
                                        # Deeper nesting - look for list items
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
                                elif next_stripped.startswith("-"):
                                    # List at this level
                                    if key not in result or not isinstance(
                                        result[key], list
                                    ):
                                        result[key] = []
                                    item = next_stripped[1:].strip()
                                    if item:
                                        result[key].append(item)

                            j += 1

                        i = j - 1
                else:
                    # Nested key
                    if current_section:
                        if value:
                            result[current_section][key] = value

            i += 1

        return result

    def run_analysis(
        self,
        prompt_name: str,
        context: str,
        response_model: Type[T],
        max_retries: int = 1,
    ) -> T:
        """
        Run an analysis using the specified prompt template.

        Args:
            prompt_name: Name of the prompt template (porter, systems_dynamics)
            context: The problem context to analyze
            response_model: Pydantic model for parsing response
            max_retries: Number of retries on failure

        Returns:
            Parsed response as the specified model type
        """
        system_prompt = self._load_system_prompt()
        user_prompt = self._load_user_prompt(prompt_name, context)

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                response_text = self._make_request(system_prompt, user_prompt)

                # First, try to extract JSON directly from the response
                json_data = self._extract_json_from_text(response_text)
                if json_data:
                    # Convert keys to snake_case for Pydantic compatibility
                    json_data = self._convert_keys_to_snake_case(json_data)
                    return response_model(**json_data)

                # Clean markdown and try YAML parsing with PyYAML
                cleaned = self._extract_yaml_section(response_text)

                # Try PyYAML first (more robust than custom parser)
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
                except Exception as yaml_error:
                    # If all parsing fails, try direct JSON on cleaned text
                    try:
                        data = json.loads(cleaned)
                        return response_model(**data)
                    except:
                        raise LLMError(
                            f"Failed to parse response. Last error: {yaml_error}"
                        )

            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    continue
                raise LLMError(
                    f"Analysis failed after {max_retries + 1} attempts: {last_error}"
                )

        raise LLMError("Analysis failed unexpectedly")
