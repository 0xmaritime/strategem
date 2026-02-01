"""Strategem Core - Persistence Layer (V1 Compliant)"""

import json
from pathlib import Path
from typing import Optional, List
from .models import AnalysisResult, ProblemContext, ProvidedMaterial, FrameworkResult
from .config import config


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
            "porter_analysis": self._porter_to_dict(result.porter_analysis)
            if result.porter_analysis
            else None,
            "systems_analysis": self._systems_to_dict(result.systems_analysis)
            if result.systems_analysis
            else None,
            "porter_error": result.porter_error,
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
        return {
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
            # Legacy fields (maintained for backward compatibility)
            "raw_content": context.raw_content,
            "structured_content": context.structured_content,
            "source_type": context.source_type,
        }

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

    def _porter_to_dict(self, porter) -> dict:
        """Convert Porter analysis to dict"""
        return {
            "ThreatOfNewEntrants": {
                "level": porter.threat_of_new_entrants.level,
                "rationale": porter.threat_of_new_entrants.rationale,
                "assumptions": porter.threat_of_new_entrants.assumptions,
                "unknowns": porter.threat_of_new_entrants.unknowns,
            },
            "SupplierPower": {
                "level": porter.supplier_power.level,
                "rationale": porter.supplier_power.rationale,
                "assumptions": porter.supplier_power.assumptions,
                "unknowns": porter.supplier_power.unknowns,
            },
            "BuyerPower": {
                "level": porter.buyer_power.level,
                "rationale": porter.buyer_power.rationale,
                "assumptions": porter.buyer_power.assumptions,
                "unknowns": porter.buyer_power.unknowns,
            },
            "Substitutes": {
                "level": porter.substitutes.level,
                "rationale": porter.substitutes.rationale,
                "assumptions": porter.substitutes.assumptions,
                "unknowns": porter.substitutes.unknowns,
            },
            "Rivalry": {
                "level": porter.rivalry.level,
                "rationale": porter.rivalry.rationale,
                "assumptions": porter.rivalry.assumptions,
                "unknowns": porter.rivalry.unknowns,
            },
            "OverallObservations": porter.overall_observations,
            "KeyRisks": porter.key_risks,
            "KeyStrengths": porter.key_strengths,
        }

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
            PorterAnalysis,
            SystemsDynamicsAnalysis,
            ForceAnalysis,
        )
        from datetime import datetime

        # Load ProblemContext with V1 fields (backward compatible)
        pc_data = data["problem_context"]
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
            # Legacy fields
            raw_content=pc_data.get("raw_content"),
            structured_content=pc_data.get("structured_content"),
            source_type=pc_data.get("source_type", "unknown"),
        )

        porter_analysis = None
        if data.get("porter_analysis"):
            pa = data["porter_analysis"]
            porter_analysis = PorterAnalysis(
                ThreatOfNewEntrants=ForceAnalysis(**pa["ThreatOfNewEntrants"]),
                SupplierPower=ForceAnalysis(**pa["SupplierPower"]),
                BuyerPower=ForceAnalysis(**pa["BuyerPower"]),
                Substitutes=ForceAnalysis(**pa["Substitutes"]),
                Rivalry=ForceAnalysis(**pa["Rivalry"]),
                OverallObservations=pa["OverallObservations"],
                KeyRisks=pa.get("KeyRisks", []),
                KeyStrengths=pa.get("KeyStrengths", []),
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
            porter_analysis=porter_analysis,
            systems_analysis=systems_analysis,
            porter_error=data.get("porter_error"),
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
