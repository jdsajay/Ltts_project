"""
PDF Redliner
==============
Generates redlined PDF files — the original label PDF with
compliance annotations overlaid on each page.
"""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

from label_compliance.compliance.checker import LabelResult
from label_compliance.config import get_settings
from label_compliance.utils.helpers import safe_filename
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


def generate_redlined_pdf(
    label_result: LabelResult,
    output_dir: Path | None = None,
) -> Path | None:
    """
    Create a redlined PDF from the original label PDF.

    Overlays:
    - Red rectangles around non-compliant areas
    - Green rectangles around compliant elements
    - Text annotations in margins with ISO refs
    - Cover page with compliance summary
    """
    settings = get_settings()
    if output_dir is None:
        output_dir = settings.paths.redline_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = safe_filename(label_result.label_name)
    out_path = output_dir / f"redlined-{safe_name}.pdf"

    try:
        doc = fitz.open(str(label_result.pdf_path))
    except Exception:
        logger.exception("Cannot open PDF: %s", label_result.pdf_path)
        return None

    score = label_result.score
    color_pass = (0, 0.7, 0)     # green
    color_fail = (0.86, 0.08, 0.08)   # red
    color_partial = (1, 0.65, 0)  # orange

    # ── Add cover page ────────────────────────────────
    cover = doc.new_page(-1, width=595, height=842)  # A4
    _draw_cover_page(cover, label_result)

    # Move cover to front
    doc.move_page(len(doc) - 1, 0)

    # ── Annotate each original page ───────────────────
    for page_result in label_result.pages:
        page_idx = page_result.page_number  # +1 because we inserted cover at 0
        if page_idx >= len(doc):
            continue

        page = doc[page_idx]
        pw, ph = page.rect.width, page.rect.height

        # Scale factor: OCR coords are at render_dpi, PDF is at 72dpi
        dpi = settings.document.render_dpi
        scale = 72.0 / dpi

        for match in page_result.matches:
            if match.status == "PASS":
                color = color_pass
                for loc in match.locations[:3]:  # limit annotations
                    x, y, w, h = loc["x"], loc["y"], loc["w"], loc["h"]
                    rect = fitz.Rect(x * scale, y * scale, (x + w) * scale, (y + h) * scale)
                    if rect.is_valid and rect.width > 0:
                        annot = page.add_rect_annot(rect)
                        annot.set_colors(stroke=color)
                        annot.set_border(width=1)
                        annot.update()

            elif match.status == "FAIL":
                # Add text annotation in margin
                y_pos = 50 + page_result.matches.index(match) * 30
                if y_pos < ph - 20:
                    flag = " [NEW 2024]" if match.new_in_2024 else ""
                    text = f"MISSING: {match.rule_description}{flag}\nRef: {match.iso_ref}"
                    point = fitz.Point(pw - 150, y_pos)
                    annot = page.add_text_annot(point, text)
                    annot.set_colors(stroke=color_fail)
                    annot.update()

    doc.save(str(out_path))
    doc.close()
    logger.info("Redlined PDF saved: %s", out_path.name)
    return out_path


def _draw_cover_page(page: fitz.Page, result: LabelResult) -> None:
    """Draw a compliance summary cover page."""
    score = result.score
    tw = fitz.TextWriter(page.rect)
    font = fitz.Font("helv")

    # Title
    tw.append((50, 60), "COMPLIANCE REDLINE REPORT", font=font, fontsize=20)
    tw.append((50, 90), f"Label: {result.label_name}", font=font, fontsize=14)

    if score:
        tw.append((50, 120), f"Status: {score.status}", font=font, fontsize=16)
        tw.append((50, 145), f"Score: {score.score_pct}%", font=font, fontsize=14)
        tw.append(
            (50, 170),
            f"Passed: {score.passed}  |  Partial: {score.partial}  |  Failed: {score.failed}",
            font=font, fontsize=12,
        )
        tw.append(
            (50, 195),
            f"Critical gaps: {score.critical_count}  |  New 2024 gaps: {len(score.new_2024_gaps)}",
            font=font, fontsize=12,
        )

        # Gap list
        y = 240
        tw.append((50, y), "COMPLIANCE GAPS:", font=font, fontsize=14)
        y += 25

        for m in (score.critical_gaps or []):
            flag = " [NEW 2024]" if m.new_in_2024 else ""
            line = f"• [{m.severity.upper()}] {m.rule_description}{flag}"
            tw.append((60, y), line[:80], font=font, fontsize=10)
            y += 15
            tw.append((70, y), f"Ref: {m.iso_ref}", font=font, fontsize=9)
            y += 18
            if y > 780:
                break

    tw.write_text(page)
