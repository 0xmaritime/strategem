"""Strategem V2 - Judgment Derivation

Derives judgment nodes from the reasoning substrate.

Judgment nodes are generated when the substrate detects conflicts,
trade-offs, or irreducible ambiguities.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .nodes import (
    JudgmentNode,
    Stance,
    JudgmentTriggerType,
)
from ..substrate.graph import ReasoningGraph
from ..substrate.primitives import Claim, Assumption, Uncertainty, Mechanism


class DerivationResult(BaseModel):
    """Result of judgment derivation"""

    judgment_nodes: List[JudgmentNode] = Field(
        default_factory=list, description="Derived judgment nodes"
    )
    primitives_analyzed: int = Field(
        default=0, description="Number of primitives analyzed"
    )
    triggers_found: List[str] = Field(
        default_factory=list, description="Types of triggers found"
    )


class JudgmentDeriver:
    """
    Derives judgment nodes from the reasoning substrate.

    Judgment nodes are generated when:
    - Conflicting claims exist
    - Competing mechanisms exist
    - Value-laden assumptions exist
    - High-sensitivity uncertainties exist
    - Stakeholder power trade-offs exist
    - Framework disagreement exists
    - Option emergence exists
    """

    def __init__(self):
        self.derivation_rules = [
            self._derive_from_conflicting_claims,
            self._derive_from_competing_mechanisms,
            self._derive_from_high_sensitivity_uncertainties,
        ]

    def derive_judgment_nodes(self, substrate: ReasoningGraph) -> DerivationResult:
        """
        Derive all judgment nodes from the substrate.

        Args:
            substrate: ReasoningGraph to analyze

        Returns:
            DerivationResult with judgment nodes and metadata
        """
        result = DerivationResult()

        for rule in self.derivation_rules:
            nodes = rule(substrate)
            result.judgment_nodes.extend(nodes)
            if nodes:
                result.triggers_found.extend(
                    [node.judgment_trigger_type.value for node in nodes]
                )

        result.primitives_analyzed = len(substrate.get_all_primitives())

        # Validate no preferences
        for node in result.judgment_nodes:
            if not node.validate_no_preference():
                result.judgment_nodes.remove(node)

        return result

    def _derive_from_conflicting_claims(
        self, substrate: ReasoningGraph
    ) -> List[JudgmentNode]:
        """
        Derive judgment nodes from conflicting claims.

        Trigger: Claims with contradictory assertions.
        """
        nodes = []
        all_claims = list(substrate.claims.values())

        for i, claim1 in enumerate(all_claims):
            for claim2 in all_claims[i + 1 :]:
                if claim1.framework == claim2.framework:
                    continue

                if self._claims_conflict(claim1, claim2):
                    # Create judgment node
                    stance1 = Stance(
                        name=f"Support {claim1.framework}",
                        description=f"Trust the claim from {claim1.framework}: {claim1.statement[:100]}...",
                        supporting_primitives=[claim1.primitive_id],
                        opposing_primitives=[claim2.primitive_id],
                    )

                    stance2 = Stance(
                        name=f"Support {claim2.framework}",
                        description=f"Trust the claim from {claim2.framework}: {claim2.statement[:100]}...",
                        supporting_primitives=[claim2.primitive_id],
                        opposing_primitives=[claim1.primitive_id],
                    )

                    node = JudgmentNode(
                        judgment_trigger_type=JudgmentTriggerType.CONFLICTING_CLAIMS,
                        why_judgment_required=f"Frameworks {claim1.framework} and {claim2.framework} make contradictory claims about the same issue.",
                        what_cannot_resolve="Analytical methods cannot determine which framework's claim is more accurate without additional evidence.",
                        plausible_stances=[stance1, stance2],
                        triggering_primitives=[
                            claim1.primitive_id,
                            claim2.primitive_id,
                        ],
                        affected_frameworks=[claim1.framework, claim2.framework],
                    )

                    nodes.append(node)

        return nodes

    def _derive_from_competing_mechanisms(
        self, substrate: ReasoningGraph
    ) -> List[JudgmentNode]:
        """
        Derive judgment nodes from competing mechanisms.

        Trigger: Mechanisms with opposing effects.
        """
        nodes = []
        all_mechanisms = list(substrate.mechanisms.values())

        # Simple heuristic: reinforcing vs balancing loops
        reinforcing = [
            m for m in all_mechanisms if "reinforcing" in m.mechanism_type.lower()
        ]
        balancing = [
            m for m in all_mechanisms if "balancing" in m.mechanism_type.lower()
        ]

        if reinforcing and balancing:
            # Create judgment node
            stance1 = Stance(
                name="Emphasize Growth",
                description=f"Prioritize reinforcing mechanisms that drive growth and expansion.",
                supporting_primitives=[m.primitive_id for m in reinforcing],
                opposing_primitives=[m.primitive_id for m in balancing],
            )

            stance2 = Stance(
                name="Emphasize Stability",
                description=f"Prioritize balancing mechanisms that maintain stability and control.",
                supporting_primitives=[m.primitive_id for m in balancing],
                opposing_primitives=[m.primitive_id for m in reinforcing],
            )

            node = JudgmentNode(
                judgment_trigger_type=JudgmentTriggerType.COMPETING_MECHANISMS,
                why_judgment_required="The system has both growth-driving (reinforcing) and stability-maintaining (balancing) mechanisms.",
                what_cannot_resolve="Analytical methods cannot determine whether growth or stability should be prioritized without value judgments about risk tolerance and objectives.",
                plausible_stances=[stance1, stance2],
                triggering_primitives=[m.primitive_id for m in reinforcing + balancing],
                affected_frameworks=list(
                    set([m.framework for m in reinforcing + balancing])
                ),
            )

            nodes.append(node)

        return nodes

    def _derive_from_high_sensitivity_uncertainties(
        self, substrate: ReasoningGraph
    ) -> List[JudgmentNode]:
        """
        Derive judgment nodes from high-sensitivity uncertainties.

        Trigger: Uncertainties that would materially change outcomes.
        """
        nodes = []
        all_uncertainties = list(substrate.uncertainties.values())

        # Filter for high-sensitivity uncertainties
        high_sensitivity = [
            u
            for u in all_uncertainties
            if "critical" in u.statement.lower()
            or "high" in u.statement.lower()
            or "significant" in u.statement.lower()
        ]

        if high_sensitivity:
            # Create judgment node for each high-sensitivity uncertainty
            for uncertainty in high_sensitivity:
                stance1 = Stance(
                    name="Proceed Despite Uncertainty",
                    description="Accept the uncertainty and proceed with the decision despite the unknown.",
                    supporting_primitives=[],
                    opposing_primitives=[uncertainty.primitive_id],
                )

                stance2 = Stance(
                    name="Gather More Information",
                    description="Delay decision until the uncertainty can be reduced through additional investigation.",
                    supporting_primitives=[uncertainty.primitive_id],
                    opposing_primitives=[],
                )

                node = JudgmentNode(
                    judgment_trigger_type=JudgmentTriggerType.HIGH_SENSITIVITY_UNCERTAINTIES,
                    why_judgment_required=f"A high-sensitivity uncertainty exists: {uncertainty.statement[:80]}...",
                    what_cannot_resolve="Analytical methods cannot reduce this uncertainty without additional evidence gathering.",
                    plausible_stances=[stance1, stance2],
                    triggering_primitives=[uncertainty.primitive_id],
                    affected_frameworks=[uncertainty.framework],
                )

                nodes.append(node)

        return nodes

    def _claims_conflict(self, claim1: Claim, claim2: Claim) -> bool:
        """Simple heuristic for claim conflict detection"""
        text1 = claim1.statement.lower()
        text2 = claim2.statement.lower()

        contradictory_pairs = [
            ("is", "is not"),
            ("will", "will not"),
            ("can", "cannot"),
            ("should", "should not"),
            ("high", "low"),
            ("increase", "decrease"),
            ("success", "failure"),
            ("likely", "unlikely"),
            ("constrained", "unconstrained"),
            ("limited", "unlimited"),
        ]

        for word1, word2 in contradictory_pairs:
            if word1 in text1 and word2 in text2:
                return True

        return False


__all__ = [
    "DerivationResult",
    "JudgmentDeriver",
]
