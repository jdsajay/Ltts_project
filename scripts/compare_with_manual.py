"""
Compare manual redline (expected output) with our AI redline using AI vision.

Renders both PDFs as high-res images and sends them to the AI model
to extract and compare all visual annotations, symbols, and markings.
"""
import base64
import json
import os
import sys
from pathlib import Path

import fitz  # PyMuPDF
from openai import OpenAI

MANUAL_PDF = Path("data/labels/redlines/DRWG107621_Rev D_NATIVE.pdf")
AI_PDF = Path("outputs/redlines/redlined-DRWG107621_Rev_D_NATIVE_1.pdf")
OUTPUT_DIR = Path("outputs/debug_sections")

def render_pdf_pages(pdf_path: Path, prefix: str, dpi: int = 300) -> list[Path]:
    """Render each page of a PDF as a high-res PNG."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(pdf_path))
    pages = []
    scale = dpi / 72.0
    mat = fitz.Matrix(scale, scale)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out = OUTPUT_DIR / f"{prefix}_page{i+1}.png"
        pix.save(str(out))
        pages.append(out)
        print(f"  Rendered {out.name} ({pix.width}x{pix.height}px)")
    doc.close()
    return pages


def encode_image(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def analyze_manual_redline(manual_pages: list[Path], client: OpenAI) -> str:
    """Send manual redline pages to AI and extract every annotation."""
    content = [
        {
            "type": "text",
            "text": """You are analyzing a MANUAL REDLINE of a medical device label drawing (DRWG107621).

This PDF contains the EXPECTED/CORRECT redline output created by a human reviewer.
The reviewer has marked issues using red circles, arrows, callout boxes, strikethroughs, 
and text annotations on the label artwork.

Your task: Extract EVERY SINGLE redline annotation/marking from these pages.

For EACH marking you see, provide:
1. LOCATION: Which label panel (Combo Label, Outer Lid, Patient Record, etc.) and where exactly
2. WHAT IS MARKED: What symbol, text, or element has a redline marking on it
3. WHAT THE ANNOTATION SAYS: The callout text, comment, or correction indicated
4. TYPE OF ISSUE: Is it a symbol replacement, text change, addition, removal, size change, etc.

Be EXHAUSTIVE — capture every red marking, every callout, every strikethrough, every arrow.
Look at EVERY part of the image carefully — symbols, text blocks, barcodes, everything.

Output as a numbered list. Do NOT skip any marking.""",
        },
    ]

    for page_path in manual_pages:
        b64 = encode_image(page_path)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "high"},
        })

    print("\n  Sending manual redline to AI for analysis...")
    response = client.chat.completions.create(
        model="o3",
        messages=[
            {"role": "developer", "content": "You are an expert at reading redline markups on engineering drawings. Extract every single annotation meticulously."},
            {"role": "user", "content": content},
        ],
        max_completion_tokens=16000,
        reasoning_effort="high",
    )

    result = response.choices[0].message.content
    usage = response.usage
    if usage:
        print(f"  Tokens: {usage.total_tokens} (prompt={usage.prompt_tokens}, completion={usage.completion_tokens})")
    return result


def compare_redlines(manual_analysis: str, ai_pages: list[Path], client: OpenAI) -> str:
    """Send our AI redline + the manual analysis to compare."""
    content = [
        {
            "type": "text",
            "text": f"""You are comparing TWO redline reviews of the same medical device label (DRWG107621).

=== MANUAL REDLINE (EXPECTED/CORRECT — done by human reviewer) ===
{manual_analysis}

=== OUR AI REDLINE (attached images — what our system produced) ===
The attached images show our AI-generated redline output.

YOUR TASK:
1. Read our AI redline annotations from the attached images
2. Compare EVERY issue from the manual redline against our AI output
3. Create a detailed comparison table

For EACH issue in the manual redline:
- ✅ MATCH: Our AI found the same issue (even if wording differs)
- ❌ MISSED: Our AI did NOT detect this issue
- ⚠️ PARTIAL: Our AI found something similar but not exactly right

Also note:
- 🆕 FALSE POSITIVE: Issues our AI reported that are NOT in the manual redline

Be very specific about what we're missing and what we got right.
End with a MATCH PERCENTAGE and a list of the most critical gaps.""",
        },
    ]

    for page_path in ai_pages:
        b64 = encode_image(page_path)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "high"},
        })

    print("\n  Comparing manual vs AI redlines...")
    response = client.chat.completions.create(
        model="o3",
        messages=[
            {"role": "developer", "content": "You are an expert at comparing redline reviews. Be thorough and precise."},
            {"role": "user", "content": content},
        ],
        max_completion_tokens=16000,
        reasoning_effort="high",
    )

    result = response.choices[0].message.content
    usage = response.usage
    if usage:
        print(f"  Tokens: {usage.total_tokens} (prompt={usage.prompt_tokens}, completion={usage.completion_tokens})")
    return result


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: Set OPENAI_API_KEY")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Step 1: Render both PDFs
    print("=== Step 1: Rendering PDFs ===")
    print(f"Manual redline: {MANUAL_PDF}")
    manual_pages = render_pdf_pages(MANUAL_PDF, "manual_redline", dpi=300)

    print(f"\nAI redline: {AI_PDF}")
    ai_pages = render_pdf_pages(AI_PDF, "ai_redline", dpi=300)

    # Step 2: Analyze manual redline — use cached result if available
    cached_manual = OUTPUT_DIR / "manual_redline_analysis.txt"
    if cached_manual.exists() and cached_manual.stat().st_size > 100:
        print("\n=== Step 2: Using CACHED manual redline analysis ===")
        manual_analysis = cached_manual.read_text()
        print(f"  (loaded {len(manual_analysis)} chars from {cached_manual})")
    else:
        print("\n=== Step 2: AI Analysis of Manual Redline ===")
        manual_analysis = analyze_manual_redline(manual_pages, client)
        print("\n--- Manual Redline Findings ---")
        print(manual_analysis)
        cached_manual.write_text(manual_analysis)

    # Step 3: Compare
    print("\n=== Step 3: Comparison ===")
    comparison = compare_redlines(manual_analysis, ai_pages, client)
    print("\n--- Comparison Results ---")
    print(comparison)

    # Save comparison
    (OUTPUT_DIR / "redline_comparison.txt").write_text(comparison)
    print(f"\n=== Done — results saved to {OUTPUT_DIR}/ ===")


if __name__ == "__main__":
    main()
