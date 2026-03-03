"""
Label Segmenter
=================
Splits a multi-label PDF into individual label sections.

Many medical-device label PDFs contain multiple distinct labels on
a single page (or across pages):
  - COMBO LABEL (SET)
  - THERMOFORM LABEL
  - OUTER LID LABEL
  - PROCEDURE PACK
  - Inner label / Outer Lid Label / Box label / Patient label
  - Product info tables / matrices

This module detects those sections and extracts each one as a
separate segment — with its own text, bounding box, fonts, and
page reference — so each can be checked against ISO standards
independently.

Two approaches depending on PDF type:
  1. **DRWG files** (engineering drawings): Single-page PDFs with
     multiple labels spatially arranged. Uses PyMuPDF text block
     positions to find section headers and partition the page.
  2. **ARTW files** (artwork specs): Multi-page PDFs where each
     page often represents a different label. Uses page-level
     text to identify the section type.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import fitz  # PyMuPDF

from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

# ── Known section header patterns ─────────────────────
# Order matters — more specific patterns first
_SECTION_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("COMBO LABEL", re.compile(r"COMBO\s+LABEL", re.IGNORECASE)),
    ("THERMOFORM LABEL", re.compile(r"THERMOFORM\s+LABEL", re.IGNORECASE)),
    ("OUTER LID LABEL", re.compile(r"OUTER\s+LID\s+LABEL", re.IGNORECASE)),
    ("PROCEDURE PACK", re.compile(r"PROCEDURE\s+PACK", re.IGNORECASE)),
    ("INNER LABEL", re.compile(r"INNER\s+LABEL", re.IGNORECASE)),
    ("BOX LABEL", re.compile(r"BOX\s+LABEL", re.IGNORECASE)),
    ("PATIENT LABEL", re.compile(r"PATIENT\s+LABEL", re.IGNORECASE)),
    ("PATIENT CARD", re.compile(r"PATIENT\s+CARD", re.IGNORECASE)),
    ("UNIT LABEL", re.compile(r"UNIT\s+LABEL", re.IGNORECASE)),
    ("CARTON LABEL", re.compile(r"CARTON\s+LABEL", re.IGNORECASE)),
    ("TRAY LABEL", re.compile(r"TRAY\s+LABEL", re.IGNORECASE)),
    ("POUCH LABEL", re.compile(r"POUCH\s+LABEL", re.IGNORECASE)),
    ("IFU", re.compile(r"\bIFU\b", re.IGNORECASE)),
    # ARTW-style headers (slightly different naming)
    ("INNER LABEL", re.compile(r"Inner\s+label", re.IGNORECASE)),
    ("OUTER LID LABEL", re.compile(r"Outer\s+Lid\s+Label", re.IGNORECASE)),
    ("BOX LABEL", re.compile(r"Box\s+label", re.IGNORECASE)),
    ("PATIENT LABEL", re.compile(r"Patient\s+label", re.IGNORECASE)),
]

# Non-label sections (metadata, revision tables, title blocks)
_SKIP_PATTERNS = [
    re.compile(r"REVISIONS?$", re.IGNORECASE),
    re.compile(r"TITLE\s+BLOCK", re.IGNORECASE),
    re.compile(r"PROPRIETARY\s+AND\s+CONFIDENTIAL", re.IGNORECASE),
    re.compile(r"DO\s+NOT\s+SCALE", re.IGNORECASE),
    re.compile(r"TOLERANCES", re.IGNORECASE),
    re.compile(r"^NOTES?$", re.IGNORECASE),
    re.compile(r"^MATERIAL", re.IGNORECASE),
    re.compile(r"Labeling\s+Specification", re.IGNORECASE),
    re.compile(r"Product\s+Information.*Reference", re.IGNORECASE),
]


@dataclass
class LabelSection:
    """A single label section extracted from a multi-label PDF."""

    name: str  # e.g. "COMBO LABEL", "OUTER LID LABEL"
    section_type: str  # normalized type
    page_number: int  # 1-based page number
    bbox: tuple[float, float, float, float] | None = None  # (x0, y0, x1, y1) on page
    text: str = ""  # extracted text for this section
    fonts: list[dict] = field(default_factory=list)
    eart_number: str = ""  # EART reference if found
    has_matrix: bool = False  # whether this section has a data matrix/table
    # Per-section variable fields (REF, LOT, SN, MFGDATE, EXPDATE, etc.)
    variable_fields: list[str] = field(default_factory=list)
    # Character limits extracted from the section (e.g. {"LOTNO": 11, "SERNO": 10})
    character_limits: dict[str, int] = field(default_factory=dict)
    # Barcode content specs (e.g. "01(TK20)+17(EXPDATE)+11(MFGDATE)+10(LOTNO)+21(SERNO)")
    barcode_specs: list[str] = field(default_factory=list)
    # Regulatory symbol placeholders detected in this section
    regulatory_symbols: list[str] = field(default_factory=list)
    # Manufacturing / inspection notes found in this section
    manufacturing_notes: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        """Short identifier for logging."""
        return f"P{self.page_number}-{self.section_type}"


@dataclass
class DrawingMetadata:
    """Engineering drawing title block metadata."""
    drawing_number: str = ""
    revision: str = ""
    title: str = ""
    scale: str = ""
    material: str = ""
    finish: str = ""
    drawn_by: str = ""
    approved_by: str = ""
    print_date: str = ""
    tolerance_standard: str = ""  # e.g. "ASME Y14.5"
    tolerances: dict[str, str] = field(default_factory=dict)  # e.g. {".XX": ".01"}
    sheet_info: str = ""  # e.g. "SHEET 1 OF 1"
    plm_reference: str = ""


@dataclass
class RevisionEntry:
    """A single revision history entry."""
    rev: str = ""
    change_order: str = ""
    description: str = ""
    drawn_by: str = ""
    date: str = ""


@dataclass
class ConfigurationRow:
    """A single row from the product configuration matrix."""
    item_number: str = ""
    shelf_life_days: str = ""
    nom_volume: str = ""
    max_volume: str = ""
    diameter: str = ""
    height: str = ""
    projection: str = ""
    width: str = ""
    gtin: str = ""
    label_item_pn: str = ""
    extra: dict[str, str] = field(default_factory=dict)  # overflow columns


@dataclass
class SegmentationResult:
    """Result of segmenting a PDF into label sections."""

    pdf_path: Path
    total_pages: int
    sections: list[LabelSection] = field(default_factory=list)
    matrix_data: dict = field(default_factory=dict)  # shared product matrix data

    # ── Drawing-level metadata ──
    drawing_metadata: DrawingMetadata | None = None
    revision_history: list[RevisionEntry] = field(default_factory=list)
    variable_definitions: dict[str, str] = field(default_factory=dict)  # e.g. {"LOTNO": "LOT NUMBER"}
    character_limits: list[dict[str, str]] = field(default_factory=list)  # [{"field": "LOTNO", "max_chars": 11}]
    configuration_matrix: list[ConfigurationRow] = field(default_factory=list)
    manufacturing_notes: list[str] = field(default_factory=list)
    barcode_content_specs: list[str] = field(default_factory=list)  # e.g. "01(TK20)+17(EXPDATE)..."

    @property
    def section_count(self) -> int:
        return len(self.sections)

    @property
    def section_names(self) -> list[str]:
        return [s.name for s in self.sections]


def segment_pdf(pdf_path: Path) -> SegmentationResult:
    """
    Segment a label PDF into individual label sections.

    Analyzes the PDF structure to identify distinct labels
    (COMBO LABEL, OUTER LID, THERMOFORM, etc.) and extracts
    each as a separate LabelSection with its own text and position.

    For image-only pages (no extractable vector text), this module
    extracts embedded images, runs OCR on them, and uses the OCR
    text for section detection and analysis.

    Args:
        pdf_path: Path to the label PDF.

    Returns:
        SegmentationResult with list of detected LabelSections.
    """
    from label_compliance.document.image_extractor import (
        classify_pdf_pages,
        extract_and_ocr_embedded_images,
    )
    from label_compliance.config import get_settings
    from label_compliance.utils.helpers import safe_filename

    pdf_path = Path(pdf_path)
    logger.info("Segmenting PDF: %s", pdf_path.name)

    # ── Pre-classify pages: IMAGE_ONLY / MIXED / TEXT_ONLY ──
    pdf_analysis = classify_pdf_pages(pdf_path)

    # ── For image-only or mixed pages, extract embedded images + OCR ──
    embedded_ocr_texts: dict[int, str] = {}
    image_pages = pdf_analysis.image_only_pages + pdf_analysis.mixed_pages
    if image_pages:
        settings = get_settings()
        safe_name = safe_filename(pdf_path.stem)
        embed_dir = settings.paths.knowledge_base_dir.parent / "images" / safe_name / "embedded"
        embedded_ocr_texts = extract_and_ocr_embedded_images(
            pdf_path, embed_dir, pages=image_pages,
        )
        logger.info(
            "  Embedded image OCR for pages %s: %s",
            image_pages,
            {p: f"{len(t)} chars" for p, t in embedded_ocr_texts.items()},
        )

    doc = fitz.open(str(pdf_path))
    result = SegmentationResult(pdf_path=pdf_path, total_pages=len(doc))

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_num = page_idx + 1

        # Get page classification
        page_class = pdf_analysis.page_classifications[page_idx]

        # Get structured text with positions
        text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        blocks = text_dict.get("blocks", [])
        page_text = page.get_text()

        # For image-only pages, use OCR text instead
        if page_class.is_image_only:
            ocr_text = embedded_ocr_texts.get(page_num, "")
            logger.info(
                "  Page %d is IMAGE_ONLY — using OCR text (%d chars)",
                page_num, len(ocr_text),
            )
            # Use OCR text for section detection
            effective_text = ocr_text
        else:
            effective_text = page_text
            # For mixed pages, augment with embedded image OCR
            if page_class.page_type == "MIXED" and page_num in embedded_ocr_texts:
                extra_text = embedded_ocr_texts[page_num]
                if extra_text.strip():
                    effective_text = page_text + "\n" + extra_text

        # Find section headers with positions (only works for vector text)
        header_hits = _find_section_headers(blocks, page_num)

        # For image-only pages with no header hits, try finding headers in OCR text
        if not header_hits and page_class.is_image_only and effective_text:
            header_hits = _find_section_headers_from_text(effective_text, page_num, page)

        if header_hits:
            # Partition page into sections based on header positions
            sections = _partition_page_by_headers(
                header_hits, blocks, page, page_num
            )
            # For image-only pages, inject OCR text into sections
            if page_class.is_image_only:
                for sec in sections:
                    if not sec.text.strip() and effective_text:
                        sec.text = effective_text
            result.sections.extend(sections)
        else:
            # No headers found — treat entire page as one section
            section_type = _infer_page_type(effective_text, page_num, len(doc))
            section = LabelSection(
                name=section_type,
                section_type=_normalize_type(section_type),
                page_number=page_num,
                bbox=(0, 0, page.rect.width, page.rect.height),
                text=effective_text,
                fonts=_extract_page_fonts(page),
            )
            result.sections.append(section)

    # Extract shared matrix data (product tables)
    result.matrix_data = _extract_matrix_data(doc)

    # ── Extract drawing-level metadata ──
    full_text = "\n".join(page.get_text() for page in doc)
    result.drawing_metadata = _extract_drawing_metadata(doc)
    result.revision_history = _extract_revision_history(doc)
    result.variable_definitions = _extract_variable_definitions(full_text)
    result.character_limits = _extract_character_limits(full_text)
    result.configuration_matrix = _extract_configuration_matrix(doc)
    result.manufacturing_notes = _extract_manufacturing_notes(full_text)
    result.barcode_content_specs = _extract_barcode_specs(full_text)

    # ── Enrich each section ──
    for section in result.sections:
        _enrich_section(section)

    doc.close()

    # Log summary
    logger.info(
        "  Segmented into %d sections: %s",
        result.section_count,
        ", ".join(result.section_names),
    )
    if result.drawing_metadata:
        dm = result.drawing_metadata
        logger.info(
            "  Drawing: %s Rev %s — %s",
            dm.drawing_number, dm.revision, dm.title,
        )
    if result.configuration_matrix:
        logger.info("  Configuration matrix: %d product rows", len(result.configuration_matrix))
    if result.revision_history:
        logger.info("  Revision history: %d entries", len(result.revision_history))
    if result.variable_definitions:
        logger.info("  Variable definitions: %d fields", len(result.variable_definitions))
    if result.barcode_content_specs:
        logger.info("  Barcode content specs: %s", result.barcode_content_specs)

    return result


def _find_section_headers(
    blocks: list[dict], page_num: int
) -> list[tuple[str, str, tuple[float, float, float, float]]]:
    """
    Find section header text blocks and their positions.

    Returns list of (header_name, section_type, bbox) tuples.
    """
    hits = []
    seen_types = set()

    for block in blocks:
        if block.get("type") != 0:  # text blocks only
            continue

        bbox = block["bbox"]

        for line in block.get("lines", []):
            line_text = "".join(
                span.get("text", "") for span in line.get("spans", [])
            ).strip()

            if not line_text or len(line_text) > 80:
                continue

            # Skip non-label sections
            if any(pat.search(line_text) for pat in _SKIP_PATTERNS):
                continue

            # Check against known section patterns
            for section_name, pattern in _SECTION_PATTERNS:
                if pattern.search(line_text):
                    norm_type = _normalize_type(section_name)
                    # Avoid duplicates of the same type on the same page
                    key = f"{page_num}-{norm_type}"
                    if key not in seen_types:
                        seen_types.add(key)
                        hits.append((section_name, norm_type, bbox))
                    break

    return hits


def _find_section_headers_from_text(
    ocr_text: str,
    page_num: int,
    page: fitz.Page,
) -> list[tuple[str, str, tuple[float, float, float, float]]]:
    """
    Find section headers from OCR text (for image-only pages).

    When a page has no vector text blocks, we can't get bounding boxes
    for headers. Instead, search the OCR text for section header patterns
    and assign approximate positions based on the page layout.

    Returns list of (header_name, section_type, bbox) tuples.
    """
    hits = []
    seen_types = set()
    pw, ph = page.rect.width, page.rect.height

    for line in ocr_text.split("\n"):
        line = line.strip()
        if not line or len(line) > 80:
            continue

        # Skip non-label sections
        if any(pat.search(line) for pat in _SKIP_PATTERNS):
            continue

        # Check against known section patterns
        for section_name, pattern in _SECTION_PATTERNS:
            if pattern.search(line):
                norm_type = _normalize_type(section_name)
                key = f"{page_num}-{norm_type}"
                if key not in seen_types:
                    seen_types.add(key)
                    # Use full page bbox since we don't have exact positions
                    hits.append((section_name, norm_type, (0, 0, pw, ph)))
                break

    return hits


def _partition_page_by_headers(
    headers: list[tuple[str, str, tuple[float, float, float, float]]],
    blocks: list[dict],
    page: fitz.Page,
    page_num: int,
) -> list[LabelSection]:
    """
    Partition a page into sections based on header positions.

    Uses header x-positions to divide the page into columns/regions,
    then assigns text blocks to the nearest section.
    """
    if not headers:
        return []

    pw, ph = page.rect.width, page.rect.height

    # Sort headers by position (left-to-right, then top-to-bottom)
    headers_sorted = sorted(headers, key=lambda h: (h[2][0], h[2][1]))

    sections: list[LabelSection] = []

    for i, (name, norm_type, hdr_bbox) in enumerate(headers_sorted):
        # Define section region based on header position
        # Heuristic: section extends from this header to the next header
        hx0, hy0, hx1, hy1 = hdr_bbox

        # Section left boundary: slightly left of header
        sx0 = max(0, hx0 - 50)
        # Section top: slightly above header
        sy0 = max(0, hy0 - 30)

        # Section right boundary: next header's left edge or page edge
        sx1 = pw
        # Section bottom: next header's top or page bottom
        sy1 = ph

        for j, (_, _, next_bbox) in enumerate(headers_sorted):
            if j <= i:
                continue
            nx0, ny0 = next_bbox[0], next_bbox[1]

            # If next header is to the right, limit our right edge
            if nx0 > hx1 + 50 and abs(ny0 - hy0) < 200:
                sx1 = min(sx1, nx0 - 10)
            # If next header is below, limit our bottom edge
            elif ny0 > hy1 + 50:
                sy1 = min(sy1, ny0 - 10)

        # Collect text blocks within this section's region
        section_text_parts = []
        section_fonts = []

        for block in blocks:
            if block.get("type") != 0:
                continue

            bx0, by0, bx1, by1 = block["bbox"]
            # Check if block center is within section region
            bcx = (bx0 + bx1) / 2
            bcy = (by0 + by1) / 2

            if sx0 <= bcx <= sx1 and sy0 <= bcy <= sy1:
                for line in block.get("lines", []):
                    line_text = "".join(
                        span.get("text", "") for span in line.get("spans", [])
                    )
                    section_text_parts.append(line_text)

                    for span in line.get("spans", []):
                        section_fonts.append({
                            "name": span.get("font", "unknown"),
                            "size": round(span.get("size", 0), 1),
                            "flags": span.get("flags", 0),
                        })

        # Find EART number if present
        section_text = "\n".join(section_text_parts)
        eart_match = re.search(r"\[EART\s+([\w-]+)\]", section_text)
        eart_number = eart_match.group(1) if eart_match else ""

        section = LabelSection(
            name=name,
            section_type=norm_type,
            page_number=page_num,
            bbox=(sx0, sy0, sx1, sy1),
            text=section_text,
            fonts=section_fonts,
            eart_number=eart_number,
        )
        sections.append(section)

    return sections


def _infer_page_type(text: str, page_num: int, total_pages: int) -> str:
    """Infer the section type for a page with no explicit header."""
    text_upper = text.upper()

    # Check for known content patterns
    if "PATIENT" in text_upper and ("CARD" in text_upper or "LABEL" in text_upper):
        return "PATIENT LABEL"
    if "INNER" in text_upper and "LABEL" in text_upper:
        return "INNER LABEL"
    if "OUTER" in text_upper and ("LID" in text_upper or "LABEL" in text_upper):
        return "OUTER LID LABEL"
    if "PRODUCT INFORMATION" in text_upper or "REFERENCE ONLY" in text_upper:
        return "PRODUCT INFO"
    if "IFU" in text_upper or "INSTRUCTIONS FOR USE" in text_upper:
        return "IFU"

    # For multi-page ARTW files, page position gives clues
    if total_pages >= 3:
        if page_num == 1:
            return "COVER PAGE"
        elif page_num == 2:
            return "LABEL ARTWORK"
        elif page_num == total_pages:
            return "PRODUCT INFO"

    return f"PAGE {page_num}"


def _normalize_type(name: str) -> str:
    """Normalize section type to a standard key."""
    name_upper = name.upper().strip()

    if "COMBO" in name_upper:
        return "combo_label"
    if "THERMOFORM" in name_upper:
        return "thermoform_label"
    if "OUTER" in name_upper and "LID" in name_upper:
        return "outer_lid_label"
    if "PROCEDURE" in name_upper:
        return "procedure_pack"
    if "INNER" in name_upper:
        return "inner_label"
    if "BOX" in name_upper:
        return "box_label"
    if "PATIENT" in name_upper and "CARD" in name_upper:
        return "patient_card"
    if "PATIENT" in name_upper:
        return "patient_label"
    if "UNIT" in name_upper:
        return "unit_label"
    if "CARTON" in name_upper:
        return "carton_label"
    if "TRAY" in name_upper:
        return "tray_label"
    if "POUCH" in name_upper:
        return "pouch_label"
    if "IFU" in name_upper:
        return "ifu"
    if "PRODUCT" in name_upper and "INFO" in name_upper:
        return "product_info"
    if "COVER" in name_upper:
        return "cover_page"
    if "LABEL" in name_upper and "ARTWORK" in name_upper:
        return "label_artwork"

    return name.lower().replace(" ", "_")


def _extract_page_fonts(page: fitz.Page) -> list[dict]:
    """Extract font info from a page."""
    fonts = []
    try:
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        for block in blocks:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    fonts.append({
                        "name": span.get("font", "unknown"),
                        "size": round(span.get("size", 0), 1),
                        "flags": span.get("flags", 0),
                    })
    except Exception:
        pass
    return fonts


def _extract_matrix_data(doc: fitz.Document) -> dict:
    """
    Extract the product matrix / data table that lists all variants.

    These tables contain item numbers, volumes, dimensions, GTINs, etc.
    They're shared across all label sections in the drawing.
    """
    matrix = {}

    for page in doc:
        text = page.get_text()
        lines = text.split("\n")

        # Look for matrix header row patterns
        for i, line in enumerate(lines):
            if re.search(r"Item\s+Number.*Shelf", line, re.IGNORECASE):
                # Found a matrix header — parse subsequent rows
                matrix["header_line"] = i
                matrix["found"] = True
                break
            elif re.search(r"GTIN", line) and re.search(r"Volume|Diameter", text, re.IGNORECASE):
                matrix["has_gtin"] = True

        # Extract EART references
        earts = re.findall(r"\[EART\s+([\w-]+)\]", text)
        if earts:
            matrix["eart_refs"] = list(set(earts + matrix.get("eart_refs", [])))

    return matrix


# ══════════════════════════════════════════════════════════
#  Drawing-level metadata extraction
# ══════════════════════════════════════════════════════════


def _extract_drawing_metadata(doc: fitz.Document) -> DrawingMetadata:
    """
    Extract the engineering title block:
    Drawing Number, Revision, Title, Scale, Tolerances, etc.

    Uses both raw text regex AND pdfplumber tables for accuracy.
    """
    dm = DrawingMetadata()

    # ── Collect all page text ──
    all_text = ""
    for page in doc:
        all_text += page.get_text() + "\n"

    # ── Title: LABELS, ARTOURA, ... NON-CE  ──
    # Look for the characteristic multi-line title
    m = re.search(
        r"(LABELS?,\s*[A-Z][A-Z ,]+(?:\n[A-Z, -]+)*)",
        all_text, re.MULTILINE,
    )
    if m:
        dm.title = " ".join(m.group(1).split())

    # ── Drawing number from title block row: "107602 \n D" ──
    # The drawing number and revision typically appear together
    m = re.search(r"\b(\d{6})\s*\n\s*([A-E])\s*\n", all_text)
    if m:
        dm.drawing_number = m.group(1)
        dm.revision = m.group(2)

    # Fallback: "DWG. NO." label
    if not dm.drawing_number:
        m = re.search(r"DWG\.?\s*NO\.?\s*[:\s]*(\d{5,7})", all_text, re.IGNORECASE)
        if m:
            dm.drawing_number = m.group(1)

    # Fallback revision: last "D\s+100969569\s+REVISED" pattern in revision table
    if not dm.revision:
        revs = re.findall(r"^([A-E])\s+(?:SEE PLM|\d+)\s+REVISED", all_text, re.MULTILINE)
        if revs:
            dm.revision = revs[-1]  # latest revision

    # ── Scale ──
    m = re.search(r"SCALE:\s*([\d:]+)", all_text, re.IGNORECASE)
    if m:
        dm.scale = m.group(1)

    # ── Material / Finish — from title block table labels ──
    m = re.search(r"MATERIAL\s*\n\s*(\S+)", all_text)
    if m:
        val = m.group(1).strip()
        if val.upper() not in ("FINISH", "N/A"):
            dm.material = val
        else:
            dm.material = "N/A"
    m = re.search(r"FINISH\s*\n\s*(\S+)", all_text)
    if m:
        val = m.group(1).strip()
        if val.upper() not in ("DRAWN", "REV"):
            dm.finish = val
        else:
            dm.finish = "N/A"

    # ── Drawn by: look for "DRAWN BY:" then scan nearby lines for author ──
    m = re.search(r"DRAWN\s+BY:\s*\n", all_text, re.IGNORECASE)
    if m:
        # The author name may not be immediately after DRAWN BY: due to
        # PyMuPDF block ordering. Scan the next ~100 chars for a short name.
        vicinity = all_text[m.end():m.end() + 150]
        skip = {"SCALE", "TITLE", "DATE", "REV", "SIZE", "MATERIAL", "FINISH",
                "DWG", "SHEET", "APPROVED", "PROJECTION", "TOLERANCES", "ANY",
                "N/A", "DO", "PROPRIETARY", "SEE", "LABELS"}
        for line in vicinity.split("\n"):
            candidate = line.strip()
            if not candidate or len(candidate) < 2 or len(candidate) > 12:
                continue
            # Check it looks like a person's name/initials (2-10 alpha chars)
            if re.match(r"^[A-Za-z]{2,10}$", candidate):
                if candidate.upper() not in skip:
                    dm.drawn_by = candidate
                    break

    # ── Approved by ──
    m = re.search(r"APPROVED\s+BY:\s*\n", all_text, re.IGNORECASE)
    if m:
        vicinity = all_text[m.end():m.end() + 200]
        skip_starts = {"LABELS", "LABEL", "NON-", "TITLE", "DWG", "SHEET", "DO ", "PROPRIETARY"}
        for line in vicinity.split("\n"):
            candidate = line.strip()
            if not candidate or len(candidate) < 2:
                continue
            up = candidate.upper()
            # Skip title/label text and drawing number
            if any(up.startswith(s) for s in skip_starts):
                continue
            if re.match(r"^\d{5,7}$", candidate):  # skip drawing numbers
                continue
            if re.match(r"^[A-E]$", candidate):  # skip revision letters
                continue
            if len(candidate) < 50:
                dm.approved_by = candidate
                break

    # ── Print date ──
    m = re.search(r"Printed\s+on\s+(\d{1,2}/\d{1,2}/\d{4})", all_text)
    if m:
        dm.print_date = m.group(1)

    # ── Tolerance standard (ASME Y14.5) ──
    m = re.search(r"(ASME\s+Y\d+\.\d+)", all_text, re.IGNORECASE)
    if m:
        dm.tolerance_standard = m.group(1)

    # ── Tolerances: .XX = .01, .XXX = .005, etc. ──
    for tmatch in re.finditer(r"\.([X]+)\s*=\s*([.\d]+)", all_text):
        dm.tolerances[f".{tmatch.group(1)}"] = tmatch.group(2)
    m = re.search(r"ANGULAR\s*=\s*([\d.]+)\s*DEGREES", all_text, re.IGNORECASE)
    if m:
        dm.tolerances["ANGULAR"] = f"{m.group(1)} DEGREES"
    m = re.search(r"FRACTIONAL\s*=\s*([\d/]+)", all_text, re.IGNORECASE)
    if m:
        dm.tolerances["FRACTIONAL"] = m.group(1)

    # ── Sheet info ──
    m = re.search(r"SHEET\s+(\d+)\s+OF\s+(\d+)", all_text, re.IGNORECASE)
    if m:
        dm.sheet_info = f"SHEET {m.group(1)} OF {m.group(2)}"

    # ── PLM reference ──
    if "SEE PLM SYSTEM" in all_text.upper():
        dm.plm_reference = "SEE PLM SYSTEM"

    return dm


def _extract_revision_history(doc: fitz.Document) -> list[RevisionEntry]:
    """
    Extract revision history table (Rev A, B, C, D with C.O. numbers).
    """
    revisions = []

    try:
        import pdfplumber
        pdf = pdfplumber.open(str(doc.name))
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or not table[0]:
                    continue
                # Find revision table by header pattern
                header_text = " ".join(str(c) for c in table[0] if c).upper()
                if "REV" in header_text and ("C.O." in header_text or "DESCRIPTION" in header_text):
                    for row in table[1:]:
                        if not row or not row[0]:
                            continue
                        rev_letter = str(row[0]).strip()
                        if not rev_letter or len(rev_letter) > 3:
                            continue
                        entry = RevisionEntry(rev=rev_letter)
                        if len(row) > 1 and row[1]:
                            entry.change_order = str(row[1]).strip()
                        if len(row) > 2 and row[2]:
                            entry.description = str(row[2]).strip()
                        if len(row) > 3 and row[3]:
                            entry.drawn_by = str(row[3]).strip()
                        if len(row) > 4 and row[4]:
                            entry.date = str(row[4]).strip()
                        revisions.append(entry)
        pdf.close()
    except Exception as e:
        logger.debug("Could not extract revision history via pdfplumber: %s", e)

        # Fallback: regex from raw text
        for page in doc:
            text = page.get_text()
            for m in re.finditer(
                r"^([A-E])\s+(SEE PLM|\d+)\s+(.*?)(?:\s+(\w{2,5})\s+(SEE PLM|[\d/]+))?$",
                text, re.MULTILINE,
            ):
                revisions.append(RevisionEntry(
                    rev=m.group(1),
                    change_order=m.group(2),
                    description=m.group(3).strip(),
                    drawn_by=m.group(4) or "",
                    date=m.group(5) or "",
                ))

    return revisions


def _extract_variable_definitions(text: str) -> dict[str, str]:
    """
    Extract variable field definitions like:
      LOTNO = LOT NUMBER
      SERNO = SERIAL NUMBER
      MFGDATE = MANUFACTURING DATE
    """
    definitions = {}

    for m in re.finditer(
        r"(\b[A-Z]{2,}(?:NO|DATE|NBR|CODE)?\b)\s*=\s*([A-Z][A-Z /]+)",
        text,
    ):
        key = m.group(1).strip()
        val = m.group(2).strip()
        if len(key) >= 3 and len(val) >= 3:
            definitions[key] = val

    return definitions


def _extract_character_limits(text: str) -> list[dict[str, str]]:
    """
    Extract 'NO. OF MAXIMUM SPACES (CHARACTERS)' block.

    Returns list of dicts with max character counts.
    """
    limits = []

    m = re.search(
        r"(?:NO\.\s*OF\s*)?MAXIMUM\s+SPACES?\s*\(CHARACTERS?\)",
        text, re.IGNORECASE,
    )
    if m:
        # Extract numbers that follow the header
        after_header = text[m.end():m.end() + 200]
        nums = re.findall(r"\b(\d{2,3})\b", after_header)
        for i, n in enumerate(nums[:10]):  # cap at 10
            limits.append({"position": str(i + 1), "max_chars": n})

    return limits


def _extract_configuration_matrix(doc: fitz.Document) -> list[ConfigurationRow]:
    """
    Extract the product configuration matrix table using pdfplumber.

    This table contains item numbers, shelf life, volumes, dimensions, GTINs.
    The table typically has a double header (TK variable mapping + column names)
    with data rows below.
    """
    rows = []

    try:
        import pdfplumber
        pdf = pdfplumber.open(str(doc.name))

        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 3:
                    continue

                # Find the header row with physical column names
                # (Item Number, Shelf Life, Volume, Diameter, Height, GTIN, etc.)
                # Must distinguish from "2nd Item Number" row which is a TK mapping header
                header_row = None
                header_idx = -1
                for ridx, row in enumerate(table[:5]):
                    row_text = " ".join(
                        str(c).replace("\n", " ") for c in row if c
                    ).upper()
                    # The real header row has BOTH "ITEM" and physical columns
                    # (DIAMETER or HEIGHT or GTIN). The "2nd Item Number" row
                    # only has "TEXT LINE" columns.
                    has_item = "ITEM" in row_text
                    has_physical = any(
                        kw in row_text for kw in ("DIAMETER", "HEIGHT", "GTIN", "PROJECTION")
                    )
                    if has_item and has_physical:
                        header_row = row
                        header_idx = ridx
                        break

                if header_row is None:
                    continue

                # Map column positions — normalize newlines in header cells
                col_map = {}
                for ci, cell in enumerate(header_row):
                    if not cell:
                        continue
                    ctext = str(cell).replace("\n", " ").upper().strip()
                    if "ITEM" in ctext and "NUMBER" in ctext:
                        col_map["item_number"] = ci
                    elif "SHELF" in ctext:
                        col_map["shelf_life_days"] = ci
                    elif "NOM" in ctext and "VOL" in ctext:
                        col_map["nom_volume"] = ci
                    elif "MAX" in ctext and "VOL" in ctext:
                        col_map["max_volume"] = ci
                    elif "DIAMETER" in ctext:
                        col_map["diameter"] = ci
                    elif "HEIGHT" in ctext:
                        col_map["height"] = ci
                    elif "PROJECTION" in ctext and "MAX" not in ctext:
                        col_map["projection"] = ci
                    elif "MAX" in ctext and "PROJECTION" in ctext:
                        col_map["extra_max_projection"] = ci
                    elif "WIDTH" in ctext:
                        col_map["width"] = ci
                    elif "GTIN" in ctext:
                        col_map["gtin"] = ci
                    elif "LABEL" in ctext and "P/N" in ctext:
                        col_map["label_item_pn"] = ci
                    elif "SALINE" in ctext:
                        col_map["extra_saline_vol"] = ci
                    elif "GEL" in ctext and "VOL" in ctext:
                        col_map["extra_gel_volume"] = ci
                    elif "TOLERANCE" in ctext:
                        col_map["extra_tolerance"] = ci

                if not col_map:
                    continue

                # Parse data rows (after header)
                for data_row in table[header_idx + 1:]:
                    if not data_row or not data_row[0]:
                        continue
                    first_cell = str(data_row[0]).strip()
                    # Skip empty, dash, or header-like rows
                    if not first_cell or first_cell == "-":
                        continue
                    if first_cell.upper() in ("ITEM", "NUMBER", "2ND", "TEXT"):
                        continue

                    cr = ConfigurationRow()
                    extras = {}
                    for attr, ci in col_map.items():
                        if ci < len(data_row) and data_row[ci]:
                            val = str(data_row[ci]).strip()
                            if val == "-":
                                val = ""
                            if attr.startswith("extra_"):
                                extras[attr.replace("extra_", "")] = val
                            else:
                                setattr(cr, attr, val)

                    # Store overflow columns
                    cr.extra = extras

                    # If no item_number column was mapped, use first cell
                    if not cr.item_number and first_cell:
                        cr.item_number = first_cell

                    if cr.item_number:
                        rows.append(cr)

        pdf.close()
    except Exception as e:
        logger.debug("Could not extract configuration matrix via pdfplumber: %s", e)

    return rows


def _extract_manufacturing_notes(text: str) -> list[str]:
    """
    Extract manufacturing / inspection notes:
    - FIRST ARTICLE INSPECT PER QCIC000001
    - MFG INSPECT PER QCIC00000163
    - DO NOT SCALE DRAWING
    - etc.
    """
    notes = []
    patterns = [
        re.compile(r"FIRST\s+ARTICLE\s+INSPECT\s+PER\s+\S+", re.IGNORECASE),
        re.compile(r"MFG\s+INSPECT\s+PER\s+\S+", re.IGNORECASE),
        re.compile(r"DO\s+NOT\s+SCALE\s+DRAWING", re.IGNORECASE),
        re.compile(r"ALL\s+OF\s+THE\s+VARIABLE\s+TEXT\s+IS\s+DISPLAYED\s+AS\s+ITS\s+FIELD\s+NAME", re.IGNORECASE),
        re.compile(
            r"THE\s+SPECIFIC\s+DATA\s+TO\s+BE\s+INSERTED.*?DOCUMENTATION\s+CONFIGURATION",
            re.IGNORECASE | re.DOTALL,
        ),
        re.compile(r"2D\s+barcode\s+contains\s*:?\s*[\w()+\s]+", re.IGNORECASE),
    ]
    for pat in patterns:
        m = pat.search(text)
        if m:
            notes.append(m.group(0).strip()[:200])

    return notes


def _extract_barcode_specs(text: str) -> list[str]:
    """
    Extract 2D barcode content specifications like:
      01(TK20)+17(EXPDATE)+11(MFGDATE)+10(LOTNO)+21(SERNO)
    """
    specs = []

    # Pattern: 01(...)+17(...)+... style barcode element specs
    for m in re.finditer(
        r"\d{2}\([A-Z0-9]+\)(?:\s*\+\s*\d{2}\([A-Z0-9]+\)){1,10}",
        text, re.IGNORECASE,
    ):
        # Normalize whitespace/newlines to single spaces
        spec = re.sub(r"\s+", "", m.group(0).strip())
        if spec not in specs:
            specs.append(spec)

    return specs


def _enrich_section(section: LabelSection) -> None:
    """
    Enrich a LabelSection with parsed variable fields, symbol references,
    character limits, barcode specs, and manufacturing notes from its text.
    """
    text = section.text

    # ── Variable fields ──
    # Look for field placeholders: LOTNO, SERNO, REF, LOT, SN, MFGDATE, EXPDATE, LPNBR
    known_vars = [
        "LOTNO", "SERNO", "MFGDATE", "EXPDATE", "LPNBR",
        "REF", "LOT", "SN", "EXPIRY", "MFG",
        "TK01", "TK02", "TK03", "TK04", "TK05",
        "TK06", "TK07", "TK08", "TK09", "TK10",
        "TK11", "TK20",
    ]
    found_vars = []
    for var in known_vars:
        if re.search(r"\b" + re.escape(var) + r"\b", text, re.IGNORECASE):
            found_vars.append(var)
    section.variable_fields = found_vars

    # ── Character limits ──
    m = re.search(
        r"(?:NO\.\s*OF\s*)?MAXIMUM\s+SPACES?\s*\(CHARACTERS?\)",
        text, re.IGNORECASE,
    )
    if m:
        after = text[m.end():m.end() + 200]
        nums = re.findall(r"\b(\d{2,3})\b", after)
        for i, n in enumerate(nums[:10]):
            section.character_limits[f"field_{i+1}"] = int(n)

    # ── Barcode specs ──
    for m in re.finditer(
        r"\d{2}\([A-Z0-9]+\)(?:\s*\+\s*\d{2}\([A-Z0-9]+\)){1,10}",
        text, re.IGNORECASE,
    ):
        spec = re.sub(r"\s+", "", m.group(0).strip())
        if spec not in section.barcode_specs:
            section.barcode_specs.append(spec)

    # ── Regulatory symbols ──
    symbol_keywords = [
        (r"Rx\s*only", "Rx only"),
        (r"(?:not\s+)?made\s+with\s+natural\s+rubber\s+latex", "Not made with natural rubber latex"),
        (r"Consult\s+instructions?\s+for\s+use", "Consult instructions for use"),
        (r"Do\s+not\s+use\s+if\s+package\s+(?:is\s+)?damaged", "Do not use if package damaged"),
        (r"\bSterile\b", "Sterile"),
        (r"Single\s+use", "Single use"),
        (r"Do\s+not\s+re-?use", "Do not reuse"),
        (r"Do\s+not\s+resterilize", "Do not resterilize"),
        (r"Made\s+in\s+U\.?S\.?A\.?", "Made in USA"),
        (r"\bManufacturer\b", "Manufacturer"),
        (r"\bUDI\b", "UDI"),
        (r"\bMD\b(?!\s*=)", "MD (Medical Device)"),
        (r"\bMR\b", "MR"),
        (r"DataMatrix|2D\s+barcode", "2D DataMatrix barcode"),
        (r"Country\s+of\s+origin", "Country of origin"),
        (r"\bREF\b", "REF (Catalogue number)"),
        (r"\bLOT\b", "LOT"),
        (r"\bSN\b", "Serial Number (SN)"),
    ]
    for pat, label in symbol_keywords:
        if re.search(pat, text, re.IGNORECASE):
            if label not in section.regulatory_symbols:
                section.regulatory_symbols.append(label)

    # ── Manufacturing notes ──
    mfg_patterns = [
        re.compile(r"FIRST\s+ARTICLE\s+INSPECT\s+PER\s+\S+", re.IGNORECASE),
        re.compile(r"MFG\s+INSPECT\s+PER\s+\S+", re.IGNORECASE),
        re.compile(r"DO\s+NOT\s+SCALE\s+DRAWING", re.IGNORECASE),
    ]
    for pat in mfg_patterns:
        m = pat.search(text)
        if m:
            section.manufacturing_notes.append(m.group(0).strip())
