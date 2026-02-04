"""Strategem V1 - Porter's Five Forces Models"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .core import AnalyticalClaim


class ForceEffect(BaseModel):
    """Effect of a force on a specific decision option"""

    option_name: str = Field(
        ..., alias="OptionName", description="Name of option being analyzed"
    )
    description: str = Field(
        ..., alias="Description", description="How this force affects this option"
    )
    key_assumptions: List[str] = Field(default_factory=list, alias="KeyAssumptions")
    key_unknowns: List[str] = Field(default_factory=list, alias="KeyUnknowns")


class ForceAnalysis(BaseModel):
    """
    Single force/pressure analysis result - DECISION-BOUND VERSION.

    In V1, forces must be analyzed in context of specific decision options.
    Generic analysis without option-specific effects is invalid.
    """

    name: str = Field(
        ..., alias="Name", description="Name of force (e.g., ThreatOfNewEntrants)"
    )
    relevance_to_decision: str = Field(
        ...,
        alias="RelevanceToDecision",
        pattern="^(high|medium|low)$",
        description="How relevant this force is to decision",
    )
    relevance_rationale: str = Field(
        ...,
        alias="RelevanceRationale",
        description="Why this force is or isn't relevant to decision",
    )
    effect_by_option: List[ForceEffect] = Field(
        ...,
        alias="EffectByOption",
        description="How this force affects each decision option",
    )
    shared_assumptions: List[str] = Field(
        default_factory=list,
        alias="SharedAssumptions",
        description="Assumptions that apply to all options",
    )
    shared_unknowns: List[str] = Field(
        default_factory=list,
        alias="SharedUnknowns",
        description="Unknowns that apply to all options",
    )
    claims: List[AnalyticalClaim] = Field(
        default_factory=list, description="Explicit claims derived from this analysis"
    )


class StructuralAsymmetry(BaseModel):
    """
    Identifies how a force disproportionately affects one option vs another.
    This is where decision value emerges.
    """

    force_name: str = Field(
        ..., alias="ForceName", description="Which Porter force shows asymmetry"
    )
    description: str = Field(
        ...,
        alias="Description",
        description="How this force affects options differently",
    )
    stronger_impact_on: str = Field(
        ..., alias="StrongerImpactOn", description="Which option is more affected"
    )
    rationale: str = Field(..., alias="Rationale", description="Why impact differs")
    key_assumption: str = Field(
        ...,
        alias="KeyAssumption",
        description="Key assumption underlying this asymmetry",
    )
    stronger_impact_on: str = Field(..., description="Which option is more affected")
    rationale: str = Field(..., description="Why the impact differs")
    key_assumption: str = Field(
        ..., description="Key assumption underlying this asymmetry"
    )


class PorterAnalysis(BaseModel):
    """
    DECISION-BOUND Operating Environment Structure analysis.

    Analyzes structural pressures acting on each option under consideration.
    Generic industry analysis is INVALID - must be decision-scoped.

    V1 Requirements:
    - Each force must show relevance to decision
    - Each force must describe effect_by_option for all options
    - Must include Structural Asymmetries section
    - All claims must be option-aware
    """

    # Decision context (embedded for clarity)
    decision_question: str = Field(
        ...,
        alias="DecisionQuestion",
        description="The decision question this analysis addresses",
    )
    options_analyzed: List[str] = Field(
        ..., alias="OptionsAnalyzed", description="Options under consideration"
    )

    # Five Forces - each decision-bound
    threat_of_new_entrants: ForceAnalysis = Field(alias="ThreatOfNewEntrants")
    supplier_power: ForceAnalysis = Field(alias="SupplierPower")
    buyer_power: ForceAnalysis = Field(alias="BuyerPower")
    substitutes: ForceAnalysis = Field(alias="Substitutes")
    rivalry: ForceAnalysis = Field(alias="Rivalry")

    # Cross-option analysis (REQUIRED)
    structural_asymmetries: List[StructuralAsymmetry] = Field(
        ...,
        alias="StructuralAsymmetries",
        description="Forces that disproportionately affect different options",
    )

    # Option-aware claims (REQUIRED)
    option_aware_claims: List[AnalyticalClaim] = Field(
        ...,
        alias="OptionAwareClaims",
        description="Claims that reference specific options or comparisons",
    )

    # Shared observations only if they affect all options equally
    shared_observations: Optional[str] = Field(
        None,
        alias="SharedObservations",
        description="Observations that apply equally to all options (rare)",
    )

    class Config:
        populate_by_name = True


__all__ = [
    "ForceEffect",
    "ForceAnalysis",
    "StructuralAsymmetry",
    "PorterAnalysis",
]
