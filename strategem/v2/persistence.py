"""Strategem V2 - Persistence Layer (V2 Specific)"""

import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from strategem.core import config, ensure_directory
from .models import AnalysisResult, AnalysisArtefact


class V2PersistenceLayer:
    """
    Persistence layer for V2 analyses.

    V2: Stores analysis results and artefacts.
    JSON-native format with metadata.
    """

    def __init__(self):
        self.storage_dir = config.STORAGE_DIR / "v2"
        self.artefacts_dir = self.storage_dir / "artefacts"
        self.analyses_dir = self.storage_dir / "analyses"

        ensure_directory(self.storage_dir)
        ensure_directory(self.artefacts_dir)
        ensure_directory(self.analyses_dir)

    def save_analysis(self, result: AnalysisResult) -> str:
        """Save V2 analysis result to JSON"""
        file_path = self.analyses_dir / f"analysis_{result.analysis_id}.json"

        data = result.model_dump(mode="json", exclude_none=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

        return str(file_path)

    def load_analysis(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Load V2 analysis result from JSON"""
        file_path = self.analyses_dir / f"analysis_{analysis_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return AnalysisResult(**data)

    def list_analyses(self) -> List[str]:
        """List all V2 analysis IDs"""
        if not self.analyses_dir.exists():
            return []

        analysis_files = list(self.analyses_dir.glob("analysis_*.json"))
        analysis_ids = []

        for file_path in analysis_files:
            analysis_id = file_path.stem.replace("analysis_", "")
            analysis_ids.append(analysis_id)

        return analysis_ids

    def save_artefact(self, artefact: AnalysisArtefact) -> str:
        """Save V2 artefact to JSON"""
        file_path = (
            self.artefacts_dir / f"{artefact.artefact_type}_{artefact.artefact_id}.json"
        )

        data = artefact.model_dump(mode="json", exclude_none=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

        return str(file_path)

    def load_artefact(self, artefact_id: str) -> Optional[AnalysisArtefact]:
        """Load V2 artefact from JSON"""
        for file_path in self.artefacts_dir.glob(f"*_{artefact_id}.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return AnalysisArtefact(**data)

        return None

    def list_artefacts(self, artefact_type: Optional[str] = None) -> List[str]:
        """List all V2 artefact IDs, optionally filtered by type"""
        if not self.artefacts_dir.exists():
            return []

        artefact_files = list(self.artefacts_dir.glob("*.json"))
        artefact_ids = []

        for file_path in artefact_files:
            if artefact_type:
                if file_path.name.startswith(f"{artefact_type}_"):
                    artefact_id = file_path.stem.split("_")[-1]
                    artefact_ids.append(artefact_id)
            else:
                artefact_id = file_path.stem.split("_")[-1]
                artefact_ids.append(artefact_id)

        return artefact_ids

    def load_all_artefacts(
        self, artefact_type: Optional[str] = None
    ) -> List[AnalysisArtefact]:
        """Load all V2 artefacts as objects, optionally filtered by type"""
        if not self.artefacts_dir.exists():
            return []

        artefact_files = list(self.artefacts_dir.glob("*.json"))
        artefacts = []

        for file_path in artefact_files:
            if artefact_type and not file_path.name.startswith(f"{artefact_type}_"):
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                artefacts.append(AnalysisArtefact(**data))

        return artefacts


__all__ = ["V2PersistenceLayer", "load_all_artefacts"]
