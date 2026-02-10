"""Strategem V1 - Analytical Models

This module contains V1-specific analytical types.
These are NOT shared with V2 - V2 may have different models.

 V1 Models:
 - Enums: ConfidenceLevel, ClaimSource, DecisionType, etc.
 - Core: ProblemContext, DecisionFocus, AnalyticalClaim
 - Frameworks: SystemsDynamicsAnalysis, etc.
 - Output: AnalysisResult, AnalysisReport, DecisionSurface
"""

from .enums import (
    ConfidenceLevel,
    ClaimSource,
    DecisionType,
    ClaimType,
    FrameworkExecutionStatus,
    DecisionBindingStatus,
    CoverageStatus,
    AnalysisSufficiencyStatus,
)
from .core import (
    DecisionFocus,
    ProvidedMaterial,
    AnalyticalClaim,
    ProblemContext,
)
from .systems import (
    SystemsDynamicsAnalysis,
)
from .output import (
    FrameworkResult,
    AnalysisSufficiencySummary,
    AnalysisResult,
    ReportSection,
    DecisionSurface,
    AnalysisReport,
)
from .framework import (
    AnalysisFramework,
)

# Predefined framework configurations (V1)
SYSTEMS_DYNAMICS_FRAMEWORK = AnalysisFramework(
    name="systems_dynamics",
    analytical_lens="systemic_fragility",
    input_requirements=[
        "problem_context",
        "target_system_description",
        "system_structure",
    ],
    prompt_template="systems_dynamics.txt",
    output_schema={
        "type": "object",
        "properties": {
            "SystemOverview": {"type": "string"},
            "KeyComponents": {"type": "array"},
            "FeedbackLoops": {"type": "object"},
            "Bottlenecks": {"type": "array"},
            "Fragilities": {"type": "array"},
            "Assumptions": {"type": "array"},
            "Unknowns": {"type": "array"},
        },
    },
    description="Understands feedback loops, dependencies, and fragility of the target system",
)

__all__ = [
    # Enums
    "ConfidenceLevel",
    "ClaimSource",
    "DecisionType",
    "ClaimType",
    "FrameworkExecutionStatus",
    "DecisionBindingStatus",
    "CoverageStatus",
    "AnalysisSufficiencyStatus",
    # Core
    "DecisionFocus",
    "ProvidedMaterial",
    "AnalyticalClaim",
    "ProblemContext",
    # Systems
    "SystemsDynamicsAnalysis",
    # Output
    "FrameworkResult",
    "AnalysisSufficiencySummary",
    "AnalysisResult",
    "ReportSection",
    "DecisionSurface",
    "AnalysisReport",
    # Framework
    "AnalysisFramework",
    # Predefined frameworks
    "SYSTEMS_DYNAMICS_FRAMEWORK",
]
