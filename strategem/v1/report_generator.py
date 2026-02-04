"""Strategem Core - Report Generator (V1 Compliant)"""

from datetime import datetime
from typing import List, Optional
from .models import (
    AnalysisResult,
    AnalysisReport,
    ReportSection,
    AnalyticalClaim,
    DecisionSurface,
    ClaimSource,
    ConfidenceLevel,
    ClaimType,
    AnalysisSufficiencySummary,
    DecisionBindingStatus,
    CoverageStatus,
    AnalysisSufficiencyStatus,
)


class ReportGenerator:
    """
    Generates structured analytical reports - reasoned artifacts, not recommendations.

    V1 Structure:
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

    def _format_force(self, name: str, force) -> str:
        """Format a single force/pressure analysis"""
        lines = [
            f"### {name}",
            f"**Relevance to Decision:** {force.relevance_to_decision}",
            "",
            f"**Relevance Rationale:** {force.relevance_rationale}",
            "",
        ]

        if force.shared_assumptions:
            lines.append("**Shared Assumptions:**")
            for assumption in force.shared_assumptions:
                lines.append(f"- {assumption}")
            lines.append("")

        if force.shared_unknowns:
            lines.append("**Shared Unknowns:**")
            for unknown in force.shared_unknowns:
                lines.append(f"- {unknown}")
            lines.append("")

        if force.effect_by_option:
            lines.append("**Effect by Option:**")
            for effect in force.effect_by_option:
                lines.append(f"- **{effect.option_name}**: {effect.description}")
                if effect.key_assumptions:
                    lines.append(
                        f"  - Key Assumptions: {', '.join(effect.key_assumptions)}"
                    )
                if effect.key_unknowns:
                    lines.append(f"  - Key Unknowns: {', '.join(effect.key_unknowns)}")
            lines.append("")

        return "\n".join(lines)

    def _extract_claims_from_porter(self, porter) -> List[AnalyticalClaim]:
        """Extract explicit analytical claims from Porter analysis"""
        claims = []

        forces = [
            ("Threat of New Entrants", porter.threat_of_new_entrants),
            ("Supplier Power", porter.supplier_power),
            ("Buyer Power", porter.buyer_power),
            ("Substitutes", porter.substitutes),
            ("Competitive Rivalry", porter.rivalry),
        ]

        for force_name, force in forces:
            # Main claim for each force - system level
            claims.append(
                AnalyticalClaim(
                    statement=f"{force_name}: {force.relevance_to_decision} relevance to decision",
                    source=ClaimSource.INFERENCE,
                    confidence=ConfidenceLevel.MEDIUM,  # Porter analysis is inferential
                    framework="porter_five_forces",
                    claim_type=ClaimType.SYSTEM_LEVEL,
                    applicable_options=["all"],
                )
            )

            # Claims from shared assumptions - system level
            for assumption in force.shared_assumptions:
                claims.append(
                    AnalyticalClaim(
                        statement=assumption,
                        source=ClaimSource.ASSUMPTION,
                        confidence=ConfidenceLevel.LOW,
                        framework="porter_five_forces",
                        claim_type=ClaimType.SYSTEM_LEVEL,
                        applicable_options=["all"],
                    )
                )

        # Extract claims from option-aware claims if available
        if hasattr(porter, "option_aware_claims") and porter.option_aware_claims:
            for claim in porter.option_aware_claims:
                # Determine claim type based on affected options
                claim_type = ClaimType.COMPARATIVE
                applicable_options = (
                    claim.affected_options if claim.affected_options else []
                )

                if len(applicable_options) == 1:
                    claim_type = ClaimType.OPTION_SPECIFIC
                elif not applicable_options:
                    claim_type = ClaimType.SYSTEM_LEVEL
                    applicable_options = ["all"]

                claims.append(
                    AnalyticalClaim(
                        statement=claim.statement,
                        source=claim.source,
                        confidence=claim.confidence,
                        framework="porter_five_forces",
                        claim_type=claim_type,
                        applicable_options=applicable_options,
                    )
                )

        return claims

    def _extract_claims_from_systems(self, systems) -> List[AnalyticalClaim]:
        """Extract explicit analytical claims from Systems Dynamics analysis"""
        claims = []

        # Claims from fragilities - system level
        for fragility in systems.fragilities:
            claims.append(
                AnalyticalClaim(
                    statement=f"System fragility: {fragility}",
                    source=ClaimSource.INFERENCE,
                    confidence=ConfidenceLevel.MEDIUM,
                    framework="systems_dynamics",
                    claim_type=ClaimType.SYSTEM_LEVEL,
                    applicable_options=["all"],
                )
            )

        # Claims from assumptions - system level
        for assumption in systems.assumptions:
            claims.append(
                AnalyticalClaim(
                    statement=assumption,
                    source=ClaimSource.ASSUMPTION,
                    confidence=ConfidenceLevel.LOW,
                    framework="systems_dynamics",
                    claim_type=ClaimType.SYSTEM_LEVEL,
                    applicable_options=["all"],
                )
            )

        return claims

    def _generate_context_summary(self, result: AnalysisResult) -> str:
        """Generate context summary - what was analyzed"""
        lines = ["## Context Summary", ""]

        # Use new formal schema if available, fall back to legacy
        context = result.problem_context

        if context.title and context.title != "Untitled Analysis":
            lines.append(f"**Title:** {context.title}")
            lines.append("")

        lines.append(f"**Problem Statement:** {context.problem_statement}")
        lines.append("")

        if context.objectives:
            lines.append("**Objectives:**")
            for obj in context.objectives:
                lines.append(f"- {obj}")
            lines.append("")

        if context.constraints:
            lines.append("**Constraints:**")
            for constraint in context.constraints:
                lines.append(f"- {constraint}")
            lines.append("")

        if context.declared_assumptions:
            lines.append("**Declared Assumptions:**")
            for assumption in context.declared_assumptions:
                lines.append(f"- {assumption}")
            lines.append("")

        # Materials summary
        if context.provided_materials:
            lines.append(
                f"**Problem Context Materials:** {len(context.provided_materials)} provided"
            )
            for i, material in enumerate(context.provided_materials, 1):
                source_name = material.source if material.source else f"Material {i}"
                lines.append(f"  - {source_name} ({material.material_type})")
            lines.append("")

        # Legacy fallback
        elif context.raw_content:
            content_preview = (
                context.raw_content[:300]
                if len(context.raw_content) > 300
                else context.raw_content
            )
            if len(context.raw_content) > 300:
                content_preview += "..."
            lines.append(f"**Content Preview:** {content_preview}")
            lines.append("")

        return "\n".join(lines)

    def _generate_key_claims_section(
        self, result: AnalysisResult
    ) -> List[AnalyticalClaim]:
        """Generate key analytical claims from all frameworks"""
        all_claims = []

        if result.porter_analysis:
            all_claims.extend(self._extract_claims_from_porter(result.porter_analysis))

        if result.systems_analysis:
            all_claims.extend(
                self._extract_claims_from_systems(result.systems_analysis)
            )

        return all_claims

    def _generate_structural_pressures_section(
        self, result: AnalysisResult
    ) -> ReportSection:
        """
        Generate Structural Pressures section (Operating Environment analysis).

        Uses Porter's Five Forces framework to assess the target system's operating environment.

        V1: Frameworks always run and adapt to context. Missing decision focus reduces depth
        but never invalidates the artifact.
        """
        if not result.porter_analysis:
            return ReportSection(
                title="Structural Pressures (Operating Environment)",
                content="## Structural Pressures (Operating Environment)\n\n*No claims surfaced under current inputs.*",
            )

        porter = result.porter_analysis
        lines = ["## Structural Pressures (Operating Environment)", ""]
        lines.append(
            "*Analysis of the target system's operating environment using structural pressure framework*"
        )
        lines.append("")

        # Display decision question and options being analyzed
        if hasattr(porter, "decision_question") and porter.decision_question:
            lines.append(f"**Decision Question:** {porter.decision_question}")
            lines.append("")

        if hasattr(porter, "options_analyzed") and porter.options_analyzed:
            lines.append("**Options Analyzed:**")
            for option in porter.options_analyzed:
                lines.append(f"- {option}")
            lines.append("")

        lines.append(
            self._format_force(
                "Pressure: New Entrant Threat", porter.threat_of_new_entrants
            )
        )
        lines.append(
            self._format_force("Pressure: Supplier Power", porter.supplier_power)
        )
        lines.append(self._format_force("Pressure: Buyer Power", porter.buyer_power))
        lines.append(
            self._format_force("Pressure: Substitution Threat", porter.substitutes)
        )
        lines.append(
            self._format_force("Pressure: Competitive Intensity", porter.rivalry)
        )

        if porter.overall_observations:
            lines.append("### Overall Operating Environment Characteristics")
            lines.append(porter.overall_observations)
            lines.append("")

        if porter.key_risks:
            lines.append("### Key Structural Risks")
            for risk in porter.key_risks:
                lines.append(f"- {risk}")
            lines.append("")

        if porter.key_strengths:
            lines.append("### Key Structural Strengths")
            for strength in porter.key_strengths:
                lines.append(f"- {strength}")
            lines.append("")

        # Add Structural Asymmetries section
        if hasattr(porter, "structural_asymmetries") and porter.structural_asymmetries:
            lines.append("### Structural Asymmetries")
            for asymmetry in porter.structural_asymmetries:
                lines.append(f"**{asymmetry.force_name}**")
                lines.append(f"- Description: {asymmetry.description}")
                lines.append(f"- Stronger Impact On: {asymmetry.stronger_impact_on}")
                lines.append(f"- Rationale: {asymmetry.rationale}")
                if hasattr(asymmetry, "key_assumption") and asymmetry.key_assumption:
                    lines.append(f"- Key Assumption: {asymmetry.key_assumption}")
                lines.append("")

        # Add Option-Aware Claims section
        if hasattr(porter, "option_aware_claims") and porter.option_aware_claims:
            lines.append("### Option-Aware Claims")
            for claim in porter.option_aware_claims:
                lines.append(f"- **{claim.statement}**")
                if hasattr(claim, "source") and claim.source:
                    lines.append(f"  - Source: {claim.source}")
                if hasattr(claim, "confidence") and claim.confidence:
                    lines.append(f"  - Confidence: {claim.confidence}")
            lines.append("")

        claims = self._extract_claims_from_porter(porter)
        return ReportSection(
            title="Structural Pressures (Operating Environment)",
            content="\n".join(lines),
            claims=claims,
        )

    def _generate_systemic_risks_section(self, result: AnalysisResult) -> ReportSection:
        """
        Generate Systemic Risks section (Target System analysis).

        Uses Systems Dynamics framework to understand target system fragility.

        V1: Frameworks always run and adapt to context. Missing decision focus reduces depth
        but never invalidates the artifact.
        """
        if not result.systems_analysis:
            return ReportSection(
                title="Systemic Risks (Target System)",
                content="## Systemic Risks (Target System)\n\n*No claims surfaced under current inputs.*",
            )

        systems = result.systems_analysis
        lines = ["## Systemic Risks (Target System)", ""]
        lines.append(
            "*Analysis of the target system's internal dynamics, feedback loops, and fragilities*"
        )
        lines.append("")

        lines.append("### Target System Overview")
        lines.append(systems.system_overview)
        lines.append("")

        if systems.key_components:
            lines.append("### Key System Components")
            for component in systems.key_components:
                lines.append(f"- {component}")
            lines.append("")

        if systems.reinforcing_loops:
            lines.append("### Reinforcing Dynamics (Growth Drivers)")
            for loop in systems.reinforcing_loops:
                lines.append(f"- {loop}")
            lines.append("")

        if systems.balancing_loops:
            lines.append("### Balancing Dynamics (Constraints)")
            for loop in systems.balancing_loops:
                lines.append(f"- {loop}")
            lines.append("")

        if systems.bottlenecks:
            lines.append("### System Bottlenecks")
            for bottleneck in systems.bottlenecks:
                lines.append(f"- {bottleneck}")
            lines.append("")

        if systems.fragilities:
            lines.append("### System Fragilities")
            for fragility in systems.fragilities:
                lines.append(f"- {fragility}")
            lines.append("")

        if systems.assumptions:
            lines.append("### Key Assumptions")
            for assumption in systems.assumptions:
                lines.append(f"- {assumption}")
            lines.append("")

        claims = self._extract_claims_from_systems(systems)
        return ReportSection(
            title="Systemic Risks (Target System)",
            content="\n".join(lines),
            claims=claims,
        )

    def _generate_unknowns_and_sensitivities(self, result: AnalysisResult) -> List[str]:
        """Generate Unknowns & Sensitivities section"""
        unknowns = []

        # Collect all unknowns from Porter
        if result.porter_analysis:
            for force in [
                result.porter_analysis.threat_of_new_entrants,
                result.porter_analysis.supplier_power,
                result.porter_analysis.buyer_power,
                result.porter_analysis.substitutes,
                result.porter_analysis.rivalry,
            ]:
                if hasattr(force, "shared_unknowns") and force.shared_unknowns:
                    unknowns.extend(
                        [f"[Operating Environment] {u}" for u in force.shared_unknowns]
                    )

        # Collect unknowns from Systems Dynamics
        if result.systems_analysis and result.systems_analysis.unknowns:
            unknowns.extend(
                [f"[Target System] {u}" for u in result.systems_analysis.unknowns]
            )

        # Remove duplicates while preserving order
        seen = set()
        unique_unknowns = []
        for u in unknowns:
            if u not in seen:
                seen.add(u)
                unique_unknowns.append(u)

        return unique_unknowns

    def _generate_decision_surface(self, result: AnalysisResult) -> DecisionSurface:
        """
        Generate Decision Surface section.

        Explicitly surfaces where judgment is required:
        - What would need to be true for this assessment to change?
        - Which unknowns dominate outcome variance?
        - Where is judgment explicitly required?

        V1 Addition:
        - decision_question and options from context
        - tradeoff_axes identified from framework tension
        - blocked_judgments from framework insufficiency
        """
        assessment_change_conditions = []
        dominant_unknowns = []
        judgment_required_areas = []
        tradeoff_axes = []
        blocked_judgments = []

        decision_question = None
        options = []

        if result.problem_context.decision_focus:
            decision_question = result.problem_context.decision_focus.decision_question
            options = result.problem_context.decision_focus.options

        # From Porter analysis
        if result.porter_analysis:
            # High-relevance forces could change with market shifts
            high_relevance_forces = []
            for force_name, force in [
                ("New Entrant Threat", result.porter_analysis.threat_of_new_entrants),
                ("Supplier Power", result.porter_analysis.supplier_power),
                ("Buyer Power", result.porter_analysis.buyer_power),
                ("Substitution Threat", result.porter_analysis.substitutes),
                ("Competitive Intensity", result.porter_analysis.rivalry),
            ]:
                if (
                    hasattr(force, "relevance_to_decision")
                    and force.relevance_to_decision == "High"
                ):
                    high_relevance_forces.append(force_name)
                    judgment_required_areas.append(
                        f"How to navigate {force_name} relevance"
                    )
                if hasattr(force, "shared_unknowns") and force.shared_unknowns:
                    dominant_unknowns.extend(force.shared_unknowns)

            if high_relevance_forces:
                assessment_change_conditions.append(
                    f"Operating environment relevance would change if: {', '.join(high_relevance_forces)} dynamics shift"
                )

            # Extract tradeoff axes from structural asymmetries
            if hasattr(result.porter_analysis, "structural_asymmetries"):
                for asymmetry in result.porter_analysis.structural_asymmetries:
                    tradeoff_axes.append(f"{asymmetry.force_name} impact asymmetry")

        # From Systems Dynamics
        if result.systems_analysis:
            if result.systems_analysis.fragilities:
                for fragility in result.systems_analysis.fragilities[:3]:  # Top 3
                    judgment_required_areas.append(
                        f"How to address fragility: {fragility}"
                    )

            if result.systems_analysis.unknowns:
                dominant_unknowns.extend(result.systems_analysis.unknowns)

            if result.systems_analysis.bottlenecks:
                assessment_change_conditions.append(
                    "System performance would change if bottlenecks are resolved"
                )

        # Default if no specific insights
        if not judgment_required_areas:
            judgment_required_areas.append(
                "Overall assessment of problem context validity"
            )
            judgment_required_areas.append(
                "Weighting of competing factors across frameworks"
            )

        if not assessment_change_conditions:
            assessment_change_conditions.append(
                "New information about target system or operating environment"
            )

        if not tradeoff_axes:
            tradeoff_axes.append("Information completeness vs analysis timeliness")
            tradeoff_axes.append("Systemic risks vs operational constraints")

        # Deduplicate dominant unknowns
        seen = set()
        unique_unknowns = []
        for u in dominant_unknowns:
            if u not in seen:
                seen.add(u)
                unique_unknowns.append(u)

        return DecisionSurface(
            assessment_change_conditions=assessment_change_conditions,
            dominant_unknowns=unique_unknowns[:5],  # Top 5 most critical
            judgment_required_areas=judgment_required_areas,
            decision_question=decision_question,
            options=options,
            tradeoff_axes=tradeoff_axes,
            blocked_judgments=blocked_judgments,
        )

    def _generate_framework_agreement_tension(self, result: AnalysisResult) -> str:
        """
        Generate Framework Agreement & Tension section.

        Framework disagreement is a VALID and EXPECTED system outcome.
        Lack of consensus between frameworks does not indicate failure.
        """
        lines = [
            "## Framework Agreement & Tension",
            "",
            "*Note: Framework disagreement is a valid and expected system outcome. Lack of consensus between frameworks does not indicate failure.*",
            "",
        ]

        # Check framework results
        porter_complete = result.porter_analysis is not None
        systems_complete = result.systems_analysis is not None

        if not porter_complete and not systems_complete:
            lines.append(
                "*Both framework analyses incomplete - no comparison possible*"
            )
            return "\n".join(lines)

        if not porter_complete:
            lines.append(
                "*Operating Environment analysis incomplete - Systems Dynamics analysis only*"
            )
            return "\n".join(lines)

        if not systems_complete:
            lines.append(
                "*Target System analysis incomplete - Operating Environment analysis only*"
            )
            return "\n".join(lines)

        # Both complete - provide comparison structure
        lines.append("### Points of Agreement")
        lines.append(
            "[Decision Owner to identify where Operating Environment and Target System analyses converge]"
        )
        lines.append("")

        lines.append("### Points of Tension")
        lines.append(
            "[Decision Owner to identify where analyses conflict or highlight different aspects]"
        )
        lines.append(
            "*Example: High competitive pressure (Operating Environment) vs. strong reinforcing growth loops (Target System)*"
        )
        lines.append("")

        lines.append("### Complementary Insights")
        lines.append(
            "[Decision Owner to note how frameworks provide different but compatible perspectives]"
        )
        lines.append("")

        lines.append("### Resolution Required")
        lines.append("The Decision Owner must resolve tensions through:")
        lines.append("- Additional information gathering")
        lines.append(
            "- Explicit judgment calls on which factors to weight more heavily"
        )
        lines.append("- Acceptance of irreducible uncertainty")

        return "\n".join(lines)

    def _generate_pre_decision_observations(self, result: AnalysisResult) -> List[str]:
        """
        Generate Pre-Decision Observations (Non-Analytical).

        V1: Only used when input is genuinely ambiguous (descriptive, speculative, educational).

        These observations MUST NOT include:
        - Framework attribution
        - Confidence scores
        - Option-specific assertions
        - Claims or recommendations

        They should capture:
        - Material characteristics
        - Domain considerations
        - Pre-decision factors to investigate
        - Sources of ambiguity
        - What would be needed to bind a decision
        """
        observations = []

        # Extract material-based observations from context
        if result.problem_context.provided_materials:
            observations.append("Problem context materials were provided and reviewed")

        # Note: Exploratory mode means no decision context was inferable
        observations.append(
            "This input appears to be descriptive or exploratory rather than decision-focused"
        )

        # Suggest what would be needed
        observations.append(
            "To proceed with decision-focused analysis, the input should describe:"
        )
        observations.append("  - A choice to be made (choose, decide, select, etc.)")
        observations.append(
            "  - Multiple alternatives being considered (≥2 distinct options)"
        )
        observations.append(
            "  - A decision owner or context (who is making this decision)"
        )

        # Extract domain considerations from materials
        if result.problem_context.provided_materials:
            for material in result.problem_context.provided_materials:
                if len(material.content) > 100:
                    observations.append(
                        "Context materials contain descriptive information that may inform future analysis"
                    )
                    break

        return observations

    def _generate_analysis_sufficiency_summary(
        self, result: AnalysisResult
    ) -> Optional[AnalysisSufficiencySummary]:
        """
        Generate Analysis Sufficiency Summary section.

        V1 Requirement: Descriptive summary of completeness without evaluation.

        This is extracted from analysis result computed by orchestrator.
        """
        return result.analysis_sufficiency

    def _generate_limitations(self) -> List[str]:
        """Generate explicit limitations documentation"""
        return [
            "No external validation: Analysis is based solely on provided Problem Context Materials",
            "No learning: This analysis does not improve from past outcomes",
            "No ground truth: Framework outputs are not validated against external reality",
            "No domain authority: The system claims no special expertise beyond provided materials",
            "Framework disagreement: Different frameworks may produce conflicting assessments",
            "Assumption-dependent: All inferences rest on explicitly stated and unstated assumptions",
        ]

    def generate_report(self, result: AnalysisResult) -> AnalysisReport:
        """
        Generate complete V1 compliant analysis report.

        V1: This is a reasoned artifact, not a recommendation.
        Decision Focus is inferred, not required.

        Exploratory mode is only for genuinely ambiguous inputs.
        """
        # V1: Check if decision context is genuinely ambiguous
        is_exploratory = (
            result.analysis_sufficiency
            and result.analysis_sufficiency.decision_binding
            == DecisionBindingStatus.GENUINELY_AMBIGUOUS
        )

        # Generate all sections
        context_summary = self._generate_context_summary(result)

        # V1: No analytical claims when genuinely ambiguous
        if is_exploratory:
            key_claims = []
            pre_decision_observations = self._generate_pre_decision_observations(result)
        else:
            key_claims = self._generate_key_claims_section(result)
            pre_decision_observations = None

        # V1: Frameworks always run, decision focus is optional
        # They adapt to context, not the other way around
        structural_pressures = self._generate_structural_pressures_section(result)
        systemic_risks = self._generate_systemic_risks_section(result)

        unknowns = self._generate_unknowns_and_sensitivities(result)
        decision_surface = self._generate_decision_surface(result)
        framework_agreement = self._generate_framework_agreement_tension(result)
        analysis_sufficiency = self._generate_analysis_sufficiency_summary(result)
        limitations = self._generate_limitations()

        # Legacy sections (for backward compatibility)
        porter_section = self._generate_structural_pressures_section(result)
        systems_section = self._generate_systemic_risks_section(result)

        report = AnalysisReport(
            id=result.id,
            context_summary=context_summary,
            key_analytical_claims=key_claims,
            structural_pressures=structural_pressures,
            systemic_risks=systemic_risks,
            unknowns_and_sensitivities=unknowns,
            decision_surface=decision_surface,
            framework_agreement_tension=framework_agreement,
            analysis_sufficiency=analysis_sufficiency,
            limitations=limitations,
            # Legacy fields
            porter_section=porter_section,
            systems_section=systems_section,
            agreement_tension=framework_agreement,
            open_questions=unknowns,
        )

        # Generate full markdown report
        full_report = self._generate_full_markdown(report, pre_decision_observations)
        report.generated_report = full_report

        return report

    def _generate_full_markdown(
        self,
        report: AnalysisReport,
        pre_decision_observations: Optional[List[str]] = None,
    ) -> str:
        """Generate the complete markdown report"""

        # Key claims formatted - or pre-decision observations if applicable
        if pre_decision_observations is not None:
            # V1: Pre-decision mode - no analytical claims
            claims_section = "## Pre-Decision Observations (Non-Analytical)\n\n"
            claims_section += "*The following are pre-decision considerations, NOT analytical claims*\n\n"
            for obs in pre_decision_observations:
                claims_section += f"- {obs}\n"
        else:
            # Normal analysis mode
            claims_section = "## Key Analytical Claims\n\n"
            if report.key_analytical_claims:
                for claim in report.key_analytical_claims[:10]:  # Top 10 claims
                    claims_section += f"- **{claim.statement}**\n"
                    claims_section += f"  - Source: {claim.source.value} | Confidence: {claim.confidence.value} | Framework: {claim.framework}\n"
            else:
                claims_section += "No explicit claims extracted from analysis.\n"

        # Unknowns formatted
        unknowns_section = "## Unknowns & Sensitivities\n\n"
        if report.unknowns_and_sensitivities:
            unknowns_section += f"**Total unknowns identified: {len(report.unknowns_and_sensitivities)}**\n\n"
            for unknown in report.unknowns_and_sensitivities:
                unknowns_section += f"- {unknown}\n"
        else:
            unknowns_section += "No critical unknowns identified.\n"

        # Decision surface formatted
        decision_surface_section = "## Decision Surface\n\n"
        decision_surface_section += "*Where judgment is explicitly required*\n\n"

        decision_surface_section += "### What Would Need to Change?\n"
        for condition in report.decision_surface.assessment_change_conditions:
            decision_surface_section += f"- {condition}\n"
        decision_surface_section += "\n"

        decision_surface_section += "### Dominant Unknowns\n"
        for unknown in report.decision_surface.dominant_unknowns:
            decision_surface_section += f"- {unknown}\n"
        decision_surface_section += "\n"

        decision_surface_section += "### Where Judgment is Required\n"
        for area in report.decision_surface.judgment_required_areas:
            decision_surface_section += f"- {area}\n"

        if report.decision_surface.tradeoff_axes:
            decision_surface_section += "\n### Trade-off Axes\n"
            for axis in report.decision_surface.tradeoff_axes:
                decision_surface_section += f"- {axis}\n"

        if report.decision_surface.blocked_judgments:
            decision_surface_section += "\n### Blocked Judgments\n"
            for blocked in report.decision_surface.blocked_judgments:
                decision_surface_section += f"- {blocked}\n"

        # Analysis Sufficiency formatted
        analysis_sufficiency_section = ""
        if report.analysis_sufficiency:
            analysis_sufficiency_section = "## Analysis Sufficiency Summary\n\n"
            analysis_sufficiency_section += (
                "*Descriptive summary of analysis completeness (V1)*\n\n"
            )

            analysis_sufficiency_section += f"**Decision Context:** {report.analysis_sufficiency.decision_binding.value}\n"
            if report.decision_surface.decision_question:
                analysis_sufficiency_section += f"  - Decision Question: {report.decision_surface.decision_question}\n"
            if report.decision_surface.options:
                analysis_sufficiency_section += (
                    f"  - Options: {', '.join(report.decision_surface.options)}\n"
                )
            analysis_sufficiency_section += "\n"

            analysis_sufficiency_section += f"**Option Coverage:** {report.analysis_sufficiency.option_coverage.value}\n"
            analysis_sufficiency_section += f"**Framework Coverage:** {report.analysis_sufficiency.framework_coverage.value}\n"
            analysis_sufficiency_section += f"**Overall Status:** {report.analysis_sufficiency.overall_status.value}\n\n"

            # V1: Add note for exploratory or constrained analyses
            if (
                report.analysis_sufficiency.overall_status
                != AnalysisSufficiencyStatus.DECISION_RELEVANT_REASONING_PRODUCED
            ):
                if (
                    report.analysis_sufficiency.overall_status
                    == AnalysisSufficiencyStatus.EXPLORATORY_PRE_DECISION
                ):
                    analysis_sufficiency_section += "*Note: This analysis is exploratory. The input was descriptive rather than decision-focused. To proceed with decision analysis, provide a choice context with multiple alternatives.*\n"
                else:
                    analysis_sufficiency_section += "*Note: This analysis is constrained. See Decision Surface for limitations and areas requiring judgment.*\n"

        # Limitations formatted
        limitations_section = "## System Limitations\n\n"
        limitations_section += (
            "This analysis is subject to the following explicit limitations:\n\n"
        )
        for limitation in report.limitations:
            limitations_section += f"- {limitation}\n"

        full_report = f"""# Analytical Report: Reasoned Artifact

 **Analysis ID:** {report.id}
 **Generated:** {report.generated_at.strftime("%Y-%m-%d %H:%M:%S")}

 ---

 **⚠️ CRITICAL DISCLAIMER ⚠️**

 This is a **reasoned artifact**, not a recommendation. This system does NOT:
 - Output decisions
 - Rank options
 - Optimize objectives
 - Make recommendations

 The Decision Owner retains full responsibility for all judgments and decisions.

 ---

 {report.context_summary}

 ---

 {claims_section}

 ---

 {report.structural_pressures.content}

 ---

 {report.systemic_risks.content}

 ---

 {unknowns_section}

 ---

 {report.framework_agreement_tension}

 ---

 {decision_surface_section}

 ---

 {analysis_sufficiency_section}

 ---

 {limitations_section}

 ---

 *This report was generated by Strategem Core v1.0.0*

 *This system is a reasoning scaffold, not an oracle. Framework disagreement is a valid and expected outcome.*
 """

        return full_report

    def save_report(self, report: AnalysisReport, output_path: str = None) -> str:
        """Save report to file"""
        if output_path is None:
            from strategem.core import config

            output_path = config.REPORTS_DIR / f"report_{report.id}.md"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report.generated_report)

        return str(output_path)
