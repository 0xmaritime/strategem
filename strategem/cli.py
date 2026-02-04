"""Strategem CLI - Explicit Version Selection

CLI with explicit --v1/--v2 flags.
No magic, no auto-detection, no implicit version selection.
"""

import sys
import click
from pathlib import Path


def run_v1_analysis(
    text=None,
    file=None,
    title=None,
    problem_statement=None,
    output=None,
    decision_question=None,
    decision_type=None,
    options=None,
):
    """Run V1 analysis"""
    from strategem.v1 import (
        ContextIngestionModule,
        ContextIngestionError,
        AnalysisOrchestrator,
        ReportGenerator,
        PersistenceLayer,
        DecisionFocus,
        DecisionType,
    )

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
        options_list = [opt.strip() for opt in options.split(",")]
        decision_focus = DecisionFocus(
            decision_question=decision_question,
            decision_type=DecisionType(decision_type or "explore"),
            options=options_list,
        )
        click.echo(f"🎯 Decision Focus: {decision_question}")
        click.echo(f"   Options: {', '.join(options_list)}")
    elif decision_question or options:
        click.echo(
            "⚠️  Note: Decision focus requires both --decision-question and --options",
            err=True,
        )
        click.echo("   If not provided, system will attempt to infer from your input.")

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
                file_path=Path(file),
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
    click.echo(f"\n📊 Analysis Summary (V1):")
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

    print_v1_disclaimer()


def run_v2_analysis(
    text=None,
    file=None,
    title=None,
    problem_statement=None,
    output=None,
    decision_question=None,
    decision_type=None,
    options=None,
):
    """Run V2 analysis (DEVELOPMENT STATUS)"""
    click.echo("⚠️  V2 is in active development.", err=True)
    click.echo("   Framework execution is not yet reliable.", err=True)
    click.echo("   Use --v1 for production analysis.", err=True)
    click.echo()
    click.echo("For V2 development testing:", err=True)
    click.echo("  1. Configure OPENROUTER_API_KEY", err=True)
    click.echo("  2. Run: strategem analyze --v2 --text 'context...' \\")
    click.echo("       --decision-question 'Your question?' \\")
    click.echo("       --options 'Option A,Option B'", err=True)
    click.echo()
    sys.exit(1)


def print_v2_disclaimer():
    """Print V2 disclaimer"""
    click.echo("\n" + "=" * 60)
    click.echo("⚠️  IMPORTANT DISCLAIMER (V2)")
    click.echo("=" * 60)
    click.echo("This is a reasoned artifact, NOT a recommendation.")
    click.echo("V2 provides:")
    click.echo("  - Option-aware analysis")
    click.echo("  - Cross-framework tension mapping")
    click.echo("  - Explicit sensitivity triggers")
    click.echo("  - Assumption fragility detection")
    click.echo()
    click.echo("This system does NOT:")
    click.echo("  - Recommend, rank, or score options")
    click.echo("  - Aggregate or reconcile framework tensions")
    click.echo("  - Optimize objectives or make decisions")
    click.echo("  - Transfer learning from past cases")
    click.echo()
    click.echo("The Decision Owner retains full responsibility for all judgments.")
    click.echo("=" * 60)


def print_v1_disclaimer():
    """Print V1 disclaimer"""
    click.echo("\n" + "=" * 60)
    click.echo("⚠️  IMPORTANT DISCLAIMER")
    click.echo("=" * 60)
    click.echo("This is a reasoned artifact, NOT a recommendation.")
    click.echo("This system does NOT output decisions, rank options,")
    click.echo("optimize objectives, or make recommendations.")
    click.echo("The Decision Owner retains full responsibility.")
    click.echo("=" * 60)


@click.group()
def cli():
    """
    Strategem - Versioned Decision Support System

    A reasoning scaffold for analyzing target systems and operating environments.

    Version selection is REQUIRED (--v1 or --v2).

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
    help="Clear statement of problem being analyzed",
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
@click.option(
    "--v1",
    "use_v1",
    flag_value="v1",
    help="Use V1 for analysis",
)
@click.option(
    "--v2",
    "use_v2",
    flag_value="v2",
    help="Use V2 for analysis",
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
    use_v1,
    use_v2,
):
    """
    Run analytical frameworks on Problem Context Materials.

    Version selection is REQUIRED: use --v1 or --v2.

    This produces a reasoned artifact, not a recommendation.
    Framework disagreement is a valid and expected outcome.
    """

    # Validate version selection
    if not use_v1 and not use_v2:
        click.echo("Error: Please specify --v1 or --v2", err=True)
        click.echo("   Example: strategem analyze --file context.txt --v1", err=True)
        sys.exit(1)

    if use_v1 and use_v2:
        click.echo("Error: Cannot use both --v1 and --v2", err=True)
        sys.exit(1)

    # Run analysis with selected version
    if use_v1:
        run_v1_analysis(
            text=text,
            file=file,
            title=title,
            problem_statement=problem_statement,
            output=output,
            decision_question=decision_question,
            decision_type=decision_type,
            options=options,
        )
    else:  # use_v2
        run_v2_analysis(
            text=text,
            file=file,
            title=title,
            problem_statement=problem_statement,
            output=output,
            decision_question=decision_question,
            decision_type=decision_type,
            options=options,
        )


@cli.command()
@click.option(
    "--v1",
    "use_v1",
    flag_value="v1",
    help="List V1 analyses",
)
@click.option(
    "--v2",
    "use_v2",
    flag_value="v2",
    help="List V2 analyses",
)
def list(use_v1, use_v2):
    """List all stored analyses"""
    if not use_v1 and not use_v2:
        click.echo("Error: Please specify --v1 or --v2", err=True)
        click.echo("   Example: strategem list --v1", err=True)
        sys.exit(1)

    if use_v1:
        from strategem.v1 import PersistenceLayer

        persistence = PersistenceLayer()
        analyses = persistence.list_analyses()

        if not analyses:
            click.echo("No V1 analyses found in storage.")
            return

        click.echo(f"Found {len(analyses)} V1 analysis(es):\n")
        for analysis_id in analyses:
            result = persistence.load_analysis(analysis_id)
            if result:
                title = (
                    result.problem_context.title
                    if result.problem_context.title
                    else analysis_id[:8]
                )
                click.echo(f"  - {analysis_id} | {title}")

    else:  # use_v2
        from strategem.v2 import V2PersistenceLayer

        persistence = V2PersistenceLayer()
        analyses = persistence.list_analyses()

        if not analyses:
            click.echo("No V2 analyses found in storage.")
            return

        click.echo(f"Found {len(analyses)} V2 analysis(es):\n")
        for analysis_id in analyses:
            result = persistence.load_analysis(analysis_id)
            if result:
                click.echo(f"  - {analysis_id} | {result.decision.decision_question}")


@cli.command()
@click.argument("analysis_id")
@click.option(
    "--v1",
    "use_v1",
    flag_value="v1",
    help="Show V1 analysis",
)
@click.option(
    "--v2",
    "use_v2",
    flag_value="v2",
    help="Show V2 analysis",
)
def show(analysis_id, use_v1, use_v2):
    """Show details of a specific analysis"""
    if not use_v1 and not use_v2:
        click.echo("Error: Please specify --v1 or --v2", err=True)
        click.echo("   Example: strategem show <id> --v1", err=True)
        sys.exit(1)

    if use_v1:
        from strategem.v1 import PersistenceLayer

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
                f"   Overall: {result.porter_analysis.shared_observations[:100] if result.porter_analysis.shared_observations else 'N/A'}..."
            )

        if result.systems_analysis:
            click.echo(f"\nTarget System Analysis (Systems Dynamics):")
            click.echo(
                f"   System Overview: {result.systems_analysis.system_overview[:100]}..."
            )

    else:  # use_v2
        from strategem.v2 import V2PersistenceLayer

        persistence = V2PersistenceLayer()
        result = persistence.load_analysis(analysis_id)

        if not result:
            click.echo(f"V2 Analysis not found: {analysis_id}", err=True)
            sys.exit(1)

        click.echo(f"V2 Analysis ID: {result.analysis_id}")
        click.echo(f"Created: {result.created_at}")
        click.echo(f"Decision Question: {result.decision.decision_question}")
        click.echo(f"Decision Type: {result.decision.decision_type.value}")
        click.echo(f"Options Analyzed: {', '.join(result.options_analyzed)}")

        click.echo(f"\nFramework Results:")
        for fw_result in result.framework_results:
            status = "✓" if fw_result.success else "✗"
            click.echo(
                f"   {status} {fw_result.framework_name} ({len(fw_result.claims)} claims)"
            )

        if result.tension_map:
            click.echo(f"\nTension Mapping:")
            click.echo(f"   Summary: {result.tension_map.summary}")
            for ft in result.tension_map.framework_tensions:
                click.echo(
                    f"   - {ft.framework_1} vs {ft.framework_2}: {ft.tension_type.value}"
                )

        click.echo(
            f"\nSensitivity Triggers: {len(result.sensitivity_triggers)} identified"
        )
        for trigger in result.sensitivity_triggers[:5]:
            click.echo(f"   - {trigger.trigger_description[:80]}")


@cli.command()
@click.option(
    "--v1",
    "use_v1",
    flag_value="v1",
    help="List V1 frameworks",
)
@click.option(
    "--v2",
    "use_v2",
    flag_value="v2",
    help="List V2 frameworks",
)
def frameworks(use_v1, use_v2):
    """List available analytical frameworks"""
    if not use_v1 and not use_v2:
        click.echo("Error: Please specify --v1 or --v2", err=True)
        click.echo("   Example: strategem frameworks --v1", err=True)
        sys.exit(1)

    if use_v1:
        from strategem.v1 import AnalysisOrchestrator

        orchestrator = AnalysisOrchestrator()
        frameworks = orchestrator.list_available_frameworks()

        click.echo("V1 Available Analytical Frameworks:\n")
        for fw in frameworks:
            click.echo(f"  📐 {fw.name}")
            click.echo(f"     Analytical Lens: {fw.analytical_lens}")
            click.echo(f"     Description: {fw.description}")
            if fw.input_requirements:
                click.echo(
                    f"     Input Requirements: {', '.join(fw.input_requirements)}"
                )
            click.echo()

    else:  # use_v2
        from strategem.v2 import V2AnalysisOrchestrator

        orchestrator = V2AnalysisOrchestrator()
        frameworks = orchestrator.list_available_frameworks()

        click.echo("V2 Available Analytical Frameworks:\n")
        for fw in frameworks:
            click.echo(f"  📐 {fw.name}")
            click.echo(f"     Analytical Lens: {fw.analytical_lens}")
            click.echo(f"     Description: {fw.description}")
            click.echo(f"     Requires Decision: {fw.requires_decision}")
            click.echo(f"     Requires Options: {fw.requires_options}")
            click.echo(f"     Option-Aware: {fw.produces_option_effects}")
            if fw.input_requirements:
                click.echo(
                    f"     Input Requirements: {', '.join(fw.input_requirements)}"
                )
            click.echo()


def main():
    """Entry point for CLI"""
    cli()


if __name__ == "__main__":
    main()
