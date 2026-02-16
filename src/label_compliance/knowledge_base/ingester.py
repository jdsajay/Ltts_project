"""
ISO Standard PDF Ingester
==========================
Reads an ISO standard PDF, extracts every section/clause line-by-line,
parses "shall" requirements, tables, measurement specs, and symbol
references into a structured format for the knowledge base.

Handles multiple standards (ISO 14607, ISO 15223, ISO 14630, EU MDR, etc.).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber

from label_compliance.config import get_settings
from label_compliance.utils.helpers import safe_filename
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

# ── Regex patterns ────────────────────────────────────
SECTION_RE = re.compile(
    r"^(?P<number>(?:\d+|[A-Z])(?:\.\d+){0,5})\s+(?P<title>[A-Z][A-Za-z].{2,120})$"
)
SHALL_RE = re.compile(r"[^.]*\bshall\b[^.]*\.", re.IGNORECASE)
ITEM_RE = re.compile(r"^[a-z]\)\s+", re.MULTILINE)
MEASUREMENT_RE = re.compile(
    r"\b\d+\.?\d*\s*(?:µm|μm|mm|cm|m|cc|mL|ml|kPa|MPa|°C|kg|g|%)\b"
)
TABLE_REF_RE = re.compile(r"\bTable\s+[A-Z]?\d+(?:\.\d+)?\b", re.IGNORECASE)
FIGURE_REF_RE = re.compile(r"\bFigure\s+[A-Z]?\d+(?:\.\d+)?\b", re.IGNORECASE)
STANDARD_REF_RE = re.compile(r"\bISO\s+\d{4,5}(?:[-:]\d{1,4})?\b")
SYMBOL_REF_RE = re.compile(r"\bISO\s+7000[-–]\d+\b")

# Noise lines to skip
NOISE_PATTERNS = [
    re.compile(r"^---\s*Page\s+\d+", re.IGNORECASE),
    re.compile(r"^©\s*ISO", re.IGNORECASE),
    re.compile(r"^\s*No\s+further\s+reproduction", re.IGNORECASE),
    re.compile(r"^\s*Distributed\s+by\s+Accuris", re.IGNORECASE),
    re.compile(r"^\s*Copyrighted\s+material", re.IGNORECASE),
    re.compile(r"^\s*www\.store\.accuristech", re.IGNORECASE),
    re.compile(r"^\s*licensed\s+to\s+Accounts", re.IGNORECASE),
    re.compile(r"^\s*Payable$", re.IGNORECASE),
    re.compile(r"^\[Table \d+\]$"),
]


def _is_noise(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) <= 2:
        return True
    return any(p.match(stripped) for p in NOISE_PATTERNS)


def _extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract full text from a PDF, page by page."""
    lines: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            lines.append(f"--- Page {i} ---")
            lines.append(text)

            # Also extract tables
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row:
                        cells = [str(c).strip() if c else "" for c in row]
                        lines.append("  |  ".join(cells))
    return "\n".join(lines)


def _clean_text(raw: str) -> str:
    """Remove noise lines, keep meaningful content."""
    return "\n".join(
        line for line in raw.splitlines() if not _is_noise(line)
    )


def _parse_sections(text: str) -> list[dict]:
    """Parse text into hierarchical sections."""
    lines = text.splitlines()
    sections: list[dict] = []
    current: dict | None = None
    body_lines: list[str] = []

    def flush():
        nonlocal current, body_lines
        if current is not None:
            body = "\n".join(body_lines).strip()
            current["body"] = body
            current["requirements"] = _extract_requirements(body)
            current["measurements"] = _extract_measurements(body)
            current["table_refs"] = _extract_table_refs(body)
            current["standard_refs"] = _extract_standard_refs(body)
            current["symbol_refs"] = _extract_symbol_refs(body)
            current["keywords"] = _extract_keywords(body)
            sections.append(current)
        body_lines = []

    for line in lines:
        m = SECTION_RE.match(line.strip())
        if m:
            flush()
            num = m.group("number")
            parts = num.split(".")
            current = {
                "number": num,
                "title": m.group("title").strip(),
                "depth": len(parts),
                "parent": ".".join(parts[:-1]) if len(parts) > 1 else None,
                "body": "",
                "requirements": [],
                "measurements": [],
                "table_refs": [],
                "standard_refs": [],
                "symbol_refs": [],
                "keywords": [],
            }
        else:
            body_lines.append(line)

    flush()
    return sections


def _extract_requirements(body: str) -> list[dict]:
    """Extract 'shall' statements and lettered sub-items."""
    reqs = []
    seen = set()

    for m in SHALL_RE.finditer(body):
        text = re.sub(r"\s+", " ", m.group(0).strip())
        if len(text) > 20 and text not in seen:
            seen.add(text)
            reqs.append({"type": "shall", "text": text})

    for block in re.split(r"(?=^[a-z]\)\s+)", body, flags=re.MULTILINE):
        block = block.strip()
        if ITEM_RE.match(block):
            text = re.sub(r"\s+", " ", block)
            if len(text) > 10 and text not in seen:
                seen.add(text)
                reqs.append({"type": "item", "text": text})

    return reqs


def _extract_measurements(body: str) -> list[str]:
    """Extract measurement values (e.g., '3 mm', '150 cc')."""
    return list({m.group(0).strip() for m in MEASUREMENT_RE.finditer(body)})


def _extract_table_refs(body: str) -> list[str]:
    return list({m.group(0) for m in TABLE_REF_RE.finditer(body)})


def _extract_standard_refs(body: str) -> list[str]:
    return list({m.group(0) for m in STANDARD_REF_RE.finditer(body)})


def _extract_symbol_refs(body: str) -> list[str]:
    return list({m.group(0) for m in SYMBOL_REF_RE.finditer(body)})


def _extract_keywords(body: str) -> list[str]:
    """Extract domain keywords for indexing."""
    kw_patterns = [
        r"\b\d+\s*(?:µm|mm|cm|cc|ml|kPa|MPa|°C|kg)\b",
        r"\bISO\s+\d{4,5}(?::\d{4})?\b",
        r"\b(?:UDI|GTIN|CE|MDR|IVDR|SRN|EUDAMED)\b",
        r"\b(?:steriliz|biocompat|implant|label|packaging|shelf life|expir)\w*\b",
        r"\b(?:manufacturer|patient|surgeon)\b",
        r"\b(?:NTX|SLC|SLO|CRC|CRO|GDD|GDS|PUI|MAI|PUL|OML|OTH)\b",
        r"\b(?:micro-textured|macro-textured|surface roughness|surface complexity)\b",
        r"\b(?:REF|LOT|SN|serial|batch|barcode|DataMatrix)\b",
    ]
    found = set()
    for pat in kw_patterns:
        for m in re.finditer(pat, body, re.IGNORECASE):
            found.add(m.group(0).strip())
    return sorted(found)


def ingest_standard(pdf_path: Path) -> dict:
    """
    Full ingestion pipeline for one ISO standard PDF.

    Returns the structured knowledge base dict and saves
    it to data/knowledge_base/<standard_id>.json.
    """
    settings = get_settings()
    iso_id = safe_filename(pdf_path.stem)
    logger.info("Ingesting standard: %s from %s", iso_id, pdf_path.name)

    # 1. Extract text
    raw_text = _extract_text_from_pdf(pdf_path)
    logger.info("  Extracted %d characters of text", len(raw_text))

    # 2. Save raw text
    text_path = settings.paths.knowledge_base_dir / f"{iso_id}.txt"
    text_path.write_text(raw_text, encoding="utf-8")

    # 3. Clean and parse
    cleaned = _clean_text(raw_text)
    sections = _parse_sections(cleaned)
    logger.info("  Parsed %d sections", len(sections))

    # 4. Aggregate statistics
    all_requirements = []
    all_keywords = set()
    all_measurements = set()
    all_table_refs = set()

    for sec in sections:
        all_keywords.update(sec["keywords"])
        all_measurements.update(sec["measurements"])
        all_table_refs.update(sec["table_refs"])
        for req in sec["requirements"]:
            all_requirements.append({
                "section": sec["number"],
                "section_title": sec["title"],
                **req,
            })

    kb = {
        "iso_id": iso_id,
        "source_file": pdf_path.name,
        "total_sections": len(sections),
        "total_requirements": len(all_requirements),
        "total_keywords": len(all_keywords),
        "total_measurements": len(all_measurements),
        "sections": sections,
        "requirements": all_requirements,
        "keyword_index": sorted(all_keywords),
        "measurement_index": sorted(all_measurements),
        "table_refs": sorted(all_table_refs),
    }

    # 5. Save JSON
    kb_path = settings.paths.knowledge_base_dir / f"{iso_id}.json"
    kb_path.write_text(json.dumps(kb, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(
        "  Saved KB: %d sections, %d requirements, %d keywords → %s",
        len(sections), len(all_requirements), len(all_keywords), kb_path.name,
    )

    return kb


def ingest_all_standards() -> list[dict]:
    """Ingest all PDFs in the standards directory."""
    settings = get_settings()
    pdf_files = sorted(settings.paths.standards_dir.glob("*.pdf"))

    if not pdf_files:
        logger.warning("No PDF files found in %s", settings.paths.standards_dir)
        return []

    results = []
    for pdf_path in pdf_files:
        try:
            kb = ingest_standard(pdf_path)
            results.append(kb)
        except Exception:
            logger.exception("Failed to ingest %s", pdf_path.name)

    return results
