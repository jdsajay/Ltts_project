"""
Layout Analyzer
================
Detects zones/regions in label images: text blocks, symbols,
barcodes, logos, whitespace.  Uses contour detection and
heuristics to segment the label into functional areas.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


@dataclass
class Zone:
    """A detected region on the label."""

    zone_type: str  # "text", "symbol", "barcode", "logo", "table", "whitespace"
    x: int
    y: int
    w: int
    h: int
    confidence: float = 0.0
    content: str = ""

    @property
    def area(self) -> int:
        return self.w * self.h

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)


def analyze_layout(image_path: Path) -> list[Zone]:
    """
    Detect functional zones in a label image.

    Uses edge detection + contour analysis to find:
    - Text regions (dense characters)
    - Symbol regions (small, high-contrast icons)
    - Barcode regions (stripe patterns)
    - Logo regions (large graphical blocks)
    """
    img = cv2.imread(str(image_path))
    if img is None:
        return []

    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find text-dense regions via morphological operations
    zones = []

    # Binary threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Dilate to merge nearby text into blocks
    kernel_text = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilated = cv2.dilate(binary, kernel_text, iterations=2)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        cx, cy, cw, ch = cv2.boundingRect(contour)
        area = cw * ch

        # Skip tiny noise
        if area < 500:
            continue

        # Classify based on aspect ratio and size
        aspect = cw / max(ch, 1)
        relative_area = area / (w * h)

        if relative_area < 0.001:
            zone_type = "symbol"
        elif aspect > 5:
            zone_type = "barcode"
        elif aspect < 0.3 and relative_area > 0.01:
            zone_type = "logo"
        else:
            zone_type = "text"

        zones.append(Zone(
            zone_type=zone_type,
            x=cx, y=cy, w=cw, h=ch,
            confidence=0.7,
        ))

    # Merge overlapping zones of same type
    zones = _merge_overlapping(zones)

    logger.debug(
        "Layout: %s → %d zones (%s)",
        image_path.name,
        len(zones),
        ", ".join(f"{z.zone_type}" for z in zones[:5]),
    )
    return zones


def _merge_overlapping(zones: list[Zone], overlap_threshold: float = 0.5) -> list[Zone]:
    """Merge overlapping zones of the same type."""
    if not zones:
        return zones

    merged = []
    used = set()

    for i, za in enumerate(zones):
        if i in used:
            continue
        group = [za]
        for j, zb in enumerate(zones):
            if j <= i or j in used or za.zone_type != zb.zone_type:
                continue
            if _iou(za, zb) > overlap_threshold:
                group.append(zb)
                used.add(j)

        # Merge group into one zone
        xs = [z.x for z in group]
        ys = [z.y for z in group]
        x2s = [z.x + z.w for z in group]
        y2s = [z.y + z.h for z in group]
        merged.append(Zone(
            zone_type=za.zone_type,
            x=min(xs),
            y=min(ys),
            w=max(x2s) - min(xs),
            h=max(y2s) - min(ys),
            confidence=max(z.confidence for z in group),
        ))

    return merged


def _iou(a: Zone, b: Zone) -> float:
    """Intersection over union of two zones."""
    x1 = max(a.x, b.x)
    y1 = max(a.y, b.y)
    x2 = min(a.x + a.w, b.x + b.w)
    y2 = min(a.y + a.h, b.y + b.h)

    if x2 < x1 or y2 < y1:
        return 0.0

    intersection = (x2 - x1) * (y2 - y1)
    union = a.area + b.area - intersection
    return intersection / max(union, 1)
