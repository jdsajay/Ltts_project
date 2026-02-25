"""
Symbol Comparator
==================
Compares symbols found on a label against the Symbol Library database.

Two comparison modes:
1. **Text comparison** — Matches OCR-extracted text against the library's
   expected `pkg_text` and `ifu_text` fields.
2. **Visual comparison** — Matches extracted symbol images from the label
   against reference thumbnail images from the library using template matching.

Reports:
- Which required symbols are present on the label
- Which required symbols are missing
- Which symbols on the label don't match library entries
- Text discrepancies (expected vs actual text next to symbols)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

from label_compliance.document.ocr import OCRResult
from label_compliance.document.symbol_library_db import (
    SymbolEntry,
    SymbolLibrary,
    get_symbol_library,
)
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


@dataclass
class SymbolComparisonResult:
    """Result of comparing one library symbol against label content."""

    symbol: SymbolEntry
    found_by_text: bool = False
    found_by_visual: bool = False
    text_matches: list[str] = field(default_factory=list)
    text_score: float = 0.0
    visual_score: float = 0.0
    visual_location: dict | None = None  # {"x": ..., "y": ..., "w": ..., "h": ...}
    expected_text: str = ""
    actual_text: str = ""
    text_discrepancy: str = ""
    status: str = "MISSING"  # "FOUND", "PARTIAL", "MISSING"
    details: str = ""


@dataclass
class SymbolComparisonReport:
    """Full comparison report for a label page/document."""

    total_required: int = 0
    total_found: int = 0
    total_partial: int = 0
    total_missing: int = 0
    results: list[SymbolComparisonResult] = field(default_factory=list)
    extra_symbols: list[str] = field(default_factory=list)  # symbols on label not in library
    score: float = 0.0  # 0.0 - 1.0

    @property
    def summary(self) -> str:
        return (
            f"Symbol check: {self.total_found}/{self.total_required} found, "
            f"{self.total_partial} partial, {self.total_missing} missing "
            f"(score: {self.score:.0%})"
        )


def compare_symbols_text(
    ocr_result: OCRResult,
    required_symbols: list[SymbolEntry] | None = None,
    library: SymbolLibrary | None = None,
) -> SymbolComparisonReport:
    """
    Compare OCR-extracted text against required symbols from the library.

    Args:
        ocr_result: OCR output from a label page.
        required_symbols: Specific symbols to check for. If None, uses
            all standard + ISO 15223 symbols from the library.
        library: Symbol library instance. Uses singleton if not provided.

    Returns:
        SymbolComparisonReport with per-symbol results.
    """
    if library is None:
        library = get_symbol_library()
    library.load()

    if required_symbols is None:
        # Default: check all standard symbols + ISO 15223 symbols
        required_symbols = _get_required_symbols(library)

    text_lower = ocr_result.text_lower
    full_text = ocr_result.full_text

    report = SymbolComparisonReport(total_required=len(required_symbols))
    results: list[SymbolComparisonResult] = []

    for sym in required_symbols:
        result = SymbolComparisonResult(
            symbol=sym,
            expected_text=sym.pkg_text,
        )

        # Check if the expected package text appears on the label
        pkg_text_lower = sym.pkg_text.strip().lower()
        ifu_text_lower = sym.ifu_text.strip().lower()

        if not pkg_text_lower or pkg_text_lower in ("none", "no text required", "text not required", "na", "n/a"):
            # Symbol doesn't require specific text — skip text check
            result.status = "FOUND"
            result.details = "No text required for this symbol"
            result.found_by_text = True
            result.text_score = 1.0
            report.total_found += 1
            results.append(result)
            continue

        # Direct text match
        text_found, matched_fragments, score = _match_pkg_text(
            pkg_text_lower, ifu_text_lower, text_lower, full_text,
        )

        result.text_matches = matched_fragments
        result.text_score = score
        result.actual_text = "; ".join(matched_fragments) if matched_fragments else ""

        if text_found and score >= 0.8:
            result.found_by_text = True
            result.status = "FOUND"
            result.details = f"Text match ({score:.0%}): {', '.join(matched_fragments[:3])}"
            report.total_found += 1
        elif text_found or score >= 0.4:
            result.found_by_text = True
            result.status = "PARTIAL"
            result.details = f"Partial text match ({score:.0%}): {', '.join(matched_fragments[:3])}"
            # Check for text discrepancy
            if matched_fragments:
                result.text_discrepancy = (
                    f"Expected: '{sym.pkg_text}' → Found: '{matched_fragments[0]}'"
                )
            report.total_partial += 1
        else:
            result.status = "MISSING"
            result.details = f"Expected text not found: '{sym.pkg_text}'"
            report.total_missing += 1

        results.append(result)

    report.results = results

    # Compute overall score
    if report.total_required > 0:
        report.score = (
            report.total_found + 0.5 * report.total_partial
        ) / report.total_required

    return report


def compare_symbols_visual(
    image_path: Path,
    required_symbols: list[SymbolEntry] | None = None,
    library: SymbolLibrary | None = None,
    confidence_threshold: float = 0.6,
) -> SymbolComparisonReport:
    """
    Compare label image against reference symbol thumbnails via template matching.

    Args:
        image_path: Path to the rendered label page image.
        required_symbols: Symbols to look for. Defaults to all standard symbols.
        library: Symbol library instance.
        confidence_threshold: Minimum match score (0.0-1.0) to count as found.

    Returns:
        SymbolComparisonReport with visual matching results.
    """
    if library is None:
        library = get_symbol_library()
    library.load()

    if required_symbols is None:
        required_symbols = _get_required_symbols(library)

    # Load label image
    label_img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if label_img is None:
        logger.error("Cannot read label image: %s", image_path)
        return SymbolComparisonReport(total_required=len(required_symbols), total_missing=len(required_symbols))

    report = SymbolComparisonReport(total_required=len(required_symbols))
    results: list[SymbolComparisonResult] = []

    for sym in required_symbols:
        result = SymbolComparisonResult(
            symbol=sym,
            expected_text=sym.pkg_text,
        )

        # Get reference thumbnail path
        thumb_path = sym.get_std_thumb_path(library.library_dir)
        if thumb_path is None:
            thumb_path = sym.get_thumb_path(library.library_dir)

        if thumb_path is None or not thumb_path.exists():
            result.status = "MISSING"
            result.details = "No reference thumbnail available for visual comparison"
            report.total_missing += 1
            results.append(result)
            continue

        # Template matching at multiple scales
        best_score, best_loc, best_scale = _multi_scale_match(
            label_img, thumb_path, scales=[0.3, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
        )

        result.visual_score = best_score

        if best_score >= confidence_threshold and best_loc:
            tmpl = cv2.imread(str(thumb_path), cv2.IMREAD_GRAYSCALE)
            th, tw = tmpl.shape[:2]
            result.found_by_visual = True
            result.visual_location = {
                "x": best_loc[0],
                "y": best_loc[1],
                "w": int(tw * best_scale),
                "h": int(th * best_scale),
            }

            if best_score >= 0.8:
                result.status = "FOUND"
                result.details = f"Visual match ({best_score:.0%}) at scale {best_scale:.2f}"
                report.total_found += 1
            else:
                result.status = "PARTIAL"
                result.details = f"Weak visual match ({best_score:.0%}) at scale {best_scale:.2f}"
                report.total_partial += 1
        else:
            result.status = "MISSING"
            result.details = f"No visual match (best: {best_score:.0%})"
            report.total_missing += 1

        results.append(result)

    report.results = results
    if report.total_required > 0:
        report.score = (
            report.total_found + 0.5 * report.total_partial
        ) / report.total_required

    return report


def compare_symbols_combined(
    ocr_result: OCRResult,
    image_path: Path | None = None,
    required_symbols: list[SymbolEntry] | None = None,
    library: SymbolLibrary | None = None,
) -> SymbolComparisonReport:
    """
    Combined text + visual comparison for best accuracy.

    Runs text comparison first, then visual comparison for symbols
    not found by text. Merges results.
    """
    if library is None:
        library = get_symbol_library()
    library.load()

    if required_symbols is None:
        required_symbols = _get_required_symbols(library)

    # Text comparison
    text_report = compare_symbols_text(ocr_result, required_symbols, library)

    if image_path is None:
        return text_report

    # Find symbols still missing after text check
    missing_syms = [
        r.symbol for r in text_report.results
        if r.status == "MISSING"
    ]

    if not missing_syms:
        return text_report

    # Visual comparison on missing symbols only
    visual_report = compare_symbols_visual(
        image_path, missing_syms, library,
    )

    # Merge: update text results with visual findings
    visual_map = {r.symbol.row: r for r in visual_report.results}

    merged_results = []
    found = 0
    partial = 0
    missing = 0

    for tr in text_report.results:
        if tr.status != "MISSING":
            merged_results.append(tr)
            if tr.status == "FOUND":
                found += 1
            else:
                partial += 1
            continue

        # Check if visual matched
        vr = visual_map.get(tr.symbol.row)
        if vr and vr.status in ("FOUND", "PARTIAL"):
            tr.found_by_visual = True
            tr.visual_score = vr.visual_score
            tr.visual_location = vr.visual_location
            tr.status = vr.status
            tr.details = f"Text: not found → Visual: {vr.details}"
            if vr.status == "FOUND":
                found += 1
            else:
                partial += 1
        else:
            missing += 1
        merged_results.append(tr)

    report = SymbolComparisonReport(
        total_required=len(required_symbols),
        total_found=found,
        total_partial=partial,
        total_missing=missing,
        results=merged_results,
    )
    if report.total_required > 0:
        report.score = (found + 0.5 * partial) / report.total_required

    return report


# ── Private helpers ───────────────────────────────────


def _get_required_symbols(library: SymbolLibrary) -> list[SymbolEntry]:
    """Get the default set of required symbols for breast implant labels."""
    seen_rows = set()
    required = []

    # All ISO 15223 symbols
    for sym in library.get_iso15223_symbols():
        if sym.row not in seen_rows:
            seen_rows.add(sym.row)
            required.append(sym)

    # Breast-implant-specific symbols from the library
    for sym in library.get_expected_symbols_for_breast_implant():
        if sym.row not in seen_rows:
            seen_rows.add(sym.row)
            required.append(sym)

    return required


def _match_pkg_text(
    pkg_text: str,
    ifu_text: str,
    label_text_lower: str,
    label_full_text: str,
) -> tuple[bool, list[str], float]:
    """
    Check if expected package text appears on the label.

    Returns (found, matched_fragments, score).
    """
    matched: list[str] = []
    total_words = 0
    matched_words = 0

    # Split expected text into meaningful tokens
    for expected in (pkg_text, ifu_text):
        if not expected or expected.lower() in ("none", "no text required", "text not required"):
            continue

        # Clean HTML tags
        clean = re.sub(r"<br\s*/?>", " ", expected)
        clean = re.sub(r"<[^>]+>", "", clean)
        clean = re.sub(r"&amp;", "&", clean)

        words = re.findall(r'\b[a-zA-Z0-9]{2,}\b', clean.lower())
        total_words += len(words)

        for word in words:
            if word in label_text_lower:
                matched_words += 1
                if word not in matched:
                    matched.append(word)

        # Also try the full phrase
        clean_lower = clean.strip().lower()
        if len(clean_lower) > 3 and clean_lower in label_text_lower:
            matched.insert(0, clean.strip())

    if total_words == 0:
        return True, ["no text required"], 1.0

    score = matched_words / total_words if total_words > 0 else 0.0
    found = score >= 0.3 or len(matched) > 0

    return found, matched, score


def _multi_scale_match(
    label_img: np.ndarray,
    template_path: Path,
    scales: list[float] | None = None,
) -> tuple[float, tuple[int, int] | None, float]:
    """
    Multi-scale template matching.

    Returns (best_score, best_location, best_scale).
    """
    if scales is None:
        scales = [0.5, 0.75, 1.0, 1.25, 1.5]

    tmpl = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
    if tmpl is None:
        return 0.0, None, 1.0

    best_score = 0.0
    best_loc = None
    best_scale = 1.0

    for scale in scales:
        th, tw = tmpl.shape[:2]
        new_w = int(tw * scale)
        new_h = int(th * scale)

        if new_w < 10 or new_h < 10:
            continue
        if new_w > label_img.shape[1] or new_h > label_img.shape[0]:
            continue

        resized = cv2.resize(tmpl, (new_w, new_h))

        try:
            result = cv2.matchTemplate(label_img, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > best_score:
                best_score = max_val
                best_loc = max_loc
                best_scale = scale
        except cv2.error:
            continue

    return best_score, best_loc, best_scale
