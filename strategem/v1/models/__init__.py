"""Strategem V1 - Analytical Models

This module contains V1-specific analytical types.
These are NOT shared with V2 - V2 may have different models.

V1 Models:
- Enums: ConfidenceLevel, ClaimSource, DecisionType, etc.
- Core: ProblemContext, DecisionFocus, AnalyticalClaim
- Frameworks: PorterAnalysis, SystemsDynamicsAnalysis, etc.
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
from .porter import (
    ForceEffect,
    ForceAnalysis,
    StructuralAsymmetry,
    PorterAnalysis,
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
PORTER_FRAMEWORK = AnalysisFramework(
    name="porter_five_forces",
    analytical_lens="structural_attractiveness",
    input_requirements=[
        "problem_context",
        "target_system_description",
        "operating_environment_description",
    ],
    prompt_template="porter.txt",
    output_schema={
        "type": "object",
        "properties": {
            "ThreatOfNewEntrants": {"type": "object"},
            "SupplierPower": {"type": "object"},
            "BuyerPower": {"type": "object"},
            "Substitutes": {"type": "object"},
            "Rivalry": {"type": "object"},
            "OverallObservations": {"type": "string"},
            "KeyRisks": {"type": "array"},
            "KeyStrengths": {"type": "array"},
        },
    },
    description="Assesses structural attractiveness of the target system's operating environment",
    requires_decision_focus=True,
)

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
    # Porter
    "ForceEffect",
    "ForceAnalysis",
    "StructuralAsymmetry",
    "PorterAnalysis",
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
    "PORTER_FRAMEWORK",
    "SYSTEMS_DYNAMICS_FRAMEWORK",
]
