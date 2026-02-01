Strategem Core

Full Product Specification & Technical Task (V1)

⸻

0. Purpose of This Document

This document is a complete, self-sufficient specification for Strategem Core — the minimal, defensible version of the Strategem system.

It is written so that:
	•	A coding agent or engineering team can build the system end-to-end
	•	A reviewer or hiring manager can understand scope, intent, and tradeoffs
	•	No assumptions from later versions (V2 / V3) are required

This version is intentionally constrained.

⸻

1. Product Definition

1.1 What Strategem Core Is

Strategem Core is a decision support system that assists analysts in evaluating a single company by:
	•	Structuring unstructured input (problem context materials)
	•	Running two independent analytical frameworks via LLM inference
	•	Producing a clear, human-readable analytical report
	•	Explicitly surfacing risks, uncertainties, and missing information

The system does not make decisions or recommendations.

⸻

1.2 What Strategem Core Is NOT

Strategem Core deliberately excludes:
	•	Automated invest / reject decisions
	•	Learning, feedback loops, or calibration
	•	Multi-agent debate or persuasion
	•	External or real-time data sources
	•	Scoring beyond coarse qualitative labels

This is not an AI replacement for analysts.
It is a thinking scaffold.

⸻

2. Target User

Primary user:
	•	Business Analyst / Investment Analyst / Strategy Analyst

User characteristics:
	•	Comfortable with structured thinking
	•	Responsible for decision quality
	•	Needs transparency and traceability
	•	Retains final judgment authority

⸻

3. Problem Statement

3.1 Core Problems Addressed
	1.	Inconsistent analytical rigor across analyses
	2.	Overreliance on a single mental model
	3.	Poor visibility into uncertainty and blind spots
	4.	Unstructured notes that are hard to compare or review

3.2 Problems Explicitly Not Addressed
	•	Speed optimization
	•	Predictive accuracy guarantees
	•	Organizational workflow automation

⸻

4. High-Level System Overview

Abstraction note: Strategem Core operates on a Problem Context, not a domain-specific artifact. Investment pitch decks are treated as one possible context input, not a hard dependency.

Abstraction note: Strategem Core operates on a Problem Context, not a domain-specific artifact. Investment problem context materialss are treated as one possible context input, not a hard dependency.

4.1 System Boundary

Strategem Core processes one company at a time.

Input:
	•	Problem Context Package (documents and/or structured text)

Output:
	•	Structured analytical report (Markdown / PDF)

⸻

4.2 Core Components
	1.	Context Ingestion Module
	2.	Analysis Orchestrator
	3.	LLM Inference Layer (OpenRouter API)
	4.	Report Generator
	5.	Persistence Layer (local or DB)

⸻

5. Functional Scope

5.1 Included Functionality
	•	Provide problem context (documents and/or structured text)
	•	Extract structured text sections
	•	Run two independent analyses:
	•	Porter’s Five Forces
	•	Qualitative Systems Dynamics
	•	Generate structured report
	•	Highlight:
	•	Risks
	•	Strengths
	•	Uncertainties
	•	Missing information

⸻

5.2 Out of Scope (V1)
	•	Multiple document types
	•	Multiple companies
	•	External data ingestion
	•	User accounts or permissions
	•	API exposure for third parties

⸻

6. User Workflow

User uploads problem context materials
→ System parses document
→ System extracts structured content
→ Framework 1 analysis runs
→ Framework 2 analysis runs
→ Results are collated
→ Final report is generated
→ User reviews output

User may optionally export the report.

⸻

7. Analytical Frameworks (V1)

7.1 Framework 1: Porter’s Five Forces

Objective:
Assess structural industry attractiveness.

Dimensions:
	1.	Threat of New Entrants
	2.	Bargaining Power of Suppliers
	3.	Bargaining Power of Buyers
	4.	Threat of Substitutes
	5.	Competitive Rivalry

Output per force:
	•	Qualitative assessment (Low / Medium / High)
	•	Short justification
	•	Key assumptions
	•	Identified unknowns

⸻

7.2 Framework 2: Qualitative Systems Dynamics

Objective:
Understand feedback loops, dependencies, and fragility.

Focus areas:
	•	Growth drivers
	•	Bottlenecks
	•	Feedback loops (positive / negative)
	•	Single points of failure
	•	Dependency risks

Output:
	•	Narrative system description
	•	Key reinforcing and balancing loops
	•	Fragility indicators
	•	Areas of uncertainty

⸻

8. LLM Usage & Inference Design

8.1 LLM Role

LLMs are used strictly for:
	•	Text understanding
	•	Structured reasoning
	•	Natural language generation

LLMs are not authoritative sources of truth.

⸻

8.2 OpenRouter Integration

API: OpenRouter

Usage pattern:
	•	Stateless calls
	•	Deterministic temperature (e.g. 0.2–0.3)
	•	One call per framework

Model requirements:
	•	Strong reasoning
	•	Stable outputs
	•	Long context support

Model selection is configurable.

⸻

8.3 Prompting Principles
	•	One framework per prompt
	•	Explicit role instruction
	•	Explicit output schema
	•	Explicit uncertainty reporting
	•	No cross-framework contamination

⸻

9. Prompt Specifications

9.1 Common System Prompt (Shared)

You are an analytical assistant.
Your task is to apply a specific analytical framework to the provided company information.
You must:
- Base reasoning only on provided content
- Explicitly state assumptions
- Explicitly state unknowns
- Avoid recommendations or decisions
- Use structured output exactly as specified


⸻

9.2 Porter Analysis Prompt (User Message)

Input:
	•	Extracted problem context materials content

Required Output Schema:

PorterAnalysis:
  ThreatOfNewEntrants:
    Level: Low | Medium | High
    Rationale:
    Assumptions:
    Unknowns:
  SupplierPower:
    ...
  BuyerPower:
    ...
  Substitutes:
    ...
  Rivalry:
    ...
OverallObservations:
KeyRisks:
KeyStrengths:


⸻

9.3 Systems Dynamics Prompt

Required Output Schema:

SystemOverview:
KeyComponents:
FeedbackLoops:
  Reinforcing:
  Balancing:
Bottlenecks:
Fragilities:
Assumptions:
Unknowns:


⸻

10. Analysis Orchestration Logic

10.1 Execution Order
	1.	Document parsing
	2.	Content structuring
	3.	Porter analysis call
	4.	Systems dynamics call
	5.	Result validation
	6.	Report assembly

Analyses are independent.

⸻

10.2 Error Handling
	•	If LLM output does not match schema → retry once
	•	If retry fails → mark section as “Analysis Incomplete”
	•	Partial reports are allowed

⸻

11. Report Generation

11.1 Report Structure
	1.	Executive Summary
	2.	Context Summary
	3.	Porter’s Five Forces Analysis
	4.	Systems Dynamics Analysis
	5.	Agreement & Tension (manual comparison only)
	6.	Open Questions & Missing Information

⸻

11.2 Executive Summary Rules
	•	Max 1 page
	•	No decisions
	•	No recommendations
	•	Focus on:
	•	Structural attractiveness
	•	System fragility
	•	Uncertainty level

⸻

12. Data Model (Conceptual)

ReasonedAnalysis
- id
- input_document
- extracted_text
- porter_result
- systems_result
- generated_report
- created_at

Persistence can be local file system or database.

⸻

13. Non-Functional Requirements

13.1 Explainability
	•	All claims traceable to either:
	•	Input text
	•	Explicit assumptions

⸻

13.2 Determinism
	•	Fixed prompts
	•	Low temperature
	•	No hidden state between runs

⸻

13.3 Performance (Non-Optimized)
	•	End-to-end run under 2 minutes
	•	No parallelization required

⸻

14. Security & Privacy (V1)
	•	No storage of API keys in code
	•	No external sharing
	•	Single-user local execution assumed

⸻

15. Known Limitations (Explicit)
	•	Analysis quality depends on problem context materials quality
	•	No validation against external reality
	•	Framework outputs may contradict
	•	No learning from past outcomes

These are features, not bugs, at this stage.

⸻

16. Acceptance Criteria

Strategem Core is considered complete if:
	•	A problem context materials can be uploaded
	•	Two analyses are generated
	•	Output follows defined schemas
	•	A structured report is produced
	•	Uncertainty and unknowns are visible
	•	No recommendations are made

⸻

17. Deliverables Checklist
	•	Document ingestion module
	•	Prompt templates
	•	OpenRouter integration
	•	Orchestration logic
	•	Report generator
	•	Sample analysis report

⸻

18. Upgrade Path (Non-Binding)

This version is designed to support:
	•	Additional frameworks
	•	Consensus mechanisms
	•	Confidence calibration

Without refactoring core architecture.

⸻

End of Strategem Core Specification