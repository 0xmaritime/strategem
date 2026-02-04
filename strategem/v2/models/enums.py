"""Strategem V2 - Enums"""

from enum import Enum


class ClaimSource(str, Enum):
    """Source of an analytical claim (V2)"""

    INPUT = "input"
    ASSUMPTION = "assumption"
    INFERENCE = "inference"
    DERIVED = "derived"


class ConfidenceLevel(str, Enum):
    """Confidence levels for analytical claims (V2)"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TensionType(str, Enum):
    """Type of tension between frameworks or claims (V2)"""

    AGREEMENT = "agreement"
    TENSION = "tension"
    CONTRADICTION = "contradiction"
    DIVERGENT = "divergent"


class DependencyType(str, Enum):
    """Type of dependency between assumptions or claims (V2)"""

    SINGLE_POINT = "single_point"
    SHARED = "shared"
    CASCADING = "cascading"
    INDEPENDENT = "independent"


class SensitivityLevel(str, Enum):
    """Sensitivity level for unknowns and assumptions (V2)"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DecisionType(str, Enum):
    """Type of decision being analyzed (V2)"""

    EXPLORE = "explore"
    COMPARE = "compare"
    STRESS_TEST = "stress_test"


class ClaimSource(str, Enum):
    """Source of an analytical claim (V2)"""

    INPUT = "input"
    ASSUMPTION = "assumption"
    INFERENCE = "inference"
    DERIVED = "derived"


class FrameworkExecutionStatus(str, Enum):
    """Status of framework execution (V2)"""

    SUCCESSFUL = "successful"
    INSUFFICIENT = "insufficient"
    FAILED = "failed"


__all__ = [
    "ConfidenceLevel",
    "TensionType",
    "DependencyType",
    "SensitivityLevel",
    "DecisionType",
    "ClaimSource",
    "FrameworkExecutionStatus",
]
