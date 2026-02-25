"""
Tests for Symbol Library DB and Symbol Comparator.
"""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from label_compliance.document.symbol_library_db import (
    SymbolEntry,
    SymbolLibrary,
    _text_similarity,
    get_symbol_library,
)
from label_compliance.document.symbol_comparator import (
    SymbolComparisonReport,
    SymbolComparisonResult,
    compare_symbols_text,
    _match_pkg_text,
)
from label_compliance.document.ocr import OCRResult, OCRWord


# ═══════════════════════════════════════════════════════
#  Fixtures
# ═══════════════════════════════════════════════════════

@pytest.fixture
def sample_symbol_entry():
    return SymbolEntry(
        row=5,
        name="Manufacturer",
        classification="Standard",
        status="Active",
        pkg_text="Manufacturer",
        ifu_text="Manufacturer",
        sme_function="Labeling",
        rev_history="",
        regulations="ID: REG_0090.pdf\nTitle: ISO 15223-1 Medical devices",
        notes="",
        thumb_file_ref="0100 - Manufacturer.png",
        std_thumb_file_ref="",
        thumb_images=["row5_thumb_0.jpg"],
        std_thumb_images=[],
    )


@pytest.fixture
def sample_symbols():
    """Create a list of test symbols."""
    return [
        SymbolEntry(
            row=1, name="Manufacturer", classification="Standard",
            status="Active", pkg_text="Manufacturer", ifu_text="Manufacturer",
            sme_function="", rev_history="",
            regulations="ISO 15223-1", notes="",
            thumb_file_ref="", std_thumb_file_ref="",
        ),
        SymbolEntry(
            row=2, name="171 - STERILE", classification="Standard",
            status="Active", pkg_text="Sterile", ifu_text="Sterile",
            sme_function="", rev_history="",
            regulations="ISO 15223-1", notes="",
            thumb_file_ref="", std_thumb_file_ref="",
        ),
        SymbolEntry(
            row=3, name="0029 - SN", classification="Standard",
            status="Active", pkg_text="Serial number", ifu_text="Serial number",
            sme_function="", rev_history="",
            regulations="ISO 15223-1", notes="",
            thumb_file_ref="", std_thumb_file_ref="",
        ),
        SymbolEntry(
            row=4, name="Do not re-use", classification="Standard",
            status="Active", pkg_text="Do not re-use", ifu_text="Do not re-use",
            sme_function="", rev_history="",
            regulations="ISO 15223-1", notes="",
            thumb_file_ref="", std_thumb_file_ref="",
        ),
        SymbolEntry(
            row=5, name="Caution", classification="Standard",
            status="Active", pkg_text="Caution", ifu_text="Caution",
            sme_function="", rev_history="",
            regulations="ISO 15223-1", notes="",
            thumb_file_ref="", std_thumb_file_ref="",
        ),
        SymbolEntry(
            row=6, name="No text symbol", classification="Standard",
            status="Active", pkg_text="NO TEXT REQUIRED",
            ifu_text="NO TEXT REQUIRED",
            sme_function="", rev_history="",
            regulations="ISO 7000", notes="",
            thumb_file_ref="", std_thumb_file_ref="",
        ),
        SymbolEntry(
            row=7, name="Inactive Symbol", classification="Standard",
            status="Work In Progress", pkg_text="Test",
            ifu_text="Test",
            sme_function="", rev_history="",
            regulations="", notes="",
            thumb_file_ref="", std_thumb_file_ref="",
        ),
    ]


@pytest.fixture
def ocr_result_with_symbols():
    """OCR result containing symbol-related text."""
    words = [
        OCRWord(text="Manufacturer", x=100, y=50, w=120, h=20, confidence=95),
        OCRWord(text="Mentor", x=230, y=50, w=80, h=20, confidence=95),
        OCRWord(text="STERILE", x=100, y=100, w=80, h=20, confidence=90),
        OCRWord(text="SN", x=100, y=150, w=30, h=15, confidence=85),
        OCRWord(text="12345", x=140, y=150, w=60, h=15, confidence=90),
        OCRWord(text="Caution", x=100, y=200, w=70, h=18, confidence=92),
        OCRWord(text="Single", x=100, y=250, w=50, h=15, confidence=88),
        OCRWord(text="Use", x=155, y=250, w=30, h=15, confidence=88),
    ]
    return OCRResult(
        image_path="test_page.png",
        words=words,
        full_text="Manufacturer Mentor STERILE SN 12345 Caution Single Use",
        image_size=(2550, 3300),
    )


# ═══════════════════════════════════════════════════════
#  Symbol Library DB Tests
# ═══════════════════════════════════════════════════════

def test_text_similarity_exact():
    assert _text_similarity("manufacturer", "manufacturer") == 1.0


def test_text_similarity_partial():
    score = _text_similarity("serial number", "serial number sn")
    assert 0.5 < score < 1.0


def test_text_similarity_no_match():
    assert _text_similarity("sterile", "caution warning") == 0.0


def test_text_similarity_empty():
    assert _text_similarity("", "test") == 0.0
    assert _text_similarity("test", "") == 0.0


def test_symbol_entry_properties(sample_symbol_entry):
    assert sample_symbol_entry.is_standard is True
    assert sample_symbol_entry.is_iso_15223 is True
    assert sample_symbol_entry.is_active is True
    assert "manufacturer" in sample_symbol_entry.search_text


def test_symbol_entry_regulation_ids(sample_symbol_entry):
    ids = sample_symbol_entry.regulation_ids
    assert any("ISO 15223" in rid for rid in ids)


def test_symbol_entry_inactive():
    sym = SymbolEntry(
        row=1, name="Inactive", classification="Standard",
        status="Work In Progress", pkg_text="Test", ifu_text="",
        sme_function="", rev_history="", regulations="",
        notes="", thumb_file_ref="", std_thumb_file_ref="",
    )
    assert sym.is_active is False


def test_symbol_library_load_from_json(tmp_path):
    """Test loading symbol library from a JSON file."""
    db_data = {
        "source": "test.xlsm",
        "total_symbols": 2,
        "total_images": 0,
        "symbols": [
            {
                "row": 1,
                "name": "Manufacturer",
                "classification": "Standard",
                "status": "Active",
                "pkg_text": "Manufacturer",
                "ifu_text": "Manufacturer",
                "sme_function": "",
                "rev_history": "",
                "regulations": "ISO 15223-1",
                "notes": "",
                "thumb_file_ref": "",
                "std_thumb_file_ref": "",
                "thumb_images": [],
                "std_thumb_images": [],
            },
            {
                "row": 2,
                "name": "Sterile",
                "classification": "Standard",
                "status": "Active",
                "pkg_text": "Sterile",
                "ifu_text": "Sterile",
                "sme_function": "",
                "rev_history": "",
                "regulations": "ISO 15223-1",
                "notes": "",
                "thumb_file_ref": "",
                "std_thumb_file_ref": "",
                "thumb_images": [],
                "std_thumb_images": [],
            },
        ],
    }

    db_path = tmp_path / "symbol_library.json"
    db_path.write_text(json.dumps(db_data))

    lib = SymbolLibrary(db_path=db_path)
    lib.load()

    assert len(lib.symbols) == 2
    assert len(lib.get_standard_symbols()) == 2
    assert len(lib.get_iso15223_symbols()) == 2


def test_symbol_library_find_by_text(tmp_path):
    """Test text-based symbol lookup."""
    db_data = {
        "source": "test.xlsm",
        "total_symbols": 1,
        "total_images": 0,
        "symbols": [
            {
                "row": 1,
                "name": "Manufacturer",
                "classification": "Standard",
                "status": "Active",
                "pkg_text": "Manufacturer",
                "ifu_text": "Manufacturer",
                "sme_function": "",
                "rev_history": "",
                "regulations": "ISO 15223-1",
                "notes": "",
                "thumb_file_ref": "",
                "std_thumb_file_ref": "",
            },
        ],
    }
    db_path = tmp_path / "symbol_library.json"
    db_path.write_text(json.dumps(db_data))

    lib = SymbolLibrary(db_path=db_path)
    results = lib.find_by_text("manufacturer")
    assert len(results) >= 1
    assert results[0][1] == 1.0  # exact match


def test_symbol_library_find_by_keywords(tmp_path):
    db_data = {
        "source": "test.xlsm",
        "total_symbols": 2,
        "total_images": 0,
        "symbols": [
            {
                "row": 1,
                "name": "Serial Number",
                "classification": "Standard",
                "status": "Active",
                "pkg_text": "Serial number",
                "ifu_text": "Serial number",
                "sme_function": "",
                "rev_history": "",
                "regulations": "",
                "notes": "",
                "thumb_file_ref": "",
                "std_thumb_file_ref": "",
            },
            {
                "row": 2,
                "name": "Other",
                "classification": "Proprietary - Ethicon",
                "status": "Active",
                "pkg_text": "Something else",
                "ifu_text": "",
                "sme_function": "",
                "rev_history": "",
                "regulations": "",
                "notes": "",
                "thumb_file_ref": "",
                "std_thumb_file_ref": "",
            },
        ],
    }
    db_path = tmp_path / "symbol_library.json"
    db_path.write_text(json.dumps(db_data))

    lib = SymbolLibrary(db_path=db_path)
    results = lib.find_by_keywords(["serial", "number"])
    assert len(results) == 1
    assert results[0].name == "Serial Number"


def test_symbol_library_missing_file(tmp_path):
    """Should not crash if DB file doesn't exist."""
    lib = SymbolLibrary(db_path=tmp_path / "nonexistent.json")
    lib.load()
    assert len(lib.symbols) == 0


# ═══════════════════════════════════════════════════════
#  Symbol Comparator Tests
# ═══════════════════════════════════════════════════════

def test_match_pkg_text_exact():
    found, matched, score = _match_pkg_text(
        "manufacturer", "manufacturer",
        "the manufacturer is mentor worldwide", "The Manufacturer is Mentor Worldwide",
    )
    assert found is True
    assert score > 0.5


def test_match_pkg_text_partial():
    found, matched, score = _match_pkg_text(
        "serial number", "serial number",
        "serial number sn 12345 lot abc", "Serial Number SN 12345 LOT ABC",
    )
    assert found is True
    assert "serial" in matched or "number" in matched


def test_match_pkg_text_not_found():
    found, matched, score = _match_pkg_text(
        "do not resterilize", "do not resterilize",
        "caution single use only", "Caution Single Use Only",
    )
    # "do" and "not" are too short (<2 chars excluded by regex)
    assert score < 0.5


def test_match_pkg_text_no_text_required():
    found, matched, score = _match_pkg_text(
        "no text required", "",
        "any text here", "Any text here",
    )
    assert found is True
    assert score == 1.0


def test_compare_symbols_text_with_fixtures(
    ocr_result_with_symbols,
    sample_symbols,
):
    """Test text comparison with OCR result and sample symbols."""
    report = compare_symbols_text(
        ocr_result=ocr_result_with_symbols,
        required_symbols=sample_symbols,
    )

    assert report.total_required == len(sample_symbols)

    # Manufacturer should be found
    mfr_results = [r for r in report.results if r.symbol.name == "Manufacturer"]
    assert len(mfr_results) == 1
    assert mfr_results[0].status == "FOUND"

    # Sterile should be found
    sterile_results = [r for r in report.results if "STERILE" in r.symbol.name]
    assert len(sterile_results) == 1
    assert sterile_results[0].found_by_text is True

    # NO TEXT REQUIRED should count as found
    no_text = [r for r in report.results if r.symbol.name == "No text symbol"]
    assert len(no_text) == 1
    assert no_text[0].status == "FOUND"

    # Inactive should still be in results (we passed it as required)
    # Total found should be > 0
    assert report.total_found > 0
    assert report.score > 0


def test_compare_symbols_text_empty_ocr(sample_symbols):
    """Test comparison with empty OCR result."""
    empty_ocr = OCRResult(image_path="empty.png", words=[], full_text="", image_size=(100, 100))
    report = compare_symbols_text(
        ocr_result=empty_ocr,
        required_symbols=sample_symbols,
    )

    # "No text required" symbol should still be found
    assert report.total_required == len(sample_symbols)
    no_text_found = [r for r in report.results if r.status == "FOUND"]
    assert len(no_text_found) >= 1  # at least "NO TEXT REQUIRED"


def test_symbol_comparison_report_summary():
    report = SymbolComparisonReport(
        total_required=10,
        total_found=6,
        total_partial=2,
        total_missing=2,
        score=0.7,
    )
    assert "6/10" in report.summary
    assert "2 partial" in report.summary
    assert "2 missing" in report.summary


def test_compare_symbols_text_score_calculation(sample_symbols):
    """Verify score is (found + 0.5 * partial) / total."""
    ocr = OCRResult(
        image_path="test.png",
        words=[
            OCRWord(text="Manufacturer", x=0, y=0, w=100, h=20, confidence=95),
            OCRWord(text="Sterile", x=0, y=30, w=80, h=20, confidence=90),
        ],
        full_text="Manufacturer Sterile",
        image_size=(500, 500),
    )

    report = compare_symbols_text(ocr_result=ocr, required_symbols=sample_symbols)

    # Score formula: (found + 0.5 * partial) / total_required
    expected_score = (report.total_found + 0.5 * report.total_partial) / report.total_required
    assert abs(report.score - expected_score) < 0.01


# ═══════════════════════════════════════════════════════
#  Integration with real symbol library
# ═══════════════════════════════════════════════════════

def test_load_real_symbol_library():
    """Test loading the actual extracted symbol library."""
    db_path = Path("data/symbol_library/symbol_library.json")
    if not db_path.exists():
        pytest.skip("Symbol library not extracted yet")

    lib = SymbolLibrary(db_path=db_path)
    lib.load()

    assert len(lib.symbols) > 0
    assert len(lib.get_standard_symbols()) > 0

    # Should have ISO 15223 symbols
    iso_syms = lib.get_iso15223_symbols()
    assert len(iso_syms) > 0

    # Should find manufacturer symbol
    mfr = lib.find_by_text("manufacturer")
    assert len(mfr) > 0

    # Should find sterile symbol
    sterile = lib.find_by_keywords(["sterile"])
    assert len(sterile) > 0


def test_real_library_breast_implant_symbols():
    """Test getting expected breast implant symbols."""
    db_path = Path("data/symbol_library/symbol_library.json")
    if not db_path.exists():
        pytest.skip("Symbol library not extracted yet")

    lib = SymbolLibrary(db_path=db_path)
    expected = lib.get_expected_symbols_for_breast_implant()

    # Should find key symbols
    names = [s.name for s in expected]
    pkg_texts = [s.pkg_text.lower() for s in expected]

    assert any("manufacturer" in t for t in pkg_texts), "Manufacturer symbol expected"
    assert any("sterile" in t for t in pkg_texts), "Sterile symbol expected"
    assert any("serial" in n.lower() or "sn" in n.lower() for n in names), "Serial number expected"
