"""Strategem Core - Data Models (V1 Compliant)"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence levels for analytical claims"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ClaimSource(str, Enum):
    """Source of an analytical claim"""

    INPUT = "input"
    ASSUMPTION = "assumption"
    INFERENCE = "inference"


class AnalyticalClaim(BaseModel):
    """
    An explicit analytical claim produced by a framework.

    This is the backbone of explainability and auditability.
    Each claim must be traceable to its source and have explicit confidence.
    """

    statement: str = Field(..., description="The claim statement")
    source: ClaimSource = Field(
        ..., description="Source: input, assumption, or inference"
    )
    confidence: ConfidenceLevel = Field(
        ..., description="Confidence level: low, medium, or high"
    )
    framework: Optional[str] = Field(
        None, description="Which framework produced this claim"
    )


class ProvidedMaterial(BaseModel):
    """A single piece of provided context material"""

    material_type: str = Field(..., description="Type: document, text, data, etc.")
    content: str = Field(..., description="The material content or reference")
    source: Optional[str] = Field(None, description="Source identifier or filename")


class ProblemContext(BaseModel):
    """
    First-class Problem Context object - the root abstraction of the system.

    This formalizes the problem being analyzed, independent of domain.
    A reader must be able to imagine applying Strategem Core to:
    - a policy decision
    - an operational failure
    - a product strategy
    - a target system evaluation

    without mental friction.
    """

    # Core problem definition
    title: str = Field(..., description="Title or identifier for this problem context")
    problem_statement: str = Field(
        ..., description="Clear statement of the problem being analyzed"
    )

    # Problem scope
    objectives: List[str] = Field(
        default_factory=list, description="What the decision owner is trying to achieve"
    )
    constraints: List[str] = Field(
        default_factory=list, description="Known limitations or boundaries"
    )

    # Input materials
    provided_materials: List[ProvidedMaterial] = Field(
        default_factory=list,
        description="Problem Context Materials provided for analysis",
    )

    # Optional explicit assumptions
    declared_assumptions: List[str] = Field(
        default_factory=list,
        description="Assumptions explicitly declared by the decision owner",
    )

    # Legacy fields (maintained for backward compatibility during migration)
    raw_content: Optional[str] = Field(None, description="[Legacy] Raw input content")
    structured_content: Optional[str] = Field(
        None, description="[Legacy] Structured/processed content"
    )
    source_type: str = Field(
        "text", description="[Legacy] Source type: text, document, etc."
    )

    class Config:
        populate_by_name = True


class AnalysisFramework(BaseModel):
    """
    Formal Framework interface - frameworks must be swappable without touching orchestration logic.

    This enables:
    - Adding new frameworks without code changes
    - Swapping frameworks for different analytical lenses
    - Pivoting between problem types
    """

    name: str = Field(
        ...,
        description="Framework identifier (e.g., 'porter_five_forces', 'systems_dynamics')",
    )
    analytical_lens: str = Field(
        ...,
        description="What this framework reveals (e.g., 'structural attractiveness', 'systemic fragility')",
    )
    input_requirements: List[str] = Field(
        default_factory=list, description="What input this framework requires"
    )
    prompt_template: str = Field(..., description="Path to the prompt template file")
    output_schema: Dict[str, Any] = Field(
        default_factory=dict, description="JSON schema for expected output"
    )
    description: Optional[str] = Field(None, description="Human-readable description")


class ForceAnalysis(BaseModel):
    """Single force/pressure analysis result within an operating environment"""

    level: str = Field(..., pattern="^(Low|Medium|High)$")
    rationale: str
    assumptions: List[str] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)
    claims: List[AnalyticalClaim] = Field(
        default_factory=list, description="Explicit claims derived from this analysis"
    )


class PorterAnalysis(BaseModel):
    """
    Operating Environment Structure analysis (Porter's Five Forces framework).

    Assesses structural attractiveness of the target system's operating environment.

    Note: Framework disagreement is a valid and expected system outcome.
    Lack of consensus between frameworks does not indicate failure.
    """

    threat_of_new_entrants: ForceAnalysis = Field(alias="ThreatOfNewEntrants")
    supplier_power: ForceAnalysis = Field(alias="SupplierPower")
    buyer_power: ForceAnalysis = Field(alias="BuyerPower")
    substitutes: ForceAnalysis = Field(alias="Substitutes")
    rivalry: ForceAnalysis = Field(alias="Rivalry")
    overall_observations: str = Field(alias="OverallObservations")
    key_risks: List[str] = Field(alias="KeyRisks", default_factory=list)
    key_strengths: List[str] = Field(alias="KeyStrengths", default_factory=list)
    claims: List[AnalyticalClaim] = Field(
        default_factory=list, description="Key analytical claims from this framework"
    )


class SystemsDynamicsAnalysis(BaseModel):
    """
    Target System Dynamics analysis (Qualitative Systems Dynamics framework).

    Understands feedback loops, dependencies, and fragility of the target system.

    Note: Framework disagreement is a valid and expected system outcome.
    Lack of consensus between frameworks does not indicate failure.
    """

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
    claims: List[AnalyticalClaim] = Field(
        default_factory=list, description="Key analytical claims from this framework"
    )


class FrameworkResult(BaseModel):
    """Generic container for any framework's analysis result"""

    framework_name: str
    success: bool
    result: Optional[Any] = None
    error_message: Optional[str] = None
    claims: List[AnalyticalClaim] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    """
    Complete analysis result.

    Contains results from all frameworks applied to a problem context.
    Framework disagreement is a valid and expected outcome.
    """

    id: str
    problem_context: ProblemContext

    # Framework results (legacy specific fields)
    porter_analysis: Optional[PorterAnalysis] = None
    systems_analysis: Optional[SystemsDynamicsAnalysis] = None
    porter_error: Optional[str] = None
    systems_error: Optional[str] = None

    # Generic framework results (V1 compliant)
    framework_results: List[FrameworkResult] = Field(
        default_factory=list, description="Results from all applied frameworks"
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


# Predefined framework configurations
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
