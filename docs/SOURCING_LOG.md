# Sourcing log: batch 1 (25 models target)

**Result: 0 models added, 0 verified, 0 licensed photos.** Nothing was invented to fill the gap.
Catalog stays at 18 sample models (`npm run catalog:check`).

## Why batch 1 could not be completed with the tools available
| Needed per model | What was available | Verdict |
|---|---|---|
| Price in THB | Thai shop pages show a **price range for a whole series** (variants chosen by JavaScript); other shops list GBP/USD/JPY/EUR. Converting currency would be creating a price. | Blocked |
| Full spec (body, neck, fingerboard, pickups, bridge, controls, scale, frets, strings) | Shop pages quote parts of the spec; manufacturer pages list woods/features. Weight is usually not published. | Partial only |
| Licensed photo (e.g. Wikimedia Commons) | Search only returns shops, marketplaces and manufacturer pages. Commons file pages (which state the licence) never appeared, so no licence could be checked. Shop/manufacturer photos are copyrighted. | Blocked |

## What was actually checked
Source pages are listed so the next person can re-open them.

**Yamaha FG800 (existing sample record `yamaha-fg800`)**
- Retailer pages quoting the Yamaha spec: solid spruce top, nato/okume back and sides, nato neck, rosewood fingerboard and bridge, scale 650 mm (25 9/16"), nut 43 mm, 20 frets, no electronics or controls, colours Natural / Black / Brown Sunburst / Sand Burst.
  - https://www.muziker.ee/yamaha-fg800-bs
  - https://portlandmusiccompany.com/products/yamaha-fg800-vn-acoustic-guitar-vintage-natural-exclusive
- **Price discrepancy:** the sample record says ฿8,900. A Thai retailer lists the whole FG series (12 variants) at ฿12,400 to ฿19,700, per-model price not shown. https://marcato.co.th/product/yamaha-fg-series-acoustic-guitar/ (page updated 2026-09-07). Treat ฿8,900 as unverified and probably too low.
- Still missing for "verified": exact THB price for FG800, weight (not published).

**Epiphone Casino (existing sample record `epiphone-casino`)**
- Retail listing quoting the spec: layered maple body, mahogany neck, laurel fingerboard, 24.75" scale, 22 frets, 2 × Epiphone PRO P-90, LockTone Tune-O-Matic bridge with Diamond Trapeze tailpiece, controls 2 × volume 2 × tone. Matches the sample record. https://symphonymusicstore.co.uk/epiphone/7073-epiphone-casino-semi-acoustic-guitar-w-premium-gigbag-natural.html
- Price shown there is GBP 699, not THB. Not usable.

**Fender American Professional II Stratocaster**
- Official page exists (https://jp.fender.com/en/products/american-professional-ii-stratocaster). Retailer text confirms 3 × V-Mod II single-coil, 2-point tremolo, 25.5" scale, Deep "C" maple neck. Body is alder or roasted pine depending on finish. No THB price, no licensed photo.

## Worklist
`data-template/batch-01-worklist.csv` lists 10 Yamaha FG/FS models whose names were confirmed on the Thai retailer page above, with the facts known so far and exactly which fields are still missing. These rows are **not importable** on purpose (the importer rejects incomplete rows).

## What would unblock the next batch (pick one)
1. A source with per-model THB prices and full specs that you are allowed to use (distributor price list PDF, a shop that gives you its catalogue export). Export to the CSV template and run `npm run catalog:import`.
2. Photos you took or were given permission to use. Put them in `src/assets/guitars/<id>/` and add credits in `IMAGE_CREDITS`.
3. Decide whether the site may show a model whose price is unknown ("Price on request"). That needs a small schema and UI change (sorting, filters, compare and quiz all assume a numeric price today).

---

# Batch 1 result (Yamaha FG/FS800 series)

**Imported: 18 models** with `scripts/import-csv.mjs` from `data-template/batch-01-yamaha-fg-fs.csv`.
Catalog total is now 36 (18 built-in samples + 18 imported). Target 200, 164 to go.
The earlier `batch-01-worklist.csv` was replaced by this real batch and removed.

## Source and what is verified
- Manufacturer pages (Yamaha Malaysia lineup, model names also on the Yamaha Thailand specs page), checked 2026-10-11:
  - https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/lineup.html
  - https://th.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html (model list only; its spec table is loaded by JavaScript and could not be read)
- Recorded from the lineup page: body style (dreadnought / concert / cutaway), top wood, back and side wood, official finish names per model, 12-string and left-handed flags, FG800J rosewood fingerboard and bridge, and the electric system on FGX/FSX models.
- **Inference (not stated per model):** pickups and controls for non-X models are recorded as "None (acoustic model)". Yamaha describes each X model as the same guitar plus an electric system, so the plain FG/FS models are acoustic. Revisit if a spec sheet says otherwise.

## Status of the 18 records: `partial`
| Field | State |
|---|---|
| Price | **Unknown, shown as "Price on request".** The Yamaha pages quote Malaysian ringgit (RM1,590 to RM3,399). Converting to baht would be inventing a price. No Thai per-model price was found. |
| Neck, scale, frets, weight, controls (X models), bridge (except FG800J) | Not published on the pages read. Left empty and shown as "Not specified". |
| Strings | 12 for FG820-12 only. Other models left empty. |
| Colour swatches | Names are official. Hex values were not published, so swatches are neutral. |
| Photos | None. Yamaha's photos are copyrighted and no licence was found, so every model uses the placeholder illustration. |

## Pending cleanups
- `yamaha-fg800` is still a built-in sample. The official page confirms dreadnought body, solid spruce top, nato/okume back and sides, and finishes Natural, Black, Brown Sunburst, Sand Burst. Its sample price (฿8,900) is unverified. Promote it to `partial` and import it in the next batch.
- `epiphone-casino`, `fender-american-professional-ii-stratocaster`: see the notes above, still sample.

## Re-verification pass (2026-10-11)
After import, the Yamaha Malaysia lineup page was fetched again and all 18 imported records were compared against it field by field: model names, body style, top wood, back and side wood, official finish names per model, 12-string and left-handed flags, FG800J rosewood fingerboard and bridge, and the piezo pickup plus System66 preamp on FGX/FSX models. **No discrepancies were found.**

Facts seen on that page but deliberately not stored:
- Manufacturer RSP in Malaysian ringgit, e.g. FG800M RM1,590 (the lowest) up to FGX830C and FSX830C RM3,399 (East Malaysia, the highest). No baht price is given, so every record keeps "Price on request".
- FG800J shows no RSP at all.
- Hex colour values are not published, so swatches stay neutral.
