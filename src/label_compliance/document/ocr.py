"""
OCR Engine
===========
Runs Tesseract OCR on label images with preprocessing.
Returns structured results including word-level bounding boxes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image

from label_compliance.config import get_settings
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


@dataclass
class OCRWord:
    """A single word detected by OCR."""

    text: str
    confidence: int
    x: int
    y: int
    w: int
    h: int
    block: int = 0
    line: int = 0


@dataclass
class OCRResult:
    """Structured OCR output for one image."""

    image_path: str
    image_size: tuple[int, int]
    full_text: str
    words: list[OCRWord] = field(default_factory=list)
    text_blocks: list[dict] = field(default_factory=list)

    @property
    def word_count(self) -> int:
        return len(self.words)

    @property
    def text_lower(self) -> str:
        return self.full_text.lower()

    def words_in_region(self, x: int, y: int, w: int, h: int) -> list[OCRWord]:
        """Get all words within a bounding box region."""
        return [
            word for word in self.words
            if (word.x >= x and word.y >= y
                and word.x + word.w <= x + w
                and word.y + word.h <= y + h)
        ]

    def find_text(self, search: str) -> list[OCRWord]:
        """Find all word occurrences matching a search string."""
        search_lower = search.lower()
        return [w for w in self.words if search_lower in w.text.lower()]


def preprocess_image(img: np.ndarray, steps: list[str] | None = None) -> np.ndarray:
    """
    Preprocess image for better OCR accuracy.

    Steps: grayscale, threshold, denoise, deskew, sharpen
    """
    if steps is None:
        settings = get_settings()
        steps = settings.document.ocr_preprocess

    result = img.copy()

    for step in steps:
        if step == "grayscale" and len(result.shape) == 3:
            result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        elif step == "threshold":
            if len(result.shape) == 3:
                result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
            result = cv2.adaptiveThreshold(
                result, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
        elif step == "denoise":
            if len(result.shape) == 2:
                result = cv2.fastNlMeansDenoising(result, h=10)
            else:
                result = cv2.fastNlMeansDenoisingColored(result, h=10)
        elif step == "sharpen":
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            result = cv2.filter2D(result, -1, kernel)

    return result


def run_ocr(
    image_path: Path | str,
    preprocess: bool = True,
    language: str | None = None,
) -> OCRResult:
    """
    Run OCR on a label image.

    Args:
        image_path: Path to the image file.
        preprocess: Whether to apply preprocessing (improves accuracy).
        language: OCR language (default from config).

    Returns:
        OCRResult with full text and word-level bounding boxes.
    """
    settings = get_settings()
    image_path = Path(image_path)
    lang = language or settings.document.ocr_language
    min_conf = settings.document.ocr_min_confidence

    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        logger.error("Failed to load image: %s", image_path)
        return OCRResult(
            image_path=str(image_path),
            image_size=(0, 0),
            full_text="",
        )

    h, w = img.shape[:2]

    # Preprocess
    if preprocess:
        processed = preprocess_image(img)
    else:
        processed = img

    # Convert for pytesseract
    if len(processed.shape) == 2:
        pil_img = Image.fromarray(processed)
    else:
        pil_img = Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB))

    # Full text extraction
    full_text = pytesseract.image_to_string(pil_img, lang=lang)

    # Word-level data with bounding boxes
    word_data = pytesseract.image_to_data(pil_img, lang=lang, output_type=pytesseract.Output.DICT)

    words = []
    for i in range(len(word_data["text"])):
        text = word_data["text"][i].strip()
        conf = int(word_data["conf"][i])
        if text and conf >= min_conf:
            words.append(OCRWord(
                text=text,
                confidence=conf,
                x=word_data["left"][i],
                y=word_data["top"][i],
                w=word_data["width"][i],
                h=word_data["height"][i],
                block=word_data["block_num"][i],
                line=word_data["line_num"][i],
            ))

    # Group into text blocks
    text_blocks = _group_text_blocks(words)

    result = OCRResult(
        image_path=str(image_path),
        image_size=(w, h),
        full_text=full_text,
        words=words,
        text_blocks=text_blocks,
    )

    logger.debug(
        "OCR: %s → %d words, %d blocks, %d chars",
        image_path.name, len(words), len(text_blocks), len(full_text),
    )
    return result


def _group_text_blocks(words: list[OCRWord]) -> list[dict]:
    """Group words into logical text blocks by block/line number."""
    blocks: dict[int, dict[int, list[OCRWord]]] = {}
    for w in words:
        blocks.setdefault(w.block, {}).setdefault(w.line, []).append(w)

    result = []
    for block_num in sorted(blocks):
        block_words = []
        block_text_parts = []
        for line_num in sorted(blocks[block_num]):
            line_words = blocks[block_num][line_num]
            block_words.extend(line_words)
            block_text_parts.append(" ".join(w.text for w in line_words))

        if block_words:
            xs = [w.x for w in block_words]
            ys = [w.y for w in block_words]
            x2s = [w.x + w.w for w in block_words]
            y2s = [w.y + w.h for w in block_words]

            result.append({
                "block_num": block_num,
                "text": "\n".join(block_text_parts),
                "bbox": (min(xs), min(ys), max(x2s) - min(xs), max(y2s) - min(ys)),
                "word_count": len(block_words),
                "avg_confidence": sum(w.confidence for w in block_words) // len(block_words),
            })

    return result
