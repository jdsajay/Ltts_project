"""Document processing subpackage — PDF reading, OCR, layout, symbols."""

from label_compliance.document.pdf_reader import read_pdf
from label_compliance.document.image_renderer import render_pages
from label_compliance.document.ocr import run_ocr

__all__ = ["read_pdf", "render_pages", "run_ocr"]
