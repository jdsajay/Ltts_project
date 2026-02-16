"""
Semantic & Rule-Based Matcher
===============================
Combines semantic similarity search (via KB embeddings)
with rule-based validation to assess compliance.

Three matching layers (used in combination for maximum accuracy):
  1. Text matching  — fast keyword / regex against OCR text
  2. Semantic match — vector similarity via sentence-transformers
  3. AI verification — multimodal LLM visually inspects the label page
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from label_compliance.document.ocr import OCRResult
from label_compliance.document.symbol_detector import SymbolMatch
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


@dataclass
class MatchResult:
    """Result of matching a label against one rule."""

    rule_id: str
    rule_description: str
    iso_ref: str
    status: str  # "PASS", "PARTIAL", "FAIL"
    confidence: float = 0.0
    method: str = ""  # "text_match", "pattern", "semantic", "visual", "barcode"
    evidence: list[str] = field(default_factory=list)
    locations: list[dict] = field(default_factory=list)
    severity: str = "critical"
    new_in_2024: bool = False
    details: str = ""


def match_rule_text(
    rule: dict,
    ocr_result: OCRResult,
) -> MatchResult:
    """
    Match a single rule against OCR text using text markers and patterns.
    """
    markers = rule.get("markers", [])
    pattern = rule.get("pattern")
    text_lower = ocr_result.text_lower
    full_text = ocr_result.full_text

    matched_markers = []
    locations = []
    pattern_value = None

    # Check text markers
    for marker in markers:
        if marker.lower() in text_lower:
            matched_markers.append(marker)
            for word in ocr_result.find_text(marker):
                locations.append({
                    "text": word.text,
                    "x": word.x, "y": word.y,
                    "w": word.w, "h": word.h,
                })

    # Check regex pattern
    if pattern:
        m = re.search(pattern, full_text, re.IGNORECASE)
        if m:
            pattern_value = m.group(0)
            matched_markers.append(f"pattern:{pattern_value}")

    # Determine status
    total_markers = len(markers) + (1 if pattern else 0)
    matched_count = len(matched_markers)

    if matched_count == 0:
        status = "FAIL"
        confidence = 0.0
    elif matched_count >= max(1, total_markers * 0.5):
        status = "PASS"
        confidence = matched_count / max(total_markers, 1)
    else:
        status = "PARTIAL"
        confidence = matched_count / max(total_markers, 1)

    return MatchResult(
        rule_id=rule.get("id", "unknown"),
        rule_description=rule.get("description", ""),
        iso_ref=rule.get("iso_ref", ""),
        status=status,
        confidence=confidence,
        method="text_match",
        evidence=matched_markers,
        locations=locations,
        severity=rule.get("severity", "critical"),
        new_in_2024=rule.get("new_in_2024", False),
        details=f"Matched {matched_count}/{total_markers} markers",
    )


def match_rule_semantic(
    rule: dict,
    ocr_result: OCRResult,
    threshold: float = 0.65,
) -> MatchResult:
    """
    Match a rule against OCR text using semantic similarity via KB.

    Uses the knowledge base embeddings to find if the OCR text
    semantically covers the rule's requirement.
    """
    try:
        from label_compliance.knowledge_base.store import KnowledgeStore

        store = KnowledgeStore()
        rule_desc = rule.get("description", "")

        # Search KB for the rule description and see if label text is similar
        hits = store.search(ocr_result.full_text[:500], n_results=5)

        # Check if any hit matches this rule's section
        rule_section = rule.get("iso_ref", "")
        best_sim = 0.0

        for hit in hits:
            meta = hit.get("metadata", {})
            if rule_section and meta.get("section", "") in rule_section:
                best_sim = max(best_sim, hit.get("similarity", 0))

        if best_sim >= threshold:
            status = "PASS"
        elif best_sim >= threshold * 0.6:
            status = "PARTIAL"
        else:
            status = "FAIL"

        return MatchResult(
            rule_id=rule.get("id", "unknown"),
            rule_description=rule.get("description", ""),
            iso_ref=rule.get("iso_ref", ""),
            status=status,
            confidence=best_sim,
            method="semantic",
            evidence=[f"semantic_similarity={best_sim:.3f}"],
            severity=rule.get("severity", "critical"),
            new_in_2024=rule.get("new_in_2024", False),
            details=f"Best semantic match: {best_sim:.3f}",
        )

    except Exception as e:
        logger.debug("Semantic matching failed: %s", e)
        return MatchResult(
            rule_id=rule.get("id", "unknown"),
            rule_description=rule.get("description", ""),
            iso_ref=rule.get("iso_ref", ""),
            status="FAIL",
            confidence=0.0,
            method="semantic",
            severity=rule.get("severity", "critical"),
            new_in_2024=rule.get("new_in_2024", False),
            details=f"Semantic matching unavailable: {e}",
        )


def combine_match_results(results: list[MatchResult]) -> MatchResult:
    """
    Combine multiple match results for the same rule (e.g., text + semantic).
    Takes the best result.
    """
    if not results:
        raise ValueError("Cannot combine empty results")

    best = max(results, key=lambda r: r.confidence)

    # Merge evidence from all methods
    all_evidence = []
    all_locations = []
    methods = []
    for r in results:
        all_evidence.extend(r.evidence)
        all_locations.extend(r.locations)
        if r.method:
            methods.append(r.method)

    best.evidence = list(set(all_evidence))
    best.locations = all_locations
    best.method = "+".join(sorted(set(methods)))
    return best


# ═══════════════════════════════════════════════════════
#  AI Verification Layer
# ═══════════════════════════════════════════════════════

_AI_VERIFY_PROMPT = """\
You are an expert medical-device regulatory compliance auditor.

**Task**: Examine the attached label image and determine whether it satisfies the following ISO requirement.

**Requirement**:
- Rule ID: {rule_id}
- ISO Reference: {iso_ref}
- Description: {description}
- Category: {category}
- What to look for: {markers}

**Instructions**:
1. Carefully examine the ENTIRE label image — text, symbols, barcodes, small print, everything.
2. Determine whether the requirement is satisfied.
3. Respond with ONLY a JSON object (no markdown, no extra text):

{{
  "status": "PASS" or "PARTIAL" or "FAIL",
  "confidence": 0.0 to 1.0,
  "evidence": ["list of specific text/symbols you found that relate to this requirement"],
  "reasoning": "One sentence explanation of your assessment"
}}

Be strict. If the requirement asks for specific text and you cannot clearly see it, mark FAIL.
If you see related but incomplete information, mark PARTIAL.
Only mark PASS when you can clearly confirm the requirement is fully met.
"""

_AI_BATCH_PROMPT = """\
You are an expert medical-device regulatory compliance auditor.

**Task**: Examine the attached label image and check ALL of the following ISO requirements.

**Requirements to check**:
{rules_json}

**Instructions**:
1. Carefully examine the ENTIRE label image — text, symbols, barcodes, small print, everything.
2. For EACH requirement, determine whether it is satisfied.
3. Respond with ONLY a JSON array (no markdown, no extra text), one object per rule:

[
  {{
    "rule_id": "the rule id",
    "status": "PASS" or "PARTIAL" or "FAIL",
    "confidence": 0.0 to 1.0,
    "evidence": ["list of specific text/symbols found"],
    "reasoning": "one sentence explanation"
  }},
  ...
]

Be strict and thorough. Check every requirement against what you can actually see in the image.
"""


def _parse_ai_json(raw: str) -> dict | list | None:
    """Extract JSON from AI response, handling markdown code blocks."""
    text = raw.strip()
    # Remove markdown code block wrappers if present
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # drop opening ```json or ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON in the text
        for start_char, end_char in [("{", "}"), ("[", "]")]:
            start = text.find(start_char)
            end = text.rfind(end_char)
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    continue
        logger.warning("Could not parse AI response as JSON: %s", text[:200])
        return None


def ai_verify_rule(
    rule: dict,
    image_path: str | Path,
    ai_provider,
) -> MatchResult:
    """
    Use a multimodal AI model to visually verify a single rule
    against a label page image.

    Args:
        rule: The compliance rule dict.
        image_path: Path to the rendered page image (PNG).
        ai_provider: An AIProvider instance (Ollama or OpenAI).

    Returns:
        MatchResult with AI-based assessment.
    """
    prompt = _AI_VERIFY_PROMPT.format(
        rule_id=rule.get("id", "unknown"),
        iso_ref=rule.get("iso_ref", ""),
        description=rule.get("description", ""),
        category=rule.get("category", ""),
        markers=", ".join(rule.get("markers", [])),
    )

    try:
        raw = ai_provider.analyze_with_image(prompt, str(image_path))
        parsed = _parse_ai_json(raw)

        if parsed and isinstance(parsed, dict):
            status = parsed.get("status", "FAIL").upper()
            if status not in ("PASS", "PARTIAL", "FAIL"):
                status = "FAIL"
            confidence = float(parsed.get("confidence", 0.0))
            evidence = parsed.get("evidence", [])
            reasoning = parsed.get("reasoning", "")
        else:
            logger.warning("AI response not parseable for rule %s", rule.get("id"))
            status = "FAIL"
            confidence = 0.0
            evidence = []
            reasoning = f"AI response not parseable: {raw[:100]}"

    except Exception as e:
        logger.error("AI verification failed for rule %s: %s", rule.get("id"), e)
        status = "FAIL"
        confidence = 0.0
        evidence = []
        reasoning = f"AI error: {e}"

    return MatchResult(
        rule_id=rule.get("id", "unknown"),
        rule_description=rule.get("description", ""),
        iso_ref=rule.get("iso_ref", ""),
        status=status,
        confidence=confidence,
        method="ai_vision",
        evidence=evidence,
        severity=rule.get("severity", "critical"),
        new_in_2024=rule.get("new_in_2024", False),
        details=reasoning,
    )


def ai_verify_rules_batch(
    rules: list[dict],
    image_path: str | Path,
    ai_provider,
) -> list[MatchResult]:
    """
    Use a multimodal AI model to verify ALL rules against a label page
    image in a single prompt (more efficient than one-by-one).

    Args:
        rules: List of compliance rule dicts.
        image_path: Path to the rendered page image (PNG).
        ai_provider: An AIProvider instance.

    Returns:
        List of MatchResult, one per rule.
    """
    # Build compact rules description for the prompt
    rules_for_prompt = []
    for r in rules:
        rules_for_prompt.append({
            "rule_id": r.get("id", "unknown"),
            "iso_ref": r.get("iso_ref", ""),
            "description": r.get("description", ""),
            "category": r.get("category", ""),
            "markers": r.get("markers", []),
        })

    prompt = _AI_BATCH_PROMPT.format(
        rules_json=json.dumps(rules_for_prompt, indent=2),
    )

    results: list[MatchResult] = []

    try:
        raw = ai_provider.analyze_with_image(prompt, str(image_path))
        parsed = _parse_ai_json(raw)

        if parsed and isinstance(parsed, list):
            # Build a lookup from rule_id → AI result
            ai_map: dict[str, dict] = {}
            for item in parsed:
                if isinstance(item, dict) and "rule_id" in item:
                    ai_map[item["rule_id"]] = item

            for rule in rules:
                rule_id = rule.get("id", "unknown")
                ai_result = ai_map.get(rule_id, {})
                status = ai_result.get("status", "FAIL").upper()
                if status not in ("PASS", "PARTIAL", "FAIL"):
                    status = "FAIL"

                results.append(MatchResult(
                    rule_id=rule_id,
                    rule_description=rule.get("description", ""),
                    iso_ref=rule.get("iso_ref", ""),
                    status=status,
                    confidence=float(ai_result.get("confidence", 0.0)),
                    method="ai_vision",
                    evidence=ai_result.get("evidence", []),
                    severity=rule.get("severity", "critical"),
                    new_in_2024=rule.get("new_in_2024", False),
                    details=ai_result.get("reasoning", ""),
                ))
        else:
            logger.warning("AI batch response not parseable, falling back to individual")
            for rule in rules:
                results.append(ai_verify_rule(rule, image_path, ai_provider))

    except Exception as e:
        logger.error("AI batch verification failed: %s", e)
        # Return FAIL for all rules on error
        for rule in rules:
            results.append(MatchResult(
                rule_id=rule.get("id", "unknown"),
                rule_description=rule.get("description", ""),
                iso_ref=rule.get("iso_ref", ""),
                status="FAIL",
                confidence=0.0,
                method="ai_vision",
                severity=rule.get("severity", "critical"),
                new_in_2024=rule.get("new_in_2024", False),
                details=f"AI batch error: {e}",
            ))

    return results
