"""Strategem V2 - Systems Dynamics Analysis Model (V2 Specific)"""

from typing import List, Optional
from pydantic import BaseModel, Field

from .core import AnalyticalClaim, Unknown


class FeedbackLoop(BaseModel):
    """A feedback loop in the system (V2: option-aware)"""

    description: str = Field(..., alias="Description", description="Loop description")
    affected_options: List[str] = Field(
        ..., alias="AffectedOptions", description="Options affected by this loop"
    )
    effect_type: Optional[str] = Field(
        None,
        description="growth_driver, acceleration_mechanism, constraint, stabilizer",
    )
    assumptions: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class Bottleneck(BaseModel):
    """A system bottleneck (V2: option-aware)"""

    description: str = Field(
        ..., alias="Description", description="Bottleneck description"
    )
    affected_options: List[str] = Field(
        ..., alias="AffectedOptions", description="Options affected"
    )
    severity: str = Field(..., alias="Severity", description="high, medium, or low")
    unknowns: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class Fragility(BaseModel):
    """A system fragility (V2: option-aware)"""

    description: str = Field(
        ..., alias="Description", description="Fragility description"
    )
    affected_options: List[str] = Field(
        ..., alias="AffectedOptions", description="Options affected"
    )
    severity: str = Field(..., alias="Severity", description="high, medium, or low")
    cascading: bool = Field(..., alias="Cascading", description="Whether this cascades")
    assumptions: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class SystemsDynamicsAnalysisV2(BaseModel):
    """
    Systems Dynamics analysis result (V2).

    V2: All claims are option-aware. Decision context is required.
    """

    decision_question: str = Field(
        ..., description="Decision being analyzed", alias="DecisionQuestion"
    )
    options_analyzed: List[str] = Field(
        ..., description="Options under consideration", alias="OptionsAnalyzed"
    )

    system_overview: str = Field(
        ..., alias="SystemOverview", description="System narrative overview"
    )

    key_components: List[str] = Field(
        ..., alias="KeyComponents", description="System components"
    )

    feedback_loops: Optional[dict] = Field(
        None, alias="FeedbackLoops", description="Reinforcing and balancing loops"
    )

    bottlenecks: Optional[List[Bottleneck]] = Field(
        default_factory=list, alias="Bottlenecks"
    )

    fragilities: Optional[List[Fragility]] = Field(default_factory=list)

    option_aware_claims: Optional[List[AnalyticalClaim]] = Field(
        default_factory=list, description="Option-aware claims"
    )

    assumptions: Optional[List[str]] = Field(default_factory=list)

    unknowns: Optional[List[dict]] = Field(
        default_factory=list, description="Unknowns with sensitivities"
    )

    class Config:
        populate_by_name = True

    options_analyzed: Optional[List[str]] = Field(
        None, description="Options under consideration", alias="OptionsAnalyzed"
    )

    system_overview: Optional[str] = Field(
        None, description="System narrative overview"
    )

    key_components: Optional[List[str]] = Field(None, description="System components")

    feedback_loops: Optional[dict] = Field(
        None, alias="FeedbackLoops", description="Reinforcing and balancing loops"
    )

    bottlenecks: Optional[List[Bottleneck]] = Field(default_factory=list)

    fragilities: Optional[List[Fragility]] = Field(default_factory=list)

    option_aware_claims: Optional[List[AnalyticalClaim]] = Field(
        default_factory=list, description="Option-aware claims"
    )

    assumptions: Optional[List[str]] = Field(default_factory=list)

    unknowns: Optional[List[dict]] = Field(
        default_factory=list, description="Unknowns with sensitivities"
    )
    options_analyzed: List[str] = Field(
        ..., description="Options under consideration", alias="OptionsAnalyzed"
    )

    system_overview: str = Field(..., description="System narrative overview")

    key_components: List[str] = Field(..., description="System components")

    feedback_loops: dict = Field(
        ..., alias="FeedbackLoops", description="Reinforcing and balancing loops"
    )

    bottlenecks: List[Bottleneck] = Field(default_factory=list, alias="Bottlenecks")

    fragilities: List[Fragility] = Field(default_factory=list)

    option_aware_claims: List[AnalyticalClaim] = Field(
        default_factory=list, description="Option-aware claims"
    )

    assumptions: List[str] = Field(default_factory=list)

    unknowns: List[dict] = Field(
        default_factory=list, description="Unknowns with sensitivities"
    )


__all__ = [
    "FeedbackLoop",
    "Bottleneck",
    "Fragility",
    "SystemsDynamicsAnalysisV2",
]
