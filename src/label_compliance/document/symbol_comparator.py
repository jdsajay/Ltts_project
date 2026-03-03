"""
Symbol Comparator
==================
Compares symbols found on a label against the Symbol Library database.

Three comparison modes:
1. **Text comparison** — Matches OCR-extracted text against the library's
   expected `pkg_text` and `ifu_text` fields.
2. **Visual comparison** — Matches extracted symbol images from the label
   against reference thumbnail images from the library using template matching.
3. **AI Vision comparison** — Uses AI (GPT-4o / Ollama vision) to identify
   symbols in the label image and match against the library.

Reports:
- Which required symbols are present on the label
- Which required symbols are missing
- Which symbols on the label don't match library entries
- Text discrepancies (expected vs actual text next to symbols)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import numpy as np

from label_compliance.document.ocr import OCRResult
from label_compliance.document.symbol_library_db import (
    SymbolEntry,
    SymbolLibrary,
    get_symbol_library,
)
from label_compliance.utils.log import get_logger

if TYPE_CHECKING:
    from label_compliance.ai.base import AIProvider

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

    # Pre-process: downscale large images aggressively for template matching.
    # Template matching doesn't need high resolution — 1000px is sufficient.
    lh, lw = label_img.shape[:2]
    downscale_factor = 1.0
    _MAX_DIM_FOR_MATCHING = 1000
    if max(lw, lh) > _MAX_DIM_FOR_MATCHING:
        downscale_factor = float(_MAX_DIM_FOR_MATCHING) / max(lw, lh)
        label_img_search = cv2.resize(
            label_img,
            (int(lw * downscale_factor), int(lh * downscale_factor)),
        )
        logger.info(
            "Downscaled %dx%d label → %dx%d for template matching (factor %.2f)",
            lw, lh, label_img_search.shape[1], label_img_search.shape[0],
            downscale_factor,
        )
    else:
        label_img_search = label_img

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

        # Template matching at multiple scales (auto-computed)
        best_score, best_loc, best_scale = _multi_scale_match(
            label_img_search, thumb_path,
        )

        result.visual_score = best_score

        if best_score >= confidence_threshold and best_loc:
            tmpl = cv2.imread(str(thumb_path), cv2.IMREAD_GRAYSCALE)
            th, tw = tmpl.shape[:2]
            # Map back to original image coordinates if downscaled
            result.found_by_visual = True
            result.visual_location = {
                "x": int(best_loc[0] / downscale_factor),
                "y": int(best_loc[1] / downscale_factor),
                "w": int(tw * best_scale / downscale_factor),
                "h": int(th * best_scale / downscale_factor),
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


# ── AI Vision Symbol Detection Prompt ────────────────

_AI_SYMBOL_PROMPT = """You are an expert at identifying regulatory and ISO symbols on medical device labels.

Examine this label image carefully and identify ALL symbols/icons/pictograms you can see.
For each symbol found, provide:
- "name": what the symbol represents (e.g., "Manufacturer", "Use-by date", "Do not reuse", "CE Mark", "Sterilized using ethylene oxide", "Consult instructions for use", "Lot number", "Catalog number", "Medical Device", "UDI carrier")
- "iso_ref": the ISO standard reference if known (e.g., "ISO 15223-1:5.1.1" for Manufacturer)
- "text_near_symbol": any text printed next to or below the symbol
- "confidence": how sure you are (0.0-1.0)

Also identify:
- Barcodes (1D, 2D/DataMatrix, QR codes) and what text is near them
- CE marks (with or without notified body number)
- Any regulatory marks (UL, CSA, TUV, etc.)
- Warning/caution symbols
- Material/recycling symbols

Required symbols to specifically look for:
{symbol_checklist}

Respond with JSON only:
{{
  "symbols_found": [
    {{"name": "...", "iso_ref": "...", "text_near_symbol": "...", "confidence": 0.9}},
    ...
  ],
  "barcodes_found": [
    {{"type": "DataMatrix|QR|1D", "text_near": "..."}},
    ...
  ],
  "total_symbols_detected": 0,
  "checklist_results": [
    {{"symbol_name": "...", "found": true, "confidence": 0.9, "evidence": "..."}},
    ...
  ]
}}"""


def compare_symbols_ai_vision(
    image_path: Path,
    ai_provider: "AIProvider",
    required_symbols: list[SymbolEntry] | None = None,
    library: SymbolLibrary | None = None,
) -> SymbolComparisonReport:
    """
    Use AI vision to identify symbols in a label image and compare
    against the symbol library.

    This is the most accurate method for complex real-world label images,
    especially image-only PDFs where template matching struggles with
    scale, rotation, and artistic variations.

    Args:
        image_path: Path to the label image (full page or cropped section).
        ai_provider: AI provider instance (GPT-4o or Ollama vision).
        required_symbols: Symbols to look for. Defaults to all standard symbols.
        library: Symbol library instance.

    Returns:
        SymbolComparisonReport with AI vision results.
    """
    if library is None:
        library = get_symbol_library()
    library.load()

    if required_symbols is None:
        required_symbols = _get_required_symbols(library)

    # Build the checklist for the prompt
    checklist_lines = []
    for sym in required_symbols:
        desc = sym.name
        if sym.pkg_text and sym.pkg_text.lower() not in ("no text required", "text not required", "none", "na", "n/a"):
            desc += f' (expected text: "{sym.pkg_text}")'
        checklist_lines.append(f"- {desc}")

    checklist_str = "\n".join(checklist_lines[:50])  # Limit to avoid token overflow

    prompt = _AI_SYMBOL_PROMPT.format(symbol_checklist=checklist_str)

    logger.info("AI vision symbol detection on %s (%d required symbols)...", image_path.name, len(required_symbols))

    try:
        raw_response = ai_provider.analyze_with_image(prompt, str(image_path))
    except Exception as e:
        logger.error("AI vision symbol detection failed: %s", e)
        return SymbolComparisonReport(
            total_required=len(required_symbols),
            total_missing=len(required_symbols),
        )

    # Parse AI response
    ai_symbols = _parse_ai_symbol_response(raw_response)
    if not ai_symbols:
        logger.warning("AI returned no symbol results, response: %s", raw_response[:200])
        return SymbolComparisonReport(
            total_required=len(required_symbols),
            total_missing=len(required_symbols),
        )

    # Match AI-detected symbols against required symbols
    report = SymbolComparisonReport(total_required=len(required_symbols))
    results: list[SymbolComparisonResult] = []

    for sym in required_symbols:
        result = SymbolComparisonResult(
            symbol=sym,
            expected_text=sym.pkg_text,
        )

        # Try to match this library symbol against AI detections
        best_match = _match_symbol_to_ai_detections(sym, ai_symbols)

        if best_match:
            confidence = best_match.get("confidence", 0.5)
            evidence = best_match.get("evidence", best_match.get("name", ""))
            text_near = best_match.get("text_near_symbol", "")

            result.found_by_visual = True
            result.visual_score = confidence

            if confidence >= 0.7:
                result.status = "FOUND"
                result.details = f"AI vision: {evidence}"
                if text_near:
                    result.details += f" (text: {text_near})"
                report.total_found += 1
            else:
                result.status = "PARTIAL"
                result.details = f"AI vision (low confidence {confidence:.0%}): {evidence}"
                report.total_partial += 1
        else:
            result.status = "MISSING"
            result.details = f"AI vision: symbol not detected"
            report.total_missing += 1

        results.append(result)

    report.results = results
    if report.total_required > 0:
        report.score = (
            report.total_found + 0.5 * report.total_partial
        ) / report.total_required

    logger.info(
        "AI vision symbols: %d found, %d partial, %d missing (score: %.0f%%)",
        report.total_found, report.total_partial, report.total_missing,
        report.score * 100,
    )
    return report


def _parse_ai_symbol_response(raw: str) -> list[dict]:
    """Parse the AI's JSON response for symbol detection."""
    try:
        # Strip markdown code blocks
        text = raw.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        data = json.loads(text)

        # Extract symbols_found and checklist_results
        symbols = data.get("symbols_found", [])
        checklist = data.get("checklist_results", [])

        # Merge checklist into symbols for matching
        all_detections = list(symbols)
        for item in checklist:
            if item.get("found", False):
                all_detections.append({
                    "name": item.get("symbol_name", ""),
                    "confidence": item.get("confidence", 0.7),
                    "evidence": item.get("evidence", ""),
                    "text_near_symbol": "",
                })

        return all_detections

    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("Failed to parse AI symbol response: %s", e)
        # Attempt regex extraction
        detections = []
        # Look for symbol names in the raw text
        for m in re.finditer(r'"name"\s*:\s*"([^"]+)"', raw):
            detections.append({"name": m.group(1), "confidence": 0.6})
        return detections


def _match_symbol_to_ai_detections(
    sym: SymbolEntry,
    ai_detections: list[dict],
) -> dict | None:
    """
    Try to match a library symbol entry against AI-detected symbols.

    Uses fuzzy name matching and keyword overlap.
    """
    sym_name_lower = sym.name.lower()
    sym_pkg_lower = sym.pkg_text.lower() if sym.pkg_text else ""

    # Build keyword set from the symbol entry
    sym_keywords = set(re.findall(r'[a-z]{3,}', sym_name_lower))
    if sym_pkg_lower:
        sym_keywords.update(re.findall(r'[a-z]{3,}', sym_pkg_lower))

    # Common synonym mappings for ISO symbols
    _SYNONYMS = {
        "manufacturer": ["manufacturer", "mfg", "made by", "produced by", "factory"],
        "use-by": ["use-by", "use by", "expiry", "expiration", "exp date", "use before"],
        "lot": ["lot", "batch", "lot number", "batch number", "lotno"],
        "catalog": ["catalog", "catalogue", "cat no", "ref", "reference number", "catno"],
        "serial": ["serial", "serial number", "sn", "serno"],
        "sterile": ["sterile", "sterilized", "sterilised", "ethylene oxide", "eo", "radiation", "aseptic"],
        "single use": ["single use", "do not reuse", "do not re-use", "single-use", "disposable"],
        "caution": ["caution", "warning", "attention"],
        "consult": ["consult", "instructions", "ifu", "see instructions", "refer to"],
        "ce mark": ["ce mark", "ce", "conformité européenne", "ce marking"],
        "medical device": ["medical device", "md", "medical"],
        "udi": ["udi", "unique device", "device identifier"],
        "temperature": ["temperature", "storage", "store at", "°c", "degrees"],
        "humidity": ["humidity", "moisture", "keep dry", "dry"],
        "latex": ["latex", "natural rubber"],
        "do not use": ["do not use", "damaged", "if damaged"],
        "date of manufacture": ["date of manufacture", "manufacturing date", "mfg date"],
        "authorized rep": ["authorized rep", "ec rep", "eu rep", "representative"],
        "importer": ["importer", "imported by"],
        "recycling": ["recycling", "recycle", "recyclable"],
        "barcode": ["barcode", "data matrix", "datamatrix", "qr code", "gs1"],
    }

    best_match = None
    best_score = 0.0

    for detection in ai_detections:
        det_name = detection.get("name", "").lower()
        det_text = detection.get("text_near_symbol", "").lower()
        det_conf = detection.get("confidence", 0.5)
        det_evidence = detection.get("evidence", det_name)

        score = 0.0

        # Direct name match
        if sym_name_lower in det_name or det_name in sym_name_lower:
            score = 0.9
        else:
            # Keyword overlap
            det_keywords = set(re.findall(r'[a-z]{3,}', det_name))
            if det_text:
                det_keywords.update(re.findall(r'[a-z]{3,}', det_text))

            if sym_keywords and det_keywords:
                overlap = len(sym_keywords & det_keywords)
                if overlap > 0:
                    score = overlap / max(len(sym_keywords), 1) * 0.8

            # Synonym matching
            for key, synonyms in _SYNONYMS.items():
                sym_matches_key = any(s in sym_name_lower or s in sym_pkg_lower for s in synonyms)
                det_matches_key = any(s in det_name or s in det_text for s in synonyms)
                if sym_matches_key and det_matches_key:
                    score = max(score, 0.85)
                    break

        if score > best_score and score >= 0.3:
            best_score = score
            best_match = {
                **detection,
                "confidence": min(score, det_conf),
                "evidence": det_evidence,
            }

    return best_match


def compare_symbols_combined(
    ocr_result: OCRResult,
    image_path: Path | None = None,
    required_symbols: list[SymbolEntry] | None = None,
    library: SymbolLibrary | None = None,
    ai_provider: "AIProvider | None" = None,
    skip_visual: bool = False,
) -> SymbolComparisonReport:
    """
    Combined text + visual + AI vision comparison for best accuracy.

    Pipeline:
    1. Text comparison (OCR text vs expected pkg_text) — fast
    2. Visual template matching for missing symbols — medium accuracy
       (skipped if skip_visual=True or ai_provider is available)
    3. AI vision for still-missing symbols — highest accuracy

    Args:
        ocr_result: OCR output from the label.
        image_path: Path to label image for visual and AI matching.
        required_symbols: Specific symbols to check. Defaults to all required.
        library: Symbol library instance.
        ai_provider: AI provider for vision-based symbol detection.
            If provided, used as final fallback for missing symbols.
        skip_visual: If True, skip template matching (useful for image-only
            PDFs where AI vision is more accurate and faster).
    """
    if library is None:
        library = get_symbol_library()
    library.load()

    if required_symbols is None:
        required_symbols = _get_required_symbols(library)

    # ── Stage 1: Text comparison ──
    text_report = compare_symbols_text(ocr_result, required_symbols, library)

    if image_path is None:
        return text_report

    # Find symbols still missing after text check
    missing_after_text = [
        r.symbol for r in text_report.results
        if r.status == "MISSING"
    ]

    if not missing_after_text:
        return text_report

    # ── Stage 2: Visual template matching for missing symbols ──
    # Skip visual template matching when AI provider is available (faster
    # and more accurate), or when explicitly requested via skip_visual.
    use_visual = not skip_visual and not ai_provider

    merged_results = []
    still_missing_syms = []
    found = 0
    partial = 0
    missing = 0

    if use_visual:
        visual_report = compare_symbols_visual(
            image_path, missing_after_text, library,
        )
        visual_map = {r.symbol.row: r for r in visual_report.results}
    else:
        visual_map = {}
        logger.info(
            "Skipping template matching (%d symbols) — %s",
            len(missing_after_text),
            "AI vision will handle" if ai_provider else "skip_visual=True",
        )

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
            still_missing_syms.append(tr.symbol)
            missing += 1
        merged_results.append(tr)

    # ── Stage 3: AI Vision for still-missing symbols ──
    if ai_provider and still_missing_syms and image_path:
        logger.info(
            "AI vision symbol detection for %d still-missing symbols...",
            len(still_missing_syms),
        )
        try:
            ai_report = compare_symbols_ai_vision(
                image_path, ai_provider, still_missing_syms, library,
            )
            ai_map = {r.symbol.row: r for r in ai_report.results}

            # Update merged results with AI findings
            updated_results = []
            found = 0
            partial = 0
            missing = 0
            for mr in merged_results:
                if mr.status == "MISSING" and mr.symbol.row in ai_map:
                    ar = ai_map[mr.symbol.row]
                    if ar.status in ("FOUND", "PARTIAL"):
                        mr.found_by_visual = True
                        mr.visual_score = ar.visual_score
                        mr.status = ar.status
                        mr.details = f"Text: not found → Template: not found → AI: {ar.details}"
                updated_results.append(mr)
                if mr.status == "FOUND":
                    found += 1
                elif mr.status == "PARTIAL":
                    partial += 1
                else:
                    missing += 1
            merged_results = updated_results
        except Exception as e:
            logger.error("AI vision symbol detection failed: %s", e)
            # Counts stay as-is from stage 2

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


# Breast-implant-specific symbol names (ISO 14607 + ISO 15223 + EU MDR)
_BREAST_IMPLANT_SYMBOL_KEYWORDS = [
    "manufacturer",
    "date of manufacture",
    "use by date",
    "lot",
    "serial",
    "cataloge number",   # matches library spelling
    "model number",
    "sterile",            # matches multiple sterile variants
    "do not re-use",
    "do not resterilize",
    "caution",
    "consult instruction",
    "medical device",
    "unique device identifier",
    "ce mark",
    "ce 0120",
    "ce 0123",
    "ec rep",
    "eu rep",
    "us rep",
    "importer",
    "temperature limit",
    "no latex",
    "non-pyrogenic",
    "single use",
    "packaging damaged",
    "country of manufacture",
    "rx only",
    "mentor",             # breast implant product graphics
]


def _get_required_symbols(library: SymbolLibrary) -> list[SymbolEntry]:
    """Get the default set of required symbols for breast implant labels.

    Uses a curated list of ~25 symbol keywords relevant to ISO 14607
    breast implant labels, instead of all 137 symbols in the library.
    This dramatically improves template matching performance.
    """
    seen_rows = set()
    required = []

    for sym in library.symbols:
        if not sym.is_active or sym.row in seen_rows:
            continue
        name_lower = sym.name.lower()
        # Check if this symbol matches any breast-implant keyword
        for kw in _BREAST_IMPLANT_SYMBOL_KEYWORDS:
            if kw in name_lower:
                seen_rows.add(sym.row)
                required.append(sym)
                break

    logger.debug(
        "Required symbols for breast implant: %d (from %d total)",
        len(required), len(library.symbols),
    )
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

    Automatically computes the correct scale range based on
    label image size vs template size (handles the 200px template
    vs 6600-9632px label image scale mismatch).

    Returns (best_score, best_location, best_scale).
    """
    tmpl = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
    if tmpl is None:
        return 0.0, None, 1.0

    th, tw = tmpl.shape[:2]
    lh, lw = label_img.shape[:2]

    if scales is None:
        # Auto-compute scales: symbols on a label are typically 2-8% of
        # image width.  On a 1000px downscaled label, symbols are ~20-80px.
        # With 200px templates, we need scales ~0.1-0.4.
        # Use fewer fractions for speed (4 base scales instead of 6).
        expected_sym_sizes = [
            int(lw * frac) for frac in [0.02, 0.04, 0.06, 0.08]
        ]
        scales = sorted(set(
            round(sz / tw, 2)
            for sz in expected_sym_sizes
            if sz >= 10
        ))
        # Add ±15% around each scale for fine-tuning (fewer than before)
        fine_scales = []
        for s in scales:
            fine_scales.extend([s * 0.85, s, s * 1.15])
        scales = sorted(set(round(s, 2) for s in fine_scales if s >= 0.05))

        logger.debug(
            "Auto-computed template scales for %dx%d label vs %dx%d template: %s",
            lw, lh, tw, th, scales,
        )

    best_score = 0.0
    best_loc = None
    best_scale = 1.0

    for scale in scales:
        new_w = int(tw * scale)
        new_h = int(th * scale)

        if new_w < 10 or new_h < 10:
            continue
        if new_w > lw or new_h > lh:
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
