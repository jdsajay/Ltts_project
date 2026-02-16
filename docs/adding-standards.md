# Adding & Upgrading Standards

This guide explains how to add a new standard or upgrade an existing one.

**Key principle:** When a new version of a standard is released (e.g., ISO 14607:2024 replaces ISO 14607:2018), the old version must be removed entirely. The system always checks against the current version only — old versions are never kept alongside new ones.

---

## Upgrading a Standard (New Version Replaces Old)

When a newer edition of a standard is released, follow these steps to replace the old one completely.

### Step 1: Remove the Old Standard

```bash
# Remove old PDF
rm data/standards/ISO-14607-2018.pdf

# Remove old knowledge base JSON
rm data/knowledge_base/ISO-14607-2018.json

# Remove old rule file
rm config/rules/iso_14607_2018.yaml
```

### Step 2: Add the New Standard PDF

```bash
cp "ISO-14607-2024.pdf" data/standards/
```

### Step 3: Update the Rule File

Create a new rule file for the updated version. Rules often change between editions — do not reuse the old file without reviewing every rule.

```bash
# Create config/rules/iso_14607.yaml with updated rules
```

Mark any new or changed requirements with `new_in_2024: true` so they are flagged in reports:

```yaml
rules:
  - id: ISO14607-11.3c-surface
    iso_ref: "ISO 14607:2024, 11.3 c)"
    description: "Surface classification per Table G.2"
    category: labeling
    check_type: text_contains
    markers:
      - "smooth"
      - "textured"
      - "surface classification"
    severity: critical
    new_in_2024: true    # ← flags this as a new requirement
```

See [`rule-authoring.md`](rule-authoring.md) for the full rule format.

### Step 4: Update settings.yaml

Make sure `compliance.rule_files` references only the current rule files:

```yaml
compliance:
  rule_files:
    - iso_14607.yaml        # current version only
    - iso_15223.yaml
```

### Step 5: Rebuild the Knowledge Base

Always use `--rebuild` when replacing a standard to clear stale data:

```bash
label-compliance ingest --rebuild
```

This will:
1. Clear the existing ChromaDB collection
2. Parse all PDFs currently in `data/standards/`
3. Save new structured JSON to `data/knowledge_base/`
4. Re-index everything from scratch

### Step 6: Verify

Run checks to confirm labels are evaluated against the new standard:

```bash
label-compliance check --semantic
```

Review the output — any requirements marked `new_in_2024: true` will be highlighted in reports so you can see which labels fail the new requirements.

---

## Adding a Different Standard (Not a Replacement)

When adding a standard that covers a different domain (e.g., adding ISO 15223 for symbols alongside ISO 14607 for implants), both standards should coexist.

### Step 1: Place the PDF

```bash
cp "ISO-15223-1-2021.pdf" data/standards/
```

### Step 2: Run Ingestion

```bash
label-compliance ingest --rebuild
```

This will:
1. Parse every PDF in `data/standards/` using pdfplumber
2. Extract sections, "shall" requirements, measurements, table/figure references, and keywords
3. Save structured JSON to `data/knowledge_base/<standard-id>.json`
4. Index all requirements and section chunks into ChromaDB for semantic search

### What the Ingester Extracts

| Element | Detection Method | Example |
|---------|-----------------|---------|
| Sections | Regex: numbered headings (`11.3 Labelling requirements`) | `{number: "11.3", title: "Labelling...", body: "..."}` |
| Requirements | Regex: sentences containing "shall" | `"The label shall include the manufacturer name."` |
| Measurements | Regex: numeric values with units | `3 mm`, `25 °C`, `100 kPa` |
| Table references | Regex: `Table X.Y` patterns | `Table G.2` |
| Standard references | Regex: `ISO XXXXX` patterns | `ISO 15223-1:2021` |
| Symbol references | Regex: `ISO 7000` symbol IDs | `ISO 7000-2725` |
| Keywords | Frequency analysis of domain terms | `implant`, `sterile`, `labelling` |

### Step 3: Create Compliance Rules

Create a YAML rule file in `config/rules/`:

```yaml
# config/rules/iso_15223.yaml
rules:
  - id: SYM-mfg-date
    iso_ref: "ISO 15223-1:2021, 5.1.3"
    description: "Manufacturing date symbol shall be present"
    category: symbol
    check_type: text_contains
    markers:
      - "manufacturing date"
      - "date of manufacture"
      - "MFG"
    severity: critical
    new_in_2024: false
    specs:
      min_size_mm: 5
```

### Step 4: Register the Rule File

Add the new file to `config/settings.yaml`:

```yaml
compliance:
  rule_files:
    - iso_14607.yaml
    - iso_15223.yaml
    - new_standard.yaml    # ← add here
```

### Step 5: Verify

```bash
label-compliance check --semantic
```

All rules from all registered rule files are loaded and checked against every label.

---

## Summary: Upgrade vs. Add

| Scenario | Action |
|----------|--------|
| New **version** of same standard (e.g., 2018 → 2024) | **Replace**: delete old PDF + KB JSON + rule file, add new ones, `ingest --rebuild` |
| New **different** standard (e.g., adding ISO 15223) | **Add**: place PDF, create rules, register in settings, `ingest --rebuild` |

**The system should only contain current versions.** Never keep old editions in `data/standards/` or `config/rules/`.

---

## Label Profiles: Mapping Labels to Standards

Different labels may need to be checked against different standards. For example:
- Breast implant labels → ISO 14607 + ISO 15223
- Spinal implant labels → ISO 14630 + ISO 15223
- Engineering drawings → ISO 14607 only

This is handled by **profiles** in `config/settings.yaml`.

### Defining Profiles

Add a `profiles` section to `config/settings.yaml`:

```yaml
profiles:
  breast_implant:
    description: "CPG Gel Breast Implant labels"
    patterns:
      - "*ARTW*"
      - "*CPG*"
      - "*Gel*Breast*Implant*"
    rule_files:
      - iso_14607.yaml
      - iso_15223.yaml

  drawings:
    description: "Engineering drawings"
    patterns:
      - "*DRWG*"
    rule_files:
      - iso_14607.yaml

  spinal_implant:
    description: "Spinal implant labels"
    patterns:
      - "*SPINE*"
      - "*SPINAL*"
    rule_files:
      - iso_14630.yaml
      - iso_15223.yaml
```

### How It Works

| Field | Description |
|-------|-------------|
| `description` | Human-readable name for the profile |
| `patterns` | Glob patterns matched against the label **filename** (case-sensitive, uses `*` wildcards) |
| `rule_files` | Which YAML rule files to check this label against |

When a label is checked:
1. The system tries each profile's patterns against the label filename
2. First matching profile wins — its `rule_files` are used
3. If no profile matches, the default `compliance.rule_files` list is used

### Example Output

The CLI summary table shows which profile each label matched:

```
┌──────────────────────┬─────────────────┬──────────────┬────────┐
│ Label                │ Profile         │ Status       │ Score  │
├──────────────────────┼─────────────────┼──────────────┼────────┤
│ ARTW-100765708       │ breast_implant  │ PARTIAL      │  72%   │
│ DRWG107503_C         │ drawings        │ NON-COMPLIANT│  35%   │
│ SPINE-200001         │ spinal_implant  │ COMPLIANT    │  91%   │
│ UNKNOWN-LABEL        │ default         │ PARTIAL      │  60%   │
└──────────────────────┴─────────────────┴──────────────┴────────┘
```

### Adding a New Profile

1. Choose a profile name (e.g., `cardiac_device`)
2. Define filename patterns that identify these labels
3. List which rule files apply
4. Add to `profiles` in `settings.yaml` — no code changes needed

```yaml
  cardiac_device:
    description: "Cardiac device labels"
    patterns:
      - "*CARDIAC*"
      - "*HEART*"
      - "*CDV*"
    rule_files:
      - iso_14708.yaml
      - iso_15223.yaml
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Ingester finds 0 sections | PDF may be image-only — check if pdfplumber can extract text |
| Few requirements extracted | Verify the standard uses "shall" language; adjust `SHALL_RE` regex in `ingester.py` if needed |
| ChromaDB errors | Run `label-compliance ingest --rebuild` to reset the collection |
| Old rules still appearing | Ensure old YAML file was deleted and removed from `settings.yaml` |
| Stale KB data after upgrade | Always use `--rebuild` flag when replacing a standard |
