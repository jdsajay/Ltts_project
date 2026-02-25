"""Tests for the specs_validator module — comprehensive enforcement of ISO specs."""

import pytest

from label_compliance.compliance.specs_validator import (
    px_to_mm,
    pt_to_mm,
    mm_to_px,
    validate_rule_specs,
    SpecViolation,
    SpecsResult,
)
from label_compliance.document.ocr import OCRResult, OCRWord
from label_compliance.document.font_analyzer import FontInfo
from label_compliance.document.barcode_reader import BarcodeResult


# ── Unit conversion tests ────────────────────────────


def test_px_to_mm():
    # At 300 DPI, 1 inch = 300px = 25.4mm
    assert abs(px_to_mm(300, 300) - 25.4) < 0.01


def test_pt_to_mm():
    # 1pt = 0.3528mm; 6pt = 2.1168mm
    assert abs(pt_to_mm(6) - 2.1168) < 0.01


def test_mm_to_px():
    # 25.4mm = 300px at 300 DPI
    assert abs(mm_to_px(25.4, 300) - 300) < 0.01


# ── Helper to build OCRResult ────────────────────────


def _make_ocr(text: str, words: list[OCRWord] | None = None) -> OCRResult:
    return OCRResult(
        image_path="test.png",
        image_size=(2400, 3000),
        full_text=text,
        words=words or [],
    )


def _make_font(text: str, size: float, bold: bool = False, page: int = 1) -> FontInfo:
    return FontInfo(
        name="Helvetica",
        size=size,
        is_bold=bold,
        is_italic=False,
        text=text,
        page=page,
        bbox=(10, 10, 200, 30),
    )


# ── min_height_mm tests ─────────────────────────────


def test_min_height_pass_via_font():
    """Font at 10pt = 3.528mm → passes 3mm minimum."""
    rule = {
        "id": "TEST-HEIGHT-1",
        "iso_ref": "5.1.1",
        "description": "Test min height",
        "severity": "critical",
        "markers": ["manufacturer"],
        "specs": {"min_height_mm": 3},
    }
    fonts = [_make_font("manufacturer", 10.0)]
    result = validate_rule_specs(rule, fonts=fonts)
    assert result.all_passed


def test_min_height_fail_via_font():
    """Font at 5pt = 1.764mm → fails 3mm minimum."""
    rule = {
        "id": "TEST-HEIGHT-2",
        "iso_ref": "5.1.1",
        "description": "Test min height",
        "severity": "critical",
        "markers": ["manufacturer"],
        "specs": {"min_height_mm": 3},
    }
    fonts = [_make_font("manufacturer", 5.0)]
    result = validate_rule_specs(rule, fonts=fonts)
    assert not result.all_passed
    assert any(v.spec_field == "min_height_mm" for v in result.violations)


def test_min_height_via_ocr_bbox():
    """Falls back to OCR bounding box when no font spans match."""
    rule = {
        "id": "TEST-HEIGHT-3",
        "iso_ref": "5.1.3",
        "description": "Test min height OCR",
        "severity": "critical",
        "markers": ["LOT"],
        "specs": {"min_height_mm": 3},
    }
    # 36px at 300dpi = 3.048mm → passes
    words = [OCRWord(text="LOT", confidence=95, x=10, y=10, w=80, h=36)]
    ocr = _make_ocr("LOT 12345", words)
    result = validate_rule_specs(rule, ocr_result=ocr, dpi=300)
    assert result.all_passed


# ── min_font_size_pt tests ───────────────────────────


def test_min_font_size_pass():
    rule = {
        "id": "TEST-FONT-1",
        "iso_ref": "11.2",
        "description": "Font size check",
        "severity": "critical",
        "markers": ["volume"],
        "specs": {"min_font_size_pt": 8},
    }
    fonts = [_make_font("volume 150cc", 10.0)]
    result = validate_rule_specs(rule, fonts=fonts)
    assert result.all_passed


def test_min_font_size_fail():
    rule = {
        "id": "TEST-FONT-2",
        "iso_ref": "11.2",
        "description": "Font size check",
        "severity": "critical",
        "markers": ["volume"],
        "specs": {"min_font_size_pt": 8},
    }
    fonts = [_make_font("volume 150cc", 6.0)]
    result = validate_rule_specs(rule, fonts=fonts)
    assert not result.all_passed
    assert result.violations[0].spec_field == "min_font_size_pt"


# ── font_style tests ────────────────────────────────


def test_font_style_bold_pass():
    rule = {
        "id": "TEST-STYLE-1",
        "iso_ref": "11.2",
        "description": "Bold check",
        "severity": "major",
        "markers": ["volume"],
        "specs": {"font_style": "bold"},
    }
    fonts = [_make_font("volume 150cc", 10.0, bold=True)]
    result = validate_rule_specs(rule, fonts=fonts)
    assert result.all_passed


def test_font_style_bold_fail():
    rule = {
        "id": "TEST-STYLE-2",
        "iso_ref": "11.2",
        "description": "Bold check",
        "severity": "major",
        "markers": ["volume"],
        "specs": {"font_style": "bold"},
    }
    fonts = [_make_font("volume 150cc", 10.0, bold=False)]
    result = validate_rule_specs(rule, fonts=fonts)
    assert not result.all_passed
    assert result.violations[0].spec_field == "font_style"


# ── must_include tests ──────────────────────────────


def test_must_include_all_present():
    rule = {
        "id": "TEST-INC-1",
        "iso_ref": "11.3",
        "description": "Must include check",
        "severity": "critical",
        "markers": [],
        "specs": {"must_include": ["street", "city", "country"]},
    }
    ocr = _make_ocr("123 Main Street, Springfield City, Country: USA")
    result = validate_rule_specs(rule, ocr_result=ocr)
    assert result.all_passed


def test_must_include_missing():
    rule = {
        "id": "TEST-INC-2",
        "iso_ref": "11.3",
        "description": "Must include check",
        "severity": "critical",
        "markers": [],
        "specs": {"must_include": ["street", "city", "country"]},
    }
    ocr = _make_ocr("123 Main Avenue")
    result = validate_rule_specs(rule, ocr_result=ocr)
    assert not result.all_passed


def test_must_include_or_condition():
    rule = {
        "id": "TEST-INC-3",
        "iso_ref": "11.3 a)",
        "description": "OR condition",
        "severity": "critical",
        "markers": [],
        "specs": {"must_include": ["width OR diameter"]},
    }
    ocr = _make_ocr("diameter: 12cm, projection: 3.5cm")
    result = validate_rule_specs(rule, ocr_result=ocr)
    assert result.all_passed


# ── must_be_adjacent_to tests ────────────────────────


def test_adjacency_pass():
    rule = {
        "id": "TEST-ADJ-1",
        "iso_ref": "5.1.1",
        "description": "Adjacency check",
        "severity": "critical",
        "markers": ["manufacturer"],
        "specs": {"must_be_adjacent_to": "Mentor", "adjacency_max_mm": 15},
    }
    # 20px apart at 300dpi = ~1.7mm → well within 15mm
    words = [
        OCRWord(text="manufacturer", confidence=95, x=100, y=100, w=200, h=30),
        OCRWord(text="Mentor", confidence=95, x=120, y=140, w=100, h=30),
    ]
    ocr = _make_ocr("manufacturer Mentor LLC", words)
    result = validate_rule_specs(rule, ocr_result=ocr, dpi=300)
    assert result.all_passed


def test_adjacency_fail():
    rule = {
        "id": "TEST-ADJ-2",
        "iso_ref": "5.1.1",
        "description": "Adjacency check",
        "severity": "critical",
        "markers": ["manufacturer"],
        "specs": {"must_be_adjacent_to": "Mentor", "adjacency_max_mm": 5},
    }
    # 2000px apart at 300dpi = ~169mm → far exceeds 5mm
    words = [
        OCRWord(text="manufacturer", confidence=95, x=100, y=100, w=200, h=30),
        OCRWord(text="Mentor", confidence=95, x=2100, y=100, w=100, h=30),
    ]
    ocr = _make_ocr("manufacturer ... Mentor LLC", words)
    result = validate_rule_specs(rule, ocr_result=ocr, dpi=300)
    assert not result.all_passed
    assert result.violations[0].spec_field == "must_be_adjacent_to"


# ── position tests ──────────────────────────────────


def test_position_check_top():
    rule = {
        "id": "TEST-POS-1",
        "iso_ref": "test",
        "description": "Position check",
        "severity": "major",
        "markers": ["CE"],
        "specs": {"position": "top"},
    }
    # Word at y=100 in 3000px image → top third
    words = [OCRWord(text="CE", confidence=95, x=100, y=100, w=50, h=30)]
    ocr = _make_ocr("CE 0086", words)
    result = validate_rule_specs(rule, ocr_result=ocr, image_size=(2400, 3000))
    assert result.all_passed


def test_position_check_fail():
    rule = {
        "id": "TEST-POS-2",
        "iso_ref": "test",
        "description": "Position check",
        "severity": "major",
        "markers": ["CE"],
        "specs": {"position": "top"},
    }
    # Word at y=2500 in 3000px image → bottom third
    words = [OCRWord(text="CE", confidence=95, x=100, y=2500, w=50, h=30)]
    ocr = _make_ocr("CE 0086", words)
    result = validate_rule_specs(rule, ocr_result=ocr, image_size=(2400, 3000))
    assert not result.all_passed
    assert result.violations[0].spec_field == "position"


# ── valid_classifications tests ──────────────────────


def test_valid_classifications_pass():
    rule = {
        "id": "TEST-CLASS-1",
        "iso_ref": "G.2",
        "description": "Classifications",
        "severity": "critical",
        "markers": [],
        "specs": {
            "valid_classifications": [
                {"code": "NTX", "description": "Not textured"},
                {"code": "SLC", "description": "Low complexity"},
            ]
        },
    }
    ocr = _make_ocr("Surface: NTX - Not textured (smooth)")
    result = validate_rule_specs(rule, ocr_result=ocr)
    assert result.all_passed


def test_valid_classifications_fail():
    rule = {
        "id": "TEST-CLASS-2",
        "iso_ref": "G.2",
        "description": "Classifications",
        "severity": "critical",
        "markers": [],
        "specs": {
            "valid_classifications": [
                {"code": "NTX", "description": "Not textured"},
            ]
        },
    }
    ocr = _make_ocr("Surface: smooth finish")
    result = validate_rule_specs(rule, ocr_result=ocr)
    assert not result.all_passed


# ── min_languages tests ─────────────────────────────


def test_min_languages_pass():
    rule = {
        "id": "TEST-LANG-1",
        "iso_ref": "MDR",
        "description": "Multi-language",
        "severity": "major",
        "markers": [],
        "specs": {"min_languages": 3},
    }
    ocr = _make_ocr("en: English text\nde: Deutsch text\nfr: Texte français\nes: Texto español")
    result = validate_rule_specs(rule, ocr_result=ocr)
    assert result.all_passed


def test_min_languages_fail():
    rule = {
        "id": "TEST-LANG-2",
        "iso_ref": "MDR",
        "description": "Multi-language",
        "severity": "major",
        "markers": [],
        "specs": {"min_languages": 3},
    }
    ocr = _make_ocr("en: English text only")
    result = validate_rule_specs(rule, ocr_result=ocr)
    assert not result.all_passed


# ── barcode format tests ─────────────────────────────


def test_barcode_format_pass():
    rule = {
        "id": "TEST-BC-1",
        "iso_ref": "11.5",
        "description": "Barcode format",
        "severity": "critical",
        "markers": [],
        "specs": {"formats": ["GS1-128", "DataMatrix"]},
    }
    barcodes = [BarcodeResult(barcode_type="CODE128", data="(01)12345", x=0, y=0, w=200, h=50)]
    result = validate_rule_specs(rule, barcodes=barcodes)
    assert result.all_passed


def test_barcode_format_fail():
    rule = {
        "id": "TEST-BC-2",
        "iso_ref": "11.5",
        "description": "Barcode format",
        "severity": "critical",
        "markers": [],
        "specs": {"formats": ["DataMatrix"]},
    }
    result = validate_rule_specs(rule, barcodes=[])
    assert not result.all_passed


# ── notified body number tests ───────────────────────


def test_nb_number_pass():
    rule = {
        "id": "TEST-NB-1",
        "iso_ref": "EU MDR",
        "description": "NB number",
        "severity": "critical",
        "markers": ["CE"],
        "specs": {"must_include_nb_number": True},
    }
    ocr = _make_ocr("CE 0086 certified")
    result = validate_rule_specs(rule, ocr_result=ocr)
    assert result.all_passed


def test_nb_number_fail():
    rule = {
        "id": "TEST-NB-2",
        "iso_ref": "EU MDR",
        "description": "NB number",
        "severity": "critical",
        "markers": ["CE"],
        "specs": {"must_include_nb_number": True},
    }
    ocr = _make_ocr("CE mark present but no number")
    result = validate_rule_specs(rule, ocr_result=ocr)
    assert not result.all_passed


# ── No specs → auto-pass ─────────────────────────────


def test_no_specs_passes():
    rule = {
        "id": "TEST-NO-SPECS",
        "iso_ref": "test",
        "description": "Rule with no specs",
        "severity": "minor",
        "markers": ["test"],
    }
    result = validate_rule_specs(rule)
    assert result.all_passed


# ── Combined specs tests ────────────────────────────


def test_combined_specs_multiple_checks():
    """Rule with multiple specs — all must pass."""
    rule = {
        "id": "TEST-COMBO",
        "iso_ref": "11.2",
        "description": "Combined check",
        "severity": "critical",
        "markers": ["volume"],
        "specs": {
            "min_font_size_pt": 8,
            "font_style": "bold",
            "min_height_mm": 2,
        },
    }
    fonts = [_make_font("volume 150cc", 10.0, bold=True)]
    result = validate_rule_specs(rule, fonts=fonts)
    assert result.all_passed


def test_combined_specs_partial_fail():
    """Font size passes but bold fails → overall fail."""
    rule = {
        "id": "TEST-COMBO-2",
        "iso_ref": "11.2",
        "description": "Combined check",
        "severity": "critical",
        "markers": ["volume"],
        "specs": {
            "min_font_size_pt": 8,
            "font_style": "bold",
        },
    }
    fonts = [_make_font("volume 150cc", 10.0, bold=False)]
    result = validate_rule_specs(rule, fonts=fonts)
    assert not result.all_passed
    assert len(result.violations) == 1
    assert result.violations[0].spec_field == "font_style"


# ── SpecsResult status property ──────────────────────


def test_specs_result_status():
    r = SpecsResult(rule_id="X", iso_ref="Y", description="Z")
    assert r.status == "PASS"

    r.add_violation(SpecViolation(
        rule_id="X", spec_field="test", requirement="a", actual="b", severity="minor"
    ))
    assert r.status == "PARTIAL"  # minor-only → PARTIAL

    r.add_violation(SpecViolation(
        rule_id="X", spec_field="test2", requirement="c", actual="d", severity="critical"
    ))
    assert r.status == "FAIL"  # has critical → FAIL
