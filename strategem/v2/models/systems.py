"""Strategem V2 - Systems Dynamics Analysis Model (V2 Specific)"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field

from .core import AnalyticalClaim, Unknown


class FeedbackLoop(BaseModel):
    """A feedback loop in system (V2: option-aware)"""

    description: Optional[str] = Field(
        None, alias="Description", description="Loop description"
    )
    affected_options: Optional[List[str]] = Field(
        default_factory=list,
        alias="AffectedOptions",
        description="Options affected by this loop",
    )
    effect_type: Optional[str] = Field(
        None,
        description="growth_driver, acceleration_mechanism, constraint, stabilizer",
    )
    assumptions: Optional[List[str]] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class Bottleneck(BaseModel):
    """A system bottleneck (V2: option-aware)"""

    description: Optional[str] = Field(
        None, alias="Description", description="Bottleneck description"
    )
    affected_options: Optional[List[str]] = Field(
        default_factory=list, alias="AffectedOptions", description="Options affected"
    )
    severity: Optional[str] = Field(
        "medium", alias="Severity", description="high, medium, or low"
    )
    unknowns: Optional[List[str]] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class Fragility(BaseModel):
    """A system fragility (V2: option-aware)"""

    description: Optional[str] = Field(
        None, alias="Description", description="Fragility description"
    )
    affected_options: Optional[List[str]] = Field(
        default_factory=list, alias="AffectedOptions", description="Options affected"
    )
    severity: Optional[str] = Field(
        "medium", alias="Severity", description="high, medium, or low"
    )
    cascading: Optional[bool] = Field(
        False, alias="Cascading", description="Whether this cascades"
    )
    assumptions: Optional[List[str]] = Field(default_factory=list)

    class Config:
        populate_by_name = True


class SystemsDynamicsAnalysisV2(BaseModel):
    """
    Systems Dynamics analysis result (V2).

    V2: Decision context is optional. Claims can be option-aware or global.
    """

    decision_question: Optional[str] = Field(
        "", description="Decision being analyzed", alias="DecisionQuestion"
    )
    options_analyzed: Optional[List[str]] = Field(
        None, description="Options under consideration", alias="OptionsAnalyzed"
    )
    system_overview: Optional[str] = Field(
        "", alias="SystemOverview", description="System narrative overview"
    )
    key_components: Optional[List[str]] = Field(
        default_factory=list, alias="KeyComponents", description="System components"
    )
    feedback_loops: Optional[dict] = Field(
        None, alias="FeedbackLoops", description="Reinforcing and balancing loops"
    )
    bottlenecks: Optional[List[Bottleneck]] = Field(
        default_factory=list, alias="Bottlenecks"
    )
    fragilities: Optional[List[Fragility]] = Field(default_factory=list)
    option_aware_claims: Optional[List[AnalyticalClaim]] = Field(
        default_factory=list,
        description="Option-aware claims (optional, for when options are provided)",
        alias="OptionAwareClaims",
    )
    global_claims: Optional[List[AnalyticalClaim]] = Field(
        default_factory=list,
        description="Global claims (for when no options or option-independent analysis)",
        alias="GlobalClaims",
    )
    assumptions: Optional[List[str]] = Field(default_factory=list, alias="Assumptions")
    unknowns: Optional[List[Union[str, dict]]] = Field(
        default_factory=list,
        description="Unknowns with sensitivities",
        alias="Unknowns",
    )

    class Config:
        populate_by_name = True


__all__ = [
    "FeedbackLoop",
    "Bottleneck",
    "Fragility",
    "SystemsDynamicsAnalysisV2",
]
