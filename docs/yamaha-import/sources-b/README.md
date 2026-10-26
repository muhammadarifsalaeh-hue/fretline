# Yamaha import audit: packages 10–18

Audit performed 26 October 2026. These are normalized patches for the existing nine IDs, not new catalog entries. Product names are retained byte-for-byte from the existing reviewed records.

`records.json` preserves the existing reviewed record as its base. All added specification values were read from the **individual model column** of Yamaha Malaysia's FG/FS800 specification table, fetched by the parallel audit under `../sources-a`. This keeps regional alternatives such as “Rosewood or Walnut” intact. No number of frets, six-string count, weight, truss-rod construction or headstock overlay was inferred from the submitted images. Unconfirmed counts remain null; the existing independently sourced FG820-12 twelve-string count is retained.

`fetch.json` records actual HTTPS retrieval status, raw response SHA-256 and compact product price headers. For independent source validation, a second actual fetch is retained as compressed original HTML in the eight `ma-*.html.gz` files. `raw-evidence.json` records the response SHA-256, prior SHA-256, visible model-specific price header and extracted JSON-LD; every second-fetch price matches its record. Four dynamically generated page bodies changed bytes, so their prior and retained hashes are both recorded; 4 hashes are stable across the two fetches. No price changed. An HTTP 200 alone is not accepted as product evidence: the bare FS850 slug returned only a short template, so a separate live canonical product URL was located and read.

All nine record patches were passed through the existing `validateGuitar` function: **9/9, zero errors**. This is schema validation only, not an assertion of photograph authenticity or all-field completeness.

| Package | ID | Public THB reference | Price evidence and important corrections |
| --- | --- | ---: | --- |
| 10 | yamaha-fg840 | 19,200 | Live Music Arms price. Package price was null. Official scale 650 mm; `650 mm (25 inches)` is inconsistent. Package 21 frets is unconfirmed. Official body finish Gloss, not a Matte back/side assertion. Rosewood is fingerboard material, not metal fret material. |
| 11 | yamaha-fg850 | 19,700 | Live Music Arms price matches package. Official scale 650 mm (~25.59 in), binding Mahogany + Cream and Abalone with Black/White sound-hole inlay. |
| 12 | yamaha-fg800j | — | No Thai FG800J product price verified. FG800's 12,400 THB is never copied to FG800J. Current USA model table lists Locally Sourced Tonewood for the neck, Malaysia lists Nato; the regional variation is noted and Malaysia remains the coherent source edition. |
| 13 | yamaha-fg820-12 | 16,500 | Live Music Arms reference differs from package 18,200. Another retailer search result lists 18,200, so this is a retailer offer difference, not a claim that 18,200 is impossible. Manufacturer says no electronics: retailer SYSTEM66 assertions are excluded. Manufacturer nut width 46 mm wins over retailer 45 mm. Rosewood-or-Walnut alternatives retained. |
| 14 | yamaha-fs850 | 19,700 | Correct live Music Arms product page. Official scale 634 mm, not the package conversion ~632.5 mm. Manufacturer binding Mahogany + Cream; keep unsupported bracing/headstock statements out of verified fields. |
| 15 | yamaha-fg830 | 17,500 | Live Music Arms matches package. Manufacturer scale 650 mm (~25.59 in), not exact 25.5 in. Package 20 frets not manufacturer-verified here, retained as an unconfirmed claim rather than promoted. |
| 16 | yamaha-fsx820c | 20,500 | Live Music Arms matches package. Official electronics SYSTEM66, controls and output documented. Manufacturer Rosewood-or-Walnut alternatives retained. Package 20 frets not manufacturer-verified here. |
| 17 | yamaha-fs820 | 15,400 | Live Music Arms matches package. Manufacturer top Solid Spruce, never Solid Mahogany despite original user prose. Manufacturer sound-hole inlay Black + White; no shell/abalone claim copied from conflicting retailer prose. |
| 18 | yamaha-fg800 | 12,400 | Live Music Arms price. Existing name **FG800 Dreadnought** retained. Manufacturer top Solid Spruce; “Sitka” species, slow response and other unsupported tone claims in the package are not marked verified. Nato/Okume and Rosewood-or-Walnut alternatives retained. |

The central importer should preserve original package text as submitted provenance and display any unsupported claims as **ยังไม่ยืนยัน**. It must not silently promote all package prose into source-backed product information.

## Image rights

These submitted ZIPs contain illustrations and user-provided images, not a manufacturer photography permission grant. Packages 10, 11 and 18 explicitly identify AI illustrations; other packages only identify the user-uploaded file. No CC license, author authorization evidence or official model-photo authenticity evidence was found. Do not invent a CC license or misclassify an illustration as a manufacturer photograph. Any preview should retain the source/rights metadata and the project's existing distinction between submitted artwork and rights-verified photos. The old CC BY-SA FG820-12 owner photograph and its original attribution must remain intact.

No application file, guitar data file, practice code, model or dependency was edited by this audit.
