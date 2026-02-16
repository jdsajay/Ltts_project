# Architecture Guide

## Overview

The Label Compliance System is a four-layer pipeline that transforms ISO standard PDFs and label artwork PDFs into structured compliance reports with annotated redline outputs.

```
┌─────────────────────────────────────────────────────────────────┐
│                      INPUT LAYER                                │
│  ISO Standard PDFs ──► Ingester ──► Structured KB (JSON)        │
│  Label PDFs ──► PDF Reader + Image Renderer ──► OCR + Layout    │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                   KNOWLEDGE BASE LAYER                          │
│  ChromaDB Vector Store ◄── Sentence-Transformer Embeddings      │
│  Section index, requirement index, keyword index                │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                   COMPLIANCE ENGINE                             │
│  YAML Rules ──► Text Matching + Semantic Matching ──► Scoring   │
│  Severity weighting: critical (3x), major (2x), minor (1x)     │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     OUTPUT LAYER                                │
│  Annotated redline images (PNG)                                 │
│  Redlined PDF with cover page                                   │
│  Markdown + JSON reports                                        │
│  Cross-label gap summary matrix                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Module Map

### `knowledge_base/`

| Module | Purpose |
|--------|---------|
| `ingester.py` | Parses ISO standard PDFs into structured JSON: sections, requirements ("shall" statements), measurements, table references, symbol references, keywords |
| `embeddings.py` | Generates 384-dim vector embeddings using `all-MiniLM-L6-v2` (runs locally, no API needed) |
| `store.py` | Wraps ChromaDB for persistent indexing and cosine-similarity search |
| `query.py` | High-level query interface — finds applicable requirements for a given text |

### `document/`

| Module | Purpose |
|--------|---------|
| `pdf_reader.py` | Extracts text, tables, fonts, and metadata from PDFs using pdfplumber + PyMuPDF |
| `image_renderer.py` | Renders each PDF page as a 300 DPI PNG using PyMuPDF |
| `ocr.py` | Runs Tesseract OCR with preprocessing (grayscale, threshold, denoise, sharpen). Returns word-level bounding boxes |
| `layout.py` | Detects layout zones (text, symbol, barcode, logo) using contour analysis |
| `font_analyzer.py` | Extracts font names, sizes, styles. Validates minimum legibility (6pt) |
| `symbol_detector.py` | Detects ISO symbols via OCR text markers and multi-scale visual template matching |
| `barcode_reader.py` | Reads GS1-128, DataMatrix, QR barcodes. Parses UDI Application Identifiers (GTIN, LOT, Serial, Expiry) |

### `compliance/`

| Module | Purpose |
|--------|---------|
| `rules.py` | Loads compliance rules from YAML files (`config/rules/`). Supports filtering by category, severity, and new-in-2024. Resolves per-label **profiles** to map labels to specific rule sets |
| `matcher.py` | Text-based and semantic matching engine. Checks OCR text against rule markers and regex patterns |
| `scorer.py` | Severity-weighted scoring. Thresholds: ≥85% COMPLIANT, ≥50% PARTIAL, <50% NON-COMPLIANT |
| `checker.py` | **Main orchestrator.** For each label: resolve profile → load profile-specific rules → read PDF → extract fonts → render pages → OCR + layout → detect symbols/barcodes → match rules → score |

### `redline/`

| Module | Purpose |
|--------|---------|
| `annotator.py` | Draws color-coded bounding boxes on page images. Green=PASS, Red=FAIL, Orange=PARTIAL. Adds a side panel summary |
| `pdf_redliner.py` | Generates a redlined PDF with annotations overlaid on the original pages and a compliance cover page |
| `report.py` | Generates Markdown and JSON reports per label. Also generates a cross-label summary with gap matrix |

### `ai/`

| Module | Purpose |
|--------|---------|
| `base.py` | Abstract `AIProvider` interface and factory function `get_ai_provider()` |
| `local.py` | Ollama provider for free local LLM inference (text + multimodal with llava/llama3.2-vision) |
| `api.py` | OpenAI provider for GPT-4o multimodal analysis (requires API key) |

## Data Flow for a Single Label

```
label.pdf
    │
    ├──► pdf_reader.read_pdf()          → PDFData (text, tables, metadata)
    ├──► font_analyzer.extract_fonts()  → list[FontInfo]
    ├──► image_renderer.render_pages()  → list[page.png paths]
    │
    │   For each page image:
    │   ├──► ocr.run_ocr()             → OCRResult (words + bounding boxes)
    │   ├──► layout.analyze_layout()   → list[Zone]
    │   ├──► symbol_detector.detect()  → list[SymbolMatch]
    │   ├──► barcode_reader.read()     → list[BarcodeResult]
    │   └──► matcher.match_rule_text() → MatchResult per rule
    │
    ├──► scorer.compute_score()        → ComplianceScore
    │
    └──► Output:
         ├──► annotator.annotate_label()      → redline PNGs
         ├──► pdf_redliner.generate()         → redlined PDF
         └──► report.generate_report()        → MD + JSON
```

## Scoring Algorithm

Each rule has a severity: `critical`, `major`, or `minor`.

Weights: `critical=3`, `major=2`, `minor=1`

For each rule, the match status contributes:
- PASS → full weight
- PARTIAL → half weight
- FAIL → zero weight

```
weighted_score = sum(earned_weight) / sum(total_weight) × 100%

COMPLIANT       if weighted_score ≥ 85%
PARTIAL         if weighted_score ≥ 50%
NON-COMPLIANT   if weighted_score < 50%
```

Critical failures are flagged separately regardless of overall score.

## Extending the System

- **Add a new ISO standard**: See [`docs/adding-standards.md`](adding-standards.md)
- **Map labels to standards (profiles)**: See the "Label Profiles" section in [`docs/adding-standards.md`](adding-standards.md)
- **Write new compliance rules**: See [`docs/rule-authoring.md`](rule-authoring.md)
- **Swap AI providers**: Set `AI_PROVIDER` in `.env` — options: `local`, `openai`, `none`
