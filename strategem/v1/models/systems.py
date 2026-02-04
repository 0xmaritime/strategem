"""Strategem V1 - Systems Dynamics Models"""

from typing import List
from pydantic import BaseModel, Field
from .core import AnalyticalClaim


class SystemsDynamicsAnalysis(BaseModel):
    """
    Target System Dynamics analysis (Qualitative Systems Dynamics framework).

    Understands feedback loops, dependencies, and fragility of the target system.

    Note: Framework disagreement is a valid and expected system outcome.
    Lack of consensus between frameworks does not indicate failure.
    """

    system_overview: str = Field(alias="SystemOverview")
    key_components: List[str] = Field(alias="KeyComponents", default_factory=list)
    reinforcing_loops: List[str] = Field(
        alias="FeedbackLoops.Reinforcing", default_factory=list
    )
    balancing_loops: List[str] = Field(
        alias="FeedbackLoops.Balancing", default_factory=list
    )
    bottlenecks: List[str] = Field(alias="Bottlenecks", default_factory=list)
    fragilities: List[str] = Field(alias="Fragilities", default_factory=list)
    assumptions: List[str] = Field(alias="Assumptions", default_factory=list)
    unknowns: List[str] = Field(alias="Unknowns", default_factory=list)
    claims: List[AnalyticalClaim] = Field(
        default_factory=list, description="Key analytical claims from this framework"
    )


__all__ = [
    "SystemsDynamicsAnalysis",
]
