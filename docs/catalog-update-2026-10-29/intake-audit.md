# Incoming catalog audit — 2026-10-29

Read-only audit against baseline `edc293f`. No application/data files changed.

- Aggregate: 200 unique original IDs, all matching the existing effective catalog; 10 brands × 20.
- Ten brand JSON files match aggregate records exactly. All ten UTF-8-BOM CSVs (20 rows each) match aggregate identity, price, price-source and status fields.
- Normalize 22 `acoustic-electric` records to existing `acoustic`; do not add a fifth category.
- Preserve bass for `epiphone-thunderbird-64-with-rosewood-fretboard`; incoming `electric` is an error.

## Prices

README promises only 17 prices, not 200. Existing catalog has 18 sourced prices. The 17 incoming values comprise 8 Yamaha and 9 Fender: 9 new Fender candidates, 7 Yamaha values identical to old values, and one Yamaha conflict.

`yamaha-fg820-12`: incoming Music Life category listing is THB18,200; old Music Arms exact product listing is THB16,500. Retain old source-backed quote unless a new price is independently justified; different stores are not interchangeable evidence. Ten existing prices are null in the upload and must remain intact.

Most incoming sources are broad retailer category URLs. They can support a value only if actual model and amount are independently located. This audit did not fetch external pages.

## Specifications and description

Only 21 records have any non-null comparison specification: 20 Yamaha plus Fender Player II Stratocaster. Only 19 records declare any verified fields (18 Yamaha plus Fender); declared provenance labels are not independent proof. The remainder are mostly null. Generic descriptions and model-name highlights are explicitly editorial, not manufacturer-confirmed technical facts. Google search links are not evidence.

Preserve existing richer Yamaha specifications and exact materials. Specifically FG800J incoming Nato/Okume back/sides conflicts with existing manufacturer-backed Nato/Mahogany. Existing scale lengths do not conflict with incoming values.

Fender Strat incoming SKU is Black/Maple specifically. It must not narrow existing manufacturer material options (`Alder / Chambered Ash / Chambered Mahogany`, `Slab Rosewood / Maple`) to Alder/Maple across the generic product record.

Full counts, all candidates, non-empty fields and CSV checks: [intake-audit.json](intake-audit.json).
