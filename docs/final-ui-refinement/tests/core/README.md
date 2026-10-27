# Final core QA evidence

The production build was run successfully by the root agent before the freeze. Its actual Vite output is retained in [build.log](build.log). The tested `dist/index.html` SHA-256 is `c462802a6f4b51b37cd043b678c44a501943649cf47d5ebdcd841ceb49f7b3d8`. Source, scripts, public assets, and build files remained byte-identical throughout the checks and the targeted harness remediation.

The final actual results are in [results.json](results.json). Eight checks exited 0:

| Check | Actual result |
| --- | --- |
| JavaScript/JSX syntax | 183 modules parsed, exit 0 |
| Python syntax | 30 scripts parsed without bytecode output, exit 0 |
| Original catalog validator | 200 models, no data problems, exit 0 |
| Original image integrity checker | Registered image hashes/files valid, exit 0 |
| Original Practice data/geometry checker | 56 passed, 0 failed, exit 0 |
| Original Phase 4 checker | 19/19, exit 0 |
| Original hand runtime checker | 20 passed, 0 failed, exit 0 |
| Original Yamaha import checker | 11 evidence/isolation checks, exit 0 |

[preservation.json](preservation.json) records 311 existing protected files matching commit `985d0c4898bb02961d25752d8ad0d2dc2ccd1588`, no changed protected files, and no unexpected new source files. The catalog contains 200 unique IDs across 10 brands with 20 models each. All 42 original chord records remain byte-identical, including C major `x32010`, frets `[null,3,2,0,1,0]`, fingers `[null,3,2,null,1,null]`, open strings 3/1, and muted string 6. Practice pre-render selection/filter/navigation/fingering logic and viewer scene/camera/internal review-gate logic match the baseline after removing only retired display-label computations.

The Home sequence contains one new Practice card followed by the original Find and Compare components. The original components, shared editorial stylesheet, text, image definitions, and shared buttons are protected by byte equality. Retired `GuitarModes` files are absent.

The original historical checks still fail. Their actual exit codes and complete captured assertions are retained under [historical](historical):

| Original check | Exit | Actual first assertion site | Historical expectation |
| --- | --- | --- | --- |
| Phase 5 | 1 | `check-phase5.mjs:46:12` | Every brand price range is null |
| Phase 6 | 1 | `check-phase6.mjs:35:39` | Every product price is null |
| Phase 7 | 1 | `check-phase7.mjs:38:5` | Older out-of-batch product snapshot |
| Phase 8 | 1 | `check-phase8.mjs:43:12` | Pacifica price is null instead of 34000 |
| Phase 9 | 1 | `check-phase9.mjs:23:10` | Catalog equals older Phase 8 audit snapshot |
| Phase 8 catalog | 1 | `check-phase8-catalog.mjs:59:12` | Budget filter returns 0 instead of 14 |

All six assertion sites match the committed prior failure logs under `docs/premium-quiz-compare/tests/core`. Those logs and each original checker remain byte-identical to the baseline; current catalog and scoring/filter source data are likewise protected. The approved Yamaha updates predate this UI work. No original criterion, fixture, source data, price, score, or pose status was edited to make these checks pass. **The original historical tests are not all green.**

The first new combined syntax helper parsed both languages but returned exit 1 after Node reported `spawnSync python EPERM`. Its report and output remain in [harness-first-attempt](harness-first-attempt). Splitting this helper into direct Node and Python processes produced actual exits 0 for both. Only those helpers and the Phase 9 logging path were rerun; the latter now captures the full large assertion diff to a regular file and still exits 1. The original Phase 4 middleware fixture also emitted a WebSocket `EPERM` warning on port 24678 while passing all 19 assertions and exiting 0; the full warning remains in its log.

[practice-presentation-review.md](practice-presentation-review.md) documents the final authorized removal of the public unfinished-hand panel and the unchanged internal engine. This evidence does not include a physical iPad/Safari test or certify anatomical hand accuracy.
