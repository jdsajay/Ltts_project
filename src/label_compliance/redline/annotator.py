"""
Image Annotator
================
Draws compliance annotations on label images:
  - Green boxes on compliant elements
  - Red boxes on non-compliant areas
  - Side panel with detailed findings
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from label_compliance.compliance.checker import PageResult, LabelResult
from label_compliance.compliance.matcher import MatchResult
from label_compliance.config import get_settings
from label_compliance.utils.helpers import safe_filename
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

# Try to load system fonts (macOS → Linux → fallback)
_FONT_PATHS = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/SFNSText.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for fp in _FONT_PATHS:
        try:
            return ImageFont.truetype(fp, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def annotate_label(
    label_result: LabelResult,
    output_dir: Path | None = None,
) -> list[Path]:
    """
    Generate annotated redline images for all pages of a label.

    Each page gets:
    - The original label image
    - Green bounding boxes on found elements
    - Red annotation panel showing missing elements
    - Compliance status header

    Returns list of generated image paths.
    """
    settings = get_settings()
    if output_dir is None:
        output_dir = settings.paths.redline_dir

    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = safe_filename(label_result.label_name)
    generated: list[Path] = []

    # Aggregate all matches for the annotation panel
    all_matches = label_result.all_matches or []
    score = label_result.score

    for page in label_result.pages:
        if page.image_path is None or page.ocr is None:
            continue

        out_path = output_dir / f"redline-{safe_name}-page-{page.page_number:02d}.png"
        _annotate_page(page, all_matches, score, out_path, settings)
        generated.append(out_path)
        logger.info("  Annotated: %s", out_path.name)

    return generated


def _annotate_page(
    page: PageResult,
    all_matches: list[MatchResult],
    score,
    output_path: Path,
    settings,
) -> None:
    """Annotate a single page image."""
    img = Image.open(page.image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    font = _load_font(settings.redline.font_size)
    font_small = _load_font(max(settings.redline.font_size - 4, 8))
    font_title = _load_font(settings.redline.font_size + 8)

    color_pass = tuple(settings.redline.color_pass)
    color_fail = tuple(settings.redline.color_fail)
    color_partial = tuple(settings.redline.color_partial)

    # Draw bounding boxes on found elements (from this page's matches)
    for match in page.matches:
        if match.status == "PASS":
            color = color_pass
        elif match.status == "PARTIAL":
            color = color_partial
        else:
            continue  # Don't draw boxes for missing items

        for loc in match.locations:
            x, y, w, h = loc["x"], loc["y"], loc["w"], loc["h"]
            draw.rectangle(
                [x - 3, y - 3, x + w + 3, y + h + 3],
                outline=color,
                width=2,
            )

    # Build annotation panel
    panel_width = settings.redline.panel_width
    panel_height = max(img.height, 900)
    panel = Image.new("RGB", (img.width + panel_width, panel_height), (255, 255, 255))
    panel.paste(img, (0, 0))
    pdraw = ImageDraw.Draw(panel)

    x_panel = img.width + 15
    y = 10

    # Title bar
    status_text = score.status if score else "CHECKING"
    status_color = (
        color_pass if status_text == "COMPLIANT"
        else color_partial if status_text == "PARTIAL"
        else color_fail
    )
    pdraw.text((x_panel, y), "COMPLIANCE REDLINE", fill=color_fail, font=font_title)
    y += 30
    pdraw.text((x_panel, y), f"Status: {status_text}", fill=status_color, font=font)
    y += 22
    if score:
        pdraw.text((x_panel, y), f"Score: {score.score_pct}%", fill=(0, 0, 0), font=font)
        y += 22
        pdraw.text(
            (x_panel, y),
            f"✅ {score.passed}  ⚠️ {score.partial}  ❌ {score.failed}",
            fill=(0, 0, 0), font=font,
        )
        y += 22
    pdraw.line([(x_panel, y), (x_panel + panel_width - 30, y)], fill=(0, 0, 0), width=1)
    y += 12

    # Failed items (red)
    failed = [m for m in all_matches if m.status == "FAIL"]
    if failed:
        pdraw.text((x_panel, y), f"❌ MISSING ({len(failed)}):", fill=color_fail, font=font)
        y += 22
        for m in failed:
            flag = " [NEW 2024]" if m.new_in_2024 else ""
            pdraw.text((x_panel + 5, y), f"• {m.rule_description}{flag}", fill=color_fail, font=font_small)
            y += 16
            pdraw.text((x_panel + 15, y), f"  {m.iso_ref}", fill=(120, 120, 120), font=font_small)
            y += 18

    y += 8
    pdraw.line([(x_panel, y), (x_panel + panel_width - 30, y)], fill=(200, 200, 200), width=1)
    y += 8

    # Partial items (orange)
    partials = [m for m in all_matches if m.status == "PARTIAL"]
    if partials:
        pdraw.text((x_panel, y), f"⚠️ PARTIAL ({len(partials)}):", fill=color_partial, font=font)
        y += 22
        for m in partials:
            pdraw.text((x_panel + 5, y), f"• {m.rule_description}", fill=color_partial, font=font_small)
            y += 16
            evidence = ", ".join(m.evidence[:3])
            pdraw.text((x_panel + 15, y), f"  Found: {evidence}", fill=(120, 120, 120), font=font_small)
            y += 18

    y += 8
    pdraw.line([(x_panel, y), (x_panel + panel_width - 30, y)], fill=(200, 200, 200), width=1)
    y += 8

    # Passed items (green) — compact
    passed = [m for m in all_matches if m.status == "PASS"]
    if passed:
        pdraw.text((x_panel, y), f"✅ COMPLIANT ({len(passed)}):", fill=color_pass, font=font)
        y += 22
        for m in passed:
            evidence = ", ".join(m.evidence[:2])
            line = f"• {m.rule_description}: {evidence}"
            pdraw.text((x_panel + 5, y), line[:70], fill=(0, 100, 0), font=font_small)
            y += 16

    panel.save(str(output_path))


def annotate_comparison(
    clean_result: LabelResult,
    redline_result: LabelResult,
    output_dir: Path | None = None,
) -> list[Path]:
    """
    Generate side-by-side comparison images showing
    what the redline fixed vs what's still missing.
    """
    settings = get_settings()
    if output_dir is None:
        output_dir = settings.paths.redline_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = safe_filename(clean_result.label_name)
    generated: list[Path] = []

    clean_pages = clean_result.pages
    redline_pages = redline_result.pages

    for cp, rp in zip(clean_pages, redline_pages):
        if cp.image_path is None or rp.image_path is None:
            continue

        out_path = output_dir / f"comparison-{safe_name}-page-{cp.page_number:02d}.png"
        _draw_comparison(cp, rp, clean_result, redline_result, out_path)
        generated.append(out_path)

    return generated


def _draw_comparison(
    clean_page: PageResult,
    redline_page: PageResult,
    clean_result: LabelResult,
    redline_result: LabelResult,
    output_path: Path,
) -> None:
    """Draw side-by-side clean vs redline comparison."""
    clean_img = Image.open(clean_page.image_path).convert("RGB")
    redline_img = Image.open(redline_page.image_path).convert("RGB")

    # Scale to same height
    target_h = min(clean_img.height, redline_img.height, 1200)
    clean_img = clean_img.resize(
        (int(clean_img.width * target_h / clean_img.height), target_h),
        Image.LANCZOS,
    )
    redline_img = redline_img.resize(
        (int(redline_img.width * target_h / redline_img.height), target_h),
        Image.LANCZOS,
    )

    gap = 10
    delta_w = 350
    total_w = clean_img.width + redline_img.width + delta_w + gap * 3
    canvas = Image.new("RGB", (total_w, target_h + 40), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    font = _load_font(16)
    font_small = _load_font(12)

    # Headers
    draw.text((gap, 5), "CLEAN (current)", fill=(0, 0, 150), font=font)
    draw.text((gap + clean_img.width + gap, 5), "REDLINE (proposed)", fill=(180, 0, 0), font=font)
    draw.text((gap + clean_img.width + gap + redline_img.width + gap, 5), "DELTA", fill=(0, 0, 0), font=font)

    # Paste images
    canvas.paste(clean_img, (gap, 35))
    canvas.paste(redline_img, (gap + clean_img.width + gap, 35))

    # Delta analysis
    x_d = gap + clean_img.width + gap + redline_img.width + gap
    y = 40

    clean_fail = {m.rule_id for m in (clean_result.all_matches or []) if m.status == "FAIL"}
    redline_fail = {m.rule_id for m in (redline_result.all_matches or []) if m.status == "FAIL"}
    fixed = clean_fail - redline_fail
    still_missing = redline_fail

    if fixed:
        draw.text((x_d, y), "FIXED:", fill=(0, 140, 0), font=font_small)
        y += 16
        for rid in fixed:
            match = next((m for m in clean_result.all_matches if m.rule_id == rid), None)
            if match:
                draw.text((x_d + 5, y), f"+ {match.rule_description}", fill=(0, 120, 0), font=font_small)
                y += 14

    y += 10
    if still_missing:
        draw.text((x_d, y), "STILL MISSING:", fill=(200, 0, 0), font=font_small)
        y += 16
        for rid in still_missing:
            match = next((m for m in redline_result.all_matches if m.rule_id == rid), None)
            if match:
                flag = " *NEW*" if match.new_in_2024 else ""
                draw.text((x_d + 5, y), f"- {match.rule_description}{flag}", fill=(180, 0, 0), font=font_small)
                y += 14

    canvas.save(str(output_path))
