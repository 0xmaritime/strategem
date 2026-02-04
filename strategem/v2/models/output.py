"""Strategem V2 - Output Models"""

from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from .enums import FrameworkExecutionStatus
from .core import Decision, AnalyticalClaim
from .tension import FrameworkTension
from .sensitivity import SensitivityTrigger


class FrameworkResult(BaseModel):
    """Result from a single framework execution (V2)"""

    framework_name: str
    success: bool
    execution_status: FrameworkExecutionStatus = Field(
        default=FrameworkExecutionStatus.SUCCESSFUL,
        description="Execution status: successful, insufficient, or failed",
    )
    execution_reason: Optional[str] = Field(
        None, description="Reason for execution status if not successful"
    )
    result: Optional[Any] = Field(None, description="Framework-specific result data")
    claims: List[AnalyticalClaim] = Field(
        default_factory=list, description="Claims produced by this framework"
    )
    assumptions: List[str] = Field(
        default_factory=list, description="Assumptions made by this framework"
    )
    unknowns: List[str] = Field(
        default_factory=list, description="Unknowns identified by this framework"
    )


class TensionMapResult(BaseModel):
    """
    Result of cross-framework tension mapping (V2).

    V2: Tension mapping is explicit, not implicit.
    """

    framework_tensions: List[FrameworkTension] = Field(
        ..., description="Tensions identified between frameworks"
    )
    agreement_areas: List[str] = Field(
        default_factory=list, description="Areas where frameworks agree"
    )
    tension_areas: List[str] = Field(
        default_factory=list, description="Areas where frameworks are in tension"
    )
    contradiction_areas: List[str] = Field(
        default_factory=list, description="Areas where frameworks contradict"
    )
    summary: str = Field(
        ..., description="Human-readable summary of framework relationships"
    )


class AnalysisResult(BaseModel):
    """
    Complete analysis result (V2).

    V2: Includes explicit decision context, framework results,
    tension mapping, and sensitivity triggers.
    """

    analysis_id: str
    decision: Decision
    options_analyzed: List[str]
    framework_results: List[FrameworkResult]
    tension_map: Optional[TensionMapResult] = Field(
        None, description="Cross-framework tension mapping"
    )
    sensitivity_triggers: List[SensitivityTrigger] = Field(
        default_factory=list,
        description="Sensitivities that would change the assessment",
    )
    created_at: datetime = Field(default_factory=datetime.now)


class AnalysisArtefact(BaseModel):
    """
    First-class analytical artefact (V2).

    V2: Artefacts are structured, versioned, and auditable.
    They represent the reasoned artifact produced by the system.
    """

    artefact_id: str
    analysis_id: str
    artefact_type: str = Field(
        ...,
        description="Type of artefact (e.g., 'option_report', 'tension_map', 'sensitivity_analysis')",
    )
    version: str = Field(
        ..., description="Strategem version that produced this artefact"
    )
    content: Dict[str, Any] = Field(
        ..., description="Structured content of the artefact"
    )
    generated_at: datetime = Field(default_factory=datetime.now)
    content_hash: Optional[str] = Field(
        None, description="Hash of content for integrity verification"
    )


__all__ = [
    "FrameworkResult",
    "TensionMapResult",
    "AnalysisResult",
    "AnalysisArtefact",
]
