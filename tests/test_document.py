"""Tests for document processing modules."""

import pytest
from pathlib import Path

from PIL import Image


def test_ocr_result_structure():
    """OCR data classes initialise correctly."""
    from label_compliance.document.ocr import OCRResult, OCRWord

    word = OCRWord(text="hello", confidence=95, x=10, y=20, w=90, h=20)
    result = OCRResult(image_path="test.png", image_size=(100, 100), full_text="hello", words=[word])
    assert result.full_text == "hello"
    assert len(result.words) == 1
    assert result.words[0].confidence == 95


def test_layout_zone_structure():
    """Zone data class works."""
    from label_compliance.document.layout import Zone

    z = Zone(zone_type="text", x=0, y=0, w=100, h=50, confidence=0.8)
    assert z.zone_type == "text"


def test_font_info_structure():
    """FontInfo data class works."""
    from label_compliance.document.font_analyzer import FontInfo

    f = FontInfo(name="Helvetica", size=12.0, page=1)
    assert f.name == "Helvetica"
    assert f.size == 12.0


def test_barcode_result_structure():
    """BarcodeResult data class works."""
    from label_compliance.document.barcode_reader import BarcodeResult

    b = BarcodeResult(
        barcode_type="CODE128",
        data="0100123456789012",
        x=10, y=20, w=200, h=40,
    )
    assert b.barcode_type == "CODE128"


def test_symbol_match_structure():
    """SymbolMatch data class works."""
    from label_compliance.document.symbol_detector import SymbolMatch

    s = SymbolMatch(
        rule_id="SYM-mfg-date",
        description="Manufacturing date",
        iso_ref="ISO 15223",
        found=True,
        method="ocr",
        confidence=0.9,
    )
    assert s.found is True
    assert s.method == "ocr"
