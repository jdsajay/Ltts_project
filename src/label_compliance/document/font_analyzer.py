"""
Font Analyzer
==============
Extracts and validates font information from PDF labels.
Checks font names, sizes, and styles against ISO requirements.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF

from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


@dataclass
class FontInfo:
    """Information about a font span in the PDF."""

    name: str
    size: float
    is_bold: bool = False
    is_italic: bool = False
    color: int = 0
    text: str = ""
    page: int = 0
    bbox: tuple[float, float, float, float] = (0, 0, 0, 0)


def extract_fonts(pdf_path: Path) -> list[FontInfo]:
    """
    Extract all font usage from a PDF with context.

    Returns a list of FontInfo objects, one per text span,
    with font name, size, style, and the text rendered in that font.
    """
    fonts: list[FontInfo] = []

    try:
        doc = fitz.open(str(pdf_path))
        for page_num, page in enumerate(doc, 1):
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
            for block in blocks:
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if not text:
                            continue

                        flags = span.get("flags", 0)
                        fonts.append(FontInfo(
                            name=span.get("font", "unknown"),
                            size=round(span.get("size", 0), 1),
                            is_bold=bool(flags & 2**4),   # bit 4 = bold
                            is_italic=bool(flags & 2**1),  # bit 1 = italic
                            color=span.get("color", 0),
                            text=text[:200],
                            page=page_num,
                            bbox=tuple(span.get("bbox", (0, 0, 0, 0))),
                        ))

        doc.close()
    except Exception:
        logger.exception("Font extraction failed: %s", pdf_path.name)

    logger.debug("Extracted %d font spans from %s", len(fonts), pdf_path.name)
    return fonts


def get_font_summary(fonts: list[FontInfo]) -> dict:
    """
    Summarize font usage: unique fonts, sizes, most common font.
    """
    if not fonts:
        return {"unique_fonts": [], "size_range": (0, 0), "dominant_font": "unknown"}

    font_counts: dict[str, int] = {}
    sizes: list[float] = []

    for f in fonts:
        font_counts[f.name] = font_counts.get(f.name, 0) + 1
        sizes.append(f.size)

    dominant = max(font_counts, key=font_counts.get)

    return {
        "unique_fonts": sorted(font_counts.keys()),
        "font_counts": font_counts,
        "size_range": (min(sizes), max(sizes)),
        "dominant_font": dominant,
        "total_spans": len(fonts),
    }


def validate_font_size(fonts: list[FontInfo], min_size_pt: float = 6.0) -> list[dict]:
    """
    Check if any text is below minimum readable font size.

    ISO labels typically require minimum 6pt for critical information.
    """
    violations = []
    for f in fonts:
        if f.size > 0 and f.size < min_size_pt:
            violations.append({
                "font": f.name,
                "size": f.size,
                "min_required": min_size_pt,
                "text_preview": f.text[:80],
                "page": f.page,
            })
    return violations
