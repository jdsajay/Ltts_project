"""
Redline Validator
==================
Compares our generated redline output against sample (human-produced)
redline PDFs to measure how close our automated results are.

Two comparison approaches:
  1. Visual diff — render both PDFs as images, compute SSIM/pixel diff
  2. Text diff  — extract text changes between clean and sample redline,
                  compare to our detected gaps
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from label_compliance.config import get_settings
from label_compliance.document.image_renderer import render_pages
from label_compliance.document.ocr import run_ocr
from label_compliance.document.pdf_reader import read_pdf
from label_compliance.utils.helpers import safe_filename
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)


@dataclass
class TextDiff:
    """A text-level change found in the sample redline."""
    text: str
    change_type: str  # "added", "removed", "modified"
    page: int = 0


@dataclass
class ValidationResult:
    """Result of comparing our output vs sample redline."""
    label_name: str
    clean_pdf: Path
    sample_redline_pdf: Path

    # Text-level comparison
    sample_changes: list[TextDiff] = field(default_factory=list)
    our_gaps_found: list[str] = field(default_factory=list)
    our_gaps_missed: list[str] = field(default_factory=list)
    overlap_count: int = 0
    precision: float = 0.0   # what fraction of our findings match sample
    recall: float = 0.0      # what fraction of sample changes we found

    # Visual similarity
    page_similarities: list[float] = field(default_factory=list)
    avg_similarity: float = 0.0


def find_sample_redline(clean_pdf: Path) -> Path | None:
    """
    Given a clean label PDF, find its corresponding sample redline.

    Convention: clean=DRWG107503_C.pdf → redline=DRWG107503_C_Redline.pdf
    """
    stem = clean_pdf.stem
    parent = clean_pdf.parent

    # Try common naming patterns
    candidates = [
        parent / f"{stem}_Redline.pdf",
        parent / f"{stem}_redline.pdf",
        parent / f"{stem}_REDLINE.pdf",
        parent / f"{stem} Redline.pdf",
        parent / f"{stem}-redline.pdf",
    ]

    for c in candidates:
        if c.exists():
            return c

    return None


def validate_against_sample(
    clean_pdf: Path,
    sample_redline_pdf: Path,
    our_report_json: Path | None = None,
) -> ValidationResult:
    """
    Compare our compliance findings against a sample (human) redline.

    Process:
    1. Extract text from clean PDF and sample redline PDF
    2. Diff the text to find what the human auditor changed/added
    3. Load our gap report and compare
    4. Compute precision and recall

    Args:
        clean_pdf: The clean label PDF we checked.
        sample_redline_pdf: The human-produced redline PDF to compare against.
        our_report_json: Our generated JSON report for this label.

    Returns:
        ValidationResult with comparison metrics.
    """
    result = ValidationResult(
        label_name=clean_pdf.stem,
        clean_pdf=clean_pdf,
        sample_redline_pdf=sample_redline_pdf,
    )

    # ── Step 1: Extract text from both PDFs ───────────
    logger.info("Extracting text from clean: %s", clean_pdf.name)
    clean_data = read_pdf(clean_pdf)

    logger.info("Extracting text from sample redline: %s", sample_redline_pdf.name)
    redline_data = read_pdf(sample_redline_pdf)

    # ── Step 2: OCR both for complete text ────────────
    settings = get_settings()
    settings.ensure_dirs()

    safe_name = safe_filename(clean_pdf.stem)
    clean_img_dir = settings.paths.knowledge_base_dir.parent / "images" / safe_name
    redline_img_dir = settings.paths.knowledge_base_dir.parent / "images" / f"{safe_name}_sample_redline"

    clean_images = render_pages(clean_pdf, output_dir=clean_img_dir)
    redline_images = render_pages(sample_redline_pdf, output_dir=redline_img_dir)

    clean_texts: list[str] = []
    redline_texts: list[str] = []

    for img in clean_images:
        ocr = run_ocr(img)
        clean_texts.append(ocr.full_text)

    for img in redline_images:
        ocr = run_ocr(img)
        redline_texts.append(ocr.full_text)

    # ── Step 3: Find text differences ─────────────────
    for page_idx, (ct, rt) in enumerate(zip(clean_texts, redline_texts), 1):
        clean_words = set(_normalize_words(ct))
        redline_words = set(_normalize_words(rt))

        added = redline_words - clean_words
        removed = clean_words - redline_words

        for word in added:
            if len(word) >= 3:  # skip tiny fragments
                result.sample_changes.append(TextDiff(
                    text=word, change_type="added", page=page_idx
                ))

        for word in removed:
            if len(word) >= 3:
                result.sample_changes.append(TextDiff(
                    text=word, change_type="removed", page=page_idx
                ))

    # Handle extra pages in redline (added pages)
    for page_idx in range(len(clean_texts) + 1, len(redline_texts) + 1):
        rt = redline_texts[page_idx - 1]
        for word in _normalize_words(rt):
            if len(word) >= 3:
                result.sample_changes.append(TextDiff(
                    text=word, change_type="added", page=page_idx
                ))

    logger.info("  Found %d text changes in sample redline", len(result.sample_changes))

    # ── Step 4: Compare with our findings ─────────────
    if our_report_json and our_report_json.exists():
        import json
        report = json.loads(our_report_json.read_text())
        our_gaps = report.get("gaps", [])

        # Also check results for failed/partial items
        results_list = report.get("results", [])
        for mr in results_list:
            if mr.get("status") in ("FAIL", "PARTIAL"):
                our_gaps.append({
                    "rule_id": mr.get("rule_id", ""),
                    "description": mr.get("description", ""),
                    "evidence": mr.get("evidence", []),
                })

        # For each of our gaps, check if the sample redline addressed it
        sample_text_lower = " ".join(t.text.lower() for t in result.sample_changes)

        for gap in our_gaps:
            desc = gap.get("description", "").lower()
            keywords = [w for w in desc.split() if len(w) > 3]
            matching = sum(1 for kw in keywords if kw in sample_text_lower)
            if matching >= max(1, len(keywords) * 0.3):
                result.our_gaps_found.append(gap.get("description", ""))
            else:
                result.our_gaps_missed.append(gap.get("description", ""))

        result.overlap_count = len(result.our_gaps_found)
        total_our = len(result.our_gaps_found) + len(result.our_gaps_missed)
        total_sample = len(result.sample_changes)

        if total_our > 0:
            result.precision = result.overlap_count / total_our
        if total_sample > 0:
            result.recall = result.overlap_count / max(total_sample, 1)

    # ── Step 5: Visual similarity (SSIM) ──────────────
    try:
        import cv2
        from skimage.metrics import structural_similarity as ssim

        for ci, ri in zip(clean_images, redline_images):
            c_img = cv2.imread(str(ci), cv2.IMREAD_GRAYSCALE)
            r_img = cv2.imread(str(ri), cv2.IMREAD_GRAYSCALE)

            if c_img is not None and r_img is not None:
                # Resize to same dimensions
                h = min(c_img.shape[0], r_img.shape[0])
                w = min(c_img.shape[1], r_img.shape[1])
                c_img = cv2.resize(c_img, (w, h))
                r_img = cv2.resize(r_img, (w, h))

                score, _ = ssim(c_img, r_img, full=True)
                result.page_similarities.append(score)

        if result.page_similarities:
            result.avg_similarity = sum(result.page_similarities) / len(result.page_similarities)

    except ImportError:
        logger.debug("skimage not available for SSIM")

    return result


def _normalize_words(text: str) -> list[str]:
    """Split text into normalized words for comparison."""
    # Remove common OCR noise, normalize
    text = re.sub(r"[^\w\s]", " ", text.lower())
    return [w.strip() for w in text.split() if w.strip()]


def format_validation_report(results: list[ValidationResult]) -> str:
    """Format validation results as Markdown."""
    lines = ["# Validation Report: Our Output vs Sample Redlines", ""]
    lines.append(f"**Labels validated:** {len(results)}")
    lines.append("")

    for r in results:
        lines.append(f"## {r.label_name}")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Sample redline changes | {len(r.sample_changes)} |")
        lines.append(f"| Our gaps found in sample | {r.overlap_count} |")
        lines.append(f"| Our gaps not in sample | {len(r.our_gaps_missed)} |")
        lines.append(f"| Precision | {r.precision:.0%} |")
        lines.append(f"| Recall | {r.recall:.0%} |")
        lines.append(f"| Visual similarity (avg) | {r.avg_similarity:.1%} |")
        lines.append("")

        if r.page_similarities:
            lines.append("### Page-by-Page Visual Similarity")
            lines.append("")
            for i, sim in enumerate(r.page_similarities, 1):
                bar = "█" * int(sim * 20) + "░" * (20 - int(sim * 20))
                lines.append(f"- Page {i}: {bar} {sim:.1%}")
            lines.append("")

        if r.sample_changes:
            added = [c for c in r.sample_changes if c.change_type == "added"]
            removed = [c for c in r.sample_changes if c.change_type == "removed"]
            if added:
                lines.append(f"### Text Added in Sample Redline ({len(added)} items)")
                lines.append("")
                for c in added[:30]:  # limit output
                    lines.append(f"- [Page {c.page}] + {c.text}")
                if len(added) > 30:
                    lines.append(f"- ... and {len(added) - 30} more")
                lines.append("")

            if removed:
                lines.append(f"### Text Removed in Sample Redline ({len(removed)} items)")
                lines.append("")
                for c in removed[:20]:
                    lines.append(f"- [Page {c.page}] - {c.text}")
                if len(removed) > 20:
                    lines.append(f"- ... and {len(removed) - 20} more")
                lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)
