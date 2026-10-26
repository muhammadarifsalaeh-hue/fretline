# Completed Batch 3 browser results

The original serial runner completed with exit code **0** against the frozen
production build. Source and built pose library both hash to
`2e2816f7adf533f80fba931e4d73b592a670a614ea014406903da162b5f01aa1`.
All cross-report build bindings match. No application source was changed during
these runs, and no failed case was replaced or relabelled as passing.

| Actual completed suite | Result |
|---|---|
| Chromium 154.0.8037.57 complete trainer | 21/21 |
| Linux WebKit 26.5 complete trainer | 21/21 |
| Original shared/gallery/camera regressions | 107/107 |
| All seven camera presets, four rotate/zoom controls and reset | 2/2 engines |
| C, Em7, E7, Fmaj7, Dm actual source-to-rendered poses | 4/4 engine/viewport cases |
| Normal/reduced-motion hand reveal, cancellation and disposal | 4/4 engine/motion cases |
| Unexpected console/runtime/network errors | 0 |
| Teaching hands approved by these browser tests | 0 |
| Physical iPad Safari | Not tested |

Both complete trainer suites independently render/check all 42 chord diagrams,
search, filters, history, keyboard, desktop/tablet/mobile layouts, loading,
WebGL/context-loss/module/model fallbacks, touch, lazy routes, SPA cleanup and
performance lifecycle. Their owned startup-settlement adapter retains the same
800 ms idle assertion; the original suite is unchanged. Both complete runs
passed all 21 cases without a focused replacement.

The new five-pose checks compare each actual saved root and all 22 bone rotations
with the applied scene fingerprint, confirm real WebGL pixel changes and warned
inspection, capture four camera views, and verify zoom/reset and automatic
inspection closure on chord changes. The evidence includes **80 four-view canvas
captures plus 20 warning captures** across Chromium/WebKit and desktop/mobile.
The complete report tree contains 284 actual PNGs, including canonical trainer,
layout, gallery, fallback and camera captures.

The deterministic reveal check holds a browser-local clock only for an 80 ms
half-reveal and a 160 ms completion capture. Actual half-to-final rendered pixel
changes are **4,392 (Chromium)** and **4,153 (WebKit)** while source bone and
geometry fingerprints remain constant. Separate native-clock openings complete
and stop: idle frame counts remain **27→27** and **28→28** over 800 ms. Navigating
away during a reveal disposes the old scene: detached-canvas counts remain
**48→48** and **54→54**. Reduced-motion cases reveal immediately.

This is an appearance transition, not a certified physical trajectory between
chords. The seven geometric endpoint passes are established by the independent
actual-mesh audit, not these browser checks. These images do not approve anatomy:
extended proximal fingers/palm presentation and the finite sleeve end remain
visible. All teaching-review gates remain unapproved. Linux WebKit and software
rendering do not establish native iPad Safari compatibility, GPU memory use or
hardware frame rate. Chromium's reported heap covers JavaScript only.

Read [the frozen acceptance report](reports/final-summary.json),
[per-pose captures and source fingerprints](reports/batch-poses/batch-poses-browser.json),
and [actual reveal measurements](reports/hand-reveal/hand-reveal-browser.json).
