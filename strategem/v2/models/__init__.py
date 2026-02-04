"""Strategem V2 - Analytical Models

V2 models represent the enhanced analytical depth required by V2.
These are separate from V1 models and may have different structure and semantics.

V2 Key Changes from V1:
- Decision Focus is REQUIRED (no inference)
- All frameworks MUST be option-aware
- Cross-framework tension mapping
- Assumption fragility detection
- Structured artefacts as first-class outputs
"""

from .enums import (
    ConfidenceLevel,
    TensionType,
    DependencyType,
    SensitivityLevel,
    DecisionType,
    ClaimSource,
    FrameworkExecutionStatus,
)

from .core import (
    Decision,
    Option,
    AnalyticalClaim,
    OptionEffect,
    Assumption,
    Unknown,
)

from .tension import (
    FrameworkTension,
    ClaimTension,
)

from .dependency import (
    AssumptionDependency,
    ClaimDependency,
)

from .sensitivity import (
    SensitivityTrigger,
)

from .output import (
    FrameworkResult,
    TensionMapResult,
    AnalysisResult,
    AnalysisArtefact,
)

from .framework import (
    FrameworkContract,
)

from .porter import (
    PorterAnalysisV2,
    StructuralAsymmetry,
    PorterForce,
    ForceEffect,
)

from .systems import (
    SystemsDynamicsAnalysisV2,
    FeedbackLoop,
    Bottleneck,
    Fragility,
)

__all__ = [
    # Enums
    "ConfidenceLevel",
    "TensionType",
    "DependencyType",
    "SensitivityLevel",
    "DecisionType",
    "ClaimSource",
    "FrameworkExecutionStatus",
    # Core models
    "Decision",
    "Option",
    "AnalyticalClaim",
    "OptionEffect",
    "Assumption",
    "Unknown",
    # Tension models
    "FrameworkTension",
    "ClaimTension",
    # Dependency models
    "AssumptionDependency",
    "ClaimDependency",
    # Sensitivity models
    "SensitivityTrigger",
    # Output models
    "FrameworkResult",
    "TensionMapResult",
    "AnalysisResult",
    "AnalysisArtefact",
    # Framework
    "FrameworkContract",
    # Framework models
    "PorterAnalysisV2",
    "StructuralAsymmetry",
    "PorterForce",
    "ForceEffect",
    "SystemsDynamicsAnalysisV2",
    "FeedbackLoop",
    "Bottleneck",
    "Fragility",
]
