"""Strategem Core - Context Ingestion Module"""

from pathlib import Path
from typing import Union
from .models import ProblemContext


class ContextIngestionError(Exception):
    """Error during context ingestion"""

    pass


class ContextIngestionModule:
    """Module for ingesting and parsing problem context materials"""

    def ingest_text(self, text: str) -> ProblemContext:
        """Ingest raw text content"""
        return ProblemContext(raw_content=text, source_type="text")

    def ingest_file(self, file_path: Union[str, Path]) -> ProblemContext:
        """Ingest content from a file"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise ContextIngestionError(f"File not found: {file_path}")

        try:
            content = file_path.read_text(encoding="utf-8")
            return ProblemContext(raw_content=content, source_type="document")
        except UnicodeDecodeError:
            # Try reading as binary and decode
            try:
                content = file_path.read_bytes().decode("utf-8", errors="ignore")
                return ProblemContext(raw_content=content, source_type="document")
            except Exception as e:
                raise ContextIngestionError(f"Failed to read file: {e}")

    def structure_content(self, context: ProblemContext) -> ProblemContext:
        """Structure the raw content for analysis"""
        # For V1, we'll keep the content as-is but could add
        # section extraction, key point identification, etc.
        context.structured_content = context.raw_content
        return context
