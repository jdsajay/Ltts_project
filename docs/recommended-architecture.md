# Recommended Architecture — Local Development

## System Purpose

Automated compliance checking and redlining of medical device labels against ISO standards (ISO 14607, ISO 15223, and future standards). The system ingests standards into a knowledge base, analyzes label PDFs using AI vision, and produces annotated redline PDFs that mirror what a human regulatory reviewer would mark.

---

## High-Level Pipeline

```
┌──────────────────────────────────────────────────────────────────────┐
│                        1. INGESTION LAYER                           │
│                                                                      │
│  ISO PDFs ──► AI Ingester (o3) ──► Structured JSON (knowledge base) │
│  Symbol Library (.xlsm) ──► AI Symbol Ingester ──► symbol_library_  │
│                                                      ai.json        │
│  YAML Rules (config/rules/) ──► rules.py loader                     │
└───────────────────────────────────┬──────────────────────────────────┘
                                    │
┌───────────────────────────────────▼──────────────────────────────────┐
│                     2. DOCUMENT PROCESSING LAYER                     │
│                                                                      │
│  Label PDF ──► PyMuPDF ──► Page images (300 DPI PNGs)               │
│            ──► PDF text, tables, fonts, metadata                     │
│            ──► Tesseract OCR (word-level bounding boxes)             │
│            ──► Layout analysis (text / symbol / barcode zones)       │
│            ──► Barcode decoding (GS1-128, DataMatrix, QR → UDI)     │
│            ──► Symbol detection (template matching + OCR markers)    │
└───────────────────────────────────┬──────────────────────────────────┘
                                    │
┌───────────────────────────────────▼──────────────────────────────────┐
│                   3. AI COMPLIANCE ENGINE (core)                     │
│                                                                      │
│  Two modes:                                                          │
│                                                                      │
│  A. Rule-based check (fast, offline-capable)                         │
│     YAML rules ──► text/semantic matching ──► severity scoring       │
│                                                                      │
│  B. AI Vision Redline (primary — 3-pass pipeline, OpenAI o3)        │
│     Pass 0: Panel identification (low reasoning)                     │
│     Pass 1: Per-panel exhaustive analysis (medium reasoning)         │
│     Pass 2: Cross-panel consistency & dedup (medium reasoning)       │
│                                                                      │
│     Input: page image + knowledge base context + symbol library      │
│     Output: list of findings with bounding boxes and severity        │
└───────────────────────────────────┬──────────────────────────────────┘
                                    │
┌───────────────────────────────────▼──────────────────────────────────┐
│                        4. OUTPUT LAYER                               │
│                                                                      │
│  Redlined PDF ──► marker annotations + legend page                   │
│  Compliance report ──► Markdown + JSON                               │
│  Debug sections ──► per-panel crops for inspection                   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3-Pass AI Redline Pipeline (Detail)

This is the core differentiator — an AI vision pipeline that examines label artwork the way a human reviewer would.

### Pass 0 — Panel Identification

- **Input**: Full page image (300 DPI)
- **Model**: o3 (low reasoning effort)
- **Purpose**: Segment the page into panels/regions, classify each as `label_panel`, `data_table`, `title_block`, `revision_table`, `notes_block`, `drawing_info`, etc.
- **Output**: JSON array of panel bounding boxes with names and types
- **Filtering**: Non-label panels (`data_table`, `title_block`, `revision_table`, `notes_block`, `drawing_info`) are skipped in Pass 1 to save cost and reduce noise

### Pass 1 — Per-Panel Exhaustive Analysis

- **Input**: Cropped panel image + full knowledge base context + symbol library
- **Model**: o3 (medium reasoning effort)
- **Purpose**: For each label panel, identify every compliance issue:
  - Missing required symbols (ISO 15223 + ISO 14607)
  - Incorrect or ambiguous text
  - Missing mandatory fields (LOT, REF, manufacturer, etc.)
  - Font legibility issues
  - Barcode/UDI problems
  - Items that should be **deleted** (non-compliant content)
- **Output**: JSON array of findings, each with:
  - `finding_id`, `type` (missing | incorrect | add | delete | modify)
  - `severity` (NC = non-conformance, OFI = opportunity for improvement)
  - `location` (bounding box coordinates relative to panel)
  - `description`, `requirement`, `recommendation`

### Pass 2 — Cross-Panel Consistency

- **Input**: All Pass 1 findings + full page image
- **Model**: o3 (medium reasoning effort)
- **Purpose**: Deduplicate findings, check cross-panel consistency (e.g., same LOT format across panels), assign final bounding boxes in page coordinates
- **Output**: Deduplicated, finalized findings list

---

## Module Map

```
src/label_compliance/
├── cli.py                  # Click CLI — 7 commands (see below)
├── config.py               # Settings loader (YAML + .env → typed dataclasses)
├── __main__.py             # Entry point
│
├── knowledge_base/
│   ├── ai_ingester.py      # Sends ISO PDFs to o3 for structured extraction
│   ├── ai_symbol_ingester.py # Enriches symbol library via o3 vision
│   ├── ingester.py         # Legacy text-based PDF parser
│   ├── embeddings.py       # Sentence-transformer embeddings (all-MiniLM-L6-v2)
│   ├── store.py            # ChromaDB vector store wrapper
│   └── query.py            # Semantic similarity search over KB
│
├── document/
│   ├── pdf_reader.py       # PDF text/table/metadata extraction (PyMuPDF + pdfplumber)
│   ├── image_renderer.py   # Page → 300 DPI PNG rendering
│   ├── image_extractor.py  # Extract embedded images from PDF
│   ├── label_segmenter.py  # Segment multi-panel label pages
│   ├── ocr.py              # Tesseract OCR with preprocessing
│   ├── layout.py           # Zone detection (contour analysis)
│   ├── font_analyzer.py    # Font extraction & legibility validation
│   ├── symbol_detector.py  # ISO symbol detection (template + OCR)
│   ├── symbol_comparator.py # Symbol image comparison
│   ├── symbol_library_db.py # Symbol library data access
│   └── barcode_reader.py   # GS1-128, DataMatrix, QR → UDI parsing
│
├── compliance/
│   ├── checker.py          # Main orchestrator for rule-based compliance
│   ├── rules.py            # YAML rule loader + profile resolver
│   ├── matcher.py          # Text + semantic matching engine
│   ├── scorer.py           # Severity-weighted compliance scoring
│   └── specs_validator.py  # Cross-label specification validator
│
├── redline/
│   ├── ai_redliner.py      # ★ Core: 3-pass AI vision redline pipeline
│   ├── annotator.py        # Draw color-coded annotations on page images
│   ├── pdf_redliner.py     # Compose redlined PDF with cover page
│   ├── report.py           # Markdown + JSON report generation
│   └── validator.py        # Validate redline output quality
│
├── ai/
│   ├── base.py             # Abstract AIProvider interface + factory
│   ├── api.py              # OpenAI provider (o3 / GPT-4o)
│   └── local.py            # Ollama provider (llama3.2-vision, local)
│
└── utils/
    ├── helpers.py           # Shared utilities
    └── log.py               # Logging configuration
```

---

## CLI Commands

| Command | Purpose |
|---------|---------|
| `ingest` | Parse ISO standard PDFs into knowledge base (legacy text parser) |
| `ingest-ai` | Parse ISO standard PDFs using o3 AI vision → structured JSON |
| `ingest-symbols` | Enrich symbol library Excel export via o3 → symbol_library_ai.json |
| `check` | Run rule-based compliance check on label PDF(s) |
| `redline` | Run 3-pass AI vision redline pipeline on label PDF(s) |
| `report` | Generate summary reports from existing check/redline outputs |
| `run` | Full pipeline: ingest → check → report (batch mode) |

---

## Configuration

All settings live in `config/settings.yaml` with environment overrides via `.env`.

### Key Configuration Sections

| Section | Controls |
|---------|----------|
| `paths.*` | Input/output directories |
| `knowledge_base.*` | ChromaDB collection, embedding model, chunk sizes |
| `document.*` | OCR settings (DPI, language, confidence, preprocessing) |
| `compliance.*` | Rule files, semantic threshold, scoring levels |
| `profiles.*` | Label filename patterns → rule file mappings |
| `redline.*` | Annotation colors, font size, output format |
| `ai.*` | Provider selection, model names, temperature, batch size |
| `ai.redline_*` | 3-pass pipeline tuning (model, reasoning effort, token budgets, panel filtering) |

### AI Redline Tuning Knobs

```yaml
ai:
  redline_model: o3                          # Vision model
  redline_pass0_reasoning_effort: low        # Panel ID — fast
  redline_pass1_reasoning_effort: medium     # Per-panel analysis — thorough
  redline_pass2_reasoning_effort: medium     # Cross-panel dedup
  redline_pass0_max_completion_tokens: 16000
  redline_pass1_max_completion_tokens: 16000
  redline_pass2_max_completion_tokens: 8000
  redline_skip_panel_types:                  # Don't analyze these panel types
    - data_table
    - title_block
    - revision_table
    - notes_block
    - drawing_info
  redline_skip_name_keywords:                # Skip panels with these in name
    - title block
    - revision
    - bom
    - general notes
    - data table
```

---

## Knowledge Sources

| Source | Format | How Ingested |
|--------|--------|--------------|
| ISO 14607:2024 | PDF → JSON | `ingest-ai` (o3 reads PDF, extracts sections/requirements) |
| ISO 15223-1 | PDF → JSON | `ingest-ai` |
| Symbol Library | Excel (.xlsm) → JSON | `ingest-symbols` (o3 enriches each symbol with description/meaning) |
| Compliance Rules | YAML | Loaded directly by `rules.py` from `config/rules/` |
| Future: country-specific rules | YAML | Same loader — add new files to `config/rules/` and profiles |

---

## Data Flow: Redline Command

```
$ python -m label_compliance redline "data/labels/clean/DRWG107602_Rev D 1.pdf"

1. Load settings (config/settings.yaml + .env)
2. Load knowledge base (data/knowledge_base/*.json)
3. Load symbol library (data/symbol_library/symbol_library_ai.json)
4. Render each PDF page → 300 DPI PNG

For each page:
  5. PASS 0: Send full page to o3 → get panel bounding boxes & types
  6. Filter out non-label panels (title blocks, data tables, etc.)
  7. Crop each label panel from full page image

  For each label panel:
    8. PASS 1: Send cropped panel + KB context + symbol library to o3
       → get list of findings (missing, incorrect, add, delete, modify)

  9. PASS 2: Send all findings + full page to o3
     → deduplicated findings with page-level coordinates

  10. Render annotations onto page image:
      - Numbered markers at finding locations
      - Legend page with full details

11. Compose final PDF:
    - Page 1: Compliance summary cover page
    - Pages 2+: Annotated label pages
    - Final page(s): Finding legend with all details

12. Save to outputs/redlines/
```

---

## Directory Structure

```
project/
├── config/
│   ├── settings.yaml              # All configuration
│   └── rules/
│       ├── iso_14607.yaml         # 36+ rules for breast implant labels
│       └── iso_15223.yaml         # 15+ rules for medical device symbols
│
├── data/
│   ├── labels/clean/              # Input: clean label PDFs
│   ├── labels/redlines/           # Input: manual redline PDFs (for benchmarking)
│   ├── knowledge_base/            # AI-extracted ISO standard JSON
│   ├── symbol_library/            # Symbol library (Excel + AI-enriched JSON)
│   ├── standards/                 # Raw ISO standard PDFs
│   └── images/                    # Extracted page images and sections
│
├── outputs/
│   ├── redlines/                  # Generated redline PDFs
│   ├── reports/                   # Compliance reports (MD + JSON)
│   ├── logs/                      # Processing logs
│   └── debug_sections/            # Cropped panels for debugging
│
├── src/label_compliance/          # Main source code (see module map above)
├── tests/                         # 98 unit tests
├── scripts/                       # Utility/analysis scripts
└── docs/                          # Documentation
```

---

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Language | Python 3.12 | Ecosystem maturity for PDF/AI/ML |
| PDF engine | PyMuPDF (fitz) | Fast rendering, annotation, text extraction |
| AI vision | OpenAI o3 | Best-in-class multimodal reasoning for label analysis |
| OCR | Tesseract (via pytesseract) | Free, local, good enough for printed labels |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Runs locally, no API cost, 384-dim vectors |
| Vector store | ChromaDB | Lightweight local vector DB, no server needed |
| Barcodes | pyzbar + pylibdmtx | GS1-128 and DataMatrix decoding |
| CLI | Click | Clean command structure with options/flags |
| Config | PyYAML + python-dotenv | YAML for structure, .env for secrets |
| Testing | pytest | Standard Python test framework |

---

## Improvement Roadmap (Local-First)

### 1. Rendering Quality (High Priority)

The redline PDF output needs cleaner annotations:
- **Marker-only mode**: Small numbered markers on the label, all details in the legend
- Max 30 characters for any on-page text
- Max 40 markers per page to prevent clutter
- 7pt minimum font, 12px minimum marker spacing
- Proper connector lines from markers to relevant areas
- Legend page sorted by severity (NC first, then OFI)

### 2. Accuracy Improvement (High Priority)

Current benchmark: ~32.5% match against human manual redline.

Strategies:
- **Few-shot prompting**: Include examples of correct findings in Pass 1 prompt (2-3 ground-truth panel analyses from manual redlines)
- **Symbol library enrichment**: More detailed symbol descriptions with visual features for better symbol identification
- **Deletion detection**: Strengthen prompts to identify content that should be removed, not just content that's missing
- **Post-processing validation**: After AI returns findings, validate bounding boxes actually land on relevant content
- **Calibration data**: Build a set of 5-10 manually reviewed labels as ground truth to iteratively measure and improve

### 3. Active Learning Loop

Instead of model retraining (expensive, complex), use few-shot prompting with curated examples:
- Maintain a `data/few_shot_examples/` directory with human-validated panel analyses
- Inject 2-3 representative examples into the Pass 1 prompt
- When a reviewer corrects an AI finding, save the correction as a new few-shot example
- Periodically prune/rotate examples to keep prompt size manageable

### 4. Human Review Interface (Future)

A lightweight local web UI for reviewing and correcting AI findings:
- Display redlined PDF pages side-by-side with finding list
- Allow accept/reject/edit per finding
- Accepted corrections become few-shot examples automatically
- Built with Flask or Streamlit — runs entirely locally

### 5. Additional Standards & Rules

The system is designed to support new standards easily:
- Add new YAML rule files to `config/rules/`
- Add new profiles to `config/settings.yaml` to map label patterns to rule sets
- Ingest new ISO PDFs with `ingest-ai` command
- Country-specific requirements (EU MDR, FDA 21 CFR, etc.) can be added as additional rule files

### 6. Batch Processing & Caching

- Cache Pass 0 panel identification results (panels don't change between runs)
- Cache knowledge base context assembly (same KB across labels)
- Parallel processing of independent panels within a page
- Resume capability for interrupted batch runs

---

## Local Development Setup

```bash
# Clone and setup
git clone <repo-url> && cd Ltts_project
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env: set OPENAI_API_KEY=sk-...

# Ingest knowledge base (one-time)
python -m label_compliance ingest-ai          # ISO standards → JSON
python -m label_compliance ingest-symbols     # Symbol library → JSON

# Run redline on a label
python -m label_compliance redline "data/labels/clean/DRWG107602_Rev D 1.pdf"

# Run rule-based compliance check
python -m label_compliance check "data/labels/clean/DRWG107602_Rev D 1.pdf"

# Run tests
pytest tests/ -v
```
