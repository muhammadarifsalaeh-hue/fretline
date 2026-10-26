# Yamaha packages 1–9 — source audit

Checked 2026-10-26. `records.json` contains proposed replacements only for the nine existing stable IDs. Original catalog names and IDs remain unchanged; no extra guitar or `-02` SKU is created. All records remain `partial`: current sources do not establish instrument mass or fret counts, and the submitted artwork does not establish product measurements.

`official-table.json` is an exact column-by-column extraction from the Yamaha Malaysia FG/FS800 specification table. Its original HTTP body is retained losslessly as `yamaha-my-specs.html.gz`; `fetch.json` records URL, redirect target, byte count, SHA-256 and actual UTC fetch time. Source text exports and all fetched bodies are preserved for review. `official-lineup.json` and `fetch-additional.json` provide fresh exact-model evidence of Scalloped Bracing for all nineteen models, under-saddle piezo pickups for the X models, and left-handed FG820L; these are incorporated in the nine normalized patches. The old Thai lineup URL redirected to the generic guitar index, so that response is not used as evidence of a particular model, price or specification.

## Price results

Prices are observations of the actual Music Arms product pages on 2026-10-26, not Yamaha recommended retail prices, guaranteed checkout prices or stock assurances. The exact model/offer extracts are in `products.json`; malformed source JSON-LD was parsed with literal-control-character tolerance, and visible page prices were checked independently in the saved text. No downloaded merchant images are imported or licensed by this audit.

| Existing ID | Submitted THB | Observed THB | Result |
|---|---:|---:|---|
| yamaha-fsx830c | 24,000 | 24,000 | Matches |
| yamaha-fsx800c | 14,200 | 15,500 | Use observed 15,500; retain submitted 14,200 as unconfirmed historical input |
| yamaha-fs800 | 12,400 | 12,400 | Matches |
| yamaha-fgx820c | 20,500 | 20,500 | Package `FGX820C//02` maps existing FGX820C; suffix not independently established as separate SKU |
| yamaha-fg800m | 12,400 | 12,400 | Matches |
| yamaha-fg820l | 18,200 | 18,200 | Page explicitly lists `Discontinued`; no claim available to buy |
| yamaha-fs830 | 16,000 | 17,500 | Use observed 17,500; retain submitted 16,000 as unconfirmed historical input |
| yamaha-fg820 | 15,400 | 15,400 | Matches |
| yamaha-fgx800c | 15,500 | 15,500 | Matches |

## Material conflicts and resolution

- FSX830C: official scale **634 mm** and nut **43 mm**. Do not copy the submitted nut `1.675 inches` or literal “shell-like” bracing claim. SYSTEM66, cream binding, Rosewood and 3-band EQ/Tuner/Mid FQ are in the exact official column.
- FSX800C: official binding **Black**, scale **634 mm**, nut **43 mm**, fingerboard/bridge **Rosewood or Walnut**. Submitted Rosewood-only narrows the manufacturer's current alternatives. Archive contains flat `FSX800C.jpg`, not its JSON image path; resolve from actual inventory, never invent a missing file.
- FS800: current official fingerboard/bridge **Rosewood or Walnut**; preserve the alternatives. The color montage is a single illustration, not three separate files or verified finish availability.
- FGX820C: official scale **650 mm**, nut **43 mm**, **Rosewood or Walnut**, SYSTEM66, Vol/3-band EQ/Tuner/Mid FQ. The source table does not call this `AMF`, provide battery quantity or establish a separate `//02` SKU. The sleeve of source material/old merchant descriptions must not override the coherent model-specific manufacturer column.
- FG800M: official body and neck finish **Matt**, nut **43 mm**, Tortoise Pattern pickguard, **Rosewood or Walnut**. Submitted Gloss, 44 mm, Black pickguard and D'Addario EXP11 are not the values in the current official column.
- FG820L: official scale **650 mm**, nut **43 mm**, **Rosewood or Walnut**. Store identifies left-handed model, but a submission's generated illustration cannot establish handedness or accurate stringing. Unsupported head-face Rosewood and 20 frets remain unconfirmed.
- FS830: official scale **634 mm**, nut **43 mm**, Rosewood, Cream binding, Abalone w/ Black + White. Source table does not establish fret count or colors available in the Thai market.
- FG820: official nut **43 mm**, binding **Cream**, **Rosewood or Walnut**, pickguard Tortoise Pattern (Black for BL/SB variations). Submitted 44 mm/Black binding/narrowed Rosewood are corrected to exact official values. Factory string products are Yamaha FS50BT or D'Addario XT; do not interpret `0.12` as a confirmed gauge.
- FGX800C: official scale **650 mm**, nut **43 mm**, **Rosewood or Walnut**, SYSTEM66. The submitted claims that Nato/Okoume are the same botanical family as mahogany, the head face is Rosewood, and bracing is “shell-like” are not established by the current official table and should not be presented as verified facts.

The normalized descriptions use concise factual construction data. The original submitted Thai description/specification payloads must be retained separately with “ยังไม่ยืนยัน” where unsupported; they should not replace current manufacturer facts just because they appeared in a ZIP.

## Image rights / model matching

None of packages 1–9 contains a named photographer/rights holder, grant of rights, CC license, or evidence allowing a human to mark original manufacturer/merchant photo rights verified. User instruction to import is permission to process the files; it is not a claim that the pictures are manufacturer product photos or reusable third-party photos. Do not invent a CC license or set the legacy rights checker green.

Some packages explicitly call the images created/presentation illustrations (FG820L, FGX800C); FS830 says possible generated illustration. Others only say user-supplied. Exact copies can be retained as project artwork only under the existing distinct project-artwork provenance policy, with manufacturer model accuracy/finishes unverified and no claim of licensed original product photography. Otherwise keep them in non-public intake/preview. FG820L illustration additionally needs a human handedness check. Do not generate replacement photos or split composite montages into purported verified single-color photographs.
