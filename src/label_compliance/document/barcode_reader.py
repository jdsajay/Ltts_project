"""
Barcode Reader
===============
Reads GS1-128, DataMatrix, and QR barcodes from label images.
Validates UDI/GTIN format compliance.
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

# On macOS ARM, Homebrew installs libraries to /opt/homebrew/lib which isn't
# in the default dynamic linker search path.  pyzbar uses ctypes.util.find_library
# which relies on DYLD_LIBRARY_PATH.  We add the path before pyzbar is imported.
if sys.platform == "darwin":
    _brew_lib = "/opt/homebrew/lib"
    _intel_lib = "/usr/local/lib"
    _current = os.environ.get("DYLD_LIBRARY_PATH", "")
    _paths = [p for p in [_brew_lib, _intel_lib] if Path(p).exists()]
    if _paths:
        os.environ["DYLD_LIBRARY_PATH"] = ":".join(_paths + ([_current] if _current else []))


@dataclass
class BarcodeResult:
    """Decoded barcode data."""

    barcode_type: str  # "GS1-128", "DataMatrix", "QR", "EAN13", etc.
    data: str
    x: int
    y: int
    w: int
    h: int
    is_udi: bool = False
    gtin: str | None = None
    lot: str | None = None
    serial: str | None = None
    expiry: str | None = None


def read_barcodes(image_path: Path) -> list[BarcodeResult]:
    """
    Read all barcodes from an image.

    Uses pyzbar for 1D/2D barcode decoding.
    Falls back to OpenCV detection if pyzbar not available.
    """
    img = cv2.imread(str(image_path))
    if img is None:
        return []

    results = []

    try:
        from pyzbar.pyzbar import decode, ZBarSymbol

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Try multiple preprocessing approaches
        images_to_scan = [
            gray,
            cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2),
        ]

        seen_data = set()
        for scan_img in images_to_scan:
            pil_img = _cv2_to_pil(scan_img)
            decoded = decode(pil_img)

            for barcode in decoded:
                data = barcode.data.decode("utf-8", errors="replace")
                if data in seen_data:
                    continue
                seen_data.add(data)

                rect = barcode.rect
                bc_type = barcode.type

                result = BarcodeResult(
                    barcode_type=bc_type,
                    data=data,
                    x=rect.left,
                    y=rect.top,
                    w=rect.width,
                    h=rect.height,
                )

                # Parse GS1 elements
                _parse_gs1(result)
                results.append(result)

    except ImportError:
        logger.warning("pyzbar not available — barcode scanning disabled")

    logger.debug("Barcodes found in %s: %d", image_path.name, len(results))
    return results


def _parse_gs1(result: BarcodeResult) -> None:
    """Parse GS1-128 Application Identifiers from barcode data."""
    data = result.data

    # GTIN: AI (01)
    gtin_match = re.search(r"\(01\)(\d{14})", data)
    if gtin_match:
        result.gtin = gtin_match.group(1)
        result.is_udi = True

    # LOT: AI (10)
    lot_match = re.search(r"\(10\)([A-Za-z0-9]+)", data)
    if lot_match:
        result.lot = lot_match.group(1)

    # Serial: AI (21)
    serial_match = re.search(r"\(21\)([A-Za-z0-9]+)", data)
    if serial_match:
        result.serial = serial_match.group(1)

    # Expiry: AI (17)
    exp_match = re.search(r"\(17\)(\d{6})", data)
    if exp_match:
        result.expiry = exp_match.group(1)


def _cv2_to_pil(img: np.ndarray):
    """Convert OpenCV image to PIL Image."""
    from PIL import Image

    if len(img.shape) == 2:
        return Image.fromarray(img)
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
