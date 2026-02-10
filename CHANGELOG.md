# Changelog

All notable changes to Strategem Core will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-04

### Added - V2 Full Implementation & Debugging Fixes

#### Core Layer
- **Response Normalization**: Created `V2ResponseNormalizer` for handling LLM output variations
- **Pydantic Error Logging**: Enhanced validation error reporting with detailed field-level context
- **Enum Normalization**: Case-insensitive mapping for confidence, source, decision_type enums

#### V2 Models
- **Field Aliases**: Added `alias` parameters to `AnalyticalClaim` (Source, Confidence, Framework)
- **Optional Fields**: Relaxed non-load-bearing fields to optional with defaults
- **Union Types**: `Unknowns` fields now accept both `str` and `dict` types
- **Fixed Duplicate Definitions**: Removed duplicate field definitions in `SystemsDynamicsAnalysisV2`

#### V2 LLM Layer
- **Raw LLM Output Logging**: Added comprehensive logging of all LLM responses before parsing
- **Normalization Integration**: All V2 responses now pass through normalization layer
- **Error Recovery**: Improved error handling with detailed traceback logging

#### V2 Orchestrator
- **Partial Success Tolerance**: Framework failures no longer abort entire analysis
- **Enhanced Extraction**: Improved claims/assumptions/unknowns extraction from force objects and systems dynamics models
- **Better Logging**: Added detailed status messages for framework execution

#### V2 Web Interface
- **V2 Entry Point**: Added `/v2` route with required decision question & options
- **V2 Results Page**: Enhanced with full claims, assumptions, unknowns display
- **V2 Report Download**: Added `/report/v2/{id}/download` endpoint for markdown reports
- **Raw Output Details**: Added expandable framework output sections for debugging

#### V2 Artefact Generator
- **V2 Report Generation**: Added markdown report generation with full V2 structure
- **Enhanced Output**: Includes claims, tensions, sensitivity triggers, and structural artefacts

#### Bug Fixes
- **Fixed Web App Decorators**: Removed incorrect `@app.get("/v1")` decorator that broke V2 routes
- **Template Fix**: Fixed `model_dump_json` usage - replaced with `tojson` filter for dict compatibility
- **Framework Extraction**: Fixed assumption/unknown extraction from nested force objects and systems dynamics models

#### Documentation
- **README Updates**: Updated V2 status to "Fully Functional"
- **Architecture Updates**: Updated V2 section to reflect current stable state
- **Route Documentation**: Added V2-specific routes and endpoints
- **Troubleshooting**: Added V2-specific issues and workarounds

---

## [1.0.0] - 2026-02-01

### Added - V1 Compliance Implementation

#### Core Models
- **ProblemContext formal schema**: Added title, problem_statement, objectives, constraints, provided_materials, declared_assumptions
- **AnalyticalClaim model**: Explicit claims with statement, source (input/assumption/inference), confidence (low/medium/high), framework
- **AnalysisFramework interface**: Swappable framework configuration with name, analytical_lens, input_requirements, prompt_template, output_schema
- **DecisionSurface section**: Assessment change conditions, dominant unknowns, judgment required areas
- **FrameworkResult model**: Generic container for framework results
- **ProvidedMaterial model**: Structured problem context materials
- **Predefined frameworks**: SYSTEMS_DYNAMICS_FRAMEWORK constant

#### Domain-Neutral Terminology
- Replaced "company" → "target system"
- Replaced "industry" → "operating environment"
- Replaced "investment/analyst" → "decision owner"
- Replaced "pitch deck" → "problem context material"
- Replaced "business model" → "system structure"

#### Report Structure (V1)
- **Context Summary**: What was analyzed
- **Key Analytical Claims**: Explicit claims with sources and confidence
- **Systemic Risks**: Target system analysis
- **Unknowns & Sensitivities**: Explicit uncertainty inventory
- **Framework Agreement & Tension**: Points of convergence and conflict
- **Decision Surface**: Where judgment is required
  - Assessment change conditions
  - Dominant unknowns
  - Judgment required areas
- **System Limitations**: Explicitly documented boundaries

#### Orchestrator
- **Framework interface**: register_framework() method for extensibility
- **run_framework()**: Run single framework generically
- **run_analysis_with_frameworks()**: Run multiple frameworks
- Framework results collection
- Backward compatibility with legacy methods

#### Context Ingestion
- **Formal schema support**: create_problem_context() for composite materials
- **Enhanced ingest methods**: Support for title, problem_statement, objectives, constraints
- **Material structuring**: Combines provided_materials into structured_content

#### Prompts
- **Domain-neutral language**: Target System, Problem Context Materials
- **Explicit boundaries**: "This system does NOT output decisions, rank options, optimize objectives, or provide recommendations"
- **Framework disagreement**: Explicitly acknowledged as valid and expected outcome
- **Hard rules**: Listed in system prompt

#### CLI
- **New options**: --title, --problem-statement
- **frameworks command**: List available analytical frameworks
- **Enhanced output**: Shows report structure, framework results, disclaimer
- **Updated terminology**: Problem Context Materials, frameworks, etc.

#### Web Interface
- **Disclaimer banner**: Critical system boundaries displayed prominently
- **Updated templates**: Domain-neutral terminology throughout
- **Framework status display**: Shows all framework results
- **Problem Context summary**: Displays title, objectives, constraints

#### Documentation
- **Comprehensive README**: Complete usage guide, API reference, examples
- **Architecture documentation**: Detailed technical architecture
- **This changelog**: Version history

#### Testing
- **Non-business test case**: sample_remote_team.txt (remote-first team structure)
- **Backward compatibility**: All tests pass with legacy data
- **CLI independence**: Core modules work without web dependencies

### Changed

#### Report Generator
- Replaced "Executive Summary" with new V1 structure
- Renamed sections to use domain-neutral terminology
- Added explicit limitations section
- Hardcoded disclaimer in markdown output
- Enhanced claim extraction from framework outputs

#### Persistence
- Updated to handle new V1 ProblemContext fields
- Saves framework_results list
- Backward compatible loading with defaults for missing fields

### Security

#### System Boundaries (Hard Rules)
- System does NOT output decisions
- System does NOT rank options
- System does NOT optimize objectives
- System does NOT provide recommendations
- Framework disagreement is valid

### Known Limitations

- Analysis quality depends on Problem Context Materials quality
- No external validation against reality
- Framework outputs may contradict (this is expected)
- No learning from past outcomes
- No domain authority claimed
- Single-user local execution (V1 scope)

### Technical Details

#### Files Modified
- strategem/models.py (312 lines added)
- strategem/context_ingestion.py (195 lines added)
- strategem/orchestrator.py (179 lines added)
- strategem/report_generator.py (623 lines changed)
- strategem/persistence.py (90 lines added)
- strategem/cli.py (159 lines changed)
- strategem/prompts/*.txt (domain-neutral language)
- strategem/web/templates/*.html (V1 UI)
- strategem/web/app.py (context variables)
- strategem/__init__.py (new exports)

#### Files Added
- sample_remote_team.txt (non-business test case)
- ARCHITECTURE.md (technical documentation)
- CHANGELOG.md (this file)

### Migration Notes

- Persistence layer handles backward compatibility automatically
- Legacy fields (raw_content, source_type) maintained for old data
- Old analyses load with default values for new fields
- No migration script required

## Pre-V1 Versions

### Development Phase
- Initial prototype implementation
- Basic Systems Dynamics analysis
- CLI interface
- Web interface
- Report generation
- Local persistence

---

[1.0.0]: https://github.com/0xmaritime/strategem/releases/tag/v1.0.0
