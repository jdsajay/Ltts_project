# Compliance Report: DRWG107602_Rev D 1

**Generated:** 2026-03-01 15:29
**Source:** DRWG107602_Rev D 1.pdf
**Pages:** 1

## Drawing Information

| Field | Value |
|-------|-------|
| Drawing Number | 107602 |
| Revision | D |
| Title | LABELS, ARTOURA, ULTRA HIGH PROFILE, NON-CE |
| Scale | 1:1 |
| Drawn By | WPAZ |
| Approved By | SEE PLM SYSTEM |
| Print Date | 4/4/2022 |
| Tolerance Standard | ASME Y14.5 |
| Sheet | SHEET 1 OF 1 |
| PLM Reference | SEE PLM SYSTEM |

**Tolerances:**

- .XX = .01
- .XXX = .005
- .XXXX = .0010
- ANGULAR = 1.0 DEGREES
- FRACTIONAL = 1/32

## Variable Field Definitions

> All variable text is displayed as its field name in the artwork.

| Variable | Description |
|----------|-------------|
| LOTNO | LOT NUMBER |
| SERNO | SERIAL NUMBER |
| MFGDATE | MANUFACTURING DATE |
| EXPDATE | EXPIRATION DATE |
| LPNBR | LABEL PART NUMBER |

## Character Limits

| Position | Max Characters |
|----------|----------------|
| 1 | 07 |
| 2 | 11 |
| 3 | 10 |
| 4 | 10 |
| 5 | 10 |

## Product Configuration Matrix

> 6 product variants defined.

| Item Number | Shelf Life | Volume | Diameter | Height/Proj | GTIN |
|-------------|------------|--------|----------|-------------|------|
| TEXP100RUH | 1460d | 350cc | 10.0cm | 7.0cm | 00081317009528 |
| TEXP110RUH | 1460d | 455cc | 11.0cm | 7.6cm | 00081317009535 |
| TEXP120RUH | 1460d | 535cc | 12.0cm | 8.0cm | 00081317009542 |
| TEXP130RUH | 1460d | 650cc | 13.0cm | 8.2cm | 00081317009559 |
| TEXP135RUH | 1460d | 700cc | 13.5cm | 8.3cm | 00081317009566 |
| TEXP140RUH | 1460d | 850cc | 14.0cm | 8.9cm | 00081317009573 |

## Manufacturing / Inspection Notes

- FIRST ARTICLE INSPECT PER QCIC000001
- MFG INSPECT PER QCIC00000163
- DO NOT SCALE DRAWING
- ALL OF THE VARIABLE TEXT IS DISPLAYED AS ITS FIELD NAME

## Summary

| Metric | Value |
|--------|-------|
| **Status** | **NON-COMPLIANT** |
| Score | 32.8% |
| Rules checked | 28 |
| ✅ Passed | 8 |
| ⚠️ Partial | 9 |
| ❌ Failed | 11 |
| Critical gaps | 14 |
| New 2024 gaps | 2 |
| 📏 Spec violations | 218 |
| Rules with spec failures | 14 |

## Section-by-Section Results

> PDF segmented into **3** label sections.

| # | Section | Type | Page | Score | Pass | Partial | Fail |
|---|---------|------|------|-------|------|---------|------|
| 1 | OUTER LID LABEL | outer_lid_label | 1 | NON-COMPLIANT (36.7%) | 7 | 11 | 10 |
| 2 | COMBO LABEL | combo_label | 1 | NON-COMPLIANT (40.5%) | 7 | 13 | 8 |
| 3 | THERMOFORM LABEL | thermoform_label | 1 | NON-COMPLIANT (39.2%) | 8 | 10 | 10 |

### 📄 OUTER LID LABEL
- **EART/Part:** 107602-005
- **Type:** outer_lid_label
- **Page:** 1
- **Score:** NON-COMPLIANT (36.7%)

**Variable fields:** LOTNO, SERNO, MFGDATE, EXPDATE, LPNBR, LOT

**Regulatory symbols detected:** LOT

**Notes:** FIRST ARTICLE INSPECT PER QCIC000001; MFG INSPECT PER QCIC00000163

| Status | Rule | Severity | Evidence |
|--------|------|----------|----------|
| ⚠️ | Implant shall be supplied in sealed sterile packaging | critical | sterile |
| ⚠️ | Double packaging system — inner and outer pack | major | outer |
| ❌ | Instructions for use shall accompany the implant | critical | — |
| ❌ | Labels shall comply with ISO 14630 and ISO 15223-1 | critical | — |
| ⚠️ | Nominal volume stated on the unit container label | critical | cc, pattern:850cc |
| ❌ | Implant type/model stated on the unit container | critical | — |
| ✅ | Implant dimensions: width, height/diameter, projection | critical | projection, diameter |
| ⚠️ | Volume also stated on the implant label (not just container) | critical | cc, pattern:850cc |
| ❌ | Description of the implant shell(s) | major | — |
| ❌ | Surface classification per normative Annex G, Table G.2 | critical | — |
| ❌ | Description of the implant fill material | major | — |
| ✅ | Shelf life / use-by date on packaging | critical | expir, EXPDATE |
| ❌ | Unique Device Identifier (UDI) on label | critical | — |
| ⚠️ | UDI carrier (barcode or 2D DataMatrix) | critical | GTIN |
| ⚠️ | Manufacturer symbol (factory icon) | critical | Mentor |
| ⚠️ | Date of manufacture symbol | critical | MFGDATE |
| ✅ | Use-by date / expiration symbol | critical | EXPDATE, expir |
| ✅ | Batch code / LOT number symbol | critical | LOT, LOTNO |
| ✅ | Serial number symbol | critical | No SN or SERNO symbol visible, SERNO |
| ⚠️ | Catalogue / reference number symbol | critical | REF |
| ⚠️ | Sterilization method symbol | critical | sterile |
| ❌ | Do not reuse / single use symbol | major | — |
| ⚠️ | CE marking with notified body number | critical | CE |
| ⚠️ | Manufacturer name and full registered address | critical | Irving, Texas |
| ❌ | Product name in official EU member state languages | major | — |
| ⚠️ | GTIN barcode (GS1-128 or 2D DataMatrix) | critical | GTIN |
| ⚠️ | Surface classification category code on label | critical | OTH |
| ❌ | Patient implant card included with product | major | — |

**Spec violations in OUTER LID LABEL:**

- ⚠️ **min_font_size_pt** (ISO14607-9.1): Required: ≥ 6pt font size → Actual: No matching font spans found
- ⚠️ **must_include** (ISO14607-9.1): Required: Must include: sealed → Actual: 'sealed' not found in text
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
- ⚠️ **min_font_size_pt** (ISO14607-11.3b-shell-desc): Required: ≥ 6pt font size → Actual: No matching font spans found
- ⚠️ **must_include** (ISO14607-11.3b-shell-desc): Required: Must include one of: shell OR barrier OR layer → Actual: None of [shell, barrier, layer] found in text
- ⚠️ **valid_classifications** (ISO14607-11.3c-surface): Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
- ⚠️ **table_ref** (ISO14607-11.3c-surface): Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
- ⚠️ **must_include** (ISO14607-11.3d-fill): Required: Must include one of: gel OR saline OR fill → Actual: None of [gel, saline, fill] found in text
- ⚠️ **min_height_mm** (ISO14607-11.5-udi): Required: ≥ 2mm height → Actual: Element not found — cannot measure height
- ⚠️ **min_font_size_pt** (ISO14607-11.5-udi): Required: ≥ 6pt font size → Actual: No matching font spans found
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.47mm (font Tahoma @ 7.0pt)
- ⚠️ **must_be_adjacent_to** (SYM-manufacturer): Required: Must be within 10mm of 'manufacturer' → Actual: Adjacent element 'manufacturer' not found
- ⚠️ **must_be_adjacent_to** (SYM-date-manufacture): Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
- ⚠️ **min_height_mm** (SYM-catalogue): Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
- ⚠️ **min_height_mm** (SYM-single-use): Required: ≥ 5mm height → Actual: Element not found — cannot measure height
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
- ⚠️ **must_include_nb_number** (SYM-ce-mark): Required: Notified body number directly adjacent to CE mark → Actual: CE mark found but NB number not adjacent. Standalone numbers nearby: ['1460', '1460', '9840', '6000', '7202']
- ⚠️ **must_include** (MDR-address): Required: Must include: street → Actual: 'street' not found in text
- ⚠️ **must_include** (MDR-address): Required: Must include: city → Actual: 'city' not found in text
- ⚠️ **must_include** (MDR-address): Required: Must include: country → Actual: 'country' not found in text
- ⚠️ **min_languages** (MDR-multilingual): Required: ≥ 3 languages → Actual: Found 1 languages: ['Sb']

**Symbols:** 17/48 found, 27 partial, 4 missing (64%)

### 📄 COMBO LABEL
- **EART/Part:** 107602-004
- **Type:** combo_label
- **Page:** 1
- **Score:** NON-COMPLIANT (40.5%)

**Notes:** DO NOT SCALE DRAWING

| Status | Rule | Severity | Evidence |
|--------|------|----------|----------|
| ⚠️ | Implant shall be supplied in sealed sterile packaging | critical | sterile |
| ⚠️ | Double packaging system — inner and outer pack | major | outer |
| ❌ | Instructions for use shall accompany the implant | critical | — |
| ❌ | Labels shall comply with ISO 14630 and ISO 15223-1 | critical | — |
| ⚠️ | Nominal volume stated on the unit container label | critical | cc, pattern:850cc |
| ❌ | Implant type/model stated on the unit container | critical | — |
| ✅ | Implant dimensions: width, height/diameter, projection | critical | projection, diameter |
| ⚠️ | Volume also stated on the implant label (not just container) | critical | cc, pattern:850cc |
| ❌ | Description of the implant shell(s) | major | — |
| ❌ | Surface classification per normative Annex G, Table G.2 | critical | — |
| ❌ | Description of the implant fill material | major | — |
| ✅ | Shelf life / use-by date on packaging | critical | expir, EXPDATE |
| ❌ | Unique Device Identifier (UDI) on label | critical | — |
| ⚠️ | UDI carrier (barcode or 2D DataMatrix) | critical | GTIN |
| ⚠️ | Manufacturer symbol (factory icon) | critical | Mentor |
| ⚠️ | Date of manufacture symbol | critical | MFGDATE |
| ✅ | Use-by date / expiration symbol | critical | EXPDATE, expir |
| ✅ | Batch code / LOT number symbol | critical | LOT, LOTNO |
| ✅ | Serial number symbol | critical | SN, serial |
| ⚠️ | Catalogue / reference number symbol | critical | REF |
| ⚠️ | Sterilization method symbol | critical | sterile |
| ❌ | Do not reuse / single use symbol | major | — |
| ⚠️ | CE marking with notified body number | critical | CE |
| ⚠️ | Manufacturer name and full registered address | critical | Irving, Texas |
| ⚠️ | Product name in official EU member state languages | major | es: |
| ⚠️ | GTIN barcode (GS1-128 or 2D DataMatrix) | critical | GTIN |
| ⚠️ | Surface classification category code on label | critical | OTH |
| ❌ | Patient implant card included with product | major | — |

**Spec violations in COMBO LABEL:**

- ⚠️ **min_font_size_pt** (ISO14607-9.1): Required: ≥ 6pt font size → Actual: No matching font spans found
- ⚠️ **must_include** (ISO14607-9.1): Required: Must include: sealed → Actual: 'sealed' not found in text
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
- ⚠️ **min_font_size_pt** (ISO14607-11.3b-shell-desc): Required: ≥ 6pt font size → Actual: No matching font spans found
- ⚠️ **must_include** (ISO14607-11.3b-shell-desc): Required: Must include one of: shell OR barrier OR layer → Actual: None of [shell, barrier, layer] found in text
- ⚠️ **valid_classifications** (ISO14607-11.3c-surface): Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
- ⚠️ **table_ref** (ISO14607-11.3c-surface): Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
- ⚠️ **must_include** (ISO14607-11.3d-fill): Required: Must include one of: gel OR saline OR fill → Actual: None of [gel, saline, fill] found in text
- ⚠️ **min_height_mm** (ISO14607-11.5-udi): Required: ≥ 2mm height → Actual: Element not found — cannot measure height
- ⚠️ **min_font_size_pt** (ISO14607-11.5-udi): Required: ≥ 6pt font size → Actual: No matching font spans found
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.47mm (font Tahoma @ 7.0pt)
- ⚠️ **must_be_adjacent_to** (SYM-manufacturer): Required: Must be within 10mm of 'manufacturer' → Actual: Adjacent element 'manufacturer' not found
- ⚠️ **must_be_adjacent_to** (SYM-date-manufacture): Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
- ⚠️ **min_height_mm** (SYM-catalogue): Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
- ⚠️ **min_height_mm** (SYM-single-use): Required: ≥ 5mm height → Actual: Element not found — cannot measure height
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
- ⚠️ **must_include** (MDR-address): Required: Must include: street → Actual: 'street' not found in text
- ⚠️ **must_include** (MDR-address): Required: Must include: city → Actual: 'city' not found in text
- ⚠️ **must_include** (MDR-address): Required: Must include: country → Actual: 'country' not found in text
- ⚠️ **min_languages** (MDR-multilingual): Required: ≥ 3 languages → Actual: Found 2 languages: ['BY', 'Sb']

**Symbols:** 18/48 found, 26 partial, 4 missing (65%)

### 📄 THERMOFORM LABEL
- **EART/Part:** 107602-004
- **Type:** thermoform_label
- **Page:** 1
- **Score:** NON-COMPLIANT (39.2%)

**Notes:** DO NOT SCALE DRAWING

| Status | Rule | Severity | Evidence |
|--------|------|----------|----------|
| ⚠️ | Implant shall be supplied in sealed sterile packaging | critical | sterile |
| ⚠️ | Double packaging system — inner and outer pack | major | outer |
| ❌ | Instructions for use shall accompany the implant | critical | — |
| ❌ | Labels shall comply with ISO 14630 and ISO 15223-1 | critical | — |
| ⚠️ | Nominal volume stated on the unit container label | critical | cc, pattern:850cc |
| ❌ | Implant type/model stated on the unit container | critical | — |
| ✅ | Implant dimensions: width, height/diameter, projection | critical | projection, diameter |
| ⚠️ | Volume also stated on the implant label (not just container) | critical | cc, pattern:850cc |
| ❌ | Description of the implant shell(s) | major | — |
| ❌ | Surface classification per normative Annex G, Table G.2 | critical | — |
| ❌ | Description of the implant fill material | major | — |
| ✅ | Shelf life / use-by date on packaging | critical | expir, EXPDATE |
| ❌ | Unique Device Identifier (UDI) on label | critical | — |
| ⚠️ | UDI carrier (barcode or 2D DataMatrix) | critical | GTIN |
| ⚠️ | Manufacturer symbol (factory icon) | critical | Mentor |
| ⚠️ | Date of manufacture symbol | critical | MFGDATE |
| ✅ | Use-by date / expiration symbol | critical | EXPDATE, expir |
| ✅ | Batch code / LOT number symbol | critical | LOT, LOTNO |
| ✅ | Serial number symbol | critical | SN, No SN or SERNO symbol visible |
| ⚠️ | Catalogue / reference number symbol | critical | REF |
| ⚠️ | Sterilization method symbol | critical | sterile |
| ❌ | Do not reuse / single use symbol | major | — |
| ⚠️ | CE marking with notified body number | critical | CE |
| ⚠️ | Manufacturer name and full registered address | critical | Irving, Texas |
| ❌ | Product name in official EU member state languages | major | — |
| ⚠️ | GTIN barcode (GS1-128 or 2D DataMatrix) | critical | GTIN |
| ⚠️ | Surface classification category code on label | critical | OTH |
| ❌ | Patient implant card included with product | major | — |

**Spec violations in THERMOFORM LABEL:**

- ⚠️ **min_font_size_pt** (ISO14607-9.1): Required: ≥ 6pt font size → Actual: No matching font spans found
- ⚠️ **must_include** (ISO14607-9.1): Required: Must include: sealed → Actual: 'sealed' not found in text
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
- ⚠️ **font_style** (ISO14607-11.2-volume): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
- ⚠️ **font_style** (ISO14607-11.3a-volume-label): Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
- ⚠️ **min_font_size_pt** (ISO14607-11.3b-shell-desc): Required: ≥ 6pt font size → Actual: No matching font spans found
- ⚠️ **must_include** (ISO14607-11.3b-shell-desc): Required: Must include one of: shell OR barrier OR layer → Actual: None of [shell, barrier, layer] found in text
- ⚠️ **valid_classifications** (ISO14607-11.3c-surface): Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
- ⚠️ **table_ref** (ISO14607-11.3c-surface): Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
- ⚠️ **must_include** (ISO14607-11.3d-fill): Required: Must include one of: gel OR saline OR fill → Actual: None of [gel, saline, fill] found in text
- ⚠️ **min_height_mm** (ISO14607-11.5-udi): Required: ≥ 2mm height → Actual: Element not found — cannot measure height
- ⚠️ **min_font_size_pt** (ISO14607-11.5-udi): Required: ≥ 6pt font size → Actual: No matching font spans found
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.47mm (font Tahoma @ 7.0pt)
- ⚠️ **must_be_adjacent_to** (SYM-manufacturer): Required: Must be within 10mm of 'manufacturer' → Actual: Adjacent element 'manufacturer' not found
- ⚠️ **must_be_adjacent_to** (SYM-date-manufacture): Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
- ⚠️ **min_height_mm** (SYM-catalogue): Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
- ⚠️ **min_height_mm** (SYM-single-use): Required: ≥ 5mm height → Actual: Element not found — cannot measure height
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
- ⚠️ **must_include** (MDR-address): Required: Must include: street → Actual: 'street' not found in text
- ⚠️ **must_include** (MDR-address): Required: Must include: city → Actual: 'city' not found in text
- ⚠️ **must_include** (MDR-address): Required: Must include: country → Actual: 'country' not found in text
- ⚠️ **min_languages** (MDR-multilingual): Required: ≥ 3 languages → Actual: Found 2 languages: ['BY', 'Sb']

**Symbols:** 18/48 found, 26 partial, 4 missing (65%)

## Rule-by-Rule Results (Overall)

| # | Status | Rule | ISO Ref | Severity | Evidence |
|---|--------|------|---------|----------|----------|
| 1 | ⚠️ | Implant shall be supplied in sealed sterile packaging | 9.1 | critical | STERILE symbol present, packaging, sealed |
| 2 | ❌ | Double packaging system — inner and outer pack | 9.2 | major | outer, No mention of double packaging, inner or outer pack |
| 3 | ❌ | Instructions for use shall accompany the implant | 10.1 | critical | Instructions for use symbol present |
| 4 | ❌ | Labels shall comply with ISO 14630 and ISO 15223-1 | 11.1 | critical | No mention of ISO 14630 or ISO 15223 |
| 5 | ⚠️ | Nominal volume stated on the unit container label | 11.2 | critical | cc, pattern:850cc, 850cc |
| 6 | ✅ | Implant type/model stated on the unit container | 11.2 | critical | MENTOR Artoura, Ultra High Profile, Breast Tissue Expander, Breast Tissue Expander, Suture Tabs, Textured, Integral Injection Dome |
| 7 | ❌ | Implant dimensions: width, height/diameter, projection | 11.3 a) | critical | pattern:10.0cm, mm, cm |
| 8 | ❌ | Volume also stated on the implant label (not just container) | 11.3 a) | critical | No volume information such as cc, ml, or volume is visible., cc, pattern:850cc |
| 9 | ❌ | Description of the implant shell(s) | 11.3 b) | major | No description of the implant shell is visible. |
| 10 | ⚠️ | Surface classification per normative Annex G, Table G.2 🆕 | 11.3 c) | critical | Textured surface is mentioned in the product description., Textured |
| 11 | ❌ | Description of the implant fill material | 11.3 d) | major | No mention of fill material such as gel, saline, fill, silicone gel, cohesive |
| 12 | ✅ | Shelf life / use-by date on packaging | 11.4 | critical | expir, EXPDATE symbol and field present, EXPDATE |
| 13 | ⚠️ | Unique Device Identifier (UDI) on label | 11.5 | critical | GTIN 00081317009573, GTIN 00081317009559, UDI present in text: (01)TK20(17)PDTETE(10)LOTNO |
| 14 | ✅ | UDI carrier (barcode or 2D DataMatrix) | 11.5 | critical | GTIN 00081317009573, GTIN 00081317009559, 1D barcode present |
| 15 | ⚠️ | Manufacturer symbol (factory icon) | ISO 15223-1:2021, 5.1.1 | critical | Mentor, Manufacturer symbol and address present: MENTOR, 3041 Skyway Circle North, Irving, TX 75038-3540 USA, MENTOR-TEXAS CORP. |
| 16 | ⚠️ | Date of manufacture symbol | ISO 15223-1:2021, 5.1.3 | critical | MFGDATE, MFGDATE symbol present |
| 17 | ✅ | Use-by date / expiration symbol | ISO 15223-1:2021, 5.1.4 | critical | EXPDATE symbol present, expir, EXPDATE |
| 18 | ✅ | Batch code / LOT number symbol | ISO 15223-1:2021, 5.1.5 | critical | LOT symbol present, LOT symbol present with placeholder 'LOTNO', lot |
| 19 | ✅ | Serial number symbol | ISO 15223-1:2021, 5.1.6 | critical | No SN or SERNO symbol visible, SERNO, No SN or SERNO symbol present |
| 20 | ⚠️ | Catalogue / reference number symbol | ISO 15223-1:2021, 5.1.7 | critical | EART 107602-001, 107602, REF |
| 21 | ✅ | Sterilization method symbol | ISO 15223-1:2021, 5.2.1–5.2.8 | critical | STERILE symbol present, STERILE symbol with 'STERILIZE' text, sterile |
| 22 | ⚠️ | Do not reuse / single use symbol | ISO 15223-1:2021, 5.4.2 | major | Do not reuse symbol present, Single use symbol (2), Single use symbol (crossed-out 2) |
| 23 | ❌ | CE marking with notified body number | EU MDR 2017/745, Art. 20 | critical | No CE mark visible, CE mark not visible, CE |
| 24 | ⚠️ | Manufacturer name and full registered address | ISO 14630 / EU MDR Art. 10(11) | critical | address, Skyway Circle North, MENTOR address: 3041 Skyway Circle North, Irving, TX 75038-3540 USA |
| 25 | ❌ | Product name in official EU member state languages | EU MDR Art. 10(11) | major | Product name only in English, es: |
| 26 | ✅ | GTIN barcode (GS1-128 or 2D DataMatrix) | EU MDR / UDI Regulation | critical | 00081317009528, GTIN 00081317009573, Barcode with (01) indicating GTIN present |
| 27 | ❌ | Surface classification category code on label 🆕 | ISO 14607:2024, Annex G, Table G.2 | critical | No visible surface classification category code such as NTX, SLC, SLO, CRC, CRO, No surface classification category code like NTX, SLC, SLO, CRC, CRO visible, OTH |
| 28 | ❌ | Patient implant card included with product | ISO 14607:2024, Annex H | major | Surgeon Name: Surgeon Name:, Surgeon Name: Surgeon Name, Date of Implant: Breast:RLIDIL |

## Compliance Gaps

### ⚠️ Implant shall be supplied in sealed sterile packaging
- **Rule ID:** ISO14607-9.1
- **ISO Reference:** 9.1
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** STERILE symbol present, packaging, sealed, sterile, THERMOFORM LABEL
- **Spec violations:** 12
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **must_include**: Required: Must include: sealed → Actual: 'sealed' not found in text
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **must_include**: Required: Must include: sealed → Actual: 'sealed' not found in text
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **must_include**: Required: Must include: sealed → Actual: 'sealed' not found in text
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **must_include**: Required: Must include: sealed → Actual: 'sealed' not found in text
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **must_include**: Required: Must include: sealed → Actual: 'sealed' not found in text
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **must_include**: Required: Must include: sealed → Actual: 'sealed' not found in text
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ❌ Double packaging system — inner and outer pack
- **Rule ID:** ISO14607-9.2
- **ISO Reference:** 9.2
- **Severity:** major
- **Status:** FAIL
- **Partial evidence:** outer, No mention of double packaging, inner or outer pack
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ❌ Instructions for use shall accompany the implant
- **Rule ID:** ISO14607-10.1
- **ISO Reference:** 10.1
- **Severity:** critical
- **Status:** FAIL
- **Partial evidence:** Instructions for use symbol present
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ❌ Labels shall comply with ISO 14630 and ISO 15223-1
- **Rule ID:** ISO14607-11.1
- **ISO Reference:** 11.1
- **Severity:** critical
- **Status:** FAIL
- **Partial evidence:** No mention of ISO 14630 or ISO 15223
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ⚠️ Nominal volume stated on the unit container label
- **Rule ID:** ISO14607-11.2-volume
- **ISO Reference:** 11.2
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** cc, pattern:850cc, 850cc, No volume information like cc or ml, No volume information like cc or ml found, No volume information visible
- **Spec violations:** 36
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
    - Location: {'bbox': (195.9042205810547, 92.76905059814453, 226.05418395996094, 109.87100219726562), 'text': '350cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
    - Location: {'bbox': (195.9159393310547, 107.09326934814453, 226.06590270996094, 124.19522094726562), 'text': '455cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
    - Location: {'bbox': (195.9276580810547, 121.41748809814453, 226.07762145996094, 138.51943969726562), 'text': '535cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
    - Location: {'bbox': (195.9393768310547, 135.8946533203125, 226.08934020996094, 152.99661254882812), 'text': '650cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
    - Location: {'bbox': (195.9513397216797, 150.371337890625, 226.10130310058594, 167.47329711914062), 'text': '700cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
    - Location: {'bbox': (195.9630584716797, 164.8485107421875, 226.11302185058594, 181.95046997070312), 'text': '850cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
    - Location: {'bbox': (195.9042205810547, 92.76905059814453, 226.05418395996094, 109.87100219726562), 'text': '350cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
    - Location: {'bbox': (195.9159393310547, 107.09326934814453, 226.06590270996094, 124.19522094726562), 'text': '455cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
    - Location: {'bbox': (195.9276580810547, 121.41748809814453, 226.07762145996094, 138.51943969726562), 'text': '535cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
    - Location: {'bbox': (195.9393768310547, 135.8946533203125, 226.08934020996094, 152.99661254882812), 'text': '650cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
    - Location: {'bbox': (195.9513397216797, 150.371337890625, 226.10130310058594, 167.47329711914062), 'text': '700cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
    - Location: {'bbox': (195.9630584716797, 164.8485107421875, 226.11302185058594, 181.95046997070312), 'text': '850cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
    - Location: {'bbox': (195.9042205810547, 92.76905059814453, 226.05418395996094, 109.87100219726562), 'text': '350cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
    - Location: {'bbox': (195.9159393310547, 107.09326934814453, 226.06590270996094, 124.19522094726562), 'text': '455cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
    - Location: {'bbox': (195.9276580810547, 121.41748809814453, 226.07762145996094, 138.51943969726562), 'text': '535cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
    - Location: {'bbox': (195.9393768310547, 135.8946533203125, 226.08934020996094, 152.99661254882812), 'text': '650cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
    - Location: {'bbox': (195.9513397216797, 150.371337890625, 226.10130310058594, 167.47329711914062), 'text': '700cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
    - Location: {'bbox': (195.9630584716797, 164.8485107421875, 226.11302185058594, 181.95046997070312), 'text': '850cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
    - Location: {'bbox': (195.9042205810547, 92.76905059814453, 226.05418395996094, 109.87100219726562), 'text': '350cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
    - Location: {'bbox': (195.9159393310547, 107.09326934814453, 226.06590270996094, 124.19522094726562), 'text': '455cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
    - Location: {'bbox': (195.9276580810547, 121.41748809814453, 226.07762145996094, 138.51943969726562), 'text': '535cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
    - Location: {'bbox': (195.9393768310547, 135.8946533203125, 226.08934020996094, 152.99661254882812), 'text': '650cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
    - Location: {'bbox': (195.9513397216797, 150.371337890625, 226.10130310058594, 167.47329711914062), 'text': '700cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
    - Location: {'bbox': (195.9630584716797, 164.8485107421875, 226.11302185058594, 181.95046997070312), 'text': '850cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
    - Location: {'bbox': (195.9042205810547, 92.76905059814453, 226.05418395996094, 109.87100219726562), 'text': '350cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
    - Location: {'bbox': (195.9159393310547, 107.09326934814453, 226.06590270996094, 124.19522094726562), 'text': '455cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
    - Location: {'bbox': (195.9276580810547, 121.41748809814453, 226.07762145996094, 138.51943969726562), 'text': '535cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
    - Location: {'bbox': (195.9393768310547, 135.8946533203125, 226.08934020996094, 152.99661254882812), 'text': '650cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
    - Location: {'bbox': (195.9513397216797, 150.371337890625, 226.10130310058594, 167.47329711914062), 'text': '700cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
    - Location: {'bbox': (195.9630584716797, 164.8485107421875, 226.11302185058594, 181.95046997070312), 'text': '850cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
    - Location: {'bbox': (195.9042205810547, 92.76905059814453, 226.05418395996094, 109.87100219726562), 'text': '350cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
    - Location: {'bbox': (195.9159393310547, 107.09326934814453, 226.06590270996094, 124.19522094726562), 'text': '455cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
    - Location: {'bbox': (195.9276580810547, 121.41748809814453, 226.07762145996094, 138.51943969726562), 'text': '535cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
    - Location: {'bbox': (195.9393768310547, 135.8946533203125, 226.08934020996094, 152.99661254882812), 'text': '650cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
    - Location: {'bbox': (195.9513397216797, 150.371337890625, 226.10130310058594, 167.47329711914062), 'text': '700cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
    - Location: {'bbox': (195.9630584716797, 164.8485107421875, 226.11302185058594, 181.95046997070312), 'text': '850cc'}
- **Specs passed:** 8
- **Action:** Review and update label to include this element

### ❌ Implant dimensions: width, height/diameter, projection
- **Rule ID:** ISO14607-11.3a-dimensions
- **ISO Reference:** 11.3 a)
- **Severity:** critical
- **Status:** FAIL
- **Partial evidence:** pattern:10.0cm, mm, cm, projection, No dimensions such as width, height, projection, or diameter are visible., diameter
- **Specs passed:** 19
- **Action:** Review and update label to include this element

### ❌ Volume also stated on the implant label (not just container)
- **Rule ID:** ISO14607-11.3a-volume-label
- **ISO Reference:** 11.3 a)
- **Severity:** critical
- **Status:** FAIL
- **Partial evidence:** No volume information such as cc, ml, or volume is visible., cc, pattern:850cc, 850cc
- **Spec violations:** 36
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
    - Location: {'bbox': (195.9042205810547, 92.76905059814453, 226.05418395996094, 109.87100219726562), 'text': '350cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
    - Location: {'bbox': (195.9159393310547, 107.09326934814453, 226.06590270996094, 124.19522094726562), 'text': '455cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
    - Location: {'bbox': (195.9276580810547, 121.41748809814453, 226.07762145996094, 138.51943969726562), 'text': '535cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
    - Location: {'bbox': (195.9393768310547, 135.8946533203125, 226.08934020996094, 152.99661254882812), 'text': '650cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
    - Location: {'bbox': (195.9513397216797, 150.371337890625, 226.10130310058594, 167.47329711914062), 'text': '700cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
    - Location: {'bbox': (195.9630584716797, 164.8485107421875, 226.11302185058594, 181.95046997070312), 'text': '850cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
    - Location: {'bbox': (195.9042205810547, 92.76905059814453, 226.05418395996094, 109.87100219726562), 'text': '350cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
    - Location: {'bbox': (195.9159393310547, 107.09326934814453, 226.06590270996094, 124.19522094726562), 'text': '455cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
    - Location: {'bbox': (195.9276580810547, 121.41748809814453, 226.07762145996094, 138.51943969726562), 'text': '535cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
    - Location: {'bbox': (195.9393768310547, 135.8946533203125, 226.08934020996094, 152.99661254882812), 'text': '650cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
    - Location: {'bbox': (195.9513397216797, 150.371337890625, 226.10130310058594, 167.47329711914062), 'text': '700cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
    - Location: {'bbox': (195.9630584716797, 164.8485107421875, 226.11302185058594, 181.95046997070312), 'text': '850cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
    - Location: {'bbox': (195.9042205810547, 92.76905059814453, 226.05418395996094, 109.87100219726562), 'text': '350cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
    - Location: {'bbox': (195.9159393310547, 107.09326934814453, 226.06590270996094, 124.19522094726562), 'text': '455cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
    - Location: {'bbox': (195.9276580810547, 121.41748809814453, 226.07762145996094, 138.51943969726562), 'text': '535cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
    - Location: {'bbox': (195.9393768310547, 135.8946533203125, 226.08934020996094, 152.99661254882812), 'text': '650cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
    - Location: {'bbox': (195.9513397216797, 150.371337890625, 226.10130310058594, 167.47329711914062), 'text': '700cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
    - Location: {'bbox': (195.9630584716797, 164.8485107421875, 226.11302185058594, 181.95046997070312), 'text': '850cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
    - Location: {'bbox': (195.9042205810547, 92.76905059814453, 226.05418395996094, 109.87100219726562), 'text': '350cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
    - Location: {'bbox': (195.9159393310547, 107.09326934814453, 226.06590270996094, 124.19522094726562), 'text': '455cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
    - Location: {'bbox': (195.9276580810547, 121.41748809814453, 226.07762145996094, 138.51943969726562), 'text': '535cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
    - Location: {'bbox': (195.9393768310547, 135.8946533203125, 226.08934020996094, 152.99661254882812), 'text': '650cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
    - Location: {'bbox': (195.9513397216797, 150.371337890625, 226.10130310058594, 167.47329711914062), 'text': '700cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
    - Location: {'bbox': (195.9630584716797, 164.8485107421875, 226.11302185058594, 181.95046997070312), 'text': '850cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
    - Location: {'bbox': (195.9042205810547, 92.76905059814453, 226.05418395996094, 109.87100219726562), 'text': '350cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
    - Location: {'bbox': (195.9159393310547, 107.09326934814453, 226.06590270996094, 124.19522094726562), 'text': '455cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
    - Location: {'bbox': (195.9276580810547, 121.41748809814453, 226.07762145996094, 138.51943969726562), 'text': '535cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
    - Location: {'bbox': (195.9393768310547, 135.8946533203125, 226.08934020996094, 152.99661254882812), 'text': '650cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
    - Location: {'bbox': (195.9513397216797, 150.371337890625, 226.10130310058594, 167.47329711914062), 'text': '700cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
    - Location: {'bbox': (195.9630584716797, 164.8485107421875, 226.11302185058594, 181.95046997070312), 'text': '850cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '350cc')
    - Location: {'bbox': (195.9042205810547, 92.76905059814453, 226.05418395996094, 109.87100219726562), 'text': '350cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '455cc')
    - Location: {'bbox': (195.9159393310547, 107.09326934814453, 226.06590270996094, 124.19522094726562), 'text': '455cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '535cc')
    - Location: {'bbox': (195.9276580810547, 121.41748809814453, 226.07762145996094, 138.51943969726562), 'text': '535cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '650cc')
    - Location: {'bbox': (195.9393768310547, 135.8946533203125, 226.08934020996094, 152.99661254882812), 'text': '650cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '700cc')
    - Location: {'bbox': (195.9513397216797, 150.371337890625, 226.10130310058594, 167.47329711914062), 'text': '700cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
    - Location: {'bbox': (195.9630584716797, 164.8485107421875, 226.11302185058594, 181.95046997070312), 'text': '850cc'}
- **Specs passed:** 8
- **Action:** Review and update label to include this element

### ❌ Description of the implant shell(s)
- **Rule ID:** ISO14607-11.3b-shell-desc
- **ISO Reference:** 11.3 b)
- **Severity:** major
- **Status:** FAIL
- **Partial evidence:** No description of the implant shell is visible.
- **Spec violations:** 12
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **must_include**: Required: Must include one of: shell OR barrier OR layer → Actual: None of [shell, barrier, layer] found in text
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **must_include**: Required: Must include one of: shell OR barrier OR layer → Actual: None of [shell, barrier, layer] found in text
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **must_include**: Required: Must include one of: shell OR barrier OR layer → Actual: None of [shell, barrier, layer] found in text
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **must_include**: Required: Must include one of: shell OR barrier OR layer → Actual: None of [shell, barrier, layer] found in text
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **must_include**: Required: Must include one of: shell OR barrier OR layer → Actual: None of [shell, barrier, layer] found in text
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **must_include**: Required: Must include one of: shell OR barrier OR layer → Actual: None of [shell, barrier, layer] found in text
- **Action:** Review and update label to include this element

### ⚠️ Surface classification per normative Annex G, Table G.2 **(NEW in 2024)**
- **Rule ID:** ISO14607-11.3c-surface
- **ISO Reference:** 11.3 c)
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** Textured surface is mentioned in the product description., Textured
- **Spec violations:** 12
  - ⚠️ **valid_classifications**: Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
  - ⚠️ **table_ref**: Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
  - ⚠️ **valid_classifications**: Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
  - ⚠️ **table_ref**: Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
  - ⚠️ **valid_classifications**: Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
  - ⚠️ **table_ref**: Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
  - ⚠️ **valid_classifications**: Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
  - ⚠️ **table_ref**: Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
  - ⚠️ **valid_classifications**: Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
  - ⚠️ **table_ref**: Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
  - ⚠️ **valid_classifications**: Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
  - ⚠️ **table_ref**: Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
- **Action:** Review and update label to include this element

### ❌ Description of the implant fill material
- **Rule ID:** ISO14607-11.3d-fill
- **ISO Reference:** 11.3 d)
- **Severity:** major
- **Status:** FAIL
- **Partial evidence:** No mention of fill material such as gel, saline, fill, silicone gel, cohesive
- **Spec violations:** 6
  - ⚠️ **must_include**: Required: Must include one of: gel OR saline OR fill → Actual: None of [gel, saline, fill] found in text
  - ⚠️ **must_include**: Required: Must include one of: gel OR saline OR fill → Actual: None of [gel, saline, fill] found in text
  - ⚠️ **must_include**: Required: Must include one of: gel OR saline OR fill → Actual: None of [gel, saline, fill] found in text
  - ⚠️ **must_include**: Required: Must include one of: gel OR saline OR fill → Actual: None of [gel, saline, fill] found in text
  - ⚠️ **must_include**: Required: Must include one of: gel OR saline OR fill → Actual: None of [gel, saline, fill] found in text
  - ⚠️ **must_include**: Required: Must include one of: gel OR saline OR fill → Actual: None of [gel, saline, fill] found in text
- **Specs passed:** 2
- **Action:** Review and update label to include this element

### ⚠️ Unique Device Identifier (UDI) on label
- **Rule ID:** ISO14607-11.5-udi
- **ISO Reference:** 11.5
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** GTIN 00081317009573, GTIN 00081317009559, UDI present in text: (01)TK20(17)PDTETE(10)LOTNO, GTIN: 00081317009573, GTIN 00081317009528, GTIN 00081317009566, GTIN: 00081317009559, GTIN: 00081317009528, GTIN: 00081317009566
- **Spec violations:** 12
  - ⚠️ **min_height_mm**: Required: ≥ 2mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **min_height_mm**: Required: ≥ 2mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **min_height_mm**: Required: ≥ 2mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **min_height_mm**: Required: ≥ 2mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **min_height_mm**: Required: ≥ 2mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **min_height_mm**: Required: ≥ 2mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
- **Action:** Review and update label to include this element

### ⚠️ Manufacturer symbol (factory icon)
- **Rule ID:** SYM-manufacturer
- **ISO Reference:** ISO 15223-1:2021, 5.1.1
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** Mentor, Manufacturer symbol and address present: MENTOR, 3041 Skyway Circle North, Irving, TX 75038-3540 USA, MENTOR-TEXAS CORP., Manufacturer symbol (factory icon) and name 'MENTOR' present, MENTOR, MENTOR®
- **Spec violations:** 24
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1055.60986328125, 1175.5142822265625, 1491.0391845703125, 1185.685302734375), 'text': 'PROPRIETARY AND CONFIDENTIAL - THE INFORMATION CON'}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1070.596923828125, 1182.5142822265625, 1476.05224609375, 1192.685302734375), 'text': 'ANY REPRODUCTION IN PART OR AS A WHOLE WITHOUT THE'}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.47mm (font Tahoma @ 7.0pt)
    - Location: {'bbox': (1008.7007446289062, 1113.3040771484375, 1133.591796875, 1123.47509765625), 'text': 'submitted to Mentor-Texas. for approval'}
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacturer' → Actual: Adjacent element 'manufacturer' not found
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1055.60986328125, 1175.5142822265625, 1491.0391845703125, 1185.685302734375), 'text': 'PROPRIETARY AND CONFIDENTIAL - THE INFORMATION CON'}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1070.596923828125, 1182.5142822265625, 1476.05224609375, 1192.685302734375), 'text': 'ANY REPRODUCTION IN PART OR AS A WHOLE WITHOUT THE'}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.47mm (font Tahoma @ 7.0pt)
    - Location: {'bbox': (1008.7007446289062, 1113.3040771484375, 1133.591796875, 1123.47509765625), 'text': 'submitted to Mentor-Texas. for approval'}
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacturer' → Actual: Adjacent element 'manufacturer' not found
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1055.60986328125, 1175.5142822265625, 1491.0391845703125, 1185.685302734375), 'text': 'PROPRIETARY AND CONFIDENTIAL - THE INFORMATION CON'}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1070.596923828125, 1182.5142822265625, 1476.05224609375, 1192.685302734375), 'text': 'ANY REPRODUCTION IN PART OR AS A WHOLE WITHOUT THE'}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.47mm (font Tahoma @ 7.0pt)
    - Location: {'bbox': (1008.7007446289062, 1113.3040771484375, 1133.591796875, 1123.47509765625), 'text': 'submitted to Mentor-Texas. for approval'}
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacturer' → Actual: Adjacent element 'manufacturer' not found
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1055.60986328125, 1175.5142822265625, 1491.0391845703125, 1185.685302734375), 'text': 'PROPRIETARY AND CONFIDENTIAL - THE INFORMATION CON'}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1070.596923828125, 1182.5142822265625, 1476.05224609375, 1192.685302734375), 'text': 'ANY REPRODUCTION IN PART OR AS A WHOLE WITHOUT THE'}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.47mm (font Tahoma @ 7.0pt)
    - Location: {'bbox': (1008.7007446289062, 1113.3040771484375, 1133.591796875, 1123.47509765625), 'text': 'submitted to Mentor-Texas. for approval'}
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacturer' → Actual: Adjacent element 'manufacturer' not found
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1055.60986328125, 1175.5142822265625, 1491.0391845703125, 1185.685302734375), 'text': 'PROPRIETARY AND CONFIDENTIAL - THE INFORMATION CON'}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1070.596923828125, 1182.5142822265625, 1476.05224609375, 1192.685302734375), 'text': 'ANY REPRODUCTION IN PART OR AS A WHOLE WITHOUT THE'}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.47mm (font Tahoma @ 7.0pt)
    - Location: {'bbox': (1008.7007446289062, 1113.3040771484375, 1133.591796875, 1123.47509765625), 'text': 'submitted to Mentor-Texas. for approval'}
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacturer' → Actual: Adjacent element 'manufacturer' not found
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1055.60986328125, 1175.5142822265625, 1491.0391845703125, 1185.685302734375), 'text': 'PROPRIETARY AND CONFIDENTIAL - THE INFORMATION CON'}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1070.596923828125, 1182.5142822265625, 1476.05224609375, 1192.685302734375), 'text': 'ANY REPRODUCTION IN PART OR AS A WHOLE WITHOUT THE'}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.47mm (font Tahoma @ 7.0pt)
    - Location: {'bbox': (1008.7007446289062, 1113.3040771484375, 1133.591796875, 1123.47509765625), 'text': 'submitted to Mentor-Texas. for approval'}
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacturer' → Actual: Adjacent element 'manufacturer' not found
- **Action:** Review and update label to include this element

### ⚠️ Date of manufacture symbol
- **Rule ID:** SYM-date-manufacture
- **ISO Reference:** ISO 15223-1:2021, 5.1.3
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** MFGDATE, MFGDATE symbol present
- **Spec violations:** 6
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ⚠️ Catalogue / reference number symbol
- **Rule ID:** SYM-catalogue
- **ISO Reference:** ISO 15223-1:2021, 5.1.7
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** EART 107602-001, 107602, REF, REF symbol present with 'TK04', EART 107602-004, REF symbol present
- **Spec violations:** 6
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
    - Location: {'text': 'REF', 'x': 5448, 'y': 3379, 'w': 65, 'h': 27}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
    - Location: {'text': 'REF', 'x': 5448, 'y': 3379, 'w': 65, 'h': 27}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
    - Location: {'text': 'REF', 'x': 5448, 'y': 3379, 'w': 65, 'h': 27}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
    - Location: {'text': 'REF', 'x': 5448, 'y': 3379, 'w': 65, 'h': 27}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
    - Location: {'text': 'REF', 'x': 5448, 'y': 3379, 'w': 65, 'h': 27}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
    - Location: {'text': 'REF', 'x': 5448, 'y': 3379, 'w': 65, 'h': 27}
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ⚠️ Do not reuse / single use symbol
- **Rule ID:** SYM-single-use
- **ISO Reference:** ISO 15223-1:2021, 5.4.2
- **Severity:** major
- **Status:** PARTIAL
- **Partial evidence:** Do not reuse symbol present, Single use symbol (2), Single use symbol (crossed-out 2)
- **Spec violations:** 6
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: Element not found — cannot measure height
- **Action:** Review and update label to include this element

### ❌ CE marking with notified body number
- **Rule ID:** SYM-ce-mark
- **ISO Reference:** EU MDR 2017/745, Art. 20
- **Severity:** critical
- **Status:** FAIL
- **Partial evidence:** No CE mark visible, CE mark not visible, CE, No CE marking visible
- **Spec violations:** 26
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
    - Location: {'bbox': (323.52459716796875, 1027.2801513671875, 545.9368896484375, 1044.382080078125), 'text': 'NO. OF MAXIMUM SPACES (CHARACTERS)'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
    - Location: {'bbox': (653.1255493164062, 72.5596923828125, 711.0254516601562, 90.02651977539062), 'text': 'Tolerance'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1027.420166015625, 1037.4332275390625, 1070.8092041015625, 1047.604248046875), 'text': 'TOLERANCES:'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
    - Location: {'bbox': (1375.7049560546875, 1089.9727783203125, 1419.6171875, 1106.2967529296875), 'text': 'NON-CE'}
  - ⚠️ **must_include_nb_number**: Required: Notified body number directly adjacent to CE mark → Actual: CE mark found but NB number not adjacent. Standalone numbers nearby: ['1460', '1460', '9840', '6000', '7202']
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
    - Location: {'bbox': (323.52459716796875, 1027.2801513671875, 545.9368896484375, 1044.382080078125), 'text': 'NO. OF MAXIMUM SPACES (CHARACTERS)'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
    - Location: {'bbox': (653.1255493164062, 72.5596923828125, 711.0254516601562, 90.02651977539062), 'text': 'Tolerance'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1027.420166015625, 1037.4332275390625, 1070.8092041015625, 1047.604248046875), 'text': 'TOLERANCES:'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
    - Location: {'bbox': (1375.7049560546875, 1089.9727783203125, 1419.6171875, 1106.2967529296875), 'text': 'NON-CE'}
  - ⚠️ **must_include_nb_number**: Required: Notified body number directly adjacent to CE mark → Actual: CE mark found but NB number not adjacent. Standalone numbers nearby: ['1460', '1460', '9840', '6000', '7202']
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
    - Location: {'bbox': (323.52459716796875, 1027.2801513671875, 545.9368896484375, 1044.382080078125), 'text': 'NO. OF MAXIMUM SPACES (CHARACTERS)'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
    - Location: {'bbox': (653.1255493164062, 72.5596923828125, 711.0254516601562, 90.02651977539062), 'text': 'Tolerance'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1027.420166015625, 1037.4332275390625, 1070.8092041015625, 1047.604248046875), 'text': 'TOLERANCES:'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
    - Location: {'bbox': (1375.7049560546875, 1089.9727783203125, 1419.6171875, 1106.2967529296875), 'text': 'NON-CE'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
    - Location: {'bbox': (323.52459716796875, 1027.2801513671875, 545.9368896484375, 1044.382080078125), 'text': 'NO. OF MAXIMUM SPACES (CHARACTERS)'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
    - Location: {'bbox': (653.1255493164062, 72.5596923828125, 711.0254516601562, 90.02651977539062), 'text': 'Tolerance'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1027.420166015625, 1037.4332275390625, 1070.8092041015625, 1047.604248046875), 'text': 'TOLERANCES:'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
    - Location: {'bbox': (1375.7049560546875, 1089.9727783203125, 1419.6171875, 1106.2967529296875), 'text': 'NON-CE'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
    - Location: {'bbox': (323.52459716796875, 1027.2801513671875, 545.9368896484375, 1044.382080078125), 'text': 'NO. OF MAXIMUM SPACES (CHARACTERS)'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
    - Location: {'bbox': (653.1255493164062, 72.5596923828125, 711.0254516601562, 90.02651977539062), 'text': 'Tolerance'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1027.420166015625, 1037.4332275390625, 1070.8092041015625, 1047.604248046875), 'text': 'TOLERANCES:'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
    - Location: {'bbox': (1375.7049560546875, 1089.9727783203125, 1419.6171875, 1106.2967529296875), 'text': 'NON-CE'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
    - Location: {'bbox': (323.52459716796875, 1027.2801513671875, 545.9368896484375, 1044.382080078125), 'text': 'NO. OF MAXIMUM SPACES (CHARACTERS)'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
    - Location: {'bbox': (653.1255493164062, 72.5596923828125, 711.0254516601562, 90.02651977539062), 'text': 'Tolerance'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1027.420166015625, 1037.4332275390625, 1070.8092041015625, 1047.604248046875), 'text': 'TOLERANCES:'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
    - Location: {'bbox': (1375.7049560546875, 1089.9727783203125, 1419.6171875, 1106.2967529296875), 'text': 'NON-CE'}
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ⚠️ Manufacturer name and full registered address
- **Rule ID:** MDR-address
- **ISO Reference:** ISO 14630 / EU MDR Art. 10(11)
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** address, Skyway Circle North, MENTOR address: 3041 Skyway Circle North, Irving, TX 75038-3540 USA, MENTOR, 3041 Skyway Circle North, Irving, TX 75038-3540 USA, Texas, Manufacturer address: 3041 Skyway Circle North, Irving, TX 75038-3540 USA, Irving
- **Spec violations:** 18
  - ⚠️ **must_include**: Required: Must include: street → Actual: 'street' not found in text
  - ⚠️ **must_include**: Required: Must include: city → Actual: 'city' not found in text
  - ⚠️ **must_include**: Required: Must include: country → Actual: 'country' not found in text
  - ⚠️ **must_include**: Required: Must include: street → Actual: 'street' not found in text
  - ⚠️ **must_include**: Required: Must include: city → Actual: 'city' not found in text
  - ⚠️ **must_include**: Required: Must include: country → Actual: 'country' not found in text
  - ⚠️ **must_include**: Required: Must include: street → Actual: 'street' not found in text
  - ⚠️ **must_include**: Required: Must include: city → Actual: 'city' not found in text
  - ⚠️ **must_include**: Required: Must include: country → Actual: 'country' not found in text
  - ⚠️ **must_include**: Required: Must include: street → Actual: 'street' not found in text
  - ⚠️ **must_include**: Required: Must include: city → Actual: 'city' not found in text
  - ⚠️ **must_include**: Required: Must include: country → Actual: 'country' not found in text
  - ⚠️ **must_include**: Required: Must include: street → Actual: 'street' not found in text
  - ⚠️ **must_include**: Required: Must include: city → Actual: 'city' not found in text
  - ⚠️ **must_include**: Required: Must include: country → Actual: 'country' not found in text
  - ⚠️ **must_include**: Required: Must include: street → Actual: 'street' not found in text
  - ⚠️ **must_include**: Required: Must include: city → Actual: 'city' not found in text
  - ⚠️ **must_include**: Required: Must include: country → Actual: 'country' not found in text
- **Specs passed:** 3
- **Action:** Review and update label to include this element

### ❌ Product name in official EU member state languages
- **Rule ID:** MDR-multilingual
- **ISO Reference:** EU MDR Art. 10(11)
- **Severity:** major
- **Status:** FAIL
- **Partial evidence:** Product name only in English, es:
- **Spec violations:** 6
  - ⚠️ **min_languages**: Required: ≥ 3 languages → Actual: Found 1 languages: ['Sb']
  - ⚠️ **min_languages**: Required: ≥ 3 languages → Actual: Found 1 languages: ['Sb']
  - ⚠️ **min_languages**: Required: ≥ 3 languages → Actual: Found 2 languages: ['BY', 'Sb']
  - ⚠️ **min_languages**: Required: ≥ 3 languages → Actual: Found 2 languages: ['BY', 'Sb']
  - ⚠️ **min_languages**: Required: ≥ 3 languages → Actual: Found 2 languages: ['BY', 'Sb']
  - ⚠️ **min_languages**: Required: ≥ 3 languages → Actual: Found 2 languages: ['BY', 'Sb']
- **Action:** Review and update label to include this element

### ❌ Surface classification category code on label **(NEW in 2024)**
- **Rule ID:** ISO14607-G.2
- **ISO Reference:** ISO 14607:2024, Annex G, Table G.2
- **Severity:** critical
- **Status:** FAIL
- **Partial evidence:** No visible surface classification category code such as NTX, SLC, SLO, CRC, CRO, No surface classification category code like NTX, SLC, SLO, CRC, CRO visible, OTH
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ❌ Patient implant card included with product
- **Rule ID:** ISO14607-H
- **ISO Reference:** ISO 14607:2024, Annex H
- **Severity:** major
- **Status:** FAIL
- **Partial evidence:** Surgeon Name: Surgeon Name:, Surgeon Name: Surgeon Name, Date of Implant: Breast:RLIDIL, Patient Name: Pationt Name, Patient Name: Pationt Name:, Symbol for information (i) present, but no explicit mention of patient implant card
- **Specs passed:** 1
- **Action:** Review and update label to include this element

## 📏 Specification Violations Detail

> These violations indicate that while the text content may be present,
> the physical attributes (size, font, position, adjacency) do not meet ISO requirements.

| Rule | Spec Field | Required | Actual | Severity | Page |
|------|-----------|----------|--------|----------|------|
| ISO14607-9.1 | min_font_size_pt | ≥ 6pt font size | No matching font spans found | critical | 1 |
| ISO14607-9.1 | must_include | Must include: sealed | 'sealed' not found in text | critical | 1 |
| ISO14607-9.1 | min_font_size_pt | ≥ 6pt font size | No matching font spans found | critical | 1 |
| ISO14607-9.1 | must_include | Must include: sealed | 'sealed' not found in text | critical | 1 |
| ISO14607-9.1 | min_font_size_pt | ≥ 6pt font size | No matching font spans found | critical | 1 |
| ISO14607-9.1 | must_include | Must include: sealed | 'sealed' not found in text | critical | 1 |
| ISO14607-9.1 | min_font_size_pt | ≥ 6pt font size | No matching font spans found | critical | 1 |
| ISO14607-9.1 | must_include | Must include: sealed | 'sealed' not found in text | critical | 1 |
| ISO14607-9.1 | min_font_size_pt | ≥ 6pt font size | No matching font spans found | critical | 1 |
| ISO14607-9.1 | must_include | Must include: sealed | 'sealed' not found in text | critical | 1 |
| ISO14607-9.1 | min_font_size_pt | ≥ 6pt font size | No matching font spans found | critical | 1 |
| ISO14607-9.1 | must_include | Must include: sealed | 'sealed' not found in text | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '350cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '455cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '535cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '650cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '700cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '850cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '350cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '455cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '535cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '650cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '700cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '850cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '350cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '455cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '535cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '650cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '700cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '850cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '350cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '455cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '535cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '650cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '700cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '850cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '350cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '455cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '535cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '650cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '700cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '850cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '350cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '455cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '535cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '650cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '700cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '850cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '350cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '455cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '535cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '650cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '700cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '850cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '350cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '455cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '535cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '650cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '700cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '850cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '350cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '455cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '535cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '650cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '700cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '850cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '350cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '455cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '535cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '650cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '700cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '850cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '350cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '455cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '535cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '650cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '700cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '850cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '350cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '455cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '535cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '650cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '700cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '850cc') | critical | 1 |
| ISO14607-11.3b-shell-desc | min_font_size_pt | ≥ 6pt font size | No matching font spans found | major | 1 |
| ISO14607-11.3b-shell-desc | must_include | Must include one of: shell OR barrier OR layer | None of [shell, barrier, layer] found in text | major | 1 |
| ISO14607-11.3b-shell-desc | min_font_size_pt | ≥ 6pt font size | No matching font spans found | major | 1 |
| ISO14607-11.3b-shell-desc | must_include | Must include one of: shell OR barrier OR layer | None of [shell, barrier, layer] found in text | major | 1 |
| ISO14607-11.3b-shell-desc | min_font_size_pt | ≥ 6pt font size | No matching font spans found | major | 1 |
| ISO14607-11.3b-shell-desc | must_include | Must include one of: shell OR barrier OR layer | None of [shell, barrier, layer] found in text | major | 1 |
| ISO14607-11.3b-shell-desc | min_font_size_pt | ≥ 6pt font size | No matching font spans found | major | 1 |
| ISO14607-11.3b-shell-desc | must_include | Must include one of: shell OR barrier OR layer | None of [shell, barrier, layer] found in text | major | 1 |
| ISO14607-11.3b-shell-desc | min_font_size_pt | ≥ 6pt font size | No matching font spans found | major | 1 |
| ISO14607-11.3b-shell-desc | must_include | Must include one of: shell OR barrier OR layer | None of [shell, barrier, layer] found in text | major | 1 |
| ISO14607-11.3b-shell-desc | min_font_size_pt | ≥ 6pt font size | No matching font spans found | major | 1 |
| ISO14607-11.3b-shell-desc | must_include | Must include one of: shell OR barrier OR layer | None of [shell, barrier, layer] found in text | major | 1 |
| ISO14607-11.3c-surface | valid_classifications | Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] | No valid classification code found in text | critical | 1 |
| ISO14607-11.3c-surface | table_ref | Content from Table G.2 must be present | Neither 'Table G.2' nor its content codes found | critical | 1 |
| ISO14607-11.3c-surface | valid_classifications | Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] | No valid classification code found in text | critical | 1 |
| ISO14607-11.3c-surface | table_ref | Content from Table G.2 must be present | Neither 'Table G.2' nor its content codes found | critical | 1 |
| ISO14607-11.3c-surface | valid_classifications | Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] | No valid classification code found in text | critical | 1 |
| ISO14607-11.3c-surface | table_ref | Content from Table G.2 must be present | Neither 'Table G.2' nor its content codes found | critical | 1 |
| ISO14607-11.3c-surface | valid_classifications | Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] | No valid classification code found in text | critical | 1 |
| ISO14607-11.3c-surface | table_ref | Content from Table G.2 must be present | Neither 'Table G.2' nor its content codes found | critical | 1 |
| ISO14607-11.3c-surface | valid_classifications | Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] | No valid classification code found in text | critical | 1 |
| ISO14607-11.3c-surface | table_ref | Content from Table G.2 must be present | Neither 'Table G.2' nor its content codes found | critical | 1 |
| ISO14607-11.3c-surface | valid_classifications | Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] | No valid classification code found in text | critical | 1 |
| ISO14607-11.3c-surface | table_ref | Content from Table G.2 must be present | Neither 'Table G.2' nor its content codes found | critical | 1 |
| ISO14607-11.3d-fill | must_include | Must include one of: gel OR saline OR fill | None of [gel, saline, fill] found in text | major | 1 |
| ISO14607-11.3d-fill | must_include | Must include one of: gel OR saline OR fill | None of [gel, saline, fill] found in text | major | 1 |
| ISO14607-11.3d-fill | must_include | Must include one of: gel OR saline OR fill | None of [gel, saline, fill] found in text | major | 1 |
| ISO14607-11.3d-fill | must_include | Must include one of: gel OR saline OR fill | None of [gel, saline, fill] found in text | major | 1 |
| ISO14607-11.3d-fill | must_include | Must include one of: gel OR saline OR fill | None of [gel, saline, fill] found in text | major | 1 |
| ISO14607-11.3d-fill | must_include | Must include one of: gel OR saline OR fill | None of [gel, saline, fill] found in text | major | 1 |
| ISO14607-11.5-udi | min_height_mm | ≥ 2mm height | Element not found — cannot measure height | critical | 1 |
| ISO14607-11.5-udi | min_font_size_pt | ≥ 6pt font size | No matching font spans found | critical | 1 |
| ISO14607-11.5-udi | min_height_mm | ≥ 2mm height | Element not found — cannot measure height | critical | 1 |
| ISO14607-11.5-udi | min_font_size_pt | ≥ 6pt font size | No matching font spans found | critical | 1 |
| ISO14607-11.5-udi | min_height_mm | ≥ 2mm height | Element not found — cannot measure height | critical | 1 |
| ISO14607-11.5-udi | min_font_size_pt | ≥ 6pt font size | No matching font spans found | critical | 1 |
| ISO14607-11.5-udi | min_height_mm | ≥ 2mm height | Element not found — cannot measure height | critical | 1 |
| ISO14607-11.5-udi | min_font_size_pt | ≥ 6pt font size | No matching font spans found | critical | 1 |
| ISO14607-11.5-udi | min_height_mm | ≥ 2mm height | Element not found — cannot measure height | critical | 1 |
| ISO14607-11.5-udi | min_font_size_pt | ≥ 6pt font size | No matching font spans found | critical | 1 |
| ISO14607-11.5-udi | min_height_mm | ≥ 2mm height | Element not found — cannot measure height | critical | 1 |
| ISO14607-11.5-udi | min_font_size_pt | ≥ 6pt font size | No matching font spans found | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.47mm (font Tahoma @ 7.0pt) | critical | 1 |
| SYM-manufacturer | must_be_adjacent_to | Must be within 10mm of 'manufacturer' | Adjacent element 'manufacturer' not found | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.47mm (font Tahoma @ 7.0pt) | critical | 1 |
| SYM-manufacturer | must_be_adjacent_to | Must be within 10mm of 'manufacturer' | Adjacent element 'manufacturer' not found | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.47mm (font Tahoma @ 7.0pt) | critical | 1 |
| SYM-manufacturer | must_be_adjacent_to | Must be within 10mm of 'manufacturer' | Adjacent element 'manufacturer' not found | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.47mm (font Tahoma @ 7.0pt) | critical | 1 |
| SYM-manufacturer | must_be_adjacent_to | Must be within 10mm of 'manufacturer' | Adjacent element 'manufacturer' not found | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.47mm (font Tahoma @ 7.0pt) | critical | 1 |
| SYM-manufacturer | must_be_adjacent_to | Must be within 10mm of 'manufacturer' | Adjacent element 'manufacturer' not found | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.47mm (font Tahoma @ 7.0pt) | critical | 1 |
| SYM-manufacturer | must_be_adjacent_to | Must be within 10mm of 'manufacturer' | Adjacent element 'manufacturer' not found | critical | 1 |
| SYM-date-manufacture | must_be_adjacent_to | Must be within 10mm of 'manufacture' | Adjacent element 'manufacture' not found | critical | 1 |
| SYM-date-manufacture | must_be_adjacent_to | Must be within 10mm of 'manufacture' | Adjacent element 'manufacture' not found | critical | 1 |
| SYM-date-manufacture | must_be_adjacent_to | Must be within 10mm of 'manufacture' | Adjacent element 'manufacture' not found | critical | 1 |
| SYM-date-manufacture | must_be_adjacent_to | Must be within 10mm of 'manufacture' | Adjacent element 'manufacture' not found | critical | 1 |
| SYM-date-manufacture | must_be_adjacent_to | Must be within 10mm of 'manufacture' | Adjacent element 'manufacture' not found | critical | 1 |
| SYM-date-manufacture | must_be_adjacent_to | Must be within 10mm of 'manufacture' | Adjacent element 'manufacture' not found | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.29mm (27px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.29mm (27px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.29mm (27px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.29mm (27px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.29mm (27px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.29mm (27px at 300dpi) | critical | 1 |
| SYM-single-use | min_height_mm | ≥ 5mm height | Element not found — cannot measure height | major | 1 |
| SYM-single-use | min_height_mm | ≥ 5mm height | Element not found — cannot measure height | major | 1 |
| SYM-single-use | min_height_mm | ≥ 5mm height | Element not found — cannot measure height | major | 1 |
| SYM-single-use | min_height_mm | ≥ 5mm height | Element not found — cannot measure height | major | 1 |
| SYM-single-use | min_height_mm | ≥ 5mm height | Element not found — cannot measure height | major | 1 |
| SYM-single-use | min_height_mm | ≥ 5mm height | Element not found — cannot measure height | major | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma,Bold @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.88mm (font Tahoma,Bold @ 11.0pt) | critical | 1 |
| SYM-ce-mark | must_include_nb_number | Notified body number directly adjacent to CE mark | CE mark found but NB number not adjacent. Standalo | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma,Bold @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.88mm (font Tahoma,Bold @ 11.0pt) | critical | 1 |
| SYM-ce-mark | must_include_nb_number | Notified body number directly adjacent to CE mark | CE mark found but NB number not adjacent. Standalo | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma,Bold @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.88mm (font Tahoma,Bold @ 11.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma,Bold @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.88mm (font Tahoma,Bold @ 11.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma,Bold @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.88mm (font Tahoma,Bold @ 11.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma,Bold @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.88mm (font Tahoma,Bold @ 11.0pt) | critical | 1 |
| MDR-address | must_include | Must include: street | 'street' not found in text | critical | 1 |
| MDR-address | must_include | Must include: city | 'city' not found in text | critical | 1 |
| MDR-address | must_include | Must include: country | 'country' not found in text | critical | 1 |
| MDR-address | must_include | Must include: street | 'street' not found in text | critical | 1 |
| MDR-address | must_include | Must include: city | 'city' not found in text | critical | 1 |
| MDR-address | must_include | Must include: country | 'country' not found in text | critical | 1 |
| MDR-address | must_include | Must include: street | 'street' not found in text | critical | 1 |
| MDR-address | must_include | Must include: city | 'city' not found in text | critical | 1 |
| MDR-address | must_include | Must include: country | 'country' not found in text | critical | 1 |
| MDR-address | must_include | Must include: street | 'street' not found in text | critical | 1 |
| MDR-address | must_include | Must include: city | 'city' not found in text | critical | 1 |
| MDR-address | must_include | Must include: country | 'country' not found in text | critical | 1 |
| MDR-address | must_include | Must include: street | 'street' not found in text | critical | 1 |
| MDR-address | must_include | Must include: city | 'city' not found in text | critical | 1 |
| MDR-address | must_include | Must include: country | 'country' not found in text | critical | 1 |
| MDR-address | must_include | Must include: street | 'street' not found in text | critical | 1 |
| MDR-address | must_include | Must include: city | 'city' not found in text | critical | 1 |
| MDR-address | must_include | Must include: country | 'country' not found in text | critical | 1 |
| MDR-multilingual | min_languages | ≥ 3 languages | Found 1 languages: ['Sb'] | major | 1 |
| MDR-multilingual | min_languages | ≥ 3 languages | Found 1 languages: ['Sb'] | major | 1 |
| MDR-multilingual | min_languages | ≥ 3 languages | Found 2 languages: ['BY', 'Sb'] | major | 1 |
| MDR-multilingual | min_languages | ≥ 3 languages | Found 2 languages: ['BY', 'Sb'] | major | 1 |
| MDR-multilingual | min_languages | ≥ 3 languages | Found 2 languages: ['BY', 'Sb'] | major | 1 |
| MDR-multilingual | min_languages | ≥ 3 languages | Found 2 languages: ['BY', 'Sb'] | major | 1 |

## Font Size Violations

| Font | Size | Min Required | Text Preview | Page |
|------|------|-------------|-------------|------|
| Arial | 5.9pt | 6.0pt | Printed on 4/4/2022 | 1 |
| Tahoma | 5.0pt | 6.0pt | LAST SAVED BY: wpaz ON Monday, April 4,  | 1 |

## 🏷️ Symbol Library Comparison

> Compared label content against the Symbol Library database (48 required symbols checked).

| Metric | Value |
|--------|-------|
| Symbols checked | 48 |
| ✅ Found | 18 |
| ⚠️ Partial | 26 |
| ❌ Missing | 4 |
| Score | 65% |

### ✅ Found Symbols

| Symbol Name | Classification | Expected Text | Match Method | Score |
|-------------|---------------|----------------|-------------|-------|
| 0197 - No Latex | Proprietary - Ethicon | Not made with natural rubber latex | Text | 100% |
| 171 - STERILE | Standard | Sterile | Text | 100% |
| CE 0120 | Safety Mark | TEXT NOT REQUIRED | Text | 100% |
| Use by date | Standard | Use-by date | Text | 100% |
| Caution | Standard | Caution | Visual | 90% |
| Rx Only horizontal | Standard | TEXT NOT REQUIRED | Text | 100% |
| CE 0123 | Safety Mark | TEXT NOT REQUIRED | Text | 100% |
| Brazil Device Mark | Safety Mark | NA | Text | 100% |
| Manufacturer | Standard | Manufacturer | Visual | 85% |
| Do not re-use | Standard | Do not re-use | Text | 100% |
| Non Sterile | Standard | Non-sterile | Text | 100% |
| 0276 - STERILE R wide | Standard | Sterilized using irradiation | Visual | 90% |
| STERILE Asceptic wide | Standard | Sterilized using aseptic processing tech | Visual | 85% |
| CE Mark | Safety Mark | TEXT NOT REQUIRED | Text | 100% |
| Caution, hot surface | Standard | Caution, hot surface | Visual | 90% |
| LOT | Standard | Batch code | Visual | 90% |
| STERILE EO wide | Standard | Sterilized using ethylene oxide | Visual | 90% |
| Rx Only Vertical | Standard | TEXT NOT REQUIRED | Text | 100% |

### ⚠️ Partially Matched Symbols

| Symbol Name | Expected Text | Actual Match | Details |
|-------------|---------------|-------------|---------|
| Mentor MplusCO2 | SILTEX™ Round Moderate Plus Profile Gel  | profile; breast; implant; ii | Partial text match (40%): profile, breast, implant |
| Mentor HPCO2 | SILTEX™ Round High Profile Gel Breast Im | high; profile; breast; implant; ii | Partial text match (56%): high, profile, breast |
| Sterile EO or R | Method of Sterilization: Ethylene Oxide  | of; or | Partial text match (29%): of, or |
| 0277 - STERILE Steam or Heat wide | Sterilized using steam or dry heat | or | Partial text match (17%): or |
| Mentor MPCO2 | SILTEX™ Round Moderate Profile Gel Breas | profile; breast; implant; ii | Partial text match (44%): profile, breast, implant |
| Non-Pyrogenic_424 | Non-pyrogenic | non | Partial text match (50%): non |
| 0253 - Sterile Fluid Path_for small point size | Sterile fluid path | sterile; fluid | Partial text match (67%): sterile, fluid |
| Date of Manufacture | Date of manufacture | date; of | Partial text match (67%): date, of |
| Model Number | Model Number | number | Partial text match (50%): number |
| Sterile barrier system-Single barrier | Single sterile barrier system | sterile; system | Partial text match (50%): sterile, system |
| Single sterile barrier system_protective packaging | Single sterile barrier system with prote | sterile; system; with | Partial text match (38%): sterile, system, with |
| Single sterile barrier system_protective packaging | Single sterile barrier system with prote | sterile; system; with | Partial text match (38%): sterile, system, with |
| No latex | Does not contain or presence of natural  | not; contain; or; of; natural; rubber; l | Partial text match (78%): not, contain, or |
| Unique Device Identifier | Unique Device Identifier | device | Partial text match (33%): device |
| Medical Device | Medical Device | device | Partial text match (50%): device |
| Double sterile barrier system | Double Sterile barrier system | sterile; system | Partial text match (50%): sterile, system |
| Consult Instruction for Use | Consult Instructions for use | for; use | Partial text match (50%): for, use |
| EC REP | Authorized representative in the Europea | in; the | Partial text match (25%): in, the |
| Do Not Resterilize | Do not resterilize | do; not | Partial text match (67%): do, not |
| Consult instruction for use I book | Consult instructions for use or consult  | for; use; or | Partial text match (50%): for, use, or |
| Country of Manufacture | Country of manufacture | of | Partial text match (33%): of |
| Packaging damaged | Do not use if package is damaged and con | do; not; use; if; is; and; for | Partial text match (67%): do, not, use |
| Regulatory Compliance Mark | Regulatory Compliance Mark | mark | Partial text match (33%): mark |
| Serial Interface | Serial Interface (for service use only) | serial; for; use; only | Partial text match (67%): serial, for, use |
| Cataloge number | Catalogue number | number | Partial text match (50%): number |
| CAUTION, patient weight limit | CAUTION, patient weight limit | patient | Partial text match (25%): patient |

### ❌ Missing Symbols

| Symbol Name | Classification | Expected Text | Regulation | Action |
|-------------|---------------|----------------|-----------|--------|
| Temperature limit | Standard | Temperature limit | ID: REG_0059.pdf
Title: ISO 7000 Graphical symbols for use o | Add to label |
| Importer | Standard | Importer | ID: REG_0082.pdf
Title: ISO 15223-1 Medical devices — Symbol | Add to label |
| EU REP | Standard | Authorized representative | ID: REG_0082.pdf
Title: ISO 15223-1 Medical devices — Symbol | Add to label |
| US REP | Standard | Authorized representative | ID: REG_0082.pdf
Title: ISO 15223-1 Medical devices — Symbol | Add to label |

## Page-by-Page OCR Details

### Page 1
- Words detected: 628
- Text length: 6367 chars
- Barcodes: 7
  - CODE128: SERNO
  - CODE128: 1234ABCD01
  - CODE128: LOTNO
  - CODE128: LOTNO
  - CODE128: SERNO
  - CODE128: 1234ABCD01
  - CODE128: LOTNO
- Layout zones: 17
