# Homepage Premium redesign — executed acceptance results

Baseline: `4bbecf86585ab14cca2d23e2b65f090db20a1816`. Final application source and production assets stayed frozen during the completed Home run. Authorized Home composition changes are not treated as protected unrelated files.

| Check | Actual result | Evidence |
|---|---|---|
| Production build | PASS; existing Three.js chunk-size warning retained | [build.txt](build.txt) |
| Home browser acceptance | **32/32 PASS**, Chromium 154.0.8037.57 and Linux WebKit 26.5 | [Final results](final/browser-results.json), [run log](final-run.txt) |
| Existing standalone Quiz/Compare browser regression | **25/25 PASS**, unchanged existing suite on the same frozen production build | [Results](standalone-regression/browser-results.json), [run log](standalone-regression-run.txt) |
| Unrelated-file preservation | PASS: **180** original files byte-identical | [preservation.json](preservation.json) |
| Catalog | PASS: **200 unique models / 10 brands / 20 models each** | [core/catalog.txt](core/catalog.txt) |
| Existing image registry | PASS; existing catalog image gaps remain declared | [core/images.txt](core/images.txt) |
| Practice checks | PASS: **56/56**; no Practice source/model changes | [core/practice.txt](core/practice.txt) |
| Original Phase 4 Quiz/Compare logic | PASS: **19/19** | [core/phase4.txt](core/phase4.txt) |
| Yamaha import isolation/evidence | PASS: **11/11** | [core/yamaha.txt](core/yamaha.txt) |
| New photographic assets | PASS: **39/39** actual file/source/hash/proportion/transparency/budget checks | [Photo results](../photos/checks.json) |
| Focused final carousel regression | PASS: **6/6** on Chromium/WebKit at three viewport sizes | [Focused results](final-carousel/browser-results.json) |

The Home acceptance covers Desktop 1440×1000, tablet 768×1024 and mobile 390×844. Extra containment probes cover 320px, 834px portrait, 1024px landscape and 1194px landscape. All console/runtime/request/HTTP/harness error lists were empty. `sourceAndBuildUnchangedDuringRun` is true.

The existing standalone suite independently completed all 25 scenarios on the same source/build bytes, also with zero console/runtime/request/HTTP/harness errors and unchanged hashes. It covers the dedicated Quiz's full option/answer/back/edit/retake/result flow, six original result profiles, Compare add/remove/max-four selection, category/keyboard controls, real image bindings, sharing/clipboard fallback, history/reload/clear behavior and existing routes. The two suites ran sequentially to avoid browser resource contention during motion measurements.

## Verified behavior

- The logo rail moves automatically with no playback controls, directional buttons, motion-status copy or visible scrollbar. All three copies contain the same ten brand destinations. Each real brand route was actually opened.
- All six measured automatic rates were **29.390–30.615 CSS pixels/second**, within the unchanged 30px/second target and final strict 27–33 band. The actual loop boundary was crossed; maximum observed normalized frame displacement was **1px**, below the retained 3px ceiling, with no blank rail frames.
- Mouse dragging, release/resume, keyboard brand navigation and reduced-motion manual scrolling work. Chromium tablet/mobile cases dispatch native browser touch events and hold the finger for **1,250ms**, proving autoplay does not fight a held gesture.
- Native horizontal wheel movement must exceed **70px while still manual**. The test uses trusted input evidence and subtracts the maximum pre-event autoplay drift. A return to automatic motion before that native movement explicitly fails; automatic pixels cannot supply a pass.
- The inline Home Quiz preserves all original **22 options** in five steps (**5/3/5/5/4**), keeps previous answers, and opens the original results route. Real resulting IDs, scores, reasons and caveats match the frozen original fixture.
- The Home comparison uses the actual registered photographs for Yamaha FG820-12 and Martin D-28 by default. It does not silently save that demo pair. All eight requested preview rows are available, unknown values stay unspecified, saved selection works from two to four guitars, removal updates context, the full table expands, and the dedicated Compare route receives the displayed IDs.
- Actual image files decode; product-card bytes match the publication/illustration registry rather than generic background images. No Three.js or GLB resource is loaded by Home.

## Failures found and corrected

The first complete run passed 29/32 because the hook discarded animation elapsed time above 48ms. Linux WebKit's slow initial painting exposed that real speed bug. The hook now advances by the actual animation timestamp and resets its clock when hidden/offscreen.

A second real bug cancelled WebKit native wheel/touch momentum: adopting a native scroll event redundantly assigned its unchanged value back to `scrollLeft`. Native position adoption now avoids that setter; actual requested movement and seamless rebasing still write as needed.

Two test assumptions were corrected with causal evidence. Position/time are sampled together inside a frame, rather than attaching a new clock reading to a stale frame position. Native wheel delivery is asynchronous, and passive listeners can observe scrolling after its default action; the final probe therefore captures a pre-dispatch frame baseline and observes trusted native movement while manual within a bounded two-second deadline. The speed tolerance was tightened, not relaxed. The native movement, seamless-loop, no-blank-frame and held-touch requirements remain intact.

Raw earlier results remain in [initial-webkit-failure](initial-webkit-failure/), [initial-webkit-wheel](initial-webkit-wheel/) and [initial-passive-wheel-sampling](initial-passive-wheel-sampling/). [Timing/source diagnostics](webkit-motion-fix/README.md) and [native wheel trace](webkit-wheel-trace.json) explain the separate causes. Stale failure PNGs were removed from the final passing folder only after their bytes were retained separately; see [artifact-retention.json](artifact-retention.json).

## Limits and outstanding review

- **No physical iPad Safari was tested.** Linux WebKit is a separate software-rendered test environment. Playwright here does not expose native WebKit touch dragging; its mouse/wheel, rendered responsive layout and keyboard behavior were tested. Chromium's dispatched native touch gesture is also not a physical iPad result.
- Initial Linux WebKit software painting stalls around **500–1,000ms** remain visible in the retained trace. The passing steady-state motion checks do not certify fluent physical-device startup. Portrait/landscape Safari swipe/momentum, tapping logos and all Quiz/Compare actions still need device review.
- Nine actual existing logo files are retained. Córdoba keeps its honest text treatment because a permitted standalone official mark was not obtained; no logo was fabricated.
- Existing catalog photo gaps were not filled with incorrect models. The default real-photo comparison pair contains two acoustic models, unlike the electric/acoustic named pair in the reference. The editorial background independently includes both instrument types.
- Historical Phase 5–9 and one shared price-filter fixture already had stale assumptions before this Home task. Their prior failures remain documented in [the preceding actual test report](../../premium-quiz-compare/tests/final-checks.md). They were not rewritten to manufacture a green result. The current product/scoring files remain byte-identical to the baseline.

Reproduction commands and the exact browser methodology are in [README.md](README.md).
