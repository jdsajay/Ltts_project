"""
Compliance Checker — Main Engine
==================================
Orchestrates the full compliance check for a single label PDF:

1. Read PDF → extract text, tables, fonts, metadata
2. Render pages as images
3. OCR each page
4. Detect layout zones
5. Detect symbols (OCR + visual + barcode)
6. Match all rules (text + semantic + visual)
7. Score compliance
8. Return structured results

This is the primary entry point for checking a label.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from label_compliance.compliance.matcher import (
    MatchResult,
    match_rule_text,
    combine_match_results,
    ai_verify_rules_batch,
    ai_verify_rules_text_batch,
)
from label_compliance.compliance.rules import load_rules
from label_compliance.compliance.scorer import ComplianceScore, compute_score
from label_compliance.compliance.specs_validator import (
    validate_rule_specs,
    SpecsResult,
    SpecViolation,
)
from label_compliance.config import get_settings
from label_compliance.document.barcode_reader import read_barcodes, BarcodeResult
from label_compliance.document.font_analyzer import extract_fonts, FontInfo, validate_font_size
from label_compliance.document.image_renderer import render_pages
from label_compliance.document.layout import analyze_layout, Zone
from label_compliance.document.ocr import run_ocr, OCRResult
from label_compliance.document.pdf_reader import read_pdf, PDFData
from label_compliance.document.symbol_comparator import (
    compare_symbols_combined,
    SymbolComparisonReport,
)
from label_compliance.document.symbol_detector import detect_symbols_from_ocr, SymbolMatch
from label_compliance.utils.helpers import safe_filename
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


@dataclass
class PageResult:
    """Compliance analysis results for a single page."""

    page_number: int
    image_path: Path | None = None
    ocr: OCRResult | None = None
    symbols: list[SymbolMatch] = field(default_factory=list)
    barcodes: list[BarcodeResult] = field(default_factory=list)
    zones: list[Zone] = field(default_factory=list)
    matches: list[MatchResult] = field(default_factory=list)
    spec_results: list[SpecsResult] = field(default_factory=list)
    symbol_comparison: SymbolComparisonReport | None = None


@dataclass
class LabelResult:
    """Full compliance analysis results for one label PDF."""

    label_name: str
    pdf_path: Path
    profile: str = "default"
    pdf_data: PDFData | None = None
    pages: list[PageResult] = field(default_factory=list)
    fonts: list[FontInfo] = field(default_factory=list)
    font_violations: list[dict] = field(default_factory=list)
    all_matches: list[MatchResult] = field(default_factory=list)
    all_spec_results: list[SpecsResult] = field(default_factory=list)
    symbol_comparison: SymbolComparisonReport | None = None
    score: ComplianceScore | None = None
    image_dir: Path | None = None


def check_label(
    pdf_path: Path,
    rules: list[dict] | None = None,
    semantic: bool = False,
    use_ai: bool = True,
    ai_vision: bool = False,
) -> LabelResult:
    """
    Run the full compliance check on a label PDF.

    AI text analysis runs by default. Vision analysis is optional (slow on CPU).

    Args:
        pdf_path: Path to the label PDF to check.
        rules: Optional rule list. Defaults to profile-matched rules.
        semantic: Whether to also run semantic matching (requires KB).
        use_ai: Whether to run AI text-based verification (default: True).
        ai_vision: Whether to also run AI vision verification on page images
                   (slow on CPU — requires Ollama llama3.2-vision).

    Returns:
        LabelResult with full analysis and score.
    """
    from label_compliance.compliance.rules import resolve_rules_for_label

    settings = get_settings()
    settings.ensure_dirs()
    label_name = pdf_path.stem
    safe_name = safe_filename(label_name)

    logger.info("═" * 60)
    logger.info("Checking label: %s", label_name)
    logger.info("═" * 60)

    profile_name = "default"
    if rules is None:
        rules, profile_name = resolve_rules_for_label(pdf_path.name)
        logger.info("Profile: %s → %d rules", profile_name, len(rules))

    # ── Initialize AI provider ─────────────────────────
    ai_provider = None
    if use_ai:
        try:
            from label_compliance.ai.base import get_ai_provider
            ai_provider = get_ai_provider()
            if ai_provider.name == "none":
                logger.warning("AI provider is 'none' — AI verification disabled")
                ai_provider = None
            else:
                logger.info("AI enabled: %s", ai_provider.name)
                if ai_vision:
                    logger.info("AI vision mode: ON (will analyze page images)")
                else:
                    logger.info("AI text mode: ON (fast OCR text analysis)")
        except Exception as e:
            logger.error("Failed to initialize AI provider: %s — proceeding without AI", e)
            ai_provider = None

    result = LabelResult(label_name=label_name, pdf_path=pdf_path, profile=profile_name)

    # ── Step 1: Read PDF ──────────────────────────────
    logger.info("Step 1: Reading PDF...")
    pdf_data = read_pdf(pdf_path)
    result.pdf_data = pdf_data

    # ── Step 2: Extract fonts ─────────────────────────
    logger.info("Step 2: Analyzing fonts...")
    fonts = extract_fonts(pdf_path)
    result.fonts = fonts
    result.font_violations = validate_font_size(fonts)
    if result.font_violations:
        logger.warning("  %d font size violations found", len(result.font_violations))

    # ── Step 3: Render pages ──────────────────────────
    logger.info("Step 3: Rendering pages as images...")
    image_dir = settings.paths.knowledge_base_dir.parent / "images" / safe_name
    image_paths = render_pages(pdf_path, output_dir=image_dir)
    result.image_dir = image_dir

    # ── Step 4: Process each page ─────────────────────
    aggregated_matches: dict[str, list[MatchResult]] = {}

    for i, img_path in enumerate(image_paths, 1):
        logger.info("Step 4: Processing page %d/%d...", i, len(image_paths))
        page_result = PageResult(page_number=i, image_path=img_path)

        # OCR
        ocr_result = run_ocr(img_path)
        page_result.ocr = ocr_result
        logger.info("  OCR: %d words, %d chars", ocr_result.word_count, len(ocr_result.full_text))

        # Layout analysis
        zones = analyze_layout(img_path)
        page_result.zones = zones
        logger.debug("  Layout: %d zones", len(zones))

        # Symbol detection (OCR-based)
        symbols = detect_symbols_from_ocr(ocr_result, rules)
        page_result.symbols = symbols

        # Barcode reading
        barcodes = read_barcodes(img_path)
        page_result.barcodes = barcodes
        if barcodes:
            logger.info("  Barcodes: %d found", len(barcodes))

        # Rule matching + specs validation for this page
        render_dpi = settings.document.render_dpi
        img_size = ocr_result.image_size if ocr_result else (0, 0)

        for rule in rules:
            match = match_rule_text(rule, ocr_result)

            # ── Specs validation (font, size, position, etc.) ──
            spec_result = validate_rule_specs(
                rule=rule,
                ocr_result=ocr_result,
                fonts=fonts,
                zones=zones,
                symbols=symbols,
                barcodes=barcodes,
                page_number=i,
                dpi=render_dpi,
                image_size=img_size,
            )
            page_result.spec_results.append(spec_result)

            # Merge spec violations into match result
            if not spec_result.all_passed:
                match.specs_passed = False
                match.spec_violations = [
                    {
                        "rule_id": v.rule_id,
                        "spec_field": v.spec_field,
                        "requirement": v.requirement,
                        "actual": v.actual,
                        "severity": v.severity,
                        "page": v.page,
                        "location": v.location,
                    }
                    for v in spec_result.violations
                ]
                match.spec_details = spec_result.details
                # Downgrade PASS → PARTIAL if specs fail
                if match.status == "PASS":
                    match.status = "PARTIAL"
                    match.details += " | DOWNGRADED: spec violations detected"
                    logger.warning(
                        "  Rule %s downgraded to PARTIAL: %d spec violations",
                        rule.get("id"), len(spec_result.violations),
                    )
            else:
                match.spec_details = spec_result.details

            page_result.matches.append(match)

            # Aggregate: keep best match across pages
            rule_id = rule.get("id", "unknown")
            if rule_id not in aggregated_matches:
                aggregated_matches[rule_id] = []
            aggregated_matches[rule_id].append(match)

        logger.info(
            "  Specs: %d rules checked, %d with violations",
            len(page_result.spec_results),
            sum(1 for sr in page_result.spec_results if not sr.all_passed),
        )

        # ── AI Text Verification ──────────────────────
        #  Send OCR text + rules to AI text model for fast verification.
        #  In "smart" mode, only re-check FAIL/PARTIAL rules.
        if ai_provider and ocr_result:
            ai_mode = getattr(settings.ai, "ai_mode", "smart")
            ai_batch_size = getattr(settings.ai, "batch_size", 5)

            if ai_mode == "smart":
                # Only AI-verify rules that text matching found FAIL or PARTIAL
                rules_to_verify = [
                    r for r in rules
                    if any(
                        m.rule_id == r.get("id") and m.status in ("FAIL", "PARTIAL")
                        for m in page_result.matches
                    )
                ]
                if rules_to_verify:
                    logger.info(
                        "  AI text (smart): Re-checking %d FAIL/PARTIAL rules…",
                        len(rules_to_verify),
                    )
                else:
                    logger.info("  AI text (smart): All rules PASS — skipping AI")
            else:
                rules_to_verify = rules
                logger.info("  AI text (full): Checking all %d rules…", len(rules_to_verify))

            if rules_to_verify:
                try:
                    ai_text_results = ai_verify_rules_text_batch(
                        rules_to_verify,
                        ocr_result.full_text,
                        ai_provider,
                        batch_size=ai_batch_size,
                    )
                    for ai_match in ai_text_results:
                        rid = ai_match.rule_id
                        if rid not in aggregated_matches:
                            aggregated_matches[rid] = []
                        aggregated_matches[rid].append(ai_match)
                    logger.info("  AI text: Done — %d results", len(ai_text_results))
                except Exception as e:
                    logger.error("  AI text verification error: %s", e)

        # ── AI Vision Verification (optional, slow) ───
        #  Send the page image + rules to the AI vision model.
        if ai_provider and ai_vision and img_path:
            ai_batch_size = getattr(settings.ai, "batch_size", 5)
            logger.info("  AI vision: Verifying %d rules with %s…", len(rules), ai_provider.name)
            try:
                ai_results = ai_verify_rules_batch(
                    rules, img_path, ai_provider, batch_size=ai_batch_size,
                )
                for ai_match in ai_results:
                    rid = ai_match.rule_id
                    if rid not in aggregated_matches:
                        aggregated_matches[rid] = []
                    aggregated_matches[rid].append(ai_match)
                logger.info("  AI vision: Done — %d results", len(ai_results))
            except Exception as e:
                logger.error("  AI vision error: %s", e)

        # ── Symbol Library Comparison ─────────────────
        try:
            sym_report = compare_symbols_combined(
                ocr_result=ocr_result,
                image_path=None,  # text-only for speed; use image_path for visual
            )
            page_result.symbol_comparison = sym_report
            logger.info(
                "  Symbols: %s",
                sym_report.summary,
            )
        except Exception as e:
            logger.error("  Symbol comparison error: %s", e)

        result.pages.append(page_result)

    # ── Step 5: Combine results across pages ──────────
    logger.info("Step 5: Aggregating results...")
    combined_matches = []
    for rule_id, matches in aggregated_matches.items():
        best = combine_match_results(matches)
        combined_matches.append(best)

    result.all_matches = combined_matches

    # ── Step 5b: Aggregate spec results ───────────────
    all_spec_results: list[SpecsResult] = []
    for page in result.pages:
        all_spec_results.extend(page.spec_results)
    result.all_spec_results = all_spec_results

    total_spec_violations = sum(
        len(sr.violations) for sr in all_spec_results
    )
    rules_with_violations = sum(
        1 for sr in all_spec_results if not sr.all_passed
    )
    if total_spec_violations > 0:
        logger.warning(
            "  Specs: %d total violations across %d rules",
            total_spec_violations, rules_with_violations,
        )
    else:
        logger.info("  Specs: All passed ✓")

    # ── Step 5c: Aggregate symbol comparison ──────────
    best_sym_comparison: SymbolComparisonReport | None = None
    for page in result.pages:
        if page.symbol_comparison is not None:
            if best_sym_comparison is None or page.symbol_comparison.score > best_sym_comparison.score:
                best_sym_comparison = page.symbol_comparison
    result.symbol_comparison = best_sym_comparison
    if best_sym_comparison and best_sym_comparison.total_required > 0:
        logger.info(
            "  Symbol Library: %d/%d found, %d partial, %d missing (%.0f%%)",
            best_sym_comparison.total_found,
            best_sym_comparison.total_required,
            best_sym_comparison.total_partial,
            best_sym_comparison.total_missing,
            best_sym_comparison.score * 100,
        )

    # ── Step 6: Score ─────────────────────────────────
    logger.info("Step 6: Computing compliance score...")
    score = compute_score(
        label_name=label_name,
        match_results=combined_matches,
        compliant_threshold=settings.compliance.score_compliant,
        partial_threshold=settings.compliance.score_partial,
    )
    result.score = score

    passed_count = sum(1 for m in combined_matches if m.status == "PASS")
    failed_count = sum(1 for m in combined_matches if m.status == "FAIL")
    partial_count = sum(1 for m in combined_matches if m.status == "PARTIAL")
    specs_failed = sum(1 for m in combined_matches if not m.specs_passed)

    logger.info("═" * 60)
    logger.info(
        "Result: %s → %s (%.1f%%)",
        label_name, score.status, score.score_pct,
    )
    logger.info(
        "  ✅ %d PASS | ⚠️  %d PARTIAL | ❌ %d FAIL | 🔴 %d critical gaps",
        passed_count, partial_count, failed_count, score.critical_count,
    )
    logger.info(
        "  📏 Spec violations: %d total across %d rules (%d rules had spec failures)",
        total_spec_violations, rules_with_violations, specs_failed,
    )
    if best_sym_comparison and best_sym_comparison.total_required > 0:
        logger.info(
            "  🏷️  Symbol library: %d/%d found | %d partial | %d missing",
            best_sym_comparison.total_found,
            best_sym_comparison.total_required,
            best_sym_comparison.total_partial,
            best_sym_comparison.total_missing,
        )
    logger.info("═" * 60)

    return result
