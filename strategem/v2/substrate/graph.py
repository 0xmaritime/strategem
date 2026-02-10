"""Strategem V2 - Reasoning Graph

The Reasoning Graph stores primitives and their relationships.
It provides cross-framework comparison and dependency tracking.

Explicitly forbids:
- Ranking
- Weighting
- Scoring
"""

from typing import Dict, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field
from strategem.core import generate_id
from .primitives import (
    Claim,
    Assumption,
    Uncertainty,
    Mechanism,
    StakeholderPower,
    PrimitiveType,
)


class EdgeType(str, Enum):
    """Types of relationships between primitives"""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    REQUIRES = "requires"
    DERIVED_FROM = "derived_from"
    AFFECTS = "affects"


class ReasoningGraphNode(BaseModel):
    """A node in the reasoning graph (wraps a primitive)"""

    node_id: str = Field(default_factory=generate_id)
    primitive_id: str = Field(..., description="ID of the primitive this node wraps")
    primitive_type: PrimitiveType = Field(..., description="Type of primitive")
    framework: str = Field(..., description="Source framework")

    metadata: Dict = Field(default_factory=dict, description="Additional node metadata")


class ReasoningGraphEdge(BaseModel):
    """An edge in the reasoning graph (relationship between primitives)"""

    edge_id: str = Field(default_factory=generate_id)
    from_node_id: str = Field(..., description="Source node ID")
    to_node_id: str = Field(..., description="Target node ID")
    edge_type: EdgeType = Field(..., description="Type of relationship")

    weight: Optional[float] = Field(
        None, description="Optional weight (NOT for ranking/scoring)"
    )
    metadata: Dict = Field(default_factory=dict, description="Additional edge metadata")


class ReasoningGraph(BaseModel):
    """
    The canonical reasoning graph.

    Stores primitives, links dependencies, tracks provenance.
    Allows cross-framework comparison.

    Constraints:
    - No ranking
    - No weighting (except for provenance tracking)
    - No scoring
    """

    graph_id: str = Field(default_factory=generate_id)

    # Primitives by type
    claims: Dict[str, Claim] = Field(default_factory=dict)
    assumptions: Dict[str, Assumption] = Field(default_factory=dict)
    uncertainties: Dict[str, Uncertainty] = Field(default_factory=dict)
    mechanisms: Dict[str, Mechanism] = Field(default_factory=dict)
    stakeholder_powers: Dict[str, StakeholderPower] = Field(default_factory=dict)

    # Graph structure
    nodes: Dict[str, ReasoningGraphNode] = Field(default_factory=dict)
    edges: Dict[str, ReasoningGraphEdge] = Field(default_factory=dict)

    # Provenance tracking
    frameworks: Set[str] = Field(default_factory=set)

    class Config:
        arbitrary_types_allowed = True

    def add_claim(self, claim: Claim) -> None:
        """Add a claim to the graph"""
        self.claims[claim.primitive_id] = claim
        self._add_node_for_primitive(claim)
        self.frameworks.add(claim.framework)

    def add_assumption(self, assumption: Assumption) -> None:
        """Add an assumption to the graph"""
        self.assumptions[assumption.primitive_id] = assumption
        self._add_node_for_primitive(assumption)
        self.frameworks.add(assumption.framework)

    def add_uncertainty(self, uncertainty: Uncertainty) -> None:
        """Add an uncertainty to the graph"""
        self.uncertainties[uncertainty.primitive_id] = uncertainty
        self._add_node_for_primitive(uncertainty)
        self.frameworks.add(uncertainty.framework)

    def add_mechanism(self, mechanism: Mechanism) -> None:
        """Add a mechanism to the graph"""
        self.mechanisms[mechanism.primitive_id] = mechanism
        self._add_node_for_primitive(mechanism)
        self.frameworks.add(mechanism.framework)

    def add_stakeholder_power(self, stakeholder_power: StakeholderPower) -> None:
        """Add a stakeholder power to the graph"""
        self.stakeholder_powers[stakeholder_power.primitive_id] = stakeholder_power
        self._add_node_for_primitive(stakeholder_power)
        self.frameworks.add(stakeholder_power.framework)

    def _add_node_for_primitive(self, primitive) -> None:
        """Create a node for a primitive"""
        node = ReasoningGraphNode(
            primitive_id=primitive.primitive_id,
            primitive_type=primitive.primitive_type,
            framework=primitive.framework,
        )
        self.nodes[node.node_id] = node

    def add_edge(
        self,
        from_primitive_id: str,
        to_primitive_id: str,
        edge_type: EdgeType,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Add an edge between two primitives"""
        # Find node IDs for primitives
        from_node_id = None
        to_node_id = None

        for node in self.nodes.values():
            if node.primitive_id == from_primitive_id:
                from_node_id = node.node_id
            if node.primitive_id == to_primitive_id:
                to_node_id = node.node_id

        if not from_node_id or not to_node_id:
            return

        edge = ReasoningGraphEdge(
            from_node_id=from_node_id,
            to_node_id=to_node_id,
            edge_type=edge_type,
            metadata=metadata or {},
        )
        self.edges[edge.edge_id] = edge

    def get_all_primitives(self) -> List:
        """Get all primitives in the graph"""
        all_primitives = []
        all_primitives.extend(self.claims.values())
        all_primitives.extend(self.assumptions.values())
        all_primitives.extend(self.uncertainties.values())
        all_primitives.extend(self.mechanisms.values())
        all_primitives.extend(self.stakeholder_powers.values())
        return all_primitives

    def get_primitives_by_framework(self, framework: str) -> List:
        """Get all primitives from a specific framework"""
        return [p for p in self.get_all_primitives() if p.framework == framework]

    def get_cross_framework_conflicts(self) -> List[Dict]:
        """
        Find conflicts between frameworks.

        Returns list of conflict dictionaries with:
        - primitive_1: first conflicting primitive
        - primitive_2: second conflicting primitive
        - conflict_type: type of conflict
        """
        conflicts = []

        # Simple conflict detection: contradictory claims
        all_claims = list(self.claims.values())

        for i, claim1 in enumerate(all_claims):
            for claim2 in all_claims[i + 1 :]:
                if claim1.framework == claim2.framework:
                    continue

                # Simple heuristic: claims with contradictory keywords
                # (this is a placeholder - more sophisticated detection in Phase 4)
                if self._claims_may_conflict(claim1, claim2):
                    conflicts.append(
                        {
                            "primitive_1": claim1,
                            "primitive_2": claim2,
                            "conflict_type": "contradiction",
                        }
                    )

        return conflicts

    def _claims_may_conflict(self, claim1: Claim, claim2: Claim) -> bool:
        """Simple heuristic for claim conflict detection"""
        # Placeholder - more sophisticated detection in Phase 4
        text1 = claim1.statement.lower()
        text2 = claim2.statement.lower()

        contradictory_pairs = [
            ("is", "is not"),
            ("will", "will not"),
            ("can", "cannot"),
            ("should", "should not"),
            ("high", "low"),
            ("increase", "decrease"),
            ("success", "failure"),
            ("likely", "unlikely"),
        ]

        for word1, word2 in contradictory_pairs:
            if word1 in text1 and word2 in text2:
                return True

        return False

    def get_summary(self) -> Dict:
        """Get summary of graph contents"""
        return {
            "graph_id": self.graph_id,
            "total_primitives": len(self.get_all_primitives()),
            "claims": len(self.claims),
            "assumptions": len(self.assumptions),
            "uncertainties": len(self.uncertainties),
            "mechanisms": len(self.mechanisms),
            "stakeholder_powers": len(self.stakeholder_powers),
            "frameworks": list(self.frameworks),
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "cross_framework_conflicts": len(self.get_cross_framework_conflicts()),
        }


__all__ = [
    "EdgeType",
    "ReasoningGraphNode",
    "ReasoningGraphEdge",
    "ReasoningGraph",
]
