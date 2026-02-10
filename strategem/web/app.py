"""Strategem Core - FastAPI Web Application"""

import os
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from strategem.core import config
from strategem.v1 import (
    ContextIngestionModule,
    ContextIngestionError,
    AnalysisOrchestrator,
    ReportGenerator,
    PersistenceLayer,
    DecisionFocus,
    DecisionType,
)
from strategem.v2 import (
    V2AnalysisOrchestrator,
    V2PersistenceLayer,
    V2ArtefactGenerator,
    Decision,
    Option,
)


def _build_decision_focus_from_form(
    decision_question: Optional[str],
    decision_type: Optional[str],
    options: Optional[str],
) -> Optional[DecisionFocus]:
    """
    Build DecisionFocus from form inputs (optional hint, not requirement).

    V1: Forms are optional hints, never epistemic authorities.
    """
    if decision_question and options:
        options_list = [opt.strip() for opt in options.split(",")]
        return DecisionFocus(
            decision_question=decision_question,
            decision_type=DecisionType(decision_type or "explore"),
            options=options_list,
        )
    return None


app = FastAPI(
    title="Strategem Core",
    description="Decision Support System for Business Analysis",
    version="2.0.0-dev",
)

# Mount static files
app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)

# Templates
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Initialize V1 modules
context_ingestion = ContextIngestionModule()
orchestrator = AnalysisOrchestrator()
report_generator = ReportGenerator()
persistence = PersistenceLayer()

# Initialize V2 modules
v2_orchestrator = V2AnalysisOrchestrator()
v2_artefact_generator = V2ArtefactGenerator()
v2_persistence = V2PersistenceLayer()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Landing page for version selection"""
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/v1", response_class=HTMLResponse)
async def v1_home(request: Request):
    """V1 analysis page"""
    return templates.TemplateResponse("v1_index.html", {"request": request})


@app.get("/v2", response_class=HTMLResponse)
async def v2_home(request: Request):
    """V2 analysis page"""
    return templates.TemplateResponse("v2_index.html", {"request": request})


@app.post("/analyze/text")
async def analyze_text(
    request: Request,
    text: str = Form(...),
    decision_question: Optional[str] = Form(None),
    decision_type: Optional[str] = Form(None),
    options: Optional[str] = Form(None),
    version: str = Form("v1"),
):
    """Analyze text input (V1 or V2)"""
    if version == "v2":
        return await _analyze_v2_text(
            request, text, decision_question, decision_type, options
        )
    return await _analyze_v1_text(
        request, text, decision_question, decision_type, options
    )


async def _analyze_v1_text(
    request: Request,
    text: str,
    decision_question: Optional[str],
    decision_type: Optional[str],
    options: Optional[str],
):
    """V1 text analysis (optional DecisionFocus)"""
    try:
        decision_focus = _build_decision_focus_from_form(
            decision_question, decision_type, options
        )

        context = context_ingestion.ingest_text(text, decision_focus=decision_focus)
        context = context_ingestion.structure_content(context)

        result = orchestrator.run_full_analysis(context)

        report = report_generator.generate_report(result)
        report_path = report_generator.save_report(report)

        result.generated_report = report.generated_report

        persistence.save_analysis(result)

        return RedirectResponse(url=f"/analysis/{result.id}", status_code=303)

    except Exception as e:
        import sys
        import traceback

        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"ERROR in _analyze_v1_text: {error_msg}", file=sys.stderr)
        print(f"TRACE: {error_trace}", file=sys.stderr)
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": error_msg, "error_trace": error_trace},
            status_code=500,
        )


async def _analyze_v2_text(
    request: Request,
    text: str,
    decision_question: Optional[str],
    decision_type: Optional[str],
    options: Optional[str],
):
    """V2 text analysis (decision and options are optional)"""
    try:
        decision = None
        options_objs = None

        if decision_question:
            decision = Decision(
                decision_question=decision_question,
                decision_type=DecisionType(decision_type or "explore"),
            )

        if options:
            options_list = [opt.strip() for opt in options.split(",")]
            options_objs = [
                Option(name=opt_name, description=f"Option: {opt_name}")
                for opt_name in options_list
            ]

        result = v2_orchestrator.run_full_analysis(
            decision=decision, options=options_objs, context=text
        )

        v2_persistence.save_analysis(result)

        artefacts = v2_artefact_generator.generate_all_artefacts(
            result.analysis_id,
            decision,
            options_objs,
            result.framework_results,
            result.tension_map,
        )

        for artefact in artefacts:
            v2_persistence.save_artefact(artefact)

        # Generate and save markdown report for V2
        report_content = generate_v2_report(result, artefacts)
        report_path = config.REPORTS_DIR / f"report_{result.analysis_id}.md"
        config.REPORTS_DIR.mkdir(exist_ok=True)
        report_path.write_text(report_content)

        return RedirectResponse(
            url=f"/analysis/v2/{result.analysis_id}", status_code=303
        )

    except Exception as e:
        return templates.TemplateResponse(
            "error.html", {"request": request, "error": str(e)}
        )


def generate_v2_report(
    result: AnalysisResult, artefacts: List[AnalysisArtefact]
) -> str:
    """
    Generate markdown report for V2 analysis.

    V2 (Reasoning Substrate): Decision and options are optional.
    Structured report with claims and unknowns.
    """
    lines = []

    # Header
    lines.append(f"# Strategem Core V2 - Analysis Report")
    lines.append("")
    lines.append(f"**Analysis ID:** {result.analysis_id}")
    lines.append(f"**Generated:** {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Disclaimer
    lines.append("> ⚠️ **This is a reasoned artifact, NOT a recommendation.**")
    lines.append(
        "> This system does NOT output decisions, rank options, optimize objectives, or make recommendations."
    )
    lines.append("> The Decision Owner retains full responsibility.")
    lines.append("")

    # Decision Context (optional)
    if result.decision:
        lines.append("## Decision Context")
        lines.append("")
        lines.append(f"- **Question:** {result.decision.decision_question}")
        if result.decision.decision_type:
            lines.append(f"- **Type:** {result.decision.decision_type.value}")
        if result.options_analyzed:
            lines.append(f"- **Options:** {', '.join(result.options_analyzed)}")
        lines.append("")

    # Framework Results
    lines.append("## Framework Analysis Results")
    lines.append("")

    for fw_result in result.framework_results:
        if not fw_result.success:
            lines.append(f"### ❌ {fw_result.framework_name} - FAILED")
            if fw_result.execution_reason:
                lines.append(f"**Reason:** {fw_result.execution_reason}")
            lines.append("")
            continue

        lines.append(f"### {fw_result.framework_name}")
        lines.append("")

        # Claims
        if fw_result.claims:
            lines.append(f"**Claims ({len(fw_result.claims)}):**")
            for i, claim in enumerate(fw_result.claims, 1):
                lines.append(f"{i}. {claim.statement}")
                lines.append(f"   - Framework: {claim.framework}")
                lines.append(f"   - Confidence: {claim.confidence.value}")
                lines.append(f"   - Source: {claim.source.value}")
                lines.append(f"   - Affects: {', '.join(claim.affected_options)}")
                lines.append("")
        else:
            lines.append("**Claims: None**")
            lines.append("")

        # Assumptions
        if fw_result.assumptions:
            lines.append(f"**Assumptions ({len(fw_result.assumptions)}):**")
            for i, assumption in enumerate(fw_result.assumptions, 1):
                lines.append(f"{i}. {assumption}")
            lines.append("")
        else:
            lines.append("**Assumptions: None**")
            lines.append("")

        # Unknowns
        if fw_result.unknowns:
            lines.append(f"**Unknowns ({len(fw_result.unknowns)}):**")
            for i, unknown in enumerate(fw_result.unknowns, 1):
                lines.append(f"{i}. {unknown}")
            lines.append("")
        else:
            lines.append("**Unknowns: None**")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Tension Mapping
    if result.tension_map:
        lines.append("## Framework Tension Mapping")
        lines.append("")
        lines.append(f"**Summary:** {result.tension_map.summary}")
        lines.append("")

        if result.tension_map.agreement_areas:
            lines.append("**Areas of Agreement:**")
            for area in result.tension_map.agreement_areas:
                lines.append(f"- {area}")
            lines.append("")

        if result.tension_map.tension_areas:
            lines.append("**Areas of Tension:**")
            for area in result.tension_map.tension_areas:
                lines.append(f"- {area}")
            lines.append("")

        if result.tension_map.contradiction_areas:
            lines.append("**Areas of Contradiction:**")
            for area in result.tension_map.contradiction_areas:
                lines.append(f"- {area}")
            lines.append("")

        if result.tension_map.framework_tensions:
            lines.append("**Framework Tensions:**")
            for ft in result.tension_map.framework_tensions:
                lines.append("")
                lines.append(f"**{ft.framework_1} vs {ft.framework_2}**")
                lines.append(f"- Type: {ft.tension_type.value}")
                lines.append(f"- Summary: {ft.summary}")
                if ft.resolution_areas:
                    lines.append(f"- Resolution Required:")
                    for area in ft.resolution_areas:
                        lines.append(f"  - {area}")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Sensitivity Triggers
    if result.sensitivity_triggers:
        lines.append("## Sensitivity Triggers")
        lines.append("")
        for i, trigger in enumerate(result.sensitivity_triggers, 1):
            lines.append(f"### {i}. {trigger.trigger_description}")
            lines.append(
                f"- **Evidence needed:** {trigger.evidence_needed or 'Not specified'}"
            )
            if trigger.question_generated:
                lines.append(f"- **Question:** {trigger.question_generated}")
            lines.append("")

    # Structured Artefacts
    if artefacts:
        lines.append("## Structured Artefacts")
        lines.append("")
        for artefact in artefacts:
            lines.append(f"### {artefact.artefact_type.replace('_', ' ').title()}")
            lines.append(f"- **ID:** {artefact.artefact_id}")
            lines.append(f"- **Type:** {artefact.artefact_type}")
            lines.append(f"- **Version:** {artefact.version}")
            lines.append(
                f"- **Generated:** {artefact.generated_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            if artefact.content_hash:
                lines.append(f"- **Hash:** {artefact.content_hash}")
            lines.append("")
        lines.append("---")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*Strategem Core v2.0.0-dev - A reasoning scaffold, not an oracle.*")
    lines.append(
        "*V2: Reasoning Substrate | Judgment Externalization | Framework Toggleability*"
    )

    return "\n".join(lines)


@app.post("/analyze/file")
async def analyze_file(
    request: Request,
    file: UploadFile = File(...),
    decision_question: Optional[str] = Form(None),
    decision_type: Optional[str] = Form(None),
    options: Optional[str] = Form(None),
    version: str = Form("v1"),
):
    """Analyze uploaded file (V1 or V2)"""
    if version == "v2":
        return await _analyze_v2_file(
            request, file, decision_question, decision_type, options
        )
    return await _analyze_v1_file(
        request, file, decision_question, decision_type, options
    )


async def _analyze_v1_file(
    request: Request,
    file: UploadFile,
    decision_question: Optional[str],
    decision_type: Optional[str],
    options: Optional[str],
):
    """V1 file analysis (optional DecisionFocus)"""
    try:
        temp_path = config.STORAGE_DIR / f"temp_{uuid.uuid4()}_{file.filename}"
        content = await file.read()
        temp_path.write_bytes(content)

        try:
            decision_focus = _build_decision_focus_from_form(
                decision_question, decision_type, options
            )

            context = context_ingestion.ingest_file(
                temp_path, decision_focus=decision_focus
            )
            context = context_ingestion.structure_content(context)

            result = orchestrator.run_full_analysis(context)

            report = report_generator.generate_report(result)
            report_path = report_generator.save_report(report)

            result.generated_report = report.generated_report

            persistence.save_analysis(result)

            return RedirectResponse(url=f"/analysis/{result.id}", status_code=303)

        finally:
            if temp_path.exists():
                temp_path.unlink()

    except Exception as e:
        return templates.TemplateResponse(
            "error.html", {"request": request, "error": str(e)}
        )


async def _analyze_v2_file(
    request: Request,
    file: UploadFile,
    decision_question: Optional[str],
    decision_type: Optional[str],
    options: Optional[str],
):
    """V2 file analysis (decision and options are optional)"""
    try:
        decision = None
        options_objs = None

        if decision_question:
            decision = Decision(
                decision_question=decision_question,
                decision_type=DecisionType(decision_type or "explore"),
            )

        if options:
            options_list = [opt.strip() for opt in options.split(",")]
            options_objs = [
                Option(name=opt_name, description=f"Option: {opt_name}")
                for opt_name in options_list
            ]

        temp_path = config.STORAGE_DIR / f"temp_{uuid.uuid4()}_{file.filename}"
        content = await file.read()
        temp_path.write_bytes(content)

        try:
            result = v2_orchestrator.run_full_analysis(
                decision=decision, options=options_objs, context=temp_path.read_text()
            )

            v2_persistence.save_analysis(result)

            artefacts = v2_artefact_generator.generate_all_artefacts(
                result.analysis_id,
                decision,
                options_objs,
                result.framework_results,
                result.tension_map,
            )

            for artefact in artefacts:
                v2_persistence.save_artefact(artefact)

            return RedirectResponse(
                url=f"/analysis/v2/{result.analysis_id}", status_code=303
            )

        finally:
            if temp_path.exists():
                temp_path.unlink()

    except Exception as e:
        return templates.TemplateResponse(
            "error.html", {"request": request, "error": str(e)}
        )


@app.get("/analysis/{analysis_id}", response_class=HTMLResponse)
async def view_analysis(request: Request, analysis_id: str):
    """View V1 analysis results"""
    result = persistence.load_analysis(analysis_id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    report_path = config.REPORTS_DIR / f"report_{analysis_id}.md"
    report_content = None
    if report_path.exists():
        report_content = report_path.read_text()

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "version": "v1",
            "result": result,
            "report_content": report_content,
            "has_systems": result.systems_analysis is not None,
        },
    )


@app.get("/analysis/v2/{analysis_id}", response_class=HTMLResponse)
async def view_v2_analysis(request: Request, analysis_id: str):
    """View V2 analysis results"""
    import sys

    try:
        result = v2_persistence.load_analysis(analysis_id)

        if not result:
            raise HTTPException(status_code=404, detail="V2 Analysis not found")

        artefacts = v2_persistence.load_all_artefacts()
        # Filter artefacts to only show those for the current analysis
        analysis_artefacts = [a for a in artefacts if a.analysis_id == analysis_id]

        return templates.TemplateResponse(
            "results_v2.html",
            {
                "request": request,
                "version": "v2",
                "result": result,
                "artefacts": analysis_artefacts,
            },
        )
    except Exception as e:
        import traceback

        print(f"Error rendering V2 results: {e}", file=sys.stderr)
        print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@app.get("/analyses", response_class=HTMLResponse)
async def list_analyses(request: Request, version: str = Query("v1")):
    """List all analyses (V1 or V2)"""
    if version == "v2":
        return await _list_v2_analyses(request)
    return await _list_v1_analyses(request)


async def _list_v1_analyses(request: Request):
    """List V1 analyses"""
    analysis_ids = persistence.list_analyses()
    analyses = []

    for analysis_id in analysis_ids:
        result = persistence.load_analysis(analysis_id)
        if result:
            analyses.append(
                {
                    "id": result.id,
                    "title": result.problem_context.title,
                    "created_at": result.created_at,
                    "problem_context": result.problem_context,
                    "framework_results": result.framework_results,
                    "version": "v1",
                }
            )

    analyses.sort(key=lambda x: x["created_at"], reverse=True)

    return templates.TemplateResponse(
        "list.html", {"request": request, "analyses": analyses, "version": "v1"}
    )


async def _list_v2_analyses(request: Request):
    """List V2 analyses"""
    analysis_ids = v2_persistence.list_analyses()
    analyses = []

    for analysis_id in analysis_ids:
        result = v2_persistence.load_analysis(analysis_id)
        if result:
            title = (
                result.decision.decision_question
                if result.decision
                else f"Analysis {analysis_id[:8]}"
            )
            analyses.append(
                {
                    "id": result.analysis_id,
                    "title": title,
                    "created_at": result.created_at,
                    "framework_results": result.framework_results,
                    "version": "v2",
                }
            )

    analyses.sort(key=lambda x: x["created_at"], reverse=True)

    return templates.TemplateResponse(
        "list.html", {"request": request, "analyses": analyses, "version": "v2"}
    )


@app.get("/report/{analysis_id}/download")
async def download_report(analysis_id: str):
    """Download analysis report as Markdown file"""
    report_path = config.REPORTS_DIR / f"report_{analysis_id}.md"

    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        path=report_path,
        filename=f"strategem_report_{analysis_id}.md",
        media_type="text/markdown",
    )


@app.get("/report/v2/{analysis_id}/download")
async def download_v2_report(analysis_id: str):
    """Download V2 analysis report as Markdown file"""
    report_path = config.REPORTS_DIR / f"report_{analysis_id}.md"

    if not report_path.exists():
        raise HTTPException(status_code=404, detail="V2 Report not found")

    return FileResponse(
        path=report_path,
        filename=f"strategem_v2_report_{analysis_id}.md",
        media_type="text/markdown",
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0-dev", "versions": ["v1", "v2"]}


def main():
    """Run the FastAPI application"""
    uvicorn.run("strategem.web.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
