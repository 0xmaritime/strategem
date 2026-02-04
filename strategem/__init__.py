"""Strategem - Versioned Decision Support System

Strategem provides explicit version selection for compatibility and evolution:
- V1: Decision-Bound Reasoning Scaffold (stable, frozen)
- V2: Enhanced Analytical Depth (active development)

Both versions are fully functional and bounded with zero leakage.
"""

import sys
from typing import Optional

# Import core primitives (shared across versions)
from strategem.core import (
    # Primitives
    ConfidenceLevel,
    FrameworkName,
    ExecutionStatus,
    ContentType,
    generate_id,
    get_timestamp,
    V1_VERSION,
    V2_VERSION,
)


def analyze_v1(context):
    """
    Analyze using V1 (explicit).

    Args:
        context: ProblemContext instance

    Returns:
        AnalysisResult from V1
    """
    from strategem.v1 import AnalysisOrchestrator

    orchestrator = AnalysisOrchestrator()
    return orchestrator.run_full_analysis(context)


def analyze_v2(context):
    """
    Analyze using V2 (explicit).

    Args:
        context: ProblemContext instance

    Returns:
        AnalysisResult from V2
    """
    from strategem.v2 import AnalysisOrchestrator

    orchestrator = AnalysisOrchestrator()
    return orchestrator.run_full_analysis(context)


# Version identifiers
__version__ = "2.0.0-dev"
V1_VERSION = V1_VERSION
V2_VERSION = V2_VERSION


# Explicit version selection (no magic)
def get_version(version: str):
    """
    Get analysis function for specified version.

    Args:
        version: "v1" or "v2"

    Returns:
        Analysis function for the requested version
    """
    version = version.lower()
    if version == "v1":
        return analyze_v1
    elif version == "v2":
        return analyze_v2
    else:
        raise ValueError(f"Unknown version: {version}. Use 'v1' or 'v2'")


__all__ = [
    # Version analysis functions
    "analyze_v1",
    "analyze_v2",
    "get_version",
    # Version identifiers
    "__version__",
    "V1_VERSION",
    "V2_VERSION",
    # Core primitives (shared)
    "ConfidenceLevel",
    "FrameworkName",
    "ExecutionStatus",
    "ContentType",
    "generate_id",
    "get_timestamp",
]
