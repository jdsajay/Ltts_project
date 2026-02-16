"""
PDF Reader
===========
Extracts text, tables, and metadata from label PDFs.
Uses pdfplumber for text/tables and PyMuPDF for metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber

from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


@dataclass
class PageData:
    """Data extracted from a single PDF page."""

    page_number: int
    text: str = ""
    tables: list[list[list[str]]] = field(default_factory=list)
    width: float = 0.0
    height: float = 0.0
    fonts: list[dict] = field(default_factory=list)


@dataclass
class PDFData:
    """All extracted data from a PDF file."""

    path: Path
    filename: str
    num_pages: int = 0
    pages: list[PageData] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    full_text: str = ""

    @property
    def all_fonts(self) -> list[dict]:
        """Get all unique fonts used across pages."""
        seen = set()
        fonts = []
        for page in self.pages:
            for f in page.fonts:
                key = (f.get("name", ""), f.get("size", 0))
                if key not in seen:
                    seen.add(key)
                    fonts.append(f)
        return fonts


def read_pdf(pdf_path: Path) -> PDFData:
    """
    Extract all text, tables, fonts, and metadata from a PDF.

    This is the primary entry point for processing label PDFs.
    """
    pdf_path = Path(pdf_path)
    logger.info("Reading PDF: %s", pdf_path.name)

    result = PDFData(path=pdf_path, filename=pdf_path.name)
    all_text_parts: list[str] = []

    # ── pdfplumber pass: text + tables ────────────────
    try:
        with pdfplumber.open(pdf_path) as pdf:
            result.num_pages = len(pdf.pages)

            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                tables = page.extract_tables() or []

                # Clean tables
                clean_tables = []
                for table in tables:
                    clean_table = []
                    for row in table:
                        if row:
                            clean_row = [str(c).strip() if c else "" for c in row]
                            clean_table.append(clean_row)
                    if clean_table:
                        clean_tables.append(clean_table)

                page_data = PageData(
                    page_number=i,
                    text=text,
                    tables=clean_tables,
                    width=float(page.width),
                    height=float(page.height),
                )
                result.pages.append(page_data)
                all_text_parts.append(text)

    except Exception:
        logger.exception("pdfplumber failed for %s", pdf_path.name)

    # ── PyMuPDF pass: fonts + metadata ───────────────
    try:
        doc = fitz.open(str(pdf_path))
        result.metadata = dict(doc.metadata) if doc.metadata else {}

        for i, page in enumerate(doc):
            if i < len(result.pages):
                fonts = _extract_fonts(page)
                result.pages[i].fonts = fonts

        doc.close()
    except Exception:
        logger.exception("PyMuPDF font extraction failed for %s", pdf_path.name)

    result.full_text = "\n".join(all_text_parts)
    logger.info(
        "  %d pages, %d chars, %d fonts",
        result.num_pages, len(result.full_text), len(result.all_fonts),
    )
    return result


def _extract_fonts(page: fitz.Page) -> list[dict]:
    """Extract font information from a PyMuPDF page."""
    fonts = []
    try:
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        seen = set()
        for block in blocks:
            if block.get("type") != 0:  # text blocks only
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    font_name = span.get("font", "unknown")
                    font_size = round(span.get("size", 0), 1)
                    key = (font_name, font_size)
                    if key not in seen:
                        seen.add(key)
                        fonts.append({
                            "name": font_name,
                            "size": font_size,
                            "flags": span.get("flags", 0),
                            "color": span.get("color", 0),
                        })
    except Exception:
        logger.debug("Font extraction failed for page")
    return fonts
