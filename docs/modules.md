# Module Reference

Detailed reference for every module in `src/label_compliance/`.

---

## `config.py` — Settings Loader

Loads `config/settings.yaml` and merges environment variables from `.env`.

| Export | Type | Description |
|--------|------|-------------|
| `get_settings()` | `→ Settings` | Singleton accessor for all configuration |
| `Settings` | dataclass | Top-level settings container |
| `Settings.ensure_dirs()` | method | Creates all output directories |

Settings dataclasses: `PathSettings`, `KBSettings`, `DocumentSettings`, `ComplianceSettings`, `RedlineSettings`, `AISettings`, `ProcessingSettings`

---

## `cli.py` — Command-Line Interface

Click-based CLI with four commands. Entry point registered as `label-compliance` in `pyproject.toml`.

| Command | Function | Description |
|---------|----------|-------------|
| `ingest` | `ingest()` | Parse ISO PDFs → KB JSON → ChromaDB index |
| `check` | `check()` | Check label PDFs, generate redlines and reports |
| `report` | `report()` | Cross-label summary from existing JSON reports |
| `run` | `run()` | Full pipeline: ingest → check → report |

---

## `knowledge_base/ingester.py` — ISO PDF Parser

| Function | Signature | Description |
|----------|-----------|-------------|
| `ingest_standard` | `(pdf_path: Path) → dict` | Parse a single ISO PDF into structured JSON |
| `ingest_all_standards` | `() → list[dict]` | Parse all PDFs in the configured standards directory |

Key regex patterns: `SECTION_RE`, `SHALL_RE`, `MEASUREMENT_RE`, `TABLE_REF_RE`

Output JSON structure:
```json
{
  "standard_id": "ISO-14607-2024",
  "sections": [{"number": "11.3", "title": "...", "body": "..."}],
  "requirements": ["The label shall include..."],
  "measurements": ["3 mm", "25 °C"],
  "table_refs": ["Table G.2"],
  "keywords": ["implant", "sterile", ...]
}
```

## `knowledge_base/embeddings.py` — Vector Embeddings

| Function | Signature | Description |
|----------|-----------|-------------|
| `embed_texts` | `(texts: list[str]) → list[list[float]]` | Batch embed using sentence-transformers |
| `embed_single` | `(text: str) → list[float]` | Embed a single text string |

Model: `all-MiniLM-L6-v2` (384 dimensions, runs locally)

## `knowledge_base/store.py` — ChromaDB Vector Store

| Class | Method | Description |
|-------|--------|-------------|
| `KnowledgeStore` | `index_knowledge_base(kb_path)` | Index a JSON KB file into ChromaDB |
| | `search(query, n_results)` | Semantic search by cosine similarity |
| | `reset()` | Clear the entire collection |

## `knowledge_base/query.py` — Query Interface

| Function | Signature | Description |
|----------|-----------|-------------|
| `query_requirements` | `(query: str, top_k: int) → list[dict]` | Find matching requirements |
| `find_applicable_requirements` | `(text: str, threshold: float) → list[dict]` | Filter by similarity threshold |

---

## `document/pdf_reader.py` — PDF Reader

| Function | Returns | Description |
|----------|---------|-------------|
| `read_pdf(pdf_path)` | `PDFData` | Extract text, tables, fonts, and metadata from a PDF |

`PDFData` contains `list[PageData]` where each page has `text`, `tables`, `fonts`, and `metadata`.

## `document/image_renderer.py` — Page Renderer

| Function | Returns | Description |
|----------|---------|-------------|
| `render_pages(pdf_path, output_dir)` | `list[Path]` | Render all pages as 300 DPI PNGs |
| `render_single_page(pdf_path, page_num, output_path)` | `Path` | Render one page |

## `document/ocr.py` — OCR Engine

| Function/Class | Description |
|----------------|-------------|
| `run_ocr(image_path)` | Run Tesseract with preprocessing, returns `OCRResult` |
| `preprocess_image(img, steps)` | Apply grayscale/threshold/denoise/sharpen |
| `OCRResult` | Contains `full_text`, `words: list[OCRWord]`, `text_blocks` |
| `OCRResult.text_lower` | Property: lowercase full text |
| `OCRResult.find_text(search)` | Find words matching a search string |
| `OCRResult.words_in_region(x, y, w, h)` | Get words within a bounding box |

## `document/layout.py` — Layout Analyzer

| Function | Returns | Description |
|----------|---------|-------------|
| `analyze_layout(image_path)` | `list[Zone]` | Detect text, symbol, barcode, and logo zones |

Uses OpenCV contour analysis with zone merging to identify layout regions.

## `document/font_analyzer.py` — Font Analyzer

| Function | Returns | Description |
|----------|---------|-------------|
| `extract_fonts(pdf_path)` | `list[FontInfo]` | Extract all font spans from PDF pages |
| `get_font_summary(fonts)` | `dict` | Summarize unique fonts, sizes, styles |
| `validate_font_size(fonts, min_size_pt)` | `list[dict]` | Find fonts below minimum size (default: 6pt) |

## `document/symbol_detector.py` — Symbol Detector

| Function | Returns | Description |
|----------|---------|-------------|
| `detect_symbols_from_ocr(ocr_result, rules)` | `list[SymbolMatch]` | Match symbols via OCR text markers |
| `detect_symbols_visual(image_path)` | `list[SymbolMatch]` | Multi-scale template matching (0.5x–1.5x) |

## `document/barcode_reader.py` — Barcode Reader

| Function | Returns | Description |
|----------|---------|-------------|
| `read_barcodes(image_path)` | `list[BarcodeResult]` | Read all barcodes from an image |

Supports GS1-128, DataMatrix, QR. Parses UDI Application Identifiers: `(01)` GTIN, `(10)` LOT, `(21)` Serial, `(17)` Expiry.

---

## `compliance/rules.py` — Rule Loader

| Function | Returns | Description |
|----------|---------|-------------|
| `load_rules()` | `list[dict]` | Load all rules from configured YAML files |
| `load_rules(rule_files)` | `list[dict]` | Load rules from a specific list of YAML files |
| `resolve_rules_for_label(label_filename)` | `tuple[list[dict], str]` | Match a label filename against profiles in `settings.yaml`. Returns `(rules, profile_name)`. Falls back to default `compliance.rule_files` if no profile matches. |
| `get_rules_by_category(category)` | `list[dict]` | Filter by category |
| `get_rules_by_severity(severity)` | `list[dict]` | Filter by severity |
| `get_new_2024_rules()` | `list[dict]` | Get rules flagged `new_in_2024: true` |

## `compliance/matcher.py` — Match Engine

| Function | Returns | Description |
|----------|---------|-------------|
| `match_rule_text(rule, ocr_result)` | `MatchResult` | Match a rule against OCR text |
| `match_rule_semantic(rule, text, kb_store)` | `MatchResult` | Match using vector similarity |
| `combine_match_results(results)` | `MatchResult` | Merge multi-page results for one rule |

## `compliance/scorer.py` — Score Calculator

| Function | Returns | Description |
|----------|---------|-------------|
| `compute_score(label_name, match_results)` | `ComplianceScore` | Severity-weighted compliance score |

`ComplianceScore` fields: `label_name`, `total_rules`, `passed`, `partial`, `failed`, `score_pct`, `status`, `critical_gaps`, `new_2024_gaps`

## `compliance/checker.py` — Main Orchestrator

| Function | Returns | Description |
|----------|---------|-------------|
| `check_label(pdf_path, rules, semantic)` | `LabelResult` | Full 6-step compliance check for one label. When `rules` is not provided, uses `resolve_rules_for_label()` to select the correct profile's rules. |

`LabelResult` fields: `label_name`, `pdf_path`, `profile`, `pages`, `score`, `match_results`, `fonts`, `barcodes`, `symbols`, `redline_path`, `report_path`

Steps: Read PDF → Extract fonts → Render pages → OCR + layout + symbols + barcodes → Match rules → Score

---

## `redline/annotator.py` — Image Annotator

| Function | Returns | Description |
|----------|---------|-------------|
| `annotate_label(label_result)` | `list[Path]` | Generate annotated redline PNGs with color-coded boxes |
| `annotate_comparison(original_path, redline_path, output_path)` | `Path` | Side-by-side comparison image |

Colors: Green=PASS, Red=FAIL, Orange=PARTIAL, Blue=INFO

## `redline/pdf_redliner.py` — PDF Redliner

| Function | Returns | Description |
|----------|---------|-------------|
| `generate_redlined_pdf(label_result)` | `Path` | PDF with annotations and compliance cover page |

## `redline/report.py` — Report Generator

| Function | Returns | Description |
|----------|---------|-------------|
| `generate_report(label_result)` | `(Path, Path)` | Markdown + JSON report for one label |
| `generate_summary_report(json_files, output_dir)` | `Path` | Cross-label summary with gap matrix |

---

## `ai/base.py` — AI Provider Interface

| Export | Description |
|--------|-------------|
| `AIProvider` | Abstract base class with `analyze()` and `analyze_with_image()` |
| `get_ai_provider()` | Factory that returns the configured provider |
| `NoOpProvider` | Dummy provider when AI is disabled |

## `ai/local.py` — Ollama Provider

Local inference using Ollama. Supports text and multimodal (llava, llama3.2-vision).

## `ai/api.py` — OpenAI Provider

API-based inference using GPT-4o. Supports text and image analysis. Requires `OPENAI_API_KEY` in `.env`.
