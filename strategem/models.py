"""Strategem Core - Data Models"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ForceAnalysis(BaseModel):
    """Single force analysis result"""

    level: str = Field(..., pattern="^(Low|Medium|High)$")
    rationale: str
    assumptions: List[str] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)


class PorterAnalysis(BaseModel):
    """Porter's Five Forces analysis result"""

    threat_of_new_entrants: ForceAnalysis = Field(alias="ThreatOfNewEntrants")
    supplier_power: ForceAnalysis = Field(alias="SupplierPower")
    buyer_power: ForceAnalysis = Field(alias="BuyerPower")
    substitutes: ForceAnalysis = Field(alias="Substitutes")
    rivalry: ForceAnalysis = Field(alias="Rivalry")
    overall_observations: str = Field(alias="OverallObservations")
    key_risks: List[str] = Field(alias="KeyRisks", default_factory=list)
    key_strengths: List[str] = Field(alias="KeyStrengths", default_factory=list)


class SystemsDynamicsAnalysis(BaseModel):
    """Systems Dynamics analysis result"""

    system_overview: str = Field(alias="SystemOverview")
    key_components: List[str] = Field(alias="KeyComponents", default_factory=list)
    reinforcing_loops: List[str] = Field(
        alias="FeedbackLoops.Reinforcing", default_factory=list
    )
    balancing_loops: List[str] = Field(
        alias="FeedbackLoops.Balancing", default_factory=list
    )
    bottlenecks: List[str] = Field(alias="Bottlenecks", default_factory=list)
    fragilities: List[str] = Field(alias="Fragilities", default_factory=list)
    assumptions: List[str] = Field(alias="Assumptions", default_factory=list)
    unknowns: List[str] = Field(alias="Unknowns", default_factory=list)


class ProblemContext(BaseModel):
    """Input problem context"""

    raw_content: str
    structured_content: Optional[str] = None
    source_type: str = "text"  # text, document, etc.


class AnalysisResult(BaseModel):
    """Complete analysis result"""

    id: str
    problem_context: ProblemContext
    porter_analysis: Optional[PorterAnalysis] = None
    systems_analysis: Optional[SystemsDynamicsAnalysis] = None
    porter_error: Optional[str] = None
    systems_error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    generated_report: Optional[str] = None


class ReportSection(BaseModel):
    """Report section"""

    title: str
    content: str


class AnalysisReport(BaseModel):
    """Final structured report"""

    id: str
    executive_summary: str
    context_summary: str
    porter_section: ReportSection
    systems_section: ReportSection
    agreement_tension: str
    open_questions: List[str]
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_report: Optional[str] = None  # Full markdown report content
