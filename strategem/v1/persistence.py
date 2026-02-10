"""Strategem Core - Persistence Layer (V1 Compliant)"""

import json
from pathlib import Path
from typing import Optional, List
from .models import AnalysisResult, ProblemContext, ProvidedMaterial, FrameworkResult
from strategem.core import config


class PersistenceLayer:
    """Handles persistence of analysis results"""

    def __init__(self, storage_dir: Path = None):
        self.storage_dir = Path(storage_dir) if storage_dir else config.STORAGE_DIR
        self.storage_dir.mkdir(exist_ok=True)

    def save_analysis(self, result: AnalysisResult) -> str:
        """Save analysis result to storage"""
        file_path = self.storage_dir / f"analysis_{result.id}.json"

        # Convert to dict for JSON serialization
        data = {
            "id": result.id,
            "problem_context": self._problem_context_to_dict(result.problem_context),
            "systems_analysis": self._systems_to_dict(result.systems_analysis)
            if result.systems_analysis
            else None,
            "systems_error": result.systems_error,
            "framework_results": self._framework_results_to_dict(
                result.framework_results
            ),
            "created_at": result.created_at.isoformat(),
            "generated_report": result.generated_report,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return str(file_path)

    def _problem_context_to_dict(self, context: ProblemContext) -> dict:
        """Convert ProblemContext to dict with V1 fields"""
        result = {
            # V1 formal schema fields
            "title": context.title,
            "problem_statement": context.problem_statement,
            "objectives": context.objectives,
            "constraints": context.constraints,
            "provided_materials": [
                {
                    "material_type": m.material_type,
                    "content": m.content,
                    "source": m.source,
                }
                for m in context.provided_materials
            ],
            "declared_assumptions": context.declared_assumptions,
            # Decision Focus (V1 Decision-Bound)
            "decision_focus": {
                "decision_question": context.decision_focus.decision_question,
                "decision_type": context.decision_focus.decision_type.value,
                "options": context.decision_focus.options,
            }
            if context.decision_focus
            else None,
            # Legacy fields (maintained for backward compatibility)
            "raw_content": context.raw_content,
            "structured_content": context.structured_content,
            "source_type": context.source_type,
        }
        return result

    def _framework_results_to_dict(self, results: List[FrameworkResult]) -> list:
        """Convert FrameworkResult list to dict"""
        return [
            {
                "framework_name": r.framework_name,
                "success": r.success,
                "error_message": r.error_message,
            }
            for r in results
        ]

    def _systems_to_dict(self, systems) -> dict:
        """Convert Systems analysis to dict"""
        return {
            "SystemOverview": systems.system_overview,
            "KeyComponents": systems.key_components,
            "FeedbackLoops": {
                "Reinforcing": systems.reinforcing_loops,
                "Balancing": systems.balancing_loops,
            },
            "Bottlenecks": systems.bottlenecks,
            "Fragilities": systems.fragilities,
            "Assumptions": systems.assumptions,
            "Unknowns": systems.unknowns,
        }

    def load_analysis(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Load analysis result from storage"""
        file_path = self.storage_dir / f"analysis_{analysis_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Reconstruct AnalysisResult
        from .models import (
            ProblemContext,
            SystemsDynamicsAnalysis,
        )
        from datetime import datetime

        # Load ProblemContext with V1 fields (backward compatible)
        pc_data = data["problem_context"]

        # Load decision_focus if present
        decision_focus = None
        if pc_data.get("decision_focus"):
            df_data = pc_data["decision_focus"]
            from .models import DecisionFocus, DecisionType

            decision_focus = DecisionFocus(
                decision_question=df_data["decision_question"],
                decision_type=DecisionType(df_data["decision_type"]),
                options=df_data["options"],
            )

        problem_context = ProblemContext(
            # V1 fields (with defaults for backward compatibility)
            title=pc_data.get("title", "Untitled Analysis"),
            problem_statement=pc_data.get(
                "problem_statement", "Problem context provided for analysis"
            ),
            objectives=pc_data.get("objectives", []),
            constraints=pc_data.get("constraints", []),
            provided_materials=[
                ProvidedMaterial(
                    material_type=m["material_type"],
                    content=m["content"],
                    source=m.get("source"),
                )
                for m in pc_data.get("provided_materials", [])
            ]
            if pc_data.get("provided_materials")
            else [],
            declared_assumptions=pc_data.get("declared_assumptions", []),
            # Decision Focus (V1 Decision-Bound)
            decision_focus=decision_focus,
            # Legacy fields
            raw_content=pc_data.get("raw_content"),
            structured_content=pc_data.get("structured_content"),
            source_type=pc_data.get("source_type", "unknown"),
        )

        systems_analysis = None
        if data.get("systems_analysis"):
            sa = data["systems_analysis"]
            fl = sa.get("FeedbackLoops", {})
            systems_analysis = SystemsDynamicsAnalysis(
                SystemOverview=sa["SystemOverview"],
                KeyComponents=sa.get("KeyComponents", []),
                FeedbackLoops_Reinforcing=fl.get("Reinforcing", []),
                FeedbackLoops_Balancing=fl.get("Balancing", []),
                Bottlenecks=sa.get("Bottlenecks", []),
                Fragilities=sa.get("Fragilities", []),
                Assumptions=sa.get("Assumptions", []),
                Unknowns=sa.get("Unknowns", []),
            )

        # Load framework results (backward compatible)
        framework_results = []
        for fr_data in data.get("framework_results", []):
            framework_results.append(
                FrameworkResult(
                    framework_name=fr_data["framework_name"],
                    success=fr_data["success"],
                    error_message=fr_data.get("error_message"),
                )
            )

        return AnalysisResult(
            id=data["id"],
            problem_context=problem_context,
            systems_analysis=systems_analysis,
            systems_error=data.get("systems_error"),
            framework_results=framework_results,
            created_at=datetime.fromisoformat(data["created_at"]),
            generated_report=data.get("generated_report"),
        )

    def list_analyses(self) -> list:
        """List all stored analysis IDs"""
        analyses = []
        for file_path in self.storage_dir.glob("analysis_*.json"):
            analysis_id = file_path.stem.replace("analysis_", "")
            analyses.append(analysis_id)
        return analyses
