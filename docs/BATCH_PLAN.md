# Plan for the next batches (toward 200 models)

Status: 36 / 200. Only the Yamaha FG/FS800 series (18 models) is source-backed so far, all `partial` (price unknown).

## What worked
The manufacturer's regional **lineup page** lists every model of a series with per-model facts (body, woods, finishes, electronics). One page gave 18 models in one fetch. The spec table pages load by JavaScript and could not be read, so neck, scale, frets and weight stay empty until a readable spec source is found.

## Sources already seen (open these next, same method)
All of these links appeared in pages already read, so they are known to exist. Their contents have **not** been read yet.

| Batch | Source | Expected content |
|---|---|---|
| 2 | https://th.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/ (series list) and `.../acoustic-guitars/ta-series/` | TransAcoustic FG-TA, FS-TA, FGC-TA, FSC-TA are named on the FG/FS page. Other acoustic series are listed on the category page. |
| 3 | https://th.yamaha.com/en/musical-instruments/guitars-basses-amps/products/classical-nylon-guitars/ | Classical and nylon series. Also lets the built-in sample `yamaha-c40` be verified. |
| 4 | https://th.yamaha.com/en/musical-instruments/guitars-basses-amps/products/electric-guitars/ and `.../electric-basses/` | Electric guitar and bass series (Pacifica and others). |
| 5 | https://th.yamaha.com/en/musical-instruments/guitars-basses-amps/products/silent-guitar/ | SILENT guitar series. |

## Risks, stated plainly
1. **One brand would dominate.** If all 200 came from Yamaha, the Brands page and filters would look lopsided. Other makers need their own official lineup pages (Fender, Gibson, Ibanez, Taylor, Martin, Epiphone, PRS, Squier, Gretsch, Córdoba are already in the catalog). Not every site is readable without JavaScript.
2. **Counts are unknown.** Nobody has read these category pages yet, so how many distinct models they hold is not known. Do not promise 200 from Yamaha alone.
3. **Prices.** Official sites quote local currency. Without a Thai dealer or distributor price list, models stay "Price on request".
4. **Photos.** No licensed photo has been found for any model. Manufacturer photos need written permission.

## Procedure per batch
1. Fetch the lineup page. Copy only facts stated there into `data-template/batch-NN-*.csv` (blank = unknown).
2. `npm run catalog:import -- file.csv --dry-run`, then without `--dry-run`.
3. `npm run catalog:check` (duplicates, counts), then check the new models in the Catalog.
4. Log what was and was not verified in `docs/SOURCING_LOG.md`.
