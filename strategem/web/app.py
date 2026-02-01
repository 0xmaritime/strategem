"""Strategem Core - FastAPI Web Application"""

import os
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from strategem.config import config
from strategem.context_ingestion import ContextIngestionModule, ContextIngestionError
from strategem.orchestrator import AnalysisOrchestrator
from strategem.report_generator import ReportGenerator
from strategem.persistence import PersistenceLayer
from strategem.models import AnalysisResult


app = FastAPI(
    title="Strategem Core",
    description="Decision Support System for Business Analysis",
    version="1.0.0",
)

# Mount static files
app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)

# Templates
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Initialize modules
context_ingestion = ContextIngestionModule()
orchestrator = AnalysisOrchestrator()
report_generator = ReportGenerator()
persistence = PersistenceLayer()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page with upload form"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze/text")
async def analyze_text(request: Request, text: str = Form(...)):
    """Analyze text input"""
    try:
        # Ingest and structure content
        context = context_ingestion.ingest_text(text)
        context = context_ingestion.structure_content(context)

        # Run analysis
        result = orchestrator.run_full_analysis(context)

        # Generate and save report
        report = report_generator.generate_report(result)
        report_path = report_generator.save_report(report)

        # Attach generated report to result for persistence
        result.generated_report = report.generated_report

        # Save analysis data
        persistence.save_analysis(result)

        # Redirect to results page
        return RedirectResponse(url=f"/analysis/{result.id}", status_code=303)

    except Exception as e:
        return templates.TemplateResponse(
            "error.html", {"request": request, "error": str(e)}
        )


@app.post("/analyze/file")
async def analyze_file(request: Request, file: UploadFile = File(...)):
    """Analyze uploaded file"""
    try:
        # Save uploaded file temporarily
        temp_path = config.STORAGE_DIR / f"temp_{uuid.uuid4()}_{file.filename}"
        content = await file.read()
        temp_path.write_bytes(content)

        try:
            # Ingest and structure content
            context = context_ingestion.ingest_file(temp_path)
            context = context_ingestion.structure_content(context)

            # Run analysis
            result = orchestrator.run_full_analysis(context)

            # Generate and save report
            report = report_generator.generate_report(result)
            report_path = report_generator.save_report(report)

            # Attach generated report to result for persistence
            result.generated_report = report.generated_report

            # Save analysis data
            persistence.save_analysis(result)

            # Redirect to results page
            return RedirectResponse(url=f"/analysis/{result.id}", status_code=303)

        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()

    except Exception as e:
        return templates.TemplateResponse(
            "error.html", {"request": request, "error": str(e)}
        )


@app.get("/analysis/{analysis_id}", response_class=HTMLResponse)
async def view_analysis(request: Request, analysis_id: str):
    """View analysis results"""
    result = persistence.load_analysis(analysis_id)

    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Load report
    report_path = config.REPORTS_DIR / f"report_{analysis_id}.md"
    report_content = None
    if report_path.exists():
        report_content = report_path.read_text()

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "result": result,
            "report_content": report_content,
            "has_porter": result.porter_analysis is not None,
            "has_systems": result.systems_analysis is not None,
        },
    )


@app.get("/analyses", response_class=HTMLResponse)
async def list_analyses(request: Request):
    """List all analyses"""
    analysis_ids = persistence.list_analyses()
    analyses = []

    for analysis_id in analysis_ids:
        result = persistence.load_analysis(analysis_id)
        if result:
            analyses.append(
                {
                    "id": result.id,
                    "created_at": result.created_at,
                    "source_type": result.problem_context.source_type,
                    "has_porter": result.porter_analysis is not None,
                    "has_systems": result.systems_analysis is not None,
                }
            )

    # Sort by date (newest first)
    analyses.sort(key=lambda x: x["created_at"], reverse=True)

    return templates.TemplateResponse(
        "list.html", {"request": request, "analyses": analyses}
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


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


def main():
    """Run the FastAPI application"""
    uvicorn.run("strategem.web.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
