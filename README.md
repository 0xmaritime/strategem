# Strategem Core

A decision support system for business analysis that structures unstructured input and runs independent analytical frameworks via LLM inference.

## Features

- **Context Ingestion**: Parse problem context from text or documents
- **Porter's Five Forces Analysis**: Assess structural industry attractiveness
- **Qualitative Systems Dynamics**: Understand feedback loops and system fragility
- **Structured Report Generation**: Produce clear, human-readable analytical reports
- **Uncertainty Surfacing**: Explicitly identify risks, unknowns, and missing information

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your OpenRouter API key:
```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

Optional configuration:
```bash
export LLM_MODEL="anthropic/claude-3.5-sonnet"  # Default model
export LLM_TEMPERATURE="0.2"  # Default: 0.2
export LLM_MAX_TOKENS="4000"  # Default: 4000
```

## Usage

### Web Interface (Recommended)

Start the web server:
```bash
python -m strategem.web.app
```

Or use the command:
```bash
strategem-web
```

Then open http://localhost:8000 in your browser.

The web interface provides:
- **Upload form**: Paste text or upload files
- **Results view**: Structured report with analysis details
- **History**: Browse past analyses
- **Download**: Export reports as Markdown

### CLI Interface

#### Analyze a company from text:
```bash
python -m strategem.cli analyze --text "Your company description here..."
```

#### Analyze from a file:
```bash
python -m strategem.cli analyze --file ./company_info.txt
```

#### Save report to specific location:
```bash
python -m strategem.cli analyze --file ./company_info.txt --output ./reports/my_report.md
```

## Project Structure

```
strategem/
├── __init__.py
├── config.py              # Configuration settings
├── models.py              # Data models (Pydantic)
├── context_ingestion.py   # Document/text parsing
├── llm_layer.py           # OpenRouter integration
├── orchestrator.py        # Analysis workflow
├── report_generator.py    # Report generation
├── persistence.py         # Local storage
├── cli.py                 # Command-line interface
├── prompts/               # LLM prompt templates
│   ├── system.txt
│   ├── porter.txt
│   └── systems_dynamics.txt
└── web/                   # FastAPI web application
    ├── app.py             # FastAPI app & routes
    ├── templates/         # Jinja2 HTML templates
    │   ├── index.html     # Upload form
    │   ├── results.html   # Analysis results
    │   ├── list.html      # Analysis history
    │   └── error.html     # Error page
    └── static/css/        # Stylesheets
        └── style.css
```

## Architecture

Strategem Core follows a pipeline architecture:

1. **Context Ingestion** → Parse input materials
2. **Analysis Orchestration** → Run two independent frameworks
3. **LLM Inference** → Generate structured analyses
4. **Report Generation** → Collate results into human-readable format
5. **Persistence** → Store results locally

## Design Principles

- **Transparency**: All claims traceable to input or explicit assumptions
- **Determinism**: Fixed prompts, low temperature, no hidden state
- **No Recommendations**: System does not make investment decisions
- **Explicit Uncertainty**: Unknowns and risks clearly surfaced

## License

MIT
