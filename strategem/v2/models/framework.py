"""Strategem V2 - Framework Contract"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class FrameworkContract(BaseModel):
    """
    Formal contract for V2 frameworks.

    V2: All frameworks must adhere to this contract.
    Frameworks MUST be option-aware and tension-capable.
    """

    name: str = Field(
        ...,
        description="Framework identifier (e.g., 'porter_five_forces_v2', 'systems_dynamics_v2')",
    )
    analytical_lens: str = Field(
        ...,
        description="What this framework reveals (e.g., 'structural_attractiveness', 'systemic_fragility')",
    )
    description: Optional[str] = Field(None, description="Human-readable description")

    # Input requirements (V2: Decision is REQUIRED)
    requires_decision: bool = Field(
        ..., description="Whether this framework requires explicit Decision context"
    )
    requires_options: bool = Field(
        ..., description="Whether this framework requires explicit Option definitions"
    )
    input_requirements: List[str] = Field(
        default_factory=list, description="Additional input requirements"
    )

    # Output requirements (V2: MUST be option-aware)
    produces_option_effects: bool = Field(
        ..., description="Whether this framework produces OptionEffect for each option"
    )
    produces_claims: bool = Field(
        ..., description="Whether this framework produces AnalyticalClaim objects"
    )
    produces_assumptions: bool = Field(
        ..., description="Whether this framework produces Assumption objects"
    )
    produces_unknowns: bool = Field(
        ..., description="Whether this framework produces Unknown objects"
    )

    # Implementation details (response_model excluded from Pydantic validation)
    prompt_template: str = Field(..., description="Path to prompt template file")

    # Store response model separately (not validated by Pydantic)
    __response_model_class__: Optional[Any] = None

    output_schema: Dict[str, Any] = Field(
        default_factory=dict, description="JSON schema for expected output"
    )

    def set_response_model(self, model_class: Any):
        """Set the response model class (used internally)"""
        object.__setattr__(self, "__response_model_class__", model_class)

    @property
    def response_model(self) -> Any:
        """Get the response model class"""
        return self.__response_model_class__


__all__ = [
    "FrameworkContract",
]
