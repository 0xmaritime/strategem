"""Strategem V1 - Output Models"""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from .enums import (
    FrameworkExecutionStatus,
    DecisionBindingStatus,
    CoverageStatus,
    AnalysisSufficiencyStatus,
)
from .core import AnalyticalClaim, ProblemContext


class FrameworkResult(BaseModel):
    """Generic container for any framework's analysis result"""

    framework_name: str
    success: bool
    result: Optional[Any] = None
    error_message: Optional[str] = None
    claims: List[AnalyticalClaim] = Field(default_factory=list)
    execution_status: FrameworkExecutionStatus = Field(
        default=FrameworkExecutionStatus.SUCCESSFUL,
        description="Execution status: successful, insufficient, or failed",
    )
    execution_reason: Optional[str] = Field(
        None, description="Reason for execution status if not successful"
    )


class AnalysisSufficiencySummary(BaseModel):
    """
    Analysis Sufficiency Summary - V1 completeness indicator.

    This section is descriptive only, not evaluative. It describes
    completeness of the analysis without making judgments.
    """

    decision_binding: DecisionBindingStatus = Field(
        ...,
        description="Status of decision focus binding: explicit, derived, or insufficient",
    )
    option_coverage: CoverageStatus = Field(
        ..., description="Coverage of decision options: complete or partial"
    )
    framework_coverage: CoverageStatus = Field(
        ..., description="Coverage of frameworks: complete or partial"
    )
    overall_status: AnalysisSufficiencyStatus = Field(
        ...,
        description="Overall sufficiency: sufficient, constrained, or exploratory_only",
    )


class AnalysisResult(BaseModel):
    """
    Complete analysis result.

    Contains results from all frameworks applied to a problem context.
    Framework disagreement is a valid and expected outcome.
    """

    id: str
    problem_context: ProblemContext

    # Framework results (legacy specific fields)
    porter_analysis: Optional[Any] = None
    systems_analysis: Optional[Any] = None
    porter_error: Optional[str] = None
    systems_error: Optional[str] = None

    # Generic framework results (V1 compliant)
    framework_results: List[FrameworkResult] = Field(
        default_factory=list, description="Results from all applied frameworks"
    )

    # V1 completeness hardening
    analysis_sufficiency: Optional[AnalysisSufficiencySummary] = Field(
        None, description="Summary of analysis completeness and binding"
    )

    created_at: datetime = Field(default_factory=datetime.now)
    generated_report: Optional[str] = None


class ReportSection(BaseModel):
    """Report section"""

    title: str
    content: str
    claims: List[AnalyticalClaim] = Field(default_factory=list)


class DecisionSurface(BaseModel):
    """
    Decision Surface - explicitly surfaces where judgment is required.

    This section answers:
    - What would need to be true for this assessment to change?
    - Which unknowns dominate outcome variance?
    - Where is judgment explicitly required?

    This prevents the system from becoming a pseudo-oracle.
    """

    assessment_change_conditions: List[str] = Field(
        default_factory=list,
        description="What would need to be true for this assessment to change",
    )
    dominant_unknowns: List[str] = Field(
        default_factory=list, description="Which unknowns dominate outcome variance"
    )
    judgment_required_areas: List[str] = Field(
        default_factory=list, description="Where is judgment explicitly required"
    )

    decision_question: Optional[str] = Field(
        None, description="The decision question being addressed"
    )
    options: List[str] = Field(
        default_factory=list, description="The options under consideration"
    )
    tradeoff_axes: List[str] = Field(
        default_factory=list,
        description="Trade-off axes identified (e.g., 'Transparency vs Flexibility')",
    )
    blocked_judgments: List[str] = Field(
        default_factory=list,
        description="Judgments that are blocked due to insufficiency",
    )


class AnalysisReport(BaseModel):
    """
    Final structured report - a reasoned artifact, not a recommendation.

    This report provides:
    - Context Summary: What was analyzed
    - Key Analytical Claims: Explicit claims with sources and confidence
    - Structural Pressures: Operating environment analysis
    - Systemic Risks: Target system fragilities
    - Unknowns & Sensitivities: Explicit uncertainty
    - Decision Surface: Where judgment is required
    - Analysis Sufficiency Summary: V1 completeness indicator

    This system does NOT:
    - Output decisions
    - Rank options
    - Optimize objectives
    - Make recommendations
    """

    id: str

    # V1 Compliant report structure
    context_summary: str
    key_analytical_claims: List[AnalyticalClaim]
    structural_pressures: ReportSection  # Porter/Operating Environment
    systemic_risks: ReportSection  # Systems Dynamics/Target System
    unknowns_and_sensitivities: List[str]
    decision_surface: DecisionSurface

    # Framework agreement/disagreement (explicitly acknowledged)
    framework_agreement_tension: str = Field(
        ..., description="Points of agreement and tension between frameworks"
    )

    # Analysis Sufficiency Summary (V1 new section)
    analysis_sufficiency: Optional[AnalysisSufficiencySummary] = Field(
        None, description="Summary of analysis completeness and binding"
    )

    # Legacy fields (maintained during migration)
    executive_summary: Optional[str] = Field(
        None, description="[Legacy] Replaced by context_summary + key_analytical_claims"
    )
    porter_section: Optional[ReportSection] = None
    systems_section: Optional[ReportSection] = None
    agreement_tension: Optional[str] = None
    open_questions: Optional[List[str]] = Field(default_factory=list)

    generated_at: datetime = Field(default_factory=datetime.now)
    generated_report: Optional[str] = None  # Full markdown report content

    # Explicit limitations
    limitations: List[str] = Field(
        default_factory=list, description="Explicitly documented system limitations"
    )


__all__ = [
    "FrameworkResult",
    "AnalysisSufficiencySummary",
    "AnalysisResult",
    "ReportSection",
    "DecisionSurface",
    "AnalysisReport",
]
