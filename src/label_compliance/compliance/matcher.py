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
    spec_violations: list[dict] = field(default_factory=list)
    spec_details: list[str] = field(default_factory=list)
    specs_passed: bool = True


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
    Takes the best result, and merges all spec violations.
    """
    if not results:
        raise ValueError("Cannot combine empty results")

    best = max(results, key=lambda r: r.confidence)

    # Merge evidence from all methods
    all_evidence = []
    all_locations = []
    all_spec_violations = []
    all_spec_details = []
    methods = []
    any_specs_failed = False
    for r in results:
        all_evidence.extend(r.evidence)
        all_locations.extend(r.locations)
        all_spec_violations.extend(r.spec_violations)
        all_spec_details.extend(r.spec_details)
        if not r.specs_passed:
            any_specs_failed = True
        if r.method:
            methods.append(r.method)

    best.evidence = list(set(all_evidence))
    best.locations = all_locations
    best.spec_violations = all_spec_violations
    best.spec_details = list(set(all_spec_details))
    best.specs_passed = not any_specs_failed
    best.method = "+".join(sorted(set(methods)))

    # If text matched but specs failed, downgrade status
    if best.status == "PASS" and any_specs_failed:
        best.status = "PARTIAL"
        best.details += " | DOWNGRADED: spec violations found"

    return best


# ═══════════════════════════════════════════════════════
#  AI Verification Layer
# ═══════════════════════════════════════════════════════

import re as _re

# ── Prompts — kept short and directive for small models ──

_AI_SINGLE_RULE_PROMPT = """\
Check if this label text satisfies the ISO requirement below.

Rule: {rule_id} ({iso_ref})
Requirement: {description}
Look for: {markers}

Label text:
{label_text}

Respond with JSON: {{"status":"PASS" or "PARTIAL" or "FAIL","confidence":0.0-1.0,"evidence":["what you found"],"reasoning":"why"}}"""

_AI_BATCH_TEXT_PROMPT = """\
Check if the label text below satisfies each ISO requirement.
For each rule, decide PASS/PARTIAL/FAIL.

Rules:
{rules_list}

Label text:
{label_text}

Respond with JSON: {{"results":[{{"rule_id":"id","status":"PASS/PARTIAL/FAIL","confidence":0.0-1.0,"evidence":["found"],"reasoning":"why"}}]}}"""

_AI_VISION_PROMPT = """\
Check if the label image satisfies each ISO requirement.
For each rule, examine the image carefully and decide PASS/PARTIAL/FAIL.

Rules:
{rules_list}

Respond with JSON: {{"results":[{{"rule_id":"id","status":"PASS/PARTIAL/FAIL","confidence":0.0-1.0,"evidence":["found"],"reasoning":"why"}}]}}"""


def _parse_ai_json(raw: str) -> dict | list | None:
    """Robustly extract JSON from AI response.

    Handles:
    - Pure JSON output (from format="json")
    - Markdown code blocks (```json ... ```)
    - JSON embedded in narrative text
    - Truncated JSON (best-effort repair)
    - Single result vs array
    """
    if not raw or not raw.strip():
        return None

    text = raw.strip()

    # 1. Remove markdown code block wrappers
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]  # drop opening ```json
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # 2. Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 3. Find the outermost { } or [ ] and try parsing
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                # 4. Try fixing common issues: trailing commas, unquoted values
                fixed = _repair_json(candidate)
                try:
                    return json.loads(fixed)
                except json.JSONDecodeError:
                    pass

    # 5. Try to extract individual result objects with regex
    results = _extract_results_regex(text)
    if results:
        return results

    logger.warning("Could not parse AI response (%d chars): %.100s…", len(text), text)
    return None


def _repair_json(text: str) -> str:
    """Attempt to repair common JSON issues from LLM output."""
    # Remove trailing commas before } or ]
    text = _re.sub(r",\s*([}\]])", r"\1", text)
    # Fix single quotes → double quotes (careful with apostrophes)
    # Only do this if no double quotes exist in keys/values
    if "'" in text and '"' not in text[:50]:
        text = text.replace("'", '"')
    # Fix unquoted PASS/PARTIAL/FAIL values
    text = _re.sub(r':\s*(PASS|PARTIAL|FAIL)\b', r': "\1"', text)
    # Fix truncation — close unclosed brackets/braces
    open_braces = text.count("{") - text.count("}")
    open_brackets = text.count("[") - text.count("]")
    if open_braces > 0:
        text += "}" * open_braces
    if open_brackets > 0:
        text += "]" * open_brackets
    return text


def _extract_results_regex(text: str) -> list[dict] | None:
    """Last-resort: extract key fields using regex patterns."""
    results = []
    # Pattern: look for rule_id, status, confidence patterns
    rule_pattern = _re.compile(
        r'"?rule_id"?\s*:\s*"([^"]+)".*?'
        r'"?status"?\s*:\s*"(PASS|PARTIAL|FAIL)".*?'
        r'"?confidence"?\s*:\s*([\d.]+)',
        _re.DOTALL | _re.IGNORECASE,
    )
    for match in rule_pattern.finditer(text):
        results.append({
            "rule_id": match.group(1),
            "status": match.group(2).upper(),
            "confidence": float(match.group(3)),
            "evidence": [],
            "reasoning": "extracted via regex fallback",
        })

    return results if results else None


def ai_verify_rule_text(
    rule: dict,
    ocr_text: str,
    ai_provider,
) -> MatchResult:
    """
    Use AI to verify a rule against OCR text only (no image).
    Fast — uses the text model (llama3.2 3B). 

    Args:
        rule: The compliance rule dict.
        ocr_text: Full OCR text from the label.
        ai_provider: An AIProvider instance.

    Returns:
        MatchResult with AI text-based assessment.
    """
    # Truncate text to avoid overwhelming the model
    label_text = ocr_text[:2000] if len(ocr_text) > 2000 else ocr_text

    prompt = _AI_SINGLE_RULE_PROMPT.format(
        rule_id=rule.get("id", "unknown"),
        iso_ref=rule.get("iso_ref", ""),
        description=rule.get("description", ""),
        markers=", ".join(rule.get("markers", [])[:8]),
        label_text=label_text,
    )

    try:
        raw = ai_provider.analyze(prompt)
        parsed = _parse_ai_json(raw)

        if parsed and isinstance(parsed, dict):
            status = parsed.get("status", "FAIL").upper()
            if status not in ("PASS", "PARTIAL", "FAIL"):
                status = "FAIL"
            return MatchResult(
                rule_id=rule.get("id", "unknown"),
                rule_description=rule.get("description", ""),
                iso_ref=rule.get("iso_ref", ""),
                status=status,
                confidence=float(parsed.get("confidence", 0.5)),
                method="ai_text",
                evidence=parsed.get("evidence", []),
                severity=rule.get("severity", "critical"),
                new_in_2024=rule.get("new_in_2024", False),
                details=parsed.get("reasoning", ""),
            )
        else:
            logger.warning("AI text response not parseable for rule %s", rule.get("id"))

    except Exception as e:
        logger.error("AI text verify failed for rule %s: %s", rule.get("id"), e)

    return MatchResult(
        rule_id=rule.get("id", "unknown"),
        rule_description=rule.get("description", ""),
        iso_ref=rule.get("iso_ref", ""),
        status="FAIL",
        confidence=0.0,
        method="ai_text",
        severity=rule.get("severity", "critical"),
        new_in_2024=rule.get("new_in_2024", False),
        details="AI text analysis failed",
    )


def ai_verify_rules_text_batch(
    rules: list[dict],
    ocr_text: str,
    ai_provider,
    batch_size: int = 5,
) -> list[MatchResult]:
    """
    Use AI text model to verify rules in small batches (no image needed).
    Much faster than vision — suitable for confirming text presence.

    Args:
        rules: List of compliance rule dicts to verify.
        ocr_text: Full OCR text from the label.
        ai_provider: An AIProvider instance.
        batch_size: Number of rules per AI call (default 5).

    Returns:
        List of MatchResult, one per rule.
    """
    label_text = ocr_text[:2000] if len(ocr_text) > 2000 else ocr_text
    all_results: list[MatchResult] = []

    # Split rules into small batches
    for batch_start in range(0, len(rules), batch_size):
        batch = rules[batch_start:batch_start + batch_size]

        # Build compact rules list for prompt
        rules_desc = "\n".join(
            f"- {r.get('id', '?')}: {r.get('description', '')} "
            f"(look for: {', '.join(r.get('markers', [])[:5])})"
            for r in batch
        )

        prompt = _AI_BATCH_TEXT_PROMPT.format(
            rules_list=rules_desc,
            label_text=label_text,
        )

        try:
            raw = ai_provider.analyze(prompt)
            parsed = _parse_ai_json(raw)

            # Handle wrapped format {"results": [...]}
            if parsed and isinstance(parsed, dict) and "results" in parsed:
                parsed = parsed["results"]

            if parsed and isinstance(parsed, list):
                ai_map = {}
                for item in parsed:
                    if isinstance(item, dict) and "rule_id" in item:
                        ai_map[item["rule_id"]] = item

                for rule in batch:
                    rid = rule.get("id", "unknown")
                    ai_result = ai_map.get(rid, {})
                    status = ai_result.get("status", "FAIL").upper()
                    if status not in ("PASS", "PARTIAL", "FAIL"):
                        status = "FAIL"

                    all_results.append(MatchResult(
                        rule_id=rid,
                        rule_description=rule.get("description", ""),
                        iso_ref=rule.get("iso_ref", ""),
                        status=status,
                        confidence=float(ai_result.get("confidence", 0.0)),
                        method="ai_text",
                        evidence=ai_result.get("evidence", []),
                        severity=rule.get("severity", "critical"),
                        new_in_2024=rule.get("new_in_2024", False),
                        details=ai_result.get("reasoning", ""),
                    ))
            else:
                # Batch parse failed — fall back to individual
                logger.warning(
                    "AI text batch %d-%d parse failed, trying individual",
                    batch_start, batch_start + len(batch),
                )
                for rule in batch:
                    all_results.append(ai_verify_rule_text(rule, ocr_text, ai_provider))

        except Exception as e:
            logger.error("AI text batch error: %s", e)
            for rule in batch:
                all_results.append(MatchResult(
                    rule_id=rule.get("id", "unknown"),
                    rule_description=rule.get("description", ""),
                    iso_ref=rule.get("iso_ref", ""),
                    status="FAIL",
                    confidence=0.0,
                    method="ai_text",
                    severity=rule.get("severity", "critical"),
                    new_in_2024=rule.get("new_in_2024", False),
                    details=f"AI text batch error: {e}",
                ))

    return all_results


def ai_verify_rule(
    rule: dict,
    image_path: str | Path,
    ai_provider,
) -> MatchResult:
    """
    Use a multimodal AI vision model to visually verify a single rule
    against a label page image.
    """
    markers = rule.get("markers", [])[:8]
    prompt = (
        f"Check if this label image satisfies: {rule.get('id', '')} "
        f"({rule.get('iso_ref', '')}): {rule.get('description', '')}. "
        f"Look for: {', '.join(markers)}. "
        f'Respond JSON: {{"status":"PASS/PARTIAL/FAIL","confidence":0.0-1.0,'
        f'"evidence":["found"],"reasoning":"why"}}'
    )

    try:
        raw = ai_provider.analyze_with_image(prompt, str(image_path))
        parsed = _parse_ai_json(raw)

        if parsed and isinstance(parsed, dict):
            status = parsed.get("status", "FAIL").upper()
            if status not in ("PASS", "PARTIAL", "FAIL"):
                status = "FAIL"
            return MatchResult(
                rule_id=rule.get("id", "unknown"),
                rule_description=rule.get("description", ""),
                iso_ref=rule.get("iso_ref", ""),
                status=status,
                confidence=float(parsed.get("confidence", 0.0)),
                method="ai_vision",
                evidence=parsed.get("evidence", []),
                severity=rule.get("severity", "critical"),
                new_in_2024=rule.get("new_in_2024", False),
                details=parsed.get("reasoning", ""),
            )
        else:
            logger.warning("AI vision response not parseable for rule %s", rule.get("id"))

    except Exception as e:
        logger.error("AI vision failed for rule %s: %s", rule.get("id"), e)

    return MatchResult(
        rule_id=rule.get("id", "unknown"),
        rule_description=rule.get("description", ""),
        iso_ref=rule.get("iso_ref", ""),
        status="FAIL",
        confidence=0.0,
        method="ai_vision",
        severity=rule.get("severity", "critical"),
        new_in_2024=rule.get("new_in_2024", False),
        details="AI vision analysis failed",
    )


def ai_verify_rules_batch(
    rules: list[dict],
    image_path: str | Path,
    ai_provider,
    batch_size: int = 5,
) -> list[MatchResult]:
    """
    Use multimodal AI vision model to verify rules in small batches.
    Splits into groups of `batch_size` to avoid overwhelming the model.
    """
    all_results: list[MatchResult] = []

    for batch_start in range(0, len(rules), batch_size):
        batch = rules[batch_start:batch_start + batch_size]

        rules_desc = "\n".join(
            f"- {r.get('id', '?')}: {r.get('description', '')} "
            f"(look for: {', '.join(r.get('markers', [])[:5])})"
            for r in batch
        )

        prompt = _AI_VISION_PROMPT.format(rules_list=rules_desc)

        try:
            raw = ai_provider.analyze_with_image(prompt, str(image_path))
            parsed = _parse_ai_json(raw)

            # Handle wrapped format {"results": [...]}
            if parsed and isinstance(parsed, dict) and "results" in parsed:
                parsed = parsed["results"]

            if parsed and isinstance(parsed, list):
                ai_map = {}
                for item in parsed:
                    if isinstance(item, dict) and "rule_id" in item:
                        ai_map[item["rule_id"]] = item

                for rule in batch:
                    rid = rule.get("id", "unknown")
                    ai_result = ai_map.get(rid, {})
                    status = ai_result.get("status", "FAIL").upper()
                    if status not in ("PASS", "PARTIAL", "FAIL"):
                        status = "FAIL"

                    all_results.append(MatchResult(
                        rule_id=rid,
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
                logger.warning(
                    "AI vision batch %d-%d parse failed, trying individual",
                    batch_start, batch_start + len(batch),
                )
                for rule in batch:
                    all_results.append(ai_verify_rule(rule, image_path, ai_provider))

        except Exception as e:
            logger.error("AI vision batch error: %s", e)
            for rule in batch:
                all_results.append(MatchResult(
                    rule_id=rule.get("id", "unknown"),
                    rule_description=rule.get("description", ""),
                    iso_ref=rule.get("iso_ref", ""),
                    status="FAIL",
                    confidence=0.0,
                    method="ai_vision",
                    severity=rule.get("severity", "critical"),
                    new_in_2024=rule.get("new_in_2024", False),
                    details=f"AI vision batch error: {e}",
                ))

    return all_results
