# Label Compliance System

Automated medical-device label compliance checker for ISO 14607:2024 and related standards. Ingests ISO standard PDFs into a searchable knowledge base, processes label artwork/drawing PDFs, checks text, symbols, fonts, barcodes, and dimensions against regulatory rules, and generates annotated redline outputs highlighting gaps.

---

## Quick Start

```bash
# 1. Clone and set up
git clone <repo-url> && cd Ltts_project
make install                     # creates .venv, installs everything

# 2. Activate the environment
source .venv/bin/activate

# 3. Run the full pipeline
label-compliance run             # ingest → check → report
```

Sample data is already included in `data/standards/` (ISO 14607:2024) and `data/labels/` (6 label PDFs).

## Manual Setup (without Make)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Tesseract OCR is required for label image analysis:
brew install tesseract           # macOS
# sudo apt install tesseract-ocr  # Ubuntu/Debian
```

## Project Structure

```
Ltts_project/
├── config/
│   ├── settings.yaml                # All paths, thresholds, and options
│   └── rules/
│       ├── iso_14607.yaml           # 27 rules for ISO 14607:2024
│       └── iso_15223.yaml           # 11 symbol rules for ISO 15223-1
├── src/label_compliance/            # Main package
│   ├── cli.py                       # CLI (click) — ingest, check, report, run
│   ├── config.py                    # YAML + .env settings loader
│   ├── knowledge_base/              # ISO ingestion, embeddings, ChromaDB store
│   ├── document/                    # PDF reader, OCR, layout, fonts, symbols, barcodes
│   ├── compliance/                  # Rule loader, matcher, scorer, checker
│   ├── redline/                     # Image annotator, PDF redliner, reports
│   └── ai/                          # Ollama (free) and OpenAI (API) providers
├── data/
│   ├── standards/                   # ISO standard PDFs (input)
│   ├── labels/                      # Label PDFs to check (input)
│   ├── knowledge_base/              # Generated KB JSON (auto-created)
│   └── symbol_library/              # Reference symbol images (optional)
├── outputs/                         # All generated output (auto-created)
│   ├── redlines/                    # Annotated PNG and PDF redlines
│   ├── reports/                     # Markdown + JSON compliance reports
│   └── logs/                        # Run logs
├── tests/                           # pytest suite (20 tests)
├── docs/                            # Meeting notes, reference transcripts
├── pyproject.toml                   # Dependencies and build config
├── Makefile                         # Dev workflow targets
├── requirements.txt                 # Pinned dependencies
└── .env.example                     # Environment variable template
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `label-compliance ingest` | Parse ISO PDFs → structured JSON KB → ChromaDB vector index |
| `label-compliance ingest --rebuild` | Clear existing KB and rebuild from scratch |
| `label-compliance check` | Check all labels in configured `data/labels/` |
| `label-compliance check path/to/label.pdf` | Check a specific label file |
| `label-compliance check -d path/to/dir/` | Check all PDFs in a directory |
| `label-compliance check --semantic` | Include semantic (vector) matching |
| `label-compliance check --no-redline` | Skip redline generation |
| `label-compliance check -f png` | Output format: `pdf`, `png`, or `both` |
| `label-compliance report` | Generate cross-label summary from existing results |
| `label-compliance run` | Full pipeline: ingest → check all → report |
| `label-compliance run --rebuild --semantic` | Full pipeline with KB rebuild and semantic matching |

## Configuration

All settings are in [`config/settings.yaml`](config/settings.yaml). Key sections:

| Section | Controls |
|---------|----------|
| `paths` | Input/output directories |
| `knowledge_base` | ChromaDB collection, chunk size, embedding model |
| `document` | Render DPI, OCR language, preprocessing steps |
| `compliance` | Rule files, semantic threshold, scoring levels |
| `profiles` | Map label filename patterns to specific rule files (see below) |
| `redline` | Annotation colors, font size, output format |
| `ai` | Provider selection, model, temperature |
| `processing` | Batch size, parallel workers |

For AI features, copy `.env.example` → `.env` and configure:

```bash
cp .env.example .env
```

### Label Profiles

Different labels can be checked against different standards using **profiles** in `settings.yaml`:

```yaml
profiles:
  breast_implant:
    patterns: ["*ARTW*", "*CPG*"]
    rule_files: [iso_14607.yaml, iso_15223.yaml]
  drawings:
    patterns: ["*DRWG*"]
    rule_files: [iso_14607.yaml]
```

Labels matching a profile's filename patterns will only be checked against that profile's rule files. Labels not matching any profile use the default `compliance.rule_files`. See [`docs/adding-standards.md`](docs/adding-standards.md) for full details.

### Environment Variables

| Variable | Values | Default |
|----------|--------|---------|
| `AI_PROVIDER` | `local` (Ollama), `openai`, `none` | `local` |
| `OPENAI_API_KEY` | Your API key | — |
| `OLLAMA_MODEL` | Any Ollama model | `llama3.2` |
| `RENDER_DPI` | Image resolution | `300` |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING` | `INFO` |

## What It Checks

| Category | Details |
|----------|---------|
| **Text content** | Manufacturer name, addresses, model/catalog numbers, warnings, IFU references, sterilization method, storage conditions |
| **ISO 14607:2024** | All 27 labeling clauses including **NEW 2024** surface classification (Section 11.3c, Table G.2) |
| **Symbols** | 11 ISO 15223-1 medical device symbols with ISO 7000 reference IDs and minimum dimensions |
| **Fonts** | Minimum legibility validation (6pt), font inventory per page |
| **Barcodes** | GS1-128, DataMatrix, QR code detection with UDI/GTIN/LOT/Serial/Expiry parsing |
| **Dimensions** | Symbol size validation (3mm / 5mm minimums per ISO requirements) |

## Testing

```bash
make test              # run all 20 tests
make lint              # ruff linting
make format            # ruff auto-format
pytest tests/ -v       # verbose test output
```

## System Requirements

| Requirement | Version |
|-------------|---------|
| Python | ≥ 3.11 |
| Tesseract OCR | ≥ 5.0 (`brew install tesseract`) |
| Ollama (optional) | Latest (`brew install ollama`) |

## Documentation

| Document | Location |
|----------|----------|
| Architecture guide | [`docs/architecture.md`](docs/architecture.md) |
| Adding new standards | [`docs/adding-standards.md`](docs/adding-standards.md) |
| Rule authoring | [`docs/rule-authoring.md`](docs/rule-authoring.md) |
| Module reference | [`docs/modules.md`](docs/modules.md) |
| Meeting transcript | [`docs/meeting-transcript-clean.md`](docs/meeting-transcript-clean.md) |
