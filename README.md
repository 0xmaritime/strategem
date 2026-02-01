# Strategem Core v1.0.0

**A Reasoning Scaffold for Decision Support**

Strategem Core is a decision support system that structures unstructured problem context and runs independent analytical frameworks via LLM inference. It produces **reasoned artifacts**, not recommendations.

---

## ⚠️ Critical System Boundaries

**This system does NOT:**
- Output decisions or recommendations
- Rank or compare options  
- Optimize objectives
- Provide investment advice
- Validate against external reality
- Learn from past outcomes
- Claim domain authority

**Framework disagreement is a valid and expected outcome.**

The **Decision Owner** retains full responsibility for all judgments and decisions.

---

## What is Strategem Core?

Strategem Core assists decision-makers by:

1. **Structuring Problem Context**: Formalizing objectives, constraints, and materials
2. **Running Multiple Analytical Frameworks**: Applying independent lenses to the same problem
3. **Explicitly Surfacing Uncertainty**: Identifying unknowns, assumptions, and sensitivities
4. **Providing a Decision Surface**: Clarifying where judgment is required

### Target Applications

Strategem Core is domain-agnostic. It can analyze:
- Policy decisions
- Operational failures  
- Product strategies
- Target system evaluations
- Organizational changes
- Technology migrations

...without mental friction, because it operates on **Problem Context**, not domain-specific artifacts.

---

## Quick Start

### Prerequisites

- Python 3.8+
- OpenRouter API key

### Installation

```bash
# Clone the repository
git clone https://github.com/0xmaritime/strategem.git
cd strategem

# Install dependencies
pip install -r requirements.txt

# Configure environment
export OPENROUTER_API_KEY="your-api-key-here"

# Optional: Configure model
export LLM_MODEL="anthropic/claude-3.5-sonnet"  # Default
export LLM_TEMPERATURE="0.2"                    # Default
export LLM_MAX_TOKENS="4000"                    # Default
```

### Start the Web Interface

```bash
python -m strategem.web.app
# or
strategem-web
```

Then open http://localhost:8000

### Use the CLI

```bash
# Analyze from text
python -m strategem.cli analyze --text "Your problem context here..."

# Analyze from file  
python -m strategem.cli analyze --file ./problem_context.txt

# With formal schema
python -m strategem.cli analyze --file ./problem.txt \
  --title "Q3 Strategy Review" \
  --problem-statement "Evaluate market expansion options"
```

---

## Core Concepts

### Problem Context (First-Class Object)

The root abstraction of the system. Everything depends on this.

```python
ProblemContext:
  title: str                          # Identifier for this analysis
  problem_statement: str              # Clear statement of the problem
  objectives: List[str]               # What the decision owner wants to achieve
  constraints: List[str]              # Known limitations or boundaries
  provided_materials: List[ProvidedMaterial]  # Input documents/texts/data
  declared_assumptions: List[str]     # Explicit assumptions from decision owner
```

**Example Problem Context:**

```
Title: Remote-First Transition Analysis
Problem Statement: Evaluate the robustness of transitioning to a 
                   fully remote-first team structure
Objectives:
  - Maintain engineering productivity
  - Sustain team cohesion
  - Enable global hiring
Constraints:
  - $50K infrastructure budget
  - 18-month lease obligations
Provided Materials:
  - Current productivity metrics
  - Employee satisfaction surveys
  - Infrastructure assessment
```

### Analytical Frameworks

Frameworks are **swappable** without touching orchestration logic.

**Predefined Frameworks:**

| Framework | Analytical Lens | Reveals |
|-----------|----------------|---------|
| **Operating Environment Structure** (Porter's Five Forces) | Structural Attractiveness | Pressures from new entrants, suppliers, buyers, substitutes, competitive intensity |
| **Target System Dynamics** (Systems Dynamics) | Systemic Fragility | Feedback loops, bottlenecks, fragilities, growth drivers |

**Framework Interface:**

```python
AnalysisFramework:
  name: str                    # Framework identifier
  analytical_lens: str         # What this framework reveals
  input_requirements: List[str]  # Required inputs
  prompt_template: str         # Path to prompt template
  output_schema: Dict          # Expected output structure
```

### Analytical Claims

Every framework output produces explicit claims:

```python
AnalyticalClaim:
  statement: str           # The claim
  source: ClaimSource      # input | assumption | inference
  confidence: ConfidenceLevel  # low | medium | high
  framework: str           # Which framework produced this
```

**Example:**
- Statement: "Competitive pressure is High"
- Source: inference
- Confidence: medium
- Framework: porter_five_forces

### Report Structure (V1)

The system produces a **reasoned artifact** with the following sections:

1. **Context Summary**: What was analyzed
2. **Key Analytical Claims**: Explicit claims with sources and confidence levels
3. **Structural Pressures** (Operating Environment): Analysis of external pressures
4. **Systemic Risks** (Target System): Analysis of internal dynamics and fragilities
5. **Unknowns & Sensitivities**: Explicit uncertainty inventory
6. **Framework Agreement & Tension**: Points of convergence and conflict between frameworks
7. **Decision Surface**: 
   - What would need to be true for this assessment to change?
   - Which unknowns dominate outcome variance?
   - Where is judgment explicitly required?
8. **System Limitations**: Explicitly documented boundaries

---

## Detailed Usage Guide

### CLI Reference

#### `analyze` - Run Analysis

```bash
strategem analyze [OPTIONS]

Options:
  -t, --text TEXT              Problem Context Material as text
  -f, --file PATH              Path to file containing material
  --title TEXT                 Title for this analysis
  --problem-statement TEXT     Clear problem statement
  -o, --output PATH            Output path for report
  
Examples:
  # Basic text analysis
  strategem analyze --text "Company X operates in..."
  
  # File analysis
  strategem analyze --file ./company_profile.txt
  
  # With formal schema
  strategem analyze --file ./context.txt \
    --title "Market Entry Analysis" \
    --problem-statement "Should we enter the European market?"
```

#### `frameworks` - List Frameworks

```bash
strategem frameworks

# Output:
# Available Analytical Frameworks:
#   📐 porter_five_forces
#      Analytical Lens: structural_attractiveness
#      Description: Assesses structural attractiveness of the target system's operating environment
```

#### `list` - List Analyses

```bash
strategem list

# Output:
# Found 3 analysis(es):
#   - analysis-id-1 | Market Entry Analysis
#   - analysis-id-2 | Remote Work Evaluation
#   - analysis-id-3 | Untitled Analysis
```

#### `show` - Show Analysis Details

```bash
strategem show <analysis_id>
```

### Web Interface

#### Routes

| Route | Description |
|-------|-------------|
| `/` | Upload form for new analysis |
| `/analyses` | List all saved analyses |
| `/analysis/<id>` | View specific analysis results |
| `/report/<id>/download` | Download report as Markdown |
| `/api/health` | Health check endpoint |

#### POST Endpoints

| Endpoint | Form Data | Description |
|----------|-----------|-------------|
| `/analyze/text` | `text` | Analyze text input |
| `/analyze/file` | `file` | Analyze uploaded file |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Problem Context Package                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │   Material   │ │   Material   │ │   Material   │        │
│  │     1        │ │     2        │ │     N        │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Context Ingestion & Structuring                 │
│           (ProblemContext formal schema)                     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Analysis Orchestrator                           │
│  ┌─────────────────┐        ┌─────────────────┐             │
│  │  Framework 1    │        │  Framework 2    │             │
│  │  (Operating     │        │  (Target        │             │
│  │   Environment)  │        │   System)       │             │
│  └─────────────────┘        └─────────────────┘             │
│           │                          │                       │
│           └──────────┬───────────────┘                       │
│                      ▼                                       │
│           ┌─────────────────┐                               │
│           │  Independent    │                               │
│           │  LLM Inferences │                               │
│           └─────────────────┘                               │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Report Generator                                │
│  - Context Summary                                           │
│  - Key Analytical Claims                                     │
│  - Structural Pressures                                      │
│  - Systemic Risks                                           │
│  - Unknowns & Sensitivities                                  │
│  - Framework Agreement & Tension                             │
│  - Decision Surface                                          │
│  - Limitations                                               │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Reasoned Artifact (Markdown)                    │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### Context Ingestion Module
- Parses Problem Context Materials
- Structures content for framework consumption
- Supports text, files, and composite materials
- Maintains backward compatibility

#### Analysis Orchestrator
- Manages framework lifecycle
- Runs frameworks independently
- Collects results
- No cross-framework contamination

#### LLM Inference Layer
- OpenRouter API integration
- Stateless calls
- Deterministic temperature (0.2)
- Structured output parsing (JSON/YAML)
- Retry logic

#### Report Generator
- Collates framework outputs
- Extracts analytical claims
- Generates Decision Surface
- Produces human-readable Markdown
- Hardcoded disclaimers

#### Persistence Layer
- JSON serialization
- V1 schema support with backward compatibility
- Local file system storage

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Required | API key for OpenRouter |
| `LLM_MODEL` | `openai/gpt-4o-mini` | Model identifier |
| `LLM_TEMPERATURE` | `0.2` | Sampling temperature |
| `LLM_MAX_TOKENS` | `4000` | Max tokens per response |

### Directory Structure

```
strategem/
├── storage/          # Analysis data (JSON)
├── reports/          # Generated reports (Markdown)
└── prompts/          # LLM prompt templates
```

---

## API Reference

### Python API

```python
from strategem import (
    ProblemContext, 
    ContextIngestionModule,
    AnalysisOrchestrator,
    ReportGenerator
)

# Create problem context
ingestion = ContextIngestionModule()
context = ingestion.ingest_text(
    text="Problem description...",
    title="Analysis Title",
    problem_statement="Clear problem statement",
    objectives=["Obj 1", "Obj 2"],
    constraints=["Constraint 1"]
)

# Run analysis
orchestrator = AnalysisOrchestrator()
result = orchestrator.run_full_analysis(context)

# Generate report
report_gen = ReportGenerator()
report = report_gen.generate_report(result)

# Save report
path = report_gen.save_report(report)
```

### Registering Custom Frameworks

```python
from strategem.models import AnalysisFramework

# Define custom framework
my_framework = AnalysisFramework(
    name="custom_analysis",
    analytical_lens="unique_perspective",
    input_requirements=["problem_context"],
    prompt_template="custom_prompt",
    output_schema={...}
)

# Register with orchestrator
orchestrator.register_framework(
    name="custom_analysis",
    framework=my_framework,
    response_model=MyResponseModel
)

# Run custom framework
result = orchestrator.run_analysis_with_frameworks(
    context=context,
    frameworks=["porter", "systems_dynamics", "custom_analysis"]
)
```

---

## Testing

### Run Tests

```bash
# Test CLI independence (no web dependencies)
python -c "from strategem.cli import cli; print('✓ CLI works')"

# Test model imports
python -c "from strategem.models import ProblemContext; print('✓ Models work')"

# Test web app
python -c "from strategem.web.app import app; print('✓ Web app works')"
```

### Sample Test Cases

Two sample files are provided:

1. **sample_company.txt** - Business scenario (SaaS company analysis)
2. **sample_remote_team.txt** - Non-business scenario (remote work structure)

```bash
# Test with company scenario
python -m strategem.cli analyze --file sample_company.txt

# Test with non-business scenario  
python -m strategem.cli analyze --file sample_remote_team.txt
```

---

## Troubleshooting

### Common Issues

**API Key Not Configured:**
```
Error: OpenRouter API key not configured
Solution: export OPENROUTER_API_KEY="your-key"
```

**LLM Output Parse Error:**
```
The system will retry once automatically.
If persistent, check the prompt template formatting.
```

**Port Already in Use:**
```
Error: [Errno 48] Address already in use
Solution: Kill existing process or change port in config
```

### Debug Mode

Set `LLM_TEMPERATURE=0.7` for more varied outputs during testing.

---

## Development

### Project Structure

```
strategem/
├── __init__.py              # Package exports
├── config.py                # Configuration
├── models.py                # Pydantic data models
├── context_ingestion.py     # Input parsing
├── llm_layer.py             # OpenRouter integration
├── orchestrator.py          # Analysis workflow
├── report_generator.py      # Report generation
├── persistence.py           # Local storage
├── cli.py                   # CLI interface
├── prompts/                 # LLM prompts
│   ├── system.txt
│   ├── porter.txt
│   └── systems_dynamics.txt
└── web/                     # FastAPI web app
    ├── app.py
    ├── templates/
    └── static/
```

### Adding New Frameworks

1. Create prompt template in `prompts/`
2. Define response model in `models.py`
3. Register in orchestrator
4. Update documentation

### Design Principles

- **Transparency**: All claims traceable to input or explicit assumptions
- **Determinism**: Fixed prompts, low temperature, no hidden state
- **No Recommendations**: System provides analysis, not advice
- **Explicit Uncertainty**: Unknowns and risks clearly surfaced
- **Framework Independence**: Analyses run independently, disagreement is valid

---

## Known Limitations

- Analysis quality depends on Problem Context Materials quality
- No validation against external reality
- Framework outputs may contradict (this is expected)
- No learning from past outcomes
- No domain authority claimed
- Single-user local execution (V1)

---

## Version History

### v1.0.0 (Current)
- V1 Compliance implementation
- Domain-neutral terminology
- Formal ProblemContext schema
- AnalysisFramework interface
- AnalyticalClaim model
- Decision Surface section
- Explicit system boundaries
- Non-business test case

---

## License

MIT

---

## Contributing

This is a reasoning scaffold, not an oracle. Framework disagreement is a valid and expected outcome.

**Remember:** The Decision Owner retains full responsibility for all judgments and decisions.
