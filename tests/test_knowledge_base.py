"""Tests for the knowledge base modules."""

import json
from pathlib import Path

import pytest


def test_ingester_section_regex():
    """Section regex recognises numbered headings."""
    from label_compliance.knowledge_base.ingester import SECTION_RE

    m = SECTION_RE.match("11.3 Labelling requirements for breast implants")
    assert m is not None
    assert m.group("number") == "11.3"

    m = SECTION_RE.match("A.2 Normative references")
    assert m is not None
    assert m.group("number") == "A.2"


def test_shall_regex():
    """SHALL regex extracts requirements."""
    from label_compliance.knowledge_base.ingester import SHALL_RE

    hits = SHALL_RE.findall(
        "The label shall include the name. The report shall be retained."
    )
    assert len(hits) == 2


def test_measurement_regex():
    """Measurement regex finds dimensions."""
    from label_compliance.knowledge_base.ingester import MEASUREMENT_RE

    text = "Minimum size 3 mm and tolerance ±5%"
    matches = MEASUREMENT_RE.findall(text)
    assert any("mm" in m for m in matches)


def test_chunk_text():
    """Helper chunk_text produces overlapping chunks."""
    from label_compliance.utils.helpers import chunk_text

    text = "A" * 1000
    chunks = chunk_text(text, size=200, overlap=50)
    assert len(chunks) >= 5
    # No chunk should exceed size
    for c in chunks:
        assert len(c) <= 200


def test_safe_filename():
    """safe_filename sanitises special characters."""
    from label_compliance.utils.helpers import safe_filename

    assert safe_filename("Hello/World: Test!") == "Hello_World__Test"
