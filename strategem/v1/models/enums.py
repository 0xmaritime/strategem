"""Strategem V1 - Enums"""

from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence levels for analytical claims"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ClaimSource(str, Enum):
    """Source of an analytical claim"""

    INPUT = "input"
    ASSUMPTION = "assumption"
    INFERENCE = "inference"


class DecisionType(str, Enum):
    """Type of decision being analyzed"""

    EXPLORE = "explore"
    COMPARE = "compare"
    STRESS_TEST = "stress_test"


class ClaimType(str, Enum):
    """Type of analytical claim"""

    OPTION_SPECIFIC = "option_specific"
    COMPARATIVE = "comparative"
    SYSTEM_LEVEL = "system_level"


class FrameworkExecutionStatus(str, Enum):
    """Status of framework execution"""

    SUCCESSFUL = "successful"
    INSUFFICIENT = "insufficient"
    FAILED = "failed"


class DecisionBindingStatus(str, Enum):
    """Status of decision binding in analysis (V1)"""

    DECISION_CONTEXT_PRESENT = "decision_context_present"
    GENUINELY_AMBIGUOUS = "genuinely_ambiguous"


class CoverageStatus(str, Enum):
    """Status of coverage (options or frameworks)"""

    COMPLETE = "complete"
    PARTIAL = "partial"
    NOT_APPLICABLE = "not_applicable"


class AnalysisSufficiencyStatus(str, Enum):
    """Overall sufficiency status of the analysis (V1)"""

    DECISION_RELEVANT_REASONING_PRODUCED = "decision_relevant_reasoning_produced"
    DECISION_RELEVANT_BUT_CONSTRAINED = "decision_relevant_but_constrained"
    EXPLORATORY_PRE_DECISION = "exploratory_pre_decision"


__all__ = [
    "ConfidenceLevel",
    "ClaimSource",
    "DecisionType",
    "ClaimType",
    "FrameworkExecutionStatus",
    "DecisionBindingStatus",
    "CoverageStatus",
    "AnalysisSufficiencyStatus",
]
