"""Strategem V2 - Dependency Models"""

from typing import List, Optional
from pydantic import BaseModel, Field
from .enums import DependencyType


class ClaimDependency(BaseModel):
    """
    Dependency relationship between claims.

    V2: Claims may depend on assumptions or other claims.
    """

    dependent_claim_id: str = Field(..., description="ID of claim that depends")
    dependency_claim_id: Optional[str] = Field(
        None, description="ID of claim it depends on (if claim-on-claim dependency)"
    )
    dependency_assumption_id: Optional[str] = Field(
        None,
        description="ID of assumption it depends on (if claim-on-assumption dependency)",
    )
    dependency_type: DependencyType = Field(
        ...,
        description="Type of dependency: single_point, shared, cascading, or independent",
    )
    collapse_description: str = Field(
        ..., description="What happens if this dependency fails"
    )
    affected_options: List[str] = Field(
        ..., description="Options affected by this dependency"
    )


class AssumptionDependency(BaseModel):
    """
    Dependency mapping for assumptions.

    V2: Assumptions can be single-point-of-failure, shared, or cascading.
    """

    assumption_id: str = Field(..., description="ID of assumption")
    dependency_type: DependencyType = Field(
        ...,
        description="Type of dependency: single_point, shared, cascading, or independent",
    )
    dependent_claims: List[str] = Field(
        ..., description="IDs of claims that depend on this assumption"
    )
    collapse_impact: str = Field(..., description="Impact if this assumption fails")
    affected_options: List[str] = Field(
        ..., description="Options affected by this assumption dependency"
    )
    fragility_assessment: Optional[str] = Field(
        None, description="Assessment of how fragile this assumption is"
    )


__all__ = [
    "ClaimDependency",
    "AssumptionDependency",
]
