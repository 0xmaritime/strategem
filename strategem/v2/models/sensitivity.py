"""Strategem V2 - Sensitivity Models"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .enums import SensitivityLevel


class SensitivityTrigger(BaseModel):
    """
    A trigger that would materially change the assessment.

    V2: Sensitivities are first-class. What would need to be true
    for this assessment to change?
    """

    trigger_description: str = Field(
        ..., description="What condition or fact would change the assessment"
    )
    affected_claims: List[str] = Field(
        ..., description="IDs of claims that would change"
    )
    affected_options: List[str] = Field(
        ..., description="Options affected by this sensitivity"
    )
    sensitivity_level: SensitivityLevel = Field(
        ..., description="Sensitivity level: critical, high, medium, or low"
    )
    evidence_needed: Optional[str] = Field(
        None, description="What evidence would address this sensitivity"
    )
    question_generated: Optional[str] = Field(
        None, description="Inquiry prompt for the user (not advice)"
    )


__all__ = [
    "SensitivityTrigger",
]
