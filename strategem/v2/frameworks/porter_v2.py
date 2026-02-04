"""Strategem V2 - Porter Five Forces Framework (V2 Implementation)"""

from pydantic import BaseModel

from ..models import FrameworkContract
from ..models import PorterAnalysisV2

PORTER_V2_FRAMEWORK = FrameworkContract(
    name="porter_five_forces_v2",
    analytical_lens="structural_attractiveness",
    description="Analyzes structural attractiveness of the target system's operating environment using Porter's Five Forces framework. V2: Option-aware and decision-bound.",
    requires_decision=True,
    requires_options=True,
    input_requirements=["problem_context", "decision_question", "options"],
    produces_option_effects=True,
    produces_claims=True,
    produces_assumptions=True,
    produces_unknowns=True,
    prompt_template="porter_v2.txt",
    output_schema={
        "type": "object",
        "properties": {
            "DecisionQuestion": {"type": "string"},
            "OptionsAnalyzed": {"type": "array", "items": {"type": "string"}},
            "ThreatOfNewEntrants": {
                "type": "object",
                "properties": {
                    "Name": {"type": "string"},
                    "RelevanceToDecision": {"type": "string"},
                    "RelevanceRationale": {"type": "string"},
                    "EffectByOption": {"type": "array"},
                    "SharedAssumptions": {"type": "array"},
                    "SharedUnknowns": {"type": "array"},
                },
            },
            "SupplierPower": {"type": "object"},
            "BuyerPower": {"type": "object"},
            "Substitutes": {"type": "object"},
            "Rivalry": {"type": "object"},
            "StructuralAsymmetries": {"type": "array"},
            "OptionAwareClaims": {"type": "array"},
        },
    },
)

PORTER_V2_FRAMEWORK.set_response_model(PorterAnalysisV2)


__all__ = ["PORTER_V2_FRAMEWORK"]
