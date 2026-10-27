# Home redesign — actual QA evidence

Baseline: `4bbecf86585ab14cca2d23e2b65f090db20a1816`, the completed standalone Quiz/Compare redesign. The new Home work intentionally changes Home components; this audit does not classify those authorized changes as regressions.

Final executed results: **32/32 Home scenarios** and **25/25 existing standalone Quiz/Compare scenarios** passed on the same frozen production build, with zero browser/network errors. See [TEST-RESULTS.md](TEST-RESULTS.md) for exact evidence, the real WebKit bugs found and fixed, the corrected measurement method, historical fixture limits and physical-device work still required.

- `before/`: 12 real Chromium production screenshots (Brands, Find, Compare and full Home × desktop/tablet/mobile), plus exact production-index hash and Git-bound protected-file hashes.
- `check-preservation.py`: verifies 180 unrelated original files remain byte-identical, including all catalog/quiz/scoring/selection data, standalone Quiz and Compare, shared table, navigation/layout, Catalog/Wishlist/detail pages and Practice code/models.
- `core/`: actual command exits and outputs for Catalog, Images, Practice, Phase 4 and Yamaha preservation checks.
- `browser.py`: production-browser acceptance and actual screenshots for Home composition, every original quiz option, all five questions/back/results, source-bound product images, Compare context/add/remove/expansion, ten actual brand routes, responsive widths, reduced motion, mouse dragging, loop rebasing, autoplay and input resume.

The original five-step data has **5 / 3 / 5 / 5 / 4 options**, not four answers at every step. The acceptance test preserves all 22 values. Its result assertions use the already frozen original answer/result fixture, rather than computing expected results from the new UI.

Actual product-card image bytes must match the existing model-specific publication/illustration registry; an editorial photo is not accepted as a missing model photo. The default Home example uses the two licensed real-photo models Yamaha FG820-12 and Martin D-28. Their missing weight and other unknown fields must remain unspecified; selecting a different model must never substitute the default pair's images for it.

## Reproduce

Root must first complete `npm run build` and freeze the source and built assets. Run a production preview at port 5451, then:

```bash
python docs/home-premium-redesign/tests/check-preservation.py
PLAYWRIGHT_BROWSERS_PATH=/tmp/fretline-browser-engines \
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 \
python docs/home-premium-redesign/tests/browser.py \
  --url http://127.0.0.1:5451 \
  --output docs/home-premium-redesign/tests/final
```

This environment also needs the existing Linux WebKit shared-library path available to its launcher. No new npm browser/test dependency was installed for this change.

The harness records browser versions, raw error lists, viewport measurements, image-source checksums, source/build stability and every scenario's actual result. A script's existence is not a passing result: see `final/browser-results.json` after execution.

## Touch and Safari limits

Chromium can dispatch a native browser touch gesture through its DevTools protocol, which exercises the actual native scroll + pointer cancellation + resume behavior. It is still an automated browser, not a physical device.

Linux WebKit does not expose native touch dragging through this Playwright environment. Its native horizontal wheel scrolling, mouse dragging, pointer lifecycle, keyboard/reduced motion and rendered responsive layout are tested. These are not represented as a successful physical iPad Safari swipe test. Physical iPad portrait/landscape, finger swipe/momentum, brand tap, pinch zoom, all five Quiz steps and Compare table scrolling remain an explicit device-review step.

## Historical fixture failures

The preceding approved product-data work already documented stale Phase 5–9 assumptions (such as requiring a verified Yamaha price to remain null) and a shared price-filter fixture that assumed no priced guitars. Those expectations are not changed or weakened for this Home redesign. Their prior raw outputs remain in `docs/premium-quiz-compare/tests/`; current catalog facts and data-trust rules are protected against accidental edits.

## Motion measurement and native input

The automatic target stays at **30 CSS pixels/second**. Final acceptance reads native position and animation time together inside requestAnimationFrame, then requires **27–33px/second**. This is stricter than the original broad displacement check of 10–40px during a nominal 800ms host wait. The original seamless-boundary maximum of 3px per observed frame, no-blank coverage and all gesture/hold checks remain intact.

A trusted passive wheel event can be delivered after the compositor has already scrolled. Therefore its event-listener position is not used as a pre-input baseline. The wheel probe captures native position/time in a frame before dispatch, records the trusted event, subtracts the maximum possible 30px/second autoplay drift before delivery, and requires more than 70 remaining native pixels while the rail is in manual mode. It explicitly rejects a return to automatic motion before that requirement is met, so later autoplay cannot make a failed gesture pass. Native movement is observed with a bounded two-second deadline instead of assuming a fixed 200ms wait includes asynchronous event delivery and scrolling.

Initial failures are retained separately: `initial-webkit-failure/` records the real discarded-animation-time bug; `initial-webkit-wheel/` records the real momentum-cancellation bug; `initial-passive-wheel-sampling/` records the later test-only passive-event baseline mistake. Causal source and timing evidence is in `webkit-motion-fix/` and `webkit-wheel-trace.json`.

Linux WebKit software rendering showed initial painting stalls of roughly 500–1,000ms in the retained traces. Correct steady motion does not certify fluent startup on a physical iPad. No physical iPad result is claimed.
