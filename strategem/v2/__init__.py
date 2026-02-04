"""Strategem V2 - Public API

V2 provides enhanced analytical depth:
- Required decision context (no inference)
- All frameworks option-aware
- Cross-framework tension mapping
- Assumption fragility detection
- Structured artefacts as first-class outputs
"""

from .models import (
    # Enums
    ConfidenceLevel,
    TensionType,
    DependencyType,
    SensitivityLevel,
    DecisionType,
    ClaimSource,
    FrameworkExecutionStatus,
    # Core models
    Decision,
    Option,
    AnalyticalClaim,
    OptionEffect,
    Assumption,
    Unknown,
    # Tension models
    FrameworkTension,
    ClaimTension,
    # Dependency models
    AssumptionDependency,
    ClaimDependency,
    # Sensitivity models
    SensitivityTrigger,
    # Output models
    FrameworkResult,
    TensionMapResult,
    AnalysisResult,
    AnalysisArtefact,
    # Framework
    FrameworkContract,
)

from .orchestrator import V2AnalysisOrchestrator
from .tension_mapper import V2TensionMapper
from .artefact_generator import V2ArtefactGenerator
from .frameworks import PORTER_V2_FRAMEWORK, SYSTEMS_DYNAMICS_V2_FRAMEWORK
from .persistence import V2PersistenceLayer

__version__ = "2.0.0-dev"

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
    # Main classes
    "V2AnalysisOrchestrator",
    "V2TensionMapper",
    "V2ArtefactGenerator",
    "V2PersistenceLayer",
    # Predefined frameworks
    "PORTER_V2_FRAMEWORK",
    "SYSTEMS_DYNAMICS_V2_FRAMEWORK",
    # Version
    "__version__",
]
