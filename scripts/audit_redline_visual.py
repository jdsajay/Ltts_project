import base64
import os
from pathlib import Path

import fitz
from openai import OpenAI

PDF_PATH = Path("outputs/redlines/redlined-DRWG107621_Rev_D_NATIVE_1.pdf")
OUT_DIR = Path("outputs/debug_sections")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing")

    with fitz.open(str(PDF_PATH)) as doc:
        pix = doc[0].get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
        img_path = OUT_DIR / "ai_redline_quality_page1.png"
        pix.save(str(img_path))

    img_b64 = base64.b64encode((OUT_DIR / "ai_redline_quality_page1.png").read_bytes()).decode("utf-8")

    prompt = """You are auditing REDLINE VISUAL QUALITY only.

Analyze this AI-generated redline page and provide:
1) Top 8 rendering/readability problems visible on the page.
2) A strict rendering spec for production-quality redlines.
3) JSON parameters:
{
  \"max_on_page_label_chars\": int,
  \"max_marker_radius\": int,
  \"label_font_size\": float,
  \"max_connectors_per_quadrant\": int,
  \"prefer_marker_only_mode\": bool,
  \"use_legend_only_for_details\": bool,
  \"min_marker_spacing_px\": int,
  \"max_labels_per_page\": int
}
Be practical and concise."""

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="o3",
        messages=[
            {
                "role": "developer",
                "content": "You are an expert in engineering redline readability and annotation UX.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}",
                            "detail": "high",
                        },
                    },
                ],
            },
        ],
        max_completion_tokens=5000,
        reasoning_effort="medium",
    )
    text = resp.choices[0].message.content or ""
    out_path = OUT_DIR / "redline_visual_audit.txt"
    out_path.write_text(text)
    print(text)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
