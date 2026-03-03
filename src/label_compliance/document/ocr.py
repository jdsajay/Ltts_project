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


def preprocess_image(
    img: np.ndarray,
    steps: list[str] | None = None,
    is_high_res: bool = False,
) -> np.ndarray:
    """
    Preprocess image for better OCR accuracy.

    Steps: grayscale, threshold, denoise, deskew, sharpen, upscale
    
    For high-resolution embedded images (e.g., 9632x7200 label scans),
    uses gentler preprocessing to preserve detail. For smaller rendered
    pages, uses standard adaptive thresholding.
    
    Args:
        img: Input image as numpy array.
        steps: Preprocessing steps to apply. Defaults to config value.
        is_high_res: If True, use gentler preprocessing for high-res images.
    """
    if steps is None:
        settings = get_settings()
        steps = settings.document.ocr_preprocess

    result = img.copy()
    h, w = result.shape[:2]
    
    # Auto-detect high-res images (> 4000px in either dimension)
    if not is_high_res and (h > 4000 or w > 4000):
        is_high_res = True

    for step in steps:
        if step == "grayscale" and len(result.shape) == 3:
            result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        elif step == "threshold":
            if len(result.shape) == 3:
                result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
            if is_high_res:
                # For high-res label images: use Otsu thresholding which
                # is better at preserving text in complex label layouts
                # with mixed colors and backgrounds
                _, result = cv2.threshold(
                    result, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )
            else:
                result = cv2.adaptiveThreshold(
                    result, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                )
        elif step == "denoise":
            if is_high_res:
                # Gentler denoising for high-res images (preserve detail)
                if len(result.shape) == 2:
                    result = cv2.fastNlMeansDenoising(result, h=5)
                else:
                    result = cv2.fastNlMeansDenoisingColored(result, h=5)
            else:
                if len(result.shape) == 2:
                    result = cv2.fastNlMeansDenoising(result, h=10)
                else:
                    result = cv2.fastNlMeansDenoisingColored(result, h=10)
        elif step == "sharpen":
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            result = cv2.filter2D(result, -1, kernel)
        elif step == "upscale":
            # Upscale small images for better OCR (useful for cropped sections)
            if h < 500 or w < 500:
                scale = max(2, 1000 // min(h, w))
                result = cv2.resize(result, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    return result


def run_ocr(
    image_path: Path | str,
    preprocess: bool = True,
    language: str | None = None,
    multi_strategy: bool = False,
) -> OCRResult:
    """
    Run OCR on a label image.

    Args:
        image_path: Path to the image file.
        preprocess: Whether to apply preprocessing (improves accuracy).
        language: OCR language (default from config).
        multi_strategy: If True, run OCR with multiple preprocessing
            strategies and pick the best result. Slower but more accurate
            for complex label images. Auto-enabled for high-res images.

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
    is_high_res = h > 4000 or w > 4000

    # Auto-enable multi-strategy for high-res label images
    if is_high_res and not multi_strategy:
        multi_strategy = True

    if multi_strategy:
        return _run_ocr_multi_strategy(img, image_path, lang, min_conf, is_high_res)

    # Single strategy
    if preprocess:
        processed = preprocess_image(img, is_high_res=is_high_res)
    else:
        processed = img

    return _ocr_on_image(processed, image_path, lang, min_conf, w, h)


def _ocr_on_image(
    processed: np.ndarray,
    image_path: Path,
    lang: str,
    min_conf: int,
    orig_w: int,
    orig_h: int,
) -> OCRResult:
    """Run Tesseract OCR on a preprocessed image array."""
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
        image_size=(orig_w, orig_h),
        full_text=full_text,
        words=words,
        text_blocks=text_blocks,
    )

    logger.debug(
        "OCR: %s → %d words, %d blocks, %d chars",
        image_path.name, len(words), len(text_blocks), len(full_text),
    )
    return result


def _run_ocr_multi_strategy(
    img: np.ndarray,
    image_path: Path,
    lang: str,
    min_conf: int,
    is_high_res: bool,
) -> OCRResult:
    """
    Run OCR with multiple preprocessing strategies and return the best.

    Strategies:
    1. Raw image (no preprocessing) — best for clean, high-res scans
    2. Grayscale + Otsu threshold — good for mixed backgrounds
    3. Grayscale + denoise — good for noisy scans
    4. Standard preprocessing (grayscale + adaptive threshold + denoise)

    Picks the strategy that produces the most confident words.
    """
    h, w = img.shape[:2]
    
    strategies: list[tuple[str, np.ndarray]] = [
        ("raw", img.copy()),
    ]

    # Strategy 2: Grayscale only (preserves most detail)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()
    strategies.append(("grayscale", gray))

    # Strategy 3: Grayscale + Otsu (good for high-res)
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    strategies.append(("otsu", otsu))

    # Strategy 4: Standard preprocessing
    standard = preprocess_image(img, is_high_res=is_high_res)
    strategies.append(("standard", standard))

    best_result: OCRResult | None = None
    best_score = -1

    for name, processed in strategies:
        result = _ocr_on_image(processed, image_path, lang, min_conf, w, h)

        # Score by: number of confident words + average confidence
        if result.words:
            avg_conf = sum(wd.confidence for wd in result.words) / len(result.words)
            score = len(result.words) * (avg_conf / 100.0)
        else:
            score = 0

        logger.debug(
            "  OCR strategy '%s': %d words, score=%.1f",
            name, len(result.words), score,
        )

        if score > best_score:
            best_score = score
            best_result = result

    # If all strategies failed, return the standard one
    if best_result is None:
        best_result = _ocr_on_image(standard, image_path, lang, min_conf, w, h)

    logger.info(
        "Multi-strategy OCR %s: best=%d words, %d chars",
        image_path.name,
        best_result.word_count if best_result else 0,
        len(best_result.full_text) if best_result else 0,
    )
    return best_result


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
