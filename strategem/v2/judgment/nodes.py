"""Strategem V2 - Judgment Nodes

A Judgment Node represents an irreducible interpretive fork.

A judgment node exists when:
- Evidence supports multiple plausible interpretations
- The system cannot analytically resolve the choice
- Resolution depends on values, risk tolerance, or belief

Judgment nodes are derived, never emitted by frameworks.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from strategem.core import generate_id


class JudgmentTriggerType(str, Enum):
    """Types of triggers for judgment nodes"""

    CONFLICTING_CLAIMS = "conflicting_claims"
    COMPETING_MECHANISMS = "competing_mechanisms"
    VALUE_LADEN_ASSUMPTIONS = "value_laden_assumptions"
    HIGH_SENSITIVITY_UNCERTAINTIES = "high_sensitivity_uncertainties"
    STAKEHOLDER_POWER_TRADEOFFS = "stakeholder_power_tradeoffs"
    FRAMEWORK_DISAGREEMENT = "framework_disagreement"
    OPTION_EMERGENCE = "option_emergence"


class Stance(BaseModel):
    """
    A plausible stance within a judgment node.

    No stance may be marked as preferred.
    """

    stance_id: str = Field(default_factory=generate_id)
    name: str = Field(..., description="Name or label for this stance")
    description: str = Field(..., description="Description of this stance")

    downstream_implications: List[str] = Field(
        default_factory=list,
        description="Downstream implications of taking this stance",
    )

    supporting_primitives: List[str] = Field(
        default_factory=list,
        description="IDs of primitives that support this stance",
    )

    opposing_primitives: List[str] = Field(
        default_factory=list,
        description="IDs of primitives that oppose this stance",
    )

    # Explicitly NO preference field
    # No stance may be marked as preferred

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class JudgmentNode(BaseModel):
    """
    An irreducible interpretive fork.

    Represents a point where analytical resolution is impossible
    and judgment is required.
    """

    node_id: str = Field(default_factory=generate_id)
    judgment_trigger_type: JudgmentTriggerType = Field(
        ..., description="What triggered this judgment node"
    )

    # Why judgment is required
    why_judgment_required: str = Field(
        ..., description="Why judgment is required for this issue"
    )

    # What cannot resolve it
    what_cannot_resolve: str = Field(
        ...,
        description="What analytical tools cannot resolve about this issue",
    )

    # Plausible stances
    plausible_stances: List[Stance] = Field(
        ..., description="Plausible stances for this judgment"
    )

    # Triggering evidence
    triggering_primitives: List[str] = Field(
        default_factory=list,
        description="IDs of primitives that triggered this judgment",
    )

    # Frameworks involved
    affected_frameworks: List[str] = Field(
        default_factory=list,
        description="Frameworks involved in this judgment",
    )

    # Scope
    scope: str = Field(
        default="global", description="Scope: 'global' or specific dimension"
    )

    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    def validate_no_preference(self) -> bool:
        """
        Validate that no stance is marked as preferred.

        This is a hard invariant: judgment nodes cannot have preferences.
        """
        for stance in self.plausible_stances:
            if "preferred" in stance.metadata or stance.metadata.get("preferred"):
                return False
        return True


__all__ = [
    "JudgmentTriggerType",
    "Stance",
    "JudgmentNode",
]
