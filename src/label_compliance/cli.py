"""
Label Compliance CLI
=====================
Command-line interface for the label compliance system.

Commands:
    ingest   — Build / rebuild the ISO knowledge base
    check    — Check one or more label PDFs for compliance
    report   — Generate a cross-label summary report
    run      — Full pipeline: ingest → check → report
"""

from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table

from label_compliance.config import get_settings
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)
console = Console()


# ═══════════════════════════════════════════════════════
#  Root group
# ═══════════════════════════════════════════════════════
@click.group()
@click.version_option(version="0.1.0", prog_name="label-compliance")
def main():
    """Medical-device label compliance checker (ISO 14607 & more)."""
    pass


# ═══════════════════════════════════════════════════════
#  INGEST — build the knowledge base
# ═══════════════════════════════════════════════════════
@main.command()
@click.option(
    "--standards-dir", "-s",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directory with ISO standard PDFs. Default: config value.",
)
@click.option("--rebuild", is_flag=True, help="Clear existing KB and rebuild from scratch.")
def ingest(standards_dir: Path | None, rebuild: bool):
    """Ingest ISO standard PDFs into the knowledge base."""
    from label_compliance.knowledge_base.ingester import ingest_all_standards, ingest_standard
    from label_compliance.knowledge_base.store import KnowledgeStore

    settings = get_settings()
    settings.ensure_dirs()

    std_dir = standards_dir or Path(settings.paths.standards_dir)
    if not std_dir.exists():
        console.print(f"[red]Standards directory not found:[/red] {std_dir}")
        console.print("[dim]Place ISO PDF files there and rerun.[/dim]")
        sys.exit(1)

    pdfs = list(std_dir.glob("*.pdf"))
    if not pdfs:
        console.print(f"[yellow]No PDF files found in {std_dir}[/yellow]")
        sys.exit(1)

    console.print(f"\n[bold]Ingesting {len(pdfs)} standard(s)…[/bold]\n")

    # Step 1: Parse PDFs → structured JSON
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), transient=True) as progress:
        task = progress.add_task("Parsing standards…", total=len(pdfs))
        kb_files = []
        for pdf in sorted(pdfs):
            kb = ingest_standard(pdf)
            kb_files.append(kb)
            progress.advance(task)

    # Show KB stats
    for kb in kb_files:
        kb_path = Path(settings.paths.knowledge_base_dir) / f"{kb['iso_id']}.json"
        n_sec = len(kb.get("sections", []))
        n_req = len(kb.get("requirements", []))
        n_kw = len(kb.get("keywords", []))
        console.print(
            f"  [green]✓[/green] {kb['iso_id']}: "
            f"{n_sec} sections, {n_req} requirements, {n_kw} keywords → {kb_path.name}"
        )

    # Step 2: Index into ChromaDB
    store = KnowledgeStore()
    if rebuild:
        store.reset()
        console.print("[dim]  KB reset.[/dim]")

    total_indexed = 0
    for kb in kb_files:
        kb_path = Path(settings.paths.knowledge_base_dir) / f"{kb['iso_id']}.json"
        n = store.index_knowledge_base(kb_path)
        total_indexed += n

    console.print(f"\n[bold green]Done.[/bold green] {total_indexed} chunks indexed in ChromaDB.\n")


# ═══════════════════════════════════════════════════════
#  CHECK — check labels for compliance
# ═══════════════════════════════════════════════════════
@main.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--labels-dir", "-d",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directory of label PDFs to check (alternative to passing file paths).",
)
@click.option("--semantic/--no-semantic", default=False, help="Enable semantic KB matching.")
@click.option("--ai/--no-ai", default=True, help="Enable AI text analysis (default: on).")
@click.option("--ai-vision/--no-ai-vision", default=False, help="Enable AI vision analysis (slow on CPU).")
@click.option("--redline/--no-redline", default=True, help="Generate redlined output.")
@click.option(
    "--format", "-f",
    type=click.Choice(["pdf", "png", "both"], case_sensitive=False),
    default="both",
    help="Redline output format.",
)
@click.option("--workers", "-w", type=int, default=None, help="Parallel workers. Default: config.")
def check(
    paths: tuple[Path, ...],
    labels_dir: Path | None,
    semantic: bool,
    ai: bool,
    ai_vision: bool,
    redline: bool,
    format: str,
    workers: int | None,
):
    """Check label PDFs for ISO compliance and generate redlines."""
    from label_compliance.compliance.checker import check_label, LabelResult
    from label_compliance.redline.annotator import annotate_label
    from label_compliance.redline.pdf_redliner import generate_redlined_pdf
    from label_compliance.redline.report import generate_report

    settings = get_settings()
    settings.ensure_dirs()

    # Collect PDF files
    pdf_files: list[Path] = []
    for p in paths:
        p = Path(p)
        if p.is_file() and p.suffix.lower() == ".pdf":
            pdf_files.append(p)
        elif p.is_dir():
            pdf_files.extend(sorted(p.glob("**/*.pdf")))

    if labels_dir:
        pdf_files.extend(sorted(labels_dir.glob("**/*.pdf")))

    if not pdf_files:
        # Fall back to configured labels_dir
        configured = Path(settings.paths.labels_dir)
        if configured.exists():
            pdf_files = sorted(configured.glob("**/*.pdf"))

    if not pdf_files:
        console.print("[red]No label PDFs found.[/red] Pass file paths or use --labels-dir.")
        sys.exit(1)

    # Filter out sample redline PDFs — only check clean versions
    # Redline files (e.g. *_Redline.pdf) are reference samples, not input
    clean_files = [f for f in pdf_files if "_Redline" not in f.stem and "_redline" not in f.stem]
    redline_files = [f for f in pdf_files if f not in clean_files]
    if redline_files:
        console.print(
            f"[dim]  Skipping {len(redline_files)} sample redline(s) "
            f"(only checking clean labels)[/dim]"
        )
    pdf_files = clean_files

    if not pdf_files:
        console.print("[yellow]No clean label PDFs found (all are redline samples).[/yellow]")
        sys.exit(1)

    # Deduplicate
    pdf_files = list(dict.fromkeys(pdf_files))
    console.print(f"\n[bold]Checking {len(pdf_files)} label(s)…[/bold]\n")

    max_workers = workers or settings.processing.max_workers
    results: list[LabelResult] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("Processing labels…", total=len(pdf_files))

        for pdf in pdf_files:
            progress.update(task, description=f"Checking {pdf.name}…")
            try:
                result = check_label(pdf, semantic=semantic, use_ai=ai, ai_vision=ai_vision)
                results.append(result)

                # Generate outputs
                if redline:
                    if format in ("png", "both"):
                        annotate_label(result)
                    if format in ("pdf", "both"):
                        generate_redlined_pdf(result)
                    generate_report(result)

            except Exception as e:
                logger.error("Failed to process %s: %s", pdf.name, e, exc_info=True)
                console.print(f"  [red]✗[/red] {pdf.name}: {e}")

            progress.advance(task)

    # Show summary table
    _print_results_table(results)

    ai_note = " [bold magenta](with AI verification)[/bold magenta]" if ai else ""
    vision_note = " + [bold magenta]vision[/bold magenta]" if ai_vision else ""
    console.print(
        f"\n[bold green]Done.{ai_note}{vision_note}[/bold green] "
        f"Checked {len(results)}/{len(pdf_files)} label(s). "
        f"See [blue]{settings.paths.output_dir}/[/blue].\n"
    )


def _print_results_table(results):
    """Display a rich summary table of results."""
    from label_compliance.compliance.checker import LabelResult

    table = Table(title="Compliance Summary", show_lines=True)
    table.add_column("Label", style="bold")
    table.add_column("Profile", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Score", justify="right")
    table.add_column("Pass", justify="right", style="green")
    table.add_column("Partial", justify="right", style="yellow")
    table.add_column("Fail", justify="right", style="red")
    table.add_column("Not Checked", justify="right", style="dim")

    for r in results:
        if r.score is None:
            table.add_row(r.label_name, getattr(r, "profile", "?"), "[dim]ERROR[/dim]", "-", "-", "-", "-", "-")
            continue

        status_color = {
            "COMPLIANT": "green",
            "PARTIAL": "yellow",
            "NON-COMPLIANT": "red",
        }.get(r.score.status, "dim")

        table.add_row(
            r.label_name,
            getattr(r, "profile", "default"),
            f"[{status_color}]{r.score.status}[/{status_color}]",
            f"{r.score.score_pct:.0f}%",
            str(r.score.passed),
            str(r.score.partial),
            str(r.score.failed),
            str(r.score.total_rules - r.score.passed - r.score.partial - r.score.failed),
        )

    console.print()
    console.print(table)


# ═══════════════════════════════════════════════════════
#  REPORT — generate cross-label summary
# ═══════════════════════════════════════════════════════
@main.command()
@click.option(
    "--output-dir", "-o",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Output directory for the summary report.",
)
def report(output_dir: Path | None):
    """Generate a cross-label summary report from existing check results."""
    from label_compliance.redline.report import generate_summary_report

    settings = get_settings()
    out = output_dir or Path(settings.paths.report_dir)
    reports_dir = Path(settings.paths.report_dir)

    json_files = list(reports_dir.glob("*.json"))
    if not json_files:
        console.print(f"[yellow]No JSON report files found in {reports_dir}[/yellow]")
        console.print("[dim]Run 'label-compliance check' first.[/dim]")
        sys.exit(1)

    console.print(f"\n[bold]Generating summary from {len(json_files)} report(s)…[/bold]\n")
    summary_path = generate_summary_report(json_files, out)
    console.print(f"[bold green]Summary report:[/bold green] {summary_path}\n")


# ═══════════════════════════════════════════════════════
#  RUN — full pipeline: ingest → check → report
# ═══════════════════════════════════════════════════════
@main.command()
@click.option("--rebuild", is_flag=True, help="Rebuild the knowledge base from scratch.")
@click.option("--semantic/--no-semantic", default=False, help="Enable semantic matching.")
@click.option("--ai/--no-ai", default=True, help="Enable AI text analysis (default: on).")
@click.option("--ai-vision/--no-ai-vision", default=False, help="Enable AI vision analysis (slow on CPU).")
@click.option(
    "--format", "-f",
    type=click.Choice(["pdf", "png", "both"], case_sensitive=False),
    default="both",
    help="Redline output format.",
)
def run(rebuild: bool, semantic: bool, ai: bool, ai_vision: bool, format: str):
    """Run the full pipeline: ingest → check → report."""
    settings = get_settings()
    settings.ensure_dirs()

    t0 = time.time()
    console.print("\n[bold cyan]═══ Label Compliance Pipeline ═══[/bold cyan]\n")

    # Step 1: Ingest
    console.rule("[bold]Step 1 — Ingest Standards[/bold]")
    from label_compliance.knowledge_base.ingester import ingest_all_standards
    from label_compliance.knowledge_base.store import KnowledgeStore

    std_dir = Path(settings.paths.standards_dir)
    if std_dir.exists() and list(std_dir.glob("*.pdf")):
        kbs = ingest_all_standards()
        store = KnowledgeStore()
        if rebuild:
            store.reset()

        total = 0
        for kb in kbs:
            kb_path = Path(settings.paths.knowledge_base_dir) / f"{kb['iso_id']}.json"
            total += store.index_knowledge_base(kb_path)
        console.print(f"  [green]✓[/green] Indexed {total} chunks.\n")
    else:
        console.print(f"  [yellow]No standards in {std_dir}, skipping ingest.[/yellow]\n")

    # Step 2: Check labels
    console.rule("[bold]Step 2 — Check Labels[/bold]")
    from label_compliance.compliance.checker import check_label
    from label_compliance.redline.annotator import annotate_label
    from label_compliance.redline.pdf_redliner import generate_redlined_pdf
    from label_compliance.redline.report import generate_report, generate_summary_report

    labels_dir = Path(settings.paths.labels_dir)
    if not labels_dir.exists():
        console.print(f"  [red]Labels directory not found:[/red] {labels_dir}")
        sys.exit(1)

    pdf_files = sorted(labels_dir.glob("**/*.pdf"))
    if not pdf_files:
        console.print(f"  [yellow]No label PDFs in {labels_dir}.[/yellow]")
        sys.exit(1)

    # Filter out sample redline PDFs — only check clean versions
    pdf_files = [f for f in pdf_files if "_Redline" not in f.stem and "_redline" not in f.stem]
    if not pdf_files:
        console.print("[yellow]No clean label PDFs found.[/yellow]")
        sys.exit(1)
    console.print(f"  Found {len(pdf_files)} clean label(s) to check.\n")

    results = []
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"),
        BarColumn(), TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("", total=len(pdf_files))
        for pdf in pdf_files:
            progress.update(task, description=f"Checking {pdf.name}…")
            try:
                result = check_label(pdf, semantic=semantic, use_ai=ai, ai_vision=ai_vision)
                results.append(result)
                if format in ("png", "both"):
                    annotate_label(result)
                if format in ("pdf", "both"):
                    generate_redlined_pdf(result)
                generate_report(result)
            except Exception as e:
                logger.error("Failed: %s — %s", pdf.name, e, exc_info=True)
                console.print(f"  [red]✗[/red] {pdf.name}: {e}")
            progress.advance(task)

    _print_results_table(results)

    # Step 3: Summary report
    console.rule("[bold]Step 3 — Summary Report[/bold]")
    report_dir = Path(settings.paths.report_dir)
    json_files = list(report_dir.glob("*.json"))
    if json_files:
        summary = generate_summary_report(json_files, report_dir)
        console.print(f"  [green]✓[/green] Summary: {summary}\n")

    elapsed = time.time() - t0
    console.print(
        f"\n[bold cyan]Pipeline complete in {elapsed:.1f}s[/bold cyan] "
        f"— {len(results)} labels processed.\n"
    )


# ═══════════════════════════════════════════════════════
#  VALIDATE — compare our output vs sample redlines
# ═══════════════════════════════════════════════════════
@main.command()
@click.option(
    "--labels-dir", "-d",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directory containing clean + sample redline PDFs.",
)
def validate(labels_dir: Path | None):
    """Compare our generated redlines against sample (human) redlines.

    Pairs clean labels with their *_Redline.pdf counterparts,
    then measures text diff overlap and visual similarity.
    """
    from label_compliance.redline.validator import (
        find_sample_redline,
        validate_against_sample,
        format_validation_report,
    )
    from label_compliance.utils.helpers import safe_filename

    settings = get_settings()
    settings.ensure_dirs()

    ldir = labels_dir or Path(settings.paths.labels_dir)
    all_pdfs = sorted(ldir.glob("**/*.pdf"))

    # Find clean/redline pairs
    clean_pdfs = [f for f in all_pdfs if "_Redline" not in f.stem and "_redline" not in f.stem]
    pairs: list[tuple[Path, Path]] = []
    for clean in clean_pdfs:
        sample = find_sample_redline(clean)
        if sample:
            pairs.append((clean, sample))

    if not pairs:
        console.print("[yellow]No clean+redline pairs found.[/yellow]")
        console.print("[dim]Expected naming: LABEL.pdf + LABEL_Redline.pdf[/dim]")
        sys.exit(1)

    console.print(f"\n[bold]Validating {len(pairs)} label pair(s)…[/bold]\n")
    for clean, sample in pairs:
        console.print(f"  Clean:   {clean.name}")
        console.print(f"  Sample:  {sample.name}")

    results = []
    report_dir = Path(settings.paths.report_dir)

    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"),
        BarColumn(), TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("Validating…", total=len(pairs))
        for clean, sample in pairs:
            progress.update(task, description=f"Validating {clean.stem}…")

            # Find our JSON report for this label
            safe_name = safe_filename(clean.stem)
            our_json = report_dir / f"report-{safe_name}.json"

            try:
                vr = validate_against_sample(clean, sample, our_json)
                results.append(vr)
            except Exception as e:
                logger.error("Validation failed for %s: %s", clean.name, e, exc_info=True)
                console.print(f"  [red]✗[/red] {clean.name}: {e}")

            progress.advance(task)

    # Print results table
    table = Table(title="Validation: Our Output vs Sample Redlines", show_lines=True)
    table.add_column("Label", style="bold")
    table.add_column("Sample Changes", justify="right")
    table.add_column("Our Gaps Found", justify="right", style="green")
    table.add_column("Our Gaps Missed", justify="right", style="red")
    table.add_column("Precision", justify="right")
    table.add_column("Recall", justify="right")
    table.add_column("Visual Sim", justify="right")

    for r in results:
        table.add_row(
            r.label_name,
            str(len(r.sample_changes)),
            str(r.overlap_count),
            str(len(r.our_gaps_missed)),
            f"{r.precision:.0%}",
            f"{r.recall:.0%}",
            f"{r.avg_similarity:.1%}",
        )

    console.print()
    console.print(table)

    # Write detailed report
    report_md = format_validation_report(results)
    out_path = report_dir / "validation-report.md"
    out_path.write_text(report_md, encoding="utf-8")
    console.print(f"\n[bold green]Detailed report:[/bold green] {out_path}\n")


if __name__ == "__main__":
    main()
