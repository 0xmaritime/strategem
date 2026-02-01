"""Strategem Core - Context Ingestion Module (V1 Compliant)"""

from pathlib import Path
from typing import Union, Optional, List
from .models import ProblemContext, ProvidedMaterial


class ContextIngestionError(Exception):
    """Error during context ingestion"""

    pass


class ContextIngestionModule:
    """
    Module for ingesting and parsing Problem Context Materials.

    Supports both legacy raw content ingestion and new formal ProblemContext schema.
    """

    def ingest_text(
        self,
        text: str,
        title: Optional[str] = None,
        problem_statement: Optional[str] = None,
        objectives: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        declared_assumptions: Optional[List[str]] = None,
    ) -> ProblemContext:
        """
        Ingest raw text content as Problem Context Material.

        Args:
            text: The raw text content (Problem Context Material)
            title: Optional title/identifier for this problem context
            problem_statement: Clear statement of the problem being analyzed
            objectives: What the decision owner is trying to achieve
            constraints: Known limitations or boundaries
            declared_assumptions: Assumptions explicitly declared by the decision owner
        """
        material = ProvidedMaterial(
            material_type="text", content=text, source="direct_input"
        )

        return ProblemContext(
            title=title or "Untitled Analysis",
            problem_statement=problem_statement
            or "Problem context provided for analysis",
            objectives=objectives or [],
            constraints=constraints or [],
            provided_materials=[material],
            declared_assumptions=declared_assumptions or [],
            # Legacy fields for backward compatibility
            raw_content=text,
            source_type="text",
        )

    def ingest_file(
        self,
        file_path: Union[str, Path],
        title: Optional[str] = None,
        problem_statement: Optional[str] = None,
        objectives: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        declared_assumptions: Optional[List[str]] = None,
    ) -> ProblemContext:
        """
        Ingest content from a file as Problem Context Material.

        Args:
            file_path: Path to the file containing Problem Context Material
            title: Optional title/identifier for this problem context
            problem_statement: Clear statement of the problem being analyzed
            objectives: What the decision owner is trying to achieve
            constraints: Known limitations or boundaries
            declared_assumptions: Assumptions explicitly declared by the decision owner
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise ContextIngestionError(f"File not found: {file_path}")

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try reading as binary and decode
            try:
                content = file_path.read_bytes().decode("utf-8", errors="ignore")
            except Exception as e:
                raise ContextIngestionError(f"Failed to read file: {e}")

        material = ProvidedMaterial(
            material_type="document", content=content, source=str(file_path)
        )

        return ProblemContext(
            title=title or file_path.stem,
            problem_statement=problem_statement
            or "Problem context provided for analysis",
            objectives=objectives or [],
            constraints=constraints or [],
            provided_materials=[material],
            declared_assumptions=declared_assumptions or [],
            # Legacy fields for backward compatibility
            raw_content=content,
            source_type="document",
        )

    def structure_content(self, context: ProblemContext) -> ProblemContext:
        """
        Structure the Problem Context Materials for analysis.

        Combines all provided materials into structured content for framework processing.
        """
        # Combine all provided materials into structured content
        structured_parts = []

        # Add problem statement
        structured_parts.append(f"PROBLEM STATEMENT: {context.problem_statement}")

        # Add objectives if present
        if context.objectives:
            structured_parts.append(f"OBJECTIVES: {', '.join(context.objectives)}")

        # Add constraints if present
        if context.constraints:
            structured_parts.append(f"CONSTRAINTS: {', '.join(context.constraints)}")

        # Add declared assumptions if present
        if context.declared_assumptions:
            structured_parts.append(
                f"DECLARED ASSUMPTIONS: {', '.join(context.declared_assumptions)}"
            )

        # Add all provided materials
        for i, material in enumerate(context.provided_materials, 1):
            structured_parts.append(
                f"\nPROVIDED MATERIAL [{i}] ({material.material_type}):"
            )
            structured_parts.append(material.content)

        context.structured_content = "\n\n".join(structured_parts)

        # If no materials were explicitly provided but raw_content exists (legacy), use that
        if not context.provided_materials and context.raw_content:
            context.structured_content = context.raw_content

        return context

    def create_problem_context(
        self,
        title: str,
        problem_statement: str,
        materials: List[Union[str, Path]],
        objectives: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        declared_assumptions: Optional[List[str]] = None,
    ) -> ProblemContext:
        """
        Create a formal ProblemContext from multiple materials.

        This is the preferred V1 method for creating problem contexts.

        Args:
            title: Title or identifier for this problem context
            problem_statement: Clear statement of the problem being analyzed
            materials: List of text strings or file paths (Problem Context Materials)
            objectives: What the decision owner is trying to achieve
            constraints: Known limitations or boundaries
            declared_assumptions: Assumptions explicitly declared by the decision owner
        """
        provided_materials = []
        raw_contents = []

        for material in materials:
            if isinstance(material, str) and not Path(material).exists():
                # Treat as text content
                provided_materials.append(
                    ProvidedMaterial(
                        material_type="text", content=material, source="input"
                    )
                )
                raw_contents.append(material)
            else:
                # Treat as file path
                file_path = Path(material)
                try:
                    content = file_path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    content = file_path.read_bytes().decode("utf-8", errors="ignore")

                provided_materials.append(
                    ProvidedMaterial(
                        material_type="document", content=content, source=str(file_path)
                    )
                )
                raw_contents.append(content)

        return ProblemContext(
            title=title,
            problem_statement=problem_statement,
            objectives=objectives or [],
            constraints=constraints or [],
            provided_materials=provided_materials,
            declared_assumptions=declared_assumptions or [],
            # Legacy fields
            raw_content="\n\n".join(raw_contents),
            source_type="composite",
        )
