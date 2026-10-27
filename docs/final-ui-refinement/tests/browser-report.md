# Final browser acceptance

**71/71 distinct final cases passed:** 40 Home/UI/Practice checks and 31 Quiz/Compare checks. Actual browser versions were Chromium 154.0.8037.57 and Linux WebKit 26.5. Four viewport sizes were covered (1440×1000, 1194×834, 768×1024, 390×844), with restored Home also verified at the 1024×1366 portrait edge.

[Consolidated machine-readable results](final-browser-summary.json) · [56 actual before/after screenshot pairs and the restored Home group](screenshot-index.html) · [Screenshot manifest](screenshot-pairs.json) · [Independent visual review](visual-review.md)

## Coverage

- Home: exactly three cards, original Find/Compare copy, numbered eyebrows, original blue/room photographs and gold controls; real Practice/Quiz/Compare destinations; large-left/two-right landscape arrangement and portrait/mobile stacking; Featured immediately follows the group with original product IDs and tabs.
- Catalog: decoded cinematic photograph, removed long note, all 200 real models, actual search/category/brand/budget/sort/pagination, wishlist/Compare/detail actions.
- Quiz: all 22 original option values, real five-step navigation/back/edit/retake, and all six unchanged result fixtures including model IDs/order/scores/reasons/caveats/prices. Hero/bottom removed controls are absent, questions remain immediately usable.
- Compare: four original slots, add/search/fifth-model limit, six real table categories, differences/example switches, mobile table scroll, actual selected-product image hashes, share/clipboard, remove/history/reload/clear-confirm/cancel. Oversized empty presets and long note are absent.
- Practice, in **each** engine: all 42 original chords, 84 full/compact SVG diagrams checked against the unchanged independent voicing fixture; exact strings/frets/fingers/notes/barrés and instructions; 42 real WebGL2 canvas updates; all six filters and real search; previous/next wrap and keyboard navigation; six camera presets and four camera buttons verified by real pixel changes, keyboard/reset, and unchanged geometry. Injected WebGL failure kept the F diagram and all 42 choices usable; real retry recovered 3D with selection preserved. Unapproved hands remained hidden and no hand pose was promoted.

## Integrity and initial diagnostics

All source/build hashes remained unchanged across final runs and the last filesystem check. The actual served index on port 5451 matches frozen SHA-256 `c462802a6f4b51b37cd043b678c44a501943649cf47d5ebdcd841ceb49f7b3d8`. All 56 baseline PNGs and metadata remain byte-identical. Quiz fixtures, independent chord criteria, and chords.js match baseline 985d0c4.

Final evidence has zero unexpected console/runtime/HTTP/request/harness errors. Original diagnostics remain available: two WebKit lazy-scene requests were canceled when the early Home test intentionally navigated away from Practice before initialization; a clean route retest now waits for actual scene initialization and has no failed requests. The newly added 1194px Compare test initially assumed tablet-style table overflow; its corrected viewport condition retains mandatory overflow at 768/390 and the targeted landscape retest passed. These diagnostics and retest links are preserved in the consolidated report.

WebKit was installed from the official Playwright distribution under /tmp; its missing WPE dependencies were extracted from official Debian packages under /tmp. The unused GTK desktop validation was skipped; real headless WebKit rendering and every assertion still ran. No project dependency or system package changed. [Runtime setup provenance](webkit-runtime-setup.json).

## Limits

No physical iPad or native iPadOS Safari test was performed. Mobile retains the baseline left-edge neck crop; full-neck visibility on small screens is not asserted. Structural musical/diagram/camera checks do not certify anatomical hand contact or approve unfinished hand poses.
