"""Strategem V2 - Reasoning Substrate

The Reasoning Substrate is a canonical internal representation that sits
between frameworks and outputs. It normalizes all framework outputs into
a set of primitive types that can be compared, linked, and analyzed
across frameworks.

The substrate is the only place where:
- Cross-framework interaction occurs
- Conflicts are detected
- Judgment is derived (in Phase 4)

Frameworks never interact directly with each other or with judgment logic.
"""

from .primitives import (
    Claim,
    Assumption,
    Uncertainty,
    Mechanism,
    StakeholderPower,
    PrimitiveType,
)
from .graph import (
    EdgeType,
    ReasoningGraph,
    ReasoningGraphNode,
    ReasoningGraphEdge,
)
from .ingest import (
    SubstrateIngestor,
    IngestionResult,
)

__all__ = [
    # Primitives
    "Claim",
    "Assumption",
    "Uncertainty",
    "Mechanism",
    "StakeholderPower",
    "PrimitiveType",
    # Graph
    "EdgeType",
    "ReasoningGraph",
    "ReasoningGraphNode",
    "ReasoningGraphEdge",
    # Ingestion
    "SubstrateIngestor",
    "IngestionResult",
]
