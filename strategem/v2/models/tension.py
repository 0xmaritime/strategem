"""Strategem V2 - Tension Models"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .enums import TensionType, ConfidenceLevel


class ClaimTension(BaseModel):
    """
    Tension between two claims from different frameworks.

    V2: Explicit tension mapping is required.
    """

    claim_1_id: str = Field(..., description="ID of first claim")
    claim_1_framework: str = Field(..., description="Framework of first claim")
    claim_2_id: str = Field(..., description="ID of second claim")
    claim_2_framework: str = Field(..., description="Framework of second claim")
    tension_type: TensionType = Field(
        ...,
        description="Type of tension: agreement, tension, contradiction, or divergent",
    )
    description: str = Field(..., description="Description of the tension or agreement")
    affected_options: List[str] = Field(
        ..., description="Options affected by this tension"
    )
    resolution_note: Optional[str] = Field(
        None,
        description="Note on how to resolve this tension (human judgment required)",
    )


class FrameworkTension(BaseModel):
    """
    Aggregate tension between two frameworks.

    V2: Frameworks may disagree, and this is a valid outcome.
    The system surfaces tension; the human resolves it.
    """

    framework_1: str = Field(..., description="First framework name")
    framework_2: str = Field(..., description="Second framework name")
    tension_type: TensionType = Field(
        ..., description="Overall tension type between frameworks"
    )
    claim_tensions: List[ClaimTension] = Field(
        ...,
        description="Individual claim tensions that comprise this framework tension",
    )
    summary: str = Field(..., description="Human-readable summary of the tension")
    resolution_areas: List[str] = Field(
        default_factory=list, description="Areas requiring human judgment to resolve"
    )


__all__ = [
    "ClaimTension",
    "FrameworkTension",
]
