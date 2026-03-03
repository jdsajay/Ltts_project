"""
Image Extractor
=================
Extracts embedded images from PDF pages and classifies pages as
image-only, mixed (text + images), or text-only.

Many medical-device label PDFs (especially DRWG files) contain the
actual label artwork as embedded raster images (JPEG/PNG). These
images hold critical compliance content — symbols, barcodes,
regulatory marks — that cannot be extracted via text-based methods.

This module:
1. Detects whether a PDF page is image-only, mixed, or text-only.
2. Extracts embedded images from PDF pages.
3. Runs enhanced OCR on extracted images.
4. Provides a unified text extraction pipeline that works for ALL
   PDF types (vector text, embedded images, or both).
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


# Minimum embedded image area (pixels) to consider it a label image
# (skip tiny icons, logos < 100x100)
_MIN_IMAGE_AREA = 50_000  # ~224x224 pixels


@dataclass
class EmbeddedImage:
    """An image extracted from a PDF page."""

    xref: int
    width: int
    height: int
    extension: str  # "png", "jpeg", etc.
    page_number: int  # 1-based
    image_bytes: bytes = field(repr=False)
    saved_path: Path | None = None

    @property
    def area(self) -> int:
        return self.width * self.height

    @property
    def is_label_image(self) -> bool:
        """Whether this is likely a label image (not a tiny icon)."""
        return self.area >= _MIN_IMAGE_AREA


@dataclass
class PageClassification:
    """Classification of a single PDF page's content type."""

    page_number: int  # 1-based
    text_length: int
    embedded_image_count: int
    total_image_area: int

    @property
    def page_type(self) -> str:
        """Classify as IMAGE_ONLY, MIXED, or TEXT_ONLY."""
        has_text = self.text_length > 50  # more than trivial whitespace
        has_images = self.embedded_image_count > 0 and self.total_image_area >= _MIN_IMAGE_AREA
        if has_images and not has_text:
            return "IMAGE_ONLY"
        elif has_images and has_text:
            return "MIXED"
        else:
            return "TEXT_ONLY"

    @property
    def is_image_only(self) -> bool:
        return self.page_type == "IMAGE_ONLY"

    @property
    def has_significant_images(self) -> bool:
        return self.total_image_area >= _MIN_IMAGE_AREA


@dataclass
class PDFImageAnalysis:
    """Full image analysis of a PDF document."""

    pdf_path: Path
    total_pages: int
    page_classifications: list[PageClassification] = field(default_factory=list)
    embedded_images: list[EmbeddedImage] = field(default_factory=list)

    @property
    def has_image_only_pages(self) -> bool:
        return any(pc.is_image_only for pc in self.page_classifications)

    @property
    def image_only_pages(self) -> list[int]:
        return [pc.page_number for pc in self.page_classifications if pc.is_image_only]

    @property
    def mixed_pages(self) -> list[int]:
        return [pc.page_number for pc in self.page_classifications if pc.page_type == "MIXED"]


def classify_pdf_pages(pdf_path: Path) -> PDFImageAnalysis:
    """
    Classify each page of a PDF as IMAGE_ONLY, MIXED, or TEXT_ONLY.

    This is a fast pre-scan that determines how each page should be processed:
    - TEXT_ONLY: Use standard text extraction (pdfplumber/PyMuPDF)
    - IMAGE_ONLY: Extract embedded images → OCR → use OCR text
    - MIXED: Use both text extraction AND embedded image OCR

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        PDFImageAnalysis with per-page classifications.
    """
    pdf_path = Path(pdf_path)
    doc = fitz.open(str(pdf_path))
    result = PDFImageAnalysis(pdf_path=pdf_path, total_pages=len(doc))

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_num = page_idx + 1

        text = page.get_text().strip()
        images = page.get_images(full=True)

        total_area = 0
        significant_count = 0

        for img_info in images:
            xref = img_info[0]
            try:
                base_img = doc.extract_image(xref)
                w, h = base_img["width"], base_img["height"]
                area = w * h
                total_area += area
                if area >= _MIN_IMAGE_AREA:
                    significant_count += 1
            except Exception:
                pass

        pc = PageClassification(
            page_number=page_num,
            text_length=len(text),
            embedded_image_count=significant_count,
            total_image_area=total_area,
        )
        result.page_classifications.append(pc)

    doc.close()

    # Log summary
    img_only = [pc.page_number for pc in result.page_classifications if pc.is_image_only]
    mixed = [pc.page_number for pc in result.page_classifications if pc.page_type == "MIXED"]
    text_only = [pc.page_number for pc in result.page_classifications if pc.page_type == "TEXT_ONLY"]
    logger.info(
        "PDF classification %s: %d pages — IMAGE_ONLY=%s, MIXED=%s, TEXT_ONLY=%s",
        pdf_path.name, result.total_pages, img_only or "none", mixed or "none", text_only or "none",
    )

    return result


def extract_embedded_images(
    pdf_path: Path,
    output_dir: Path,
    pages: list[int] | None = None,
    min_area: int = _MIN_IMAGE_AREA,
) -> list[EmbeddedImage]:
    """
    Extract embedded images from a PDF and save them as files.

    For image-only PDFs, this extracts the full-page raster images
    that contain the actual label artwork. For mixed PDFs, it
    extracts the label artwork images embedded alongside vector text.

    Args:
        pdf_path: Path to the PDF file.
        output_dir: Directory to save extracted images.
        pages: Specific pages to extract from (1-based). None = all pages.
        min_area: Minimum image area in pixels to extract.

    Returns:
        List of EmbeddedImage objects with saved file paths.
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    extracted: list[EmbeddedImage] = []
    seen_xrefs: set[int] = set()

    for page_idx in range(len(doc)):
        page_num = page_idx + 1
        if pages and page_num not in pages:
            continue

        page = doc[page_idx]
        images = page.get_images(full=True)

        for img_idx, img_info in enumerate(images):
            xref = img_info[0]

            # Skip duplicate xrefs (same image referenced multiple times)
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            try:
                base_img = doc.extract_image(xref)
                w, h = base_img["width"], base_img["height"]
                ext = base_img["ext"]
                img_bytes = base_img["image"]

                if w * h < min_area:
                    logger.debug(
                        "  Skipping small image xref=%d (%dx%d) on page %d",
                        xref, w, h, page_num,
                    )
                    continue

                # Save the image
                img_filename = f"page-{page_num:02d}_embedded-{img_idx:02d}_{w}x{h}.{ext}"
                img_path = output_dir / img_filename
                img_path.write_bytes(img_bytes)

                emb = EmbeddedImage(
                    xref=xref,
                    width=w,
                    height=h,
                    extension=ext,
                    page_number=page_num,
                    image_bytes=img_bytes,
                    saved_path=img_path,
                )
                extracted.append(emb)

                logger.debug(
                    "  Extracted image: page %d, %dx%d %s → %s",
                    page_num, w, h, ext, img_path.name,
                )

            except Exception as e:
                logger.warning("Failed to extract image xref=%d: %s", xref, e)

    doc.close()

    logger.info(
        "Extracted %d embedded images from %s",
        len(extracted), pdf_path.name,
    )
    return extracted


def extract_and_ocr_embedded_images(
    pdf_path: Path,
    output_dir: Path,
    pages: list[int] | None = None,
) -> dict[int, str]:
    """
    Extract embedded images and run OCR on them.

    This is the key function for image-only PDFs: it extracts the
    raster label images, runs OCR with optimized settings, and
    returns the OCR text organized by page number.

    Args:
        pdf_path: Path to the PDF file.
        output_dir: Directory to save extracted images.
        pages: Specific pages to process (1-based). None = all.

    Returns:
        Dict mapping page_number → OCR text from embedded images.
    """
    from label_compliance.document.ocr import run_ocr

    images = extract_embedded_images(pdf_path, output_dir, pages=pages)

    page_texts: dict[int, list[str]] = {}

    for emb in images:
        if not emb.saved_path or not emb.is_label_image:
            continue

        # Run OCR on the extracted image with enhanced settings
        ocr_result = run_ocr(emb.saved_path, preprocess=True)

        page_texts.setdefault(emb.page_number, []).append(ocr_result.full_text)

        logger.debug(
            "  OCR on embedded image page %d: %d words, %d chars",
            emb.page_number, ocr_result.word_count, len(ocr_result.full_text),
        )

    # Combine texts per page
    result: dict[int, str] = {}
    for page_num, texts in page_texts.items():
        combined = "\n".join(t for t in texts if t.strip())
        result[page_num] = combined
        logger.info(
            "  Page %d embedded image OCR: %d chars",
            page_num, len(combined),
        )

    return result


def get_best_text_for_page(
    pdf_path: Path,
    page_number: int,
    output_dir: Path,
    classification: PageClassification | None = None,
) -> str:
    """
    Get the best possible text for a page, using the right strategy
    based on the page's content type.

    - TEXT_ONLY: PyMuPDF text extraction
    - IMAGE_ONLY: Extract embedded images → OCR
    - MIXED: PyMuPDF text + embedded image OCR (combined)

    Args:
        pdf_path: Path to the PDF.
        page_number: 1-based page number.
        output_dir: Directory for saving extracted images.
        classification: Pre-computed classification (avoids re-scan).

    Returns:
        Best extracted text for the page.
    """
    from label_compliance.document.ocr import run_ocr

    doc = fitz.open(str(pdf_path))
    page = doc[page_number - 1]
    vector_text = page.get_text().strip()
    doc.close()

    if classification is None:
        analysis = classify_pdf_pages(pdf_path)
        classification = analysis.page_classifications[page_number - 1]

    texts = []

    # Always include vector text if available
    if vector_text:
        texts.append(vector_text)

    # For IMAGE_ONLY or MIXED pages, also extract and OCR embedded images
    if classification.page_type in ("IMAGE_ONLY", "MIXED"):
        embedded_texts = extract_and_ocr_embedded_images(
            pdf_path, output_dir, pages=[page_number]
        )
        emb_text = embedded_texts.get(page_number, "")
        if emb_text.strip():
            texts.append(emb_text)

    combined = "\n".join(texts)
    logger.debug(
        "Best text for page %d (%s): %d chars (vector=%d, embedded=%d)",
        page_number,
        classification.page_type,
        len(combined),
        len(vector_text),
        len(combined) - len(vector_text),
    )
    return combined
