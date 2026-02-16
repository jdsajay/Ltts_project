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
)
from label_compliance.compliance.rules import load_rules
from label_compliance.compliance.scorer import ComplianceScore, compute_score
from label_compliance.config import get_settings
from label_compliance.document.barcode_reader import read_barcodes, BarcodeResult
from label_compliance.document.font_analyzer import extract_fonts, FontInfo, validate_font_size
from label_compliance.document.image_renderer import render_pages
from label_compliance.document.layout import analyze_layout, Zone
from label_compliance.document.ocr import run_ocr, OCRResult
from label_compliance.document.pdf_reader import read_pdf, PDFData
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
    score: ComplianceScore | None = None
    image_dir: Path | None = None


def check_label(
    pdf_path: Path,
    rules: list[dict] | None = None,
    semantic: bool = False,
    use_ai: bool = False,
) -> LabelResult:
    """
    Run the full compliance check on a label PDF.

    Args:
        pdf_path: Path to the label PDF to check.
        rules: Optional rule list. Defaults to profile-matched rules.
        semantic: Whether to also run semantic matching (requires KB).
        use_ai: Whether to run AI multimodal verification on each page
                for highest accuracy (requires Ollama or OpenAI).

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

    # ── Initialize AI provider if requested ───────────
    ai_provider = None
    if use_ai:
        try:
            from label_compliance.ai.base import get_ai_provider
            ai_provider = get_ai_provider()
            if ai_provider.name == "none":
                logger.warning("AI provider is 'none' — AI verification disabled")
                ai_provider = None
            else:
                logger.info("AI verification enabled: %s", ai_provider.name)
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

        # Rule matching for this page
        for rule in rules:
            match = match_rule_text(rule, ocr_result)
            page_result.matches.append(match)

            # Aggregate: keep best match across pages
            rule_id = rule.get("id", "unknown")
            if rule_id not in aggregated_matches:
                aggregated_matches[rule_id] = []
            aggregated_matches[rule_id].append(match)

        # ── AI Vision Verification ────────────────────
        #  Send the page image + all rules to the AI model
        #  for multimodal visual verification.
        if ai_provider and img_path:
            logger.info("  AI: Verifying %d rules with %s…", len(rules), ai_provider.name)
            try:
                ai_results = ai_verify_rules_batch(rules, img_path, ai_provider)
                for ai_match in ai_results:
                    rid = ai_match.rule_id
                    if rid not in aggregated_matches:
                        aggregated_matches[rid] = []
                    aggregated_matches[rid].append(ai_match)
                logger.info("  AI: Done — %d results", len(ai_results))
            except Exception as e:
                logger.error("  AI verification error: %s", e)

        result.pages.append(page_result)

    # ── Step 5: Combine results across pages ──────────
    logger.info("Step 5: Aggregating results...")
    combined_matches = []
    for rule_id, matches in aggregated_matches.items():
        best = combine_match_results(matches)
        combined_matches.append(best)

    result.all_matches = combined_matches

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

    logger.info("═" * 60)
    logger.info(
        "Result: %s → %s (%.1f%%)",
        label_name, score.status, score.score_pct,
    )
    logger.info(
        "  ✅ %d PASS | ⚠️  %d PARTIAL | ❌ %d FAIL | 🔴 %d critical gaps",
        passed_count, partial_count, failed_count, score.critical_count,
    )
    logger.info("═" * 60)

    return result
