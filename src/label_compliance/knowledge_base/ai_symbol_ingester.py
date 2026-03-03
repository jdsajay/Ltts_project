"""
AI-Powered Symbol Library Ingester
=====================================
Uses GPT-4o vision to analyze the company Symbol Library Excel file
and produce an enriched, AI-annotated symbol database.

Unlike the basic openpyxl extraction (scripts/extract_symbol_library.py)
that only reads column values, this module:
 - Sends symbol thumbnail images to GPT-4o for visual analysis
 - Identifies the ISO standard each symbol corresponds to
 - Generates detailed visual descriptions of each symbol
 - Determines which product types require each symbol
 - Maps symbols to specific regulatory requirements
 - Detects design version differences (current vs outdated)
"""

from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

from label_compliance.config import get_settings
from label_compliance.utils.log import get_logger

logger = get_logger(__name__)

_AI_SYMBOL_DB_FILENAME = "symbol_library_ai.json"

# Batch size — how many symbols to send to GPT-4o per call
# Each symbol has a thumbnail image so we keep batches small
_BATCH_SIZE = 15


def _get_api_key() -> str:
    """Get API key from the configured env var."""
    from label_compliance.config import get_settings
    settings = get_settings()
    env_var = settings.ai.api_key_env_var or "OPENAI_API_KEY"
    api_key = os.getenv(env_var)
    if not api_key:
        raise ValueError(f"{env_var} not set")
    return api_key


def _encode_image(image_path: Path) -> str:
    """Base64-encode an image file."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _detect_mime(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
    }.get(suffix, "image/png")


def _load_base_library() -> dict:
    """Load the existing (basic-extracted) symbol library JSON."""
    settings = get_settings()
    db_path = settings.paths.symbol_library_dir / "symbol_library.json"
    if not db_path.exists():
        raise FileNotFoundError(
            f"Base symbol library not found at {db_path}. "
            "Run `python scripts/extract_symbol_library.py` first."
        )
    with open(db_path) as f:
        return json.load(f)


def _build_symbol_batch_prompt(symbols_meta: list[dict]) -> str:
    """Build a GPT-4o prompt for a batch of symbols with their metadata."""
    lines = [
        "You are an expert in medical device regulatory symbols and ISO standards.",
        "",
        "I am showing you a batch of symbols from a company Symbol Library Excel file.",
        "For EACH symbol, I provide:",
        "  - The thumbnail image (attached)",
        "  - Metadata: name, classification, package text, regulations, status",
        "",
        "For EACH symbol, analyze the image and provide:",
        "",
        "1. **visual_description**: Describe what the symbol looks like in detail",
        "   (shape, colors, lines, arrows, text within the symbol, enclosure type).",
        "2. **iso_standard**: The ISO standard this symbol comes from (e.g., ISO 7000-3082,",
        "   ISO 15223-1:2021 clause 5.1.1). If it's proprietary, say 'Proprietary'.",
        "3. **purpose**: What does this symbol communicate to the user?",
        "4. **required_for**: List of product categories requiring this symbol",
        "   (e.g., ['all medical devices', 'sterile devices', 'implants', 'IVDs']).",
        "5. **min_height_mm**: Minimum symbol height in mm per the applicable standard",
        "   (3mm for most ISO 15223 symbols, 5mm for CE marks, 0 if unknown).",
        "6. **placement_requirement**: Where on the label this symbol must appear",
        "   (e.g., 'adjacent to manufacturer name', 'near lot number field').",
        "7. **current_version_notes**: Any notes about the current version design.",
        "   If the symbol was updated in a recent ISO revision, note what changed.",
        "",
        "=== SYMBOLS TO ANALYZE ===",
        "",
    ]

    for idx, sym in enumerate(symbols_meta):
        lines.append(f"SYMBOL {idx + 1} (Row {sym['row']}):")
        lines.append(f"  Name: {sym['name']}")
        lines.append(f"  Classification: {sym['classification']}")
        lines.append(f"  Status: {sym['status']}")
        lines.append(f"  Package Text: {sym['pkg_text']}")
        lines.append(f"  IFU Text: {sym['ifu_text']}")
        lines.append(f"  Regulations: {sym['regulations']}")
        lines.append(f"  Notes: {sym.get('notes', '')}")
        lines.append("")

    lines.append("=== OUTPUT FORMAT ===")
    lines.append("")
    lines.append("Respond with JSON:")
    lines.append("{")
    lines.append('  "symbols": [')
    lines.append("    {")
    lines.append('      "row": 5,')
    lines.append('      "visual_description": "...",')
    lines.append('      "iso_standard": "ISO 7000-3082 / ISO 15223-1:2021, 5.1.1",')
    lines.append('      "purpose": "Identifies the medical device manufacturer",')
    lines.append('      "required_for": ["all medical devices"],')
    lines.append('      "min_height_mm": 3,')
    lines.append('      "placement_requirement": "Adjacent to manufacturer name and address",')
    lines.append('      "current_version_notes": "Updated in ISO 15223-1:2021"')
    lines.append("    }")
    lines.append("  ]")
    lines.append("}")

    return "\n".join(lines)


def _call_gpt4o_batch(
    prompt: str,
    image_paths: list[Path],
) -> str | None:
    """Call AI vision model with symbol thumbnail images."""
    from label_compliance.config import get_ai_client, get_settings

    client = get_ai_client()
    model = get_settings().ai.ingestion_model

    content_parts: list[dict] = [{"type": "text", "text": prompt}]

    # Add each symbol thumbnail as an image
    for img_path in image_paths:
        if img_path and img_path.exists():
            b64 = _encode_image(img_path)
            mime = _detect_mime(img_path)
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime};base64,{b64}",
                    "detail": "low",  # thumbnails are small
                },
            })

    t0 = time.time()
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert in medical device regulatory labelling symbols, "
                    "ISO 15223-1, ISO 7000, IEC 60417, and EU MDR requirements. "
                    "You analyze symbol images and classify them accurately. "
                    "Always respond with valid JSON."
                ),
            },
            {"role": "user", "content": content_parts},
        ],
        temperature=0.1,
        max_tokens=4096,
    )

    elapsed = time.time() - t0
    usage = response.usage
    if usage:
        logger.info(
            "GPT-4o symbol batch took %.1fs — %d tokens (prompt=%d, completion=%d)",
            elapsed, usage.total_tokens, usage.prompt_tokens, usage.completion_tokens,
        )

    content = response.choices[0].message.content
    if not content:
        logger.warning("GPT-4o returned empty response for symbol batch")
        return None
    return content


def ingest_symbol_library_with_ai(
    excel_path: Path | None = None,
    force: bool = False,
) -> dict:
    """
    AI-powered ingestion of the symbol library.

    Steps:
    1. Load the base extracted JSON (from scripts/extract_symbol_library.py)
    2. For each batch of symbols that have thumbnail images:
       a. Send the thumbnails + metadata to GPT-4o
       b. GPT-4o returns visual descriptions, ISO mappings, requirements
    3. Merge AI annotations into the symbol data
    4. Save enriched database as symbol_library_ai.json

    Returns the enriched symbol data dict.
    """
    settings = get_settings()
    output_path = settings.paths.symbol_library_dir / _AI_SYMBOL_DB_FILENAME
    images_dir = settings.paths.symbol_library_dir / "images"

    # Check if already exists (unless force)
    if output_path.exists() and not force:
        logger.info("AI symbol library already exists at %s (use force=True to re-ingest)", output_path)
        with open(output_path) as f:
            return json.load(f)

    # Load base library
    base_data = _load_base_library()
    symbols = base_data.get("symbols", [])
    logger.info("Loaded base symbol library: %d symbols", len(symbols))

    # Filter to active symbols with thumbnails
    symbols_with_images = []
    for sym in symbols:
        if sym.get("status") != "Active":
            continue
        # Find best thumbnail
        thumb_path = None
        for fname in sym.get("std_thumb_images", []) + sym.get("thumb_images", []):
            p = images_dir / fname
            if p.exists():
                thumb_path = p
                break
        if thumb_path:
            sym["_thumb_path"] = str(thumb_path)
            symbols_with_images.append(sym)

    logger.info("Active symbols with thumbnails: %d / %d", len(symbols_with_images), len(symbols))

    # Process in batches
    ai_annotations: dict[int, dict] = {}  # row -> AI data
    total_batches = (len(symbols_with_images) + _BATCH_SIZE - 1) // _BATCH_SIZE

    for batch_idx in range(total_batches):
        start = batch_idx * _BATCH_SIZE
        end = min(start + _BATCH_SIZE, len(symbols_with_images))
        batch = symbols_with_images[start:end]

        logger.info(
            "Processing batch %d/%d (symbols %d–%d)...",
            batch_idx + 1, total_batches, start + 1, end,
        )

        # Build prompt
        prompt = _build_symbol_batch_prompt(batch)

        # Collect thumbnail paths
        thumb_paths = [Path(s["_thumb_path"]) for s in batch]

        # Call GPT-4o
        try:
            response_text = _call_gpt4o_batch(prompt, thumb_paths)
            if not response_text:
                logger.warning("Empty response for batch %d", batch_idx + 1)
                continue

            batch_data = json.loads(response_text)
            for ai_sym in batch_data.get("symbols", []):
                row = ai_sym.get("row")
                if row:
                    ai_annotations[row] = ai_sym

            logger.info(
                "Batch %d: got AI annotations for %d symbols",
                batch_idx + 1, len(batch_data.get("symbols", [])),
            )

        except Exception as e:
            logger.error("Error processing batch %d: %s", batch_idx + 1, e)
            continue

        # Brief pause between batches to avoid rate limits
        if batch_idx < total_batches - 1:
            time.sleep(1)

    # Merge AI annotations into base data
    enriched_symbols = []
    for sym in symbols:
        row = sym.get("row")
        ai_data = ai_annotations.get(row, {})
        enriched = {
            **sym,
            "ai_visual_description": ai_data.get("visual_description", ""),
            "ai_iso_standard": ai_data.get("iso_standard", ""),
            "ai_purpose": ai_data.get("purpose", ""),
            "ai_required_for": ai_data.get("required_for", []),
            "ai_min_height_mm": ai_data.get("min_height_mm", 0),
            "ai_placement_requirement": ai_data.get("placement_requirement", ""),
            "ai_current_version_notes": ai_data.get("current_version_notes", ""),
        }
        # Remove temp field
        enriched.pop("_thumb_path", None)
        enriched_symbols.append(enriched)

    annotated_count = sum(1 for s in enriched_symbols if s.get("ai_visual_description"))
    logger.info(
        "AI annotation complete: %d / %d symbols enriched",
        annotated_count, len(enriched_symbols),
    )

    # Build output
    output = {
        "source": base_data.get("source", ""),
        "ai_ingested_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "ai_model": "gpt-4o",
        "total_symbols": len(enriched_symbols),
        "ai_annotated_symbols": annotated_count,
        "total_images": base_data.get("total_images", 0),
        "symbols": enriched_symbols,
    }

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    logger.info("AI-enriched symbol library saved: %s", output_path)

    return output


def get_ai_symbol_library() -> dict | None:
    """Load the AI-enriched symbol library if it exists."""
    settings = get_settings()
    path = settings.paths.symbol_library_dir / _AI_SYMBOL_DB_FILENAME
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def get_ai_symbol_reference_text(ai_db: dict) -> str:
    """
    Build a rich text description of required symbols for the AI redline prompt,
    using the AI-enriched annotations (visual descriptions, ISO mappings, etc.).
    """
    lines = [
        "\n=== AI-ENRICHED SYMBOL LIBRARY REFERENCE ===",
        "Each symbol below has been analyzed by AI with visual descriptions,",
        "ISO standard mappings, and placement requirements.\n",
    ]

    symbols = ai_db.get("symbols", [])

    # Focus on standard/active symbols that have AI annotations
    relevant = [
        s for s in symbols
        if s.get("status") == "Active"
        and s.get("ai_visual_description")
        and s.get("classification") in ("Standard", "Pictogram", "Regulatory")
    ]

    # Sort by classification, then by ISO reference
    relevant.sort(key=lambda s: (s.get("ai_iso_standard", ""), s.get("name", "")))

    for sym in relevant:
        lines.append(f"SYMBOL: {sym['name']} (Row {sym['row']})")
        lines.append(f"  Classification: {sym['classification']}")
        lines.append(f"  Package Text: {sym['pkg_text']}")
        if sym.get("ai_iso_standard"):
            lines.append(f"  ISO Standard: {sym['ai_iso_standard']}")
        if sym.get("ai_visual_description"):
            lines.append(f"  Visual Description: {sym['ai_visual_description']}")
        if sym.get("ai_purpose"):
            lines.append(f"  Purpose: {sym['ai_purpose']}")
        if sym.get("ai_required_for"):
            lines.append(f"  Required For: {', '.join(sym['ai_required_for'])}")
        if sym.get("ai_min_height_mm"):
            lines.append(f"  Minimum Height: {sym['ai_min_height_mm']}mm")
        if sym.get("ai_placement_requirement"):
            lines.append(f"  Placement: {sym['ai_placement_requirement']}")
        if sym.get("ai_current_version_notes"):
            lines.append(f"  Version Notes: {sym['ai_current_version_notes']}")
        lines.append("")

    lines.append(f"Total AI-annotated symbols: {len(relevant)}")
    lines.append("Compare each symbol on the label against these descriptions.\n")

    return "\n".join(lines)
