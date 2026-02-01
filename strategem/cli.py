"""Strategem Core - Command Line Interface"""

import sys
import click
from pathlib import Path

from strategem.context_ingestion import ContextIngestionModule, ContextIngestionError
from strategem.orchestrator import AnalysisOrchestrator
from strategem.report_generator import ReportGenerator
from strategem.persistence import PersistenceLayer


@click.group()
def cli():
    """Strategem Core - Decision Support System for Business Analysis"""
    pass


@cli.command()
@click.option("--text", "-t", help="Company information as text string")
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="Path to file containing company information",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output path for report (default: auto-generated)",
)
def analyze(text, file, output):
    """Run strategic analysis on company information"""

    # Validate input
    if not text and not file:
        click.echo("Error: Must provide either --text or --file", err=True)
        sys.exit(1)

    if text and file:
        click.echo("Error: Cannot use both --text and --file", err=True)
        sys.exit(1)

    # Ingest context
    ingestion = ContextIngestionModule()
    try:
        if text:
            click.echo("📄 Ingesting text input...")
            context = ingestion.ingest_text(text)
        else:
            click.echo(f"📄 Ingesting file: {file}")
            context = ingestion.ingest_file(file)

        # Structure content
        context = ingestion.structure_content(context)
        click.echo("✓ Context ingested successfully")

    except ContextIngestionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    # Run analysis
    click.echo("\n🔍 Running Porter's Five Forces analysis...")
    orchestrator = AnalysisOrchestrator()

    try:
        result = orchestrator.run_full_analysis(context)

        if result.porter_analysis:
            click.echo("✓ Porter analysis complete")
        else:
            click.echo(f"⚠ Porter analysis failed: {result.porter_error}")

        if result.systems_analysis:
            click.echo("✓ Systems Dynamics analysis complete")
        else:
            click.echo(f"⚠ Systems Dynamics analysis failed: {result.systems_error}")

    except Exception as e:
        click.echo(f"Error during analysis: {e}", err=True)
        sys.exit(1)

    # Generate report
    click.echo("\n📝 Generating report...")
    report_generator = ReportGenerator()
    report = report_generator.generate_report(result)

    # Save report
    report_path = report_generator.save_report(report, output)
    click.echo(f"✓ Report saved to: {report_path}")

    # Persist analysis
    persistence = PersistenceLayer()
    analysis_path = persistence.save_analysis(result)
    click.echo(f"✓ Analysis data saved to: {analysis_path}")

    # Summary
    click.echo(f"\n📊 Analysis Summary:")
    click.echo(f"   ID: {result.id}")
    click.echo(
        f"   Porter Analysis: {'✓ Complete' if result.porter_analysis else '✗ Failed'}"
    )
    click.echo(
        f"   Systems Analysis: {'✓ Complete' if result.systems_analysis else '✗ Failed'}"
    )
    click.echo(f"\n📁 Output Files:")
    click.echo(f"   Report: {report_path}")
    click.echo(f"   Data: {analysis_path}")


@cli.command()
def list():
    """List all stored analyses"""
    persistence = PersistenceLayer()
    analyses = persistence.list_analyses()

    if not analyses:
        click.echo("No analyses found in storage.")
        return

    click.echo(f"Found {len(analyses)} analysis(es):\n")
    for analysis_id in analyses:
        click.echo(f"  - {analysis_id}")


@cli.command()
@click.argument("analysis_id")
def show(analysis_id):
    """Show details of a specific analysis"""
    persistence = PersistenceLayer()
    result = persistence.load_analysis(analysis_id)

    if not result:
        click.echo(f"Analysis not found: {analysis_id}", err=True)
        sys.exit(1)

    click.echo(f"Analysis ID: {result.id}")
    click.echo(f"Created: {result.created_at}")
    click.echo(f"Source: {result.problem_context.source_type}")
    click.echo(f"\nPorter Analysis: {'✓' if result.porter_analysis else '✗'}")
    click.echo(f"Systems Analysis: {'✓' if result.systems_analysis else '✗'}")


def main():
    """Entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()
