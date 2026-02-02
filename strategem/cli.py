"""Strategem Core - Command Line Interface (V1 Compliant)"""

import sys
import click
from pathlib import Path

from strategem.context_ingestion import ContextIngestionModule, ContextIngestionError
from strategem.orchestrator import AnalysisOrchestrator
from strategem.report_generator import ReportGenerator
from strategem.persistence import PersistenceLayer
from strategem.models import DecisionFocus, DecisionType


@click.group()
def cli():
    """
    Strategem Core - Decision Support System

    A reasoning scaffold for analyzing target systems and operating environments.

    ⚠️  This system does NOT:
    - Output decisions
    - Rank options
    - Optimize objectives
    - Make recommendations

    The Decision Owner retains full responsibility for all judgments.
    """
    pass


@cli.command()
@click.option("--text", "-t", help="Problem Context Material as text string")
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="Path to file containing Problem Context Material",
)
@click.option(
    "--title",
    help="Title or identifier for this problem context",
)
@click.option(
    "--problem-statement",
    help="Clear statement of the problem being analyzed",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output path for report (default: auto-generated)",
)
@click.option(
    "--decision-question",
    help="The specific decision question being analyzed (required for decision-bound frameworks)",
)
@click.option(
    "--decision-type",
    type=click.Choice(["explore", "compare", "stress_test"]),
    help="Type of decision: explore, compare, or stress_test",
)
@click.option(
    "--options",
    help="Comma-separated list of options under consideration (e.g., 'Option A,Option B,Option C')",
)
def analyze(
    text,
    file,
    title,
    problem_statement,
    output,
    decision_question,
    decision_type,
    options,
):
    """
    Run analytical frameworks on Problem Context Materials.

    This produces a reasoned artifact, not a recommendation.
    Framework disagreement is a valid and expected outcome.
    """

    # Validate input
    if not text and not file:
        click.echo("Error: Must provide either --text or --file", err=True)
        sys.exit(1)

    if text and file:
        click.echo("Error: Cannot use both --text and --file", err=True)
        sys.exit(1)

    # Build DecisionFocus if provided (V1: Optional hint, not requirement)
    decision_focus = None
    if decision_question and options:
        # V1: Decision focus forms are optional hints
        # System will infer from context if not provided
        options_list = [opt.strip() for opt in options.split(",")]
        decision_focus = DecisionFocus(
            decision_question=decision_question,
            decision_type=DecisionType(decision_type or "explore"),
            options=options_list,
        )
        click.echo(f"🎯 Decision Focus: {decision_question}")
        click.echo(f"   Options: {', '.join(options_list)}")
    elif decision_question or options:
        # V1: If only one part provided, warn but don't block
        click.echo(
            "⚠️  Note: Decision focus requires both --decision-question and --options",
            err=True,
        )
        click.echo(
            "   If not provided, the system will attempt to infer from your input."
        )

    # Ingest context
    ingestion = ContextIngestionModule()
    try:
        if text:
            click.echo("📄 Ingesting Problem Context Material (text)...")
            context = ingestion.ingest_text(
                text=text,
                title=title or "Untitled Analysis",
                problem_statement=problem_statement
                or "Problem context provided for analysis",
                decision_focus=decision_focus,
            )
        else:
            click.echo(f"📄 Ingesting Problem Context Material (file): {file}")
            context = ingestion.ingest_file(
                file_path=file,
                title=title,
                problem_statement=problem_statement,
                decision_focus=decision_focus,
            )

        # Structure content
        context = ingestion.structure_content(context)
        click.echo("✓ Problem Context ingested successfully")

    except ContextIngestionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    # Run analysis
    click.echo("\n🔍 Running analytical frameworks...")
    click.echo("   - Operating Environment Structure (Porter's Five Forces)")
    click.echo("   - Target System Dynamics (Systems Dynamics)")
    click.echo()

    orchestrator = AnalysisOrchestrator()

    try:
        result = orchestrator.run_full_analysis(context)

        # Report framework results
        for fw_result in result.framework_results:
            if fw_result.success:
                click.echo(f"✓ {fw_result.framework_name} analysis complete")
            else:
                click.echo(
                    f"⚠ {fw_result.framework_name} analysis failed: {fw_result.error_message}"
                )

    except Exception as e:
        click.echo(f"Error during analysis: {e}", err=True)
        sys.exit(1)

    # Generate report
    click.echo("\n📝 Generating reasoned artifact...")
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
    click.echo(f"   Title: {result.problem_context.title}")

    # Framework status
    for fw_result in result.framework_results:
        status = "✓ Complete" if fw_result.success else "✗ Failed"
        click.echo(f"   {fw_result.framework_name}: {status}")

    # Key metrics from new report structure
    click.echo(f"\n📋 Report Contents:")
    click.echo(f"   - Context Summary")
    click.echo(
        f"   - Key Analytical Claims: {len(report.key_analytical_claims)} extracted"
    )
    click.echo(f"   - Structural Pressures (Operating Environment)")
    click.echo(f"   - Systemic Risks (Target System)")
    click.echo(
        f"   - Unknowns & Sensitivities: {len(report.unknowns_and_sensitivities)} identified"
    )
    click.echo(f"   - Decision Surface")
    click.echo(f"   - Framework Agreement & Tension")
    click.echo(f"   - System Limitations")

    click.echo(f"\n📁 Output Files:")
    click.echo(f"   Report: {report_path}")
    click.echo(f"   Data: {analysis_path}")

    click.echo("\n" + "=" * 60)
    click.echo("⚠️  IMPORTANT DISCLAIMER")
    click.echo("=" * 60)
    click.echo("This is a reasoned artifact, NOT a recommendation.")
    click.echo("This system does NOT output decisions, rank options,")
    click.echo("optimize objectives, or make recommendations.")
    click.echo("The Decision Owner retains full responsibility.")
    click.echo("=" * 60)


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
        result = persistence.load_analysis(analysis_id)
        if result:
            title = (
                result.problem_context.title
                if result.problem_context.title
                else analysis_id[:8]
            )
            click.echo(f"  - {analysis_id} | {title}")


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
    click.echo(f"Title: {result.problem_context.title}")
    click.echo(f"Problem Statement: {result.problem_context.problem_statement}")

    click.echo(f"\nFramework Results:")
    for fw_result in result.framework_results:
        status = "✓" if fw_result.success else "✗"
        click.echo(f"   {status} {fw_result.framework_name}")

    click.echo(
        f"\nProblem Context Materials: {len(result.problem_context.provided_materials)} provided"
    )

    if result.porter_analysis:
        click.echo(f"\nOperating Environment Analysis (Porter):")
        click.echo(
            f"   Overall: {result.porter_analysis.overall_observations[:100]}..."
        )

    if result.systems_analysis:
        click.echo(f"\nTarget System Analysis (Systems Dynamics):")
        click.echo(
            f"   System Overview: {result.systems_analysis.system_overview[:100]}..."
        )


@cli.command()
def frameworks():
    """List available analytical frameworks"""
    orchestrator = AnalysisOrchestrator()
    frameworks = orchestrator.list_available_frameworks()

    click.echo("Available Analytical Frameworks:\n")
    for fw in frameworks:
        click.echo(f"  📐 {fw.name}")
        click.echo(f"     Analytical Lens: {fw.analytical_lens}")
        click.echo(f"     Description: {fw.description}")
        if fw.input_requirements:
            click.echo(f"     Input Requirements: {', '.join(fw.input_requirements)}")
        click.echo()


def main():
    """Entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()
