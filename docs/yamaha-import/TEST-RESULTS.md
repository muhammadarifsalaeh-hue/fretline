# Yamaha import test delivery

The final import acceptance is **passed**; the statement “every historical test passed” would be false. No existing assertion was deleted, weakened or marked successful without execution.

[Machine-readable acceptance](tests/acceptance.json) · [final raw browser results](tests/final/browser-results.json) · [core command exits](tests/core/results.json)

| Actual verification | Result |
|---|---|
| Production build | Passed; existing lazy Three.js chunk-size warning remains |
| `npm run catalog:check` | Passed: 200 unique models, 10 brands, 20 each |
| `npm run images:check` | Passed for the unchanged publication registry; does not certify the 20 excluded Preview images |
| `npm run practice:check` | 56/56 passed |
| `node scripts/check-hand-runtime.mjs` | 20/20 passed; no Practice files changed |
| Original Phase4 checks | 19/19 passed |
| Exact Yamaha evidence/data validation | 11/11 passed, with per-model field and price assertions |
| Dev-only preview plugin/isolation guards | 13/13 passed |
| Actual ordinary-dev direct-asset isolation | 8/8 passed, including denied raw/file URLs |
| Immutable IDs, other models, original source/assets, rights and Practice | 8/8 preservation checks passed |
| Chromium 154.0.8037.57 | 140/140 final cases passed |
| Linux WebKit 26.5 | 140/140 final cases passed |
| Console / runtime / network errors in final browser run | 0 / 0 / 0 |
| New source-backed price-filter checks | 6/6 passed across both engines and three viewport sizes |
| Original Pacifica gallery regression | 79/79 passed |
| Original shared regression | 17/18 passed; remaining old zero-price fixture described below |
| Review screenshots after actual lazy-image decoding | 14/14 captured, 0 console/runtime errors |
| Physical iPad Safari / hardware performance | Not tested in this environment |

## What was exercised

The 280-case final run covers 18 actual existing Yamaha IDs in both ordinary production and the explicit development preview, on desktop 1440×1000, tablet touch 768×1024 and mobile touch 390×844 in both browser engines. It asserts unchanged names, actual displayed THB prices, sourced specification text, horizontal containment, all source-image bytes/dimensions, containment styling, thumbnails/lightbox, all 20 catalog IDs through pagination, search, comparison groups covering all 18 imported IDs, wishlist reload persistence and Find My Guitar recommendations.

The final run’s complete source/build hashes remained unchanged during execution. Its screenshot/data JSON is retained under `tests/final/`; review captures in `tests/screenshots/` explicitly load all actual lazy images before capture. They are distinct from raw full-page browser captures that can legitimately contain offscreen native-lazy images awaiting visibility.

The existing shared suite’s 320 px Compare check first found a real 344 px document overflow. The newly populated lowest-price verdict could expand its implicit grid track. Adding only `min-w-0` to that list item fixes the actual document width to 320 px; the original 320 px check subsequently passed. Comparison calculation and selection behavior are unchanged.

## Historical tests that still fail

The original shared `price-1440` case expects zero models below THB30,000. That assumption was true when only Pacifica had a sourced THB34,000 price. The import legitimately introduces 17 confirmed Yamaha prices below THB30,000, so the unchanged old case fails. A separate fresh regression checks the exact 17 IDs, excludes unconfirmed FG800J/FGX830C, checks inclusive THB15,500 and THB34,000 boundaries and the empty >THB70,000 case: 6/6 passed. The old failure remains in [its raw report](tests/legacy-shared-final/shared-regression.json).

`phase5:check` through `phase9:check` were run and failed against fixed assumptions/snapshots from earlier project phases: absence of brand logos/ranges, all prices null including Pacifica’s previously verified THB34,000, and immutable earlier Yamaha data snapshots. Baseline failures for the previous project are recorded [here](../practice-trainer/tests/reports/legacy-static-baseline.md). The newly intended 18-model data import also differs from those historical snapshots; it must not be “fixed” by removing valid prices or reverting the supplied-model updates.

The second command in `phase8:check` is normally skipped when its first command fails. It was therefore also executed independently: `check-phase8-catalog.mjs` passes its first eight catalog/search assertions, then fails its old expectation of zero matches within the newly populated price budget (actual 14). Its [raw output](tests/core/phase8-catalog-standalone.txt) and [actual exit](tests/core/phase8-catalog-standalone.json) are retained. These failures require separate historical-fixture maintenance, not lower data accuracy.

## Failures found and resolved before acceptance

- Initial preview server was unavailable during the first browser run. Its production half passed 140 cases; all preview failures were retained. The final runner owns the preview server lifecycle and checks readiness.
- An intermediate FG800 test used the alphabetical intake-file order instead of the explicit Natural/Black/Sunburst gallery order. The harness was corrected to compare against hash-bound original files in the intended order; the application’s correctly ordered images were not changed to satisfy that mistaken expectation.
- A full intermediate run passed all 280 functional assertions but was correctly rejected because duplicate source URLs for FG800, FG800J and FG820-12 produced React duplicate-key warnings in development. The source entries were consolidated with their supported fields retained. A new uniqueness check was added; the entire final run then passed with zero console errors.
- The original 320 px Compare regression and retailer-source summary integration issue were corrected as described in the delivery report.

Raw intermediate reports are preserved under `tests/after/`, `tests/preview-retest/` and `tests/console-before-fix/`; they are never relabeled as passes. Redundant generated intermediate screenshots were pruned while retaining representative failures, baseline captures, every original upload and final review evidence. [Artifact retention record](tests/intermediate-artifact-retention.json).

## Physical iPad Safari review

Open the private forwarded Codespaces port using the README commands. On the real device: browse all three Yamaha catalog pages; search FSX830C; open each supplied model; check all FG800 thumbnails and FG820-12’s secondary illustration; open/close the lightbox; compare multiple real prices; reload a wishlist; and complete Find My Guitar. Check portrait/landscape touch scrolling, zoom and page containment. Linux WebKit and synthetic touch do not certify native iPad Safari or hardware memory/FPS.
