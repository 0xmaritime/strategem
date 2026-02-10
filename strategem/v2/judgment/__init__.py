"""Strategem V2 - Judgment Layer

The Judgment Layer derives judgment nodes from the reasoning substrate.
Judgment nodes represent irreducible interpretive forks that cannot be
resolved analytically.

Judgment is derived, never emitted by frameworks.
"""

from .nodes import (
    JudgmentNode,
    Stance,
    JudgmentTriggerType,
)
from .derive import (
    JudgmentDeriver,
    DerivationResult,
)

__all__ = [
    "JudgmentNode",
    "Stance",
    "JudgmentTriggerType",
    "JudgmentDeriver",
    "DerivationResult",
]
