"""Strategem V2 - Systems Dynamics Framework Adapter

Adapter for Systems Dynamics V2 framework.
Translates Systems Dynamics output → canonical primitives.

Mapping:
- Feedback loops → Mechanisms
- System state transitions → Claims
- Growth/reinforcing assumptions → Assumptions
- Unknown parameters → Uncertainties
"""

from typing import List, Dict, Any, Optional
from ..substrate.primitives import (
    Claim,
    Assumption,
    Uncertainty,
    Mechanism,
)
from ..substrate.graph import ReasoningGraph


class SystemsDynamicsAdapter:
    """
    Adapter for Systems Dynamics V2 framework.

    Translates framework-native output into canonical primitives.
    Performs no interpretation - only structural translation.
    """

    def __init__(self, framework_name: str = "systems_dynamics_v2"):
        self.framework_name = framework_name

    def adapt(
        self,
        framework_result: Any,
        substrate: ReasoningGraph,
    ) -> int:
        """
        Adapt Systems Dynamics framework result into substrate.

        Args:
            framework_result: Systems Dynamics V2 framework result
            substrate: ReasoningGraph to add primitives to

        Returns:
            Number of primitives added
        """
        primitives_added = 0

        # Extract and adapt claims
        claims = self._adapt_claims(framework_result)
        for claim in claims:
            substrate.add_claim(claim)
            primitives_added += 1

        # Extract and adapt assumptions
        assumptions = self._adapt_assumptions(framework_result)
        for assumption in assumptions:
            substrate.add_assumption(assumption)
            primitives_added += 1

        # Extract and adapt uncertainties
        uncertainties = self._adapt_uncertainties(framework_result)
        for uncertainty in uncertainties:
            substrate.add_uncertainty(uncertainty)
            primitives_added += 1

        # Extract and adapt mechanisms
        mechanisms = self._adapt_mechanisms(framework_result)
        for mechanism in mechanisms:
            substrate.add_mechanism(mechanism)
            primitives_added += 1

        return primitives_added

    def _adapt_claims(self, framework_result: Any) -> List[Claim]:
        """Extract and adapt claims from framework result"""
        claims = []

        # Try to extract from global_claims first (for option-independent analysis)
        global_claims = None
        if hasattr(framework_result, "global_claims"):
            global_claims = framework_result.global_claims
        elif hasattr(framework_result, "result"):
            result_obj = framework_result.result
            if hasattr(result_obj, "global_claims"):
                global_claims = result_obj.global_claims

        if global_claims:
            for claim_obj in global_claims:
                claim = Claim(
                    statement=getattr(claim_obj, "Statement", ""),
                    framework=self.framework_name,
                    provenance=getattr(claim_obj, "Source", "inference"),
                    scope="global",
                    affected_dimensions=[],
                )
                claims.append(claim)

        # Then try option-aware claims
        option_aware_claims = None
        if hasattr(framework_result, "option_aware_claims"):
            option_aware_claims = framework_result.option_aware_claims
        elif hasattr(framework_result, "result"):
            result_obj = framework_result.result
            if hasattr(result_obj, "option_aware_claims"):
                option_aware_claims = result_obj.option_aware_claims

        if option_aware_claims:
            for claim_obj in option_aware_claims:
                claim = Claim(
                    statement=getattr(claim_obj, "Statement", ""),
                    framework=self.framework_name,
                    provenance=getattr(claim_obj, "Source", "inference"),
                    scope="option_aware",
                    affected_dimensions=list(getattr(claim_obj, "AffectedOptions", [])),
                )
                claims.append(claim)

        return claims

    def _adapt_assumptions(self, framework_result: Any) -> List[Assumption]:
        """Extract and adapt assumptions from framework result"""
        assumptions = []

        # Try to extract from assumptions list
        assumptions_list = None
        if hasattr(framework_result, "assumptions"):
            assumptions_list = framework_result.assumptions
        elif hasattr(framework_result, "shared_assumptions"):
            assumptions_list = framework_result.shared_assumptions
        elif hasattr(framework_result, "result"):
            result_obj = framework_result.result
            if hasattr(result_obj, "assumptions"):
                assumptions_list = result_obj.assumptions
            elif hasattr(result_obj, "shared_assumptions"):
                assumptions_list = result_obj.shared_assumptions

        if assumptions_list:
            for assumption_text in assumptions_list:
                assumption = Assumption(
                    statement=self._extract_text(assumption_text),
                    framework=self.framework_name,
                    provenance="framework",
                    scope="global",
                )
                assumptions.append(assumption)

        return assumptions

    def _adapt_uncertainties(self, framework_result: Any) -> List[Uncertainty]:
        """Extract and adapt uncertainties from framework result"""
        uncertainties = []

        # Try to extract from unknowns list
        unknowns_list = None
        if hasattr(framework_result, "unknowns"):
            unknowns_list = framework_result.unknowns
        elif hasattr(framework_result, "shared_unknowns"):
            unknowns_list = framework_result.shared_unknowns
        elif hasattr(framework_result, "result"):
            result_obj = framework_result.result
            if hasattr(result_obj, "unknowns"):
                unknowns_list = result_obj.unknowns
            elif hasattr(result_obj, "shared_unknowns"):
                unknowns_list = result_obj.shared_unknowns

        if unknowns_list:
            for unknown_item in unknowns_list:
                text = self._extract_text(unknown_item)

                # Extract evidence_needed if available
                evidence_needed = None
                if isinstance(unknown_item, dict):
                    evidence_needed = unknown_item.get(
                        "EvidenceNeeded"
                    ) or unknown_item.get("evidence_needed")
                elif hasattr(unknown_item, "EvidenceNeeded"):
                    evidence_needed = unknown_item.EvidenceNeeded
                elif hasattr(unknown_item, "evidence_needed"):
                    evidence_needed = unknown_item.evidence_needed

                uncertainty = Uncertainty(
                    statement=text,
                    framework=self.framework_name,
                    provenance="framework",
                    scope="global",
                    evidence_needed=evidence_needed,
                )
                uncertainties.append(uncertainty)

        return uncertainties

    def _adapt_mechanisms(self, framework_result: Any) -> List[Mechanism]:
        """Extract and adapt mechanisms from framework result"""
        mechanisms = []

        # Try to extract from feedback loops
        feedback_loops = None
        if hasattr(framework_result, "result"):
            result_obj = framework_result.result
            if hasattr(result_obj, "feedback_loops"):
                feedback_loops = result_obj.feedback_loops
            elif hasattr(result_obj, "FeedbackLoops"):
                feedback_loops = result_obj.FeedbackLoops

        if feedback_loops:
            # Handle both dict and list formats
            if isinstance(feedback_loops, dict):
                for loop_type, loops in feedback_loops.items():
                    for loop in loops:
                        description = self._extract_text(loop)
                        if description:
                            mechanisms.append(
                                Mechanism(
                                    description=description,
                                    framework=self.framework_name,
                                    provenance="framework",
                                    mechanism_type=f"feedback_loop_{loop_type}",
                                    scope="global",
                                )
                            )
            elif isinstance(feedback_loops, list):
                for loop in feedback_loops:
                    description = self._extract_text(loop)
                    if description:
                        mechanisms.append(
                            Mechanism(
                                description=description,
                                framework=self.framework_name,
                                provenance="framework",
                                mechanism_type="feedback_loop",
                                scope="global",
                            )
                        )

        return mechanisms

    def _extract_text(self, item: Any) -> str:
        """Extract text from various item types"""
        if isinstance(item, str):
            return item
        elif isinstance(item, dict):
            return (
                item.get("Description")
                or item.get("description")
                or item.get("Statement")
                or item.get("statement")
                or item.get("text", "")
            )
        elif hasattr(item, "Description"):
            return item.Description
        elif hasattr(item, "description"):
            return item.description
        elif hasattr(item, "Statement"):
            return item.Statement
        elif hasattr(item, "statement"):
            return item.statement
        elif hasattr(item, "text"):
            return item.text
        else:
            return str(item)


__all__ = [
    "SystemsDynamicsAdapter",
]
