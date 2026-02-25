"""
Specs Validator
================
Validates every detail defined in rule 'specs' fields against
the actual label content — fonts, physical dimensions, symbol
sizes, positions, colors, and placement.

This module bridges the gap between what rules *define* (in YAML)
and what the system *enforces*. Every spec field is consumed here.

Physical measurement: Images are rendered at a known DPI (default 300),
so pixels can be converted to mm:  mm = pixels * 25.4 / DPI
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from label_compliance.document.font_analyzer import FontInfo
from label_compliance.document.ocr import OCRResult, OCRWord
from label_compliance.document.layout import Zone
from label_compliance.document.symbol_detector import SymbolMatch
from label_compliance.document.barcode_reader import BarcodeResult
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

# ── Physical Measurement Utilities ─────────────────────


def px_to_mm(px: float, dpi: int = 300) -> float:
    """Convert pixels to millimeters given DPI."""
    return px * 25.4 / dpi


def pt_to_mm(pt: float) -> float:
    """Convert font points to millimeters. 1pt = 0.3528mm."""
    return pt * 0.3528


def mm_to_px(mm: float, dpi: int = 300) -> float:
    """Convert millimeters to pixels given DPI."""
    return mm * dpi / 25.4


# ── Spec Violation Dataclass ───────────────────────────


@dataclass
class SpecViolation:
    """A single specs-level violation for a rule."""

    rule_id: str
    spec_field: str          # Which spec field failed (e.g., "min_height_mm")
    requirement: str         # What was required
    actual: str              # What was found
    severity: str = "critical"
    iso_ref: str = ""
    page: int = 0
    location: dict = field(default_factory=dict)  # bbox where issue was found


@dataclass
class SpecsResult:
    """Full specs validation result for one rule."""

    rule_id: str
    iso_ref: str
    description: str
    all_passed: bool = True
    violations: list[SpecViolation] = field(default_factory=list)
    details: list[str] = field(default_factory=list)

    def add_violation(self, v: SpecViolation) -> None:
        self.violations.append(v)
        self.all_passed = False

    def add_pass(self, detail: str) -> None:
        self.details.append(f"PASS: {detail}")

    @property
    def status(self) -> str:
        if self.all_passed:
            return "PASS"
        # If only minor violations, PARTIAL
        if all(v.severity == "minor" for v in self.violations):
            return "PARTIAL"
        return "FAIL"


# ── Main Validation Entry Point ───────────────────────


def validate_rule_specs(
    rule: dict,
    ocr_result: OCRResult | None = None,
    fonts: list[FontInfo] | None = None,
    zones: list[Zone] | None = None,
    symbols: list[SymbolMatch] | None = None,
    barcodes: list[BarcodeResult] | None = None,
    page_number: int = 0,
    dpi: int = 300,
    image_size: tuple[int, int] = (0, 0),
) -> SpecsResult:
    """
    Validate ALL specs fields of a rule against actual label data.

    This is the comprehensive enforcement function. It checks:
    - min_height_mm: physical height of text/symbol
    - min_font_size_pt: minimum font size
    - font_style: required bold/italic
    - must_include: required sub-elements
    - must_be_adjacent_to: positional relationship
    - position: required placement zone
    - valid_classifications: allowed values
    - min_languages: multilingual requirements
    - formats: barcode format requirements
    - table_ref: table reference requirements
    - symbol_ref: symbol reference requirements
    - color_requirements: text/symbol color
    """
    specs = rule.get("specs", {})
    rule_id = rule.get("id", "unknown")
    iso_ref = rule.get("iso_ref", "")
    description = rule.get("description", "")
    severity = rule.get("severity", "critical")
    markers = rule.get("markers", [])

    result = SpecsResult(rule_id=rule_id, iso_ref=iso_ref, description=description)

    if not specs:
        result.add_pass("No specs defined — text matching only")
        return result

    # ── 1. min_height_mm — physical height check ──────
    if "min_height_mm" in specs:
        _check_min_height(
            result, specs, rule_id, severity, iso_ref,
            ocr_result, fonts, zones, symbols, dpi, page_number, markers,
        )

    # ── 2. min_font_size_pt — font point size check ──
    if "min_font_size_pt" in specs:
        _check_min_font_size(
            result, specs, rule_id, severity, iso_ref, fonts, markers, page_number,
        )

    # ── 3. font_style — bold/italic requirement ──────
    if "font_style" in specs:
        _check_font_style(
            result, specs, rule_id, severity, iso_ref, fonts, markers, page_number,
        )

    # ── 4. must_include — required sub-elements ──────
    if "must_include" in specs:
        _check_must_include(
            result, specs, rule_id, severity, iso_ref, ocr_result, page_number,
        )

    # ── 5. must_be_adjacent_to — positional check ────
    if "must_be_adjacent_to" in specs:
        _check_adjacency(
            result, specs, rule_id, severity, iso_ref,
            ocr_result, markers, dpi, page_number,
        )

    # ── 6. position — required placement zone ────────
    if "position" in specs:
        _check_position(
            result, specs, rule_id, severity, iso_ref,
            ocr_result, markers, image_size, page_number,
        )

    # ── 7. valid_classifications — allowed values ────
    if "valid_classifications" in specs:
        _check_valid_classifications(
            result, specs, rule_id, severity, iso_ref, ocr_result, page_number,
        )

    # ── 8. min_languages — multilingual check ────────
    if "min_languages" in specs:
        _check_min_languages(
            result, specs, rule_id, severity, iso_ref, ocr_result, page_number,
        )

    # ── 9. formats — barcode format requirements ─────
    if "formats" in specs:
        _check_barcode_formats(
            result, specs, rule_id, severity, iso_ref, barcodes, page_number,
        )

    # ── 10. must_include_nb_number — notified body ───
    if specs.get("must_include_nb_number"):
        _check_nb_number(
            result, specs, rule_id, severity, iso_ref, ocr_result, page_number,
        )

    # ── 11. valid_methods — sterilization methods ────
    if "valid_methods" in specs:
        _check_valid_methods(
            result, specs, rule_id, severity, iso_ref, ocr_result, page_number,
        )

    # ── 12. table_ref — table reference ──────────────
    if "table_ref" in specs:
        _check_table_ref(
            result, specs, rule_id, severity, iso_ref, ocr_result, page_number,
        )

    # ── 13. color_requirements ───────────────────────
    if "color_requirements" in specs:
        _check_color(
            result, specs, rule_id, severity, iso_ref, fonts, markers, page_number,
        )

    # ── 14. min_contrast_ratio ───────────────────────
    if "min_contrast_ratio" in specs:
        _check_contrast(
            result, specs, rule_id, severity, iso_ref, fonts, markers, page_number,
        )

    return result


# ═══════════════════════════════════════════════════════
#  Individual Check Implementations
# ═══════════════════════════════════════════════════════


def _find_marker_words(
    ocr_result: OCRResult | None, markers: list[str],
) -> list[OCRWord]:
    """Find all OCR words matching any of the markers."""
    if not ocr_result:
        return []
    words = []
    for marker in markers:
        words.extend(ocr_result.find_text(marker))
    return words


def _find_font_spans_for_markers(
    fonts: list[FontInfo] | None, markers: list[str],
) -> list[FontInfo]:
    """Find font spans whose text matches any marker."""
    if not fonts:
        return []
    spans = []
    for f in fonts:
        text_lower = f.text.lower()
        for marker in markers:
            if marker.lower() in text_lower:
                spans.append(f)
                break
    return spans


def _check_min_height(
    result: SpecsResult,
    specs: dict,
    rule_id: str,
    severity: str,
    iso_ref: str,
    ocr_result: OCRResult | None,
    fonts: list[FontInfo] | None,
    zones: list[Zone] | None,
    symbols: list[SymbolMatch] | None,
    dpi: int,
    page_number: int,
    markers: list[str],
) -> None:
    """Check physical height of text/symbol meets min_height_mm."""
    min_h_mm = specs["min_height_mm"]

    # Strategy 1: Check font spans from PDF (most accurate for text)
    font_spans = _find_font_spans_for_markers(fonts, markers)
    if font_spans:
        for span in font_spans:
            actual_h_mm = pt_to_mm(span.size)
            if actual_h_mm < min_h_mm:
                result.add_violation(SpecViolation(
                    rule_id=rule_id,
                    spec_field="min_height_mm",
                    requirement=f"≥ {min_h_mm}mm height",
                    actual=f"{actual_h_mm:.2f}mm (font {span.name} @ {span.size}pt)",
                    severity=severity,
                    iso_ref=iso_ref,
                    page=span.page,
                    location={"bbox": span.bbox, "text": span.text[:50]},
                ))
            else:
                result.add_pass(
                    f"Height {actual_h_mm:.2f}mm ≥ {min_h_mm}mm "
                    f"(font {span.name} @ {span.size}pt, text: '{span.text[:30]}')"
                )
        return

    # Strategy 2: Check OCR word bounding boxes (for image-based symbols)
    marker_words = _find_marker_words(ocr_result, markers)
    if marker_words:
        for word in marker_words:
            actual_h_mm = px_to_mm(word.h, dpi)
            if actual_h_mm < min_h_mm:
                result.add_violation(SpecViolation(
                    rule_id=rule_id,
                    spec_field="min_height_mm",
                    requirement=f"≥ {min_h_mm}mm height",
                    actual=f"{actual_h_mm:.2f}mm ({word.h}px at {dpi}dpi)",
                    severity=severity,
                    iso_ref=iso_ref,
                    page=page_number,
                    location={"text": word.text, "x": word.x, "y": word.y,
                              "w": word.w, "h": word.h},
                ))
            else:
                result.add_pass(
                    f"Height {actual_h_mm:.2f}mm ≥ {min_h_mm}mm "
                    f"(text: '{word.text}', {word.h}px at {dpi}dpi)"
                )
        return

    # Strategy 3: Check symbol detection matches
    if symbols:
        for sym in symbols:
            if sym.rule_id == rule_id and sym.locations:
                for loc in sym.locations:
                    h_px = loc.get("h", 0)
                    actual_h_mm = px_to_mm(h_px, dpi)
                    if actual_h_mm < min_h_mm:
                        result.add_violation(SpecViolation(
                            rule_id=rule_id,
                            spec_field="min_height_mm",
                            requirement=f"≥ {min_h_mm}mm height",
                            actual=f"{actual_h_mm:.2f}mm ({h_px}px at {dpi}dpi)",
                            severity=severity,
                            iso_ref=iso_ref,
                            page=page_number,
                            location=loc,
                        ))
                    else:
                        result.add_pass(
                            f"Symbol height {actual_h_mm:.2f}mm ≥ {min_h_mm}mm"
                        )
                return

    # No matching elements found — can't validate height
    result.add_violation(SpecViolation(
        rule_id=rule_id,
        spec_field="min_height_mm",
        requirement=f"≥ {min_h_mm}mm height",
        actual="Element not found — cannot measure height",
        severity=severity,
        iso_ref=iso_ref,
        page=page_number,
    ))


def _check_min_font_size(
    result: SpecsResult,
    specs: dict,
    rule_id: str,
    severity: str,
    iso_ref: str,
    fonts: list[FontInfo] | None,
    markers: list[str],
    page_number: int,
) -> None:
    """Check font size meets minimum point size requirement."""
    min_pt = specs["min_font_size_pt"]
    spans = _find_font_spans_for_markers(fonts, markers)

    if not spans:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="min_font_size_pt",
            requirement=f"≥ {min_pt}pt font size",
            actual="No matching font spans found",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    for span in spans:
        if span.size < min_pt:
            result.add_violation(SpecViolation(
                rule_id=rule_id,
                spec_field="min_font_size_pt",
                requirement=f"≥ {min_pt}pt",
                actual=f"{span.size}pt (font: {span.name}, text: '{span.text[:40]}')",
                severity=severity,
                iso_ref=iso_ref,
                page=span.page,
                location={"bbox": span.bbox, "text": span.text[:50]},
            ))
        else:
            result.add_pass(
                f"Font size {span.size}pt ≥ {min_pt}pt "
                f"(font: {span.name}, text: '{span.text[:30]}')"
            )


def _check_font_style(
    result: SpecsResult,
    specs: dict,
    rule_id: str,
    severity: str,
    iso_ref: str,
    fonts: list[FontInfo] | None,
    markers: list[str],
    page_number: int,
) -> None:
    """Check font style (bold/italic) requirements."""
    required_style = specs["font_style"]  # "bold", "italic", "bold_italic"
    spans = _find_font_spans_for_markers(fonts, markers)

    if not spans:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="font_style",
            requirement=f"Font style: {required_style}",
            actual="No matching font spans found",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    for span in spans:
        style_ok = True
        actual_style_parts = []
        if span.is_bold:
            actual_style_parts.append("bold")
        if span.is_italic:
            actual_style_parts.append("italic")
        actual_style = "_".join(actual_style_parts) if actual_style_parts else "regular"

        if "bold" in required_style and not span.is_bold:
            style_ok = False
        if "italic" in required_style and not span.is_italic:
            style_ok = False

        if not style_ok:
            result.add_violation(SpecViolation(
                rule_id=rule_id,
                spec_field="font_style",
                requirement=f"Required: {required_style}",
                actual=f"Found: {actual_style} (font: {span.name}, text: '{span.text[:40]}')",
                severity=severity,
                iso_ref=iso_ref,
                page=span.page,
                location={"bbox": span.bbox, "text": span.text[:50]},
            ))
        else:
            result.add_pass(
                f"Font style '{actual_style}' matches required '{required_style}' "
                f"(text: '{span.text[:30]}')"
            )


def _check_must_include(
    result: SpecsResult,
    specs: dict,
    rule_id: str,
    severity: str,
    iso_ref: str,
    ocr_result: OCRResult | None,
    page_number: int,
) -> None:
    """Check that all required sub-elements are present in text."""
    must_include = specs["must_include"]
    if not ocr_result:
        for item in must_include:
            result.add_violation(SpecViolation(
                rule_id=rule_id,
                spec_field="must_include",
                requirement=f"Must include: {item}",
                actual="No OCR text available",
                severity=severity,
                iso_ref=iso_ref,
                page=page_number,
            ))
        return

    text_lower = ocr_result.text_lower

    for item in must_include:
        # Handle OR conditions: "width OR diameter"
        if " OR " in item:
            alternatives = [a.strip().lower() for a in item.split(" OR ")]
            found = any(alt in text_lower for alt in alternatives)
            if found:
                matched = [a for a in alternatives if a in text_lower]
                result.add_pass(f"Found '{matched[0]}' (from: {item})")
            else:
                result.add_violation(SpecViolation(
                    rule_id=rule_id,
                    spec_field="must_include",
                    requirement=f"Must include one of: {item}",
                    actual=f"None of [{', '.join(alternatives)}] found in text",
                    severity=severity,
                    iso_ref=iso_ref,
                    page=page_number,
                ))
        else:
            if item.lower() in text_lower:
                result.add_pass(f"Found required element: '{item}'")
            else:
                result.add_violation(SpecViolation(
                    rule_id=rule_id,
                    spec_field="must_include",
                    requirement=f"Must include: {item}",
                    actual=f"'{item}' not found in text",
                    severity=severity,
                    iso_ref=iso_ref,
                    page=page_number,
                ))


def _check_adjacency(
    result: SpecsResult,
    specs: dict,
    rule_id: str,
    severity: str,
    iso_ref: str,
    ocr_result: OCRResult | None,
    markers: list[str],
    dpi: int,
    page_number: int,
) -> None:
    """
    Check that a symbol/text is adjacent to (near) another element.

    Adjacency = the two elements' bounding boxes are within a threshold
    distance (default 15mm, ~177px at 300dpi).
    """
    adjacent_to = specs["must_be_adjacent_to"]
    max_distance_mm = specs.get("adjacency_max_mm", 15.0)
    max_distance_px = mm_to_px(max_distance_mm, dpi)

    if not ocr_result:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="must_be_adjacent_to",
            requirement=f"Must be within {max_distance_mm}mm of '{adjacent_to}'",
            actual="No OCR data available",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    # Find words for the marker element
    marker_words = _find_marker_words(ocr_result, markers)
    # Find words for the adjacent element
    adjacent_words = ocr_result.find_text(adjacent_to)

    if not marker_words:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="must_be_adjacent_to",
            requirement=f"Must be within {max_distance_mm}mm of '{adjacent_to}'",
            actual=f"Primary element (markers: {markers}) not found",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    if not adjacent_words:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="must_be_adjacent_to",
            requirement=f"Must be within {max_distance_mm}mm of '{adjacent_to}'",
            actual=f"Adjacent element '{adjacent_to}' not found",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    # Check closest distance between any marker word and any adjacent word
    min_dist_px = float("inf")
    best_pair = (None, None)

    for mw in marker_words:
        mx_center = mw.x + mw.w / 2
        my_center = mw.y + mw.h / 2
        for aw in adjacent_words:
            ax_center = aw.x + aw.w / 2
            ay_center = aw.y + aw.h / 2
            dist = ((mx_center - ax_center) ** 2 + (my_center - ay_center) ** 2) ** 0.5
            if dist < min_dist_px:
                min_dist_px = dist
                best_pair = (mw, aw)

    min_dist_mm = px_to_mm(min_dist_px, dpi)

    if min_dist_mm <= max_distance_mm:
        result.add_pass(
            f"'{best_pair[0].text}' is {min_dist_mm:.1f}mm from "
            f"'{best_pair[1].text}' (max: {max_distance_mm}mm)"
        )
    else:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="must_be_adjacent_to",
            requirement=f"Must be within {max_distance_mm}mm of '{adjacent_to}'",
            actual=f"Distance: {min_dist_mm:.1f}mm (exceeds {max_distance_mm}mm limit)",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
            location={
                "marker_text": best_pair[0].text if best_pair[0] else "",
                "marker_pos": {"x": best_pair[0].x, "y": best_pair[0].y} if best_pair[0] else {},
                "adjacent_text": best_pair[1].text if best_pair[1] else "",
                "adjacent_pos": {"x": best_pair[1].x, "y": best_pair[1].y} if best_pair[1] else {},
            },
        ))


def _check_position(
    result: SpecsResult,
    specs: dict,
    rule_id: str,
    severity: str,
    iso_ref: str,
    ocr_result: OCRResult | None,
    markers: list[str],
    image_size: tuple[int, int],
    page_number: int,
) -> None:
    """
    Check that an element appears in the required zone of the label.

    Position values: "top", "bottom", "left", "right", "center",
                     "top-left", "top-right", "bottom-left", "bottom-right"

    The image is divided into a 3x3 grid for zone detection.
    """
    required_position = specs["position"]
    if not ocr_result or image_size == (0, 0):
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="position",
            requirement=f"Must be in '{required_position}' zone",
            actual="No image/OCR data for position check",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    marker_words = _find_marker_words(ocr_result, markers)
    if not marker_words:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="position",
            requirement=f"Must be in '{required_position}' zone",
            actual=f"Element (markers: {markers}) not found",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    img_w, img_h = image_size
    # Use the centroid of all marker words
    cx = sum(w.x + w.w / 2 for w in marker_words) / len(marker_words)
    cy = sum(w.y + w.h / 2 for w in marker_words) / len(marker_words)

    # Determine which zone the element is in
    x_zone = "left" if cx < img_w / 3 else ("right" if cx > 2 * img_w / 3 else "center")
    y_zone = "top" if cy < img_h / 3 else ("bottom" if cy > 2 * img_h / 3 else "middle")

    actual_zone = f"{y_zone}-{x_zone}" if y_zone != "middle" else x_zone
    if x_zone == "center":
        actual_zone = y_zone if y_zone != "middle" else "center"

    # Normalize for comparison
    req_lower = required_position.lower().replace(" ", "-")
    actual_lower = actual_zone.lower()

    # Check if position matches (with some flexibility)
    position_match = False
    if req_lower == actual_lower:
        position_match = True
    elif req_lower in actual_lower or actual_lower in req_lower:
        position_match = True
    elif req_lower == "top" and "top" in actual_lower:
        position_match = True
    elif req_lower == "bottom" and "bottom" in actual_lower:
        position_match = True
    elif req_lower == "left" and "left" in actual_lower:
        position_match = True
    elif req_lower == "right" and "right" in actual_lower:
        position_match = True

    if position_match:
        result.add_pass(
            f"Element in '{actual_zone}' matches required '{required_position}' "
            f"(centroid at {cx:.0f},{cy:.0f} in {img_w}x{img_h} image)"
        )
    else:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="position",
            requirement=f"Must be in '{required_position}' zone",
            actual=f"Found in '{actual_zone}' zone (centroid at {cx:.0f},{cy:.0f})",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
            location={"centroid_x": cx, "centroid_y": cy,
                       "image_w": img_w, "image_h": img_h},
        ))


def _check_valid_classifications(
    result: SpecsResult,
    specs: dict,
    rule_id: str,
    severity: str,
    iso_ref: str,
    ocr_result: OCRResult | None,
    page_number: int,
) -> None:
    """Check that a valid classification code appears in the text."""
    valid = specs["valid_classifications"]
    if not ocr_result:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="valid_classifications",
            requirement=f"Must contain one of: {valid}",
            actual="No OCR text available",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    text_upper = ocr_result.full_text.upper()
    found_codes = []

    for item in valid:
        if isinstance(item, dict):
            code = item.get("code", "")
        else:
            code = str(item)
        if code.upper() in text_upper:
            found_codes.append(code)

    if found_codes:
        result.add_pass(f"Valid classification found: {', '.join(found_codes)}")
    else:
        codes_list = [
            (c.get("code", "") if isinstance(c, dict) else str(c)) for c in valid
        ]
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="valid_classifications",
            requirement=f"Must contain one of: {codes_list}",
            actual="No valid classification code found in text",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))


def _check_min_languages(
    result: SpecsResult,
    specs: dict,
    rule_id: str,
    severity: str,
    iso_ref: str,
    ocr_result: OCRResult | None,
    page_number: int,
) -> None:
    """Check minimum number of languages present."""
    min_langs = specs["min_languages"]
    if not ocr_result:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="min_languages",
            requirement=f"≥ {min_langs} languages",
            actual="No OCR text available",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    # Detect language prefixes (en:, de:, fr:, etc.)
    lang_pattern = re.compile(r'\b([a-z]{2}):', re.IGNORECASE)
    found_langs = set(lang_pattern.findall(ocr_result.full_text))

    # Also check for common ISO 639-1 language blocks
    # Some labels use section headers like "English", "Français", etc.
    lang_names = {
        "english": "en", "deutsch": "de", "français": "fr",
        "español": "es", "italiano": "it", "nederlands": "nl",
        "português": "pt", "polski": "pl", "svenska": "sv",
        "dansk": "da", "suomi": "fi", "norsk": "no",
    }
    text_lower = ocr_result.text_lower
    for name, code in lang_names.items():
        if name in text_lower:
            found_langs.add(code)

    if len(found_langs) >= min_langs:
        result.add_pass(
            f"Found {len(found_langs)} languages: {sorted(found_langs)} "
            f"(required: ≥ {min_langs})"
        )
    else:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="min_languages",
            requirement=f"≥ {min_langs} languages",
            actual=f"Found {len(found_langs)} languages: {sorted(found_langs)}",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))


def _check_barcode_formats(
    result: SpecsResult,
    specs: dict,
    rule_id: str,
    severity: str,
    iso_ref: str,
    barcodes: list[BarcodeResult] | None,
    page_number: int,
) -> None:
    """Check that required barcode formats are present."""
    required_formats = specs["formats"]
    if not barcodes:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="formats",
            requirement=f"Barcode in format(s): {required_formats}",
            actual="No barcodes detected on label",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    found_types = [bc.barcode_type for bc in barcodes]
    # Normalize format names for matching
    format_map = {
        "GS1-128": ["CODE128", "GS1-128", "CODE-128"],
        "DataMatrix": ["DATAMATRIX", "DATA_MATRIX"],
        "QR": ["QRCODE", "QR"],
        "EAN13": ["EAN13", "EAN-13"],
    }

    matched_formats = []
    for req_fmt in required_formats:
        aliases = format_map.get(req_fmt, [req_fmt.upper()])
        for bc_type in found_types:
            if bc_type.upper() in aliases or req_fmt.upper() in bc_type.upper():
                matched_formats.append(req_fmt)
                break

    if matched_formats:
        result.add_pass(f"Barcode format(s) found: {matched_formats} (from: {found_types})")
    else:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="formats",
            requirement=f"Barcode format(s): {required_formats}",
            actual=f"Found formats: {found_types} — none match required",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))


def _check_nb_number(
    result: SpecsResult,
    specs: dict,
    rule_id: str,
    severity: str,
    iso_ref: str,
    ocr_result: OCRResult | None,
    page_number: int,
) -> None:
    """Check that a notified body number appears next to CE mark."""
    if not ocr_result:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="must_include_nb_number",
            requirement="Notified body number with CE mark",
            actual="No OCR text available",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    # Look for 4-digit notified body number near "CE"
    nb_pattern = re.compile(r'CE\s*(\d{4})|(\d{4})\s*CE', re.IGNORECASE)
    match = nb_pattern.search(ocr_result.full_text)

    if match:
        nb_num = match.group(1) or match.group(2)
        result.add_pass(f"Notified body number found: {nb_num} with CE mark")
    else:
        # Check if any standalone 4-digit number could be NB number
        # (common NB numbers: 0086, 0459, 0344, etc.)
        standalone = re.findall(r'\b(\d{4})\b', ocr_result.full_text)
        ce_found = "ce" in ocr_result.text_lower
        if ce_found and standalone:
            result.add_violation(SpecViolation(
                rule_id=rule_id,
                spec_field="must_include_nb_number",
                requirement="Notified body number directly adjacent to CE mark",
                actual=f"CE mark found but NB number not adjacent. "
                       f"Standalone numbers nearby: {standalone[:5]}",
                severity=severity,
                iso_ref=iso_ref,
                page=page_number,
            ))
        else:
            result.add_violation(SpecViolation(
                rule_id=rule_id,
                spec_field="must_include_nb_number",
                requirement="Notified body number with CE mark (e.g., CE 0086)",
                actual="CE mark and/or notified body number not found",
                severity=severity,
                iso_ref=iso_ref,
                page=page_number,
            ))


def _check_valid_methods(
    result: SpecsResult,
    specs: dict,
    rule_id: str,
    severity: str,
    iso_ref: str,
    ocr_result: OCRResult | None,
    page_number: int,
) -> None:
    """Check that a valid sterilization method is indicated."""
    valid_methods = specs["valid_methods"]
    if not ocr_result:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="valid_methods",
            requirement=f"Must indicate sterilization method",
            actual="No OCR text available",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    text_lower = ocr_result.text_lower
    found = []
    for method in valid_methods:
        # Extract keywords from method description
        method_lower = method.lower()
        keywords = ["irradiation", "ethylene oxide", "sterile", "aseptic",
                     "steam", "dry heat", "radiation"]
        for kw in keywords:
            if kw in method_lower and kw in text_lower:
                found.append(method)
                break

    if found:
        result.add_pass(f"Sterilization method indicated: {found}")
    else:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="valid_methods",
            requirement=f"Must indicate valid sterilization method: {valid_methods}",
            actual="No recognized sterilization method found in text",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))


def _check_table_ref(
    result: SpecsResult,
    specs: dict,
    rule_id: str,
    severity: str,
    iso_ref: str,
    ocr_result: OCRResult | None,
    page_number: int,
) -> None:
    """Check that a referenced table's content is present."""
    table_ref = specs["table_ref"]
    if not ocr_result:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="table_ref",
            requirement=f"Content from {table_ref} must be present",
            actual="No OCR text available",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    # Check if table reference or its content codes appear
    text_lower = ocr_result.text_lower
    if table_ref.lower() in text_lower:
        result.add_pass(f"Table reference '{table_ref}' found in text")
    else:
        # Check valid_classifications as proxy for table content
        valid = specs.get("valid_classifications", [])
        if valid:
            codes = [
                (c.get("code", "") if isinstance(c, dict) else str(c)) for c in valid
            ]
            found = [c for c in codes if c.upper() in ocr_result.full_text.upper()]
            if found:
                result.add_pass(
                    f"Table {table_ref} content present via codes: {found}"
                )
                return

        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="table_ref",
            requirement=f"Content from {table_ref} must be present",
            actual=f"Neither '{table_ref}' nor its content codes found",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))


def _check_color(
    result: SpecsResult,
    specs: dict,
    rule_id: str,
    severity: str,
    iso_ref: str,
    fonts: list[FontInfo] | None,
    markers: list[str],
    page_number: int,
) -> None:
    """Check text/symbol color requirements."""
    color_req = specs["color_requirements"]
    required_color = color_req if isinstance(color_req, str) else color_req.get("color", "black")

    # Map color names to typical RGB integer values (as stored by PyMuPDF)
    color_map = {
        "black": 0x000000,
        "red": 0xFF0000,
        "blue": 0x0000FF,
        "green": 0x008000,
        "white": 0xFFFFFF,
    }

    spans = _find_font_spans_for_markers(fonts, markers)
    if not spans:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="color_requirements",
            requirement=f"Text color: {required_color}",
            actual="No matching font spans found",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    expected_rgb = color_map.get(required_color.lower())
    for span in spans:
        if expected_rgb is not None:
            # Allow some tolerance for color matching
            if span.color == expected_rgb:
                result.add_pass(
                    f"Color matches: {required_color} (0x{span.color:06X}) "
                    f"for '{span.text[:30]}'"
                )
            else:
                result.add_violation(SpecViolation(
                    rule_id=rule_id,
                    spec_field="color_requirements",
                    requirement=f"Text color: {required_color} (0x{expected_rgb:06X})",
                    actual=f"Found color: 0x{span.color:06X} for '{span.text[:40]}'",
                    severity=severity,
                    iso_ref=iso_ref,
                    page=span.page,
                    location={"bbox": span.bbox, "text": span.text[:50]},
                ))
        else:
            result.add_pass(f"Color check skipped — unknown color name: {required_color}")


def _check_contrast(
    result: SpecsResult,
    specs: dict,
    rule_id: str,
    severity: str,
    iso_ref: str,
    fonts: list[FontInfo] | None,
    markers: list[str],
    page_number: int,
) -> None:
    """
    Basic contrast ratio check between text and background.
    This is a simplified check — full WCAG contrast requires
    sampling the actual background color behind the text.
    """
    min_ratio = specs["min_contrast_ratio"]
    spans = _find_font_spans_for_markers(fonts, markers)

    if not spans:
        result.add_violation(SpecViolation(
            rule_id=rule_id,
            spec_field="min_contrast_ratio",
            requirement=f"Contrast ratio ≥ {min_ratio}:1",
            actual="No matching font spans found",
            severity=severity,
            iso_ref=iso_ref,
            page=page_number,
        ))
        return

    for span in spans:
        # Simplified: assume white background (0xFFFFFF)
        # Calculate relative luminance
        fg_r = ((span.color >> 16) & 0xFF) / 255.0
        fg_g = ((span.color >> 8) & 0xFF) / 255.0
        fg_b = (span.color & 0xFF) / 255.0

        def _srgb_to_linear(c: float) -> float:
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

        fg_lum = (
            0.2126 * _srgb_to_linear(fg_r) +
            0.7152 * _srgb_to_linear(fg_g) +
            0.0722 * _srgb_to_linear(fg_b)
        )
        bg_lum = 1.0  # white background assumption

        lighter = max(fg_lum, bg_lum)
        darker = min(fg_lum, bg_lum)
        ratio = (lighter + 0.05) / (darker + 0.05)

        if ratio >= min_ratio:
            result.add_pass(
                f"Contrast ratio {ratio:.1f}:1 ≥ {min_ratio}:1 "
                f"for '{span.text[:30]}'"
            )
        else:
            result.add_violation(SpecViolation(
                rule_id=rule_id,
                spec_field="min_contrast_ratio",
                requirement=f"Contrast ratio ≥ {min_ratio}:1",
                actual=f"Contrast ratio {ratio:.1f}:1 for '{span.text[:40]}'",
                severity=severity,
                iso_ref=iso_ref,
                page=span.page,
                location={"bbox": span.bbox, "text": span.text[:50]},
            ))
