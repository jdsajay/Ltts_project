# AI Redline Report: DRWG107621_Rev D_NATIVE 1

**Analysis Model**: o3
**Analysis Time**: 340.0s
**Total Non-Conformances**: 26

## Summary

Found 26 non-conformances across 7 panels (22 per-panel + 4 cross-panel)

## Non-Conformances

**NC-1. Required 2D DataMatrix UDI carrier is absent; only 1D GS1-128 barcode provided.**
- Area: Outer Lid Label – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 14607:2024, 11.5; ISO 15223-1:2021, 5.7.7; EU MDR Art.27
- Elements: I2
- Current: `Linear barcode only`
- Corrected: `Add 2D DataMatrix encoding full UDI-DI & UDI-PI per ISO 15223-1 & EU MDR Art.27`

**NC-2. Wrong sterilization symbol version – uses “STERILE |” graphic that is not in current symbol library row 50.**
- Area: Outer Lid Label – CPX4 Tall Height
- Action: replace
- ISO Reference: ISO 15223-1:2021, 5.2.x; ISO14607-SYM-version
- Elements: I2
- Current: `STERILE |`
- Corrected: `Replace with boxed “STERILE” symbol per ISO 15223-1:2021, 5.2.3-5.2.8 or method-specific symbol in current library.`

**NC-3. Quantity symbol missing and redundant text “Quantity:1” used instead.**
- Area: Outer Lid Label – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.4.6; ISO14607-text-redundancy
- Elements: I2
- Current: `Quantity:1`
- Corrected: `Add quantity/contains symbol (open box) with ‘1’ adjacent; remove redundant text.`

**NC-4. Double sterile barrier system symbol required for outer packaging but not present.**
- Area: Outer Lid Label – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.2.10; ISO14607-11.2
- Elements: I2
- Current: `No concentric-oval symbol`
- Corrected: `Insert double-sterile-barrier symbol per ISO 15223-1:2021, 5.2.10.`

**NC-5. Serial number (SN) symbol is missing; only LOT and REF symbols shown.**
- Area: Outer Lid Label – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.1.6
- Elements: I2
- Current: `No SN boxed symbol`
- Corrected: `Add boxed “SN” symbol with variable serial number field.`

**NC-6. UDI symbol not present adjacent to barcode.**
- Area: Outer Lid Label – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.7.7
- Elements: I2
- Current: `No UDI rectangle symbol`
- Corrected: `Place UDI symbol immediately left of the barcode as per library row 265.`

**NC-7. Human-readable interpretation under barcode is incomplete – lacks 14-digit GTIN, full expiry (YYMMDD) and serial number.**
- Area: Outer Lid Label – CPX4 Tall Height
- Action: update
- ISO Reference: ISO 14607:2024, 11.5; GS1 GENSPEC 3.2.3
- Elements: I2
- Current: `(01)TK20(17)PDTETE(10)LOTNO`
- Corrected: `Complete HRI with full (01)GTIN14 (17)YYMMDD (10)LOT (21)SERIAL etc.`

**NC-8. CE mark, Medical Device (MD) and EC REP symbols are all absent; required for EU market configuration.**
- Area: Outer Lid Label – CPX4 Tall Height
- Action: add
- ISO Reference: EU MDR 2017/745 Art.20 & Annex I; ISO 15223-1:2021 5.1.2
- Elements: I2
- Current: `No CE / MD / EC REP symbols`
- Corrected: `Add CE mark with NB number, MD rectangle, and EC REP symbol per MDR Annex I & ISO 15223-1 5.1.2.`

**NC-9. Sterile symbol uses outdated variant 'STERILE |I'; current ISO library version is plain rectangle with the word 'STERILE' only.**
- Area: Thermoform Label – CPX4 Tall Height
- Action: replace
- ISO Reference: ISO 15223-1:2021, 5.2.3-5.2.8
- Elements: I3
- Current: `STERILE |I`
- Corrected: `Replace with symbol 171-STERILE (plain rectangle, no divider)`

**NC-10. Mandatory 2D DataMatrix UDI carrier absent on this panel.**
- Area: Thermoform Label – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 14607:2024, 11.5 / EU MDR Art.27
- Elements: I3
- Current: `No DataMatrix present – only 1D barcode`
- Corrected: `Add GS1 2D DataMatrix encoding UDI-DI & UDI-PI adjacent to linear code.`

**NC-11. UDI symbol (boxed 'UDI') not shown next to the barcode as required.**
- Area: Thermoform Label – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.7.7
- Elements: I3
- Current: `Symbol absent`
- Corrected: `Add ISO/GS1 UDI symbol directly left of DataMatrix/linear barcode.`

**NC-12. Quantity conveyed only as text 'Quantity:1'; ISO quantity symbol (open box) is required and text becomes redundant.**
- Area: Thermoform Label – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.4.6
- Elements: I3
- Current: `Quantity:1`
- Corrected: `Insert ISO 15223-1 5.4.6 quantity symbol with '1' inside; delete redundant text.`

**NC-13. Manufacturer symbol and address missing on the panel.**
- Area: Thermoform Label – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.1.1
- Elements: I3
- Current: `No factory 'Manufacturer' symbol or address block`
- Corrected: `Add ISO 7000-3082 factory symbol followed by registered name & full address.`

**NC-14. Authorized representative symbol (EC REP) is completely absent from the panel.**
- Area: Combo Label (Set) – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.1.2
- Elements: I4
- Current: `MR`
- Corrected: `Add EC REP symbol (ISO 7000-3088) with authorised EU address`

**NC-15. Date-of-manufacture symbol shown is wrong version (regular factory icon). Must use ISO 7000-2497 version that incorporates the date element.**
- Area: Combo Label (Set) – CPX4 Tall Height
- Action: replace
- ISO Reference: ISO 15223-1:2021, 5.1.3
- Elements: I4
- Current: `MFGDATE`
- Corrected: `Replace icon with correct ISO 7000-2497 symbol, keep text or remove per company style`

**NC-16. Panel omits the double sterile barrier system symbol although three sterile barriers are indicated (STERILE R / EO / _).**
- Area: Combo Label (Set) – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.2.10
- Elements: I4
- Current: `STERILE R / EO boxes only`
- Corrected: `Add concentric-oval symbol per ISO 15223-1:2021, 5.2.10 near sterile information`

**NC-17. No single-use / Do-not-reuse symbol. Device is single-use per IFU, symbol required.**
- Area: Combo Label (Set) – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.4.2
- Elements: I4
- Current: `Quantity:1 (text only)`
- Corrected: `Insert ISO 7000-1051 symbol (Ø2) near device description.`

**NC-18. UDI carrier lacks mandatory Human Readable Interpretation (GTIN, LOT, EXP, SN) adjacent to DataMatrix.**
- Area: Combo Label (Set) – CPX4 Tall Height
- Action: add
- ISO Reference: EU MDR 2017/745 Art. 27 & ISO 15223-1:2021, 5.7.7
- Elements: I4
- Current: `(DataMatrix with no text)`
- Corrected: `Print HRI: (01)GTIN (17)YYMMDD (10)LOT (21)SN directly below/next to code`

**NC-19. UDI carrier incomplete — panel shows only a 1-D linear barcode with no 2-D DataMatrix and no adjacent HRI text.**
- Area: Section Header – Thermoform Label Identifier
- Action: add
- ISO Reference: ISO 14607:2024, 11.5 & ISO 15223-1:2021, 5.7.7
- Elements: I6
- Current: `Linear barcode with no HRI`
- Corrected: `Add 2-D GS1 DataMatrix encoding full UDI-DI + UDI-PI and place HRI (GTIN, LOT, expiry, SN) immediately below per ISO 15223-1 & EU MDR Art.27.`

**NC-20. Batch code (LOT) symbol and placeholder text are missing from patient record label; ISO requires LOT or SN (preferably both).**
- Area: Section Header – Thermoform Label Identifier
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.1.5 & ISO 14607:2024, 11.5 b)
- Elements: I6
- Current: `No LOT symbol or field present`
- Corrected: `Insert ISO 7000-2492 LOT frame symbol followed by LOT alphanumeric field.`

**NC-21. Redundant text 'SERNO' duplicates the meaning of the adjacent SN symbol, violating ISO text-redundancy guidance.**
- Area: Section Header – Thermoform Label Identifier
- Action: remove
- ISO Reference: ISO 15223-1:2021, Clause 1 & ISO14607-text-redundancy rule
- Elements: I6
- Current: `SN  SERNO`
- Corrected: `SN   <serial number value>`

**NC-22. UDI symbol (boxed 'UDI') is not shown adjacent to the barcode as required.**
- Area: Section Header – Thermoform Label Identifier
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.7.7
- Elements: I6
- Current: `No UDI symbol`
- Corrected: `Insert boxed 'UDI' symbol directly left of the 2-D DataMatrix once added.`

**NC-23. Quantity is conveyed only as the text string “Quantity:1”.  The ISO 15223-1 quantity symbol (open box with numeral) is required on this panel just as on the Outer-Lid and Thermoform labels.**
- Area: Combo Label (Set) – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.4.6
- Elements: I4
- Current: `Quantity:1`
- Corrected: `[quantity-symbol] 1`

**NC-24. The CE marking, Medical Device (MD) symbol and Authorized Representative (EC REP) symbol are all absent on the Thermoform label, although they are mandatory for an EU-market configuration and were already identified as missing on the Outer-Lid panel.**
- Area: Thermoform Label – CPX4 Tall Height
- Action: add
- ISO Reference: EU MDR 2017/745 Art.20 & Annex I; ISO 15223-1:2021 5.1.2
- Elements: I3
- Current: `MADE IN U.S.A. (last line on panel)`
- Corrected: `[CE]  [MD]  [EC REP] (symbols grouped near regulatory block)`

**NC-25. The boxed “UDI” symbol required to identify the carrier is not printed adjacent to the DataMatrix/linear barcodes on the Combo label set.  Same omission was noted on Outer-Lid, Thermoform and Supplementary panels, so this panel must also be corrected.**
- Area: Combo Label (Set) – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.7.7
- Elements: I4
- Current: `(barcodes shown with no identifying symbol)`
- Corrected: `[UDI] symbol placed immediately left of DataMatrix and linear barcodes`

**NC-26. Manufacturer symbol (factory icon) is missing; only the word “MENTOR” appears.  Each packaging level—including the Combo patient/implant labels—must bear the ISO 15223-1 manufacturer symbol together with the name and address.**
- Area: Combo Label (Set) – CPX4 Tall Height
- Action: add
- ISO Reference: ISO 15223-1:2021, 5.1.1
- Elements: I4
- Current: `MENTOR®  (brand name only)`
- Corrected: `[manufacturer-symbol]  Mentor Texas, USA`
