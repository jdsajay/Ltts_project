"""
Report Generator
==================
Generates Markdown and JSON compliance reports.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from label_compliance.compliance.checker import LabelResult
from label_compliance.compliance.scorer import ComplianceScore
from label_compliance.config import get_settings
from label_compliance.utils.helpers import safe_filename
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


def generate_report(
    label_result: LabelResult,
    output_dir: Path | None = None,
) -> tuple[Path, Path]:
    """
    Generate Markdown + JSON compliance reports for a label.

    Returns: (markdown_path, json_path)
    """
    settings = get_settings()
    if output_dir is None:
        output_dir = settings.paths.report_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = safe_filename(label_result.label_name)
    md_path = output_dir / f"report-{safe_name}.md"
    json_path = output_dir / f"report-{safe_name}.json"

    # Markdown report
    md_content = _render_markdown(label_result)
    md_path.write_text(md_content, encoding="utf-8")

    # JSON report
    json_content = _render_json(label_result)
    json_path.write_text(json.dumps(json_content, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info("Reports: %s, %s", md_path.name, json_path.name)
    return md_path, json_path


def _render_markdown(result: LabelResult) -> str:
    """Render a detailed Markdown compliance report."""
    score = result.score
    lines: list[str] = []

    lines.append(f"# Compliance Report: {result.label_name}")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Source:** {result.pdf_path.name}")
    lines.append(f"**Pages:** {len(result.pages)}")
    lines.append("")

    # ── Drawing Metadata ──────────────────────────────
    seg = result.segmentation
    if seg and seg.drawing_metadata:
        dm = seg.drawing_metadata
        lines.append("## Drawing Information")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        if dm.drawing_number:
            lines.append(f"| Drawing Number | {dm.drawing_number} |")
        if dm.revision:
            lines.append(f"| Revision | {dm.revision} |")
        if dm.title:
            lines.append(f"| Title | {dm.title} |")
        if dm.scale:
            lines.append(f"| Scale | {dm.scale} |")
        if dm.drawn_by:
            lines.append(f"| Drawn By | {dm.drawn_by} |")
        if dm.approved_by:
            lines.append(f"| Approved By | {dm.approved_by} |")
        if dm.print_date:
            lines.append(f"| Print Date | {dm.print_date} |")
        if dm.tolerance_standard:
            lines.append(f"| Tolerance Standard | {dm.tolerance_standard} |")
        if dm.material and dm.material != "N/A":
            lines.append(f"| Material | {dm.material} |")
        if dm.sheet_info:
            lines.append(f"| Sheet | {dm.sheet_info} |")
        if dm.plm_reference:
            lines.append(f"| PLM Reference | {dm.plm_reference} |")
        lines.append("")

        # Tolerances
        if dm.tolerances:
            lines.append("**Tolerances:**")
            lines.append("")
            for k, v in dm.tolerances.items():
                lines.append(f"- {k} = {v}")
            lines.append("")

    # ── Variable Definitions ──────────────────────────
    if seg and seg.variable_definitions:
        lines.append("## Variable Field Definitions")
        lines.append("")
        lines.append("> All variable text is displayed as its field name in the artwork.")
        lines.append("")
        lines.append("| Variable | Description |")
        lines.append("|----------|-------------|")
        for var, desc in seg.variable_definitions.items():
            lines.append(f"| {var} | {desc} |")
        lines.append("")

    # ── Character Limits ──────────────────────────────
    if seg and seg.character_limits:
        lines.append("## Character Limits")
        lines.append("")
        lines.append("| Position | Max Characters |")
        lines.append("|----------|----------------|")
        for cl in seg.character_limits:
            lines.append(f"| {cl['position']} | {cl['max_chars']} |")
        lines.append("")

    # ── Configuration Matrix ──────────────────────────
    if seg and seg.configuration_matrix:
        lines.append("## Product Configuration Matrix")
        lines.append("")
        lines.append(f"> {len(seg.configuration_matrix)} product variants defined.")
        lines.append("")
        lines.append("| Item Number | Shelf Life | Volume | Diameter | Height/Proj | GTIN |")
        lines.append("|-------------|------------|--------|----------|-------------|------|")
        for cr in seg.configuration_matrix:
            ht = cr.height or cr.projection or "—"
            lines.append(
                f"| {cr.item_number} | {cr.shelf_life_days or '—'}d | "
                f"{cr.nom_volume or '—'} | {cr.diameter or '—'} | {ht} | "
                f"{cr.gtin or '—'} |"
            )
        lines.append("")

    # ── Revision History ──────────────────────────────
    if seg and seg.revision_history:
        lines.append("## Revision History")
        lines.append("")
        lines.append("| Rev | C.O. | Description | Drawn | Date |")
        lines.append("|-----|------|-------------|-------|------|")
        for r in seg.revision_history:
            lines.append(
                f"| {r.rev} | {r.change_order} | {r.description} | "
                f"{r.drawn_by} | {r.date} |"
            )
        lines.append("")

    # ── Manufacturing Notes ───────────────────────────
    if seg and seg.manufacturing_notes:
        lines.append("## Manufacturing / Inspection Notes")
        lines.append("")
        for note in seg.manufacturing_notes:
            lines.append(f"- {note}")
        lines.append("")

    # ── Barcode Content Specs ─────────────────────────
    if seg and seg.barcode_content_specs:
        lines.append("## Barcode Content Specifications")
        lines.append("")
        lines.append("> 2D barcode data element structure:")
        lines.append("")
        for spec in seg.barcode_content_specs:
            lines.append(f"- `{spec}`")
        lines.append("")

    # Summary table
    if score:
        lines.append("## Summary")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| **Status** | **{score.status}** |")
        lines.append(f"| Score | {score.score_pct}% |")
        lines.append(f"| Rules checked | {score.total_rules} |")
        lines.append(f"| ✅ Passed | {score.passed} |")
        lines.append(f"| ⚠️ Partial | {score.partial} |")
        lines.append(f"| ❌ Failed | {score.failed} |")
        lines.append(f"| Critical gaps | {score.critical_count} |")
        lines.append(f"| New 2024 gaps | {len(score.new_2024_gaps)} |")
        lines.append(f"| 📏 Spec violations | {score.spec_violation_count} |")
        lines.append(f"| Rules with spec failures | {score.rules_with_spec_failures} |")
        lines.append("")

    # ── Per-Section Results ──────────────────────────
    if result.sections:
        lines.append("## Section-by-Section Results")
        lines.append("")
        if result.segmentation:
            lines.append(
                f"> PDF segmented into **{result.segmentation.section_count}** label sections."
            )
            lines.append("")
        lines.append("| # | Section | Type | Page | Score | Pass | Partial | Fail |")
        lines.append("|---|---------|------|------|-------|------|---------|------|")
        for si, sec in enumerate(result.sections, 1):
            s = sec.score
            stat = s.status if s else "—"
            pct = f"{s.score_pct}%" if s else "—"
            ps = s.passed if s else 0
            pt = s.partial if s else 0
            fl = s.failed if s else 0
            lines.append(
                f"| {si} | {sec.section_name} | {sec.section_type} | {sec.page_number} | "
                f"{stat} ({pct}) | {ps} | {pt} | {fl} |"
            )
        lines.append("")

        # Detail per section
        for sec in result.sections:
            s = sec.score
            lines.append(f"### 📄 {sec.section_name}")
            if sec.eart_number:
                lines.append(f"- **EART/Part:** {sec.eart_number}")
            lines.append(f"- **Type:** {sec.section_type}")
            lines.append(f"- **Page:** {sec.page_number}")
            if s:
                lines.append(f"- **Score:** {s.status} ({s.score_pct}%)")
            lines.append("")

            # Variable fields on this section
            if hasattr(sec, "section_text") and sec.section_text:
                # Extract variable fields from section text
                import re as _re
                vars_found = []
                for var in ["LOTNO", "SERNO", "MFGDATE", "EXPDATE", "LPNBR",
                            "REF", "LOT", "SN", "TK01", "TK02", "TK03", "TK04",
                            "TK05", "TK06", "TK07", "TK08", "TK09", "TK10",
                            "TK11", "TK20"]:
                    if _re.search(r"\b" + _re.escape(var) + r"\b", sec.section_text, _re.IGNORECASE):
                        vars_found.append(var)
                if vars_found:
                    lines.append(f"**Variable fields:** {', '.join(vars_found)}")
                    lines.append("")

            # Regulatory symbols detected
            if seg and seg.sections:
                # Find matching segmenter section for regulatory_symbols
                for sseg in seg.sections:
                    if sseg.name == sec.section_name and sseg.page_number == sec.page_number:
                        if sseg.regulatory_symbols:
                            lines.append(f"**Regulatory symbols detected:** {', '.join(sseg.regulatory_symbols)}")
                            lines.append("")
                        if sseg.barcode_specs:
                            lines.append(f"**Barcode content:** `{', '.join(sseg.barcode_specs)}`")
                            lines.append("")
                        if sseg.manufacturing_notes:
                            lines.append(f"**Notes:** {'; '.join(sseg.manufacturing_notes)}")
                            lines.append("")
                        break

            # Section matches table
            if sec.matches:
                lines.append("| Status | Rule | Severity | Evidence |")
                lines.append("|--------|------|----------|----------|")
                for m in sec.matches:
                    icon = "✅" if m.status == "PASS" else "⚠️" if m.status == "PARTIAL" else "❌"
                    ev = ", ".join(m.evidence[:2]) if m.evidence else "—"
                    # strip section prefix from details for cleaner display
                    lines.append(
                        f"| {icon} | {m.rule_description[:60]} | {m.severity} | {ev[:60]} |"
                    )
                lines.append("")

            # Section spec violations
            sec_spec_violations = [
                m for m in sec.matches if m.spec_violations
            ]
            if sec_spec_violations:
                lines.append(f"**Spec violations in {sec.section_name}:**")
                lines.append("")
                for m in sec_spec_violations:
                    for sv in m.spec_violations:
                        lines.append(
                            f"- ⚠️ **{sv['spec_field']}** ({m.rule_id}): "
                            f"Required: {sv['requirement']} → Actual: {sv['actual']}"
                        )
                lines.append("")

            # Section symbol comparison
            sym = sec.symbol_comparison
            if sym and sym.total_required > 0:
                lines.append(
                    f"**Symbols:** {sym.total_found}/{sym.total_required} found, "
                    f"{sym.total_partial} partial, {sym.total_missing} missing "
                    f"({sym.score:.0%})"
                )
                lines.append("")

    # Detailed results table
    lines.append("## Rule-by-Rule Results (Overall)")
    lines.append("")
    lines.append("| # | Status | Rule | ISO Ref | Severity | Evidence |")
    lines.append("|---|--------|------|---------|----------|----------|")

    for i, m in enumerate(result.all_matches or [], 1):
        icon = "✅" if m.status == "PASS" else "⚠️" if m.status == "PARTIAL" else "❌"
        new = " 🆕" if m.new_in_2024 else ""
        evidence = ", ".join(m.evidence[:3]) if m.evidence else "—"
        lines.append(
            f"| {i} | {icon} | {m.rule_description}{new} | {m.iso_ref} | {m.severity} | {evidence} |"
        )

    lines.append("")

    # Gaps detail
    gaps = [m for m in (result.all_matches or []) if m.status in ("FAIL", "PARTIAL")]
    if gaps:
        lines.append("## Compliance Gaps")
        lines.append("")
        for m in gaps:
            icon = "❌" if m.status == "FAIL" else "⚠️"
            new = " **(NEW in 2024)**" if m.new_in_2024 else ""
            lines.append(f"### {icon} {m.rule_description}{new}")
            lines.append(f"- **Rule ID:** {m.rule_id}")
            lines.append(f"- **ISO Reference:** {m.iso_ref}")
            lines.append(f"- **Severity:** {m.severity}")
            lines.append(f"- **Status:** {m.status}")
            if m.evidence:
                lines.append(f"- **Partial evidence:** {', '.join(m.evidence)}")
            if m.spec_violations:
                lines.append(f"- **Spec violations:** {len(m.spec_violations)}")
                for sv in m.spec_violations:
                    lines.append(f"  - ⚠️ **{sv['spec_field']}**: Required: {sv['requirement']} → Actual: {sv['actual']}")
                    if sv.get('location'):
                        lines.append(f"    - Location: {sv['location']}")
            if m.spec_details:
                passed_details = [d for d in m.spec_details if d.startswith("PASS:")]
                if passed_details:
                    lines.append(f"- **Specs passed:** {len(passed_details)}")
            lines.append(f"- **Action:** Review and update label to include this element")
            lines.append("")

    # Spec violations section (all rules including PASS with spec issues)
    rules_with_specs = [m for m in (result.all_matches or []) if m.spec_violations]
    if rules_with_specs:
        lines.append("## 📏 Specification Violations Detail")
        lines.append("")
        lines.append("> These violations indicate that while the text content may be present,")
        lines.append("> the physical attributes (size, font, position, adjacency) do not meet ISO requirements.")
        lines.append("")
        lines.append("| Rule | Spec Field | Required | Actual | Severity | Page |")
        lines.append("|------|-----------|----------|--------|----------|------|")
        for m in rules_with_specs:
            for sv in m.spec_violations:
                lines.append(
                    f"| {m.rule_id} | {sv['spec_field']} | {sv['requirement']} | "
                    f"{sv['actual'][:50]} | {sv['severity']} | {sv.get('page', '—')} |"
                )
        lines.append("")

    # Font analysis
    if result.font_violations:
        lines.append("## Font Size Violations")
        lines.append("")
        lines.append("| Font | Size | Min Required | Text Preview | Page |")
        lines.append("|------|------|-------------|-------------|------|")
        for fv in result.font_violations:
            lines.append(
                f"| {fv['font']} | {fv['size']}pt | {fv['min_required']}pt | {fv['text_preview'][:40]} | {fv['page']} |"
            )
        lines.append("")

    # Symbol Library Comparison
    sym_report = result.symbol_comparison
    if sym_report and sym_report.total_required > 0:
        lines.append("## 🏷️ Symbol Library Comparison")
        lines.append("")
        lines.append(f"> Compared label content against the Symbol Library database "
                      f"({sym_report.total_required} required symbols checked).")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Symbols checked | {sym_report.total_required} |")
        lines.append(f"| ✅ Found | {sym_report.total_found} |")
        lines.append(f"| ⚠️ Partial | {sym_report.total_partial} |")
        lines.append(f"| ❌ Missing | {sym_report.total_missing} |")
        lines.append(f"| Score | {sym_report.score:.0%} |")
        lines.append("")

        # Found symbols
        found_syms = [r for r in sym_report.results if r.status == "FOUND"]
        if found_syms:
            lines.append("### ✅ Found Symbols")
            lines.append("")
            lines.append("| Symbol Name | Classification | Expected Text | Match Method | Score |")
            lines.append("|-------------|---------------|----------------|-------------|-------|")
            for r in found_syms:
                method = []
                if r.found_by_text:
                    method.append("Text")
                if r.found_by_visual:
                    method.append("Visual")
                lines.append(
                    f"| {r.symbol.name[:50]} | {r.symbol.classification} | "
                    f"{r.expected_text[:40]} | {', '.join(method)} | "
                    f"{max(r.text_score, r.visual_score):.0%} |"
                )
            lines.append("")

        # Partial symbols
        partial_syms = [r for r in sym_report.results if r.status == "PARTIAL"]
        if partial_syms:
            lines.append("### ⚠️ Partially Matched Symbols")
            lines.append("")
            lines.append("| Symbol Name | Expected Text | Actual Match | Details |")
            lines.append("|-------------|---------------|-------------|---------|")
            for r in partial_syms:
                lines.append(
                    f"| {r.symbol.name[:50]} | {r.expected_text[:40]} | "
                    f"{r.actual_text[:40]} | {r.details[:60]} |"
                )
            lines.append("")

        # Missing symbols
        missing_syms = [r for r in sym_report.results if r.status == "MISSING"]
        if missing_syms:
            lines.append("### ❌ Missing Symbols")
            lines.append("")
            lines.append("| Symbol Name | Classification | Expected Text | Regulation | Action |")
            lines.append("|-------------|---------------|----------------|-----------|--------|")
            for r in missing_syms:
                regs = r.symbol.regulations[:60] if r.symbol.regulations else "—"
                lines.append(
                    f"| {r.symbol.name[:50]} | {r.symbol.classification} | "
                    f"{r.expected_text[:40]} | {regs} | Add to label |"
                )
            lines.append("")

    # Page details
    lines.append("## Page-by-Page OCR Details")
    lines.append("")
    for page in result.pages:
        lines.append(f"### Page {page.page_number}")
        if page.ocr:
            lines.append(f"- Words detected: {page.ocr.word_count}")
            lines.append(f"- Text length: {len(page.ocr.full_text)} chars")
        if page.barcodes:
            lines.append(f"- Barcodes: {len(page.barcodes)}")
            for bc in page.barcodes:
                lines.append(f"  - {bc.barcode_type}: {bc.data[:50]}")
        if page.zones:
            lines.append(f"- Layout zones: {len(page.zones)}")
        lines.append("")

    return "\n".join(lines)


def _render_json(result: LabelResult) -> dict:
    """Render a structured JSON compliance report."""
    score = result.score

    return {
        "label_name": result.label_name,
        "pdf_file": result.pdf_path.name,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "status": score.status if score else "UNKNOWN",
            "score_pct": score.score_pct if score else 0,
            "total_rules": score.total_rules if score else 0,
            "passed": score.passed if score else 0,
            "partial": score.partial if score else 0,
            "failed": score.failed if score else 0,
            "critical_gaps": score.critical_count if score else 0,
            "new_2024_gaps": len(score.new_2024_gaps) if score else 0,
            "spec_violation_count": score.spec_violation_count if score else 0,
            "rules_with_spec_failures": score.rules_with_spec_failures if score else 0,
        },
        "results": [
            {
                "rule_id": m.rule_id,
                "description": m.rule_description,
                "iso_ref": m.iso_ref,
                "status": m.status,
                "confidence": m.confidence,
                "severity": m.severity,
                "new_in_2024": m.new_in_2024,
                "evidence": m.evidence,
                "method": m.method,
                "specs_passed": m.specs_passed,
                "spec_violations": m.spec_violations,
                "spec_details": m.spec_details,
            }
            for m in (result.all_matches or [])
        ],
        "pages": [
            {
                "page_number": p.page_number,
                "word_count": p.ocr.word_count if p.ocr else 0,
                "barcode_count": len(p.barcodes),
                "zone_count": len(p.zones),
            }
            for p in result.pages
        ],
        "font_violations": result.font_violations,
        "segmentation": {
            "section_count": result.segmentation.section_count if result.segmentation else 0,
            "section_names": result.segmentation.section_names if result.segmentation else [],
            "drawing_metadata": _render_drawing_metadata_json(result.segmentation) if result.segmentation else None,
            "variable_definitions": result.segmentation.variable_definitions if result.segmentation else {},
            "character_limits": result.segmentation.character_limits if result.segmentation else [],
            "revision_history": [
                {"rev": r.rev, "change_order": r.change_order, "description": r.description}
                for r in (result.segmentation.revision_history if result.segmentation else [])
            ],
            "manufacturing_notes": result.segmentation.manufacturing_notes if result.segmentation else [],
            "barcode_content_specs": result.segmentation.barcode_content_specs if result.segmentation else [],
            "configuration_matrix": [
                {
                    "item_number": cr.item_number,
                    "shelf_life_days": cr.shelf_life_days,
                    "nom_volume": cr.nom_volume,
                    "diameter": cr.diameter,
                    "height": cr.height,
                    "projection": cr.projection,
                    "gtin": cr.gtin,
                }
                for cr in (result.segmentation.configuration_matrix if result.segmentation else [])
            ],
        } if result.segmentation else None,
        "sections": [
            {
                "section_name": sec.section_name,
                "section_type": sec.section_type,
                "page_number": sec.page_number,
                "eart_number": sec.eart_number,
                "score": {
                    "status": sec.score.status,
                    "score_pct": sec.score.score_pct,
                    "passed": sec.score.passed,
                    "partial": sec.score.partial,
                    "failed": sec.score.failed,
                } if sec.score else None,
                "match_count": len(sec.matches),
                "spec_violations": sum(
                    len(m.spec_violations) for m in sec.matches if m.spec_violations
                ),
                "symbol_comparison": {
                    "total_required": sec.symbol_comparison.total_required,
                    "total_found": sec.symbol_comparison.total_found,
                    "total_missing": sec.symbol_comparison.total_missing,
                    "score": round(sec.symbol_comparison.score, 4),
                } if sec.symbol_comparison and sec.symbol_comparison.total_required > 0 else None,
            }
            for sec in (result.sections or [])
        ],
        "symbol_library_comparison": _render_symbol_comparison_json(result),
    }


def _render_symbol_comparison_json(result: LabelResult) -> dict | None:
    """Render symbol library comparison as JSON."""
    sym_report = result.symbol_comparison
    if sym_report is None or sym_report.total_required == 0:
        return None

    return {
        "total_required": sym_report.total_required,
        "total_found": sym_report.total_found,
        "total_partial": sym_report.total_partial,
        "total_missing": sym_report.total_missing,
        "score": round(sym_report.score, 4),
        "results": [
            {
                "symbol_name": r.symbol.name,
                "classification": r.symbol.classification,
                "status": r.status,
                "expected_text": r.expected_text,
                "actual_text": r.actual_text,
                "text_score": round(r.text_score, 4),
                "visual_score": round(r.visual_score, 4),
                "found_by_text": r.found_by_text,
                "found_by_visual": r.found_by_visual,
                "text_discrepancy": r.text_discrepancy,
                "details": r.details,
                "regulation": r.symbol.regulations[:200],
            }
            for r in sym_report.results
        ],
    }


def _render_drawing_metadata_json(seg) -> dict | None:
    """Render drawing metadata as JSON."""
    dm = seg.drawing_metadata
    if dm is None:
        return None
    return {
        "drawing_number": dm.drawing_number,
        "revision": dm.revision,
        "title": dm.title,
        "scale": dm.scale,
        "material": dm.material,
        "finish": dm.finish,
        "drawn_by": dm.drawn_by,
        "approved_by": dm.approved_by,
        "print_date": dm.print_date,
        "tolerance_standard": dm.tolerance_standard,
        "tolerances": dm.tolerances,
        "sheet_info": dm.sheet_info,
        "plm_reference": dm.plm_reference,
    }


def generate_summary_report(
    all_results: list[LabelResult],
    output_dir: Path | None = None,
) -> Path:
    """
    Generate a cross-label summary report (gap matrix).
    Shows which labels have which gaps.
    """
    settings = get_settings()
    if output_dir is None:
        output_dir = settings.paths.report_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    out_path = output_dir / "summary-report.md"
    lines = [
        "# Cross-Label Compliance Summary",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Labels checked:** {len(all_results)}",
        "",
        "## Overview",
        "",
        "| Label | Status | Score | Pass | Partial | Fail | Critical |",
        "|-------|--------|-------|------|---------|------|----------|",
    ]

    for r in all_results:
        s = r.score
        if s:
            lines.append(
                f"| {r.label_name[:40]} | {s.status} | {s.score_pct}% | {s.passed} | {s.partial} | {s.failed} | {s.critical_count} |"
            )

    lines.append("")

    # Gap matrix: which rules fail across which labels
    all_rule_ids = set()
    for r in all_results:
        for m in (r.all_matches or []):
            if m.status in ("FAIL", "PARTIAL"):
                all_rule_ids.add(m.rule_id)

    if all_rule_ids:
        lines.append("## Gap Matrix")
        lines.append("")
        header = "| Rule |" + "|".join(r.label_name[:15] for r in all_results) + "|"
        sep = "|------|" + "|".join("---" for _ in all_results) + "|"
        lines.append(header)
        lines.append(sep)

        for rule_id in sorted(all_rule_ids):
            cells = [rule_id[:30]]
            for r in all_results:
                match = next((m for m in (r.all_matches or []) if m.rule_id == rule_id), None)
                if match is None:
                    cells.append("—")
                elif match.status == "PASS":
                    cells.append("✅")
                elif match.status == "PARTIAL":
                    cells.append("⚠️")
                else:
                    cells.append("❌")
            lines.append("| " + " | ".join(cells) + " |")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Summary report: %s", out_path.name)
    return out_path
