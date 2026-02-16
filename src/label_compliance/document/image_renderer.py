"""
Image Renderer
================
Renders PDF pages as high-res PNG images for OCR and visual analysis.
Uses PyMuPDF (fitz) for rendering.
"""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

from label_compliance.config import get_settings
from label_compliance.utils.helpers import safe_filename
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


def render_pages(
    pdf_path: Path,
    output_dir: Path | None = None,
    dpi: int | None = None,
) -> list[Path]:
    """
    Render all pages of a PDF as PNG images.

    Args:
        pdf_path: Path to the PDF file.
        output_dir: Directory to save images. Defaults to data/images/<pdf_stem>/.
        dpi: Render resolution. Defaults to config value (300).

    Returns:
        List of paths to the generated PNG images.
    """
    settings = get_settings()
    dpi = dpi or settings.document.render_dpi
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    if output_dir is None:
        stem = safe_filename(pdf_path.stem)
        output_dir = settings.paths.knowledge_base_dir.parent / "images" / stem

    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    image_paths: list[Path] = []

    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=mat)
        img_path = output_dir / f"page-{i:02d}.png"
        pix.save(str(img_path))
        image_paths.append(img_path)
        logger.debug("  Rendered page %d → %s (%dx%d)", i, img_path.name, pix.width, pix.height)

    doc.close()
    logger.info("Rendered %d pages from %s at %d DPI", len(image_paths), pdf_path.name, dpi)
    return image_paths


def render_single_page(
    pdf_path: Path,
    page_number: int,
    dpi: int = 300,
) -> Image.Image:
    """Render a single page as a PIL Image (in-memory, no file save)."""
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    doc = fitz.open(str(pdf_path))
    page = doc[page_number - 1]
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return img
