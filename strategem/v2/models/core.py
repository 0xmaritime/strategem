"""Strategem V2 - Core Models"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .enums import ConfidenceLevel, ClaimSource, DecisionType


class Decision(BaseModel):
    """
    Decision context - REQUIRED in V2.

    V2: Decision Focus is required, not inferred.
    Without Decision, analysis cannot proceed.
    """

    decision_question: str = Field(
        ..., description="The specific decision question being asked"
    )
    decision_type: DecisionType = Field(
        ..., description="Type of decision: explore, compare, or stress_test"
    )

    class Config:
        populate_by_name = True


class Option(BaseModel):
    """
    A decision option under consideration.

    V2: All frameworks MUST analyze each option explicitly.
    Generic analysis without option binding is invalid.
    """

    name: str = Field(..., description="Unique name/identifier for this option")
    description: Optional[str] = Field(
        None, description="Human-readable description of this option"
    )
    metadata: dict = Field(
        default_factory=dict, description="Optional metadata for this option"
    )


class AnalyticalClaim(BaseModel):
    """
    An explicit analytical claim produced by a framework.

    V2: Claims MUST be explicitly option-aware.
    Every claim must specify which option(s) it affects.
    """

    statement: str = Field(..., alias="Statement", description="The claim statement")
    source: ClaimSource = Field(
        ..., description="Source: input, assumption, inference, or derived"
    )
    confidence: ConfidenceLevel = Field(
        ..., description="Confidence level: low, medium, or high"
    )
    framework: str = Field(..., description="Which framework produced this claim")
    affected_options: List[str] = Field(
        ...,
        alias="AffectedOptions",
        description="Which decision option(s) this claim affects",
    )
    claim_id: Optional[str] = Field(
        None,
        alias="ClaimId",
        description="Unique identifier for this claim (for tension mapping)",
    )

    class Config:
        populate_by_name = True


class OptionEffect(BaseModel):
    """
    Effect of a structural force or framework on a specific option.

    V2: Every framework must produce option-aware effects.
    """

    option_name: str = Field(..., description="Name of option being analyzed")
    effect_description: str = Field(
        ..., description="How this framework/force affects this option"
    )
    magnitude: Optional[str] = Field(
        None, description="Qualitative magnitude (e.g., 'high', 'medium', 'low')"
    )
    direction: Optional[str] = Field(
        None,
        description="Direction of effect (e.g., 'positive', 'negative', 'neutral')",
    )
    assumptions: List[str] = Field(
        default_factory=list, description="Assumptions underlying this effect"
    )
    unknowns: List[str] = Field(
        default_factory=list, description="Unknowns affecting this effect"
    )


class Assumption(BaseModel):
    """
    An explicit assumption underlying analysis.

    V2: Assumptions are first-class, mapped to claims, and tested for fragility.
    """

    statement: str = Field(..., description="The assumption statement")
    framework: str = Field(..., description="Framework that made this assumption")
    affected_options: List[str] = Field(
        default_factory=list, description="Options affected by this assumption"
    )
    fragility: Optional[str] = Field(
        None,
        description="Assessment of assumption fragility (e.g., 'high', 'medium', 'low')",
    )
    assumption_id: Optional[str] = Field(
        None, description="Unique identifier for this assumption"
    )


class Unknown(BaseModel):
    """
    An explicit unknown in the analysis.

    V2: Unknowns are first-class, mapped to sensitivities.
    """

    statement: str = Field(..., description="The unknown statement")
    framework: str = Field(..., description="Framework that identified this unknown")
    affected_options: List[str] = Field(
        default_factory=list, description="Options affected by this unknown"
    )
    sensitivity: Optional[str] = Field(
        None,
        description="Sensitivity level (e.g., 'critical', 'high', 'medium', 'low')",
    )
    evidence_needed: Optional[str] = Field(
        None, description="What evidence would reduce this unknown"
    )


__all__ = [
    "Decision",
    "Option",
    "AnalyticalClaim",
    "OptionEffect",
    "Assumption",
    "Unknown",
]
