"""Tests for compliance engine modules."""

import pytest


def test_load_rules():
    """Rules load from YAML config."""
    from label_compliance.compliance.rules import load_rules

    rules = load_rules()
    assert len(rules) > 0
    # Each rule must have required keys
    for r in rules:
        assert "id" in r
        assert "description" in r
        assert "severity" in r


def test_rules_by_category():
    """Filter rules by category."""
    from label_compliance.compliance.rules import get_rules_by_category

    labeling = get_rules_by_category("labeling")
    assert isinstance(labeling, list)


def test_new_2024_rules():
    """At least one 'new_in_2024' rule exists."""
    from label_compliance.compliance.rules import get_new_2024_rules

    new_rules = get_new_2024_rules()
    assert len(new_rules) >= 1
    assert any("surface" in r.get("description", "").lower() for r in new_rules)


def test_match_rule_text_found():
    """Text matcher finds present text."""
    from label_compliance.compliance.matcher import match_rule_text
    from label_compliance.document.ocr import OCRResult

    rule = {
        "id": "TEST-01",
        "check_type": "text_contains",
        "markers": ["silicone gel"],
        "severity": "major",
        "description": "Test rule",
        "iso_ref": "TEST",
    }
    ocr = OCRResult(image_path="test.png", image_size=(100, 100),
                    full_text="This implant is made from silicone gel and saline.")
    result = match_rule_text(rule, ocr)
    assert result.status in ("PASS", "PARTIAL")
    assert result.confidence > 0


def test_match_rule_text_missing():
    """Text matcher flags missing text."""
    from label_compliance.compliance.matcher import match_rule_text
    from label_compliance.document.ocr import OCRResult

    rule = {
        "id": "TEST-02",
        "check_type": "text_contains",
        "markers": ["surface classification", "textured"],
        "severity": "critical",
        "description": "Surface must be stated",
        "iso_ref": "TEST",
    }
    ocr = OCRResult(image_path="test.png", image_size=(100, 100),
                    full_text="This is a breast implant product label with no surface info.")
    result = match_rule_text(rule, ocr)
    assert result.status in ("FAIL", "PARTIAL")


def test_compute_score_all_pass():
    """Perfect matches yield COMPLIANT."""
    from label_compliance.compliance.matcher import MatchResult
    from label_compliance.compliance.scorer import compute_score

    matches = [
        MatchResult(rule_id="R1", rule_description="d1", iso_ref="ref", status="PASS", confidence=1.0, evidence=["ok"], severity="critical"),
        MatchResult(rule_id="R2", rule_description="d2", iso_ref="ref", status="PASS", confidence=1.0, evidence=["ok"], severity="major"),
        MatchResult(rule_id="R3", rule_description="d3", iso_ref="ref", status="PASS", confidence=1.0, evidence=["ok"], severity="minor"),
    ]
    score = compute_score("test-label", matches)
    assert score.status == "COMPLIANT"
    assert score.score_pct >= 85


def test_compute_score_all_fail():
    """All failures yield NON-COMPLIANT."""
    from label_compliance.compliance.matcher import MatchResult
    from label_compliance.compliance.scorer import compute_score

    matches = [
        MatchResult(rule_id="R1", rule_description="d1", iso_ref="ref", status="FAIL", confidence=0.0, evidence=[], severity="critical"),
        MatchResult(rule_id="R2", rule_description="d2", iso_ref="ref", status="FAIL", confidence=0.0, evidence=[], severity="major"),
    ]
    score = compute_score("test-label", matches)
    assert score.status == "NON-COMPLIANT"
    assert score.score_pct < 50
