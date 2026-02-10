"""Strategem V2 - Substrate Ingestion

Ingests framework outputs and normalizes them into canonical primitives.
Framework outputs are translated, not interpreted.

Performs no interpretation - only structural translation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .primitives import (
    Claim,
    Assumption,
    Uncertainty,
    Mechanism,
    StakeholderPower,
)
from .graph import ReasoningGraph


class IngestionResult(BaseModel):
    """Result of framework output ingestion"""

    success: bool
    framework: str
    primitives_ingested: int = 0
    errors: List[str] = Field(default_factory=list)


class SubstrateIngestor:
    """
    Ingests framework outputs into the reasoning substrate.

    Translates framework-native output → canonical primitives.
    Performs no interpretation - only structural translation.
    """

    def ingest_framework_result(
        self,
        framework_name: str,
        framework_result: Any,
        substrate: ReasoningGraph,
    ) -> IngestionResult:
        """
        Ingest a framework result into the substrate.

        Args:
            framework_name: Name of the framework
            framework_result: Framework-specific result object
            substrate: ReasoningGraph to ingest into

        Returns:
            IngestionResult with success status and count
        """
        result = IngestionResult(success=True, framework=framework_name)

        try:
            # Extract claims from framework result
            claims = self._extract_claims(framework_name, framework_result)
            for claim in claims:
                substrate.add_claim(claim)
                result.primitives_ingested += 1

            # Extract assumptions from framework result
            assumptions = self._extract_assumptions(framework_name, framework_result)
            for assumption in assumptions:
                substrate.add_assumption(assumption)
                result.primitives_ingested += 1

            # Extract uncertainties from framework result
            uncertainties = self._extract_uncertainties(
                framework_name, framework_result
            )
            for uncertainty in uncertainties:
                substrate.add_uncertainty(uncertainty)
                result.primitives_ingested += 1

            # Extract mechanisms from framework result
            mechanisms = self._extract_mechanisms(framework_name, framework_result)
            for mechanism in mechanisms:
                substrate.add_mechanism(mechanism)
                result.primitives_ingested += 1

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def _extract_claims(
        self, framework_name: str, framework_result: Any
    ) -> List[Claim]:
        """Extract claims from framework result"""
        claims = []

        # Try to extract from AnalyticalClaim objects
        if hasattr(framework_result, "claims"):
            for claim_obj in framework_result.claims:
                claim = Claim(
                    statement=getattr(claim_obj, "statement", ""),
                    framework=framework_name,
                    provenance=getattr(claim_obj, "source", "unknown"),
                    scope="global",
                    affected_dimensions=getattr(claim_obj, "affected_options", []),
                )
                claims.append(claim)

        # Try to extract from option_aware_claims
        elif hasattr(framework_result, "option_aware_claims"):
            for claim_obj in framework_result.option_aware_claims:
                claim = Claim(
                    statement=getattr(claim_obj, "Statement", ""),
                    framework=framework_name,
                    provenance=getattr(claim_obj, "Source", "inference"),
                    scope="global",
                    affected_dimensions=getattr(claim_obj, "AffectedOptions", []),
                )
                claims.append(claim)

        # Try to extract from result object (Systems Dynamics V2)
        elif hasattr(framework_result, "result"):
            inner_result = framework_result.result
            if hasattr(inner_result, "option_aware_claims"):
                for claim_obj in inner_result.option_aware_claims:
                    claim = Claim(
                        statement=getattr(claim_obj, "Statement", ""),
                        framework=framework_name,
                        provenance=getattr(claim_obj, "Source", "inference"),
                        scope="global",
                        affected_dimensions=getattr(claim_obj, "AffectedOptions", []),
                    )
                    claims.append(claim)

        return claims

    def _extract_assumptions(
        self, framework_name: str, framework_result: Any
    ) -> List[Assumption]:
        """Extract assumptions from framework result"""
        assumptions = []

        # Try to extract from assumptions list
        if hasattr(framework_result, "assumptions"):
            for assumption_text in framework_result.assumptions:
                assumption = Assumption(
                    statement=self._extract_text(assumption_text),
                    framework=framework_name,
                    provenance="framework",
                    scope="global",
                )
                assumptions.append(assumption)

        # Try to extract from shared_assumptions
        elif hasattr(framework_result, "shared_assumptions"):
            for assumption_text in framework_result.shared_assumptions:
                assumption = Assumption(
                    statement=self._extract_text(assumption_text),
                    framework=framework_name,
                    provenance="framework",
                    scope="global",
                )
                assumptions.append(assumption)

        # Try to extract from result object (Systems Dynamics V2)
        elif hasattr(framework_result, "result"):
            inner_result = framework_result.result
            if hasattr(inner_result, "assumptions"):
                for assumption_text in inner_result.assumptions:
                    assumption = Assumption(
                        statement=self._extract_text(assumption_text),
                        framework=framework_name,
                        provenance="framework",
                        scope="global",
                    )
                    assumptions.append(assumption)

        return assumptions

    def _extract_uncertainties(
        self, framework_name: str, framework_result: Any
    ) -> List[Uncertainty]:
        """Extract uncertainties from framework result"""
        uncertainties = []

        # Try to extract from unknowns list
        if hasattr(framework_result, "unknowns"):
            for unknown_text in framework_result.unknowns:
                uncertainty = Uncertainty(
                    statement=self._extract_text(unknown_text),
                    framework=framework_name,
                    provenance="framework",
                    scope="global",
                )
                uncertainties.append(uncertainty)

        # Try to extract from shared_unknowns
        elif hasattr(framework_result, "shared_unknowns"):
            for unknown_text in framework_result.shared_unknowns:
                uncertainty = Uncertainty(
                    statement=self._extract_text(unknown_text),
                    framework=framework_name,
                    provenance="framework",
                    scope="global",
                )
                uncertainties.append(uncertainty)

        # Try to extract from result object (Systems Dynamics V2)
        elif hasattr(framework_result, "result"):
            inner_result = framework_result.result
            if hasattr(inner_result, "unknowns"):
                for unknown_item in inner_result.unknowns:
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
                        framework=framework_name,
                        provenance="framework",
                        scope="global",
                        evidence_needed=evidence_needed,
                    )
                    uncertainties.append(uncertainty)

        return uncertainties

    def _extract_mechanisms(
        self, framework_name: str, framework_result: Any
    ) -> List[Mechanism]:
        """Extract mechanisms from framework result"""
        mechanisms = []

        # Try to extract from result object (Systems Dynamics V2)
        if hasattr(framework_result, "result"):
            inner_result = framework_result.result

            # Extract feedback loops as mechanisms
            if hasattr(inner_result, "feedback_loops"):
                feedback_loops = inner_result.feedback_loops

                # Handle both dict and list formats
                if isinstance(feedback_loops, dict):
                    for loop_type, loops in feedback_loops.items():
                        for loop in loops:
                            if isinstance(loop, dict):
                                description = loop.get("Description") or loop.get(
                                    "description", ""
                                )
                                mechanisms.append(
                                    Mechanism(
                                        description=description,
                                        framework=framework_name,
                                        provenance="framework",
                                        mechanism_type=f"feedback_loop_{loop_type}",
                                        scope="global",
                                    )
                                )
                            elif isinstance(loop, str):
                                mechanisms.append(
                                    Mechanism(
                                        description=loop,
                                        framework=framework_name,
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
                item.get("Statement") or item.get("statement") or item.get("text", "")
            )
        elif hasattr(item, "Statement"):
            return item.Statement
        elif hasattr(item, "statement"):
            return item.statement
        elif hasattr(item, "text"):
            return item.text
        else:
            return str(item)


__all__ = [
    "IngestionResult",
    "SubstrateIngestor",
]
