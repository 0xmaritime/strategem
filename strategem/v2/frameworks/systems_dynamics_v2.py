"""Strategem V2 - Systems Dynamics Framework (V2 Implementation)"""

from pydantic import BaseModel

from ..models import FrameworkContract
from ..models import SystemsDynamicsAnalysisV2

SYSTEMS_DYNAMICS_V2_FRAMEWORK = FrameworkContract(
    name="systems_dynamics_v2",
    analytical_lens="systemic_fragility",
    description="Analyzes target system dynamics, feedback loops, bottlenecks, and fragilities. V2: Option-aware and decision-bound.",
    requires_decision=True,
    requires_options=True,
    input_requirements=["problem_context", "decision_question", "options"],
    produces_option_effects=True,
    produces_claims=True,
    produces_assumptions=True,
    produces_unknowns=True,
    prompt_template="systems_dynamics_v2.txt",
    response_model=SystemsDynamicsAnalysisV2,
    output_schema={
        "type": "object",
        "properties": {
            "DecisionQuestion": {"type": "string"},
            "OptionsAnalyzed": {"type": "array", "items": {"type": "string"}},
            "SystemOverview": {"type": "string"},
            "KeyComponents": {"type": "array", "items": {"type": "string"}},
            "FeedbackLoops": {
                "type": "object",
                "properties": {
                    "Reinforcing": {"type": "array"},
                    "Balancing": {"type": "array"},
                },
            },
            "Bottlenecks": {"type": "array"},
            "Fragilities": {"type": "array"},
            "OptionAwareClaims": {"type": "array"},
            "Assumptions": {"type": "array"},
            "Unknowns": {"type": "array"},
        },
    },
)

SYSTEMS_DYNAMICS_V2_FRAMEWORK.set_response_model(SystemsDynamicsAnalysisV2)


__all__ = ["SYSTEMS_DYNAMICS_V2_FRAMEWORK"]
