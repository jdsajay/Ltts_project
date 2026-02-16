"""
Symbol Detector
================
Detects required regulatory symbols on labels by combining
OCR text matching and visual template matching.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

from label_compliance.document.ocr import OCRResult, OCRWord
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


@dataclass
class SymbolMatch:
    """Result of checking one required symbol."""

    rule_id: str
    description: str
    iso_ref: str
    found: bool
    method: str = ""  # "ocr_text", "ocr_pattern", "template_match", "barcode"
    matched_text: list[str] = field(default_factory=list)
    pattern_value: str | None = None
    locations: list[dict] = field(default_factory=list)  # bounding boxes where found
    confidence: float = 0.0
    severity: str = "critical"
    new_in_2024: bool = False


def detect_symbols_from_ocr(
    ocr_result: OCRResult,
    rules: list[dict],
) -> list[SymbolMatch]:
    """
    Check which required symbols/elements are present based on OCR text.

    Args:
        ocr_result: OCR output from a label image.
        rules: List of rule dicts from config/rules/*.yaml.

    Returns:
        List of SymbolMatch results, one per rule.
    """
    text_lower = ocr_result.text_lower
    findings: list[SymbolMatch] = []

    for rule in rules:
        rule_id = rule.get("id", "unknown")
        markers = rule.get("markers", [])
        pattern = rule.get("pattern")
        check_type = rule.get("check_type", "text_match")

        matched_markers: list[str] = []
        locations: list[dict] = []
        pattern_value: str | None = None

        # Text marker matching
        for marker in markers:
            if marker.lower() in text_lower:
                matched_markers.append(marker)
                # Find bounding box locations
                for word in ocr_result.find_text(marker):
                    locations.append({
                        "text": word.text,
                        "x": word.x, "y": word.y,
                        "w": word.w, "h": word.h,
                    })

        # Pattern matching (dates, measurements)
        if pattern:
            m = re.search(pattern, ocr_result.full_text, re.IGNORECASE)
            if m:
                pattern_value = m.group(0)

        is_found = len(matched_markers) > 0 or pattern_value is not None

        findings.append(SymbolMatch(
            rule_id=rule_id,
            description=rule.get("description", ""),
            iso_ref=rule.get("iso_ref", ""),
            found=is_found,
            method="ocr_text" if matched_markers else ("ocr_pattern" if pattern_value else ""),
            matched_text=matched_markers,
            pattern_value=pattern_value,
            locations=locations,
            confidence=0.9 if is_found else 0.0,
            severity=rule.get("severity", "critical"),
            new_in_2024=rule.get("new_in_2024", False),
        ))

    return findings


def detect_symbols_visual(
    image_path: Path,
    template_dir: Path | None = None,
) -> list[dict]:
    """
    Detect symbols using visual template matching.
    Matches reference symbol images against the label.

    This supplements OCR-based detection for graphical symbols
    like manufacturer, sterilization, single-use icons.
    """
    if template_dir is None:
        from label_compliance.config import get_settings
        template_dir = get_settings().paths.symbol_library_dir

    if not template_dir.exists():
        return []

    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return []

    matches = []
    templates = list(template_dir.glob("*.png"))

    for tmpl_path in templates:
        tmpl = cv2.imread(str(tmpl_path), cv2.IMREAD_GRAYSCALE)
        if tmpl is None:
            continue

        # Multi-scale template matching
        best_score = 0.0
        best_loc = None
        best_scale = 1.0

        for scale in [0.5, 0.75, 1.0, 1.25, 1.5]:
            th, tw = tmpl.shape[:2]
            new_w = int(tw * scale)
            new_h = int(th * scale)
            if new_w < 10 or new_h < 10:
                continue
            if new_w > img.shape[1] or new_h > img.shape[0]:
                continue

            resized = cv2.resize(tmpl, (new_w, new_h))
            result = cv2.matchTemplate(img, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > best_score:
                best_score = max_val
                best_loc = max_loc
                best_scale = scale

        if best_score > 0.6 and best_loc:
            th, tw = int(tmpl.shape[0] * best_scale), int(tmpl.shape[1] * best_scale)
            matches.append({
                "template": tmpl_path.stem,
                "score": best_score,
                "x": best_loc[0],
                "y": best_loc[1],
                "w": tw,
                "h": th,
                "scale": best_scale,
            })
            logger.debug(
                "Visual match: %s at (%d,%d) score=%.3f scale=%.2f",
                tmpl_path.stem, best_loc[0], best_loc[1], best_score, best_scale,
            )

    return matches
