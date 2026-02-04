"""Strategem V2 - Tension Mapper (V2 Specific)"""

from typing import List

from .models import (
    FrameworkResult,
    TensionMapResult,
    FrameworkTension,
    ClaimTension,
    AnalyticalClaim,
    TensionType,
)


class V2TensionMapper:
    """
    Maps tensions between framework outputs (V2).

    V2: Explicit tension mapping is required.
    NO aggregation, NO reconciliation.
    The system surfaces tension; human resolves it.
    """

    def map_framework_tensions(
        self, framework_results: List[FrameworkResult]
    ) -> TensionMapResult:
        """
        Map tensions between frameworks.

        V2: Compare claims across frameworks.
        Identify: agreement, tension, contradiction.
        DO NOT aggregate or reconcile.

        Args:
            framework_results: Results from multiple frameworks

        Returns:
            TensionMapResult with explicit tensions
        """
        framework_tensions = []
        agreement_areas = []
        tension_areas = []
        contradiction_areas = []

        if len(framework_results) < 2:
            return TensionMapResult(
                framework_tensions=[],
                agreement_areas=[],
                tension_areas=[],
                contradiction_areas=[],
                summary="Insufficient frameworks for tension mapping (need at least 2)",
            )

        all_claims_by_framework = {}
        for fw_result in framework_results:
            if fw_result.success:
                all_claims_by_framework[fw_result.framework_name] = fw_result.claims

        framework_names = list(all_claims_by_framework.keys())

        for i in range(len(framework_names)):
            for j in range(i + 1, len(framework_names)):
                fw1_name = framework_names[i]
                fw2_name = framework_names[j]

                claims1 = all_claims_by_framework[fw1_name]
                claims2 = all_claims_by_framework[fw2_name]

                framework_tension = self._compare_frameworks(
                    fw1_name, fw2_name, claims1, claims2
                )

                framework_tensions.append(framework_tension)

                if framework_tension.tension_type == TensionType.AGREEMENT:
                    agreement_areas.append(f"{fw1_name} and {fw2_name}")
                elif framework_tension.tension_type == TensionType.TENSION:
                    tension_areas.append(f"{fw1_name} and {fw2_name}")
                elif framework_tension.tension_type == TensionType.CONTRADICTION:
                    contradiction_areas.append(f"{fw1_name} and {fw2_name}")

        summary = self._generate_summary(framework_tensions)

        return TensionMapResult(
            framework_tensions=framework_tensions,
            agreement_areas=agreement_areas,
            tension_areas=tension_areas,
            contradiction_areas=contradiction_areas,
            summary=summary,
        )

    def _compare_frameworks(
        self,
        fw1_name: str,
        fw2_name: str,
        claims1: List[AnalyticalClaim],
        claims2: List[AnalyticalClaim],
    ) -> FrameworkTension:
        """
        Compare two frameworks and identify tensions.

        V2: NO aggregation. Just identify tensions.
        """
        claim_tensions = []
        agreements = 0
        tensions = 0
        contradictions = 0
        divergents = 0

        for claim1 in claims1:
            for claim2 in claims2:
                tension = self._compare_claims(claim1, claim2)
                if tension:
                    claim_tensions.append(tension)

                    if tension.tension_type == TensionType.AGREEMENT:
                        agreements += 1
                    elif tension.tension_type == TensionType.TENSION:
                        tensions += 1
                    elif tension.tension_type == TensionType.CONTRADICTION:
                        contradictions += 1
                    elif tension.tension_type == TensionType.DIVERGENT:
                        divergents += 1

        overall_tension_type = self._determine_overall_tension_type(
            agreements, tensions, contradictions, divergents
        )

        summary = self._generate_framework_summary(
            fw1_name, fw2_name, overall_tension_type, claim_tensions
        )

        resolution_areas = []
        if contradictions > 0:
            resolution_areas.append(
                f"Resolve contradictions between {fw1_name} and {fw2_name}"
            )
        if tensions > 0:
            resolution_areas.append(
                f"Aclarify tensions between {fw1_name} and {fw2_name}"
            )

        return FrameworkTension(
            framework_1=fw1_name,
            framework_2=fw2_name,
            tension_type=overall_tension_type,
            claim_tensions=claim_tensions,
            summary=summary,
            resolution_areas=resolution_areas,
        )

    def _compare_claims(
        self, claim1: AnalyticalClaim, claim2: AnalyticalClaim
    ) -> ClaimTension:
        """
        Compare two claims and identify tension.

        V2: Simple semantic comparison.
        """
        claim1_lower = claim1.statement.lower()
        claim2_lower = claim2.statement.lower()

        affected_options_intersection = set(claim1.affected_options) & set(
            claim2.affected_options
        )

        if not affected_options_intersection:
            return None

        tension_type = TensionType.DIVERGENT
        description = f"Frameworks address different aspects"

        if self._are_contradictory(claim1_lower, claim2_lower):
            tension_type = TensionType.CONTRADICTION
            description = (
                f"Claims appear to be in direct contradiction: "
                f"'{claim1.statement}' vs '{claim2.statement}'"
            )
        elif self._are_complementary(claim1_lower, claim2_lower):
            tension_type = TensionType.AGREEMENT
            description = (
                f"Claims appear to agree or be complementary: "
                f"'{claim1.statement}' and '{claim2.statement}'"
            )
        elif self._have_tension(claim1_lower, claim2_lower):
            tension_type = TensionType.TENSION
            description = (
                f"Claims indicate tension or different emphasis: "
                f"'{claim1.statement}' vs '{claim2.statement}'"
            )

        return ClaimTension(
            claim_1_id=claim1.claim_id or "unknown",
            claim_1_framework=claim1.framework,
            claim_2_id=claim2.claim_id or "unknown",
            claim_2_framework=claim2.framework,
            tension_type=tension_type,
            description=description,
            affected_options=list(affected_options_intersection),
            resolution_note=None,
        )

    def _are_contradictory(self, claim1_lower: str, claim2_lower: str) -> bool:
        """Check if claims are contradictory"""
        contradiction_patterns = [
            ("low", "high"),
            ("positive", "negative"),
            ("unlikely", "likely"),
            ("not", ""),
            ("cannot", "can"),
            ("impossible", "possible"),
        ]

        for pattern1, pattern2 in contradiction_patterns:
            if pattern1 in claim1_lower and pattern2 in claim2_lower:
                return True
            if pattern2 in claim1_lower and pattern1 in claim2_lower:
                return True

        return False

    def _are_complementary(self, claim1_lower: str, claim2_lower: str) -> bool:
        """Check if claims are complementary or agree"""
        similar_words = [
            "similar",
            "comparable",
            "consistent",
            "aligned",
            "same",
            "both",
        ]

        for word in similar_words:
            if word in claim1_lower and word in claim2_lower:
                return True

        return False

    def _have_tension(self, claim1_lower: str, claim2_lower: str) -> bool:
        """Check if claims have tension (not contradiction, not agreement)"""
        tension_words = [
            "however",
            "but",
            "although",
            "despite",
            "conversely",
            "whereas",
        ]

        for word in tension_words:
            if word in claim1_lower or word in claim2_lower:
                return True

        return False

    def _determine_overall_tension_type(
        self, agreements: int, tensions: int, contradictions: int, divergents: int
    ) -> TensionType:
        """Determine overall tension type between frameworks"""
        if contradictions > 0:
            return TensionType.CONTRADICTION

        if tensions > agreements:
            return TensionType.TENSION

        if agreements > tensions:
            return TensionType.AGREEMENT

        return TensionType.DIVERGENT

    def _generate_framework_summary(
        self,
        fw1_name: str,
        fw2_name: str,
        tension_type: TensionType,
        claim_tensions: List[ClaimTension],
    ) -> str:
        """Generate human-readable summary of framework tension"""
        if tension_type == TensionType.AGREEMENT:
            return f"{fw1_name} and {fw2_name} largely agree on key points"
        elif tension_type == TensionType.TENSION:
            return (
                f"{fw1_name} and {fw2_name} show areas of tension but not contradiction"
            )
        elif tension_type == TensionType.CONTRADICTION:
            return f"{fw1_name} and {fw2_name} are in contradiction on key points"
        else:
            return f"{fw1_name} and {fw2_name} address different aspects of the problem"

    def _generate_summary(self, framework_tensions: List[FrameworkTension]) -> str:
        """Generate overall summary of framework relationships"""
        if not framework_tensions:
            return "No frameworks to compare"

        agreements = sum(
            1 for ft in framework_tensions if ft.tension_type == TensionType.AGREEMENT
        )
        tensions = sum(
            1 for ft in framework_tensions if ft.tension_type == TensionType.TENSION
        )
        contradictions = sum(
            1
            for ft in framework_tensions
            if ft.tension_type == TensionType.CONTRADICTION
        )

        parts = []
        if agreements > 0:
            parts.append(f"{agreements} framework pair(s) in agreement")
        if tensions > 0:
            parts.append(f"{tensions} framework pair(s) in tension")
        if contradictions > 0:
            parts.append(f"{contradictions} framework pair(s) in contradiction")

        return "; ".join(parts) if parts else "Framework tensions identified"


__all__ = ["V2TensionMapper"]
