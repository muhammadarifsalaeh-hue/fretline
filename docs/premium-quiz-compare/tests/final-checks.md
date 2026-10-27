# Premium Quiz / Compare — actual final checks

This records executed checks, not a blanket claim that every historical fixture passed. Browser results were collected after the final source/build freeze.

The completed final production-browser acceptance is **25 / 25 scenarios passed** across Chromium 154.0.8037.57 and Linux WebKit 26.5, at Desktop 1440×1000, synthetic-touch tablet 768×1024 and mobile 390×844. Extra overflow probes cover 320 px, 834 px portrait, 1024 px landscape and 1194 px landscape. The complete `src` and production-asset hashes stayed unchanged throughout execution. There were **zero console errors, runtime errors, failed requests, HTTP errors, or browser-harness failures**. [Raw final results](final/browser-results.json) · [final run log](final/run.txt).

Those scenarios exercise every original option value, the full five-step Quiz/back/edit/retake flow, six immutable result profiles, exact original scores/reasons/caveats, Compare zero-to-four selection, fifth-selection cap, actual catalog image hashes and honest placeholders, all six real spec categories and keyboard navigation, difference/sample switches, clipboard success and denied-clipboard manual sharing, removal/history/reload, clear cancel/confirm, existing routes, and viewport containment. Screenshots in `final/` decode actual local images before capture; no prototype or substituted model photograph is used.

| Command | Actual result |
|---|---|
| `node docs/premium-quiz-compare/tests/check-preservation.mjs` | PASS: 108 original files byte-identical to `f2168ef`; 200 unique models / 10 brands / 20 each; all 1,500 complete answer combinations and 4,020 recommendation records retain the same IDs, order, scores, reasons and caveats |
| `npm run catalog:check` | PASS: 200 / 10 / 20, no validation errors |
| `npm run images:check` | PASS: publication registry and file hashes intact; 197 catalog models still have honest placeholders |
| `npm run practice:check` | PASS: 56 / 56 |
| `node scripts/check-hand-runtime.mjs` | PASS: 20 / 20 existing loading/disposal/error/visibility guards; no Practice files changed |
| `npm run phase4:check` | PASS: 19 / 19 Quiz/scoring/comparison assertions |
| `node scripts/check-yamaha-import.mjs` | PASS: 11 / 11 source/data/isolation assertions |
| `python docs/premium-quiz-compare/photos/check-photos.py` | PASS: 34 / 34 source, license-metadata, actual WebP decode, responsive dimensions and checksum checks; five original photographs / fifteen variants / 839,000 runtime bytes |
| Homepage full comparison after Compare stylesheet loads | PASS: 8 / 8; original noncompact model headers and computed styles unchanged after Compare → Home navigation; selected-model removal works |
| Original shared browser suite | 17 / 18 pass; the pre-existing `price-1440` fixture still incorrectly expects zero catalog matches below THB 30,000 after the authorized Yamaha prices |
| Original gallery browser suite, unadapted | Stops after 30 passing assertions: expects `Gloss Polyurethane` in the default Compare table, while the new Main category intentionally omits extended material rows |
| Original gallery assertions through the new All category | PASS: 79 / 79, with only a real click on the new All category inserted before the old extended-spec assertion; every original assertion remains unchanged |
| `npm run phase5:check` | FAIL: old assertion requires every brand to have no logo or price range |
| `npm run phase6:check` | FAIL: old assertion requires Pacifica's confirmed THB 34,000 price to be null |
| `npm run phase7:check` | FAIL: old fixed catalog snapshot precedes authorized source-backed product updates |
| `npm run phase8:check` | FAIL: old assertion requires Pacifica's confirmed THB 34,000 price to be null; chained catalog subcommand does not run after this failure |
| `node scripts/check-phase8-catalog.mjs`, run independently | FAIL: eight earlier assertions pass, then its old price-budget fixture expects zero matches while the already imported valid data yields 14 |
| `npm run phase9:check` | FAIL: old fixed catalog snapshot precedes authorized source-backed product updates |

Raw outputs and command exits: [core/results.json](core/results.json). These historical failures were already documented by the preceding Yamaha import in [its test report](../../yamaha-import/TEST-RESULTS.md). The original product data and existing historical scripts are unchanged by this redesign. No fixture, recommendation criterion, or data value was relaxed to get a pass.

The first preservation command hit the managed execution sandbox's Node `spawnSync git` restriction. It was rerun successfully with network-enabled execution, without changing test code or expected bytes; only the completed successful output is in the final core log.

The first complete new-page browser run executed 25 scenarios, with 23 passes and two test-harness failures. It wrongly demanded opacity `1` from the decorative Compare hero on mobile, whose approved CSS deliberately uses `.72`. Both actual images decoded and all console/runtime/network error lists were empty. The harness now expects `.72` only for that exact hero at the matching `max-width: 599px` breakpoint, while retaining the strict opacity `1` requirement for every product `SmartImage`. The UI was not changed to satisfy the test. Initial raw evidence remains in [initial-harness/browser-results.json](initial-harness/browser-results.json). After the corrected complete run passed, duplicate successful initial screenshots were pruned; both actual failure screenshots and the raw report/log remain, with [artifact retention details](initial-harness/artifact-retention.json).

The historical gallery UI adapter is [regression-gallery-adapter.py](regression-gallery-adapter.py); its [79-assertion result](category-adapted-gallery/regression/browser-premium-category-adapter.json) is distinguished from the unchanged old suite's raw failure in [legacy-final](legacy-final/regression-summary.json). The [eight-check Homepage report](home-shared/results.json) additionally checks that loading the redesigned route's CSS does not alter its shared table on the existing Homepage.

Linux WebKit and synthetic touch do not certify a physical iPad running Safari. Physical-device validation remains a user review step.
