"""Strategem V2 - Framework Adapter Layer

Adapters translate framework-native output → canonical primitives.
Performs no interpretation - only structural translation.

Frameworks never talk to the orchestrator or artefact generator directly.
All communication goes through the substrate via adapters.
"""

from .systems_dynamics_adapter import SystemsDynamicsAdapter


__all__ = [
    "SystemsDynamicsAdapter",
]
