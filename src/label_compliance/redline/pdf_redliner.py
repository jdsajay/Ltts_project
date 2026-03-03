"""
PDF Redliner
==============
Generates redlined PDF files — the original label PDF with
compliance annotations drawn directly on the label artwork.

Annotation style (matches manual redline format):
- Red rectangles (Square annotations) around non-compliant elements
- Red FreeText callouts describing what needs to change
- Red lines connecting callouts to problem areas
- Green rectangles around compliant elements
- Orange rectangles around partial matches
- Compact summary block in a margin area
"""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

from label_compliance.compliance.checker import LabelResult, SectionResult
from label_compliance.compliance.matcher import MatchResult
from label_compliance.config import get_settings
from label_compliance.utils.helpers import safe_filename
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

# Colors matching manual redline style (RGB 0-1 floats)
RED = (0.86, 0.20, 0.15)       # #db3326 — non-compliant
DARK_RED = (0.90, 0.13, 0.22)  # #e52138 — critical callouts
GREEN = (0.0, 0.55, 0.0)      # compliant
ORANGE = (1.0, 0.55, 0.0)     # partial
GRAY = (0.5, 0.5, 0.5)        # reference text
WHITE = (1.0, 1.0, 1.0)


def generate_redlined_pdf(
    label_result: LabelResult,
    output_dir: Path | None = None,
) -> Path | None:
    """
    Create a redlined PDF by annotating directly on the original drawing.

    Draws:
    - Red Square annotations around non-compliant label sections/elements
    - Red FreeText callouts near each issue describing what's wrong
    - Green/orange boxes on compliant/partial elements with locations
    - Compact compliance summary in the bottom-right margin area
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

    dpi = settings.document.render_dpi
    scale = 72.0 / dpi  # OCR coords → PDF coords

    # Process each page
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        pw, ph = page.rect.width, page.rect.height

        # Gather all section results for this page
        page_sections = [
            s for s in label_result.sections
            if s.page_number == page_idx + 1
        ]

        # Get segmentation bboxes for section-level annotations
        section_bboxes = {}
        if label_result.segmentation:
            for sec in label_result.segmentation.sections:
                if sec.page_number == page_idx + 1 and sec.bbox:
                    section_bboxes[sec.name.upper()] = sec.bbox

        # --- 1. Draw RED section-level boxes on non-compliant sections only ---
        _annotate_sections(page, page_sections, section_bboxes)

        # --- 2. Mark FAIL element locations with red highlights ---
        for section in page_sections:
            _annotate_fail_locations(page, section.matches, scale, pw, ph)

        # --- 3. Add callout texts for FAIL and critical PARTIAL findings ---
        _add_callout_annotations(page, page_sections, section_bboxes, pw, ph)

        # --- 4. Add compact summary in margin ---
        _draw_summary_block(page, label_result, pw, ph)

    doc.save(str(out_path))
    doc.close()
    logger.info("Redlined PDF saved: %s", out_path.name)
    return out_path


def _annotate_sections(
    page: fitz.Page,
    sections: list[SectionResult],
    section_bboxes: dict[str, tuple],
) -> None:
    """Draw RED rectangles around non-compliant label sections only.

    Sections scoring >= 80% are left unmarked (clean).
    """
    for section in sections:
        bbox_key = section.section_name.upper()
        bbox = section_bboxes.get(bbox_key)
        if not bbox:
            continue

        x0, y0, x1, y1 = bbox
        rect = fitz.Rect(x0, y0, x1, y1)
        if not rect.is_valid or rect.is_empty:
            continue

        # Only annotate non-compliant and partially-compliant sections
        if section.score and section.score.score_pct >= 80:
            continue  # compliant — no markup needed

        color = RED if (not section.score or section.score.score_pct < 40) else ORANGE

        annot = page.add_rect_annot(rect)
        annot.set_colors(stroke=color)
        annot.set_border(width=2.0)
        annot.set_opacity(0.7)
        annot.set_info(
            content=f"{section.section_name}: {section.score.status if section.score else 'UNKNOWN'}"
                    f" ({section.score.score_pct if section.score else 0}%)",
        )
        annot.update()


def _annotate_fail_locations(
    page: fitz.Page,
    matches: list[MatchResult],
    scale: float,
    pw: float,
    ph: float,
) -> None:
    """Draw red highlights on specific text locations that FAIL.

    Only marks FAIL elements — PARTIAL items are described in callouts.
    PASS items are left clean (no markup).
    """
    for match in matches:
        if match.status != "FAIL":
            continue  # only highlight clear failures

        for loc in match.locations[:3]:  # limit per match
            x, y, w, h = loc["x"], loc["y"], loc["w"], loc["h"]
            rect = fitz.Rect(
                x * scale, y * scale,
                (x + w) * scale, (y + h) * scale,
            )
            if rect.is_valid and rect.width > 2 and rect.x1 <= pw and rect.y1 <= ph:
                annot = page.add_rect_annot(rect)
                annot.set_colors(stroke=RED)
                annot.set_border(width=1.5)
                annot.set_opacity(0.6)
                annot.set_info(content=f"{match.rule_id}: {match.rule_description[:60]}")
                annot.update()


def _add_callout_annotations(
    page: fitz.Page,
    sections: list[SectionResult],
    section_bboxes: dict[str, tuple],
    pw: float,
    ph: float,
) -> None:
    """
    Add red FreeText callout annotations for FAIL and critical PARTIAL findings.

    Positions each callout near the relevant label section on the drawing,
    with connecting lines. Each section gets one consolidated callout.
    """
    # Layout strategy: place callouts near sections, fallback to margin
    used_rects: list[fitz.Rect] = []  # avoid overlaps

    for sec_idx, section in enumerate(sections):
        bbox_key = section.section_name.upper()
        bbox = section_bboxes.get(bbox_key)

        # Gather findings
        fail_matches = [m for m in section.matches if m.status == "FAIL"]
        partial_matches = [
            m for m in section.matches
            if m.status == "PARTIAL" and m.severity == "critical"
        ]

        if not fail_matches and not partial_matches:
            continue

        # Build concise callout text
        text_lines = []
        if fail_matches:
            text_lines.append(f"{section.section_name} — MISSING:")
            for m in fail_matches:
                desc = m.rule_description
                if len(desc) > 70:
                    desc = desc[:67] + "..."
                flag = " [2024]" if m.new_in_2024 else ""
                text_lines.append(f"- {desc}{flag}")
        if partial_matches:
            label = "REVIEW:" if not fail_matches else "ALSO REVIEW:"
            text_lines.append(f"{label}")
            for m in partial_matches[:5]:
                desc = m.rule_description
                if len(desc) > 70:
                    desc = desc[:67] + "..."
                text_lines.append(f"- {desc}")

        callout_text = "\n".join(text_lines)
        line_count = len(text_lines)
        rect_h = max(line_count * 11 + 14, 40)
        rect_w = min(280, pw * 0.2)

        # Position: prefer right of section, fallback to margin columns
        if bbox:
            sx0, sy0, sx1, sy1 = bbox
            # Try right side of section
            callout_x = sx1 + 12
            callout_y = sy0
            # If too far right, try left side
            if callout_x + rect_w > pw - 10:
                callout_x = max(10, sx0 - rect_w - 12)
            # If still off-page, use overlay
            if callout_x < 10:
                callout_x = sx0 + 10
        else:
            # No bbox — distribute in right margin
            callout_x = pw - rect_w - 15
            callout_y = 50 + sec_idx * (rect_h + 20)

        # Avoid overlapping previous callouts
        callout_rect = fitz.Rect(
            callout_x, callout_y,
            callout_x + rect_w, callout_y + rect_h,
        )
        for used in used_rects:
            if callout_rect.intersects(used):
                callout_rect.y0 = used.y1 + 8
                callout_rect.y1 = callout_rect.y0 + rect_h

        # Clamp to page bounds
        if callout_rect.y1 > ph - 10:
            callout_rect.y0 = ph - rect_h - 10
            callout_rect.y1 = ph - 10
        if callout_rect.x1 > pw - 5:
            callout_rect.x0 = pw - rect_w - 5
            callout_rect.x1 = pw - 5

        try:
            annot = page.add_freetext_annot(
                callout_rect,
                callout_text,
                fontsize=7,
                fontname="helv",
                text_color=RED,
                fill_color=WHITE,
            )
            annot.set_opacity(0.95)
            annot.update()

            # Draw red border
            shape = page.new_shape()
            shape.draw_rect(callout_rect)
            shape.finish(color=RED, width=1.5)
            shape.commit()

            used_rects.append(callout_rect)

            # Connect callout to section with a red line
            if bbox:
                # Line from left edge of callout to right edge of section
                line_start = fitz.Point(
                    callout_rect.x0,
                    callout_rect.y0 + rect_h / 2,
                )
                line_end = fitz.Point(sx1, (sy0 + sy1) / 2)
                # Only draw if points are far enough apart
                dx = abs(line_start.x - line_end.x)
                dy = abs(line_start.y - line_end.y)
                if dx > 20 or dy > 20:
                    line_annot = page.add_line_annot(line_start, line_end)
                    line_annot.set_colors(stroke=RED)
                    line_annot.set_border(width=1.0)
                    line_annot.set_opacity(0.5)
                    line_annot.update()

        except Exception as e:
            logger.debug("Could not add callout for %s: %s", section.section_name, e)


def _draw_summary_block(
    page: fitz.Page,
    result: LabelResult,
    pw: float,
    ph: float,
) -> None:
    """
    Draw a compact compliance summary in the bottom-right corner
    of the drawing (near the title block area).
    """
    score = result.score
    if not score:
        return

    # Summary box dimensions and position
    box_w, box_h = 220, 85
    margin = 15
    x0 = pw - box_w - margin
    y0 = ph - box_h - margin
    rect = fitz.Rect(x0, y0, x0 + box_w, y0 + box_h)

    # Background fill
    shape = page.new_shape()
    shape.draw_rect(rect)
    shape.finish(color=RED, fill=WHITE, width=1.5)
    shape.commit()

    # Status color
    if score.score_pct >= 80:
        status_color = GREEN
    elif score.score_pct >= 40:
        status_color = ORANGE
    else:
        status_color = RED

    # Write summary text using shape insertions for color control
    tw = fitz.TextWriter(page.rect)
    font = fitz.Font("helv")
    font_bold = fitz.Font("hebo")

    tw.append((x0 + 8, y0 + 14), "COMPLIANCE CHECK", font=font_bold, fontsize=9)
    tw.append((x0 + 8, y0 + 28), f"Status: {score.status}", font=font_bold, fontsize=8)
    tw.append((x0 + 8, y0 + 40), f"Score: {score.score_pct}%", font=font, fontsize=8)
    tw.append(
        (x0 + 8, y0 + 52),
        f"Pass: {score.passed} | Partial: {score.partial} | Fail: {score.failed}",
        font=font, fontsize=7,
    )
    tw.append(
        (x0 + 8, y0 + 64),
        f"Critical gaps: {score.critical_count} | New 2024: {len(score.new_2024_gaps)}",
        font=font, fontsize=7,
    )
    num_sections = len(result.sections)
    if num_sections > 1:
        tw.append(
            (x0 + 8, y0 + 76),
            f"Sections analyzed: {num_sections}",
            font=font, fontsize=7,
        )

    tw.write_text(page, color=status_color)

