# Compliance Report: DRWG107602_Rev D

**Generated:** 2026-02-26 06:31
**Source:** DRWG107602_Rev D.pdf
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
- 2D barcode contains : 01(TK20)+17(EXPDATE)+11(MFGDATE)+10(LOTNO)+ 21(SERNO) on the flag 
label

## Barcode Content Specifications

> 2D barcode data element structure:

- `01(TK20)+17(EXPDATE)+11(MFGDATE)+10(LOTNO)+21(SERNO)`

## Summary

| Metric | Value |
|--------|-------|
| **Status** | **PARTIAL** |
| Score | 57.3% |
| Rules checked | 28 |
| ✅ Passed | 14 |
| ⚠️ Partial | 11 |
| ❌ Failed | 3 |
| Critical gaps | 11 |
| New 2024 gaps | 2 |
| 📏 Spec violations | 180 |
| Rules with spec failures | 11 |

## Section-by-Section Results

> PDF segmented into **3** label sections.

| # | Section | Type | Page | Score | Pass | Partial | Fail |
|---|---------|------|------|-------|------|---------|------|
| 1 | OUTER LID LABEL | outer_lid_label | 1 | PARTIAL (58.7%) | 13 | 12 | 3 |
| 2 | COMBO LABEL | combo_label | 1 | PARTIAL (58.7%) | 13 | 12 | 3 |
| 3 | THERMOFORM LABEL | thermoform_label | 1 | PARTIAL (56.8%) | 12 | 13 | 3 |

### 📄 OUTER LID LABEL
- **EART/Part:** 107602-005
- **Type:** outer_lid_label
- **Page:** 1
- **Score:** PARTIAL (58.7%)

**Variable fields:** LOTNO, SERNO, MFGDATE, EXPDATE, LPNBR, LOT, TK20

**Regulatory symbols detected:** 2D DataMatrix barcode, LOT

**Barcode content:** `01(TK20)+17(EXPDATE)+11(MFGDATE)+10(LOTNO)+21(SERNO)`

**Notes:** FIRST ARTICLE INSPECT PER QCIC000001; MFG INSPECT PER QCIC00000163

| Status | Rule | Severity | Evidence |
|--------|------|----------|----------|
| ⚠️ | Implant shall be supplied in sealed sterile packaging | critical | sterile |
| ✅ | Double packaging system — inner and outer pack | major | outer, double |
| ❌ | Instructions for use shall accompany the implant | critical | — |
| ❌ | Labels shall comply with ISO 14630 and ISO 15223-1 | critical | — |
| ⚠️ | Nominal volume stated on the unit container label | critical | volume, ml |
| ⚠️ | Implant type/model stated on the unit container | critical | gel |
| ✅ | Implant dimensions: width, height/diameter, projection | critical | pattern:10.0cm, mm |
| ⚠️ | Volume also stated on the implant label (not just container) | critical | cc, pattern:850cc |
| ⚠️ | Description of the implant shell(s) | major | barrier |
| ❌ | Surface classification per normative Annex G, Table G.2 | critical | surface classification not present |
| ⚠️ | Description of the implant fill material | major | gel |
| ✅ | Shelf life / use-by date on packaging | critical | EXPDATE, shelf life |
| ⚠️ | Unique Device Identifier (UDI) on label | critical | UDI |
| ✅ | UDI carrier (barcode or 2D DataMatrix) | critical | GTIN, barcode |
| ⚠️ | Manufacturer symbol (factory icon) | critical | Mentor |
| ⚠️ | Date of manufacture symbol | critical | MFGDATE |
| ✅ | Use-by date / expiration symbol | critical | EXPDATE, expir |
| ✅ | Batch code / LOT number symbol | critical | LOT, lot |
| ✅ | Serial number symbol | critical | serial, SERNO |
| ⚠️ | Catalogue / reference number symbol | critical | REF |
| ⚠️ | Sterilization method symbol | critical | sterile |
| ❌ | Do not reuse / single use symbol | major | — |
| ⚠️ | CE marking with notified body number | critical | CE |
| ⚠️ | Manufacturer name and full registered address | critical | Irving, Texas |
| ⚠️ | Product name in official EU member state languages | major | es: |
| ✅ | GTIN barcode (GS1-128 or 2D DataMatrix) | critical | GTIN, (01) |
| ⚠️ | Surface classification category code on label | critical | OTH |
| ❌ | Patient implant card included with product | major | — |

**Spec violations in OUTER LID LABEL:**

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
- ⚠️ **valid_classifications** (ISO14607-11.3c-surface): Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
- ⚠️ **table_ref** (ISO14607-11.3c-surface): Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
- ⚠️ **valid_classifications** (ISO14607-11.3c-surface): Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
- ⚠️ **table_ref** (ISO14607-11.3c-surface): Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
- ⚠️ **valid_classifications** (ISO14607-11.3c-surface): Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
- ⚠️ **table_ref** (ISO14607-11.3c-surface): Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.47mm (font Tahoma @ 7.0pt)
- ⚠️ **must_be_adjacent_to** (SYM-manufacturer): Required: Must be within 10mm of 'manufacturer' → Actual: Adjacent element 'manufacturer' not found
- ⚠️ **must_be_adjacent_to** (SYM-date-manufacture): Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
- ⚠️ **min_height_mm** (SYM-catalogue): Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
- ⚠️ **min_height_mm** (SYM-catalogue): Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
- ⚠️ **min_height_mm** (SYM-catalogue): Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
- ⚠️ **min_height_mm** (SYM-single-use): Required: ≥ 5mm height → Actual: Element not found — cannot measure height
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
- ⚠️ **must_include_nb_number** (SYM-ce-mark): Required: Notified body number directly adjacent to CE mark → Actual: CE mark found but NB number not adjacent. Standalone numbers nearby: ['1460', '1460', '3041', '3540', '3540']
- ⚠️ **must_include** (MDR-address): Required: Must include: street → Actual: 'street' not found in text
- ⚠️ **must_include** (MDR-address): Required: Must include: city → Actual: 'city' not found in text
- ⚠️ **min_languages** (MDR-multilingual): Required: ≥ 3 languages → Actual: Found 1 languages: ['NO']

**Symbols:** 27/137 found, 67 partial, 43 missing (44%)

### 📄 COMBO LABEL
- **EART/Part:** 107602-004
- **Type:** combo_label
- **Page:** 1
- **Score:** PARTIAL (58.7%)

**Regulatory symbols detected:** UDI, MD (Medical Device), MR

**Notes:** DO NOT SCALE DRAWING

| Status | Rule | Severity | Evidence |
|--------|------|----------|----------|
| ⚠️ | Implant shall be supplied in sealed sterile packaging | critical | sterile |
| ✅ | Double packaging system — inner and outer pack | major | outer, double |
| ❌ | Instructions for use shall accompany the implant | critical | — |
| ❌ | Labels shall comply with ISO 14630 and ISO 15223-1 | critical | — |
| ⚠️ | Nominal volume stated on the unit container label | critical | cc, pattern:850cc |
| ⚠️ | Implant type/model stated on the unit container | critical | gel |
| ✅ | Implant dimensions: width, height/diameter, projection | critical | pattern:10.0cm, mm |
| ⚠️ | Volume also stated on the implant label (not just container) | critical | cc, pattern:850cc |
| ⚠️ | Description of the implant shell(s) | major | barrier |
| ❌ | Surface classification per normative Annex G, Table G.2 | critical | — |
| ⚠️ | Description of the implant fill material | major | gel |
| ✅ | Shelf life / use-by date on packaging | critical | EXPDATE, shelf life |
| ⚠️ | Unique Device Identifier (UDI) on label | critical | UDI |
| ✅ | UDI carrier (barcode or 2D DataMatrix) | critical | GTIN, barcode |
| ⚠️ | Manufacturer symbol (factory icon) | critical | Mentor |
| ⚠️ | Date of manufacture symbol | critical | MFGDATE |
| ✅ | Use-by date / expiration symbol | critical | EXPDATE, expir |
| ✅ | Batch code / LOT number symbol | critical | LOT, lot |
| ✅ | Serial number symbol | critical | serial, SERNO |
| ⚠️ | Catalogue / reference number symbol | critical | REF |
| ⚠️ | Sterilization method symbol | critical | sterile |
| ❌ | Do not reuse / single use symbol | major | — |
| ⚠️ | CE marking with notified body number | critical | CE |
| ⚠️ | Manufacturer name and full registered address | critical | Irving, Texas |
| ⚠️ | Product name in official EU member state languages | major | es: |
| ✅ | GTIN barcode (GS1-128 or 2D DataMatrix) | critical | GTIN, (01) |
| ⚠️ | Surface classification category code on label | critical | OTH |
| ❌ | Patient implant card included with product | major | — |

**Spec violations in COMBO LABEL:**

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
- ⚠️ **valid_classifications** (ISO14607-11.3c-surface): Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
- ⚠️ **table_ref** (ISO14607-11.3c-surface): Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.47mm (font Tahoma @ 7.0pt)
- ⚠️ **must_be_adjacent_to** (SYM-manufacturer): Required: Must be within 10mm of 'manufacturer' → Actual: Adjacent element 'manufacturer' not found
- ⚠️ **must_be_adjacent_to** (SYM-date-manufacture): Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
- ⚠️ **min_height_mm** (SYM-catalogue): Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
- ⚠️ **min_height_mm** (SYM-catalogue): Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
- ⚠️ **min_height_mm** (SYM-catalogue): Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
- ⚠️ **min_height_mm** (SYM-single-use): Required: ≥ 5mm height → Actual: Element not found — cannot measure height
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
- ⚠️ **must_include** (MDR-address): Required: Must include: street → Actual: 'street' not found in text
- ⚠️ **must_include** (MDR-address): Required: Must include: city → Actual: 'city' not found in text
- ⚠️ **min_languages** (MDR-multilingual): Required: ≥ 3 languages → Actual: Found 2 languages: ['BY', 'NO']

**Symbols:** 29/137 found, 67 partial, 41 missing (46%)

### 📄 THERMOFORM LABEL
- **EART/Part:** 107602-004
- **Type:** thermoform_label
- **Page:** 1
- **Score:** PARTIAL (56.8%)

**Regulatory symbols detected:** UDI, MD (Medical Device), MR

**Notes:** DO NOT SCALE DRAWING

| Status | Rule | Severity | Evidence |
|--------|------|----------|----------|
| ⚠️ | Implant shall be supplied in sealed sterile packaging | critical | sterile |
| ✅ | Double packaging system — inner and outer pack | major | outer, double |
| ❌ | Instructions for use shall accompany the implant | critical | — |
| ❌ | Labels shall comply with ISO 14630 and ISO 15223-1 | critical | — |
| ⚠️ | Nominal volume stated on the unit container label | critical | volume stated on the unit container label, cc |
| ⚠️ | Implant type/model stated on the unit container | critical | gel |
| ✅ | Implant dimensions: width, height/diameter, projection | critical | pattern:10.0cm, mm |
| ⚠️ | Volume also stated on the implant label (not just container) | critical | cc, pattern:850cc |
| ⚠️ | Description of the implant shell(s) | major | barrier |
| ❌ | Surface classification per normative Annex G, Table G.2 | critical | — |
| ⚠️ | Description of the implant fill material | major | gel |
| ✅ | Shelf life / use-by date on packaging | critical | EXPDATE, shelf life |
| ⚠️ | Unique Device Identifier (UDI) on label | critical | UDI |
| ✅ | UDI carrier (barcode or 2D DataMatrix) | critical | GTIN, barcode |
| ⚠️ | Manufacturer symbol (factory icon) | critical | Mentor |
| ⚠️ | Date of manufacture symbol | critical | MFGDATE |
| ✅ | Use-by date / expiration symbol | critical | EXPDATE, expir |
| ✅ | Batch code / LOT number symbol | critical | LOT, lot |
| ✅ | Serial number symbol | critical | serial, SERNO |
| ⚠️ | Catalogue / reference number symbol | critical | REF |
| ⚠️ | Sterilization method symbol | critical | sterile |
| ❌ | Do not reuse / single use symbol | major | — |
| ⚠️ | CE marking with notified body number | critical | CE |
| ⚠️ | Manufacturer name and full registered address | critical | Irving, Texas |
| ⚠️ | Product name in official EU member state languages | major | es: |
| ✅ | GTIN barcode (GS1-128 or 2D DataMatrix) | critical | GTIN, (01) |
| ⚠️ | Surface classification category code on label | critical | OTH |
| ❌ | Patient implant card included with product | major | — |

**Spec violations in THERMOFORM LABEL:**

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
- ⚠️ **valid_classifications** (ISO14607-11.3c-surface): Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
- ⚠️ **table_ref** (ISO14607-11.3c-surface): Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-manufacturer): Required: ≥ 3mm height → Actual: 2.47mm (font Tahoma @ 7.0pt)
- ⚠️ **must_be_adjacent_to** (SYM-manufacturer): Required: Must be within 10mm of 'manufacturer' → Actual: Adjacent element 'manufacturer' not found
- ⚠️ **must_be_adjacent_to** (SYM-date-manufacture): Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
- ⚠️ **min_height_mm** (SYM-catalogue): Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
- ⚠️ **min_height_mm** (SYM-catalogue): Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
- ⚠️ **min_height_mm** (SYM-catalogue): Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
- ⚠️ **min_height_mm** (SYM-single-use): Required: ≥ 5mm height → Actual: Element not found — cannot measure height
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
- ⚠️ **min_height_mm** (SYM-ce-mark): Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
- ⚠️ **must_include** (MDR-address): Required: Must include: street → Actual: 'street' not found in text
- ⚠️ **must_include** (MDR-address): Required: Must include: city → Actual: 'city' not found in text
- ⚠️ **min_languages** (MDR-multilingual): Required: ≥ 3 languages → Actual: Found 2 languages: ['BY', 'NO']

**Symbols:** 29/137 found, 66 partial, 42 missing (45%)

## Rule-by-Rule Results (Overall)

| # | Status | Rule | ISO Ref | Severity | Evidence |
|---|--------|------|---------|----------|----------|
| 1 | ⚠️ | Implant shall be supplied in sealed sterile packaging | 9.1 | critical | sterile, packaging, sealed |
| 2 | ✅ | Double packaging system — inner and outer pack | 9.2 | major | outer, double |
| 3 | ✅ | Instructions for use shall accompany the implant | 10.1 | critical | instructions for use, IFU, instructions |
| 4 | ✅ | Labels shall comply with ISO 14630 and ISO 15223-1 | 11.1 | critical | ISO 15223-1, ISO 14630 |
| 5 | ⚠️ | Nominal volume stated on the unit container label | 11.2 | critical | volume, cc, volume stated on the unit container label |
| 6 | ✅ | Implant type/model stated on the unit container | 11.2 | critical | type, gel, model |
| 7 | ✅ | Implant dimensions: width, height/diameter, projection | 11.3 a) | critical | pattern:10.0cm, mm, cm |
| 8 | ⚠️ | Volume also stated on the implant label (not just container) | 11.3 a) | critical | volume stated on the implant label, cc, pattern:850cc |
| 9 | ⚠️ | Description of the implant shell(s) | 11.3 b) | major | barrier, shell mentioned but no detailed description |
| 10 | ❌ | Surface classification per normative Annex G, Table G.2 🆕 | 11.3 c) | critical | surface classification not present |
| 11 | ✅ | Description of the implant fill material | 11.3 d) | major | fill material mentioned, gel, fill material mentioned but no detailed description |
| 12 | ✅ | Shelf life / use-by date on packaging | 11.4 | critical | EXPDATE, shelf life, expir |
| 13 | ✅ | Unique Device Identifier (UDI) on label | 11.5 | critical | UDI present on label, UDI-DI, UDI-PI |
| 14 | ✅ | UDI carrier (barcode or 2D DataMatrix) | 11.5 | critical | GTIN, barcode, (01) |
| 15 | ⚠️ | Manufacturer symbol (factory icon) | ISO 15223-1:2021, 5.1.1 | critical | MENTOR(TM), Mentor, MENTOR-TEXAS CORP. |
| 16 | ⚠️ | Date of manufacture symbol | ISO 15223-1:2021, 5.1.3 | critical | MFGDATE, manufactured, 4/4/2022, MFGDATE, Printed on 4/4/2022 |
| 17 | ✅ | Use-by date / expiration symbol | ISO 15223-1:2021, 5.1.4 | critical | EXPDATE, expir |
| 18 | ✅ | Batch code / LOT number symbol | ISO 15223-1:2021, 5.1.5 | critical | LOT, lot, LOTNO |
| 19 | ✅ | Serial number symbol | ISO 15223-1:2021, 5.1.6 | critical | serial, SERNO, SN |
| 20 | ⚠️ | Catalogue / reference number symbol | ISO 15223-1:2021, 5.1.7 | critical | REF, catalogue, catalog, reference number, 107602, 107602-004 |
| 21 | ⚠️ | Sterilization method symbol | ISO 15223-1:2021, 5.2.1–5.2.8 | critical | sterile |
| 22 | ⚠️ | Do not reuse / single use symbol | ISO 15223-1:2021, 5.4.2 | major | found, single use, DO NOT SCALE DRAWING |
| 23 | ⚠️ | CE marking with notified body number | EU MDR 2017/745, Art. 20 | critical | CE, 0086, CE, 0086 found in label text, CE |
| 24 | ❌ | Manufacturer name and full registered address | ISO 14630 / EU MDR Art. 10(11) | critical | Manufacturer name and full registered address not found, Texas, address |
| 25 | ⚠️ | Product name in official EU member state languages | EU MDR Art. 10(11) | major | MENTOR(TM), en:, de:, fr:, es:, it: found in label text, Product name in official EU member state languages (en:) present |
| 26 | ✅ | GTIN barcode (GS1-128 or 2D DataMatrix) | EU MDR / UDI Regulation | critical | GTIN, (01) |
| 27 | ❌ | Surface classification category code on label 🆕 | ISO 14607:2024, Annex G, Table G.2 | critical | Surface classification category code not found, OTH |
| 28 | ✅ | Patient implant card included with product | ISO 14607:2024, Annex H | major | Patient implant card included with product not explicitly stated but ' implant card' mentioned in text, patient card, patient identification found in label text, patient implant card included with product |

## Compliance Gaps

### ⚠️ Implant shall be supplied in sealed sterile packaging
- **Rule ID:** ISO14607-9.1
- **ISO Reference:** 9.1
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** sterile, packaging, sealed
- **Spec violations:** 6
  - ⚠️ **must_include**: Required: Must include: sealed → Actual: 'sealed' not found in text
  - ⚠️ **must_include**: Required: Must include: sealed → Actual: 'sealed' not found in text
  - ⚠️ **must_include**: Required: Must include: sealed → Actual: 'sealed' not found in text
  - ⚠️ **must_include**: Required: Must include: sealed → Actual: 'sealed' not found in text
  - ⚠️ **must_include**: Required: Must include: sealed → Actual: 'sealed' not found in text
  - ⚠️ **must_include**: Required: Must include: sealed → Actual: 'sealed' not found in text
- **Specs passed:** 3
- **Action:** Review and update label to include this element

### ⚠️ Nominal volume stated on the unit container label
- **Rule ID:** ISO14607-11.2-volume
- **ISO Reference:** 11.2
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** volume, cc, volume stated on the unit container label, ml, pattern:850cc
- **Spec violations:** 24
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

### ⚠️ Volume also stated on the implant label (not just container)
- **Rule ID:** ISO14607-11.3a-volume-label
- **ISO Reference:** 11.3 a)
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** volume stated on the implant label, cc, pattern:850cc
- **Spec violations:** 24
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

### ⚠️ Description of the implant shell(s)
- **Rule ID:** ISO14607-11.3b-shell-desc
- **ISO Reference:** 11.3 b)
- **Severity:** major
- **Status:** PARTIAL
- **Partial evidence:** barrier, shell mentioned but no detailed description
- **Specs passed:** 2
- **Action:** Review and update label to include this element

### ❌ Surface classification per normative Annex G, Table G.2 **(NEW in 2024)**
- **Rule ID:** ISO14607-11.3c-surface
- **ISO Reference:** 11.3 c)
- **Severity:** critical
- **Status:** FAIL
- **Partial evidence:** surface classification not present
- **Spec violations:** 6
  - ⚠️ **valid_classifications**: Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
  - ⚠️ **table_ref**: Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
  - ⚠️ **valid_classifications**: Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
  - ⚠️ **table_ref**: Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
  - ⚠️ **valid_classifications**: Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
  - ⚠️ **table_ref**: Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
- **Action:** Review and update label to include this element

### ⚠️ Manufacturer symbol (factory icon)
- **Rule ID:** SYM-manufacturer
- **ISO Reference:** ISO 15223-1:2021, 5.1.1
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** MENTOR(TM), Mentor, MENTOR-TEXAS CORP.
- **Spec violations:** 20
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
- **Specs passed:** 2
- **Action:** Review and update label to include this element

### ⚠️ Date of manufacture symbol
- **Rule ID:** SYM-date-manufacture
- **ISO Reference:** ISO 15223-1:2021, 5.1.3
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** MFGDATE, manufactured, 4/4/2022, MFGDATE, Printed on 4/4/2022
- **Spec violations:** 5
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
- **Specs passed:** 3
- **Action:** Review and update label to include this element

### ⚠️ Catalogue / reference number symbol
- **Rule ID:** SYM-catalogue
- **ISO Reference:** ISO 15223-1:2021, 5.1.7
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** REF, catalogue, catalog, reference number, 107602, 107602-004, REF
- **Spec violations:** 15
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
    - Location: {'text': 'REF|', 'x': 4514, 'y': 2235, 'w': 66, 'h': 28}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
    - Location: {'text': 'REF|', 'x': 5444, 'y': 2236, 'w': 66, 'h': 27}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
    - Location: {'text': 'REF', 'x': 4514, 'y': 3379, 'w': 66, 'h': 28}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
    - Location: {'text': 'REF|', 'x': 4514, 'y': 2235, 'w': 66, 'h': 28}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
    - Location: {'text': 'REF|', 'x': 5444, 'y': 2236, 'w': 66, 'h': 27}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
    - Location: {'text': 'REF', 'x': 4514, 'y': 3379, 'w': 66, 'h': 28}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
    - Location: {'text': 'REF|', 'x': 4514, 'y': 2235, 'w': 66, 'h': 28}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
    - Location: {'text': 'REF|', 'x': 5444, 'y': 2236, 'w': 66, 'h': 27}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
    - Location: {'text': 'REF', 'x': 4514, 'y': 3379, 'w': 66, 'h': 28}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
    - Location: {'text': 'REF|', 'x': 4514, 'y': 2235, 'w': 66, 'h': 28}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
    - Location: {'text': 'REF|', 'x': 5444, 'y': 2236, 'w': 66, 'h': 27}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
    - Location: {'text': 'REF', 'x': 4514, 'y': 3379, 'w': 66, 'h': 28}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
    - Location: {'text': 'REF|', 'x': 4514, 'y': 2235, 'w': 66, 'h': 28}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.29mm (27px at 300dpi)
    - Location: {'text': 'REF|', 'x': 5444, 'y': 2236, 'w': 66, 'h': 27}
  - ⚠️ **min_height_mm**: Required: ≥ 3mm height → Actual: 2.37mm (28px at 300dpi)
    - Location: {'text': 'REF', 'x': 4514, 'y': 3379, 'w': 66, 'h': 28}
- **Specs passed:** 4
- **Action:** Review and update label to include this element

### ⚠️ Sterilization method symbol
- **Rule ID:** SYM-sterilization
- **ISO Reference:** ISO 15223-1:2021, 5.2.1–5.2.8
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** sterile
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ⚠️ Do not reuse / single use symbol
- **Rule ID:** SYM-single-use
- **ISO Reference:** ISO 15223-1:2021, 5.4.2
- **Severity:** major
- **Status:** PARTIAL
- **Partial evidence:** found, single use, DO NOT SCALE DRAWING, single use, do not reuse
- **Spec violations:** 6
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: Element not found — cannot measure height
- **Action:** Review and update label to include this element

### ⚠️ CE marking with notified body number
- **Rule ID:** SYM-ce-mark
- **ISO Reference:** EU MDR 2017/745, Art. 20
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** CE, 0086, CE, 0086 found in label text, CE, CE, 0086 found
- **Spec violations:** 56
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
    - Location: {'bbox': (323.52459716796875, 1027.2801513671875, 545.9368896484375, 1044.382080078125), 'text': 'NO. OF MAXIMUM SPACES (CHARACTERS)'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
    - Location: {'bbox': (653.1255493164062, 72.5596923828125, 711.0254516601562, 90.02651977539062), 'text': 'Tolerance'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1027.420166015625, 1037.4332275390625, 1070.8092041015625, 1047.604248046875), 'text': 'TOLERANCES:'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
    - Location: {'bbox': (1375.7049560546875, 1089.9727783203125, 1419.6171875, 1106.2967529296875), 'text': 'NON-CE'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
    - Location: {'bbox': (287.0249938964844, 489.5039978027344, 439.09197998046875, 505.99200439453125), 'text': 'Replace these symbols with'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
    - Location: {'bbox': (459.37298583984375, 490.9850158691406, 539.4219970703125, 507.4730224609375), 'text': 'Replace these'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (1275.1920166015625, 865.3579711914062, 1521.800048828125, 877.7239379882812), 'text': 'Replace with below label information and Add MD, M'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (1346.136962890625, 217.39097595214844, 1559.2469482421875, 229.75697326660156), 'text': 'Replace these 2 sections of label with these symbo'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (783.2269897460938, 979.9380493164062, 996.3370361328125, 992.3040161132812), 'text': 'Replace these 2 sections of label with these symbo'}
  - ⚠️ **must_include_nb_number**: Required: Notified body number directly adjacent to CE mark → Actual: CE mark found but NB number not adjacent. Standalone numbers nearby: ['1460', '1460', '3041', '3540', '3540']
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
    - Location: {'bbox': (323.52459716796875, 1027.2801513671875, 545.9368896484375, 1044.382080078125), 'text': 'NO. OF MAXIMUM SPACES (CHARACTERS)'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
    - Location: {'bbox': (653.1255493164062, 72.5596923828125, 711.0254516601562, 90.02651977539062), 'text': 'Tolerance'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1027.420166015625, 1037.4332275390625, 1070.8092041015625, 1047.604248046875), 'text': 'TOLERANCES:'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
    - Location: {'bbox': (1375.7049560546875, 1089.9727783203125, 1419.6171875, 1106.2967529296875), 'text': 'NON-CE'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
    - Location: {'bbox': (287.0249938964844, 489.5039978027344, 439.09197998046875, 505.99200439453125), 'text': 'Replace these symbols with'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
    - Location: {'bbox': (459.37298583984375, 490.9850158691406, 539.4219970703125, 507.4730224609375), 'text': 'Replace these'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (1275.1920166015625, 865.3579711914062, 1521.800048828125, 877.7239379882812), 'text': 'Replace with below label information and Add MD, M'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (1346.136962890625, 217.39097595214844, 1559.2469482421875, 229.75697326660156), 'text': 'Replace these 2 sections of label with these symbo'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (783.2269897460938, 979.9380493164062, 996.3370361328125, 992.3040161132812), 'text': 'Replace these 2 sections of label with these symbo'}
  - ⚠️ **must_include_nb_number**: Required: Notified body number directly adjacent to CE mark → Actual: CE mark found but NB number not adjacent. Standalone numbers nearby: ['1460', '1460', '3041', '3540', '3540']
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
    - Location: {'bbox': (323.52459716796875, 1027.2801513671875, 545.9368896484375, 1044.382080078125), 'text': 'NO. OF MAXIMUM SPACES (CHARACTERS)'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
    - Location: {'bbox': (653.1255493164062, 72.5596923828125, 711.0254516601562, 90.02651977539062), 'text': 'Tolerance'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1027.420166015625, 1037.4332275390625, 1070.8092041015625, 1047.604248046875), 'text': 'TOLERANCES:'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
    - Location: {'bbox': (1375.7049560546875, 1089.9727783203125, 1419.6171875, 1106.2967529296875), 'text': 'NON-CE'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
    - Location: {'bbox': (287.0249938964844, 489.5039978027344, 439.09197998046875, 505.99200439453125), 'text': 'Replace these symbols with'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
    - Location: {'bbox': (459.37298583984375, 490.9850158691406, 539.4219970703125, 507.4730224609375), 'text': 'Replace these'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (1275.1920166015625, 865.3579711914062, 1521.800048828125, 877.7239379882812), 'text': 'Replace with below label information and Add MD, M'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (1346.136962890625, 217.39097595214844, 1559.2469482421875, 229.75697326660156), 'text': 'Replace these 2 sections of label with these symbo'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (783.2269897460938, 979.9380493164062, 996.3370361328125, 992.3040161132812), 'text': 'Replace these 2 sections of label with these symbo'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
    - Location: {'bbox': (323.52459716796875, 1027.2801513671875, 545.9368896484375, 1044.382080078125), 'text': 'NO. OF MAXIMUM SPACES (CHARACTERS)'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
    - Location: {'bbox': (653.1255493164062, 72.5596923828125, 711.0254516601562, 90.02651977539062), 'text': 'Tolerance'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1027.420166015625, 1037.4332275390625, 1070.8092041015625, 1047.604248046875), 'text': 'TOLERANCES:'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
    - Location: {'bbox': (1375.7049560546875, 1089.9727783203125, 1419.6171875, 1106.2967529296875), 'text': 'NON-CE'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
    - Location: {'bbox': (287.0249938964844, 489.5039978027344, 439.09197998046875, 505.99200439453125), 'text': 'Replace these symbols with'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
    - Location: {'bbox': (459.37298583984375, 490.9850158691406, 539.4219970703125, 507.4730224609375), 'text': 'Replace these'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (1275.1920166015625, 865.3579711914062, 1521.800048828125, 877.7239379882812), 'text': 'Replace with below label information and Add MD, M'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (1346.136962890625, 217.39097595214844, 1559.2469482421875, 229.75697326660156), 'text': 'Replace these 2 sections of label with these symbo'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (783.2269897460938, 979.9380493164062, 996.3370361328125, 992.3040161132812), 'text': 'Replace these 2 sections of label with these symbo'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
    - Location: {'bbox': (323.52459716796875, 1027.2801513671875, 545.9368896484375, 1044.382080078125), 'text': 'NO. OF MAXIMUM SPACES (CHARACTERS)'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
    - Location: {'bbox': (653.1255493164062, 72.5596923828125, 711.0254516601562, 90.02651977539062), 'text': 'Tolerance'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1027.420166015625, 1037.4332275390625, 1070.8092041015625, 1047.604248046875), 'text': 'TOLERANCES:'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
    - Location: {'bbox': (1375.7049560546875, 1089.9727783203125, 1419.6171875, 1106.2967529296875), 'text': 'NON-CE'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
    - Location: {'bbox': (287.0249938964844, 489.5039978027344, 439.09197998046875, 505.99200439453125), 'text': 'Replace these symbols with'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
    - Location: {'bbox': (459.37298583984375, 490.9850158691406, 539.4219970703125, 507.4730224609375), 'text': 'Replace these'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (1275.1920166015625, 865.3579711914062, 1521.800048828125, 877.7239379882812), 'text': 'Replace with below label information and Add MD, M'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (1346.136962890625, 217.39097595214844, 1559.2469482421875, 229.75697326660156), 'text': 'Replace these 2 sections of label with these symbo'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (783.2269897460938, 979.9380493164062, 996.3370361328125, 992.3040161132812), 'text': 'Replace these 2 sections of label with these symbo'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
    - Location: {'bbox': (323.52459716796875, 1027.2801513671875, 545.9368896484375, 1044.382080078125), 'text': 'NO. OF MAXIMUM SPACES (CHARACTERS)'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
    - Location: {'bbox': (653.1255493164062, 72.5596923828125, 711.0254516601562, 90.02651977539062), 'text': 'Tolerance'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1027.420166015625, 1037.4332275390625, 1070.8092041015625, 1047.604248046875), 'text': 'TOLERANCES:'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.88mm (font Tahoma,Bold @ 11.0pt)
    - Location: {'bbox': (1375.7049560546875, 1089.9727783203125, 1419.6171875, 1106.2967529296875), 'text': 'NON-CE'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
    - Location: {'bbox': (287.0249938964844, 489.5039978027344, 439.09197998046875, 505.99200439453125), 'text': 'Replace these symbols with'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.23mm (font Helvetica @ 12.0pt)
    - Location: {'bbox': (459.37298583984375, 490.9850158691406, 539.4219970703125, 507.4730224609375), 'text': 'Replace these'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (1275.1920166015625, 865.3579711914062, 1521.800048828125, 877.7239379882812), 'text': 'Replace with below label information and Add MD, M'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (1346.136962890625, 217.39097595214844, 1559.2469482421875, 229.75697326660156), 'text': 'Replace these 2 sections of label with these symbo'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 3.18mm (font Helvetica @ 9.0pt)
    - Location: {'bbox': (783.2269897460938, 979.9380493164062, 996.3370361328125, 992.3040161132812), 'text': 'Replace these 2 sections of label with these symbo'}
- **Specs passed:** 2
- **Action:** Review and update label to include this element

### ❌ Manufacturer name and full registered address
- **Rule ID:** MDR-address
- **ISO Reference:** ISO 14630 / EU MDR Art. 10(11)
- **Severity:** critical
- **Status:** FAIL
- **Partial evidence:** Manufacturer name and full registered address not found, Texas, address, Irving
- **Spec violations:** 12
  - ⚠️ **must_include**: Required: Must include: street → Actual: 'street' not found in text
  - ⚠️ **must_include**: Required: Must include: city → Actual: 'city' not found in text
  - ⚠️ **must_include**: Required: Must include: street → Actual: 'street' not found in text
  - ⚠️ **must_include**: Required: Must include: city → Actual: 'city' not found in text
  - ⚠️ **must_include**: Required: Must include: street → Actual: 'street' not found in text
  - ⚠️ **must_include**: Required: Must include: city → Actual: 'city' not found in text
  - ⚠️ **must_include**: Required: Must include: street → Actual: 'street' not found in text
  - ⚠️ **must_include**: Required: Must include: city → Actual: 'city' not found in text
  - ⚠️ **must_include**: Required: Must include: street → Actual: 'street' not found in text
  - ⚠️ **must_include**: Required: Must include: city → Actual: 'city' not found in text
  - ⚠️ **must_include**: Required: Must include: street → Actual: 'street' not found in text
  - ⚠️ **must_include**: Required: Must include: city → Actual: 'city' not found in text
- **Specs passed:** 4
- **Action:** Review and update label to include this element

### ⚠️ Product name in official EU member state languages
- **Rule ID:** MDR-multilingual
- **ISO Reference:** EU MDR Art. 10(11)
- **Severity:** major
- **Status:** PARTIAL
- **Partial evidence:** MENTOR(TM), en:, de:, fr:, es:, it: found in label text, Product name in official EU member state languages (en:) present, es:
- **Spec violations:** 6
  - ⚠️ **min_languages**: Required: ≥ 3 languages → Actual: Found 1 languages: ['NO']
  - ⚠️ **min_languages**: Required: ≥ 3 languages → Actual: Found 1 languages: ['NO']
  - ⚠️ **min_languages**: Required: ≥ 3 languages → Actual: Found 2 languages: ['BY', 'NO']
  - ⚠️ **min_languages**: Required: ≥ 3 languages → Actual: Found 2 languages: ['BY', 'NO']
  - ⚠️ **min_languages**: Required: ≥ 3 languages → Actual: Found 2 languages: ['BY', 'NO']
  - ⚠️ **min_languages**: Required: ≥ 3 languages → Actual: Found 2 languages: ['BY', 'NO']
- **Action:** Review and update label to include this element

### ❌ Surface classification category code on label **(NEW in 2024)**
- **Rule ID:** ISO14607-G.2
- **ISO Reference:** ISO 14607:2024, Annex G, Table G.2
- **Severity:** critical
- **Status:** FAIL
- **Partial evidence:** Surface classification category code not found, OTH
- **Specs passed:** 1
- **Action:** Review and update label to include this element

## 📏 Specification Violations Detail

> These violations indicate that while the text content may be present,
> the physical attributes (size, font, position, adjacency) do not meet ISO requirements.

| Rule | Spec Field | Required | Actual | Severity | Page |
|------|-----------|----------|--------|----------|------|
| ISO14607-9.1 | must_include | Must include: sealed | 'sealed' not found in text | critical | 1 |
| ISO14607-9.1 | must_include | Must include: sealed | 'sealed' not found in text | critical | 1 |
| ISO14607-9.1 | must_include | Must include: sealed | 'sealed' not found in text | critical | 1 |
| ISO14607-9.1 | must_include | Must include: sealed | 'sealed' not found in text | critical | 1 |
| ISO14607-9.1 | must_include | Must include: sealed | 'sealed' not found in text | critical | 1 |
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
| ISO14607-11.3c-surface | valid_classifications | Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] | No valid classification code found in text | critical | 1 |
| ISO14607-11.3c-surface | table_ref | Content from Table G.2 must be present | Neither 'Table G.2' nor its content codes found | critical | 1 |
| ISO14607-11.3c-surface | valid_classifications | Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] | No valid classification code found in text | critical | 1 |
| ISO14607-11.3c-surface | table_ref | Content from Table G.2 must be present | Neither 'Table G.2' nor its content codes found | critical | 1 |
| ISO14607-11.3c-surface | valid_classifications | Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] | No valid classification code found in text | critical | 1 |
| ISO14607-11.3c-surface | table_ref | Content from Table G.2 must be present | Neither 'Table G.2' nor its content codes found | critical | 1 |
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
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.37mm (28px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.29mm (27px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.37mm (28px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.37mm (28px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.29mm (27px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.37mm (28px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.37mm (28px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.29mm (27px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.37mm (28px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.37mm (28px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.29mm (27px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.37mm (28px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.37mm (28px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.29mm (27px at 300dpi) | critical | 1 |
| SYM-catalogue | min_height_mm | ≥ 3mm height | 2.37mm (28px at 300dpi) | critical | 1 |
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
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.23mm (font Helvetica @ 12.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.23mm (font Helvetica @ 12.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | must_include_nb_number | Notified body number directly adjacent to CE mark | CE mark found but NB number not adjacent. Standalo | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma,Bold @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.88mm (font Tahoma,Bold @ 11.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.23mm (font Helvetica @ 12.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.23mm (font Helvetica @ 12.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | must_include_nb_number | Notified body number directly adjacent to CE mark | CE mark found but NB number not adjacent. Standalo | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma,Bold @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.88mm (font Tahoma,Bold @ 11.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.23mm (font Helvetica @ 12.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.23mm (font Helvetica @ 12.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma,Bold @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.88mm (font Tahoma,Bold @ 11.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.23mm (font Helvetica @ 12.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.23mm (font Helvetica @ 12.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma,Bold @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.88mm (font Tahoma,Bold @ 11.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.23mm (font Helvetica @ 12.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.23mm (font Helvetica @ 12.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma,Bold @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.88mm (font Tahoma,Bold @ 11.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.23mm (font Helvetica @ 12.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.23mm (font Helvetica @ 12.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 3.18mm (font Helvetica @ 9.0pt) | critical | 1 |
| MDR-address | must_include | Must include: street | 'street' not found in text | critical | 1 |
| MDR-address | must_include | Must include: city | 'city' not found in text | critical | 1 |
| MDR-address | must_include | Must include: street | 'street' not found in text | critical | 1 |
| MDR-address | must_include | Must include: city | 'city' not found in text | critical | 1 |
| MDR-address | must_include | Must include: street | 'street' not found in text | critical | 1 |
| MDR-address | must_include | Must include: city | 'city' not found in text | critical | 1 |
| MDR-address | must_include | Must include: street | 'street' not found in text | critical | 1 |
| MDR-address | must_include | Must include: city | 'city' not found in text | critical | 1 |
| MDR-address | must_include | Must include: street | 'street' not found in text | critical | 1 |
| MDR-address | must_include | Must include: city | 'city' not found in text | critical | 1 |
| MDR-address | must_include | Must include: street | 'street' not found in text | critical | 1 |
| MDR-address | must_include | Must include: city | 'city' not found in text | critical | 1 |
| MDR-multilingual | min_languages | ≥ 3 languages | Found 1 languages: ['NO'] | major | 1 |
| MDR-multilingual | min_languages | ≥ 3 languages | Found 1 languages: ['NO'] | major | 1 |
| MDR-multilingual | min_languages | ≥ 3 languages | Found 2 languages: ['BY', 'NO'] | major | 1 |
| MDR-multilingual | min_languages | ≥ 3 languages | Found 2 languages: ['BY', 'NO'] | major | 1 |
| MDR-multilingual | min_languages | ≥ 3 languages | Found 2 languages: ['BY', 'NO'] | major | 1 |
| MDR-multilingual | min_languages | ≥ 3 languages | Found 2 languages: ['BY', 'NO'] | major | 1 |

## Font Size Violations

| Font | Size | Min Required | Text Preview | Page |
|------|------|-------------|-------------|------|
| Arial | 5.9pt | 6.0pt | Printed on 4/4/2022 | 1 |
| Tahoma | 5.0pt | 6.0pt | LAST SAVED BY: wpaz ON Monday, April 4,  | 1 |

## 🏷️ Symbol Library Comparison

> Compared label content against the Symbol Library database (137 required symbols checked).

| Metric | Value |
|--------|-------|
| Symbols checked | 137 |
| ✅ Found | 29 |
| ⚠️ Partial | 67 |
| ❌ Missing | 41 |
| Score | 46% |

### ✅ Found Symbols

| Symbol Name | Classification | Expected Text | Match Method | Score |
|-------------|---------------|----------------|-------------|-------|
| 171 - STERILE | Standard | Sterile | Text | 100% |
| 0029 - SN | Standard | Serial number | Text | 100% |
| Use by date | Standard | Use-by date | Text | 100% |
| Latex | Standard | Contains or presence of natural rubber l | Text | 86% |
| Do not re-use | Standard | Do not re-use | Text | 100% |
| Non Sterile | Standard | Non-sterile | Text | 100% |
| Double sterile barrier system | Standard | Double Sterile barrier system | Text | 100% |
| eIFU Indicator Horizontal | Standard | NA | Text | 100% |
| Person Identification | Standard | Patient Identification / for implant car | Text | 80% |
| Rx Only horizontal | Standard | TEXT NOT REQUIRED | Text | 100% |
| Rx Only Vertical | Standard | TEXT NOT REQUIRED | Text | 100% |
| Field Intentionally Left Blank | Proprietary - Ethicon |  | Text | 100% |
| China RoHS 10 Orange | Standard | TEXT NOT REQUIRED | Text | 100% |
| China RoHS e Green | Standard | TEXT NOT REQUIRED | Text | 100% |
| China RoHS 50 Orange | Standard | TEXT NOT REQUIRED | Text | 100% |
| China RoHS 5 Orange | Standard | TEXT NOT REQUIRED | Text | 100% |
| PHT DEHP | Standard |  | Text | 100% |
| CE 0120 | Safety Mark | TEXT NOT REQUIRED | Text | 100% |
| PHT | Standard | NA | Text | 100% |
| CE 0123 | Safety Mark | TEXT NOT REQUIRED | Text | 100% |
| Brazil Device Mark | Safety Mark | NA | Text | 100% |
| CE 0344 | Safety Mark | TEXT NOT REQUIRED | Text | 100% |
| CE 1639 | Safety Mark | TEXT NOT REQUIRED | Text | 100% |
| CE Mark | Safety Mark | TEXT NOT REQUIRED | Text | 100% |
| CE 0483 | Safety Mark | TEXT NOT REQUIRED | Text | 100% |
| CE 0543 | Safety Mark | TEXT NOT REQUIRED | Text | 100% |
| TUV Rheinland of North America certification mark  | Safety Mark | TEXT NOT REQUIRED | Text | 100% |
| CE 2797 | Safety Mark |  | Text | 100% |
| CE 0086 | Safety Mark | TEXT NOT REQUIRED | Text | 100% |

### ⚠️ Partially Matched Symbols

| Symbol Name | Expected Text | Actual Match | Details |
|-------------|---------------|-------------|---------|
| 0277 - STERILE Steam or Heat wide | Sterilized using steam or dry heat | or | Partial text match (17%): or |
| Non-Pyrogenic_424 | Non-pyrogenic | non | Partial text match (50%): non |
| Keep away from heat | Keep away from heat | from | Partial text match (25%): from |
| Contains biological material of human origin | Contains biological material of human or | contains; material; of | Partial text match (50%): contains, material, of |
| 0253 - Sterile Fluid Path_for small point size | Sterile fluid path | sterile; fluid | Partial text match (67%): sterile, fluid |
| Date of Manufacture | Date of manufacture | date; of | Partial text match (67%): date, of |
| 0018 - Fragile | Fragile, handle with care | with | Partial text match (25%): with |
| Model Number | Model Number | number | Partial text match (50%): number |
| Health care centre or doctor | Health care centre or doctor / for impla | or; for; implant; name; and; address; of | Partial text match (47%): or, for, implant |
| Sterile barrier system-Single barrier | Single sterile barrier system | sterile; barrier; system | Partial text match (75%): sterile, barrier, system |
| Single sterile barrier system_protective packaging | Single sterile barrier system with prote | sterile; barrier; system; with | Partial text match (50%): sterile, barrier, system |
| Single sterile barrier system_protective packaging | Single sterile barrier system with prote | sterile; barrier; system; with | Partial text match (50%): sterile, barrier, system |
| No latex | Does not contain or presence of natural  | not; contain; or; of; natural; rubber; l | Partial text match (78%): not, contain, or |
| Date | Date / for implant card: Date of Implant | date; for; implant; of | Partial text match (71%): date, for, implant |
| Single patient - multiple use | Single patient multiple use | patient; use | Partial text match (50%): patient, use |
| Temperature Upper Limit | Upper limit of temperature | of | Partial text match (25%): of |
| Contains blood products | Contains human blood or plasma derivativ | contains; or | Partial text match (33%): contains, or |
| EC REP | Authorized representative in the Europea | in; the | Partial text match (25%): in, the |
| Contains biological material of animal origin | Contains biological material of animal o | contains; material; of | Partial text match (50%): contains, material, of |
| Contains hazardous substances | Contains hazardous substances | contains | Partial text match (33%): contains |
| Do Not Resterilize | Do not resterilize | do; not | Partial text match (67%): do, not |
| Consult instruction for use I book | Consult instructions for use or consult  | for; use; or | Partial text match (50%): for, use, or |
| LOT | Batch code | code | Partial text match (50%): code |
| Country of Manufacture | Country of manufacture | country; of | Partial text match (67%): country, of |
| Packaging damaged | Do not use if package is damaged and con | do; not; use; if; is; and; for | Partial text match (67%): do, not, use |
| Contains a medicinal substance | Contains a medicinal substance | contains | Partial text match (33%): contains |
| Temperature lower limit | Lower limit of temperature | of | Partial text match (25%): of |
| Patient information website | Patient information website / for implan | patient; information; for; implant | Partial text match (60%): patient, information, for |
| Cataloge number | Catalogue number | number | Partial text match (50%): number |
| Field Intentionally Left Blank | Sterile &amp; Nonpyro | sterile | Partial text match (50%): sterile |
| Sterile EO or R | Method of Sterilization: Ethylene Oxide  | of; or | Partial text match (29%): of, or |
| CAUTION, patient weight limit | CAUTION, patient weight limit | patient | Partial text match (25%): patient |
| Customer service phone | For customer service or to return produc | for; or; to; product; in; usa; of | Partial text match (37%): for, or, to |
| For Removal | For removal, turn knob 360° two times | for; to; release; the; from | Partial text match (31%): for, to, release |
| Test Script 100697719 - ACCLM Adoption Readiness A | [Product type] from responsible sources | product; from | Partial text match (40%): product, from |
| Dyed bidirectional barbed absorbable device | Dyed – Bidirectional – Barbed – Absorbab | tissue | Partial text match (12%): tissue |
| No Stepping on Surface | No stepping on surface | no; on | Partial text match (50%): no, on |
| Open Close | Open/Close | to; and | Partial text match (21%): to, and |
| Ablation mode | Denotes a procedure performed only in Ab | only; in | Partial text match (29%): only, in |
| Undyed bidirectional barbed absorbable device | Undyed – Bidirectional – Barbed – Absorb | tissue | Partial text match (12%): tissue |
| Ablation and Surgical mode icon | Denotes a procedure performed using both | and | Partial text match (11%): and |
| Surgical mode icon | Denotes a procedure performed only in Su | only; in | Partial text match (29%): only, in |
| 0279 - Anchored_Undyed_Abs_Mono | Undyed – Unidirectional – Barbed - Absor | tissue | Partial text match (12%): tissue |
| 98 - Center Point Spatula | Center Point Spatula Needle | needle | Partial text match (25%): needle |
| Partially Absorbable Mesh Device with Absorbable L | Partially Absorbable Mesh Device with Ab | with | Partial text match (14%): with |
| Advanced Hemostasis | Advanced Hemostasis for HARMONIC™ Device | for | Partial text match (20%): for |
| Permanent Mesh Device with Absorbable Layer | Permanent Mesh Device with Absorbable La | with | Partial text match (17%): with |
| Maximum_Energy Button | Maximum (Energy Button) for HARMONIC™ De | for | Partial text match (17%): for |
| 0204 - Anchored_Dyed_Abs_Mono | Dyed – Unidirectional – Barbed – Absorba | tissue | Partial text match (12%): tissue |
| INTERCEED Absorbable Adhesion Barrier | Absorbable Adhesion Barrier | barrier | Partial text match (33%): barrier |
| System Preferences | System Preferences | system | Partial text match (50%): system |
| Generator Footswitch Receptacle | This symbol indicates the receptacle to  | this; symbol; the; to; be | Partial text match (46%): this, symbol, the |
| Dyed Bidirectional Barbs Non-Absorbable | Dyed &ndash; Bidirectional &ndash; Barbe | non; tissue | Partial text match (15%): non, tissue |
| For Use with GRAY Hand Piece Only | For Use with GRAY Hand Piece ONLY | for; use; with; only | Partial text match (57%): for, use, with |
| Dyed Unidirectional Barbs Non-Absorbable | Dyed &ndash; Unidirectional &ndash; Barb | non; tissue | Partial text match (15%): non, tissue |
| Minimum_Energy Button | Minimum (Energy Button) for HARMONIC™ De | for | Partial text match (17%): for |
| Regulatory Compliance Mark | Regulatory Compliance Mark | mark | Partial text match (33%): mark |
| Serial Interface | Serial Interface (for service use only) | serial; for; use; only | Partial text match (67%): serial, for, use |
| For Use with BLUE Hand Piece ONLY | For Use with BLUE Hand Piece ONLY | for; use; with; only | Partial text match (57%): for, use, with |
| No Separate Handpiece Required | No Separate Hand Piece Required | no | Partial text match (20%): no |
| Mini map placement right | Mini map placement right | mini | Partial text match (25%): mini |
| Mini map placement left | Mini map placement left | mini | Partial text match (25%): mini |
| Refer to instruction manual/booklet | Refer to instruction manual/booklet | to; action | Partial text match (20%): to, action |
| Mentor MplusCO2 | SILTEX™ Round Moderate Plus Profile Gel  | profile; gel; breast; implant | Partial text match (40%): profile, gel, breast |
| Field Intentionally Left Blank | Selection 1: Text required if product do | text; if; product; an; implant; date; fo | Partial text match (58%): text, if, product |
| Mentor HPCO2 | SILTEX™ Round High Profile Gel Breast Im | high; profile; gel; breast; implant | Partial text match (56%): high, profile, gel |
| Mentor MPCO2 | SILTEX™ Round Moderate Profile Gel Breas | profile; gel; breast; implant | Partial text match (44%): profile, gel, breast |

### ❌ Missing Symbols

| Symbol Name | Classification | Expected Text | Regulation | Action |
|-------------|---------------|----------------|-----------|--------|
| Biological risk | Standard | Biological risks | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| Caution | Standard | Caution | ID: REG_0059.pdf
Title: ISO 7000 Graphical symbols for use o | Add to label |
| Unique Device Identifier | Standard | Unique Device Identifier | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| Manufacturer | Standard | Manufacturer | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| Humidity limitation | Standard | Humidity limitation | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| Medical Device | Standard | Medical Device | ID: REG_0088.pdf
Title: MDCG 2019-8 Medical Devices: Guidanc | Add to label |
| Temperature limit | Standard | Temperature limit | ID: REG_0059.pdf
Title: ISO 7000 Graphical symbols for use o | Add to label |
| 0022 - Keep Dry | Standard | Keep dry | ID: REG_0059.pdf
Title: ISO 7000 Graphical symbols for use o | Add to label |
| 0276 - STERILE R wide | Standard | Sterilized using irradiation | ID: REG_0059.pdf
Title: ISO 7000 Graphical symbols for use o | Add to label |
| STERILE Asceptic wide | Standard | Sterilized using aseptic processing tech | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| STERILE EO wide | Standard | Sterilized using ethylene oxide | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| Distributor | Standard | Distributor | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| Importer | Standard | Importer | ID: REG_0082.pdf
Title: ISO 15223-1 Medical devices — Symbol | Add to label |
| Atmospheric pressure limitation | Standard | Atmospheric pressure limitation | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| Sterilized using vapor phase hydrogen peroxide | Standard | Sterilized using vaporized hydrogen pero | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| EU REP | Standard | Authorized representative | ID: REG_0082.pdf
Title: ISO 15223-1 Medical devices — Symbol | Add to label |
| US REP | Standard | Authorized representative | ID: REG_0082.pdf
Title: ISO 15223-1 Medical devices — Symbol | Add to label |
| Caution, hot surface | Standard | Caution, hot surface | ID: REG_0063.pdf
Title: IEC 60417 Graphical Symbols for Use  | Add to label |
| Absorbable Mesh Device | Proprietary - Ethicon | Absorbable Mesh Device | — | Add to label |
| Partially Absorbable Mesh Device | Proprietary - Ethicon | Partially Absorbable Mesh Device | — | Add to label |
| Immediate stop. laser light source | Standard | Immediate stop, laser light source | ID: REG_0059.pdf
Title: ISO 7000 Graphical symbols for use o | Add to label |
| 0352 - Permanent Mesh Device_292 | Proprietary - Ethicon | Permanent Mesh Device | — | Add to label |
| Advanced Settings | Proprietary - Ethicon | Advanced Settings | — | Add to label |
| Pierced firm round cornered pledget | Product Graphic | Pierced firm round cornered pledget | — | Add to label |
| Gripping Surface Technology | Product Trademark | Gripping Surface Technology | — | Add to label |
| SURGICEL Absorbable Hemostat | Proprietary - Ethicon | Absorbable Hemostat | — | Add to label |
| Pierced soft round cornered pledget | Product Graphic | Pierced soft round cornered pledget | — | Add to label |
| Pierced firm square cornered pledget | Product Graphic | Pierced firm square cornered pledget | — | Add to label |
| Maintenance | Standard | Maintenance | ID: REG_0059.pdf
Title: ISO 7000 Graphical symbols for use o | Add to label |
| Selection; affirmative acknowledgement; success; A | Standard | Selection; affirmative acknowledgement;  | ID: REG_0063.pdf
Title: IEC 60417 Graphical Symbols for Use  | Add to label |
| Partially Absorbable Mesh Device Undyed | Proprietary - Ethicon | Partially Absorbable Mesh Device | — | Add to label |
| Pierced soft square cornered pledget | Product Graphic | Pierced soft square cornered pledget | — | Add to label |
| Cloud connectivity upload successful | Proprietary - Ethicon | Cloud connectivity upload successful | — | Add to label |
| Bell cancel | Standard | Bell cancel | ID: REG_0063.pdf
Title: IEC 60417 Graphical Symbols for Use  | Add to label |
| Advanced setting | Proprietary - Ethicon | Advanced setting | — | Add to label |
| Electrostatic sensitive devices | Standard | Electrostatic sensitive devices | ID: REG_0063.pdf
Title: IEC 60417 Graphical Symbols for Use  | Add to label |
| PACS connection actively receiving | Proprietary - Ethicon | PACS connection actively receiving | — | Add to label |
| Reception = full | Proprietary - Ethicon | Reception = full | — | Add to label |
| Port placement | Proprietary - Ethicon | Port placement | — | Add to label |
| Power error indication | Proprietary - Ethicon | Indicates a reflected power error has oc | — | Add to label |
| Refresh | Proprietary - Ethicon | Refresh | — | Add to label |

## Page-by-Page OCR Details

### Page 1
- Words detected: 726
- Text length: 4870 chars
- Barcodes: 3
  - CODE128: SERNO
  - CODE128: 1234ABCD01
  - CODE128: LOTNO
- Layout zones: 16
