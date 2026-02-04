"""Strategem V1 - Framework Model"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AnalysisFramework(BaseModel):
    """
    Formal Framework interface - frameworks must be swappable without touching orchestration logic.

    This enables:
    - Adding new frameworks without code changes
    - Swapping frameworks for different analytical lenses
    - Pivoting between problem types
    """

    name: str = Field(
        ...,
        description="Framework identifier (e.g., 'porter_five_forces', 'systems_dynamics')",
    )
    analytical_lens: str = Field(
        ...,
        description="What this framework reveals (e.g., 'structural attractiveness', 'systemic fragility')",
    )
    input_requirements: List[str] = Field(
        default_factory=list, description="What input this framework requires"
    )
    prompt_template: str = Field(..., description="Path to the prompt template file")
    output_schema: Dict[str, Any] = Field(
        default_factory=dict, description="JSON schema for expected output"
    )
    description: Optional[str] = Field(None, description="Human-readable description")
    requires_decision_focus: bool = Field(
        default=False,
        description="If True, this framework requires DecisionFocus to execute. Without it, the framework must refuse execution or return low-confidence artifacts.",
    )


__all__ = [
    "AnalysisFramework",
]
