"""Strategem V2 - Response Normalization Layer

This layer provides mechanical tolerance for LLM output variations before Pydantic validation.

Design Principles:
- Normalize LLM output to match model expectations
- Handle missing fields gracefully (default values)
- Fix common LLM quirks (PascalCase, nesting issues)
- Preserve semantic correctness, relax structural strictness
"""

import json
import re
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, ValidationError


class V2ResponseNormalizer:
    """
    Normalizes LLM responses before Pydantic validation.

    Provides mechanical forgiveness for:
    - Missing optional fields
    - Incorrect nesting structures
    - Field name variations
    - Type mismatches (str vs int, etc.)
    """

    # Known enum value mappings (for normalization)
    CONFIDENCE_MAPPINGS = {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "Low": "low",
        "Medium": "medium",
        "High": "high",
        "LOW": "low",
        "MEDIUM": "medium",
        "HIGH": "high",
    }

    SOURCE_MAPPINGS = {
        "input": "input",
        "assumption": "assumption",
        "inference": "inference",
        "derived": "derived",
        "Input": "input",
        "Assumption": "assumption",
        "Inference": "inference",
        "Derived": "derived",
    }

    DECISION_TYPE_MAPPINGS = {
        "explore": "explore",
        "compare": "compare",
        "stress_test": "stress_test",
        "stress-test": "stress_test",
        "Explore": "explore",
        "Compare": "compare",
        "Stress Test": "stress_test",
        "StressTest": "stress_test",
    }

    # V2 Field names that MUST stay in PascalCase (they have Pydantic aliases)
    # These should NOT be converted to snake_case
    PRESERVE_PASCALCASE_FIELDS = {
        "DecisionQuestion",
        "OptionsAnalyzed",
        "OptionAwareClaims",
        "OptionName",
        "AffectedOptions",
        "ClaimId",
        "RelevanceToDecision",
        "RelevanceRationale",
        "EffectByOption",
        "KeyAssumptions",
        "KeyUnknowns",
        "SharedAssumptions",
        "SharedUnknowns",
        "StructuralAsymmetries",
        "SharedObservations",
        "SystemOverview",
        "KeyComponents",
        "FeedbackLoops",
        "Description",
        "Magnitude",
        "Direction",
        "Severity",
        "Cascading",
        "Bottlenecks",
        "Fragilities",
        "Assumptions",
        "Unknowns",
    }

    @staticmethod
    def normalize_response(data: Dict[str, Any], framework_name: str) -> Dict[str, Any]:
        """
        Normalize LLM response data for V2 frameworks.

        Args:
            data: Raw parsed JSON from LLM
            framework_name: Name of framework for framework-specific normalization

        Returns:
            Normalized data ready for Pydantic validation
        """
        if not isinstance(data, dict):
            raise ValueError(f"Expected dict, got {type(data)}")

        # First pass: Preserve PascalCase fields that have Pydantic aliases
        normalized = {}
        for key, value in data.items():
            if key in V2ResponseNormalizer.PRESERVE_PASCALCASE_FIELDS:
                # Keep as-is (PascalCase) for Pydantic alias matching
                normalized[key] = value
            else:
                # Convert other fields to snake_case
                normalized[V2ResponseNormalizer._to_snake_case(key)] = value

        # Framework-specific normalization - pass original data, not intermediate normalized dict
        # The framework-specific methods will use the _get_value helper to handle both PascalCase and snake_case
        if "systems" in framework_name.lower():
            normalized = V2ResponseNormalizer._normalize_systems_response(data)
        else:
            normalized = V2ResponseNormalizer._normalize_generic_response(data)

        return normalized

    @staticmethod
    def _normalize_systems_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize systems dynamics framework response.

        Preserves PascalCase fields with Pydantic aliases while ensuring proper structure.
        """
        normalized = {}

        # Preserve PascalCase fields with aliases
        normalized["DecisionQuestion"] = (
            V2ResponseNormalizer._get_value(
                data, "DecisionQuestion", "decision_question"
            )
            or ""
        )

        normalized["OptionsAnalyzed"] = V2ResponseNormalizer._ensure_list(
            V2ResponseNormalizer._get_value(data, "OptionsAnalyzed", "options_analyzed")
        )

        normalized["SystemOverview"] = (
            V2ResponseNormalizer._get_value(data, "SystemOverview", "system_overview")
            or ""
        )

        normalized["KeyComponents"] = V2ResponseNormalizer._ensure_list(
            V2ResponseNormalizer._get_value(data, "KeyComponents", "key_components")
        )

        # Normalize FeedbackLoops (dict with Reinforcing/Balancing)
        feedback_loops = V2ResponseNormalizer._get_value(
            data, "FeedbackLoops", "feedback_loops"
        )
        if isinstance(feedback_loops, dict):
            normalized["FeedbackLoops"] = {}
            for loop_type in ["Reinforcing", "Balancing"]:
                loops = feedback_loops.get(loop_type, [])
                if isinstance(loops, list):
                    normalized["FeedbackLoops"][loop_type] = [
                        V2ResponseNormalizer._normalize_feedback_loop(loop)
                        for loop in loops
                    ]
                else:
                    normalized["FeedbackLoops"][loop_type] = []
        else:
            normalized["FeedbackLoops"] = {"Reinforcing": [], "Balancing": []}

        # Normalize Bottlenecks
        bottlenecks = V2ResponseNormalizer._get_value(
            data, "Bottlenecks", "bottlenecks"
        )
        normalized["Bottlenecks"] = V2ResponseNormalizer._normalize_bottlenecks(
            bottlenecks
        )

        # Normalize Fragilities
        fragilities = V2ResponseNormalizer._get_value(
            data, "Fragilities", "fragilities"
        )
        normalized["Fragilities"] = V2ResponseNormalizer._normalize_fragilities(
            fragilities
        )

        # Normalize OptionAwareClaims
        claims = V2ResponseNormalizer._get_value(
            data, "OptionAwareClaims", "option_aware_claims"
        )
        normalized["OptionAwareClaims"] = V2ResponseNormalizer._normalize_claims(claims)

        # Normalize Assumptions
        assumptions = V2ResponseNormalizer._get_value(
            data, "Assumptions", "assumptions"
        )
        normalized["Assumptions"] = V2ResponseNormalizer._ensure_list(assumptions)

        # Normalize Unknowns
        unknowns = V2ResponseNormalizer._get_value(data, "Unknowns", "unknowns")
        normalized["Unknowns"] = V2ResponseNormalizer._normalize_unknowns(unknowns)

        return normalized

    @staticmethod
    def _normalize_generic_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize generic framework response (fallback).

        Applies basic structural normalization without framework-specific logic.
        """
        normalized = {}

        # Try to preserve common V2 fields if present
        for key in ["DecisionQuestion", "OptionsAnalyzed", "OptionAwareClaims"]:
            if key in data:
                normalized[key] = data[key]
            elif key.lower() in data:
                normalized[key] = data[key.lower()]

        # Normalize other fields using _to_snake_case
        for key, value in data.items():
            if key not in normalized:
                normalized[V2ResponseNormalizer._to_snake_case(key)] = value

        return normalized

    @staticmethod
    def _normalize_feedback_loop(loop: Any) -> Dict[str, Any]:
        """Normalize a feedback loop entry"""
        if not isinstance(loop, dict):
            return {}

        return {
            "Description": loop.get("Description", ""),
            "AffectedOptions": V2ResponseNormalizer._ensure_list(
                loop.get("AffectedOptions", [])
            ),
            "EffectType": loop.get("EffectType", ""),
            "Assumptions": V2ResponseNormalizer._ensure_list(
                loop.get("Assumptions", [])
            ),
        }

    @staticmethod
    def _normalize_bottlenecks(bottlenecks: Any) -> List[Dict[str, Any]]:
        """Normalize bottlenecks list"""
        if not isinstance(bottlenecks, list):
            return []

        normalized = []
        for bottleneck in bottlenecks:
            if isinstance(bottleneck, dict):
                normalized.append(
                    {
                        "Description": bottleneck.get("Description", ""),
                        "AffectedOptions": V2ResponseNormalizer._ensure_list(
                            bottleneck.get("AffectedOptions", [])
                        ),
                        "Severity": bottleneck.get("Severity", "medium"),
                        "Unknowns": V2ResponseNormalizer._ensure_list(
                            bottleneck.get("Unknowns", [])
                        ),
                    }
                )

        return normalized

    @staticmethod
    def _normalize_fragilities(fragilities: Any) -> List[Dict[str, Any]]:
        """Normalize fragilities list"""
        if not isinstance(fragilities, list):
            return []

        normalized = []
        for fragility in fragilities:
            if isinstance(fragility, dict):
                normalized.append(
                    {
                        "Description": fragility.get("Description", ""),
                        "AffectedOptions": V2ResponseNormalizer._ensure_list(
                            fragility.get("AffectedOptions", [])
                        ),
                        "Severity": fragility.get("Severity", "medium"),
                        "Cascading": fragility.get("Cascading", False),
                        "Assumptions": V2ResponseNormalizer._ensure_list(
                            fragility.get("Assumptions", [])
                        ),
                    }
                )

        return normalized

    @staticmethod
    def _normalize_unknowns(unknowns: Any) -> List[Any]:
        """Normalize unknowns (can be strings or dicts)"""
        if not isinstance(unknowns, list):
            return []

        normalized = []
        for unknown in unknowns:
            if isinstance(unknown, str):
                normalized.append(
                    {
                        "Statement": unknown,
                        "AffectedOptions": [],
                        "Sensitivity": "medium",
                        "EvidenceNeeded": "",
                    }
                )
            elif isinstance(unknown, dict):
                normalized.append(
                    {
                        "Statement": unknown.get("Statement", ""),
                        "AffectedOptions": V2ResponseNormalizer._ensure_list(
                            unknown.get("AffectedOptions", [])
                        ),
                        "Sensitivity": unknown.get("Sensitivity", "medium"),
                        "EvidenceNeeded": unknown.get("EvidenceNeeded", ""),
                    }
                )

        return normalized

    @staticmethod
    def _to_snake_case(key: str) -> str:
        """Convert PascalCase to snake_case, preserving abbreviations"""
        import re

        # Handle common abbreviations first
        key = key.replace("ID", "Id")
        key = key.replace("URL", "Url")
        key = key.replace("API", "Api")

        # Convert PascalCase to snake_case
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", key)
        s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
        return s2.lower()

    @staticmethod
    def _get_value(data: Dict[str, Any], *possible_keys: str) -> Any:
        """Get value from dict trying multiple possible key variations"""
        for key in possible_keys:
            if key in data:
                return data[key]
        return None

    @staticmethod
    @staticmethod
    def _normalize_claims(claims: Any) -> List[Dict[str, Any]]:
        """Normalize claims list"""
        if not isinstance(claims, list):
            return []

        normalized_claims = []
        for claim in claims:
            if not isinstance(claim, dict):
                continue

            normalized_claim = {
                "Statement": claim.get("Statement", ""),
                "AffectedOptions": V2ResponseNormalizer._ensure_list(
                    claim.get("AffectedOptions", [])
                ),
                "Source": V2ResponseNormalizer._normalize_enum(
                    claim.get("Source", "inference"),
                    V2ResponseNormalizer.SOURCE_MAPPINGS,
                    "inference",
                ),
                "Confidence": V2ResponseNormalizer._normalize_enum(
                    claim.get("Confidence", "medium"),
                    V2ResponseNormalizer.CONFIDENCE_MAPPINGS,
                    "medium",
                ),
                "Framework": claim.get("Framework", ""),
            }

            # Optional ClaimId
            if "ClaimId" in claim:
                normalized_claim["ClaimId"] = claim["ClaimId"]

            normalized_claims.append(normalized_claim)

        return normalized_claims

    @staticmethod
    def _ensure_list(value: Any) -> List[Any]:
        """Ensure value is a list"""
        if isinstance(value, list):
            return value
        if value is None:
            return []
        return [value]

    @staticmethod
    def _normalize_enum(value: Any, mappings: Dict[str, str], default: str) -> str:
        """Normalize enum values with case-insensitive mapping"""
        if value is None:
            return default

        value_str = str(value).strip()

        # Try direct mapping
        if value_str in mappings:
            return mappings[value_str]

        # Try case-insensitive lookup
        for key, mapped_value in mappings.items():
            if key.lower() == value_str.lower():
                return mapped_value

        # Return default if no match found
        return default

    @staticmethod
    def safe_validate(
        response_model: Type[BaseModel],
        data: Dict[str, Any],
        framework_name: str = "unknown",
    ) -> BaseModel:
        """
        Safely validate data against Pydantic model with detailed error reporting.

        Args:
            response_model: Pydantic model to validate against
            data: Data to validate
            framework_name: Framework name for error context

        Returns:
            Validated Pydantic model instance

        Raises:
            ValueError: If validation fails with detailed error information
        """
        try:
            return response_model(**data)
        except ValidationError as e:
            # Build detailed error message
            error_details = []
            for error in e.errors():
                loc = " -> ".join(str(x) for x in error["loc"])
                field_type = error.get("type", "unknown")
                message = error["msg"]
                error_details.append(
                    f"  - Field: {loc}\n    Type: {field_type}\n    Message: {message}"
                )

            error_msg = (
                f"Pydantic validation failed for {framework_name}:\n"
                + "\n".join(error_details)
            )

            # Add sample of received data
            sample_keys = list(data.keys())[:10]
            error_msg += f"\n\nReceived fields: {sample_keys}"

            raise ValueError(error_msg) from e


__all__ = [
    "V2ResponseNormalizer",
]
