"""Strategem Core - Main Package (V1 Compliant)"""

__version__ = "1.0.0"
__author__ = "Strategem Team"

from .models import (
    ProblemContext,
    AnalysisResult,
    PorterAnalysis,
    SystemsDynamicsAnalysis,
    AnalysisReport,
    AnalyticalClaim,
    AnalysisFramework,
    ProvidedMaterial,
    FrameworkResult,
    DecisionSurface,
    ClaimSource,
    ConfidenceLevel,
    DecisionFocus,
    DecisionType,
    ForceEffect,
    StructuralAsymmetry,
    DecisionFocusStatus,
    ClaimType,
    FrameworkExecutionStatus,
    DecisionBindingStatus,
    CoverageStatus,
    AnalysisSufficiencyStatus,
    AnalysisSufficiencySummary,
    PORTER_FRAMEWORK,
    SYSTEMS_DYNAMICS_FRAMEWORK,
)
from .context_ingestion import ContextIngestionModule
from .orchestrator import AnalysisOrchestrator
from .report_generator import ReportGenerator
from .persistence import PersistenceLayer
from .decision_focus_extractor import DecisionFocusExtractor

__all__ = [
    "ProblemContext",
    "AnalysisResult",
    "PorterAnalysis",
    "SystemsDynamicsAnalysis",
    "AnalysisReport",
    "AnalyticalClaim",
    "AnalysisFramework",
    "ProvidedMaterial",
    "FrameworkResult",
    "DecisionSurface",
    "ClaimSource",
    "ConfidenceLevel",
    "DecisionFocus",
    "DecisionType",
    "ForceEffect",
    "StructuralAsymmetry",
    "DecisionFocusStatus",
    "ClaimType",
    "FrameworkExecutionStatus",
    "DecisionBindingStatus",
    "CoverageStatus",
    "AnalysisSufficiencyStatus",
    "AnalysisSufficiencySummary",
    "PORTER_FRAMEWORK",
    "SYSTEMS_DYNAMICS_FRAMEWORK",
    "ContextIngestionModule",
    "AnalysisOrchestrator",
    "ReportGenerator",
    "PersistenceLayer",
    "DecisionFocusExtractor",
]
