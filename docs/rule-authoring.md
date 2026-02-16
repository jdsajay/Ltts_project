# Rule Authoring Guide

Compliance rules are defined in YAML files under `config/rules/`. Each file contains a list of rules that the checker evaluates against every label.

## Rule Format

```yaml
rules:
  - id: ISO14607-11.3c-surface           # Unique identifier
    iso_ref: "ISO 14607:2024, 11.3 c)"   # Standard clause reference
    description: >-                       # Human-readable description
      Implant surface characteristics including classification
      per Table G.2 (smooth, micro-textured, macro-textured, etc.)
    category: labeling                    # Rule category (see below)
    check_type: text_contains             # Match strategy (see below)
    markers:                              # Text strings to search for
      - "smooth"
      - "textured"
      - "micro-textured"
      - "macro-textured"
      - "surface classification"
    pattern: "(?i)(smooth|textured|nano|micro|macro)"   # Optional regex
    severity: critical                    # critical | major | minor
    new_in_2024: true                     # Flag for new/changed requirements
    specs:                                # Optional specifications
      min_size_mm: 5
      iso_7000_ref: "ISO 7000-2725"
```

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique rule ID. Convention: `STANDARD-CLAUSE-shortname` |
| `iso_ref` | string | Source clause in the standard |
| `description` | string | What the rule checks for |
| `category` | string | Grouping — see categories below |
| `check_type` | string | How to match — see check types below |
| `severity` | string | `critical` (3x weight), `major` (2x), `minor` (1x) |

## Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `markers` | list[string] | Text strings to search in OCR output (case-insensitive) |
| `pattern` | string | Python regex to match against full page text |
| `new_in_2024` | bool | Flag for newly added/changed requirements |
| `specs` | dict | Additional specifications (dimensions, references, etc.) |

## Categories

| Category | Used For |
|----------|----------|
| `labeling` | General label text requirements (manufacturer, model, warnings) |
| `symbol` | ISO 15223-1 symbol presence and sizing |
| `traceability` | UDI, barcodes, lot numbers, serial numbers |
| `sterilization` | Sterilization method and sterility indicators |
| `packaging` | Packaging-level requirements |

## Check Types

| Check Type | Behavior |
|------------|----------|
| `text_contains` | At least one marker must be present in OCR text. If ≥50% of markers match → PASS, else PARTIAL/FAIL |
| `regex_match` | The `pattern` regex must match somewhere in the full text |
| `symbol_present` | Checks for symbol via OCR markers and visual template matching |
| `barcode_present` | Checks for barcode/UDI via barcode reader |

## Scoring Impact

Rules affect the compliance score based on their severity:

```
Weight: critical = 3, major = 2, minor = 1

PASS    → earns full weight
PARTIAL → earns half weight
FAIL    → earns 0
```

**Overall thresholds** (configurable in `settings.yaml`):
- ≥ 85% → COMPLIANT
- ≥ 50% → PARTIAL
- < 50% → NON-COMPLIANT

Critical failures are always flagged in reports, even if the overall score is COMPLIANT.

## Examples

### Text Requirement

```yaml
- id: ISO14607-11.2-manufacturer
  iso_ref: "ISO 14607:2024, 11.2 a)"
  description: "Manufacturer name and address on the label"
  category: labeling
  check_type: text_contains
  markers:
    - "manufacturer"
    - "manufactured by"
    - "Mentor"
  severity: critical
  new_in_2024: false
```

### Symbol Rule

```yaml
- id: SYM-sterile
  iso_ref: "ISO 15223-1:2021, 5.2.1"
  description: "Sterile symbol (ISO 7000-2725)"
  category: symbol
  check_type: symbol_present
  markers:
    - "STERILE"
    - "sterility"
  severity: critical
  specs:
    min_size_mm: 5
    iso_7000_ref: "ISO 7000-2725"
```

### Barcode/UDI Rule

```yaml
- id: ISO14607-11.5-udi
  iso_ref: "ISO 14607:2024, 11.5"
  description: "UDI barcode with GTIN and production identifiers"
  category: traceability
  check_type: barcode_present
  markers:
    - "UDI"
    - "GTIN"
    - "(01)"
  severity: critical
  new_in_2024: false
```

## Adding Rules to an Existing File

Edit the YAML file directly and add entries to the `rules` list. The rule loader caches rules per run, so changes take effect on the next invocation.

## Creating a New Rule File

1. Create `config/rules/my_standard.yaml` with a `rules:` list
2. Add `my_standard.yaml` to `compliance.rule_files` in `config/settings.yaml`
3. Run `label-compliance check` — new rules are picked up automatically
