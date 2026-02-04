"""Strategem V2 - Porter Analysis Model (V2 Specific)"""

from typing import List, Optional
from pydantic import BaseModel, Field

from .core import AnalyticalClaim


class ForceEffect(BaseModel):
    """Effect of a Porter force on a specific option (V2: option-aware)"""

    option_name: str = Field(
        ..., alias="OptionName", description="Name of option being analyzed"
    )
    description: str = Field(
        ..., alias="Description", description="How this force affects this option"
    )
    magnitude: str = Field(..., alias="Magnitude", description="high, medium, or low")
    direction: str = Field(
        ..., alias="Direction", description="positive, negative, or neutral"
    )
    key_assumptions: List[str] = Field(default_factory=list, alias="KeyAssumptions")
    key_unknowns: List[str] = Field(default_factory=list, alias="KeyUnknowns")

    class Config:
        populate_by_name = True


class PorterForce(BaseModel):
    """A single Porter force analysis (V2: option-aware)"""

    name: Optional[str] = Field(None, description="Force name")
    relevance_to_decision: Optional[str] = Field(
        None, description="high, medium, or low"
    )
    relevance_rationale: Optional[str] = Field(
        None, description="Why this matters to decision"
    )
    effect_by_option: Optional[List[ForceEffect]] = Field(
        None, description="Effects on each option"
    )
    shared_assumptions: Optional[List[str]] = Field(default_factory=list)
    shared_unknowns: Optional[List[str]] = Field(default_factory=list)


class StructuralAsymmetry(BaseModel):
    """Structural asymmetry between options (V2: option-aware)"""

    force_name: str = Field(..., description="Name of force")
    description: str = Field(..., description="Description of asymmetry")
    stronger_impact_on: str = Field(..., description="Option more affected")
    rationale: str = Field(..., description="Why impact differs")
    key_assumption: Optional[str] = Field(None, description="Underlying assumption")
    affected_options: List[str] = Field(..., description="Options affected")


class PorterAnalysisV2(BaseModel):
    """
    Porter's Five Forces analysis result (V2).

    V2: All claims are option-aware. Decision context is required.
    """

    decision_question: Optional[str] = Field(
        None, description="Decision being analyzed", alias="DecisionQuestion"
    )
    options_analyzed: Optional[List[str]] = Field(
        None, description="Options under consideration", alias="OptionsAnalyzed"
    )

    threat_of_new_entrants: Optional[PorterForce] = Field(
        None, alias="ThreatOfNewEntrants"
    )
    supplier_power: Optional[PorterForce] = Field(None, alias="SupplierPower")
    buyer_power: Optional[PorterForce] = Field(None, alias="BuyerPower")
    substitutes: Optional[PorterForce] = Field(None, alias="Substitutes")
    rivalry: Optional[PorterForce] = Field(None, alias="Rivalry")

    structural_asymmetries: Optional[List[StructuralAsymmetry]] = Field(
        default_factory=list
    )

    option_aware_claims: Optional[List[AnalyticalClaim]] = Field(
        default_factory=list,
        description="Option-aware claims produced by this framework",
    )

    shared_observations: Optional[str] = Field(None, alias="SharedObservations")

    class Config:
        populate_by_name = True


__all__ = [
    "ForceEffect",
    "PorterForce",
    "StructuralAsymmetry",
    "PorterAnalysisV2",
]
