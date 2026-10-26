# Yamaha import — 26 October 2026

Source branch: `feature/yamaha-19-import`. Baseline: `decd5544ade430530ac7c1e37ae463f251c90d50`. No merge into master.

## What was received

The message requests 19 archives, but exactly **18 ZIP files** are attached and accessible. All 18 were safely extracted into the ignored `.yamaha-intake/` folder, with file paths checked before extraction. They contain **18 existing Yamaha model IDs and 20 original images**. The user subsequently confirmed the intended nineteenth file is **FGX830C**; that archive is still absent. No nineteenth ZIP, product, SKU, image angle or price was invented.

All supplied JSON, Thai descriptions and notes are retained byte-for-byte under `original-metadata/`, including unsupported claims. Embedded CODEX instructions are treated as supplied source documents, not project instructions. Their hashes are bound in `preview-manifest.json`.

## Imported model status

“Data imported” means the available source-backed fields were merged, not that every specification or image license is confirmed. All 18 records intentionally remain `partial`. Unknown mass and fret counts are not inferred from artwork. The Detail table labels unconfirmed fields “ยังไม่ยืนยัน”.

| Existing ID / unchanged name | Observed THB | Specification data | Uploaded images | Publication status |
|---|---:|---|---:|---|
| `yamaha-fsx830c` / FSX830C | 24,000 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fsx800c` / FSX800C | 15,500 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fs800` / FS800 | 12,400 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fgx820c` / FGX820C | 20,500 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fg800m` / FG800M | 12,400 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fg820l` / FG820L | 18,200 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fs830` / FS830 | 17,500 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fg820` / FG820 | 15,400 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fgx800c` / FGX800C | 15,500 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fg840` / FG840 | 19,200 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fg850` / FG850 | 19,700 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fg800j` / FG800J | ยังไม่ยืนยัน | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fg820-12` / FG820-12 | 16,500 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fs850` / FS850 | 19,700 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fg830` / FG830 | 17,500 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fsx820c` / FSX820C | 20,500 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fs820` / FS820 | 15,400 | Yamaha exact model column; partial | 1 | Development Preview only; image rights/model match unconfirmed |
| `yamaha-fg800` / FG800 Dreadnought | 12,400 | Yamaha exact model column; partial | 3 | Development Preview only; image rights/model match unconfirmed |

**Missing new attachment:** `yamaha-fgx830c` (FGX830C). The existing Pacifica 612VIIFM images and ฿34,000 manufacturer RRP are preserved; they were not a nineteenth ZIP in this message. Thus 18 new models plus the previously prepared Pacifica cover 19 of the existing 20 Yamaha records. FGX830C remains in the catalog with its previous sourced specifications and without a new uploaded image/price.

## Evidence and corrections

Specifications come from the exact model columns in Yamaha Malaysia’s current FG/FS800 table and matching manufacturer Lineup sections. Millimetres are canonical; inch values are derived consistently. Manufacturer material alternatives such as “Rosewood or Walnut” are retained. Thirty table fields plus bracing are available through the existing Detail/Compare specification system; other guitars receive no extra empty rows.

Retail prices were actually read from model-specific Music Arms pages on 26 October 2026. They are reference listings, not Yamaha recommended retail prices, guaranteed checkout totals or availability claims. Seventeen submitted models have source-backed THB prices; FG800J has no confirmed THB price. FG800’s price is never borrowed for FG800J. FG820L and FG820-12 merchant listings mark discontinued; the full price note discloses this.

Notable conflicts: FSX800C submitted ฿14,200 → observed ฿15,500; FS830 ฿16,000 → ฿17,500; FG820-12 submitted ฿18,200 → selected Music Arms reference ฿16,500. FG840 submitted no price → observed ฿19,200. FG800M manufacturer Matt/43 mm replaces unsupported Gloss/44 mm; FS850 scale is 634 mm; FGX820C/02 maps existing FGX820C without a new ID. See [source audit A](sources-a/README.md) and [source audit B](sources-b/README.md) for field-level conflicts and retained HTTP evidence.

## Image rights and preview boundary

All 20 supplied images decode and are associated with their submitted model IDs. Several are explicitly described as generated illustrations; none contains enough evidence to certify the original rights holder, a reusable photograph license or exact product details. Uploading an illustration does not prove third-party image rights. No image was relabeled as CC, manufacturer photography, model-certified or license-verified. No new entry was inserted into `imageRights.json` or `projectArtwork.json`; both existing registers are unchanged.

The originals are retained on this private feature branch under `preview-assets/` for explicitly requested design review. The opt-in development mode serves them via exact SHA-256-bound routes, with `no-store`, `noindex` and a visible gallery credit stating the limitations. **Ordinary `npm run dev` and every production build exclude all 20 new images.** This boundary is tested. The preview is not a public release or a rights approval. Keep the Codespaces forwarded port private. Source files in this private GitHub branch are still stored in GitHub; do not make the repository public as if image rights had been approved.

Every original remains unchanged: no crop, stretching, flipping, recoloring, montage splitting or replacement generation. Gallery and Lightbox use `object-fit: contain` on black. FG800 has three real submitted image files; the other montages remain single files. FG820-12 keeps the existing licensed Peternick2468 image first and appends the new illustration only in Preview.

## Open on iPad / existing Codespace

If Vite is already running, stop it with **Ctrl+C** before typing Git commands. Preserve any local edits if Git reports a conflict; do not reset or discard them.

```bash
git fetch origin
git switch feature/yamaha-19-import
git pull --ff-only origin feature/yamaha-19-import
npm run dev:yamaha-preview -- --host 0.0.0.0 --port 5173 --strictPort
```

Open **Ports → 5173 → Open in Browser**, then visit `/guitars?brand=Yamaha` or `/guitars/yamaha-fsx830c`. No npm reinstall is needed; dependencies are unchanged. This workspace cannot know the full current hostname of your separate Codespace, so no guessed URL is supplied.

## Tests and screenshots

See [test delivery](TEST-RESULTS.md) and [Before/After screenshots](SCREENSHOTS.md). Physical iPad Safari testing remains a user-device step; Linux WebKit results do not certify actual iPad hardware.

## Files and preserved systems

Application changes are limited to `reviewedGuitars.json`, optional shared spec definitions/translations, import-specific unknown-field and retailer-source notes, and a dev-only Gallery data extension. `vite.config.js`, one npm development script and the preview plugin support the restricted mode. New data/preview checks and source evidence are under `scripts/check-yamaha-*.mjs` and this directory. No dependency was added. A single `min-w-0` class was added to the existing Compare verdict list item: multiple newly verified prices exposed a real 320 px grid overflow; comparison scoring and selection logic are unchanged.

All 200 IDs/names, non-import product data, Homepage, Animated Brand Marquee, Brands, Compare logic, Wishlist state, Catalog logic, Quiz/Find My Guitar and every Practice source/model/rig/pose asset remain unchanged. Actual regression and preservation results document this; no 3D work was resumed.

## Still required for full publication

- Supply the missing nineteenth archive, confirmed by the user as FGX830C. This model has no new attachment.
- Provide image rights/model evidence appropriate to each original before enabling production product imagery. No new image is publication-approved in this delivery.
- Confirm FG800J price and the remaining unavailable specifications; all unsupported input remains retained for review.
- Review the actual screenshots and check on physical iPad Safari before deciding on a master merge. No master merge is performed.
