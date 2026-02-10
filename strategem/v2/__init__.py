"""Strategem V2 - Public API (Reasoning Substrate)

V2 provides judgment externalization:
- Optional decision context (implicit decisions supported)
- Frameworks as primitive emitters only
- Reasoning substrate for cross-framework interaction
- Explicit judgment nodes (derived, not emitted)
- Framework toggleability without system breakage
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
from .frameworks import SYSTEMS_DYNAMICS_V2_FRAMEWORK
from .persistence import V2PersistenceLayer
from .normalization import V2ResponseNormalizer

# New V2 components (Reasoning Substrate)
from .substrate import (
    ReasoningGraph,
    SubstrateIngestor,
    IngestionResult,
)
from .framework_adapters import SystemsDynamicsAdapter
from .judgment import (
    JudgmentNode,
    Stance,
    JudgmentTriggerType,
    JudgmentDeriver,
    DerivationResult,
)
from .artefacts import (
    ArtefactExporter,
    ReasoningPrimitivesArtefact,
    JudgmentSurfaceArtefact,
    OptionAnnotationsArtefact,
)

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
    "V2ResponseNormalizer",
    # Predefined frameworks
    "SYSTEMS_DYNAMICS_V2_FRAMEWORK",
    # New V2 components (Reasoning Substrate)
    "ReasoningGraph",
    "SubstrateIngestor",
    "IngestionResult",
    "SystemsDynamicsAdapter",
    "JudgmentNode",
    "Stance",
    "JudgmentTriggerType",
    "JudgmentDeriver",
    "DerivationResult",
    "ArtefactExporter",
    "ReasoningPrimitivesArtefact",
    "JudgmentSurfaceArtefact",
    "OptionAnnotationsArtefact",
    # Version
    "__version__",
]
