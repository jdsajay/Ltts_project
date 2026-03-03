"""
AI-Powered Redline Generator  (v2 — coordinate-anchored)
==========================================================
Uses GPT-4o vision to analyze label images and produce specific
redline annotations anchored to REAL element positions.

Approach:
1. Extract every text block + image from the PDF with exact coordinates
2. Send the list of elements WITH coordinates + the rendered image to GPT-4o
3. GPT-4o references element IDs (not guessed percentages)
4. Annotations are placed at the ACTUAL element positions

This eliminates the "random box placement" problem.
"""

from __future__ import annotations

import base64
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF
import yaml

from label_compliance.config import get_settings
from label_compliance.document.symbol_library_db import get_symbol_library, SymbolEntry
from label_compliance.knowledge_base.ai_ingester import get_ai_iso_knowledge, get_labelling_requirements_text
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

# ── Redline annotation colors ──────────────────────
RED = (0.86, 0.20, 0.15)       # match manual redline red
DARK_RED = (0.90, 0.13, 0.22)
WHITE = (1.0, 1.0, 1.0)


# ── Data structures ────────────────────────────────
@dataclass
class PDFElement:
    """A text block or image extracted from the PDF with exact coordinates."""
    elem_id: str         # e.g. "T5" for text block 5, "I2" for image 2
    elem_type: str       # "text" or "image"
    bbox: tuple[float, float, float, float]  # (x0, y0, x1, y1) in PDF coords
    content: str         # text content or image description


@dataclass
class RedlineIssue:
    """A single redline issue identified by AI vision."""
    issue_id: int
    description: str           # e.g. "Replace outdated sterile symbol with ISO 15223-1:2021 version"
    area: str                  # e.g. "LEFT LABEL SECTION", "SYMBOL AREA"
    severity: str              # "non-conformance" (all ISO violations are equal)
    action: str                # "replace", "add", "remove", "update"
    search_hint: str = ""      # exact text visible near the issue for PDF text search
    element_ids: list[str] = field(default_factory=list)  # IDs of affected elements
    current_text: str = ""
    corrected_text: str = ""
    iso_reference: str = ""
    # Sub-region within the referenced element (for targeting specific
    # parts of large image elements like label artwork)
    sub_x_pct: float = 0.5    # X position within element (0=left, 1=right)
    sub_y_pct: float = 0.5    # Y position within element (0=top, 1=bottom)
    sub_w_pct: float = 1.0    # Width of sub-region as fraction of element width
    sub_h_pct: float = 1.0    # Height of sub-region as fraction of element height
    # Fallback coordinates if no element IDs matched (page-level percentages)
    x_pct: float = 0.5
    y_pct: float = 0.5
    width_pct: float = 0.1
    height_pct: float = 0.05


@dataclass
class RedlineResult:
    """Complete redline analysis result."""
    label_name: str
    issues: list[RedlineIssue] = field(default_factory=list)
    summary: str = ""
    ai_model: str = ""
    analysis_time: float = 0.0
    product_type: str = ""
    applicable_standards: list[str] = field(default_factory=list)


@dataclass
class PanelInfo:
    """Information about a cropped label panel (dynamic — works for ANY label PDF).

    Panel naming is done by AI in Pass 0, NOT by hardcoded position heuristics.
    This ensures the system works for any label layout, not just one product.
    """
    element_id: str                                    # e.g., "I2"
    image_path: Path                                   # path to high-res crop image
    bbox: tuple[float, float, float, float]            # original bbox in PDF coordinates
    pixel_size: tuple[int, int] = (0, 0)               # (width, height) of crop image
    panel_name: str = ""                               # AI-identified name (Pass 0)
    panel_type: str = ""                               # e.g., "outer_lid", "combo_label", "thermoform"
    issues: list[dict] = field(default_factory=list)   # Issues from Pass 1 per-panel analysis


# ── PDF Element Extraction ─────────────────────────
def _extract_pdf_elements(page: fitz.Page) -> list[PDFElement]:
    """Extract all text blocks and images with their exact PDF coordinates."""
    elements = []
    pw, ph = page.rect.width, page.rect.height

    # --- Text blocks ---
    blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
    text_idx = 0
    for b in blocks:
        if b["type"] != 0:
            continue
        text = ""
        for line in b["lines"]:
            for span in line["spans"]:
                text += span["text"]
            text += " "
        text = text.strip()
        if text and len(text) > 1:
            x0, y0, x1, y1 = b["bbox"]
            elements.append(PDFElement(
                elem_id=f"T{text_idx}",
                elem_type="text",
                bbox=(round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)),
                content=text[:120],
            ))
            text_idx += 1

    # --- Images with section labels ---
    imgs = page.get_images()
    for idx, img in enumerate(imgs):
        xref = img[0]
        rects = page.get_image_rects(xref)
        for r in rects:
            if r.is_valid and r.width > 10 and r.height > 10:
                # Identify section based on position on the page
                cx = (r.x0 + r.x1) / 2
                cy = (r.y0 + r.y1) / 2
                section = _identify_section(cx, cy, r, pw, ph)
                elements.append(PDFElement(
                    elem_id=f"I{idx}",
                    elem_type="image",
                    bbox=(round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1)),
                    content=f"Label artwork image {img[2]}x{img[3]}px — {section}",
                ))

    return elements


def _identify_section(
    cx: float, cy: float, rect: fitz.Rect, pw: float, ph: float
) -> str:
    """Identify which drawing region an element belongs to based on position.

    Uses relative position on the page (percentage-based) so it works for
    any label layout, not just one specific product.
    """
    rx = cx / pw  # relative X (0=left, 1=right)
    ry = cy / ph  # relative Y (0=top, 1=bottom)
    rw = rect.width / pw
    rh = rect.height / ph

    # Bottom strip — usually title block, revision table, notes
    if ry > 0.85:
        return "BOTTOM AREA (title block / notes / revision table)"
    # Top strip — revision block, header data
    if ry < 0.12:
        if rx < 0.5:
            return "TOP-LEFT DATA TABLE (product specifications / dimensions)"
        return "TOP-RIGHT AREA (revision history / drawing header)"
    # Large image spanning wide area — likely main label artwork
    if rw > 0.35 and rh > 0.15:
        return "MAIN LABEL ARTWORK (large image — primary label content)"
    # Left third — common for primary/outer label
    if rx < 0.38 and ry > 0.25:
        return "LEFT LABEL SECTION (label artwork area)"
    # Center — common for combo/secondary label
    if 0.35 < rx < 0.70 and ry > 0.25:
        return "CENTER LABEL SECTION (label artwork area)"
    # Right third
    if rx >= 0.65 and ry > 0.25:
        if rect.width > 300:
            return "RIGHT LABEL SECTION (wide — data inserts / product variants)"
        return "RIGHT LABEL SECTION (data insert or supplementary label)"
    # Data / specification table area
    if rx < 0.5 and ry < 0.35:
        return "DATA TABLE AREA (specifications / dimensions)"
    return "DRAWING AREA"


def _elements_to_text(elements: list[PDFElement], pw: float, ph: float) -> str:
    """Format elements list for the AI prompt."""
    lines = [f"PAGE SIZE: {pw:.0f} x {ph:.0f} points\n"]
    lines.append("ELEMENTS ON THE LABEL (ID, type, bbox [x0,y0,x1,y1], content):")
    lines.append("-" * 100)
    for e in elements:
        x0, y0, x1, y1 = e.bbox
        w = x1 - x0
        h = y1 - y0
        lines.append(
            f"  {e.elem_id:4s}  {e.elem_type:5s}  "
            f"[{x0:7.1f}, {y0:7.1f}, {x1:7.1f}, {y1:7.1f}]  "
            f"({w:.0f}x{h:.0f}pt)  {e.content}"
        )
    lines.append("-" * 100)
    return "\n".join(lines)


# ── Symbol Library Integration ─────────────────────

# Key symbols that MUST appear on medical device labels per ISO 15223 / MDR / FDA
_REQUIRED_LABEL_SYMBOLS = [
    # (search_keywords, display_name, iso_reference)
    ("manufacturer", "Manufacturer", "ISO 15223-1:2021, 5.1.1"),
    ("sterile", "Sterile (matching sterilization method)", "ISO 15223-1:2021, 5.2.3-5.2.8"),
    ("double sterile barrier", "Double sterile barrier system", "ISO 15223-1:2021, 5.2.10"),
    ("batch", "Batch code / LOT", "ISO 15223-1:2021, 5.1.5"),
    ("serial number", "Serial number", "ISO 15223-1:2021, 5.1.7"),
    ("use-by date", "Use-by date", "ISO 15223-1:2021, 5.1.4"),
    ("date of manufacture", "Date of manufacture", "ISO 15223-1:2021, 5.1.3"),
    ("quantity", "Quantity / Packaging unit", "ISO 15223-1:2021, 5.4.6"),
    ("do not re-use", "Do not re-use", "ISO 15223-1:2021, 5.2.2"),
    ("do not resterilize", "Do not resterilize", "ISO 15223-1:2021, 5.2.1"),
    ("caution", "Caution", "ISO 15223-1:2021, 5.4.4"),
    ("consult instruction", "Consult instructions for use", "ISO 15223-1:2021, 5.4.3"),
    ("medical device", "Medical Device (MD)", "EU MDR 2017/745, Annex I"),
    ("unique device", "Unique Device Identification (UDI)", "EU MDR 2017/745, Article 27"),
    ("authorized representative", "Authorized Representative (MR)", "ISO 15223-1:2021, 5.1.2"),
    ("Rx only", "Rx Only (Prescription)", "21 CFR 801.109"),
    ("not made with", "Not made with natural rubber latex", "FDA Guidance"),
]


def _get_symbol_reference_data() -> tuple[str, list[Path]]:
    """
    Load the symbol library and build:
    1. Text description of required symbols with expected appearance
    2. List of thumbnail image paths for visual reference

    Uses AI-enriched symbol library (symbol_library_ai.json) when available
    for richer descriptions; falls back to basic library otherwise.
    """
    from label_compliance.knowledge_base.ai_symbol_ingester import (
        get_ai_symbol_library,
        get_ai_symbol_reference_text,
    )

    lib = get_symbol_library()
    lib.load()

    # Try AI-enriched library first
    ai_db = get_ai_symbol_library()
    if ai_db:
        logger.info("Using AI-enriched symbol library (%d AI-annotated)",
                     ai_db.get("ai_annotated_symbols", 0))
        ai_text = get_ai_symbol_reference_text(ai_db)
    else:
        ai_text = ""

    lines = ["\n=== SYMBOL LIBRARY REFERENCE (from company Symbol Library Export) ==="]
    lines.append("The symbols on the label MUST match the CURRENT versions in this library.")
    lines.append("Compare each symbol on the label against these reference entries:\n")

    thumb_paths: list[Path] = []

    for keyword, required_name, iso_ref in _REQUIRED_LABEL_SYMBOLS:
        matches = lib.find_by_keywords(keyword.split())
        if not matches:
            text_matches = lib.find_by_text(keyword, threshold=0.5)
            matches = [m[0] for m in text_matches[:3]]

        if matches:
            best = None
            for m in matches:
                if m.is_standard and m.is_active:
                    best = m
                    break
            if not best:
                best = matches[0]

            lines.append(f"  REQUIRED: {required_name}")
            lines.append(f"    Library: row={best.row}, name='{best.name}'")
            lines.append(f"    Package text: '{best.pkg_text}'")
            lines.append(f"    Classification: {best.classification}")
            lines.append(f"    Thumbnail: {best.thumb_file_ref}")
            if best.std_thumb_file_ref:
                lines.append(f"    Standard thumb: {best.std_thumb_file_ref}")
            lines.append(f"    ISO Reference: {iso_ref}")

            # Add AI-enriched details if available
            if ai_db:
                for ai_sym in ai_db.get("symbols", []):
                    if ai_sym.get("row") == best.row and ai_sym.get("ai_visual_description"):
                        lines.append(f"    AI Visual: {ai_sym['ai_visual_description']}")
                        if ai_sym.get("ai_current_version_notes"):
                            lines.append(f"    Version Notes: {ai_sym['ai_current_version_notes']}")
                        break
            lines.append("")

            std_path = best.get_std_thumb_path(lib.library_dir)
            thumb_path = best.get_thumb_path(lib.library_dir)
            img = std_path or thumb_path
            if img and img not in thumb_paths:
                thumb_paths.append(img)
        else:
            lines.append(f"  REQUIRED: {required_name}")
            lines.append(f"    ** NOT FOUND in symbol library **")
            lines.append(f"    ISO Reference: {iso_ref}")
            lines.append("")

    lines.append(f"\nTotal reference symbols: {len(thumb_paths)} with thumbnails")
    lines.append("CRITICAL: Each symbol on the label must VISUALLY MATCH the current")
    lines.append("version from this library. Flag any symbol that uses an outdated design.\n")

    return "\n".join(lines), thumb_paths


def _crop_label_panels(
    page: fitz.Page,
    elements: list[PDFElement],
    label_name: str,
) -> list[PanelInfo]:
    """Crop individual label panels from the page at high resolution.

    Returns PanelInfo objects WITHOUT panel names — naming is done
    dynamically by AI in Pass 0, NOT by hardcoded position heuristics.

    Resolution scaling is ADAPTIVE:
    - Standard panels (≥ 200pt wide): 4x resolution
    - Small panels (< 200pt wide):   6x resolution for better detail

    This ensures small labels (Thermoform, patient cards) get enough
    resolution for the AI to read fine text and identify small symbols.
    """
    panels: list[PanelInfo] = []
    pw, ph = page.rect.width, page.rect.height

    # Find image elements that are label artwork (≥ 100pt wide or tall)
    label_images = [
        e for e in elements
        if e.elem_type == "image"
        and (e.bbox[2] - e.bbox[0]) > 100   # width > 100pt
        and (e.bbox[3] - e.bbox[1]) > 70    # height > 70pt
    ]

    if not label_images:
        return panels

    for elem in label_images:
        x0, y0, x1, y1 = elem.bbox
        panel_width = x1 - x0

        # Adaptive resolution: small panels get higher resolution
        scale = 4.0
        if panel_width < 150:
            scale = 8.0   # very small panels (e.g. Thermoform, cards)
        elif panel_width < 200:
            scale = 6.0   # small panels

        # Add small padding around the crop (10pt)
        pad = 10
        clip = fitz.Rect(
            max(0, x0 - pad),
            max(0, y0 - pad),
            min(pw, x1 + pad),
            min(ph, y1 + pad),
        )

        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)

        # Only keep panels large enough to be useful
        if pix.width < 200 or pix.height < 100:
            continue

        panel_path = Path(f"/tmp/panel_{label_name}_{elem.elem_id}.png")
        pix.save(str(panel_path))

        # NO hardcoded panel naming — AI will identify panels in Pass 0
        panels.append(PanelInfo(
            element_id=elem.elem_id,
            image_path=panel_path,
            bbox=(x0, y0, x1, y1),
            pixel_size=(pix.width, pix.height),
        ))
        logger.debug("Cropped panel %s: %dx%d pixels (%.0fx scale)",
                     elem.elem_id, pix.width, pix.height, scale)

    return panels


def _build_symbol_reference_sheet(thumb_paths: list[Path]) -> Path | None:
    """Composite key symbol thumbnails into a single reference image."""
    if not thumb_paths:
        return None

    from PIL import Image

    cell_size = 120
    padding = 10
    cols = min(6, len(thumb_paths))
    rows = (len(thumb_paths) + cols - 1) // cols

    sheet_w = cols * (cell_size + padding) + padding
    sheet_h = rows * (cell_size + padding + 20) + padding

    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")

    for idx, path in enumerate(thumb_paths):
        try:
            thumb = Image.open(path)
            thumb.thumbnail((cell_size, cell_size), Image.Resampling.LANCZOS)
            col = idx % cols
            row = idx // cols
            x = padding + col * (cell_size + padding)
            y = padding + row * (cell_size + padding + 20)
            x_off = (cell_size - thumb.width) // 2
            y_off = (cell_size - thumb.height) // 2
            sheet.paste(thumb, (x + x_off, y + y_off))
        except Exception as e:
            logger.debug("Could not load thumbnail %s: %s", path.name, e)

    out_path = Path("/tmp/symbol_reference_sheet.png")
    sheet.save(str(out_path))
    logger.info("Symbol reference sheet: %dx%d, %d symbols", sheet_w, sheet_h, len(thumb_paths))
    return out_path


# ── YAML Rules Loader ─────────────────────────────
def _load_yaml_rules_text() -> str:
    """Load ISO rules from YAML config files and format as prompt text.

    This feeds the SPECIFIC, actionable requirements from our rule definitions
    (with min sizes, required markers, severity, etc.) into the AI prompt.
    """
    from label_compliance.config import CONFIG_DIR
    rules_dir = CONFIG_DIR / "rules"
    if not rules_dir.exists():
        rules_dir = Path("config/rules")  # fallback

    lines = ["\n=== ISO STANDARD COMPLIANCE RULES (from config/rules/*.yaml) ==="]
    lines.append("These rules are derived from the applicable ISO standards.")
    lines.append("Check each rule against the label and flag any violations.\n")

    for yaml_file in sorted(rules_dir.glob("*.yaml")):
        try:
            data = yaml.safe_load(yaml_file.read_text())
        except Exception as e:
            logger.warning("Failed to load rules from %s: %s", yaml_file, e)
            continue

        standard = data.get("standard", yaml_file.stem)
        rules = data.get("rules", [])
        if not rules:
            continue

        lines.append(f"--- {standard} ({len(rules)} rules) ---")
        for rule in rules:
            rid = rule.get("id", "?")
            ref = rule.get("iso_ref", "")
            desc = rule.get("description", "")
            new = " [NEW 2024]" if rule.get("new_in_2024") else ""
            specs = rule.get("specs", {})

            lines.append(f"  [NC] {rid} ({ref}){new}: {desc}")

            # Include measurable specs
            if specs.get("min_height_mm"):
                lines.append(f"    → minimum symbol height: {specs['min_height_mm']}mm")
            if specs.get("min_font_size_pt"):
                lines.append(f"    → minimum font size: {specs['min_font_size_pt']}pt")
            if specs.get("font_style"):
                lines.append(f"    → required font style: {specs['font_style']}")
            if specs.get("must_include"):
                lines.append(f"    → must include: {specs['must_include']}")
            if specs.get("valid_classifications"):
                codes = [c['code'] for c in specs['valid_classifications']]
                lines.append(f"    → valid codes: {', '.join(codes)}")
            if specs.get("symbol_ref"):
                lines.append(f"    → symbol reference: {specs['symbol_ref']}")
        lines.append("")

    return "\n".join(lines)


# ── Pass 0: Dynamic Panel Identification ───────────
def _pass0_identify_panels(
    overview_image: Path,
    panels: list[PanelInfo],
    elements: list[PDFElement],
    pw: float,
    ph: float,
) -> list[PanelInfo]:
    """Pass 0: Use AI to dynamically identify what each panel is.

    Sends the full-page overview image + element list to o3 with low
    reasoning effort.  The AI names each panel (e.g., "Outer Lid Label",
    "Combo Label") and assigns a type.

    This is FULLY DYNAMIC — works for any label PDF.  No hardcoded names
    or position heuristics.
    """
    if not panels:
        return panels

    client = _get_openai_client()
    ai_cfg = _get_redline_ai_settings()

    # Build element summary for context
    panel_elements = []
    for p in panels:
        x0, y0, x1, y1 = p.bbox
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        panel_elements.append({
            "element_id": p.element_id,
            "relative_position": f"({cx/pw:.2f}, {cy/ph:.2f})",
            "size_pt": f"{x1-x0:.0f}x{y1-y0:.0f}",
            "pixels": f"{p.pixel_size[0]}x{p.pixel_size[1]}",
        })

    prompt = f"""Look at this medical device label engineering drawing.

I have extracted {len(panels)} image elements from the PDF that appear to be
label artwork panels. For each one, tell me:
1. What type of label panel it is (e.g., outer lid label, combo/set label,
   thermoform label, patient card, implant card, data table, etc.)
2. Give it a descriptive name

Here are the extracted panels with their relative positions on the page:
{json.dumps(panel_elements, indent=2)}

Respond with JSON:
{{
  "panels": [
    {{
      "element_id": "I2",
      "panel_name": "Outer Lid Label",
      "panel_type": "outer_lid"
    }}
  ]
}}

panel_type must be one of: outer_lid, combo_label, thermoform,
patient_card, implant_card, insert_card, data_table, title_block,
revision_table, notes_block, drawing_info, supplementary, unknown

IMPORTANT: classify title blocks, revision/history tables, BOM tables, and
general drawing notes as NON-LABEL panels (title_block/revision_table/
notes_block/drawing_info), not as label panels.

Be specific — look at the actual drawing to identify which element is which."""

    b64, mime = _encode_image(overview_image)

    try:
        t0 = time.time()
        response = client.chat.completions.create(
            model=_get_redline_model(),
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "developer",
                    "content": (
                        "You identify label panels in medical device engineering "
                        "drawings. Respond with valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime};base64,{b64}",
                                "detail": "high",
                            },
                        },
                    ],
                },
            ],
            reasoning_effort=ai_cfg.redline_pass0_reasoning_effort,
            max_completion_tokens=ai_cfg.redline_pass0_max_completion_tokens,
        )
        elapsed = time.time() - t0

        choice = response.choices[0]
        raw_content = choice.message.content or ""
        logger.info("Pass 0 finish_reason=%s, content_len=%d",
                     choice.finish_reason, len(raw_content))

        if not raw_content.strip():
            raise ValueError(f"Empty response (finish_reason={choice.finish_reason})")

        data = json.loads(raw_content)
        ai_panels = {p["element_id"]: p for p in data.get("panels", [])}

        # Save Pass 0 response for debugging
        debug_dir = Path("outputs/debug_sections")
        debug_dir.mkdir(parents=True, exist_ok=True)
        (debug_dir / "pass0_panel_identification.json").write_text(raw_content)

        for panel in panels:
            if panel.element_id in ai_panels:
                ap = ai_panels[panel.element_id]
                panel.panel_name = ap.get("panel_name", f"Panel {panel.element_id}")
                panel.panel_type = ap.get("panel_type", "unknown")
            else:
                panel.panel_name = f"Panel {panel.element_id}"
                panel.panel_type = "unknown"

        logger.info(
            "Pass 0: Identified %d panels in %.1fs: %s",
            len(panels), elapsed,
            ", ".join(f"{p.element_id}={p.panel_name}" for p in panels),
        )

    except Exception as e:
        logger.warning("Pass 0 panel identification failed: %s — using fallback names", e)
        for panel in panels:
            panel.panel_name = f"Panel {panel.element_id}"
            panel.panel_type = "unknown"

    return panels


def _build_panel_prompt(
    panel: PanelInfo,
    elements_text: str,
    label_text: str,
    symbol_ref_text: str = "",
    iso_requirements_text: str = "",
    yaml_rules_text: str = "",
) -> str:
    """Build a focused prompt for analyzing a SINGLE label panel.

    Gives the AI full, undivided attention on ONE panel — resulting
    in much more thorough analysis of small text, symbols, and barcodes.
    """
    # Symbol library reference
    symbol_section = ""
    if symbol_ref_text:
        symbol_section = f"""
=== COMPANY SYMBOL LIBRARY REFERENCE ===
{symbol_ref_text}

A SECOND IMAGE is attached showing the REFERENCE SYMBOLS from the company
Symbol Library.  VISUALLY compare EVERY symbol on this panel against these
reference thumbnails.  Flag any symbol whose shape, lines, or proportions
differ from the CURRENT library version.
"""

    # ISO requirements (summarised)
    iso_section = ""
    if iso_requirements_text:
        iso_lines = iso_requirements_text.split("\n")
        key_lines = [
            l for l in iso_lines
            if any(kw in l.lower() for kw in [
                "shall", "must", "required", "minimum", "height", "symbol",
                "marking", "label", "font", "section", "clause", "table",
                "barcode", "udi", "human readable", "hri", "data matrix",
                "datamatrix", "sterile", "quantity", "packaging",
            ])
        ][:40]
        if key_lines:
            iso_section = (
                "\n=== ISO STANDARD REQUIREMENTS ===\n"
                + "\n".join(key_lines) + "\n"
            )

    prompt = f"""You are an expert medical device label compliance reviewer.
You are analysing ONE SPECIFIC label panel in full detail.

╔══════════════════════════════════════════════════════════════════╗
║  PANEL UNDER REVIEW: {panel.panel_name:^42s} ║
╚══════════════════════════════════════════════════════════════════╝

Panel type : {panel.panel_type}
Element ID : {panel.element_id}
Size (pt)  : {panel.bbox[2]-panel.bbox[0]:.0f} × {panel.bbox[3]-panel.bbox[1]:.0f}

The attached HIGH-RESOLUTION image shows ONLY this panel.
Examine EVERY symbol, EVERY barcode, EVERY piece of text.
This is a CRITICAL quality review — missing a real compliance issue is a
serious failure.  Be absolutely EXHAUSTIVE.

=== FULL-PAGE ELEMENT MAP (for context) ===
{elements_text}

=== LABEL TEXT (OCR from full page) ===
{label_text}
{symbol_section}
{iso_section}
{yaml_rules_text}

────────────────────────────────────────────────
STEP 1 — SYMBOL COMPLIANCE MATRIX
────────────────────────────────────────────────
Check EVERY symbol in the checklist below ON THIS PANEL.
Report each as: present_correct | present_wrong_version | missing | n_a

Required Symbol Checklist (ISO 15223-1:2021 + applicable regs):
  □ Manufacturer (ISO 7000-3082) — factory with chimney icon
  □ Authorized Representative (ISO 7000-3088) — if EU market
  □ Date of manufacture (ISO 7000-2497) — calendar/factory icon
  □ Use-by date (ISO 7000-2607) — hourglass icon
  □ Batch/LOT code (ISO 7000-2492) — "LOT" text in frame
  □ Serial number (ISO 7000-2498) — "SN" text in frame
  □ Catalogue/REF number (ISO 7000-2493) — "REF" text in frame
  □ Sterile symbol (ISO 7000-2501 or method-specific)
  □ Double sterile barrier (ISO 15223-1:2021, 5.2.10) — if double packaging
  □ Do not re-use (ISO 7000-1051) — "2" with circle/line
  □ Do not resterilize — if sterile device
  □ Caution (ISO 15223-1:2021, 5.4.4)
  □ Consult IFU (ISO 7000-1641) — person reading document
  □ Quantity / Contains (ISO 15223-1:2021, 5.4.6)
  □ CE mark with notified body number
  □ Medical Device symbol (MDR Annex I) — "MD" diamond
  □ UDI symbol — adjacent to barcode/DataMatrix

For EACH symbol you flag (wrong version or missing), compare CAREFULLY
against the Symbol Library reference images.  Pay attention to:
  – Enclosure style (square vs. round, border vs. none)
  – Line weights and proportions
  – Fill / shading differences
  – Text within or around the symbol
  – Overall shape — even small design changes between ISO versions matter

────────────────────────────────────────────────
STEP 2 — BARCODE & UDI AUDIT
────────────────────────────────────────────────
Per EU MDR Art. 27 / FDA 21 CFR 830, EACH packaging level needs:
  □ 1D linear barcode (GS1-128)
  □ 2D DataMatrix (UDI-DI + UDI-PI)
  □ HRI (Human Readable Interpretation) — plain-text GTIN, serial, LOT,
    expiry ADJACENT to the barcode/DataMatrix

Check THIS panel:
  (a) 1D barcode present?  Also a 2D DataMatrix?
      → If only 1D and no DataMatrix → flag: ADD 2D DataMatrix
  (b) HRI text adjacent to each barcode?
      → Must include human-readable serial, LOT, expiry
      → If missing or incomplete → flag: ADD / COMPLETE HRI
  (c) UDI symbol adjacent to the UDI barcode?

────────────────────────────────────────────────
STEP 3 — TEXT CONTENT AUDIT
────────────────────────────────────────────────
(A) REDUNDANT TEXT — flag for REMOVAL when a symbol already conveys it:
    • "Quantity: N" text + quantity symbol → remove text
    • "Sterile" text + sterile symbol → remove text
    • "Single use" text + do-not-reuse symbol → remove text
    • Any free-text duplicating an ISO symbol's meaning

(B) UNNECESSARY / LEGACY TEXT — flag for REMOVAL if no ISO clause mandates
    it and it is not essential product identification:
    • Material composition as text (should be ISO symbol)
    • Safety warnings with ISO symbol equivalents
    • Legacy carry-over text from prior revisions

(C) FONT STYLE CONSISTENCY:
    All body text should use a consistent style (typically regular/roman).
    Flag: italic where surrounding text is regular, unexpected bold, etc.

(D) HEADING / LABEL ACCURACY (patient / implant cards):
    Per ISO 14607 Annex H — check required field headings.
    Flag non-ISO headings (e.g., "Patient name:" if not in Annex H).

(E) DATE FORMAT: All dates must use ISO 8601 (YYYY-MM-DD).

MANDATORY DELETION SWEEP (do this explicitly before finalizing issues):
    □ Scan every visible line for text that should be removed
    □ Scan every visible symbol/pictogram for items that should be removed
    □ If removal is needed, action MUST be "remove" (not "update")

High-priority deletion candidates:
    • Legacy safety/material phrases that are not required on this panel
    • Redundant headings/labels on patient or implant cards
    • Obsolete symbols replaced by current library versions
    • Free-text fields that should be represented by standard symbols

────────────────────────────────────────────────
STEP 4 — SYMBOLS / TEXT THAT SHOULD BE ABSENT
────────────────────────────────────────────────
  (a) Symbol NOT in the current Symbol Library? → flag for removal
  (b) Deprecated symbol design? → flag for replacement
  (c) Symbol not required by ISO for this device type? → flag
  (d) Text / pictograms with no ISO purpose? → flag for removal

=== OUTPUT FORMAT ===

Respond with JSON:
{{{{
  "panel_name": "{panel.panel_name}",
  "element_id": "{panel.element_id}",
  "symbol_audit": {{{{
    "manufacturer":       {{{{"status": "present_correct|present_wrong_version|missing|n_a", "notes": ""}}}},
    "date_of_manufacture": {{{{"status": "...", "notes": ""}}}},
    "use_by_date":        {{{{"status": "...", "notes": ""}}}},
    "batch_lot":          {{{{"status": "...", "notes": ""}}}},
    "serial_number":      {{{{"status": "...", "notes": ""}}}},
    "catalogue_ref":      {{{{"status": "...", "notes": ""}}}},
    "sterile":            {{{{"status": "...", "notes": ""}}}},
    "double_sterile":     {{{{"status": "...", "notes": ""}}}},
    "do_not_reuse":       {{{{"status": "...", "notes": ""}}}},
    "do_not_resterilize": {{{{"status": "...", "notes": ""}}}},
    "caution":            {{{{"status": "...", "notes": ""}}}},
    "consult_ifu":        {{{{"status": "...", "notes": ""}}}},
    "quantity":           {{{{"status": "...", "notes": ""}}}},
    "ce_mark":            {{{{"status": "...", "notes": ""}}}},
    "medical_device":     {{{{"status": "...", "notes": ""}}}},
    "udi":                {{{{"status": "...", "notes": ""}}}},
    "authorized_rep":     {{{{"status": "...", "notes": ""}}}}
  }}}},
  "barcode_audit": {{{{
    "linear_1d_present": true,
    "datamatrix_2d_present": false,
    "hri_present": false,
    "notes": "..."
  }}}},
  "issues": [
    {{{{
      "issue_id": 1,
      "description": "Specific description of what is wrong",
      "severity": "non-conformance",
      "action": "replace|add|remove|update",
      "current_text": "What you ACTUALLY SEE on the panel",
      "corrected_text": "What it SHOULD be per ISO / Symbol Library",
      "search_hint": "2-5 words of EXACT text visible NEAR this issue",
      "iso_reference": "Exact ISO clause (e.g., ISO 15223-1:2021, 5.1.1)",
      "sub_x_pct": 0.5,
      "sub_y_pct": 0.5,
      "sub_w_pct": 0.10,
      "sub_h_pct": 0.08
    }}}}
  ]
}}}}

=== CRITICAL RULES ===

1. DO NOT report a symbol as "missing" if it IS visible — look carefully.
2. DO NOT report barcodes as "missing" if you see a barcode pattern.
3. DO flag symbol DESIGN mismatches vs. the Symbol Library reference.
4. "search_hint" must be EXACT text visible on the label near the issue.
5. "severity" is always "non-conformance".
6. sub_x_pct / sub_y_pct are positions WITHIN THIS PANEL IMAGE
   (0,0 = top-left, 1,1 = bottom-right).
7. Create SEPARATE issues for each distinct problem.
8. Do NOT miss REMOVE actions — removal findings are mandatory when present.
9. If you find fewer than 2 issues on this panel, look again more carefully —
   most panels have at least 2-5 compliance issues.
"""
    return prompt


# ── AI Calls ───────────────────────────────────────

def _get_redline_ai_settings():
    """Return AI settings for redline passes."""
    return get_settings().ai


def _get_redline_model() -> str:
    """Configured model for redline analysis."""
    return _get_redline_ai_settings().redline_model


def _get_openai_client():
    """Get an authenticated OpenAI-compatible API client.

    Uses the centralized factory from config.py — works with
    OpenAI, xAI/Grok, NVIDIA NIM, Together, Groq, Azure, etc.
    """
    from label_compliance.config import get_ai_client
    return get_ai_client()


def _encode_image(path: Path) -> tuple[str, str]:
    """Base64-encode an image file and return (b64_string, mime_type)."""
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    ext = path.suffix.lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")
    return b64, mime


def _pass1_analyze_panel(
    panel: PanelInfo,
    prompt: str,
    symbol_sheet_path: Path | None = None,
) -> list[dict]:
    """Pass 1: Analyse a single panel with focused AI attention.

    Each panel is sent INDIVIDUALLY so the model can devote its full
    reasoning capacity to reading small text, checking every symbol,
    and auditing barcodes on THIS panel alone.

    Returns list of issue dicts for this panel.
    """
    client = _get_openai_client()
    ai_cfg = _get_redline_ai_settings()

    panel_b64, panel_mime = _encode_image(panel.image_path)

    content_parts: list[dict] = [
        {"type": "text", "text": prompt},
        {
            "type": "text",
            "text": f"HIGH-RESOLUTION CROP of {panel.panel_name} ({panel.element_id}):",
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:{panel_mime};base64,{panel_b64}",
                "detail": "high",
            },
        },
    ]

    # Attach symbol reference sheet for visual comparison
    if symbol_sheet_path and symbol_sheet_path.exists():
        sym_b64, _ = _encode_image(symbol_sheet_path)
        content_parts.append({
            "type": "text",
            "text": "SYMBOL LIBRARY REFERENCE — compare symbols against these current versions:",
        })
        content_parts.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{sym_b64}",
                "detail": "high",
            },
        })

    logger.info("Pass 1: Analysing %s (%s) ...", panel.panel_name, panel.element_id)
    t0 = time.time()

    try:
        response = client.chat.completions.create(
            model=_get_redline_model(),
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "developer",
                    "content": (
                        "You are an expert medical device label compliance reviewer. "
                        "You are performing a focused, exhaustive review of a SINGLE "
                        "label panel. Check every symbol, barcode, and text element. "
                        "Be thorough — missing a real issue is a serious failure. "
                        "Always respond with valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": content_parts,
                },
            ],
            reasoning_effort=ai_cfg.redline_pass1_reasoning_effort,
            max_completion_tokens=ai_cfg.redline_pass1_max_completion_tokens,
        )

        elapsed = time.time() - t0
        content = response.choices[0].message.content or ""
        usage = response.usage

        if usage:
            logger.info(
                "Pass 1 (%s): %.1fs — %d tokens (prompt=%d, completion=%d)",
                panel.element_id, elapsed,
                usage.total_tokens, usage.prompt_tokens, usage.completion_tokens,
            )

        if not content.strip():
            logger.error("Pass 1 returned empty for %s (finish_reason=%s)",
                         panel.element_id, response.choices[0].finish_reason)
            return []

        # Save raw AI response for debugging
        debug_dir = Path("outputs/debug_sections")
        debug_dir.mkdir(parents=True, exist_ok=True)
        debug_file = debug_dir / f"pass1_{panel.element_id}_{panel.panel_type}.json"
        debug_file.write_text(content)
        logger.info("Saved Pass 1 raw response: %s", debug_file.name)

        data = json.loads(content)
        issues = data.get("issues", [])

        # Enrich issues with panel context
        for iss in issues:
            iss["area"] = panel.panel_name
            iss["element_ids"] = [panel.element_id]

        # Log audit summary
        symbol_audit = data.get("symbol_audit", {})
        flagged = [
            k for k, v in symbol_audit.items()
            if isinstance(v, dict) and v.get("status") not in ("present_correct", "n_a")
        ]
        if flagged:
            logger.info("  Symbol flags: %s", ", ".join(flagged))

        barcode_audit = data.get("barcode_audit", {})
        if barcode_audit:
            logger.info(
                "  Barcode: 1D=%s, DataMatrix=%s, HRI=%s",
                barcode_audit.get("linear_1d_present", "?"),
                barcode_audit.get("datamatrix_2d_present", "?"),
                barcode_audit.get("hri_present", "?"),
            )

        logger.info("Pass 1 (%s): Found %d issues", panel.element_id, len(issues))
        return issues

    except Exception as e:
        logger.error("Pass 1 failed for %s: %s", panel.element_id, e, exc_info=True)
        return []


# ── Pass 2: Cross-Panel Consistency Review ────────
def _pass2_cross_panel_review(
    panels: list[PanelInfo],
    all_issues: list[dict],
    overview_image: Path,
    symbol_sheet_path: Path | None = None,
) -> list[dict]:
    """Pass 2: Cross-panel consistency review.

    After individual panel analysis, check for:
    1. Issues found on one panel but missing on others
    2. Cross-panel consistency problems
    3. Anything the per-panel analyses may have missed
    """
    if not panels or not all_issues:
        return []

    client = _get_openai_client()
    ai_cfg = _get_redline_ai_settings()

    # Build summary of per-panel findings
    panel_summaries = []
    for panel in panels:
        panel_issues = [i for i in all_issues if i.get("area") == panel.panel_name]
        summary = {
            "panel_name": panel.panel_name,
            "panel_type": panel.panel_type,
            "element_id": panel.element_id,
            "issue_count": len(panel_issues),
            "issues": [
                {
                    "description": i.get("description", "")[:100],
                    "action": i.get("action", ""),
                    "iso_reference": i.get("iso_reference", ""),
                }
                for i in panel_issues
            ],
        }
        panel_summaries.append(summary)

    prompt = f"""You have already reviewed each label panel individually.
Now perform a CROSS-PANEL consistency check.

=== PANELS AND THEIR FINDINGS ===
{json.dumps(panel_summaries, indent=2)}

=== OVERVIEW IMAGE ATTACHED ===
The full engineering drawing is attached for reference.

CROSS-PANEL CHECKS:

1. SYMBOL CONSISTENCY: If a symbol issue was found on one panel (e.g.,
   outdated Quantity symbol), check whether the SAME issue exists on OTHER
   panels.  Create a SEPARATE issue for each affected panel.

2. BARCODE CONSISTENCY: If DataMatrix or HRI was missing on one panel,
   check ALL other panels too.  Each packaging level needs its own
   DataMatrix + HRI.

3. FONT CONSISTENCY: If font issues were found on one panel, check others.

4. MISSED ITEMS: Looking at the overview, are there any OBVIOUS issues
   visible that none of the individual panel analyses caught?

5. PANEL-SPECIFIC REQUIREMENTS: Some panel types have unique requirements:
   – Patient / Implant cards need their OWN barcodes + DataMatrix + HRI
   – Thermoform labels are a packaging level with full requirements
   – Each packaging level is independent for UDI purposes

Only report NEW issues not already covered in the per-panel analyses.
Do NOT duplicate existing issues.

Respond with JSON:
{{{{
  "cross_panel_issues": [
    {{{{
      "issue_id": 1,
      "description": "...",
      "area": "Panel name where this issue occurs",
      "severity": "non-conformance",
      "action": "replace|add|remove|update",
      "element_ids": ["I2"],
      "current_text": "...",
      "corrected_text": "...",
      "search_hint": "2-5 words of EXACT text NEAR this issue",
      "iso_reference": "...",
      "sub_x_pct": 0.5,
      "sub_y_pct": 0.5,
      "sub_w_pct": 0.10,
      "sub_h_pct": 0.10
    }}}}
  ],
  "notes": "Any observations about cross-panel consistency"
}}}}

If no additional cross-panel issues are found, return an empty list.
"""

    b64, mime = _encode_image(overview_image)

    content_parts: list[dict] = [
        {"type": "text", "text": prompt},
        {"type": "text", "text": "FULL DRAWING OVERVIEW:"},
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime};base64,{b64}",
                "detail": "high",
            },
        },
    ]

    # Attach symbol sheet for reference
    if symbol_sheet_path and symbol_sheet_path.exists():
        sym_b64, _ = _encode_image(symbol_sheet_path)
        content_parts.append({"type": "text", "text": "SYMBOL LIBRARY REFERENCE:"})
        content_parts.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{sym_b64}",
                "detail": "high",
            },
        })

    logger.info("Pass 2: Cross-panel consistency review ...")
    t0 = time.time()

    try:
        response = client.chat.completions.create(
            model=_get_redline_model(),
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "developer",
                    "content": (
                        "You perform cross-panel consistency checks on medical "
                        "device labels. Find issues that span multiple panels or "
                        "were missed in individual panel reviews. "
                        "Always respond with valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": content_parts,
                },
            ],
            reasoning_effort=ai_cfg.redline_pass2_reasoning_effort,
            max_completion_tokens=ai_cfg.redline_pass2_max_completion_tokens,
        )

        elapsed = time.time() - t0
        content = response.choices[0].message.content or ""
        usage = response.usage

        if usage:
            logger.info("Pass 2: %.1fs — %d tokens", elapsed, usage.total_tokens)

        if not content.strip():
            logger.warning("Pass 2 returned empty (finish_reason=%s)",
                           response.choices[0].finish_reason)
            return []

        # Save Pass 2 response for debugging
        debug_dir = Path("outputs/debug_sections")
        debug_dir.mkdir(parents=True, exist_ok=True)
        (debug_dir / "pass2_cross_panel.json").write_text(content)

        data = json.loads(content)
        cross_issues = data.get("cross_panel_issues", [])

        if data.get("notes"):
            logger.info("Pass 2 notes: %s", data["notes"])

        logger.info("Pass 2: Found %d cross-panel issues", len(cross_issues))
        return cross_issues

    except Exception as e:
        logger.error("Pass 2 cross-panel review failed: %s", e)
        return []

def _parse_ai_response(response_text: str, label_name: str) -> RedlineResult:
    """Parse the JSON response from the AI into RedlineResult."""
    result = RedlineResult(label_name=label_name)

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse AI response: %s", e)
        result.summary = f"JSON parse error: {e}"
        return result

    result.summary = data.get("summary", "")
    result.ai_model = _get_redline_model()
    result.product_type = data.get("product_type", "")
    result.applicable_standards = data.get("applicable_standards", [])

    # Log the panel compliance matrix for debugging / audit trail
    matrix = data.get("panel_compliance_matrix", [])
    if matrix:
        logger.info("=== PANEL COMPLIANCE MATRIX ===")
        for panel_entry in matrix:
            panel_name = panel_entry.get("panel", "Unknown")
            logger.info("Panel: %s (element: %s)", panel_name, panel_entry.get("element_id", "?"))
            symbol_audit = panel_entry.get("symbol_audit", {})
            for sym_name, sym_data in symbol_audit.items():
                status = sym_data.get("status", "?") if isinstance(sym_data, dict) else sym_data
                notes = sym_data.get("notes", "") if isinstance(sym_data, dict) else ""
                if status not in ("present_correct", "n_a"):
                    logger.info("  %s: %s %s", sym_name, status, f"— {notes}" if notes else "")
            barcode = panel_entry.get("barcode_audit", {})
            if barcode:
                dm = barcode.get("datamatrix_2d_present", "?")
                hri = barcode.get("hri_present", "?")
                logger.info("  Barcodes: DataMatrix=%s, HRI=%s", dm, hri)
            text_issues = panel_entry.get("text_issues", [])
            for ti in text_issues:
                logger.info("  Text issue: %s", ti)
        logger.info("=== END MATRIX ===")

    for item in data.get("issues", []):
        eids = item.get("element_ids", [])
        if isinstance(eids, str):
            eids = [eids]

        issue = RedlineIssue(
            issue_id=item.get("issue_id", 0),
            description=item.get("description", ""),
            area=item.get("area", ""),
            severity="non-conformance",  # all ISO violations are equal
            search_hint=item.get("search_hint", ""),
            action=item.get("action", "update"),
            element_ids=eids,
            current_text=item.get("current_text", ""),
            corrected_text=item.get("corrected_text", ""),
            iso_reference=item.get("iso_reference", ""),
            sub_x_pct=float(item.get("sub_x_pct", 0.5)),
            sub_y_pct=float(item.get("sub_y_pct", 0.5)),
            sub_w_pct=float(item.get("sub_w_pct", 1.0)),
            sub_h_pct=float(item.get("sub_h_pct", 1.0)),
            x_pct=float(item.get("x_pct", 0.5)),
            y_pct=float(item.get("y_pct", 0.5)),
            width_pct=float(item.get("width_pct", 0.1)),
            height_pct=float(item.get("height_pct", 0.05)),
        )
        result.issues.append(issue)

    return result


def _is_non_label_panel(panel: PanelInfo) -> bool:
    """Return True when a panel should be skipped for label compliance analysis."""
    ai_cfg = _get_redline_ai_settings()
    skip_types = {t.strip().lower() for t in ai_cfg.redline_skip_panel_types if t}
    skip_name_keywords = [k.strip().lower() for k in ai_cfg.redline_skip_name_keywords if k]

    panel_type = (panel.panel_type or "").strip().lower()
    panel_name = (panel.panel_name or "").strip().lower()

    if panel_type in skip_types:
        return True

    return any(kw in panel_name for kw in skip_name_keywords)


# ── Analysis Pipeline ──────────────────────────────
def analyze_label_with_ai(
    pdf_path: Path,
    page_idx: int = 0,
) -> tuple[RedlineResult, list[PDFElement]]:
    """
    Multi-pass per-panel AI analysis pipeline:

      Pass 0  (o3 low)   : Dynamic panel identification — AI names each panel
      Pass 1  (o3 medium): Per-panel exhaustive analysis — one call per panel
      Pass 2  (o3 medium): Cross-panel consistency review

    Typical runtime: ~3-5 minutes (vs ~10-15 min with high reasoning).

    The pipeline is FULLY DYNAMIC — panels are discovered from the PDF
    structure and identified by AI, not hardcoded for any specific product.

    Returns:
        (RedlineResult, list of PDFElements for coordinate lookup)
    """
    label_name = pdf_path.stem
    result = RedlineResult(label_name=label_name)
    elements: list[PDFElement] = []

    t0 = time.time()

    try:
        doc = fitz.open(str(pdf_path))
        page = doc[page_idx]
        pw, ph = page.rect.width, page.rect.height

        # ── Preparation ─────────────────────────────────
        # Step 1: Extract all elements with exact coordinates
        elements = _extract_pdf_elements(page)
        logger.info("Extracted %d elements from %s", len(elements), pdf_path.name)

        # Step 2: Build element map text
        elements_text = _elements_to_text(elements, pw, ph)

        # Step 3: Render full page overview image
        mat = fitz.Matrix(3.0, 3.0)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        overview_path = Path(f"/tmp/label_overview_{label_name}.png")
        pix.save(str(overview_path))
        logger.info("Rendered overview: %dx%d", pix.width, pix.height)

        # Step 4: Crop individual panels (NO naming yet — dynamic)
        panels = _crop_label_panels(page, elements, label_name)
        logger.info("Cropped %d label panels", len(panels))

        # Step 5: Get full page text for context
        label_text = page.get_text()

        doc.close()

        # Step 6: Load AI-extracted ISO knowledge base
        iso_req_text = ""
        iso_kb = get_ai_iso_knowledge()
        if iso_kb:
            iso_req_text = get_labelling_requirements_text(iso_kb)
            logger.info(
                "Loaded AI-extracted ISO knowledge: %d sections",
                iso_kb.get("total_sections", 0),
            )
        else:
            logger.info(
                "No AI-extracted ISO KB — run 'label-compliance ingest-ai' to create"
            )

        # Step 7: Load symbol library reference
        symbol_ref_text, thumb_paths = _get_symbol_reference_data()
        logger.info("Symbol library: %d reference symbols", len(thumb_paths))

        # Step 8: Build symbol reference sheet
        symbol_sheet_path = _build_symbol_reference_sheet(thumb_paths)

        # Step 9: Load YAML rules (called once, reused for every panel)
        yaml_rules_text = _load_yaml_rules_text()

        # ══════════════════════════════════════════════════════
        # PASS 0 — Dynamic panel identification
        # ══════════════════════════════════════════════════════
        print(f"    Pass 0: Identifying {len(panels)} panels...")
        panels = _pass0_identify_panels(
            overview_path, panels, elements, pw, ph,
        )

        # Filter: only analyse actual label panels, skip title/revision tables/notes blocks.
        label_panels = [p for p in panels if not _is_non_label_panel(p)]
        skipped_panels = [p for p in panels if _is_non_label_panel(p)]
        skipped = len(skipped_panels)
        if skipped:
            skipped_names = ", ".join(
                f"{p.panel_name} ({p.panel_type or 'unknown'})" for p in skipped_panels
            )
            logger.info("Skipping %d non-label panels: %s", skipped, skipped_names)
            print(f"    Skipping {skipped} non-label panels")
        panels_to_analyse = label_panels if label_panels else panels

        panel_names = ", ".join(p.panel_name for p in panels_to_analyse)
        print(f"    Panels: {panel_names}")

        # ══════════════════════════════════════════════════════
        # PASS 1 — Per-panel exhaustive analysis
        # ══════════════════════════════════════════════════════
        all_issues: list[dict] = []
        issue_counter = 1

        for idx, panel in enumerate(panels_to_analyse, 1):
            print(f"    Pass 1: [{idx}/{len(panels_to_analyse)}] Analysing {panel.panel_name}...")
            prompt = _build_panel_prompt(
                panel,
                elements_text,
                label_text,
                symbol_ref_text,
                iso_req_text,
                yaml_rules_text,
            )
            panel_issues = _pass1_analyze_panel(panel, prompt, symbol_sheet_path)

            # Re-number issues globally
            for iss in panel_issues:
                iss["issue_id"] = issue_counter
                issue_counter += 1

            panel.issues = panel_issues
            all_issues.extend(panel_issues)
            print(f"      → {len(panel_issues)} issues found")

        logger.info(
            "Pass 1 total: %d issues across %d panels",
            len(all_issues), len(panels_to_analyse),
        )

        # ══════════════════════════════════════════════════════
        # PASS 2 — Cross-panel consistency review
        # ══════════════════════════════════════════════════════
        print(f"    Pass 2: Cross-panel consistency check...")
        cross_issues = _pass2_cross_panel_review(
            panels_to_analyse, all_issues, overview_path, symbol_sheet_path,
        )

        # Re-number cross-panel issues
        for iss in cross_issues:
            iss["issue_id"] = issue_counter
            issue_counter += 1
        all_issues.extend(cross_issues)

        if cross_issues:
            logger.info(
                "Pass 2 added %d cross-panel issues (total: %d)",
                len(cross_issues), len(all_issues),
            )
        print(f"      → {len(cross_issues)} cross-panel issues")

        # ── Build final result ──────────────────────────
        final_data = {
            "product_type": "",
            "applicable_standards": [],
            "panel_compliance_matrix": [],
            "issues": all_issues,
            "summary": (
                f"Found {len(all_issues)} non-conformances across "
                f"{len(panels)} panels "
                f"({len(all_issues) - len(cross_issues)} per-panel + "
                f"{len(cross_issues)} cross-panel)"
            ),
        }
        result = _parse_ai_response(json.dumps(final_data), label_name)
        result.analysis_time = time.time() - t0

        logger.info(
            "AI redline complete: %d issues in %.1fs (3-pass per-panel with %s)",
            len(result.issues), result.analysis_time, _get_redline_model(),
        )

        # ── Cleanup temp files ──────────────────────────
        overview_path.unlink(missing_ok=True)
        if symbol_sheet_path:
            symbol_sheet_path.unlink(missing_ok=True)
        for panel in panels:
            panel.image_path.unlink(missing_ok=True)

    except Exception as e:
        logger.error("AI redline analysis failed: %s", e, exc_info=True)
        result.summary = f"Analysis failed: {e}"

    return result, elements


# ── PDF Annotation ─────────────────────────────────
def generate_ai_redline_pdf(
    pdf_path: Path,
    redline_result: RedlineResult,
    elements: list[PDFElement],
    output_dir: Path | None = None,
) -> Path | None:
    """Generate a redlined PDF with compact numbered markers + legend page.

    Page 1: Original drawing with small numbered red circles + highlight boxes
    Page 2: Legend table listing every issue with full details
    """
    settings = get_settings()
    if output_dir is None:
        output_dir = settings.paths.redline_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    out_name = f"redlined-{pdf_path.stem.replace(' ', '_')}.pdf"
    out_path = output_dir / out_name

    try:
        doc = fitz.open(str(pdf_path))
    except Exception:
        logger.exception("Cannot open PDF: %s", pdf_path)
        return None

    page = doc[0]
    pw, ph = page.rect.width, page.rect.height

    # Build element lookup
    elem_map: dict[str, PDFElement] = {e.elem_id: e for e in elements}

    used_marker_rects: list[fitz.Rect] = []

    for issue in redline_result.issues:
        _place_compact_marker(page, issue, elem_map, pw, ph, used_marker_rects)

    # Footer note on drawing page
    _add_revision_note(page, redline_result, pw, ph)

    # Add legend page with full issue details
    _add_legend_page(doc, redline_result)

    doc.save(str(out_path))
    doc.close()
    logger.info("AI Redlined PDF saved: %s (%d issues, 2 pages)", out_path.name, len(redline_result.issues))
    return out_path


def _place_compact_marker(
    page: fitz.Page,
    issue: RedlineIssue,
    elem_map: dict[str, PDFElement],
    pw: float,
    ph: float,
    used_rects: list[fitz.Rect],
) -> None:
    """Place a compact numbered marker: red highlight box + small number label.

    Instead of verbose text callouts that overlap, we place:
    1. A red rectangle around the issue area
    2. A small red circle with the issue number
    3. A short 1-line label (truncated description)
    """
    # Resolve the target area from element IDs (with text search fallback)
    area_rect = _resolve_area_rect(issue, elem_map, pw, ph, page)

    # All non-conformances use the same red color — every ISO violation matters equally
    box_color = RED

    if area_rect.is_valid and area_rect.width > 2 and area_rect.height > 2:
        # Draw red highlight box
        border_w = 2.0
        annot = page.add_rect_annot(area_rect)
        annot.set_colors(stroke=box_color)
        annot.set_border(width=border_w)
        annot.set_opacity(0.75)
        annot.set_info(content=issue.description)
        annot.update()

    # Place numbered marker — small red circle with issue number
    marker_num = str(issue.issue_id)
    marker_radius = 8
    # Short label: NC prefix + truncated description
    short_label = issue.description[:55]
    if len(issue.description) > 55:
        short_label = short_label[:52] + "..."

    # Determine marker position — near the top-right corner of the highlight box
    if area_rect.is_valid and area_rect.width > 2:
        mx = area_rect.x1 + 2
        my = area_rect.y0 - 2
    else:
        mx = pw * 0.5
        my = ph * 0.5

    # Find a non-overlapping position for the marker + label
    label_w = min(200, len(short_label) * 4.5 + 30)
    label_h = 14
    marker_rect = fitz.Rect(mx - 1, my - marker_radius - 1,
                            mx + label_w, my + label_h + 2)

    # Shift if overlapping existing markers
    for _ in range(15):
        has_overlap = False
        for used in used_rects:
            inter = marker_rect & used
            if inter.is_valid and not inter.is_empty and inter.width > 1 and inter.height > 1:
                has_overlap = True
                marker_rect.y0 = used.y1 + 3
                marker_rect.y1 = marker_rect.y0 + label_h + marker_radius + 3
                break
        if not has_overlap:
            break

    # Clamp to page bounds
    if marker_rect.y1 > ph - 5:
        marker_rect.y0 = ph - label_h - marker_radius - 10
        marker_rect.y1 = ph - 5
    if marker_rect.x1 > pw - 5:
        shift = marker_rect.x1 - (pw - 5)
        marker_rect.x0 -= shift
        marker_rect.x1 -= shift
    if marker_rect.x0 < 5:
        marker_rect.x0 = 5
        marker_rect.x1 = 5 + label_w

    actual_mx = marker_rect.x0 + 1
    actual_my = marker_rect.y0 + marker_radius + 1

    try:
        shape = page.new_shape()

        # Draw filled red circle with issue number
        circle_center = fitz.Point(actual_mx + marker_radius, actual_my)
        shape.draw_circle(circle_center, marker_radius)
        shape.finish(color=box_color, fill=box_color, width=0.5)
        shape.commit()

        # White number text inside circle
        num_rect = fitz.Rect(
            actual_mx + 1, actual_my - marker_radius + 1,
            actual_mx + marker_radius * 2 - 1, actual_my + marker_radius - 1,
        )
        # Use insertTextbox for centered number
        page.insert_textbox(
            num_rect, marker_num,
            fontsize=8, fontname="helv",
            color=WHITE, align=1,  # center
        )

        # Short label text next to the circle
        label_rect = fitz.Rect(
            actual_mx + marker_radius * 2 + 3, actual_my - 6,
            marker_rect.x1, actual_my + 7,
        )
        page.insert_textbox(
            label_rect, f"NC-{marker_num}: {short_label}",
            fontsize=6.5, fontname="helv",
            color=box_color,
        )

        used_rects.append(marker_rect)

        # Draw connector line from marker to highlight box
        if area_rect.is_valid and area_rect.width > 2:
            line_start = fitz.Point(actual_mx + marker_radius, actual_my + marker_radius)
            ac_x = (area_rect.x0 + area_rect.x1) / 2
            ac_y = (area_rect.y0 + area_rect.y1) / 2

            # Pick closest edge point
            if actual_my + marker_radius < area_rect.y0:
                line_end = fitz.Point(ac_x, area_rect.y0)
            elif actual_my - marker_radius > area_rect.y1:
                line_start = fitz.Point(actual_mx + marker_radius, actual_my - marker_radius)
                line_end = fitz.Point(ac_x, area_rect.y1)
            elif actual_mx > area_rect.x1:
                line_start = fitz.Point(actual_mx, actual_my)
                line_end = fitz.Point(area_rect.x1, ac_y)
            else:
                line_start = fitz.Point(actual_mx + marker_radius * 2 + label_w, actual_my)
                line_end = fitz.Point(area_rect.x0, ac_y)

            dx = abs(line_start.x - line_end.x)
            dy = abs(line_start.y - line_end.y)
            if dx > 8 or dy > 8:
                shape2 = page.new_shape()
                shape2.draw_line(line_start, line_end)
                shape2.finish(color=box_color, width=0.8)
                shape2.commit()

    except Exception as e:
        logger.debug("Could not place marker for issue %d: %s", issue.issue_id, e)


def _add_legend_page(
    doc: fitz.Document,
    result: RedlineResult,
) -> None:
    """Add a clean legend page listing all issues in a table format."""
    # Use letter-size landscape for the legend
    legend_w, legend_h = 842, 595  # A4 landscape (points)
    page = doc.new_page(width=legend_w, height=legend_h)

    margin = 40
    y = margin

    # Title
    title = f"AI Redline Review — {result.label_name}"
    page.insert_textbox(
        fitz.Rect(margin, y, legend_w - margin, y + 24),
        title, fontsize=14, fontname="helv", color=(0, 0, 0),
    )
    y += 28

    # Subtitle
    subtitle = (
        f"Model: {result.ai_model}  |  "
        f"Product: {result.product_type}  |  "
        f"Issues: {len(result.issues)}  |  "
        f"Time: {result.analysis_time:.1f}s"
    )
    page.insert_textbox(
        fitz.Rect(margin, y, legend_w - margin, y + 14),
        subtitle, fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4),
    )
    y += 20

    # Summary
    if result.summary:
        page.insert_textbox(
            fitz.Rect(margin, y, legend_w - margin, y + 28),
            result.summary, fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3),
        )
        y += 32

    # Separator line
    shape = page.new_shape()
    shape.draw_line(fitz.Point(margin, y), fitz.Point(legend_w - margin, y))
    shape.finish(color=(0.7, 0.7, 0.7), width=0.5)
    shape.commit()
    y += 8

    # Column headers
    col_no = margin
    col_sev = margin + 25
    col_area = margin + 80
    col_desc = margin + 200
    col_ref = legend_w - margin - 160
    col_action = legend_w - margin - 60

    header_color = (0.2, 0.2, 0.2)
    page.insert_textbox(fitz.Rect(col_no, y, col_sev, y + 12), "#", fontsize=7, fontname="helv", color=header_color)
    page.insert_textbox(fitz.Rect(col_sev, y, col_area, y + 12), "Severity", fontsize=7, fontname="helv", color=header_color)
    page.insert_textbox(fitz.Rect(col_area, y, col_desc, y + 12), "Area", fontsize=7, fontname="helv", color=header_color)
    page.insert_textbox(fitz.Rect(col_desc, y, col_ref, y + 12), "Description", fontsize=7, fontname="helv", color=header_color)
    page.insert_textbox(fitz.Rect(col_ref, y, col_action, y + 12), "ISO Reference", fontsize=7, fontname="helv", color=header_color)
    page.insert_textbox(fitz.Rect(col_action, y, legend_w - margin, y + 12), "Action", fontsize=7, fontname="helv", color=header_color)
    y += 14

    # Separator
    shape = page.new_shape()
    shape.draw_line(fitz.Point(margin, y), fitz.Point(legend_w - margin, y))
    shape.finish(color=(0.8, 0.8, 0.8), width=0.3)
    shape.commit()
    y += 4

    # Issue rows — all non-conformances in red
    nc_color = RED

    for issue in result.issues:
        sev_color = nc_color

        # Calculate row height based on description length
        desc_text = issue.description
        if issue.current_text:
            desc_text += f"  [Current: {issue.current_text[:40]}]"
        if issue.corrected_text:
            desc_text += f"  [Fix: {issue.corrected_text[:40]}]"

        # Estimate lines needed
        desc_chars = len(desc_text)
        desc_col_width = col_ref - col_desc - 10
        chars_per_line = max(1, int(desc_col_width / 3.5))
        lines_needed = max(1, (desc_chars + chars_per_line - 1) // chars_per_line)
        row_h = max(14, lines_needed * 9 + 4)

        # Check if we need a new page
        if y + row_h > legend_h - 30:
            page = doc.new_page(width=legend_w, height=legend_h)
            y = margin
            # Re-draw headers
            page.insert_textbox(fitz.Rect(col_no, y, col_sev, y + 12), "#", fontsize=7, fontname="helv", color=header_color)
            page.insert_textbox(fitz.Rect(col_sev, y, col_area, y + 12), "Severity", fontsize=7, fontname="helv", color=header_color)
            page.insert_textbox(fitz.Rect(col_area, y, col_desc, y + 12), "Area", fontsize=7, fontname="helv", color=header_color)
            page.insert_textbox(fitz.Rect(col_desc, y, col_ref, y + 12), "Description", fontsize=7, fontname="helv", color=header_color)
            page.insert_textbox(fitz.Rect(col_ref, y, col_action, y + 12), "ISO Reference", fontsize=7, fontname="helv", color=header_color)
            page.insert_textbox(fitz.Rect(col_action, y, legend_w - margin, y + 12), "Action", fontsize=7, fontname="helv", color=header_color)
            y += 16

        # Row content
        page.insert_textbox(fitz.Rect(col_no, y, col_sev, y + row_h), str(issue.issue_id), fontsize=8, fontname="helv", color=sev_color)
        page.insert_textbox(fitz.Rect(col_sev, y, col_area, y + 12), "NC", fontsize=6.5, fontname="helv", color=sev_color)
        page.insert_textbox(fitz.Rect(col_area, y, col_desc, y + row_h), issue.area[:20], fontsize=7, fontname="helv", color=(0, 0, 0))
        page.insert_textbox(fitz.Rect(col_desc, y, col_ref - 5, y + row_h), desc_text, fontsize=7, fontname="helv", color=(0, 0, 0))
        page.insert_textbox(fitz.Rect(col_ref, y, col_action - 5, y + row_h), issue.iso_reference, fontsize=6.5, fontname="helv", color=(0.3, 0.3, 0.3))
        page.insert_textbox(fitz.Rect(col_action, y, legend_w - margin, y + row_h), issue.action, fontsize=7, fontname="helv", color=(0, 0, 0))

        y += row_h + 2

        # Light separator between rows
        shape = page.new_shape()
        shape.draw_line(fitz.Point(margin, y), fitz.Point(legend_w - margin, y))
        shape.finish(color=(0.9, 0.9, 0.9), width=0.2)
        shape.commit()
        y += 3


def _search_text_on_page(
    page: fitz.Page,
    current_text: str,
    element_ids: list[str],
    elem_map: dict[str, PDFElement],
) -> fitz.Rect | None:
    """Search for issue-related text on the PDF page to find exact position.

    Tries multiple search strategies in order of reliability:
    1. search_hint (AI-provided nearby label text — most reliable)
    2. Exact phrases from current_text
    3. Key words extracted from current_text
    4. Symbol-related keywords from description
    """
    if not current_text or len(current_text) < 3:
        return None

    # Build constraint region from element IDs
    constraint_rect = None
    if element_ids:
        for eid in element_ids:
            if eid in elem_map:
                elem = elem_map[eid]
                eb = fitz.Rect(*elem.bbox)
                expanded = fitz.Rect(eb.x0 - 30, eb.y0 - 30, eb.x1 + 30, eb.y1 + 30)
                if constraint_rect is None:
                    constraint_rect = expanded
                else:
                    constraint_rect = constraint_rect | expanded

    # Extract search terms from current_text
    search_terms = []

    # Try the full current_text first (up to 60 chars)
    clean = current_text.strip()
    if len(clean) > 3:
        search_terms.append(clean[:60])

    # Extract phone numbers, specific codes, or key phrases
    phone_match = re.search(r'\(?\d{3}\)?\s*[\-.]?\s*\d{3}[\-.]?\s*\d{4}', clean)
    if phone_match:
        search_terms.append(phone_match.group(0))

    # Extract ALL-CAPS words and significant words
    skip_words = {"the", "and", "for", "not", "with", "that", "this", "from",
                  "are", "was", "has", "but", "can", "should", "must", "will",
                  "symbol", "text", "label", "missing", "wrong", "incorrect",
                  "present", "shown", "appears", "current", "displayed"}
    words = re.findall(r'[A-Z][A-Z]+|\b\w{4,}\b', clean)
    for w in words:
        if w.lower() not in skip_words:
            search_terms.append(w)

    # Try searching for each term on the page
    for term in search_terms[:8]:  # try more terms
        try:
            rects = page.search_for(term, quads=False)
            if not rects:
                continue

            # If we have a constraint region, prefer matches inside it
            if constraint_rect is not None:
                for r in rects:
                    if constraint_rect.intersects(r):
                        return fitz.Rect(r.x0 - 4, r.y0 - 4, r.x1 + 4, r.y1 + 4)

            # No constraint or no match inside constraint — use first match
            r = rects[0]
            return fitz.Rect(r.x0 - 4, r.y0 - 4, r.x1 + 4, r.y1 + 4)
        except Exception:
            continue

    return None


def _search_by_hint(
    page: fitz.Page,
    search_hint: str,
    element_ids: list[str],
    elem_map: dict[str, PDFElement],
) -> fitz.Rect | None:
    """Search for the AI-provided search_hint text on the PDF page.

    The search_hint should contain exact text visible on the label near the issue.
    This is more reliable than current_text which often describes what's wrong
    rather than what's actually printed on the label.
    """
    if not search_hint or len(search_hint) < 2:
        return None

    # Build constraint region from element IDs
    constraint_rect = None
    if element_ids:
        for eid in element_ids:
            if eid in elem_map:
                elem = elem_map[eid]
                eb = fitz.Rect(*elem.bbox)
                expanded = fitz.Rect(eb.x0 - 30, eb.y0 - 30, eb.x1 + 30, eb.y1 + 30)
                if constraint_rect is None:
                    constraint_rect = expanded
                else:
                    constraint_rect = constraint_rect | expanded

    # Try the full hint, then progressively shorter fragments
    hints_to_try = [search_hint.strip()]

    # Split by common delimiters and try each part
    for part in re.split(r'[,;/|]', search_hint):
        part = part.strip()
        if len(part) >= 3:
            hints_to_try.append(part)

    # Also extract ALL-CAPS words (common on labels: LOT, REF, SN, STERILE, etc.)
    caps_words = re.findall(r'\b[A-Z]{2,}\b', search_hint)
    hints_to_try.extend(caps_words)

    for hint in hints_to_try[:10]:
        try:
            rects = page.search_for(hint, quads=False)
            if not rects:
                continue

            # Prefer matches inside constraint region
            if constraint_rect is not None:
                for r in rects:
                    if constraint_rect.intersects(r):
                        return fitz.Rect(r.x0 - 4, r.y0 - 4, r.x1 + 4, r.y1 + 4)

            # Use first match if no constraint
            r = rects[0]
            return fitz.Rect(r.x0 - 4, r.y0 - 4, r.x1 + 4, r.y1 + 4)
        except Exception:
            continue

    return None


def _resolve_area_rect(
    issue: RedlineIssue,
    elem_map: dict[str, PDFElement],
    pw: float,
    ph: float,
    page: fitz.Page | None = None,
) -> fitz.Rect:
    """Resolve the target highlight area from element IDs + sub-region.

    Position strategy (in order of accuracy):
    1. search_hint — AI-provided nearby label text → PDF text search → exact position
    2. current_text — text description of what's visible → PDF text search
    3. Element ID + sub-region percentages from AI (least accurate)
    4. Fallback: page-level percentage coordinates
    """

    # ── Strategy 1: search_hint text search (MOST ACCURATE) ──
    if page is not None and issue.search_hint:
        found_rect = _search_by_hint(page, issue.search_hint, issue.element_ids, elem_map)
        if found_rect is not None:
            logger.debug("Issue %d: positioned via search_hint '%s'",
                         issue.issue_id, issue.search_hint[:40])
            return found_rect

    # ── Strategy 2: current_text search ──
    if page is not None and issue.current_text:
        found_rect = _search_text_on_page(page, issue.current_text, issue.element_ids, elem_map)
        if found_rect is not None:
            logger.debug("Issue %d: positioned via current_text search for '%s'",
                         issue.issue_id, issue.current_text[:40])
            return found_rect

    # ── Strategy 3: Element ID + sub-region from AI ──
    matched_elems = []
    for eid in issue.element_ids:
        eid = eid.strip()
        if eid in elem_map:
            matched_elems.append(elem_map[eid])
        else:
            logger.debug("Element %s not found in map", eid)

    if matched_elems:
        # If a single image element with sub-region specified, use sub-region
        if (
            len(matched_elems) == 1
            and matched_elems[0].elem_type == "image"
            and issue.sub_w_pct < 0.95  # sub-region was specified (not full image)
        ):
            elem = matched_elems[0]
            ex0, ey0, ex1, ey1 = elem.bbox
            ew = ex1 - ex0
            eh = ey1 - ey0

            # Calculate sub-region center and size within the image
            cx = ex0 + issue.sub_x_pct * ew
            cy = ey0 + issue.sub_y_pct * eh
            sw = issue.sub_w_pct * ew
            sh = issue.sub_h_pct * eh

            # Clamp to element bounds
            rx0 = max(ex0, cx - sw / 2)
            ry0 = max(ey0, cy - sh / 2)
            rx1 = min(ex1, cx + sw / 2)
            ry1 = min(ey1, cy + sh / 2)

            # Ensure minimum size
            if rx1 - rx0 < 20:
                rx0 = max(ex0, cx - 15)
                rx1 = min(ex1, cx + 15)
            if ry1 - ry0 < 10:
                ry0 = max(ey0, cy - 8)
                ry1 = min(ey1, cy + 8)

            return fitz.Rect(rx0, ry0, rx1, ry1)

        # For text elements or multiple elements: union of bboxes
        bboxes = [e.bbox for e in matched_elems]
        x0 = min(b[0] for b in bboxes)
        y0 = min(b[1] for b in bboxes)
        x1 = max(b[2] for b in bboxes)
        y1 = max(b[3] for b in bboxes)

        # If all are image elements, apply sub-region to the union
        if all(e.elem_type == "image" for e in matched_elems) and issue.sub_w_pct < 0.95:
            ew = x1 - x0
            eh = y1 - y0
            cx = x0 + issue.sub_x_pct * ew
            cy = y0 + issue.sub_y_pct * eh
            sw = issue.sub_w_pct * ew
            sh = issue.sub_h_pct * eh
            return fitz.Rect(
                max(x0, cx - sw / 2),
                max(y0, cy - sh / 2),
                min(x1, cx + sw / 2),
                min(y1, cy + sh / 2),
            )

        return fitz.Rect(x0, y0, x1, y1)

    # Fallback: try to find elements by matching text content
    if issue.current_text:
        search_text = issue.current_text.lower()
        for elem in elem_map.values():
            if elem.elem_type == "text" and search_text[:20] in elem.content.lower():
                return fitz.Rect(*elem.bbox)

    # Last resort: use page-level percentage coordinates
    area_x = issue.x_pct * pw
    area_y = issue.y_pct * ph
    area_w = max(issue.width_pct * pw, 40)
    area_h = max(issue.height_pct * ph, 20)
    rect = fitz.Rect(
        max(5, area_x - area_w / 2),
        max(5, area_y - area_h / 2),
        min(pw - 5, area_x + area_w / 2),
        min(ph - 5, area_y + area_h / 2),
    )
    return rect



def _add_revision_note(
    page: fitz.Page,
    result: RedlineResult,
    pw: float,
    ph: float,
) -> None:
    """Add a small footer note."""
    note_text = f"AI Redline Review — {len(result.issues)} issues identified ({result.ai_model})"
    note_rect = fitz.Rect(pw - 380, ph - 22, pw - 10, ph - 5)
    try:
        annot = page.add_freetext_annot(
            note_rect, note_text,
            fontsize=7, fontname="helv",
            text_color=(0.5, 0.5, 0.5), fill_color=WHITE,
        )
        annot.set_opacity(0.8)
        annot.update()
    except Exception:
        pass


# ── Public API ─────────────────────────────────────
def run_ai_redline(
    pdf_path: Path,
    output_dir: Path | None = None,
) -> tuple[RedlineResult, Path | None]:
    """
    Complete AI redline pipeline:
    1. Extract real element positions from PDF
    2. Analyze label with GPT-4o vision + element map
    3. Generate annotated PDF with anchored annotations
    """
    logger.info("Starting AI redline analysis: %s", pdf_path.name)

    # Step 1+2: AI analysis with element coordinates
    result, elements = analyze_label_with_ai(pdf_path)

    if not result.issues:
        logger.warning("No issues found by AI analysis")
        return result, None

    # Step 3: Generate annotated PDF
    out_path = generate_ai_redline_pdf(pdf_path, result, elements, output_dir)

    # Step 4: Markdown report
    if out_path:
        _generate_redline_report(pdf_path, result)

    return result, out_path


def _generate_redline_report(
    pdf_path: Path,
    result: RedlineResult,
) -> Path | None:
    """Generate a markdown report of redline findings."""
    settings = get_settings()
    report_dir = settings.paths.report_dir
    report_dir.mkdir(parents=True, exist_ok=True)

    report_name = f"redline-report-{pdf_path.stem.replace(' ', '_')}.md"
    report_path = report_dir / report_name

    lines = [
        f"# AI Redline Report: {result.label_name}",
        "",
        f"**Analysis Model**: {result.ai_model}",
        f"**Analysis Time**: {result.analysis_time:.1f}s",
        f"**Total Non-Conformances**: {len(result.issues)}",
    ]

    if result.product_type:
        lines.append(f"**Product Type**: {result.product_type}")
    if result.applicable_standards:
        lines.append(f"**Applicable Standards**: {', '.join(result.applicable_standards)}")

    lines += [
        "",
        "## Summary",
        "",
        result.summary,
        "",
        "## Non-Conformances",
        "",
    ]

    for issue in result.issues:
        lines.append(f"**NC-{issue.issue_id}. {issue.description}**")
        lines.append(f"- Area: {issue.area}")
        lines.append(f"- Action: {issue.action}")
        lines.append(f"- ISO Reference: {issue.iso_reference}")
        if issue.element_ids:
            lines.append(f"- Elements: {', '.join(issue.element_ids)}")
        if issue.current_text:
            lines.append(f"- Current: `{issue.current_text}`")
        if issue.corrected_text:
            lines.append(f"- Corrected: `{issue.corrected_text}`")
        lines.append("")

    report_path.write_text("\n".join(lines))
    logger.info("Redline report saved: %s", report_path.name)
    return report_path
