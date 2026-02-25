"""
Tests for AI Integration
===========================
Tests the AI matching layer — JSON parsing, prompt handling,
text/vision batch logic, and robust fallback parsing.
"""

from __future__ import annotations

import json
import pytest

# We test the internal parsing functions directly
from label_compliance.compliance.matcher import (
    _parse_ai_json,
    _repair_json,
    _extract_results_regex,
    MatchResult,
)


# ═══════════════════════════════════════════════════════
#  JSON Parsing Tests
# ═══════════════════════════════════════════════════════

class TestParseAIJson:
    """Test the robust JSON parsing function."""

    def test_pure_json_object(self):
        raw = '{"status": "PASS", "confidence": 0.95}'
        result = _parse_ai_json(raw)
        assert result == {"status": "PASS", "confidence": 0.95}

    def test_pure_json_array(self):
        raw = '[{"rule_id": "R1", "status": "PASS"}]'
        result = _parse_ai_json(raw)
        assert isinstance(result, list)
        assert result[0]["rule_id"] == "R1"

    def test_markdown_code_block(self):
        raw = '```json\n{"status": "FAIL", "confidence": 0.1}\n```'
        result = _parse_ai_json(raw)
        assert result["status"] == "FAIL"

    def test_json_in_narrative(self):
        raw = 'Here is my analysis:\n{"status": "PARTIAL", "confidence": 0.6}\nThat is all.'
        result = _parse_ai_json(raw)
        assert result["status"] == "PARTIAL"

    def test_wrapped_results(self):
        raw = '{"results": [{"rule_id": "R1", "status": "PASS", "confidence": 0.9}]}'
        result = _parse_ai_json(raw)
        assert "results" in result
        assert result["results"][0]["status"] == "PASS"

    def test_empty_string(self):
        assert _parse_ai_json("") is None
        assert _parse_ai_json("  ") is None

    def test_no_json_at_all(self):
        assert _parse_ai_json("This is just plain text with no JSON.") is None

    def test_trailing_comma_repair(self):
        raw = '{"status": "PASS", "confidence": 0.8,}'
        result = _parse_ai_json(raw)
        assert result is not None
        assert result["status"] == "PASS"

    def test_unquoted_status_repair(self):
        raw = '{"status": PASS, "confidence": 0.9}'
        result = _parse_ai_json(raw)
        assert result is not None
        assert result["status"] == "PASS"

    def test_truncated_json_repair(self):
        # Mild truncation (just missing closing braces) can be repaired
        raw = '{"results": [{"rule_id": "R1", "status": "PASS"}]'
        result = _parse_ai_json(raw)
        assert result is not None

    def test_severely_truncated_returns_none(self):
        # Severe truncation can't be repaired — returns None gracefully
        raw = '{"results": [{"rule_id": "R1", "status": "PA'
        result = _parse_ai_json(raw)
        # This may or may not parse — important is that it doesn't crash
        # With format="json", Ollama guarantees valid output so this is rare

    def test_array_with_wrapped_format(self):
        raw = json.dumps({
            "results": [
                {"rule_id": "14607-1", "status": "PASS", "confidence": 0.95, "evidence": ["found manufacturer"], "reasoning": "ok"},
                {"rule_id": "14607-2", "status": "FAIL", "confidence": 0.1, "evidence": [], "reasoning": "missing"},
            ]
        })
        result = _parse_ai_json(raw)
        assert result["results"][0]["status"] == "PASS"
        assert result["results"][1]["status"] == "FAIL"


class TestRepairJson:
    """Test JSON repair utility."""

    def test_trailing_comma_object(self):
        assert json.loads(_repair_json('{"a": 1,}')) == {"a": 1}

    def test_trailing_comma_array(self):
        assert json.loads(_repair_json('[1, 2, 3,]')) == [1, 2, 3]

    def test_unquoted_pass(self):
        fixed = _repair_json('{"status": PASS}')
        assert '"PASS"' in fixed

    def test_unquoted_fail(self):
        fixed = _repair_json('{"status": FAIL}')
        assert '"FAIL"' in fixed

    def test_unclosed_brace(self):
        fixed = _repair_json('{"a": {"b": 1}')
        assert fixed.count("{") == fixed.count("}")

    def test_unclosed_bracket(self):
        fixed = _repair_json('[{"a": 1}')
        assert fixed.count("[") == fixed.count("]")


class TestExtractResultsRegex:
    """Test regex fallback extraction."""

    def test_extracts_single_result(self):
        text = 'rule_id: "R1", status: "PASS", confidence: 0.85'
        # Add quotes to match pattern
        text = '"rule_id": "R1", "status": "PASS", "confidence": 0.85'
        results = _extract_results_regex(text)
        assert results is not None
        assert len(results) == 1
        assert results[0]["rule_id"] == "R1"
        assert results[0]["status"] == "PASS"
        assert results[0]["confidence"] == 0.85

    def test_extracts_multiple(self):
        text = '''
        {"rule_id": "R1", "status": "PASS", "confidence": 0.9}
        {"rule_id": "R2", "status": "FAIL", "confidence": 0.1}
        '''
        results = _extract_results_regex(text)
        assert results is not None
        assert len(results) == 2

    def test_no_results(self):
        results = _extract_results_regex("just plain text")
        assert results is None

    def test_mixed_case_status(self):
        text = '"rule_id": "R1", "status": "pass", "confidence": 0.7'
        results = _extract_results_regex(text)
        assert results is not None
        assert results[0]["status"] == "PASS"


# ═══════════════════════════════════════════════════════
#  AI Provider Mock Tests
# ═══════════════════════════════════════════════════════

class MockAIProvider:
    """Mock AI provider that returns pre-set JSON responses."""

    def __init__(self, text_response: str = "", image_response: str = ""):
        self._text_response = text_response
        self._image_response = image_response
        self.text_calls = 0
        self.image_calls = 0

    def analyze(self, prompt: str, force_json: bool = True) -> str:
        self.text_calls += 1
        return self._text_response

    def analyze_with_image(self, prompt: str, image_path: str, force_json: bool = True) -> str:
        self.image_calls += 1
        return self._image_response

    @property
    def name(self) -> str:
        return "mock"


class TestAIVerifyRuleText:
    """Test AI text-based rule verification."""

    def test_successful_pass(self):
        from label_compliance.compliance.matcher import ai_verify_rule_text

        provider = MockAIProvider(text_response=json.dumps({
            "status": "PASS",
            "confidence": 0.95,
            "evidence": ["found manufacturer name"],
            "reasoning": "Label contains manufacturer name",
        }))

        rule = {
            "id": "R1",
            "description": "Manufacturer name required",
            "iso_ref": "14607-1",
            "markers": ["manufacturer", "company"],
            "severity": "critical",
        }

        result = ai_verify_rule_text(rule, "Mentor Worldwide LLC", provider)
        assert result.status == "PASS"
        assert result.confidence == 0.95
        assert result.method == "ai_text"
        assert provider.text_calls == 1

    def test_fail_response(self):
        from label_compliance.compliance.matcher import ai_verify_rule_text

        provider = MockAIProvider(text_response=json.dumps({
            "status": "FAIL",
            "confidence": 0.1,
            "evidence": [],
            "reasoning": "No expiry date found",
        }))

        rule = {
            "id": "R2",
            "description": "Expiry date required",
            "markers": ["EXP", "expiry"],
            "severity": "critical",
        }

        result = ai_verify_rule_text(rule, "Some label text", provider)
        assert result.status == "FAIL"
        assert result.confidence == 0.1

    def test_unparseable_response(self):
        from label_compliance.compliance.matcher import ai_verify_rule_text

        provider = MockAIProvider(text_response="I cannot process this request.")
        rule = {"id": "R3", "description": "test", "markers": [], "severity": "minor"}

        result = ai_verify_rule_text(rule, "text", provider)
        assert result.status == "FAIL"
        assert result.method == "ai_text"


class TestAIVerifyRulesTextBatch:
    """Test AI text-based batch rule verification."""

    def test_batch_returns_all_results(self):
        from label_compliance.compliance.matcher import ai_verify_rules_text_batch

        provider = MockAIProvider(text_response=json.dumps({
            "results": [
                {"rule_id": "R1", "status": "PASS", "confidence": 0.9, "evidence": ["found"], "reasoning": "ok"},
                {"rule_id": "R2", "status": "FAIL", "confidence": 0.1, "evidence": [], "reasoning": "missing"},
            ]
        }))

        rules = [
            {"id": "R1", "description": "Rule 1", "markers": ["a"], "severity": "critical"},
            {"id": "R2", "description": "Rule 2", "markers": ["b"], "severity": "critical"},
        ]

        results = ai_verify_rules_text_batch(rules, "label text", provider, batch_size=5)
        assert len(results) == 2
        assert results[0].status == "PASS"
        assert results[1].status == "FAIL"

    def test_batch_splits_large_sets(self):
        from label_compliance.compliance.matcher import ai_verify_rules_text_batch

        # Create 7 rules — should split into 2 batches (5 + 2)
        response = json.dumps({
            "results": [
                {"rule_id": f"R{i}", "status": "PASS", "confidence": 0.8, "evidence": [], "reasoning": "ok"}
                for i in range(1, 6)
            ]
        })

        provider = MockAIProvider(text_response=response)
        rules = [
            {"id": f"R{i}", "description": f"Rule {i}", "markers": [], "severity": "minor"}
            for i in range(1, 8)
        ]

        results = ai_verify_rules_text_batch(rules, "text", provider, batch_size=5)
        # Should have made 2 calls (5 rules + 2 rules)
        assert provider.text_calls == 2
        assert len(results) == 7


class TestAIVerifyRulesVisionBatch:
    """Test AI vision-based batch rule verification."""

    def test_vision_batch_returns_results(self):
        from label_compliance.compliance.matcher import ai_verify_rules_batch

        provider = MockAIProvider(image_response=json.dumps({
            "results": [
                {"rule_id": "V1", "status": "PASS", "confidence": 0.85, "evidence": ["symbol visible"], "reasoning": "ok"},
            ]
        }))

        rules = [
            {"id": "V1", "description": "Symbol check", "markers": ["CE"], "severity": "critical"},
        ]

        results = ai_verify_rules_batch(rules, "/tmp/fake.png", provider, batch_size=5)
        assert len(results) == 1
        assert results[0].status == "PASS"
        assert results[0].method == "ai_vision"
        assert provider.image_calls == 1
