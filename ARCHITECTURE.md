# Strategem Core Architecture Documentation

## System Overview

Strategem Core is a decision support system with two analysis versions. V1 is fully functional. V2 is partially implemented with framework execution issues.

### Version Status

| Version | Status | Architecture | State |
|---------|--------|-------------|--------|
| **V1** | ✅ Stable, Production-Ready | Monolithic, Inferred Decision | Fully Functional |
| **V2** | ⚠️ In Development | Versioned, Required Decision | Partially Implemented |

## Core Philosophy

### What This System Is
- A **reasoning scaffold** that structures thinking
- A **multi-lens analysis** tool applying different frameworks
- An **uncertainty surfacing** mechanism
- A **decision support** system (not decision maker)

### What This System Is NOT
- An oracle or recommendation engine
- A learning system that improves over time
- A validator of external reality
- A domain expert or authority
- A ranking or optimization tool

### Key Design Decisions
1. **Framework Independence**: Frameworks run independently and may disagree
2. **Explicit Uncertainty**: Unknowns are surfaced, not hidden
3. **No Recommendations**: System provides analysis, not advice
4. **Domain Agnostic**: Works on Problem Context, not specific domains
5. **Deterministic**: Fixed prompts, low temperature, reproducible outputs
6. **Decision Focus Inference**: Inferred from context, not required via forms
7. **No Framework Gating**: Frameworks adapt to context, never block analysis

---

## Current Implementation Status

### V1 (Stable - Production Ready)

**Status: ✅ Fully Functional**

- **Problem Context**: Ingestion, parsing, formalization (working)
- **Orchestrator**: Framework execution, result aggregation (working)
- **Frameworks**: Porter Five Forces, Systems Dynamics (working)
- **Report Generator**: Markdown output with all sections (working)
- **Persistence**: JSON + Markdown storage (working)
- **CLI**: Full V1 analysis commands (working)
- **Web UI**: `/v1` entry point (working)

### V2 (In Development - Known Issues)

**Status: ⚠️ Partially Implemented**

**What's Working:**
- ✅ Version isolation (v1/ and v2/ separated)
- ✅ Core layer (mechanical primitives only)
- ✅ V2 models (enums, core, tension, dependency, sensitivity, output, framework)
- ✅ V2 web UI (`/v2` entry point with required fields)
- ✅ Separate landing page (`/`) for version selection

**What's NOT Working:**
- ❌ **V2 Framework Execution**: Frameworks are defined but LLM response parsing fails consistently
  - Issue: Pydantic validation errors (mismatched field names, required fields)
  - Root cause: LLM output format doesn't match V2 model expectations
  - Result: V2 analyses fail with validation errors

**Known V2 Limitations:**
- V2 prompts (`porter_v2.txt`, `systems_dynamics_v2.txt`) exist but produce incompatible JSON
- V2 models are designed with many optional fields to handle parsing issues
- `V2AnalysisOrchestrator` has framework registration but framework execution fails
- Tension mapper and artefact generator exist but can't be tested due to framework failures

**Development Path Forward:**
1. Fix LLM prompt-output alignment (simplify V2 prompts or adjust models)
2. Add fallback parsing for malformed LLM responses
3. Implement robust error handling in V2 orchestrator
4. Add comprehensive V2 integration testing

**Recommendation**: Use V1 for all production analysis. V2 requires additional development to be production-ready.

---

## Architecture Layers

### Layer 1: Problem Context (Input)

**Purpose**: Formalize the problem being analyzed

**Components**:
```
ProblemContext (Root Abstraction)
├── title: str
├── problem_statement: str  
├── objectives: List[str]
├── constraints: List[str]
├── provided_materials: List[ProvidedMaterial]
└── declared_assumptions: List[str]
```

**Key Characteristics**:
- First-class object in the system
- Everything depends on this
- Domain-agnostic structure
- Self-contained problem definition
- Decision Focus: **inferred from context, not required**

**Example Use Cases**:
- Policy decision analysis
- Operational failure review
- Product strategy evaluation
- Target system assessment
- Organizational change planning

### Layer 2: Context Ingestion

**Purpose**: Parse and structure Problem Context Materials

**Flow**:
```
Raw Input (text/file) 
    ↓
ProvidedMaterial objects
    ↓
ProblemContext with formal schema
    ↓
Structured content for frameworks
```

**Backward Compatibility**:
- Legacy fields maintained (raw_content, source_type)
- Graceful degradation for old data
- Migration path for existing analyses

### Layer 3: Framework Layer

**Purpose**: Apply analytical lenses to the problem

**Architecture**:
```
AnalysisOrchestrator
├── _frameworks: Dict[str, AnalysisFramework]
├── _framework_models: Dict[str, Type[BaseModel]]
│
├── register_framework()      # Add new frameworks
├── run_framework()           # Run single framework
└── run_analysis_with_frameworks()  # Run multiple
```

**Current Frameworks**:

#### Operating Environment Structure (Porter's Five Forces)
**Analytical Lens**: Structural Attractiveness

Reveals:
- Threat of New Entrants
- Supplier Power
- Buyer Power
- Threat of Substitutes
- Competitive Rivalry

Output Schema:
```json
{
  "ThreatOfNewEntrants": {
    "Level": "Low | Medium | High",
    "Rationale": "...",
    "Assumptions": [...],
    "Unknowns": [...]
  },
  ...
}
```

#### Target System Dynamics (Systems Dynamics)
**Analytical Lens**: Systemic Fragility

Reveals:
- System overview and structure
- Key components
- Feedback loops (reinforcing/balancing)
- Bottlenecks
- Fragilities
- Assumptions
- Unknowns

Output Schema:
```json
{
  "SystemOverview": "...",
  "KeyComponents": [...],
  "FeedbackLoops": {
    "Reinforcing": [...],
    "Balancing": [...]
  },
  "Bottlenecks": [...],
  "Fragilities": [...],
  "Assumptions": [...],
  "Unknowns": [...]
}
```

**Framework Interface**:
```python
AnalysisFramework:
    name: str
    analytical_lens: str
    input_requirements: List[str]
    prompt_template: str
    output_schema: Dict[str, Any]
    description: Optional[str]
```

**Key Design**: Frameworks are swappable without code changes

### Layer 4: LLM Inference

**Purpose**: Generate structured analyses via LLM

**Components**:
- OpenRouter API integration
- Stateless request/response pattern
- Deterministic temperature (0.2)
- Structured output parsing
- Retry logic

**Process**:
```
System Prompt (common instructions)
    ↓
User Prompt (framework-specific + context)
    ↓
LLM Inference
    ↓
Response Parsing (JSON/YAML)
    ↓
Pydantic Model Validation
    ↓
FrameworkResult
```

**Parsing Strategy**:
1. Try JSON extraction from markdown
2. Try PyYAML parsing
3. Fallback to custom YAML parser
4. Key conversion (PascalCase → snake_case)

### Layer 5: Report Generation

**Purpose**: Collate framework outputs into reasoned artifact

**V1 Report Structure**:
```
Reasoned Artifact
├── Context Summary
│   └── Problem statement, objectives, constraints
├── Key Analytical Claims
│   └── Claims with source and confidence
├── Structural Pressures (Operating Environment)
│   └── Porter analysis reframed
├── Systemic Risks (Target System)
│   └── Systems Dynamics analysis reframed
├── Unknowns & Sensitivities
│   └── All unknowns from all frameworks
├── Framework Agreement & Tension
│   └── Explicit acknowledgment of disagreement
├── Decision Surface
│   ├── Assessment change conditions
│   ├── Dominant unknowns
│   └── Judgment required areas
└── System Limitations
    └── Explicit boundaries
```

**Analytical Claims**:
```python
AnalyticalClaim:
    statement: str
    source: ClaimSource  # input | assumption | inference
    confidence: ConfidenceLevel  # low | medium | high
    framework: str
```

**Decision Surface**:
```python
DecisionSurface:
    assessment_change_conditions: List[str]
    dominant_unknowns: List[str]
    judgment_required_areas: List[str]
    decision_question: Optional[str]
    options: List[str]
```

**Analysis Sufficiency Summary** (V1):
```python
AnalysisSufficiencySummary:
    decision_binding: "decision_context_present" | "genuinely_ambiguous"
    option_coverage: "not_applicable" | "partial" | "complete"
    framework_coverage: "partial" | "complete"
    overall_status: "decision_relevant_reasoning_produced" | "decision_relevant_but_constrained" | "exploratory_pre_decision"
```

### Layer 6: Persistence

**Purpose**: Store analyses for later retrieval

**Storage Format**: JSON

**Backward Compatibility**:
- Saves all V1 fields
- Loads with defaults for missing fields
- Graceful handling of legacy data

**Schema**:
```json
{
  "id": "uuid",
  "problem_context": {
    "title": "...",
    "problem_statement": "...",
    "objectives": [...],
    "constraints": [...],
    "provided_materials": [...],
    "declared_assumptions": [...],
    "raw_content": "...",
    "structured_content": "...",
    "source_type": "..."
  },
  "framework_results": [...],
  "porter_analysis": {...},
  "systems_analysis": {...},
  "created_at": "isoformat",
  "generated_report": "..."
}
```

## Data Flow

### Complete Analysis Flow

```
┌──────────────────────────────────────────────────────────────┐
│ 1. INPUT: Problem Context Materials                          │
│    User provides text/files describing the problem           │
└──────────────────────────────────────────────────────────────┘
                              ↓
 ┌──────────────────────────────────────────────────────────────┐
 │ 2. INGESTION: ContextIngestionModule                         │
 │    - Parse materials into ProvidedMaterial objects           │
 │    - Create ProblemContext with formal schema                │
 │    - Structure content for framework consumption             │
 │    - Infer decision focus from context (if not provided)  │
 └──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ 3. ORCHESTRATION: AnalysisOrchestrator                       │
│    - Register available frameworks                           │
│    - Run each framework independently                        │
│    - Collect FrameworkResult objects                         │
│    - Note: Frameworks may disagree (valid outcome)           │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ 4. LLM INFERENCE (per framework): LLMInferenceLayer          │
│    - Load system prompt (common instructions)                │
│    - Load framework-specific user prompt                     │
│    - Inject structured context                               │
│    - Call OpenRouter API                                     │
│    - Parse structured response                               │
│    - Validate against Pydantic model                         │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ 5. RESULT COLLECTION: AnalysisResult                         │
│    - Aggregate all framework results                         │
│    - Track success/failure per framework                     │
│    - Maintain backward compatibility fields                  │
└──────────────────────────────────────────────────────────────┘
                              ↓
 ┌──────────────────────────────────────────────────────────────┐
 │ 6. REPORT GENERATION: ReportGenerator                        │
 │    - Extract analytical claims from each framework           │
 │    - Generate Context Summary                                │
 │    - Create Structural Pressures section                     │
 │    - Create Systemic Risks section                           │
 │    - Compile Unknowns & Sensitivities                        │
 │    - Generate Framework Agreement & Tension                  │
 │    - Build Decision Surface                                  │
 │    - Compute Analysis Sufficiency Summary (V1)                 │
 │    - Add explicit limitations                                │
 │    - Inject hardcoded disclaimer                             │
 └──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ 7. PERSISTENCE: PersistenceLayer                             │
│    - Save AnalysisResult to JSON                             │
│    - Save Markdown report to file                            │
│    - Both stored in local filesystem                         │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ 8. OUTPUT: Reasoned Artifact                                 │
│    - Markdown report with all sections                       │
│    - Downloadable from web interface                         │
│    - Viewable in browser                                     │
│    - ⚠️  Clearly marked as NOT a recommendation              │
└──────────────────────────────────────────────────────────────┘
```

## Key Design Patterns

### 1. Strategy Pattern (Frameworks)
Frameworks implement the same interface but with different algorithms:
- Operating Environment Structure: External pressure analysis
- Target System Dynamics: Internal fragility analysis
- Future frameworks can be added without code changes

### 2. Template Method (Report Generation)
Report sections follow a consistent pattern:
- Generate section header
- Extract and format claims
- Handle missing data gracefully
- Produce markdown output

### 3. Adapter Pattern (LLM Layer)
LLMInferenceLayer adapts OpenRouter API:
- Normalizes different response formats
- Handles parsing errors
- Provides consistent interface

### 4. Repository Pattern (Persistence)
PersistenceLayer abstracts storage:
- JSON serialization/deserialization
- Schema versioning
- Local filesystem implementation

## Separation of Concerns

### Core vs Web
- **Core**: All reasoning logic (models, orchestrator, prompts, report generator)
- **Web**: Thin adapter layer (FastAPI routes, templates, static files)
- **CLI**: Independent interface using core modules
- **Benefit**: Core can run without web dependencies

### Framework Independence
- Each framework is self-contained
- No shared state between frameworks
- No cross-framework contamination in prompts
- Disagreement is valid and expected

### Input/Output Separation
- Input: ProblemContext formal schema
- Processing: Framework analysis
- Output: Reasoned artifact (not recommendation)

## Error Handling

### Ingestion Errors
- File not found → ContextIngestionError
- Encoding issues → Try multiple encodings
- Empty content → Validation error

### LLM Errors
- API failure → Retry once, then fail
- Parse error → Retry once with cleaned output
- Schema mismatch → Mark as incomplete

### Framework Errors
- Individual framework failure → Mark in FrameworkResult
- Other frameworks continue independently
- Partial reports are valid
- **Frameworks adapt to context, not gate on missing decision focus**

## Testing Strategy

### Unit Tests
- Model validation
- Context ingestion
- Report generation sections

### Integration Tests
- End-to-end analysis flow
- Framework registration
- Persistence save/load

### System Tests
- CLI independence (no web deps)
- Web server startup
- API endpoint responses

### Sample Test Cases
- Business scenario (sample_company.txt)
- Non-business scenario (sample_remote_team.txt)
- Edge cases (empty input, parse errors)

## Extension Points

### Adding New Frameworks

1. **Create Prompt Template**
   ```
   prompts/new_framework.txt
   ```

2. **Define Response Model**
   ```python
   class NewFrameworkAnalysis(BaseModel):
       # Fields matching prompt output schema
   ```

3. **Register Framework**
   ```python
   NEW_FRAMEWORK = AnalysisFramework(
       name="new_framework",
       analytical_lens="what_it_reveals",
       input_requirements=["problem_context"],
       prompt_template="new_framework.txt",
       output_schema={...}
   )
   
   orchestrator.register_framework(
       name="new_framework",
       framework=NEW_FRAMEWORK,
       response_model=NewFrameworkAnalysis
   )
   ```

4. **Update Report Generator** (optional)
   Add section for new framework output

### Custom Persistence

Override PersistenceLayer:
```python
class DatabasePersistence(PersistenceLayer):
    def save_analysis(self, result: AnalysisResult) -> str:
        # Database storage logic
        pass
    
    def load_analysis(self, analysis_id: str) -> Optional[AnalysisResult]:
        # Database retrieval logic
        pass
```

## Performance Considerations

### LLM Calls
- **Synchronous**: Frameworks run sequentially (not parallel in V1)
- **Timeout**: 120 seconds per call
- **Retry**: 1 retry on failure
- **Expected time**: < 2 minutes end-to-end

### Storage
- **Local filesystem**: Fast I/O
- **JSON serialization**: Lightweight
- **No database**: Single-user V1

### Memory
- **Context size**: Limited by LLM context window
- **Report size**: Typically < 50KB markdown

## Security Considerations

### V1 Scope
- Single-user local execution
- No authentication required
- No external sharing
- API keys in environment variables only

### Data Flow
- Problem Context Materials → Local processing only
- No data leaves system except to OpenRouter API
- No storage of API keys in code

## Versioning & Migration

### Current: V1.0.0
- Formal ProblemContext schema
- AnalysisFramework interface
- Domain-neutral terminology

### Migration from Pre-V1
- Persistence layer handles backward compatibility
- Legacy fields populated with defaults
- Graceful degradation for old analyses

## Future Considerations (V2+)

### Potential Enhancements
- Framework consensus mechanisms
- Confidence calibration
- Multi-user support
- Database persistence
- Real-time data ingestion
- Additional frameworks
- API authentication

### V1 Freeze (Behavioral Stability)
- No further behavioral tightening permitted in V1
- Smarter inference, deeper frameworks, better claims → V2 by definition
- Current implementation: v1.0.0 (stable, frozen)

## References

- Pydantic: https://docs.pydantic.dev/
- FastAPI: https://fastapi.tiangolo.com/
- OpenRouter: https://openrouter.ai/
- Porter's Five Forces: https://en.wikipedia.org/wiki/Porter%27s_five_forces_analysis
- Systems Dynamics: https://en.wikipedia.org/wiki/System_dynamics

---

**Document Version**: 1.0.0  
**Last Updated**: February 2026  
**Maintainer**: Strategem Core Team
