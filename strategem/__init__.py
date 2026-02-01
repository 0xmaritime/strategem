"""Strategem Core - Main Package"""

__version__ = "1.0.0"
__author__ = "Strategem Team"

from .models import (
    ProblemContext,
    AnalysisResult,
    PorterAnalysis,
    SystemsDynamicsAnalysis,
    AnalysisReport,
)
from .context_ingestion import ContextIngestionModule
from .orchestrator import AnalysisOrchestrator
from .report_generator import ReportGenerator
from .persistence import PersistenceLayer

__all__ = [
    "ProblemContext",
    "AnalysisResult",
    "PorterAnalysis",
    "SystemsDynamicsAnalysis",
    "AnalysisReport",
    "ContextIngestionModule",
    "AnalysisOrchestrator",
    "ReportGenerator",
    "PersistenceLayer",
]
