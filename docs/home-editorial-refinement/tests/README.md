# Editorial Home verification

Baseline: commit `0f994b4990211acc9151293c9f17a3aa65a156ef` on the existing feature branch. The latest Home brief supersedes the earlier inline Quiz/Compare and single-photograph presentation.

## Scope and baseline

`before/` contains 12 actual Chromium viewport captures from a separately frozen production build at the baseline commit: Hero, Categories, Find, Compare at 1440, 768 and 390 pixels. Its index SHA256 is in `capture-results.json`. New application builds cannot replace that captured baseline.

`check-preservation.py` compares 90 original files to their Git-bound hashes. These include the complete standalone Quiz and Compare pages, Quiz components/style/scoring/data, catalog product data, selection context, Practice source/models and the existing brand marquee hook. They must remain byte-identical. Shared search gains only a Home-specific opt-out for its shortcut chips.

## Browser acceptance

`browser.py` runs actual Chromium and Linux WebKit against the production build. It checks Home section order, responsive paired/stacked banners, the absence of inline Quiz/Compare tools, four category routes, ten brand routes, actual search/autocomplete, real Quiz/Compare entry routes and preservation of four saved comparisons.

Featured tests inspect the composed 200-model catalog snapshot in `catalog-fixture.json`. They retain the original featured model list, check all four tabs against catalog intake metadata and independently checked source-backed THB prices, put unknown prices last, exercise keyboard tabs, persist/remove an actual wishlist entry, and use arrows or native browser horizontal input to move the product rail. "New" is catalog intake metadata, never a fabricated product release date.

Hero tests observe DOM slide-index mutations and their browser timestamps. They require the actual 0–1–2–0 cycle at about 6 seconds per slide, mouse swipes in both directions, native Chromium touch on tablet/mobile and static reduced-motion behavior. Search controls must remain usable.

`marquee-probe.py` is copied unchanged from the preceding accepted production test: 30px/second target with 27–33px/second acceptance, actual seam crossing with at most 3px normalized movement per observed frame, no blank rail, mouse drag/resume, trusted native wheel movement, and Chromium native touch with a finger held down for 1.25 seconds. Automatic movement cannot supply pixels required for a passing manual gesture.

## Replay

Build and freeze application files first; run a production Vite preview on port 5451. Then:

```bash
python docs/home-editorial-refinement/tests/check-preservation.py
PLAYWRIGHT_BROWSERS_PATH=/tmp/fretline-browser-engines \
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 \
LD_LIBRARY_PATH=/tmp/fretline-webkit-libs/usr/lib/x86_64-linux-gnu \
python docs/home-editorial-refinement/tests/browser.py \
  --url http://127.0.0.1:5451 \
  --output docs/home-editorial-refinement/tests/final
```

Run the original standalone browser harness unchanged against the same build, writing a separate output folder:

```bash
PLAYWRIGHT_BROWSERS_PATH=/tmp/fretline-browser-engines \
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 \
LD_LIBRARY_PATH=/tmp/fretline-webkit-libs/usr/lib/x86_64-linux-gnu \
python docs/premium-quiz-compare/tests/browser.py \
  --url http://127.0.0.1:5451 \
  --output docs/home-editorial-refinement/tests/standalone-regression
```

A script is not evidence of a pass. Read each actual `browser-results.json`, including source/build hashes, individual case results and error arrays.

## Physical device limit

Linux WebKit is not physical iPad Safari. Chromium CDP generates native browser touch input, but it is not a person's finger on an iPad. WebKit here supports native wheel/mouse, rendering and keyboard checks; it does not expose a native touch-drag API. Physical iPad Safari portrait/landscape, swiping, momentum, tapping, search, full Quiz and Compare remain device-review steps.

## Retained initial harness mistakes

Two interrupted preliminary runs are retained under `initial-test-assumptions/` and `initial-context-fixture/`. They exposed test setup mistakes: the unchanged Compare page canonicalizes its empty URL to `?ids=`; Hero autoplay begins before Playwright's network-idle return; and reloading an explicitly empty Compare URL correctly replaces an artificially seeded localStorage selection. The final harness checks the canonical path/empty state, records actual browser slide-change timestamps, and seeds four selections through the original Compare URL before navigating via Home. No application change or weakened marquee threshold was used to address these mistakes.

Terminal line-ending spaces in the two initial `run.txt` logs were normalized for Git whitespace hygiene. Assertion values, traces, outcomes and screenshots were retained. No test criterion or application file was changed.
