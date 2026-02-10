"""Strategem V2 - Artefact Exports (JSON)

Generates structured JSON artefacts from reasoning substrate
and judgment nodes. Replaces "report thinking" with inspectable
JSON artefacts.

Artefacts are:
- Stable schema
- Deterministic ordering
- Human-readable labels
- Never ranked or scored
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from strategem.core import generate_id, config
from ..substrate import (
    ReasoningGraph,
    Claim,
    Assumption,
    Uncertainty,
    Mechanism,
    StakeholderPower,
)
from ..judgment import (
    JudgmentNode,
)


class ReasoningPrimitivesArtefact(BaseModel):
    """Core artefact: reasoning_primitives.json"""

    artefact_id: str = Field(default_factory=generate_id)
    artefact_type: str = "reasoning_primitives"
    version: str = "2.0.0-dev"

    # All primitives organized by type
    claims: List[Dict[str, Any]] = Field(default_factory=list)
    assumptions: List[Dict[str, Any]] = Field(default_factory=list)
    uncertainties: List[Dict[str, Any]] = Field(default_factory=list)
    mechanisms: List[Dict[str, Any]] = Field(default_factory=list)
    stakeholder_powers: List[Dict[str, Any]] = Field(default_factory=list)

    # Framework summary
    frameworks: List[str] = Field(default_factory=list)
    total_primitives: int = Field(default=0)

    # Metadata
    generated_at: str = Field(default="")

    def to_json(self, sort_keys: bool = True) -> str:
        """Convert to JSON with deterministic ordering"""
        return json.dumps(
            self.model_dump(mode="json"),
            indent=2,
            sort_keys=sort_keys,
        )


class JudgmentSurfaceArtefact(BaseModel):
    """Core artefact: judgment_surface.json"""

    artefact_id: str = Field(default_factory=generate_id)
    artefact_type: str = "judgment_surface"
    version: str = "2.0.0-dev"

    # All judgment nodes
    judgment_nodes: List[Dict[str, Any]] = Field(default_factory=list)

    # Summary
    total_judgment_nodes: int = Field(default=0)
    trigger_types_found: List[str] = Field(default_factory=list)

    # Metadata
    generated_at: str = Field(default="")

    def to_json(self, sort_keys: bool = True) -> str:
        """Convert to JSON with deterministic ordering"""
        return json.dumps(
            self.model_dump(mode="json"),
            indent=2,
            sort_keys=sort_keys,
        )


class OptionAnnotationsArtefact(BaseModel):
    """Optional artefact: option_annotations.json (only if options exist)"""

    artefact_id: str = Field(default_factory=generate_id)
    artefact_type: str = "option_annotations"
    version: str = "2.0.0-dev"

    # Option names
    options: List[str] = Field(default_factory=list)

    # Annotations (never ranked or scored)
    annotations: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)

    # Metadata
    total_primitives_affected: int = Field(default=0)
    generated_at: str = Field(default="")

    def to_json(self, sort_keys: bool = True) -> str:
        """Convert to JSON with deterministic ordering"""
        return json.dumps(
            self.model_dump(mode="json"),
            indent=2,
            sort_keys=sort_keys,
        )


class ArtefactExporter:
    """
    Generates and saves JSON artefacts from substrate and judgment nodes.

    Artefacts:
    - reasoning_primitives.json (required)
    - judgment_surface.json (required)
    - option_annotations.json (optional, only if options exist)
    """

    def __init__(self):
        pass

    def generate_reasoning_primitives(
        self, substrate: ReasoningGraph
    ) -> ReasoningPrimitivesArtefact:
        """
        Generate reasoning_primitives.json artefact.

        Args:
            substrate: ReasoningGraph to export

        Returns:
            ReasoningPrimitivesArtefact
        """
        artefact = ReasoningPrimitivesArtefact()

        # Export claims
        for claim in sorted(
            substrate.claims.values(),
            key=lambda c: c.primitive_id,
        ):
            artefact.claims.append(
                {
                    "primitive_id": claim.primitive_id,
                    "type": "claim",
                    "statement": claim.statement,
                    "framework": claim.framework,
                    "provenance": claim.provenance,
                    "scope": claim.scope,
                    "affected_dimensions": claim.affected_dimensions,
                }
            )

        # Export assumptions
        for assumption in sorted(
            substrate.assumptions.values(),
            key=lambda a: a.primitive_id,
        ):
            artefact.assumptions.append(
                {
                    "primitive_id": assumption.primitive_id,
                    "type": "assumption",
                    "statement": assumption.statement,
                    "framework": assumption.framework,
                    "provenance": assumption.provenance,
                    "scope": assumption.scope,
                    "affected_dimensions": assumption.affected_dimensions,
                }
            )

        # Export uncertainties
        for uncertainty in sorted(
            substrate.uncertainties.values(),
            key=lambda u: u.primitive_id,
        ):
            artefact.uncertainties.append(
                {
                    "primitive_id": uncertainty.primitive_id,
                    "type": "uncertainty",
                    "statement": uncertainty.statement,
                    "framework": uncertainty.framework,
                    "provenance": uncertainty.provenance,
                    "scope": uncertainty.scope,
                    "affected_dimensions": uncertainty.affected_dimensions,
                    "evidence_needed": uncertainty.evidence_needed,
                }
            )

        # Export mechanisms
        for mechanism in sorted(
            substrate.mechanisms.values(),
            key=lambda m: m.primitive_id,
        ):
            artefact.mechanisms.append(
                {
                    "primitive_id": mechanism.primitive_id,
                    "type": "mechanism",
                    "description": mechanism.description,
                    "framework": mechanism.framework,
                    "provenance": mechanism.provenance,
                    "mechanism_type": mechanism.mechanism_type,
                    "scope": mechanism.scope,
                    "affected_dimensions": mechanism.affected_dimensions,
                }
            )

        # Export stakeholder powers
        for sp in sorted(
            substrate.stakeholder_powers.values(),
            key=lambda s: s.primitive_id,
        ):
            artefact.stakeholder_powers.append(
                {
                    "primitive_id": sp.primitive_id,
                    "type": "stakeholder_power",
                    "stakeholder": sp.stakeholder,
                    "framework": sp.framework,
                    "provenance": sp.provenance,
                    "power_type": sp.power_type,
                    "scope": sp.scope,
                    "affected_dimensions": sp.affected_dimensions,
                }
            )

        # Summary
        artefact.frameworks = sorted(substrate.frameworks)
        artefact.total_primitives = len(substrate.get_all_primitives())

        return artefact

    def generate_judgment_surface(
        self, judgment_nodes: List[JudgmentNode]
    ) -> JudgmentSurfaceArtefact:
        """
        Generate judgment_surface.json artefact.

        Args:
            judgment_nodes: List of JudgmentNode to export

        Returns:
            JudgmentSurfaceArtefact
        """
        artefact = JudgmentSurfaceArtefact()

        # Export judgment nodes (sorted by node_id for determinism)
        for node in sorted(judgment_nodes, key=lambda n: n.node_id):
            # Export stances (sorted by stance_id for determinism)
            stances = []
            for stance in sorted(node.plausible_stances, key=lambda s: s.stance_id):
                stances.append(
                    {
                        "stance_id": stance.stance_id,
                        "name": stance.name,
                        "description": stance.description,
                        "downstream_implications": stance.downstream_implications,
                        "supporting_primitives": stance.supporting_primitives,
                        "opposing_primitives": stance.opposing_primitives,
                    }
                )

            artefact.judgment_nodes.append(
                {
                    "node_id": node.node_id,
                    "trigger_type": node.judgment_trigger_type.value,
                    "why_judgment_required": node.why_judgment_required,
                    "what_cannot_resolve": node.what_cannot_resolve,
                    "plausible_stances": stances,
                    "triggering_primitives": node.triggering_primitives,
                    "affected_frameworks": node.affected_frameworks,
                    "scope": node.scope,
                }
            )

        # Summary
        artefact.total_judgment_nodes = len(judgment_nodes)
        artefact.trigger_types_found = sorted(
            set([n.judgment_trigger_type.value for n in judgment_nodes])
        )

        return artefact

    def generate_option_annotations(
        self,
        substrate: ReasoningGraph,
        options: List[str],
    ) -> Optional[OptionAnnotationsArtefact]:
        """
        Generate option_annotations.json artefact (optional).

        Only generates if options exist.

        Args:
            substrate: ReasoningGraph to export
            options: List of option names

        Returns:
            OptionAnnotationsArtefact or None if no options
        """
        if not options:
            return None

        artefact = OptionAnnotationsArtefact()
        artefact.options = sorted(options)

        # Annotate each option with affecting primitives
        for option in sorted(options):
            annotations = []

            # Find claims affecting this option
            for claim in substrate.claims.values():
                if option in claim.affected_dimensions:
                    annotations.append(
                        {
                            "primitive_id": claim.primitive_id,
                            "type": "claim",
                            "statement": claim.statement,
                            "framework": claim.framework,
                        }
                    )

            # Find assumptions affecting this option
            for assumption in substrate.assumptions.values():
                if option in assumption.affected_dimensions:
                    annotations.append(
                        {
                            "primitive_id": assumption.primitive_id,
                            "type": "assumption",
                            "statement": assumption.statement,
                            "framework": assumption.framework,
                        }
                    )

            # Find uncertainties affecting this option
            for uncertainty in substrate.uncertainties.values():
                if option in uncertainty.affected_dimensions:
                    annotations.append(
                        {
                            "primitive_id": uncertainty.primitive_id,
                            "type": "uncertainty",
                            "statement": uncertainty.statement,
                            "framework": uncertainty.framework,
                        }
                    )

            # Find mechanisms affecting this option
            for mechanism in substrate.mechanisms.values():
                if option in mechanism.affected_dimensions:
                    annotations.append(
                        {
                            "primitive_id": mechanism.primitive_id,
                            "type": "mechanism",
                            "description": mechanism.description,
                            "framework": mechanism.framework,
                        }
                    )

            artefact.annotations[option] = annotations
            artefact.total_primitives_affected += len(annotations)

        return artefact

    def save_all_artefacts(
        self,
        analysis_id: str,
        substrate: ReasoningGraph,
        judgment_nodes: List[JudgmentNode],
        options: Optional[List[str]] = None,
        output_dir: Optional[Path] = None,
    ) -> Dict[str, Path]:
        """
        Generate and save all artefacts.

        Args:
            analysis_id: Analysis ID
            substrate: ReasoningGraph
            judgment_nodes: List of JudgmentNode
            options: Optional list of options
            output_dir: Optional output directory (defaults to config.STORAGE_DIR)

        Returns:
            Dict mapping artefact name to file path
        """
        if output_dir is None:
            output_dir = config.STORAGE_DIR

        output_dir.mkdir(exist_ok=True)
        saved_files = {}

        # Generate and save reasoning_primitives.json
        primitives_artefact = self.generate_reasoning_primitives(substrate)
        primitives_path = output_dir / f"{analysis_id}_reasoning_primitives.json"
        primitives_path.write_text(primitives_artefact.to_json())
        saved_files["reasoning_primitives"] = primitives_path

        # Generate and save judgment_surface.json
        judgment_artefact = self.generate_judgment_surface(judgment_nodes)
        judgment_path = output_dir / f"{analysis_id}_judgment_surface.json"
        judgment_path.write_text(judgment_artefact.to_json())
        saved_files["judgment_surface"] = judgment_path

        # Generate and save option_annotations.json (only if options exist)
        if options:
            option_artefact = self.generate_option_annotations(substrate, options)
            if option_artefact:
                option_path = output_dir / f"{analysis_id}_option_annotations.json"
                option_path.write_text(option_artefact.to_json())
                saved_files["option_annotations"] = option_path

        return saved_files


__all__ = [
    "ReasoningPrimitivesArtefact",
    "JudgmentSurfaceArtefact",
    "OptionAnnotationsArtefact",
    "ArtefactExporter",
]
