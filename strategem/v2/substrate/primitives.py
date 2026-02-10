"""Strategem V2 - Reasoning Primitives (Canonical)

All framework outputs are normalized into these canonical primitives.
Primitives are atomic, have no evaluative fields, and include provenance.

Each primitive includes:
- Provenance (framework)
- Scope (global / local)
- Affected dimensions (if applicable)
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from strategem.core import generate_id


class PrimitiveType(str, Enum):
    """Canonical primitive types"""

    CLAIM = "claim"
    ASSUMPTION = "assumption"
    UNCERTAINTY = "uncertainty"
    MECHANISM = "mechanism"
    STAKEHOLDER_POWER = "stakeholder_power"


class Claim(BaseModel):
    """
    A structural assertion about the system.

    Canonical primitive - no evaluative fields.
    """

    primitive_id: str = Field(default_factory=generate_id)
    primitive_type: PrimitiveType = Field(default=PrimitiveType.CLAIM)

    statement: str = Field(..., description="The claim statement")
    framework: str = Field(..., description="Source framework")

    provenance: str = Field(
        ..., description="Source within framework (e.g., inference, input)"
    )

    scope: str = Field(
        default="global",
        description="Scope: 'global' or specific component/option",
    )

    affected_dimensions: List[str] = Field(
        default_factory=list,
        description="Dimensions this claim affects (e.g., options, components)",
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class Assumption(BaseModel):
    """
    A belief required for a claim to hold.

    Canonical primitive - no evaluative fields.
    """

    primitive_id: str = Field(default_factory=generate_id)
    primitive_type: PrimitiveType = Field(default=PrimitiveType.ASSUMPTION)

    statement: str = Field(..., description="The assumption statement")
    framework: str = Field(..., description="Source framework")

    provenance: str = Field(..., description="Source within framework")

    scope: str = Field(
        default="global",
        description="Scope: 'global' or specific component/option",
    )

    affected_dimensions: List[str] = Field(
        default_factory=list,
        description="Dimensions this assumption affects",
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class Uncertainty(BaseModel):
    """
    An unknown that affects outcomes.

    Canonical primitive - no evaluative fields.
    """

    primitive_id: str = Field(default_factory=generate_id)
    primitive_type: PrimitiveType = Field(default=PrimitiveType.UNCERTAINTY)

    statement: str = Field(..., description="The uncertainty statement")
    framework: str = Field(..., description="Source framework")

    provenance: str = Field(..., description="Source within framework")

    scope: str = Field(
        default="global",
        description="Scope: 'global' or specific component/option",
    )

    affected_dimensions: List[str] = Field(
        default_factory=list,
        description="Dimensions this uncertainty affects",
    )

    evidence_needed: Optional[str] = Field(
        None, description="What evidence would reduce this uncertainty"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class Mechanism(BaseModel):
    """
    A causal pathway (no outcome evaluation).

    Canonical primitive - no evaluative fields.
    """

    primitive_id: str = Field(default_factory=generate_id)
    primitive_type: PrimitiveType = Field(default=PrimitiveType.MECHANISM)

    description: str = Field(..., description="Description of the mechanism")
    framework: str = Field(..., description="Source framework")

    provenance: str = Field(..., description="Source within framework")

    mechanism_type: str = Field(
        ..., description="Type of mechanism (e.g., reinforcing, balancing)"
    )

    scope: str = Field(
        default="global",
        description="Scope: 'global' or specific component/option",
    )

    affected_dimensions: List[str] = Field(
        default_factory=list,
        description="Dimensions this mechanism affects",
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class StakeholderPower(BaseModel):
    """
    Ability to block, distort, or enable outcomes.

    Canonical primitive - no evaluative fields.
    """

    primitive_id: str = Field(default_factory=generate_id)
    primitive_type: PrimitiveType = Field(default=PrimitiveType.STAKEHOLDER_POWER)

    stakeholder: str = Field(..., description="Name or description of stakeholder")
    framework: str = Field(..., description="Source framework")

    provenance: str = Field(..., description="Source within framework")

    power_type: str = Field(
        ..., description="Type of power (e.g., blocking, enabling, distorting)"
    )

    scope: str = Field(
        default="global",
        description="Scope: 'global' or specific component/option",
    )

    affected_dimensions: List[str] = Field(
        default_factory=list,
        description="Dimensions this stakeholder affects",
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


__all__ = [
    "PrimitiveType",
    "Claim",
    "Assumption",
    "Uncertainty",
    "Mechanism",
    "StakeholderPower",
]
