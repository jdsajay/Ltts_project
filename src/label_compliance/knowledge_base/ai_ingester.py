"""
AI-Powered ISO Standard Ingester
==================================
Uses GPT-4o vision to read ISO standard PDF pages (including figures,
tables, and diagrams) and produces a rich, structured knowledge base.

Unlike the regex-based ingester that only extracts text, this module:
 - Renders each page as an image and sends it to GPT-4o vision
 - Captures table content (e.g., Table G.2 surface classification)
 - Understands figure diagrams and annexes
 - Extracts precise "shall" requirements with full context
 - Groups related pages into batched calls for efficiency
"""

from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

import fitz  # PyMuPDF

from label_compliance.config import get_settings
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

# ── Page groups for efficient batched reading ──────
# Focus on label-relevant sections rather than all 62 pages
# Each group: (name, page_range_0_indexed, context_description)
_PAGE_GROUPS = [
    ("scope_and_definitions", (6, 11), "Scope, normative references, and definitions"),
    ("design_and_materials", (11, 17), "Design evaluation, materials, testing"),
    ("labelling_requirements", (17, 21), "Section 11 — ALL labelling requirements"),
    ("annex_g_surface_classification", (45, 52), "Annex G — Surface classification (Table G.2)"),
    ("annex_h_ifu_information", (52, 58), "Annex H — Information for instructions for use"),
    ("annex_i_patient_info", (58, 61), "Annex I — Patient information brochure content"),
]

# Sections most relevant to label compliance redline review
_LABEL_SECTIONS = {"labelling_requirements", "annex_g_surface_classification"}


def _get_ai_client_and_model():
    """Get an authenticated API client and ingestion model name from config."""
    from label_compliance.config import get_ai_client, get_settings
    client = get_ai_client()
    model = get_settings().ai.ingestion_model
    return client, model


def _render_pages_as_images(
    pdf_path: Path,
    start_page: int,
    end_page: int,
    dpi: int = 150,
) -> list[tuple[int, Path]]:
    """Render a range of PDF pages as PNG images.

    Returns list of (page_number_1based, image_path) tuples.
    """
    doc = fitz.open(str(pdf_path))
    scale = dpi / 72.0
    mat = fitz.Matrix(scale, scale)
    results = []

    for i in range(start_page, min(end_page, len(doc))):
        page = doc[i]
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_path = Path(f"/tmp/iso_page_{i+1}.png")
        pix.save(str(img_path))
        results.append((i + 1, img_path))

    doc.close()
    return results


def _extract_page_text(pdf_path: Path, start_page: int, end_page: int) -> dict[int, str]:
    """Extract raw text per page for supplementary context."""
    doc = fitz.open(str(pdf_path))
    texts = {}
    for i in range(start_page, min(end_page, len(doc))):
        texts[i + 1] = doc[i].get_text()
    doc.close()
    return texts


def _call_gpt4o_for_pages(
    page_images: list[tuple[int, Path]],
    page_texts: dict[int, str],
    group_name: str,
    context: str,
) -> str:
    """Send page images + text to AI vision model for structured extraction.

    Sends up to 4 pages per call to stay within token limits.
    """
    client, model = _get_ai_client_and_model()

    # Build content parts: prompt + page images
    text_context = ""
    for page_num, text in sorted(page_texts.items()):
        clean = text.strip()[:2000]  # limit text per page
        if clean:
            text_context += f"\n--- Page {page_num} text ---\n{clean}\n"

    prompt = f"""You are reading an ISO 14607:2024 standard PDF. This section is: {context}

I am providing page images AND extracted text. The images may contain FIGURES, TABLES, DIAGRAMS,
and FORMATTED CONTENT that is NOT in the text extraction.

EXTRACT ALL of the following from these pages:

1. **SECTIONS**: Every numbered section/clause with its full text content.
2. **REQUIREMENTS**: Every "shall" statement — these are mandatory requirements. Include full sentence with context.
3. **TABLES**: Extract ALL table data as structured content. For each table:
   - Table number (e.g., "Table G.2")
   - Column headers
   - All row data
   - Any notes below the table
4. **FIGURES**: Describe what each figure shows, including labels, dimensions, and key visual information.
5. **DEFINITIONS**: Any defined terms with their definitions.
6. **REFERENCES**: Cross-references to other ISO standards or sections.

SUPPLEMENTARY TEXT FROM PDF:
{text_context}

OUTPUT FORMAT — respond with JSON:
{{
  "group": "{group_name}",
  "sections": [
    {{
      "number": "11.3",
      "title": "Label",
      "full_text": "Complete text of the section including all sub-items a) b) c) etc.",
      "requirements": [
        {{
          "text": "The exact shall statement with full context",
          "type": "shall",
          "applies_to": "label|ifu|patient_card|implant|manufacturer"
        }}
      ],
      "sub_items": ["a) item text", "b) item text"],
      "references": ["ISO 14630:2024, 11.3", "Table G.2"]
    }}
  ],
  "tables": [
    {{
      "table_id": "Table G.2",
      "title": "Surface classification codes",
      "columns": ["Column1", "Column2", ...],
      "rows": [
        ["cell1", "cell2", ...],
        ...
      ],
      "notes": "Any footnotes or notes"
    }}
  ],
  "figures": [
    {{
      "figure_id": "Figure G.1",
      "title": "Figure title",
      "description": "What the figure shows, including all labeled parts, dimensions, measurement details"
    }}
  ],
  "definitions": [
    {{
      "term": "term name",
      "definition": "its definition"
    }}
  ]
}}

Be thorough — extract EVERYTHING visible. Tables and figures are especially important
since they contain information that text extraction alone misses.
"""

    content_parts: list[dict] = [{"type": "text", "text": prompt}]

    for page_num, img_path in page_images:
        img_data = img_path.read_bytes()
        b64 = base64.b64encode(img_data).decode("utf-8")
        content_parts.append({
            "type": "text",
            "text": f"--- ISO 14607:2024, Page {page_num} ---",
        })
        content_parts.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64}",
                "detail": "high",
            },
        })

    logger.info("Sending %d page images to %s for group '%s'...", len(page_images), model, group_name)
    t0 = time.time()

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise ISO standards document reader. "
                    "Extract all content including tables, figures, and requirements. "
                    "Pay special attention to tables and visual content that text extraction misses. "
                    "Always respond with valid JSON."
                ),
            },
            {
                "role": "user",
                "content": content_parts,
            },
        ],
        temperature=0.1,
        max_tokens=4096,
    )

    elapsed = time.time() - t0
    usage = response.usage
    if usage:
        logger.info(
            "  GPT-4o took %.1fs — %d tokens (prompt=%d, completion=%d)",
            elapsed, usage.total_tokens, usage.prompt_tokens, usage.completion_tokens,
        )

    return response.choices[0].message.content


def ingest_iso_with_ai(
    pdf_path: Path,
    page_groups: list[tuple[str, tuple[int, int], str]] | None = None,
    output_path: Path | None = None,
    max_pages_per_call: int = 4,
) -> dict:
    """
    AI-powered ingestion of an ISO standard PDF.

    Renders pages as images, sends to GPT-4o vision for structured extraction.
    Produces a rich knowledge base with tables, figures, and precise requirements.

    Args:
        pdf_path: Path to the ISO standard PDF
        page_groups: Optional override of page groups to process
        output_path: Where to save the output JSON (default: knowledge_base dir)
        max_pages_per_call: Max pages per GPT-4o call (to stay in token limits)

    Returns:
        The structured knowledge base dict
    """
    settings = get_settings()
    groups = page_groups or _PAGE_GROUPS

    if output_path is None:
        stem = pdf_path.stem.replace(" ", "-")
        output_path = settings.paths.knowledge_base_dir / f"{stem}-ai.json"

    logger.info("AI ingestion of %s (%d page groups)", pdf_path.name, len(groups))

    all_sections = []
    all_tables = []
    all_figures = []
    all_definitions = []
    all_requirements = []
    total_tokens = 0
    total_time = 0.0

    for group_name, (start, end), context in groups:
        logger.info("Processing group '%s' (pages %d-%d)...", group_name, start + 1, end)

        # Render pages as images
        page_images = _render_pages_as_images(pdf_path, start, end)
        page_texts = _extract_page_text(pdf_path, start, end)

        # Process in batches if too many pages
        for batch_start in range(0, len(page_images), max_pages_per_call):
            batch = page_images[batch_start:batch_start + max_pages_per_call]
            batch_page_nums = [p for p, _ in batch]
            batch_texts = {k: v for k, v in page_texts.items() if k in batch_page_nums}

            try:
                t0 = time.time()
                response_text = _call_gpt4o_for_pages(
                    batch, batch_texts, group_name, context,
                )
                batch_time = time.time() - t0
                total_time += batch_time

                data = json.loads(response_text)

                # Merge extracted data
                for sec in data.get("sections", []):
                    sec["source_group"] = group_name
                    sec["source_pages"] = batch_page_nums
                    all_sections.append(sec)

                    # Also aggregate requirements
                    for req in sec.get("requirements", []):
                        req["section"] = sec.get("number", "")
                        req["section_title"] = sec.get("title", "")
                        all_requirements.append(req)

                for tbl in data.get("tables", []):
                    tbl["source_group"] = group_name
                    tbl["source_pages"] = batch_page_nums
                    all_tables.append(tbl)

                for fig in data.get("figures", []):
                    fig["source_group"] = group_name
                    fig["source_pages"] = batch_page_nums
                    all_figures.append(fig)

                for defn in data.get("definitions", []):
                    all_definitions.append(defn)

                logger.info(
                    "  Batch pages %s: %d sections, %d tables, %d figures",
                    batch_page_nums,
                    len(data.get("sections", [])),
                    len(data.get("tables", [])),
                    len(data.get("figures", [])),
                )

            except Exception as e:
                logger.error(
                    "  Failed to process batch pages %s: %s",
                    batch_page_nums, e,
                )

            # Clean up temp images
            for _, img_path in batch:
                img_path.unlink(missing_ok=True)

    # Build final knowledge base
    kb = {
        "iso_id": pdf_path.stem,
        "source_file": pdf_path.name,
        "ingestion_method": "ai_vision",
        "ingestion_model": "gpt-4o",
        "ingested_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_time_seconds": round(total_time, 1),
        "total_sections": len(all_sections),
        "total_requirements": len(all_requirements),
        "total_tables": len(all_tables),
        "total_figures": len(all_figures),
        "total_definitions": len(all_definitions),
        "sections": all_sections,
        "tables": all_tables,
        "figures": all_figures,
        "definitions": all_definitions,
        "requirements": all_requirements,
    }

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(kb, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(
        "AI-ingested KB saved: %d sections, %d reqs, %d tables, %d figures → %s",
        len(all_sections), len(all_requirements), len(all_tables),
        len(all_figures), output_path.name,
    )

    return kb


def get_ai_iso_knowledge(iso_id: str = "ISO-14607-2024") -> dict | None:
    """Load the AI-ingested ISO knowledge base if available.

    Returns None if the AI-ingested version doesn't exist yet.
    """
    settings = get_settings()
    ai_path = settings.paths.knowledge_base_dir / f"{iso_id}-ai.json"
    if ai_path.exists():
        return json.loads(ai_path.read_text(encoding="utf-8"))
    return None


def get_labelling_requirements_text(kb: dict) -> str:
    """Extract labelling requirements (Section 11) as formatted text for prompts.

    Returns a concise but complete text block of all labelling requirements,
    including table content and figure descriptions, suitable for inclusion
    in GPT-4o prompts.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("ISO 14607:2024 — LABELLING REQUIREMENTS (AI-extracted from PDF)")
    lines.append("=" * 60)

    # Section content
    for sec in kb.get("sections", []):
        group = sec.get("source_group", "")
        if group not in ("labelling_requirements", "annex_g_surface_classification"):
            continue

        num = sec.get("number", "")
        title = sec.get("title", "")
        full_text = sec.get("full_text", "")

        lines.append(f"\n§{num} {title}")
        lines.append("-" * 40)

        if full_text:
            lines.append(full_text)

        # Sub-items
        for item in sec.get("sub_items", []):
            lines.append(f"  {item}")

        # Requirements
        for req in sec.get("requirements", []):
            lines.append(f"  ▸ REQUIREMENT: {req.get('text', '')}")

    # Tables (especially Table G.2)
    for tbl in kb.get("tables", []):
        group = tbl.get("source_group", "")
        if group not in ("labelling_requirements", "annex_g_surface_classification"):
            continue

        tbl_id = tbl.get("table_id", "Table")
        title = tbl.get("title", "")
        lines.append(f"\n📊 {tbl_id}: {title}")
        lines.append("-" * 40)

        cols = tbl.get("columns", [])
        if cols:
            lines.append("  | " + " | ".join(str(c) for c in cols) + " |")
            lines.append("  |" + "|".join(["---"] * len(cols)) + "|")

        for row in tbl.get("rows", []):
            lines.append("  | " + " | ".join(str(c) for c in row) + " |")

        notes = tbl.get("notes", "")
        if notes:
            lines.append(f"  Note: {notes}")

    # Figures
    for fig in kb.get("figures", []):
        group = fig.get("source_group", "")
        if group not in ("labelling_requirements", "annex_g_surface_classification"):
            continue

        fig_id = fig.get("figure_id", "Figure")
        desc = fig.get("description", "")
        lines.append(f"\n🔍 {fig_id}: {desc}")

    text = "\n".join(lines)
    return text


def ingest_all_with_ai() -> list[dict]:
    """Ingest all ISO PDFs in the standards directory using AI vision."""
    settings = get_settings()
    pdf_files = sorted(settings.paths.standards_dir.glob("*.pdf"))

    if not pdf_files:
        logger.warning("No PDF files found in %s", settings.paths.standards_dir)
        return []

    results = []
    for pdf_path in pdf_files:
        try:
            kb = ingest_iso_with_ai(pdf_path)
            results.append(kb)
        except Exception as e:
            logger.error("Failed to ingest %s: %s", pdf_path.name, e, exc_info=True)

    return results
