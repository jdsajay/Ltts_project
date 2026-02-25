# Compliance Report: DRWG107601_Rev D (1)

**Generated:** 2026-02-25 09:11
**Source:** DRWG107601_Rev D (1).pdf
**Pages:** 1

## Summary

| Metric | Value |
|--------|-------|
| **Status** | **NON-COMPLIANT** |
| Score | 29.4% |
| Rules checked | 28 |
| ✅ Passed | 4 |
| ⚠️ Partial | 13 |
| ❌ Failed | 11 |
| Critical gaps | 18 |
| New 2024 gaps | 2 |
| 📏 Spec violations | 43 |
| Rules with spec failures | 15 |

## Rule-by-Rule Results

| # | Status | Rule | ISO Ref | Severity | Evidence |
|---|--------|------|---------|----------|----------|
| 1 | ❌ | Implant shall be supplied in sealed sterile packaging | 9.1 | critical | — |
| 2 | ⚠️ | Double packaging system — inner and outer pack | 9.2 | major | outer |
| 3 | ❌ | Instructions for use shall accompany the implant | 10.1 | critical | — |
| 4 | ❌ | Labels shall comply with ISO 14630 and ISO 15223-1 | 11.1 | critical | — |
| 5 | ⚠️ | Nominal volume stated on the unit container label | 11.2 | critical | volume |
| 6 | ❌ | Implant type/model stated on the unit container | 11.2 | critical | — |
| 7 | ⚠️ | Implant dimensions: width, height/diameter, projection | 11.3 a) | critical | cm, pattern:10.0cm, projection |
| 8 | ⚠️ | Volume also stated on the implant label (not just container) | 11.3 a) | critical | volume |
| 9 | ❌ | Description of the implant shell(s) | 11.3 b) | major | — |
| 10 | ❌ | Surface classification per normative Annex G, Table G.2 🆕 | 11.3 c) | critical | — |
| 11 | ❌ | Description of the implant fill material | 11.3 d) | major | — |
| 12 | ✅ | Shelf life / use-by date on packaging | 11.4 | critical | expir, shelf life, EXPDATE |
| 13 | ❌ | Unique Device Identifier (UDI) on label | 11.5 | critical | — |
| 14 | ⚠️ | UDI carrier (barcode or 2D DataMatrix) | 11.5 | critical | GTIN |
| 15 | ⚠️ | Manufacturer symbol (factory icon) | ISO 15223-1:2021, 5.1.1 | critical | Mentor |
| 16 | ⚠️ | Date of manufacture symbol | ISO 15223-1:2021, 5.1.3 | critical | MFGDATE |
| 17 | ✅ | Use-by date / expiration symbol | ISO 15223-1:2021, 5.1.4 | critical | expir, EXPDATE |
| 18 | ✅ | Batch code / LOT number symbol | ISO 15223-1:2021, 5.1.5 | critical | lot, LOTNO, LOT |
| 19 | ✅ | Serial number symbol | ISO 15223-1:2021, 5.1.6 | critical | SERNO, serial, SN |
| 20 | ⚠️ | Catalogue / reference number symbol | ISO 15223-1:2021, 5.1.7 | critical | REF |
| 21 | ❌ | Sterilization method symbol | ISO 15223-1:2021, 5.2.1–5.2.8 | critical | — |
| 22 | ❌ | Do not reuse / single use symbol | ISO 15223-1:2021, 5.4.2 | major | — |
| 23 | ⚠️ | CE marking with notified body number | EU MDR 2017/745, Art. 20 | critical | CE |
| 24 | ⚠️ | Manufacturer name and full registered address | ISO 14630 / EU MDR Art. 10(11) | critical | Irving, Texas |
| 25 | ⚠️ | Product name in official EU member state languages | EU MDR Art. 10(11) | major | es: |
| 26 | ⚠️ | GTIN barcode (GS1-128 or 2D DataMatrix) | EU MDR / UDI Regulation | critical | GTIN |
| 27 | ⚠️ | Surface classification category code on label 🆕 | ISO 14607:2024, Annex G, Table G.2 | critical | OTH |
| 28 | ❌ | Patient implant card included with product | ISO 14607:2024, Annex H | major | — |

## Compliance Gaps

### ❌ Implant shall be supplied in sealed sterile packaging
- **Rule ID:** ISO14607-9.1
- **ISO Reference:** 9.1
- **Severity:** critical
- **Status:** FAIL
- **Spec violations:** 3
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **must_include**: Required: Must include: sterile → Actual: 'sterile' not found in text
  - ⚠️ **must_include**: Required: Must include: sealed → Actual: 'sealed' not found in text
- **Action:** Review and update label to include this element

### ⚠️ Double packaging system — inner and outer pack
- **Rule ID:** ISO14607-9.2
- **ISO Reference:** 9.2
- **Severity:** major
- **Status:** PARTIAL
- **Partial evidence:** outer
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ❌ Instructions for use shall accompany the implant
- **Rule ID:** ISO14607-10.1
- **ISO Reference:** 10.1
- **Severity:** critical
- **Status:** FAIL
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ❌ Labels shall comply with ISO 14630 and ISO 15223-1
- **Rule ID:** ISO14607-11.1
- **ISO Reference:** 11.1
- **Severity:** critical
- **Status:** FAIL
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ⚠️ Nominal volume stated on the unit container label
- **Rule ID:** ISO14607-11.2-volume
- **ISO Reference:** 11.2
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** volume
- **Spec violations:** 8
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '225cc')
    - Location: {'bbox': (195.9160614013672, 92.76905059814453, 226.06602478027344, 109.87100219726562), 'text': '225cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '300cc')
    - Location: {'bbox': (195.92784118652344, 107.09326934814453, 226.0778045654297, 124.19522094726562), 'text': '300cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '375cc')
    - Location: {'bbox': (195.9396209716797, 121.41748809814453, 226.08958435058594, 138.51943969726562), 'text': '375cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '475cc')
    - Location: {'bbox': (195.95140075683594, 135.8946533203125, 226.1013641357422, 152.99661254882812), 'text': '475cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '500cc')
    - Location: {'bbox': (195.9631805419922, 150.371826171875, 226.11314392089844, 167.47378540039062), 'text': '500cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '600cc')
    - Location: {'bbox': (195.9748992919922, 164.8485107421875, 226.12486267089844, 181.95046997070312), 'text': '600cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '750cc')
    - Location: {'bbox': (195.98667907714844, 179.32568359375, 226.1366424560547, 196.42764282226562), 'text': '750cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
    - Location: {'bbox': (195.9984588623047, 193.80291748046875, 226.14842224121094, 210.90487670898438), 'text': '850cc'}
- **Specs passed:** 10
- **Action:** Review and update label to include this element

### ❌ Implant type/model stated on the unit container
- **Rule ID:** ISO14607-11.2-type
- **ISO Reference:** 11.2
- **Severity:** critical
- **Status:** FAIL
- **Specs passed:** 2
- **Action:** Review and update label to include this element

### ⚠️ Implant dimensions: width, height/diameter, projection
- **Rule ID:** ISO14607-11.3a-dimensions
- **ISO Reference:** 11.3 a)
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** cm, pattern:10.0cm, projection
- **Spec violations:** 1
  - ⚠️ **must_include**: Required: Must include one of: width OR diameter → Actual: None of [width, diameter] found in text
- **Specs passed:** 22
- **Action:** Review and update label to include this element

### ⚠️ Volume also stated on the implant label (not just container)
- **Rule ID:** ISO14607-11.3a-volume-label
- **ISO Reference:** 11.3 a)
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** volume
- **Spec violations:** 8
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '225cc')
    - Location: {'bbox': (195.9160614013672, 92.76905059814453, 226.06602478027344, 109.87100219726562), 'text': '225cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '300cc')
    - Location: {'bbox': (195.92784118652344, 107.09326934814453, 226.0778045654297, 124.19522094726562), 'text': '300cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '375cc')
    - Location: {'bbox': (195.9396209716797, 121.41748809814453, 226.08958435058594, 138.51943969726562), 'text': '375cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '475cc')
    - Location: {'bbox': (195.95140075683594, 135.8946533203125, 226.1013641357422, 152.99661254882812), 'text': '475cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '500cc')
    - Location: {'bbox': (195.9631805419922, 150.371826171875, 226.11314392089844, 167.47378540039062), 'text': '500cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '600cc')
    - Location: {'bbox': (195.9748992919922, 164.8485107421875, 226.12486267089844, 181.95046997070312), 'text': '600cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '750cc')
    - Location: {'bbox': (195.98667907714844, 179.32568359375, 226.1366424560547, 196.42764282226562), 'text': '750cc'}
  - ⚠️ **font_style**: Required: Required: bold → Actual: Found: regular (font: Tahoma, text: '850cc')
    - Location: {'bbox': (195.9984588623047, 193.80291748046875, 226.14842224121094, 210.90487670898438), 'text': '850cc'}
- **Specs passed:** 10
- **Action:** Review and update label to include this element

### ❌ Description of the implant shell(s)
- **Rule ID:** ISO14607-11.3b-shell-desc
- **ISO Reference:** 11.3 b)
- **Severity:** major
- **Status:** FAIL
- **Spec violations:** 2
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
  - ⚠️ **must_include**: Required: Must include one of: shell OR barrier OR layer → Actual: None of [shell, barrier, layer] found in text
- **Action:** Review and update label to include this element

### ❌ Surface classification per normative Annex G, Table G.2 **(NEW in 2024)**
- **Rule ID:** ISO14607-11.3c-surface
- **ISO Reference:** 11.3 c)
- **Severity:** critical
- **Status:** FAIL
- **Spec violations:** 2
  - ⚠️ **valid_classifications**: Required: Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] → Actual: No valid classification code found in text
  - ⚠️ **table_ref**: Required: Content from Table G.2 must be present → Actual: Neither 'Table G.2' nor its content codes found
- **Action:** Review and update label to include this element

### ❌ Description of the implant fill material
- **Rule ID:** ISO14607-11.3d-fill
- **ISO Reference:** 11.3 d)
- **Severity:** major
- **Status:** FAIL
- **Spec violations:** 1
  - ⚠️ **must_include**: Required: Must include one of: gel OR saline OR fill → Actual: None of [gel, saline, fill] found in text
- **Specs passed:** 2
- **Action:** Review and update label to include this element

### ❌ Unique Device Identifier (UDI) on label
- **Rule ID:** ISO14607-11.5-udi
- **ISO Reference:** 11.5
- **Severity:** critical
- **Status:** FAIL
- **Spec violations:** 2
  - ⚠️ **min_height_mm**: Required: ≥ 2mm height → Actual: Element not found — cannot measure height
  - ⚠️ **min_font_size_pt**: Required: ≥ 6pt font size → Actual: No matching font spans found
- **Action:** Review and update label to include this element

### ⚠️ UDI carrier (barcode or 2D DataMatrix)
- **Rule ID:** ISO14607-11.5-udi-carrier
- **ISO Reference:** 11.5
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** GTIN
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ⚠️ Manufacturer symbol (factory icon)
- **Rule ID:** SYM-manufacturer
- **ISO Reference:** ISO 15223-1:2021, 5.1.1
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** Mentor
- **Spec violations:** 4
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
- **Partial evidence:** MFGDATE
- **Spec violations:** 1
  - ⚠️ **must_be_adjacent_to**: Required: Must be within 10mm of 'manufacture' → Actual: Adjacent element 'manufacture' not found
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ⚠️ Catalogue / reference number symbol
- **Rule ID:** SYM-catalogue
- **ISO Reference:** ISO 15223-1:2021, 5.1.7
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** REF
- **Specs passed:** 3
- **Action:** Review and update label to include this element

### ❌ Sterilization method symbol
- **Rule ID:** SYM-sterilization
- **ISO Reference:** ISO 15223-1:2021, 5.2.1–5.2.8
- **Severity:** critical
- **Status:** FAIL
- **Spec violations:** 1
  - ⚠️ **valid_methods**: Required: Must indicate valid sterilization method: ['5.2.1: Sterile — general', '5.2.4: Sterile — irradiation', '5.2.5: Sterile — ethylene oxide'] → Actual: No recognized sterilization method found in text
- **Action:** Review and update label to include this element

### ❌ Do not reuse / single use symbol
- **Rule ID:** SYM-single-use
- **ISO Reference:** ISO 15223-1:2021, 5.4.2
- **Severity:** major
- **Status:** FAIL
- **Spec violations:** 1
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: Element not found — cannot measure height
- **Action:** Review and update label to include this element

### ⚠️ CE marking with notified body number
- **Rule ID:** SYM-ce-mark
- **ISO Reference:** EU MDR 2017/745, Art. 20
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** CE
- **Spec violations:** 5
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma @ 11.8pt)
    - Location: {'bbox': (323.52459716796875, 1027.2801513671875, 545.9368896484375, 1044.382080078125), 'text': 'NO. OF MAXIMUM SPACES (CHARACTERS)'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.16mm (font Tahoma,Bold @ 11.8pt)
    - Location: {'bbox': (653.1255493164062, 72.5596923828125, 711.0254516601562, 90.02651977539062), 'text': 'Tolerance'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 2.43mm (font Tahoma @ 6.9pt)
    - Location: {'bbox': (1014.4857177734375, 1038.226318359375, 1057.874755859375, 1048.3973388671875), 'text': 'TOLERANCES:'}
  - ⚠️ **min_height_mm**: Required: ≥ 5mm height → Actual: 4.23mm (font Tahoma,Bold @ 12.0pt)
    - Location: {'bbox': (1414.6541748046875, 1088.9019775390625, 1462.635986328125, 1106.7099609375), 'text': 'NON-CE'}
  - ⚠️ **must_include_nb_number**: Required: Notified body number directly adjacent to CE mark → Actual: CE mark found but NB number not adjacent. Standalone numbers nearby: ['1460', '3540', '5731', '6000']
- **Action:** Review and update label to include this element

### ⚠️ Manufacturer name and full registered address
- **Rule ID:** MDR-address
- **ISO Reference:** ISO 14630 / EU MDR Art. 10(11)
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** Irving, Texas
- **Spec violations:** 3
  - ⚠️ **must_include**: Required: Must include: street → Actual: 'street' not found in text
  - ⚠️ **must_include**: Required: Must include: city → Actual: 'city' not found in text
  - ⚠️ **must_include**: Required: Must include: country → Actual: 'country' not found in text
- **Specs passed:** 3
- **Action:** Review and update label to include this element

### ⚠️ Product name in official EU member state languages
- **Rule ID:** MDR-multilingual
- **ISO Reference:** EU MDR Art. 10(11)
- **Severity:** major
- **Status:** PARTIAL
- **Partial evidence:** es:
- **Spec violations:** 1
  - ⚠️ **min_languages**: Required: ≥ 3 languages → Actual: Found 1 languages: ['BY']
- **Action:** Review and update label to include this element

### ⚠️ GTIN barcode (GS1-128 or 2D DataMatrix)
- **Rule ID:** MDR-gtin
- **ISO Reference:** EU MDR / UDI Regulation
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** GTIN
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ⚠️ Surface classification category code on label **(NEW in 2024)**
- **Rule ID:** ISO14607-G.2
- **ISO Reference:** ISO 14607:2024, Annex G, Table G.2
- **Severity:** critical
- **Status:** PARTIAL
- **Partial evidence:** OTH
- **Specs passed:** 1
- **Action:** Review and update label to include this element

### ❌ Patient implant card included with product
- **Rule ID:** ISO14607-H
- **ISO Reference:** ISO 14607:2024, Annex H
- **Severity:** major
- **Status:** FAIL
- **Specs passed:** 1
- **Action:** Review and update label to include this element

## 📏 Specification Violations Detail

> These violations indicate that while the text content may be present,
> the physical attributes (size, font, position, adjacency) do not meet ISO requirements.

| Rule | Spec Field | Required | Actual | Severity | Page |
|------|-----------|----------|--------|----------|------|
| ISO14607-9.1 | min_font_size_pt | ≥ 6pt font size | No matching font spans found | critical | 1 |
| ISO14607-9.1 | must_include | Must include: sterile | 'sterile' not found in text | critical | 1 |
| ISO14607-9.1 | must_include | Must include: sealed | 'sealed' not found in text | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '225cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '300cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '375cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '475cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '500cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '600cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '750cc') | critical | 1 |
| ISO14607-11.2-volume | font_style | Required: bold | Found: regular (font: Tahoma, text: '850cc') | critical | 1 |
| ISO14607-11.3a-dimensions | must_include | Must include one of: width OR diameter | None of [width, diameter] found in text | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '225cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '300cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '375cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '475cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '500cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '600cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '750cc') | critical | 1 |
| ISO14607-11.3a-volume-label | font_style | Required: bold | Found: regular (font: Tahoma, text: '850cc') | critical | 1 |
| ISO14607-11.3b-shell-desc | min_font_size_pt | ≥ 6pt font size | No matching font spans found | major | 1 |
| ISO14607-11.3b-shell-desc | must_include | Must include one of: shell OR barrier OR layer | None of [shell, barrier, layer] found in text | major | 1 |
| ISO14607-11.3c-surface | valid_classifications | Must contain one of: ['NTX', 'SLC', 'SLO', 'CRC', 'CRO'] | No valid classification code found in text | critical | 1 |
| ISO14607-11.3c-surface | table_ref | Content from Table G.2 must be present | Neither 'Table G.2' nor its content codes found | critical | 1 |
| ISO14607-11.3d-fill | must_include | Must include one of: gel OR saline OR fill | None of [gel, saline, fill] found in text | major | 1 |
| ISO14607-11.5-udi | min_height_mm | ≥ 2mm height | Element not found — cannot measure height | critical | 1 |
| ISO14607-11.5-udi | min_font_size_pt | ≥ 6pt font size | No matching font spans found | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-manufacturer | min_height_mm | ≥ 3mm height | 2.47mm (font Tahoma @ 7.0pt) | critical | 1 |
| SYM-manufacturer | must_be_adjacent_to | Must be within 10mm of 'manufacturer' | Adjacent element 'manufacturer' not found | critical | 1 |
| SYM-date-manufacture | must_be_adjacent_to | Must be within 10mm of 'manufacture' | Adjacent element 'manufacture' not found | critical | 1 |
| SYM-sterilization | valid_methods | Must indicate valid sterilization method: ['5.2.1: Sterile — general', '5.2.4: Sterile — irradiation', '5.2.5: Sterile — ethylene oxide'] | No recognized sterilization method found in text | critical | 1 |
| SYM-single-use | min_height_mm | ≥ 5mm height | Element not found — cannot measure height | major | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.16mm (font Tahoma,Bold @ 11.8pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 2.43mm (font Tahoma @ 6.9pt) | critical | 1 |
| SYM-ce-mark | min_height_mm | ≥ 5mm height | 4.23mm (font Tahoma,Bold @ 12.0pt) | critical | 1 |
| SYM-ce-mark | must_include_nb_number | Notified body number directly adjacent to CE mark | CE mark found but NB number not adjacent. Standalo | critical | 1 |
| MDR-address | must_include | Must include: street | 'street' not found in text | critical | 1 |
| MDR-address | must_include | Must include: city | 'city' not found in text | critical | 1 |
| MDR-address | must_include | Must include: country | 'country' not found in text | critical | 1 |
| MDR-multilingual | min_languages | ≥ 3 languages | Found 1 languages: ['BY'] | major | 1 |

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
| ✅ Found | 26 |
| ⚠️ Partial | 74 |
| ❌ Missing | 37 |
| Score | 46% |

### ✅ Found Symbols

| Symbol Name | Classification | Expected Text | Match Method | Score |
|-------------|---------------|----------------|-------------|-------|
| 0029 - SN | Standard | Serial number | Text | 100% |
| Use by date | Standard | Use-by date | Text | 100% |
| Manufacturer | Standard | Manufacturer | Visual | 95% |
| Do not re-use | Standard | Do not re-use | Text | 100% |
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
| Contains biological material of human origin | Contains biological material of human or | material; of | Partial text match (33%): material, of |
| Date of Manufacture | Date of manufacture | date; of | Partial text match (67%): date, of |
| 0018 - Fragile | Fragile, handle with care | with | Partial text match (25%): with |
| Model Number | Model Number | number | Partial text match (50%): number |
| Health care centre or doctor | Health care centre or doctor / for impla | or; for; implant; name; and; of; the | Partial text match (41%): or, for, implant |
| Single sterile barrier system_protective packaging | Single sterile barrier system with prote | with | Partial text match (12%): with |
| Caution | Caution |  | Text: not found → Visual: Weak visual match (78%) at scale 0 |
| Single sterile barrier system_protective packaging | Single sterile barrier system with prote | with | Partial text match (12%): with |
| No latex | Does not contain or presence of natural  | not; contain; or; of; natural; rubber; l | Partial text match (78%): not, contain, or |
| Date | Date / for implant card: Date of Implant | date; for; implant; of | Partial text match (71%): date, for, implant |
| Single patient - multiple use | Single patient multiple use | patient; use | Partial text match (50%): patient, use |
| Unique Device Identifier | Unique Device Identifier | device | Partial text match (33%): device |
| Temperature Upper Limit | Upper limit of temperature | of | Partial text match (25%): of |
| Medical Device | Medical Device | device | Partial text match (50%): device |
| Latex | Contains or presence of natural rubber l | or; of; natural; rubber; latex | Partial text match (71%): or, of, natural |
| Temperature limit | Temperature limit |  | Text: not found → Visual: Weak visual match (66%) at scale 0 |
| Non Sterile | Non-sterile | non | Partial text match (50%): non |
| Contains blood products | Contains human blood or plasma derivativ | or | Partial text match (17%): or |
| EC REP | Authorized representative in the Europea | in; the | Partial text match (25%): in, the |
| 0022 - Keep Dry | Keep dry |  | Text: not found → Visual: Weak visual match (71%) at scale 0 |
| Contains biological material of animal origin | Contains biological material of animal o | material; of | Partial text match (33%): material, of |
| Do Not Resterilize | Do not resterilize | do; not | Partial text match (67%): do, not |
| Consult instruction for use I book | Consult instructions for use or consult  | for; use; or | Partial text match (50%): for, use, or |
| Country of Manufacture | Country of manufacture | of | Partial text match (33%): of |
| Packaging damaged | Do not use if package is damaged and con | do; not; use; if; is; and; for | Partial text match (67%): do, not, use |
| Temperature lower limit | Lower limit of temperature | of | Partial text match (25%): of |
| Patient information website | Patient information website / for implan | patient; information; for; implant | Partial text match (60%): patient, information, for |
| Cataloge number | Catalogue number | number | Partial text match (50%): number |
| Sterile EO or R | Method of Sterilization: Ethylene Oxide  | of; or | Partial text match (29%): of, or |
| CAUTION, patient weight limit | CAUTION, patient weight limit | patient | Partial text match (25%): patient |
| Customer service phone | For customer service or to return produc | for; or; to; product; 800; 5731; in; usa | Partial text match (52%): for, or, to |
| For Removal | For removal, turn knob 360° two times | for; to; release; the; device | Partial text match (31%): for, to, release |
| Test Script 100697719 - ACCLM Adoption Readiness A | [Product type] from responsible sources | product | Partial text match (20%): product |
| Dyed bidirectional barbed absorbable device | Dyed – Bidirectional – Barbed – Absorbab | tissue; device | Partial text match (25%): tissue, device |
| Absorbable Mesh Device | Absorbable Mesh Device | device | Partial text match (33%): device |
| No Stepping on Surface | No stepping on surface | no; on | Partial text match (50%): no, on |
| Open Close | Open/Close | to; and; device | Partial text match (29%): to, and, device |
| Ablation mode | Denotes a procedure performed only in Ab | only; in | Partial text match (29%): only, in |
| Partially Absorbable Mesh Device | Partially Absorbable Mesh Device | device | Partial text match (25%): device |
| Undyed bidirectional barbed absorbable device | Undyed – Bidirectional – Barbed – Absorb | tissue; device | Partial text match (25%): tissue, device |
| Ablation and Surgical mode icon | Denotes a procedure performed using both | and | Partial text match (11%): and |
| Surgical mode icon | Denotes a procedure performed only in Su | only; in | Partial text match (29%): only, in |
| 0279 - Anchored_Undyed_Abs_Mono | Undyed – Unidirectional – Barbed - Absor | tissue; device | Partial text match (25%): tissue, device |
| 98 - Center Point Spatula | Center Point Spatula Needle | center; needle | Partial text match (50%): center, needle |
| Partially Absorbable Mesh Device with Absorbable L | Partially Absorbable Mesh Device with Ab | device; with | Partial text match (29%): device, with |
| Advanced Hemostasis | Advanced Hemostasis for HARMONIC™ Device | for | Partial text match (20%): for |
| Permanent Mesh Device with Absorbable Layer | Permanent Mesh Device with Absorbable La | device; with | Partial text match (33%): device, with |
| Maximum_Energy Button | Maximum (Energy Button) for HARMONIC™ De | maximum; for | Partial text match (33%): maximum, for |
| 0352 - Permanent Mesh Device_292 | Permanent Mesh Device | device | Partial text match (33%): device |
| Advanced Settings | Advanced Settings |  | Text: not found → Visual: Weak visual match (62%) at scale 0 |
| 0204 - Anchored_Dyed_Abs_Mono | Dyed – Unidirectional – Barbed – Absorba | tissue; device | Partial text match (25%): tissue, device |
| Pierced firm round cornered pledget | Pierced firm round cornered pledget |  | Text: not found → Visual: Weak visual match (75%) at scale 0 |
| System Preferences | System Preferences |  | Text: not found → Visual: Weak visual match (66%) at scale 0 |
| Generator Footswitch Receptacle | This symbol indicates the receptacle to  | this; the; to; be | Partial text match (38%): this, the, to |
| Dyed Bidirectional Barbs Non-Absorbable | Dyed &ndash; Bidirectional &ndash; Barbe | non; tissue; device | Partial text match (23%): non, tissue, device |
| Pierced firm square cornered pledget | Pierced firm square cornered pledget |  | Text: not found → Visual: Weak visual match (78%) at scale 0 |
| For Use with GRAY Hand Piece Only | For Use with GRAY Hand Piece ONLY | for; use; with; only | Partial text match (57%): for, use, with |
| Maintenance | Maintenance |  | Text: not found → Visual: Weak visual match (60%) at scale 1 |
| Dyed Unidirectional Barbs Non-Absorbable | Dyed &ndash; Unidirectional &ndash; Barb | non; tissue; device | Partial text match (23%): non, tissue, device |
| Minimum_Energy Button | Minimum (Energy Button) for HARMONIC™ De | for | Partial text match (17%): for |
| Partially Absorbable Mesh Device Undyed | Partially Absorbable Mesh Device | device | Partial text match (25%): device |
| Regulatory Compliance Mark | Regulatory Compliance Mark | mark | Partial text match (33%): mark |
| Serial Interface | Serial Interface (for service use only) | serial; for; use; only | Partial text match (67%): serial, for, use |
| For Use with BLUE Hand Piece ONLY | For Use with BLUE Hand Piece ONLY | for; use; with; only | Partial text match (57%): for, use, with |
| No Separate Handpiece Required | No Separate Hand Piece Required | no | Partial text match (20%): no |
| Power error indication | Indicates a reflected power error has oc |  | Text: not found → Visual: Weak visual match (65%) at scale 0 |
| Refresh | Refresh |  | Text: not found → Visual: Weak visual match (65%) at scale 0 |
| Refer to instruction manual/booklet | Refer to instruction manual/booklet | to; action | Partial text match (20%): to, action |
| Mentor MplusCO2 | SILTEX™ Round Moderate Plus Profile Gel  | profile; breast; implant; ii | Partial text match (40%): profile, breast, implant |
| Field Intentionally Left Blank | Selection 1: Text required if product do | text; if; product; an; implant; date; fo | Partial text match (58%): text, if, product |
| Mentor HPCO2 | SILTEX™ Round High Profile Gel Breast Im | high; profile; breast; implant; ii | Partial text match (56%): high, profile, breast |
| Mentor MPCO2 | SILTEX™ Round Moderate Profile Gel Breas | profile; breast; implant; ii | Partial text match (44%): profile, breast, implant |

### ❌ Missing Symbols

| Symbol Name | Classification | Expected Text | Regulation | Action |
|-------------|---------------|----------------|-----------|--------|
| 171 - STERILE | Standard | Sterile | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| Biological risk | Standard | Biological risks | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| Keep away from heat | Standard | Keep away from heat | ID: REG_0059.pdf
Title: ISO 7000 Graphical symbols for use o | Add to label |
| 0253 - Sterile Fluid Path_for small point size | Standard | Sterile fluid path | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| Sterile barrier system-Single barrier | Standard | Single sterile barrier system | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| Humidity limitation | Standard | Humidity limitation | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| Double sterile barrier system | Standard | Double Sterile barrier system | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| 0276 - STERILE R wide | Standard | Sterilized using irradiation | ID: REG_0059.pdf
Title: ISO 7000 Graphical symbols for use o | Add to label |
| STERILE Asceptic wide | Standard | Sterilized using aseptic processing tech | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| Contains hazardous substances | Standard | Contains hazardous substances | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| LOT | Standard | Batch code | ID: REG_0059.pdf
Title: ISO 7000 Graphical symbols for use o | Add to label |
| STERILE EO wide | Standard | Sterilized using ethylene oxide | ID: REG_0090.pdf
Title: ISO 15223-1 Medical devices - Symbol | Add to label |
| Contains a medicinal substance | Standard | Contains a medicinal substance | ID: REG_0090.pdf
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
| Field Intentionally Left Blank | Proprietary - Ethicon | Sterile &amp; Nonpyro | — | Add to label |
| Caution, hot surface | Standard | Caution, hot surface | ID: REG_0063.pdf
Title: IEC 60417 Graphical Symbols for Use  | Add to label |
| Immediate stop. laser light source | Standard | Immediate stop, laser light source | ID: REG_0059.pdf
Title: ISO 7000 Graphical symbols for use o | Add to label |
| INTERCEED Absorbable Adhesion Barrier | Proprietary - Ethicon | Absorbable Adhesion Barrier | — | Add to label |
| Gripping Surface Technology | Product Trademark | Gripping Surface Technology | — | Add to label |
| SURGICEL Absorbable Hemostat | Proprietary - Ethicon | Absorbable Hemostat | — | Add to label |
| Pierced soft round cornered pledget | Product Graphic | Pierced soft round cornered pledget | — | Add to label |
| Selection; affirmative acknowledgement; success; A | Standard | Selection; affirmative acknowledgement;  | ID: REG_0063.pdf
Title: IEC 60417 Graphical Symbols for Use  | Add to label |
| Pierced soft square cornered pledget | Product Graphic | Pierced soft square cornered pledget | — | Add to label |
| Cloud connectivity upload successful | Proprietary - Ethicon | Cloud connectivity upload successful | — | Add to label |
| Bell cancel | Standard | Bell cancel | ID: REG_0063.pdf
Title: IEC 60417 Graphical Symbols for Use  | Add to label |
| Advanced setting | Proprietary - Ethicon | Advanced setting | — | Add to label |
| Mini map placement right | Proprietary - Ethicon | Mini map placement right | — | Add to label |
| Mini map placement left | Proprietary - Ethicon | Mini map placement left | — | Add to label |
| Electrostatic sensitive devices | Standard | Electrostatic sensitive devices | ID: REG_0063.pdf
Title: IEC 60417 Graphical Symbols for Use  | Add to label |
| PACS connection actively receiving | Proprietary - Ethicon | PACS connection actively receiving | — | Add to label |
| Reception = full | Proprietary - Ethicon | Reception = full | — | Add to label |
| Port placement | Proprietary - Ethicon | Port placement | — | Add to label |

## Page-by-Page OCR Details

### Page 1
- Words detected: 682
- Text length: 4492 chars
- Barcodes: 1
  - CODE128: LOTNO
- Layout zones: 17
