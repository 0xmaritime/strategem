"""Strategem V1 - Core Models"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .enums import ClaimSource, ConfidenceLevel


class DecisionFocus(BaseModel):
    """
    Decision Focus - MANDATORY for decision-bound frameworks.

    Defines what decision is being analyzed and which options are under consideration.
    Without DecisionFocus, frameworks must refuse execution or return low-confidence artifacts.
    """

    decision_question: str = Field(
        ..., description="The specific decision question being asked"
    )
    decision_type: str = Field(
        ..., description="Type of decision: explore, compare, or stress_test"
    )
    options: List[str] = Field(
        ..., description="Array of options under consideration (minimum 1)"
    )

    class Config:
        populate_by_name = True


class ProvidedMaterial(BaseModel):
    """A single piece of provided context material"""

    material_type: str = Field(..., description="Type: document, text, data, etc.")
    content: str = Field(..., description="The material content or reference")
    source: Optional[str] = Field(None, description="Source identifier or filename")


class AnalyticalClaim(BaseModel):
    """
    An explicit analytical claim produced by a framework.

    This is the backbone of explainability and auditability.
    Each claim must be traceable to its source and have explicit confidence.
    In V1, each claim must also reference which decision option(s) it affects.
    """

    statement: str = Field(..., description="The claim statement")
    source: ClaimSource = Field(
        ..., description="Source: input, assumption, or inference"
    )
    confidence: ConfidenceLevel = Field(
        ..., description="Confidence level: low, medium, or high"
    )
    framework: Optional[str] = Field(
        None, description="Which framework produced this claim"
    )
    claim_type: str = Field(
        default="system_level",
        description="Type of claim: option_specific, comparative, or system_level",
    )
    applicable_options: List[str] = Field(
        default_factory=list,
        description="Which decision option(s) this claim affects. For option_specific: exactly 1 option. For comparative: >=2 options. For system_level: use ['all']",
    )
    affected_options: List[str] = Field(
        default_factory=list,
        description="[Legacy] Which decision option(s) this claim affects. Use applicable_options in V1.",
    )


class ProblemContext(BaseModel):
    """
    First-class Problem Context object - the root abstraction of the system.

    This formalizes the problem being analyzed, independent of domain.
    A reader must be able to imagine applying Strategem Core to:
    - a policy decision
    - an operational failure
    - a product strategy
    - a target system evaluation

    without mental friction.
    """

    # Core problem definition
    title: str = Field(..., description="Title or identifier for this problem context")
    problem_statement: str = Field(
        ..., description="Clear statement of the problem being analyzed"
    )

    # Problem scope
    objectives: List[str] = Field(
        default_factory=list, description="What the decision owner is trying to achieve"
    )
    constraints: List[str] = Field(
        default_factory=list, description="Known limitations or boundaries"
    )

    # Input materials
    provided_materials: List[ProvidedMaterial] = Field(
        default_factory=list,
        description="Problem Context Materials provided for analysis",
    )

    # Optional explicit assumptions
    declared_assumptions: List[str] = Field(
        default_factory=list,
        description="Assumptions explicitly declared by the decision owner",
    )

    # Decision Focus (required for decision-bound frameworks like Porter)
    decision_focus: Optional[DecisionFocus] = Field(
        default=None,
        description="Decision context - required for decision-bound frameworks. Without this, frameworks must refuse execution or return low-confidence artifacts.",
    )

    # Legacy fields (maintained for backward compatibility during migration)
    raw_content: Optional[str] = Field(None, description="[Legacy] Raw input content")
    structured_content: Optional[str] = Field(
        None, description="[Legacy] Structured/processed content"
    )
    source_type: str = Field(
        "text", description="[Legacy] Source type: text, document, etc."
    )

    class Config:
        populate_by_name = True


__all__ = [
    "DecisionFocus",
    "ProvidedMaterial",
    "AnalyticalClaim",
    "ProblemContext",
]
