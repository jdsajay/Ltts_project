"""
Compliance Checker — Main Engine
==================================
Orchestrates the full compliance check for a single label PDF:

1. Read PDF → extract text, tables, fonts, metadata
2. **Segment** the PDF into individual label sections
   (COMBO LABEL, OUTER LID, THERMOFORM, Patient label, etc.)
3. Render pages as images
4. For each section: OCR → layout → symbols → barcodes → rules → specs → AI → symbols
5. Score compliance per section and overall
6. Return structured results

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
from label_compliance.document.image_extractor import (
    classify_pdf_pages,
    extract_embedded_images,
    PDFImageAnalysis,
)
from label_compliance.document.image_renderer import render_pages, crop_section_image
from label_compliance.document.label_segmenter import (
    segment_pdf,
    LabelSection,
    SegmentationResult,
)
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
class SectionResult:
    """Compliance results for a single label section (e.g. COMBO LABEL, OUTER LID)."""

    section_name: str  # e.g. "COMBO LABEL"
    section_type: str  # e.g. "combo_label"
    page_number: int
    eart_number: str = ""
    section_text: str = ""  # text extracted from this section
    ocr_text: str = ""  # OCR text from the rendered image region
    matches: list[MatchResult] = field(default_factory=list)
    spec_results: list[SpecsResult] = field(default_factory=list)
    symbol_comparison: SymbolComparisonReport | None = None
    score: ComplianceScore | None = None
    fonts: list[dict] = field(default_factory=list)

    @property
    def id(self) -> str:
        return f"P{self.page_number}-{self.section_type}"


@dataclass
class LabelResult:
    """Full compliance analysis results for one label PDF."""

    label_name: str
    pdf_path: Path
    profile: str = "default"
    pdf_data: PDFData | None = None
    segmentation: SegmentationResult | None = None
    sections: list[SectionResult] = field(default_factory=list)
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

    The PDF is first segmented into individual label sections
    (COMBO LABEL, OUTER LID LABEL, THERMOFORM, Patient label, etc.),
    then each section is checked independently against ISO standards.

    Args:
        pdf_path: Path to the label PDF to check.
        rules: Optional rule list. Defaults to profile-matched rules.
        semantic: Whether to also run semantic matching (requires KB).
        use_ai: Whether to run AI text-based verification (default: True).
        ai_vision: Whether to also run AI vision verification on page images.

    Returns:
        LabelResult with per-section and overall analysis and score.
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
        except Exception as e:
            logger.error("Failed to initialize AI provider: %s — proceeding without AI", e)
            ai_provider = None

    result = LabelResult(label_name=label_name, pdf_path=pdf_path, profile=profile_name)

    # ── Step 1: Read PDF ──────────────────────────────
    logger.info("Step 1: Reading PDF...")
    pdf_data = read_pdf(pdf_path)
    result.pdf_data = pdf_data

    # ── Step 1b: Classify PDF pages (IMAGE_ONLY / MIXED / TEXT_ONLY) ──
    logger.info("Step 1b: Classifying PDF pages...")
    pdf_analysis = classify_pdf_pages(pdf_path)
    has_image_pages = pdf_analysis.has_image_only_pages
    if has_image_pages:
        logger.info(
            "  ⚠️  IMAGE-ONLY pages detected: %s — will use embedded image extraction + OCR",
            pdf_analysis.image_only_pages,
        )
    mixed_pages = pdf_analysis.mixed_pages
    if mixed_pages:
        logger.info(
            "  MIXED pages (text + images): %s — will augment with embedded image OCR",
            mixed_pages,
        )

    # ── Step 2: Segment into label sections ───────────
    # (segmenter now handles image-only pages automatically)
    logger.info("Step 2: Segmenting into label sections...")
    seg = segment_pdf(pdf_path)
    result.segmentation = seg
    logger.info(
        "  Found %d sections: %s",
        seg.section_count, ", ".join(seg.section_names),
    )

    # ── Step 3: Extract fonts ─────────────────────────
    logger.info("Step 3: Analyzing fonts...")
    fonts = extract_fonts(pdf_path)
    result.fonts = fonts
    result.font_violations = validate_font_size(fonts)
    if result.font_violations:
        logger.warning("  %d font size violations found", len(result.font_violations))

    # ── Step 4: Render pages + extract embedded images ──
    logger.info("Step 4: Rendering pages as images...")
    image_dir = settings.paths.knowledge_base_dir.parent / "images" / safe_name
    image_paths = render_pages(pdf_path, output_dir=image_dir)
    result.image_dir = image_dir

    # Also extract embedded images for image-only and mixed pages
    embedded_image_map: dict[int, list[Path]] = {}
    pages_needing_extraction = pdf_analysis.image_only_pages + pdf_analysis.mixed_pages
    if pages_needing_extraction:
        logger.info("  Extracting embedded images from pages %s...", pages_needing_extraction)
        embed_dir = image_dir / "embedded"
        embedded_images = extract_embedded_images(
            pdf_path, embed_dir, pages=pages_needing_extraction,
        )
        for emb in embedded_images:
            if emb.saved_path and emb.is_label_image:
                embedded_image_map.setdefault(emb.page_number, []).append(emb.saved_path)
        logger.info(
            "  Extracted %d embedded label images",
            sum(len(v) for v in embedded_image_map.values()),
        )

    # Build page_num → image_path map
    page_image_map: dict[int, Path] = {}
    for idx, img_path in enumerate(image_paths):
        page_image_map[idx + 1] = img_path

    # ── Step 5: Process each page (OCR, layout, symbols, barcodes) ──
    page_ocr_map: dict[int, OCRResult] = {}
    page_zones_map: dict[int, list[Zone]] = {}
    page_symbols_map: dict[int, list[SymbolMatch]] = {}
    page_barcodes_map: dict[int, list[BarcodeResult]] = {}

    for i, img_path in enumerate(image_paths, 1):
        logger.info("Step 5: Processing page %d/%d...", i, len(image_paths))
        page_class = pdf_analysis.page_classifications[i - 1]
        page_result = PageResult(page_number=i, image_path=img_path)

        # OCR on the rendered page
        ocr_result = run_ocr(img_path)

        # For pages with embedded images, also OCR those and merge results
        if i in embedded_image_map:
            embedded_texts = []
            embedded_words = []
            for emb_path in embedded_image_map[i]:
                emb_ocr = run_ocr(emb_path)
                if emb_ocr.full_text.strip():
                    embedded_texts.append(emb_ocr.full_text)
                    embedded_words.extend(emb_ocr.words)

            if embedded_texts:
                # Merge: combine rendered page OCR + embedded image OCR
                combined_text = ocr_result.full_text
                if combined_text.strip():
                    combined_text += "\n"
                combined_text += "\n".join(embedded_texts)

                # Use whichever has more words (better OCR result)
                if len(embedded_words) > len(ocr_result.words):
                    ocr_result = OCRResult(
                        image_path=str(img_path),
                        image_size=ocr_result.image_size,
                        full_text=combined_text,
                        words=embedded_words,
                        text_blocks=ocr_result.text_blocks,
                    )
                else:
                    # Keep rendered page words but augment text
                    ocr_result = OCRResult(
                        image_path=str(img_path),
                        image_size=ocr_result.image_size,
                        full_text=combined_text,
                        words=ocr_result.words,
                        text_blocks=ocr_result.text_blocks,
                    )

                logger.info(
                    "  Merged OCR (rendered + %d embedded images): %d words, %d chars",
                    len(embedded_image_map[i]),
                    ocr_result.word_count,
                    len(ocr_result.full_text),
                )

        page_result.ocr = ocr_result
        page_ocr_map[i] = ocr_result
        logger.info("  OCR: %d words, %d chars", ocr_result.word_count, len(ocr_result.full_text))

        # Layout analysis
        zones = analyze_layout(img_path)
        page_result.zones = zones
        page_zones_map[i] = zones

        # Symbol detection (OCR-based)
        symbols = detect_symbols_from_ocr(ocr_result, rules)
        page_result.symbols = symbols
        page_symbols_map[i] = symbols

        # Barcode reading — also check embedded images
        barcodes = read_barcodes(img_path)
        if i in embedded_image_map:
            for emb_path in embedded_image_map[i]:
                emb_barcodes = read_barcodes(emb_path)
                barcodes.extend(emb_barcodes)
        page_result.barcodes = barcodes
        page_barcodes_map[i] = barcodes
        if barcodes:
            logger.info("  Barcodes: %d found", len(barcodes))

        result.pages.append(page_result)

    # ── Step 6: Check each section independently ──────
    logger.info("Step 6: Checking each section against ISO rules...")
    overall_aggregated: dict[str, list[MatchResult]] = {}

    for section in seg.sections:
        sec_name = section.name
        sec_page = section.page_number
        logger.info("─" * 40)
        logger.info("Section: %s (page %d)", sec_name, sec_page)
        logger.info("─" * 40)

        sec_result = SectionResult(
            section_name=sec_name,
            section_type=section.section_type,
            page_number=sec_page,
            eart_number=section.eart_number,
            section_text=section.text,
            fonts=section.fonts,
        )

        # Get OCR text for this section
        # Use the section's own extracted text + OCR from the page
        ocr_result = page_ocr_map.get(sec_page)
        if ocr_result:
            sec_result.ocr_text = ocr_result.full_text

        # Combine section text (from PyMuPDF) + OCR text for matching
        # Section text is more accurate for vector PDFs; OCR covers scanned PDFs
        combined_text = section.text
        if ocr_result and ocr_result.full_text:
            combined_text = section.text + "\n" + ocr_result.full_text

        zones = page_zones_map.get(sec_page, [])
        symbols = page_symbols_map.get(sec_page, [])
        barcodes = page_barcodes_map.get(sec_page, [])
        img_path = page_image_map.get(sec_page)

        render_dpi = settings.document.render_dpi
        img_size = ocr_result.image_size if ocr_result else (0, 0)

        sec_aggregated: dict[str, list[MatchResult]] = {}

        # ── Rule matching for this section ──
        for rule in rules:
            # Create a synthetic OCR result with section text for matching
            section_ocr = _make_section_ocr(combined_text, ocr_result)
            match = match_rule_text(rule, section_ocr)

            # Specs validation
            spec_result = validate_rule_specs(
                rule=rule,
                ocr_result=section_ocr,
                fonts=fonts,
                zones=zones,
                symbols=symbols,
                barcodes=barcodes,
                page_number=sec_page,
                dpi=render_dpi,
                image_size=img_size,
            )
            sec_result.spec_results.append(spec_result)

            # Merge spec violations
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
                if match.status == "PASS":
                    match.status = "PARTIAL"
                    match.details += " | DOWNGRADED: spec violations detected"
                    logger.warning(
                        "  Rule %s downgraded to PARTIAL: %d spec violations",
                        rule.get("id"), len(spec_result.violations),
                    )
            else:
                match.spec_details = spec_result.details

            # Tag match with section info
            match.details = f"[{sec_name}] {match.details}"
            sec_result.matches.append(match)

            rule_id = rule.get("id", "unknown")
            sec_aggregated.setdefault(rule_id, []).append(match)
            overall_aggregated.setdefault(rule_id, []).append(match)

        # ── AI Text Verification for this section ──
        if ai_provider and combined_text.strip():
            ai_mode = getattr(settings.ai, "ai_mode", "smart")
            ai_batch_size = getattr(settings.ai, "batch_size", 5)

            if ai_mode == "smart":
                rules_to_verify = [
                    r for r in rules
                    if any(
                        m.rule_id == r.get("id") and m.status in ("FAIL", "PARTIAL")
                        for m in sec_result.matches
                    )
                ]
            else:
                rules_to_verify = rules

            if rules_to_verify:
                logger.info(
                    "  AI text (%s): Checking %d rules for [%s]…",
                    ai_mode, len(rules_to_verify), sec_name,
                )
                try:
                    ai_text_results = ai_verify_rules_text_batch(
                        rules_to_verify,
                        combined_text,
                        ai_provider,
                        batch_size=ai_batch_size,
                    )
                    for ai_match in ai_text_results:
                        ai_match.details = f"[{sec_name}] {ai_match.details}"
                        rid = ai_match.rule_id
                        sec_aggregated.setdefault(rid, []).append(ai_match)
                        overall_aggregated.setdefault(rid, []).append(ai_match)
                    logger.info("  AI text: Done — %d results", len(ai_text_results))
                except Exception as e:
                    logger.error("  AI text error for [%s]: %s", sec_name, e)

        # ── AI Vision for this section ──
        # Auto-enable vision for image-only pages (critical for accuracy)
        page_class = pdf_analysis.page_classifications[sec_page - 1] if sec_page <= len(pdf_analysis.page_classifications) else None
        should_use_vision = ai_vision or (page_class and page_class.is_image_only)
        
        if ai_provider and should_use_vision and img_path:
            ai_batch_size = getattr(settings.ai, "batch_size", 5)

            # For image-only pages, prefer embedded images (higher quality)
            # over rendered page images
            section_img = img_path  # fallback to rendered page
            
            # Try embedded image first (higher quality for image-only PDFs)
            if sec_page in embedded_image_map and embedded_image_map[sec_page]:
                # Use the largest embedded image (most likely the full label)
                best_emb = max(embedded_image_map[sec_page], key=lambda p: p.stat().st_size)
                section_img = best_emb
                logger.info(
                    "  Using embedded image for AI vision: %s",
                    best_emb.name,
                )
            elif section.bbox:
                # Crop individual section image if bbox is available
                crop_dir = img_path.parent / "sections"
                crop_dir.mkdir(parents=True, exist_ok=True)
                section_safe = safe_filename(sec_name)
                crop_path = crop_dir / f"{section_safe}.png"
                try:
                    section_img = crop_section_image(
                        full_page_image=img_path,
                        bbox=section.bbox,
                        output_path=crop_path,
                        dpi=render_dpi,
                    )
                    logger.info(
                        "  Cropped section image: %s → %s",
                        sec_name, crop_path.name,
                    )
                except Exception as e:
                    logger.warning("  Could not crop section image: %s", e)
                    section_img = img_path

            vision_note = " (auto-enabled for image-only page)" if not ai_vision else ""
            logger.info("  AI vision%s: [%s] → %d rules…", vision_note, sec_name, len(rules))
            try:
                ai_results = ai_verify_rules_batch(
                    rules, section_img, ai_provider, batch_size=ai_batch_size,
                )
                for ai_match in ai_results:
                    ai_match.details = f"[{sec_name}] {ai_match.details}"
                    rid = ai_match.rule_id
                    sec_aggregated.setdefault(rid, []).append(ai_match)
                    overall_aggregated.setdefault(rid, []).append(ai_match)
                logger.info("  AI vision: Done — %d results", len(ai_results))
            except Exception as e:
                logger.error("  AI vision error for [%s]: %s", sec_name, e)

        # ── Symbol Library Comparison for this section ──
        try:
            section_ocr_for_sym = _make_section_ocr(combined_text, ocr_result)
            # Use embedded image (higher quality) or cropped section image
            section_img_for_sym = None
            if sec_page in embedded_image_map and embedded_image_map[sec_page]:
                # Use the largest embedded image for symbol detection
                section_img_for_sym = max(
                    embedded_image_map[sec_page], key=lambda p: p.stat().st_size
                )
            elif section.bbox and img_path:
                crop_dir = img_path.parent / "sections"
                section_safe = safe_filename(sec_name)
                crop_path = crop_dir / f"{section_safe}.png"
                if crop_path.exists():
                    section_img_for_sym = crop_path
            sym_report = compare_symbols_combined(
                ocr_result=section_ocr_for_sym,
                image_path=section_img_for_sym,
                ai_provider=ai_provider,
                skip_visual=(page_class and page_class.is_image_only) if page_class else False,
            )
            sec_result.symbol_comparison = sym_report
            logger.info("  Symbols [%s]: %s", sec_name, sym_report.summary)
        except Exception as e:
            logger.error("  Symbol comparison error for [%s]: %s", sec_name, e)

        # ── Score this section ──
        sec_matches = []
        for rid, matches in sec_aggregated.items():
            sec_matches.append(combine_match_results(matches))

        sec_result.score = compute_score(
            label_name=f"{label_name}/{sec_name}",
            match_results=sec_matches,
            compliant_threshold=settings.compliance.score_compliant,
            partial_threshold=settings.compliance.score_partial,
        )

        p = sum(1 for m in sec_matches if m.status == "PASS")
        f_ = sum(1 for m in sec_matches if m.status == "FAIL")
        pt = sum(1 for m in sec_matches if m.status == "PARTIAL")
        logger.info(
            "  [%s] → %s (%.1f%%) | ✅ %d PASS | ⚠️ %d PARTIAL | ❌ %d FAIL",
            sec_name, sec_result.score.status, sec_result.score.score_pct, p, pt, f_,
        )

        result.sections.append(sec_result)

    # ── Step 7: Overall aggregation ───────────────────
    logger.info("Step 7: Aggregating overall results...")
    combined_matches = []
    for rule_id, matches in overall_aggregated.items():
        best = combine_match_results(matches)
        combined_matches.append(best)

    result.all_matches = combined_matches

    # Aggregate spec results
    all_spec_results: list[SpecsResult] = []
    for sec in result.sections:
        all_spec_results.extend(sec.spec_results)
    result.all_spec_results = all_spec_results

    total_spec_violations = sum(len(sr.violations) for sr in all_spec_results)
    rules_with_violations = sum(1 for sr in all_spec_results if not sr.all_passed)
    if total_spec_violations > 0:
        logger.warning(
            "  Specs: %d total violations across %d rules",
            total_spec_violations, rules_with_violations,
        )

    # Aggregate symbol comparison (best across sections)
    best_sym_comparison: SymbolComparisonReport | None = None
    for sec in result.sections:
        if sec.symbol_comparison is not None:
            if best_sym_comparison is None or sec.symbol_comparison.score > best_sym_comparison.score:
                best_sym_comparison = sec.symbol_comparison
    result.symbol_comparison = best_sym_comparison

    # ── Step 8: Overall Score ─────────────────────────
    logger.info("Step 8: Computing overall compliance score...")
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
    logger.info("  📋 Sections analyzed:")
    for sec in result.sections:
        if sec.score:
            logger.info(
                "     • %s → %s (%.1f%%)",
                sec.section_name, sec.score.status, sec.score.score_pct,
            )
    logger.info("═" * 60)

    return result


def _make_section_ocr(
    section_text: str, page_ocr: OCRResult | None
) -> OCRResult:
    """
    Create a synthetic OCRResult by combining section text with
    the page-level OCR word boxes (for position-based checks).

    For scanned PDFs (0 extracted text), falls back to full OCR.
    For vector PDFs, uses the extracted text (more accurate).
    """
    if page_ocr is None:
        return OCRResult(
            full_text=section_text,
            words=[],
            image_path="",
            image_size=(0, 0),
        )

    # If section text is empty (scanned PDF), use full OCR
    if not section_text.strip():
        return page_ocr

    # Use section text but keep word-level bounding boxes from OCR
    return OCRResult(
        full_text=section_text,
        words=page_ocr.words,
        image_path=page_ocr.image_path,
        image_size=page_ocr.image_size,
    )
