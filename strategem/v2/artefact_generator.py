"""Strategem V2 - Artefact Generator (V2 Specific)"""

import hashlib
import json
from typing import List, Optional, Dict, Any

from .models import (
    AnalysisArtefact,
    AnalysisResult,
    Decision,
    Option,
    FrameworkResult,
    TensionMapResult,
    SensitivityTrigger,
)
from strategem.core import generate_id, V2_VERSION


class V2ArtefactGenerator:
    """
    Generates structured analytical artefacts (V2).

    V2: Artefacts are first-class outputs.
    Structured (JSON), versioned, auditable, comparable.
    """

    def generate_all_artefacts(
        self,
        analysis_id: str,
        decision: Decision,
        options: List[Option],
        framework_results: List[FrameworkResult],
        tension_map: Optional[TensionMapResult] = None,
    ) -> List[AnalysisArtefact]:
        """
        Generate all artefact types for an analysis.

        V2: Produce multiple structured artefacts.
        """
        artefacts = []

        artefact = self.generate_option_report(
            analysis_id, decision, options, framework_results
        )
        if artefact:
            artefacts.append(artefact)

        if tension_map:
            artefact = self.generate_tension_map_artefact(analysis_id, tension_map)
            if artefact:
                artefacts.append(artefact)

        artefact = self.generate_assumption_dependency_artefact(
            analysis_id, framework_results
        )
        if artefact:
            artefacts.append(artefact)

        artefact = self.generate_claim_dependency_artefact(
            analysis_id, framework_results
        )
        if artefact:
            artefacts.append(artefact)

        artefact = self.generate_analysis_sufficiency_artefact(
            analysis_id, decision, options, framework_results
        )
        if artefact:
            artefacts.append(artefact)

        return artefacts

    def generate_option_report(
        self,
        analysis_id: str,
        decision: Decision,
        options: List[Option],
        framework_results: List[FrameworkResult],
    ) -> Optional[AnalysisArtefact]:
        """Generate option-aware report artefact"""
        option_names = [opt.name for opt in options]

        content = {
            "decision_question": decision.decision_question,
            "decision_type": decision.decision_type.value,
            "options_analyzed": option_names,
            "option_summaries": {},
        }

        for opt_name in option_names:
            content["option_summaries"][opt_name] = {
                "framework_insights": [],
                "claims_affecting_option": [],
                "assumptions_affecting_option": [],
                "unknowns_affecting_option": [],
            }

        for fw_result in framework_results:
            if fw_result.success:
                for claim in fw_result.claims:
                    for opt_name in claim.affected_options:
                        if opt_name in content["option_summaries"]:
                            content["option_summaries"][opt_name][
                                "claims_affecting_option"
                            ].append(
                                {
                                    "statement": claim.statement,
                                    "framework": claim.framework,
                                    "confidence": claim.confidence.value,
                                    "source": claim.source.value,
                                }
                            )

                for assumption in fw_result.assumptions:
                    for opt_name in option_names:
                        if opt_name in content["option_summaries"]:
                            content["option_summaries"][opt_name][
                                "assumptions_affecting_option"
                            ].append(
                                {
                                    "statement": assumption,
                                    "framework": fw_result.framework_name,
                                }
                            )

                for unknown in fw_result.unknowns:
                    for opt_name in option_names:
                        if opt_name in content["option_summaries"]:
                            content["option_summaries"][opt_name][
                                "unknowns_affecting_option"
                            ].append(
                                {
                                    "statement": unknown,
                                    "framework": fw_result.framework_name,
                                }
                            )

        return self._create_artefact(analysis_id, "option_report", content)

    def generate_tension_map_artefact(
        self, analysis_id: str, tension_map: TensionMapResult
    ) -> Optional[AnalysisArtefact]:
        """Generate tension map artefact"""
        content = {
            "framework_tensions": [],
            "agreement_areas": tension_map.agreement_areas,
            "tension_areas": tension_map.tension_areas,
            "contradiction_areas": tension_map.contradiction_areas,
            "summary": tension_map.summary,
        }

        for ft in tension_map.framework_tensions:
            content["framework_tensions"].append(
                {
                    "framework_1": ft.framework_1,
                    "framework_2": ft.framework_2,
                    "tension_type": ft.tension_type.value,
                    "summary": ft.summary,
                    "resolution_areas": ft.resolution_areas,
                    "claim_tensions": [
                        {
                            "claim_1_id": ct.claim_1_id,
                            "claim_1_framework": ct.claim_1_framework,
                            "claim_2_id": ct.claim_2_id,
                            "claim_2_framework": ct.claim_2_framework,
                            "tension_type": ct.tension_type.value,
                            "description": ct.description,
                            "affected_options": ct.affected_options,
                        }
                        for ct in ft.claim_tensions
                    ],
                }
            )

        return self._create_artefact(analysis_id, "tension_map", content)

    def generate_assumption_dependency_artefact(
        self, analysis_id: str, framework_results: List[FrameworkResult]
    ) -> Optional[AnalysisArtefact]:
        """Generate assumption dependency map artefact"""
        content = {
            "assumptions_by_framework": {},
            "shared_assumptions": [],
            "single_point_failures": [],
        }

        all_assumptions = []

        for fw_result in framework_results:
            if fw_result.success:
                content["assumptions_by_framework"][fw_result.framework_name] = (
                    fw_result.assumptions
                )
                all_assumptions.extend(fw_result.assumptions)

        assumption_counts = {}
        for assumption in all_assumptions:
            assumption_counts[assumption] = assumption_counts.get(assumption, 0) + 1

        shared_assumptions = [
            assumption for assumption, count in assumption_counts.items() if count > 1
        ]

        content["shared_assumptions"] = shared_assumptions

        content["single_point_failures"] = [
            {"assumption": assumption, "frameworks": [framework_result.framework_name]}
            for assumption, count in assumption_counts.items()
            if count == 1
            for framework_result in framework_results
            if framework_result.success and assumption in framework_result.assumptions
        ]

        return self._create_artefact(analysis_id, "assumption_dependency", content)

    def generate_claim_dependency_artefact(
        self, analysis_id: str, framework_results: List[FrameworkResult]
    ) -> Optional[AnalysisArtefact]:
        """Generate claim dependency graph artefact"""
        content = {
            "claims_by_framework": {},
            "framework_claim_counts": {},
        }

        total_claims = 0
        for fw_result in framework_results:
            if fw_result.success:
                content["claims_by_framework"][fw_result.framework_name] = [
                    {
                        "statement": claim.statement,
                        "claim_id": claim.claim_id,
                        "confidence": claim.confidence.value,
                        "source": claim.source.value,
                        "affected_options": claim.affected_options,
                    }
                    for claim in fw_result.claims
                ]
                content["framework_claim_counts"][fw_result.framework_name] = len(
                    fw_result.claims
                )
                total_claims += len(fw_result.claims)

        content["total_claims"] = total_claims

        return self._create_artefact(analysis_id, "claim_dependency", content)

    def generate_analysis_sufficiency_artefact(
        self,
        analysis_id: str,
        decision: Decision,
        options: List[Option],
        framework_results: List[FrameworkResult],
    ) -> Optional[AnalysisArtefact]:
        """Generate analysis sufficiency statement artefact"""
        successful_frameworks = sum(1 for fw in framework_results if fw.success)
        total_frameworks = len(framework_results)

        total_claims = sum(len(fw.claims) for fw in framework_results)
        total_assumptions = sum(len(fw.assumptions) for fw in framework_results)
        total_unknowns = sum(len(fw.unknowns) for fw in framework_results)

        option_coverage = {}
        for opt in options:
            opt_claims = 0
            for fw in framework_results:
                if fw.success:
                    for claim in fw.claims:
                        if opt.name in claim.affected_options:
                            opt_claims += 1
            option_coverage[opt.name] = opt_claims

        content = {
            "decision_question": decision.decision_question,
            "decision_type": decision.decision_type.value,
            "options_count": len(options),
            "frameworks_executed": total_frameworks,
            "frameworks_successful": successful_frameworks,
            "framework_success_rate": (
                successful_frameworks / total_frameworks if total_frameworks > 0 else 0
            ),
            "total_claims": total_claims,
            "total_assumptions": total_assumptions,
            "total_unknowns": total_unknowns,
            "option_claim_coverage": option_coverage,
            "sufficiency_assessment": self._assess_sufficiency(
                successful_frameworks, total_frameworks, total_claims
            ),
        }

        return self._create_artefact(analysis_id, "analysis_sufficiency", content)

    def generate_sensitivity_triggers(
        self, framework_results: List[FrameworkResult]
    ) -> List[SensitivityTrigger]:
        """Generate sensitivity triggers from framework results"""
        triggers = []

        all_unknowns = []

        for fw_result in framework_results:
            if fw_result.success:
                all_unknowns.extend(fw_result.unknowns)

        from .models import SensitivityTrigger, SensitivityLevel

        for i, unknown in enumerate(all_unknowns):
            sensitivity_level = SensitivityLevel.MEDIUM
            if "critical" in unknown.lower():
                sensitivity_level = SensitivityLevel.CRITICAL
            elif "high" in unknown.lower():
                sensitivity_level = SensitivityLevel.HIGH
            elif "low" in unknown.lower():
                sensitivity_level = SensitivityLevel.LOW

            trigger = SensitivityTrigger(
                trigger_description=f"Unknown: {unknown}",
                affected_claims=[],
                affected_options=[],
                sensitivity_level=sensitivity_level,
                evidence_needed=f"Evidence to address: {unknown}",
                question_generated=f"What evidence would materially reduce uncertainty about: {unknown}?",
            )

            triggers.append(trigger)

        return triggers

    def _create_artefact(
        self, analysis_id: str, artefact_type: str, content: Dict[str, Any]
    ) -> AnalysisArtefact:
        """Create a versioned artefact with content hash"""
        artefact_id = generate_id()

        content_json = json.dumps(content, sort_keys=True)
        content_hash = hashlib.sha256(content_json.encode()).hexdigest()[:16]

        return AnalysisArtefact(
            artefact_id=artefact_id,
            analysis_id=analysis_id,
            artefact_type=artefact_type,
            version=V2_VERSION,
            content=content,
            content_hash=content_hash,
        )

    def render_artefact_to_markdown(self, artefact: AnalysisArtefact) -> str:
        """Render an artefact to Markdown format"""
        lines = [
            f"# {artefact.artefact_type.replace('_', ' ').title()}",
            "",
            f"**Artefact ID:** {artefact.artefact_id}",
            f"**Analysis ID:** {artefact.analysis_id}",
            f"**Version:** {artefact.version}",
            f"**Content Hash:** {artefact.content_hash}",
            "",
            "---",
            "",
        ]

        if artefact.artefact_type == "option_report":
            lines.extend(self._render_option_report(artefact.content))
        elif artefact.artefact_type == "tension_map":
            lines.extend(self._render_tension_map(artefact.content))
        elif artefact.artefact_type == "assumption_dependency":
            lines.extend(self._render_assumption_dependency(artefact.content))
        elif artefact.artefact_type == "analysis_sufficiency":
            lines.extend(self._render_analysis_sufficiency(artefact.content))

        return "\n".join(lines)

    def _render_option_report(self, content: Dict[str, Any]) -> List[str]:
        """Render option report to Markdown"""
        lines = []
        lines.append("## Decision Context")
        lines.append(f"**Question:** {content['decision_question']}")
        lines.append(f"**Type:** {content['decision_type']}")
        lines.append(f"**Options:** {', '.join(content['options_analyzed'])}")
        lines.append("")
        lines.append("## Option Summaries")
        lines.append("")

        for opt_name, summary in content["option_summaries"].items():
            lines.append(f"### {opt_name}")
            lines.append("")

            if summary["claims_affecting_option"]:
                lines.append("**Claims affecting this option:**")
                for claim in summary["claims_affecting_option"]:
                    lines.append(f"- {claim['statement']}")
                    lines.append(f"  - Framework: {claim['framework']}")
                    lines.append(f"  - Confidence: {claim['confidence']}")
                    lines.append(f"  - Source: {claim['source']}")
                lines.append("")

            if summary["assumptions_affecting_option"]:
                lines.append("**Assumptions affecting this option:**")
                for assumption in summary["assumptions_affecting_option"]:
                    lines.append(
                        f"- {assumption['statement']} ({assumption['framework']})"
                    )
                lines.append("")

            if summary["unknowns_affecting_option"]:
                lines.append("**Unknowns affecting this option:**")
                for unknown in summary["unknowns_affecting_option"]:
                    lines.append(f"- {unknown['statement']} ({unknown['framework']})")
                lines.append("")

        return lines

    def _render_tension_map(self, content: Dict[str, Any]) -> List[str]:
        """Render tension map to Markdown"""
        lines = []
        lines.append("## Framework Relationships")
        lines.append(content["summary"])
        lines.append("")

        if content["agreement_areas"]:
            lines.append("### Areas of Agreement")
            for area in content["agreement_areas"]:
                lines.append(f"- {area}")
            lines.append("")

        if content["tension_areas"]:
            lines.append("### Areas of Tension")
            for area in content["tension_areas"]:
                lines.append(f"- {area}")
            lines.append("")

        if content["contradiction_areas"]:
            lines.append("### Areas of Contradiction")
            for area in content["contradiction_areas"]:
                lines.append(f"- {area}")
            lines.append("")

        lines.append("## Framework Tension Details")
        lines.append("")

        for ft in content["framework_tensions"]:
            lines.append(f"### {ft['framework_1']} vs {ft['framework_2']}")
            lines.append(f"**Tension Type:** {ft['tension_type']}")
            lines.append(f"**Summary:** {ft['summary']}")
            lines.append("")

            if ft["resolution_areas"]:
                lines.append("**Resolution Required:**")
                for area in ft["resolution_areas"]:
                    lines.append(f"- {area}")
                lines.append("")

            if ft["claim_tensions"]:
                lines.append("**Claim-Level Tensions:**")
                for ct in ft["claim_tensions"]:
                    lines.append(f"- {ct['description']}")
                    lines.append(f"  - Type: {ct['tension_type']}")
                    lines.append(
                        f"  - Affected Options: {', '.join(ct['affected_options'])}"
                    )
                lines.append("")

        return lines

    def _render_assumption_dependency(self, content: Dict[str, Any]) -> List[str]:
        """Render assumption dependency to Markdown"""
        lines = []
        lines.append("## Assumptions by Framework")
        lines.append("")

        for fw_name, assumptions in content["assumptions_by_framework"].items():
            lines.append(f"### {fw_name}")
            for assumption in assumptions:
                lines.append(f"- {assumption}")
            lines.append("")

        if content["shared_assumptions"]:
            lines.append("## Shared Assumptions")
            lines.append("These assumptions are shared across multiple frameworks:")
            for assumption in content["shared_assumptions"]:
                lines.append(f"- {assumption}")
            lines.append("")

        if content["single_point_failures"]:
            lines.append("## Single-Point Failure Assumptions")
            lines.append("These assumptions are unique to single frameworks:")
            for spf in content["single_point_failures"]:
                lines.append(f"- {spf['assumption']} ({spf['frameworks'][0]})")
            lines.append("")

        return lines

    def _render_analysis_sufficiency(self, content: Dict[str, Any]) -> List[str]:
        """Render analysis sufficiency to Markdown"""
        lines = []
        lines.append("## Execution Summary")
        lines.append(f"**Frameworks Executed:** {content['frameworks_executed']}")
        lines.append(f"**Frameworks Successful:** {content['frameworks_successful']}")
        lines.append(
            f"**Success Rate:** {content['framework_success_rate'] * 100:.1f}%"
        )
        lines.append("")

        lines.append("## Output Summary")
        lines.append(f"**Total Claims:** {content['total_claims']}")
        lines.append(f"**Total Assumptions:** {content['total_assumptions']}")
        lines.append(f"**Total Unknowns:** {content['total_unknowns']}")
        lines.append("")

        lines.append("## Option Coverage")
        lines.append("")
        for opt_name, claim_count in content["option_claim_coverage"].items():
            lines.append(f"- **{opt_name}:** {claim_count} claims")
        lines.append("")

        lines.append("## Sufficiency Assessment")
        lines.append(content["sufficiency_assessment"])
        lines.append("")

        return lines

    def _assess_sufficiency(
        self, successful_frameworks: int, total_frameworks: int, total_claims: int
    ) -> str:
        """Assess overall sufficiency of analysis"""
        if successful_frameworks == 0:
            return "INSUFFICIENT: No frameworks executed successfully"

        if total_claims == 0:
            return "INSUFFICIENT: No analytical claims produced"

        success_rate = successful_frameworks / total_frameworks

        if success_rate < 0.5:
            return "INSUFFICIENT: Less than 50% of frameworks executed successfully"
        elif success_rate < 1.0:
            return "CONSTRAINED: Partial framework execution, some analysis incomplete"
        elif total_claims < 5:
            return "CONSTRAINED: Frameworks executed but produced limited claims"
        else:
            return "SUFFICIENT: All frameworks executed successfully with substantial claim output"


__all__ = ["V2ArtefactGenerator"]
