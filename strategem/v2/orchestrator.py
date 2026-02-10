"""Strategem V2 - Analysis Orchestrator (Reasoning Substrate)"""

import uuid
from typing import List, Optional, Type, Dict, Any
from datetime import datetime

from .models import (
    Decision,
    Option,
    AnalyticalClaim,
    FrameworkResult,
    AnalysisResult,
    FrameworkContract,
    FrameworkExecutionStatus,
    SystemsDynamicsAnalysisV2,
    OptionEffect,
    Assumption,
    Unknown,
)
from .llm_layer import V2LLMInferenceLayer, LLMError
from strategem.core import config, generate_id

# New V2 components
from .substrate import ReasoningGraph
from .framework_adapters import SystemsDynamicsAdapter
from .judgment import JudgmentDeriver, DerivationResult
from .artefacts import ArtefactExporter


class V2AnalysisOrchestrator:
    """
    Orchestrates V2 analysis workflow (Reasoning Substrate).

    V2 (Reasoning Substrate) Architecture:
    - Decision context is optional (implicit decisions supported)
    - Options are optional annotations, not drivers
    - Claims may be global or option-aware
    - Framework disagreement is valid and expected
    - Frameworks are primitive emitters only
    - Reasoning Substrate normalizes all outputs
    - Judgment is derived, not emitted
    """

    def __init__(self):
        self.llm = V2LLMInferenceLayer()
        self._frameworks: Dict[str, FrameworkContract] = {}
        self._framework_models: Dict[str, Type] = {}

        # New V2 components
        self.adapters: Dict[str, Any] = {}
        self.judgment_deriver = JudgmentDeriver()
        self.artefact_exporter = ArtefactExporter()

        self._register_default_frameworks()
        self._register_default_adapters()

    def _register_default_frameworks(self):
        """Register default V2 frameworks"""
        from .frameworks.systems_dynamics_v2 import SYSTEMS_DYNAMICS_V2_FRAMEWORK

        self.register_framework(
            SYSTEMS_DYNAMICS_V2_FRAMEWORK, SystemsDynamicsAnalysisV2
        )

    def _register_default_adapters(self):
        """Register default framework adapters"""
        self.adapters["systems_dynamics_v2"] = SystemsDynamicsAdapter()

    def register_framework(self, framework: FrameworkContract, response_model: Type):
        """
        Register a V2 analytical framework.

        V2: Framework must adhere to FrameworkContract.
        Must be option-aware and decision-bound.
        """
        self._frameworks[framework.name] = framework
        self._framework_models[framework.name] = response_model

    def run_full_analysis(
        self,
        decision: Optional[Decision] = None,
        options: Optional[List[Option]] = None,
        context: str = "",
        frameworks: Optional[List[str]] = None,
    ) -> AnalysisResult:
        """
        Run complete V2 analysis.

        V2 (Reasoning Substrate): Decision and options are optional.
        Analysis can run with minimal problem context only.
        All frameworks are framework-centric (primitive emitters).

        Framework failures are tolerated - analysis continues with partial results.

        Args:
            decision: Decision context (optional in V2)
            options: List of options being analyzed (optional in V2)
            context: Problem context material
            frameworks: List of framework names to run (default: all registered)

        Returns:
            Complete V2 analysis result
        """

    def run_framework(
        self,
        framework_name: str,
        decision: Optional[Decision],
        options: Optional[List[Option]],
        context: str,
    ) -> FrameworkResult:
        """
        Run a single V2 framework.

        V2 (Reasoning Substrate): Decision and options are optional.
        Framework runs with context only if no decision/options provided.

        Framework failure does NOT abort entire analysis.
        Partial framework outputs are accepted.
        """
        import sys

        if framework_name not in self._frameworks:
            print(
                f"[V2 Orchestrator] Unknown framework: {framework_name}",
                file=sys.stderr,
            )
            return FrameworkResult(
                framework_name=framework_name,
                success=False,
                execution_status=FrameworkExecutionStatus.FAILED,
                execution_reason=f"Unknown framework: {framework_name}",
                claims=[],
                assumptions=[],
                unknowns=[],
            )

        framework = self._frameworks[framework_name]
        response_model = framework.response_model

        option_names = [opt.name for opt in options] if options else []

        print(f"[V2 Orchestrator] Running framework: {framework_name}", file=sys.stderr)

        try:
            decision_question = decision.decision_question if decision else ""
            decision_type = decision.decision_type.value if decision else "explore"

            result = self.llm.run_analysis(
                prompt_name=framework.prompt_template.replace(".txt", ""),
                context=context,
                decision_question=decision_question,
                decision_type=decision_type,
                options=option_names,
                response_model=response_model,
                max_retries=config.MAX_RETRIES,
            )

            print(
                f"[V2 Orchestrator] Framework {framework_name} completed successfully",
                file=sys.stderr,
            )

            # Extract claims and other data with validation error handling
            claims = []
            assumptions = []
            unknowns = []

            try:
                if hasattr(result, "global_claims"):
                    claims = result.global_claims or []
                elif hasattr(result, "option_aware_claims"):
                    claims = result.option_aware_claims or []
                elif hasattr(result, "option_aware_aims"):
                    claims = result.option_aware_aims or []
            except Exception as e:
                print(
                    f"[V2 Orchestrator] Error extracting claims: {e}", file=sys.stderr
                )
                pass

            try:
                if hasattr(result, "shared_assumptions"):
                    assumptions.extend(result.shared_assumptions or [])
            except Exception as e:
                pass

            try:
                if hasattr(result, "shared_unknowns"):
                    unknowns.extend(result.shared_unknowns or [])
            except Exception as e:
                pass

            # V2: Extract assumptions and unknowns from systems dynamics
            try:
                if hasattr(result, "assumptions") and result.assumptions:
                    assumptions.extend(result.assumptions)
                if hasattr(result, "unknowns") and result.unknowns:
                    # Handle both list and dict formats
                    if isinstance(result.unknowns, list):
                        for unk in result.unknowns:
                            if isinstance(unk, dict):
                                # Check both PascalCase and snake_case
                                stmt = unk.get("Statement") or unk.get("statement")
                                if stmt:
                                    unknowns.append(stmt)
                            elif isinstance(unk, str):
                                unknowns.append(unk)
                    elif isinstance(result.unknowns, dict):
                        unknowns.append(str(result.unknowns))
            except Exception as e:
                print(
                    f"[V2 Orchestrator] Error extracting from systems dynamics: {e}",
                    file=sys.stderr,
                )
                pass

            # Check if framework produced meaningful output
            # A framework is meaningful if it has claims, assumptions, unknowns, OR system data
            has_meaningful_output = (
                bool(claims)
                or bool(assumptions)
                or bool(unknowns)
                or (hasattr(result, "system_overview") and result.system_overview)
            )

            if not has_meaningful_output:
                print(
                    f"[V2 Orchestrator] Framework {framework_name} produced no output",
                    file=sys.stderr,
                )
                return FrameworkResult(
                    framework_name=framework_name,
                    success=True,
                    execution_status=FrameworkExecutionStatus.INSUFFICIENT,
                    execution_reason="Framework completed but produced no meaningful output",
                    result=result,
                    claims=[],
                    assumptions=[],
                    unknowns=[],
                )

            return FrameworkResult(
                framework_name=framework_name,
                success=True,
                execution_status=FrameworkExecutionStatus.SUCCESSFUL,
                result=result,
                claims=claims,
                assumptions=assumptions,
                unknowns=unknowns,
            )

        except Exception as e:
            print(
                f"[V2 Orchestrator] Framework {framework_name} failed: {e}",
                file=sys.stderr,
            )
            print(f"[V2 Orchestrator] Error type: {type(e).__name__}", file=sys.stderr)

            # Framework failure is NOT fatal to the analysis
            # Mark as failed but don't abort entire analysis
            return FrameworkResult(
                framework_name=framework_name,
                success=False,
                execution_status=FrameworkExecutionStatus.FAILED,
                execution_reason=str(e),
                claims=[],
                assumptions=[],
                unknowns=[],
            )

    def run_full_analysis(
        self,
        decision: Optional[Decision] = None,
        options: Optional[List[Option]] = None,
        context: str = "",
        frameworks: Optional[List[str]] = None,
    ) -> AnalysisResult:
        """
        Run complete V2 analysis (Reasoning Substrate flow).

        V2 (Reasoning Substrate) Architecture:
        - Decision context is optional (implicit decisions supported)
        - Options are optional annotations, not drivers
        - Claims may be global or option-aware
        - Framework disagreement is valid and expected
        - Frameworks are primitive emitters only
        - Reasoning Substrate normalizes all outputs
        - Judgment is derived, not emitted

        Framework failures are tolerated - analysis continues with partial results.

        Args:
            decision: Decision context (optional in V2)
            options: List of options being analyzed (optional in V2)
            context: Problem context material
            frameworks: List of framework names to run (default: all registered)

        Returns:
            Complete V2 analysis result with substrate and judgment nodes
        """
        import sys

        analysis_id = generate_id()

        # Create reasoning substrate (NEW)
        substrate = ReasoningGraph()

        if frameworks is None:
            frameworks = list(self._frameworks.keys())

        option_names = [opt.name for opt in options] if options else []

        print(
            f"[V2 Orchestrator] Starting full analysis with frameworks: {frameworks}",
            file=sys.stderr,
        )

        # Run frameworks and ingest into substrate via adapters (NEW)
        framework_results = []
        for framework_name in frameworks:
            result = self.run_framework(framework_name, decision, options, context)
            framework_results.append(result)

            # Ingest into substrate via adapter (NEW)
            if framework_name in self.adapters:
                adapter = self.adapters[framework_name]
                if (
                    result.success
                    or result.execution_status == FrameworkExecutionStatus.INSUFFICIENT
                ):
                    try:
                        primitives_added = adapter.adapt(result, substrate)
                        print(
                            f"[V2 Orchestrator] Ingested {primitives_added} primitives from {framework_name} into substrate",
                            file=sys.stderr,
                        )
                    except Exception as e:
                        print(
                            f"[V2 Orchestrator] Adapter failed for {framework_name}: {e}",
                            file=sys.stderr,
                        )

        # Count successful vs failed frameworks
        successful = sum(1 for fw in framework_results if fw.success)
        failed = sum(1 for fw in framework_results if not fw.success)
        insufficient = sum(
            1
            for fw in framework_results
            if fw.execution_status == FrameworkExecutionStatus.INSUFFICIENT
        )

        print(
            f"[V2 Orchestrator] Framework results: {successful} successful, "
            f"{failed} failed, {insufficient} insufficient",
            file=sys.stderr,
        )

        print(
            f"[V2 Orchestrator] Substrate summary: {substrate.get_summary()}",
            file=sys.stderr,
        )

        # Derive judgment nodes from substrate (NEW)
        judgment_derivation_result = self.judgment_deriver.derive_judgment_nodes(
            substrate
        )

        print(
            f"[V2 Orchestrator] Judgment derivation: {len(judgment_derivation_result.judgment_nodes)} nodes, triggers: {judgment_derivation_result.triggers_found}",
            file=sys.stderr,
        )

        # Generate and save artefacts (NEW)
        try:
            saved_files = self.artefact_exporter.save_all_artefacts(
                analysis_id=analysis_id,
                substrate=substrate,
                judgment_nodes=judgment_derivation_result.judgment_nodes,
                options=option_names,
            )
            print(
                f"[V2 Orchestrator] Artefacts saved: {list(saved_files.keys())}",
                file=sys.stderr,
            )
        except Exception as e:
            print(
                f"[V2 Orchestrator] Artefact export failed: {e}",
                file=sys.stderr,
            )

        # Legacy compatibility: Keep old tension mapper and artefact generator
        # These will be deprecated in favor of substrate + judgment nodes
        from .tension_mapper import V2TensionMapper
        from .artefact_generator import V2ArtefactGenerator

        tension_mapper = V2TensionMapper()
        artefact_generator = V2ArtefactGenerator()

        tension_map = None
        # Only map tensions if we have at least 2 successful frameworks
        successful_frameworks = [
            fw
            for fw in framework_results
            if fw.execution_status == FrameworkExecutionStatus.SUCCESSFUL
        ]

        if len(successful_frameworks) >= 2:
            try:
                tension_map = tension_mapper.map_framework_tensions(framework_results)
                print(f"[V2 Orchestrator] Tension mapping completed", file=sys.stderr)
            except Exception as e:
                print(f"[V2 Orchestrator] Tension mapping failed: {e}", file=sys.stderr)
                # Continue without tension map - this is not fatal
        else:
            print(
                f"[V2 Orchestrator] Skipping tension mapping "
                f"(need at least 2 successful frameworks, got {len(successful_frameworks)})",
                file=sys.stderr,
            )

        try:
            artefacts = artefact_generator.generate_all_artefacts(
                analysis_id, decision, options, framework_results, tension_map
            )
        except Exception as e:
            print(f"[V2 Orchestrator] Artefact generation failed: {e}", file=sys.stderr)
            artefacts = []

        try:
            sensitivity_triggers = artefact_generator.generate_sensitivity_triggers(
                framework_results
            )
        except Exception as e:
            print(
                f"[V2 Orchestrator] Sensitivity trigger generation failed: {e}",
                file=sys.stderr,
            )
            sensitivity_triggers = []

        # Return analysis result with substrate and judgment nodes (NEW)
        return AnalysisResult(
            analysis_id=analysis_id,
            decision=decision,
            options_analyzed=option_names,
            framework_results=framework_results,
            tension_map=tension_map,
            sensitivity_triggers=sensitivity_triggers,
            created_at=datetime.now(),
            # New fields (these will be added to AnalysisResult model in future)
            # substrate=substrate,
            # judgment_nodes=judgment_derivation_result.judgment_nodes,
        )

    def list_available_frameworks(self) -> List[FrameworkContract]:
        """List all registered V2 frameworks"""
        return list(self._frameworks.values())


__all__ = ["V2AnalysisOrchestrator"]
