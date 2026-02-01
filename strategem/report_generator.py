"""Strategem Core - Report Generator"""

from datetime import datetime
from typing import List
from .models import AnalysisResult, AnalysisReport, ReportSection


class ReportGenerator:
    """Generates structured analytical reports"""

    def _format_force(self, name: str, force) -> str:
        """Format a single force analysis"""
        lines = [
            f"### {name}",
            f"**Level:** {force.level}",
            "",
            f"**Rationale:** {force.rationale}",
            "",
        ]

        if force.assumptions:
            lines.append("**Assumptions:**")
            for assumption in force.assumptions:
                lines.append(f"- {assumption}")
            lines.append("")

        if force.unknowns:
            lines.append("**Unknowns:**")
            for unknown in force.unknowns:
                lines.append(f"- {unknown}")
            lines.append("")

        return "\n".join(lines)

    def _generate_executive_summary(self, result: AnalysisResult) -> str:
        """Generate executive summary"""
        lines = ["## Executive Summary", ""]

        # Structural attractiveness
        if result.porter_analysis:
            lines.append("### Structural Attractiveness")
            lines.append(result.porter_analysis.overall_observations)
            lines.append("")

        # System fragility
        if result.systems_analysis:
            lines.append("### System Fragility")
            if result.systems_analysis.fragilities:
                lines.append(
                    f"The business system exhibits {len(result.systems_analysis.fragilities)} key fragilities:"
                )
                for fragility in result.systems_analysis.fragilities[:3]:
                    lines.append(f"- {fragility}")
            else:
                lines.append("No major system fragilities identified.")
            lines.append("")

        # Uncertainty level
        lines.append("### Uncertainty Level")
        uncertainties = []
        if result.porter_analysis:
            for force in [
                result.porter_analysis.threat_of_new_entrants,
                result.porter_analysis.supplier_power,
                result.porter_analysis.buyer_power,
                result.porter_analysis.substitutes,
                result.porter_analysis.rivalry,
            ]:
                if force.unknowns:
                    uncertainties.extend(force.unknowns)

        if result.systems_analysis and result.systems_analysis.unknowns:
            uncertainties.extend(result.systems_analysis.unknowns)

        if uncertainties:
            lines.append(
                f"High uncertainty: {len(set(uncertainties))} distinct unknowns identified across analyses."
            )
        else:
            lines.append("Uncertainty level: Low (sufficient information available)")

        return "\n".join(lines)

    def _generate_context_summary(self, result: AnalysisResult) -> str:
        """Generate context summary"""
        content = result.problem_context.raw_content
        # Take first 500 chars as summary, or full content if shorter
        summary = content[:500] if len(content) > 500 else content
        if len(content) > 500:
            summary += "..."

        return f"## Context Summary\n\n{summary}\n\n*Source: {result.problem_context.source_type}*"

    def _generate_porter_section(self, result: AnalysisResult) -> ReportSection:
        """Generate Porter's Five Forces section"""
        if not result.porter_analysis:
            return ReportSection(
                title="Porter's Five Forces Analysis",
                content="## Porter's Five Forces Analysis\n\n*Analysis incomplete due to error*",
            )

        porter = result.porter_analysis
        lines = ["## Porter's Five Forces Analysis", ""]

        lines.append(
            self._format_force(
                "1. Threat of New Entrants", porter.threat_of_new_entrants
            )
        )
        lines.append(
            self._format_force(
                "2. Bargaining Power of Suppliers", porter.supplier_power
            )
        )
        lines.append(
            self._format_force("3. Bargaining Power of Buyers", porter.buyer_power)
        )
        lines.append(self._format_force("4. Threat of Substitutes", porter.substitutes))
        lines.append(self._format_force("5. Competitive Rivalry", porter.rivalry))

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

        return ReportSection(
            title="Porter's Five Forces Analysis", content="\n".join(lines)
        )

    def _generate_systems_section(self, result: AnalysisResult) -> ReportSection:
        """Generate Systems Dynamics section"""
        if not result.systems_analysis:
            return ReportSection(
                title="Systems Dynamics Analysis",
                content="## Systems Dynamics Analysis\n\n*Analysis incomplete due to error*",
            )

        systems = result.systems_analysis
        lines = ["## Systems Dynamics Analysis", ""]

        lines.append("### System Overview")
        lines.append(systems.system_overview)
        lines.append("")

        if systems.key_components:
            lines.append("### Key Components")
            for component in systems.key_components:
                lines.append(f"- {component}")
            lines.append("")

        if systems.reinforcing_loops:
            lines.append("### Reinforcing Feedback Loops (Growth Drivers)")
            for loop in systems.reinforcing_loops:
                lines.append(f"- {loop}")
            lines.append("")

        if systems.balancing_loops:
            lines.append("### Balancing Feedback Loops (Constraints)")
            for loop in systems.balancing_loops:
                lines.append(f"- {loop}")
            lines.append("")

        if systems.bottlenecks:
            lines.append("### Bottlenecks & Constraints")
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

        return ReportSection(
            title="Systems Dynamics Analysis", content="\n".join(lines)
        )

    def _generate_agreement_tension(self, result: AnalysisResult) -> str:
        """Generate agreement and tension section"""
        lines = ["## Agreement & Tension Between Frameworks", ""]

        if not result.porter_analysis or not result.systems_analysis:
            lines.append(
                "*Cannot compare frameworks - one or both analyses incomplete*"
            )
            return "\n".join(lines)

        # This is a manual comparison - just provide structure for analyst to fill in
        lines.append("### Points of Agreement")
        lines.append(
            "[Analyst to identify where Porter and Systems analyses converge on key insights]"
        )
        lines.append("")

        lines.append("### Points of Tension")
        lines.append(
            "[Analyst to identify where analyses conflict or highlight different aspects]"
        )
        lines.append("")

        lines.append("### Complementary Insights")
        lines.append(
            "[Analyst to note how the frameworks provide different but compatible perspectives]"
        )

        return "\n".join(lines)

    def _generate_open_questions(self, result: AnalysisResult) -> List[str]:
        """Generate open questions section"""
        questions = []

        # Collect all unknowns
        if result.porter_analysis:
            for force in [
                result.porter_analysis.threat_of_new_entrants,
                result.porter_analysis.supplier_power,
                result.porter_analysis.buyer_power,
                result.porter_analysis.substitutes,
                result.porter_analysis.rivalry,
            ]:
                if force.unknowns:
                    questions.extend(force.unknowns)

        if result.systems_analysis and result.systems_analysis.unknowns:
            questions.extend(result.systems_analysis.unknowns)

        # Remove duplicates while preserving order
        seen = set()
        unique_questions = []
        for q in questions:
            if q not in seen:
                seen.add(q)
                unique_questions.append(q)

        return unique_questions

    def generate_report(self, result: AnalysisResult) -> AnalysisReport:
        """Generate complete analysis report"""
        open_questions = self._generate_open_questions(result)

        # Build open questions section
        open_questions_section = "## Open Questions & Missing Information\n\n"
        if open_questions:
            for question in open_questions:
                open_questions_section += f"- {question}\n"
        else:
            open_questions_section += "No critical unknowns identified.\n"

        report = AnalysisReport(
            id=result.id,
            executive_summary=self._generate_executive_summary(result),
            context_summary=self._generate_context_summary(result),
            porter_section=self._generate_porter_section(result),
            systems_section=self._generate_systems_section(result),
            agreement_tension=self._generate_agreement_tension(result),
            open_questions=open_questions,
        )

        # Generate full markdown
        full_report = f"""# Strategic Analysis Report

**Analysis ID:** {report.id}  
**Generated:** {report.generated_at.strftime("%Y-%m-%d %H:%M:%S")}

---

{report.executive_summary}

---

{report.context_summary}

---

{report.porter_section.content}

---

{report.systems_section.content}

---

{report.agreement_tension}

---

{open_questions_section}

---

*This report was generated by Strategem Core. It provides analytical structure and does not constitute investment advice.*
"""

        report.generated_report = full_report
        return report

    def save_report(self, report: AnalysisReport, output_path: str = None) -> str:
        """Save report to file"""
        if output_path is None:
            from .config import config

            output_path = config.REPORTS_DIR / f"report_{report.id}.md"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report.generated_report)

        return str(output_path)
