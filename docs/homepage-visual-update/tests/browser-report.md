# Actual Homepage browser verification

- Final result: **42/42 grouped checks**, overall **PASS**.
- Engines: {"chromium": "154.0.8037.57", "webkit": "26.5"}.
- Viewports: Desktop 1440×1000; iPad landscape 1194×834; portrait 768×1024; Mobile 390×844; narrow Mobile 320×740; portrait tablet 1024×1366.
- Native iPadOS Safari / physical iPad: **not tested**. Linux WebKit and synthetic touch were actually executed.
- Console/runtime/HTTP/request errors: `{"consoleErrors": 0, "runtimeErrors": 0, "networkErrors": 0, "failedRequests": 0}`.
- Source and build unchanged during the final run: `True`.
- Before HTML SHA-256: `c462802a6f4b51b37cd043b678c44a501943649cf47d5ebdcd841ceb49f7b3d8`.
- After HTML SHA-256: `37ad79d1e4f440d7244bee226cef5ff4805e18694695df1d411919fa4b887765`.

Checks cover category image decoding/full-frame fit, 2×2 or stacked layout, actual Catalog counts and routes, the exact authorized Practice/Find/Compare copy and CTA routes, responsive card geometry, text containment and page overflow, preserved Hero/brand/Featured, real search/wishlist/Compare state and Practice42 selection, Hero autoplay and brand autoplay/drag/resume.

[Before / after gallery](before-after.html) · [Raw browser result](after/browser-results.json)

## Individual final checks

- PASS `chromium-desktop-fullbleed-category-grid`
- PASS `chromium-desktop-three-mode-card-layout`
- PASS `chromium-desktop-preserved-home-sections`
- PASS `chromium-desktop-navigation-real-data-state`
- PASS `chromium-landscape-fullbleed-category-grid`
- PASS `chromium-landscape-three-mode-card-layout`
- PASS `chromium-landscape-preserved-home-sections`
- PASS `chromium-portrait-fullbleed-category-grid`
- PASS `chromium-portrait-three-mode-card-layout`
- PASS `chromium-portrait-preserved-home-sections`
- PASS `chromium-mobile-fullbleed-category-grid`
- PASS `chromium-mobile-three-mode-card-layout`
- PASS `chromium-mobile-preserved-home-sections`
- PASS `chromium-mobile-navigation-real-data-state`
- PASS `chromium-narrow-fullbleed-category-grid`
- PASS `chromium-narrow-three-mode-card-layout`
- PASS `chromium-narrow-preserved-home-sections`
- PASS `chromium-portrait-edge-fullbleed-category-grid`
- PASS `chromium-portrait-edge-three-mode-card-layout`
- PASS `chromium-portrait-edge-preserved-home-sections`
- PASS `chromium-normal-motion-hero-brand`
- PASS `webkit-desktop-fullbleed-category-grid`
- PASS `webkit-desktop-three-mode-card-layout`
- PASS `webkit-desktop-preserved-home-sections`
- PASS `webkit-desktop-navigation-real-data-state`
- PASS `webkit-landscape-fullbleed-category-grid`
- PASS `webkit-landscape-three-mode-card-layout`
- PASS `webkit-landscape-preserved-home-sections`
- PASS `webkit-portrait-fullbleed-category-grid`
- PASS `webkit-portrait-three-mode-card-layout`
- PASS `webkit-portrait-preserved-home-sections`
- PASS `webkit-mobile-fullbleed-category-grid`
- PASS `webkit-mobile-three-mode-card-layout`
- PASS `webkit-mobile-preserved-home-sections`
- PASS `webkit-mobile-navigation-real-data-state`
- PASS `webkit-narrow-fullbleed-category-grid`
- PASS `webkit-narrow-three-mode-card-layout`
- PASS `webkit-narrow-preserved-home-sections`
- PASS `webkit-portrait-edge-fullbleed-category-grid`
- PASS `webkit-portrait-edge-three-mode-card-layout`
- PASS `webkit-portrait-edge-preserved-home-sections`
- PASS `webkit-normal-motion-hero-brand`

## Unchanged Quiz / Compare regression

- Original checker: `docs/final-ui-refinement/tests/quiz-compare-browser.py`, not edited for this work.
- Final result: **13/13**, overall **True**.
- Both actual Chromium and WebKit; Desktop and Mobile five-step Quiz flow, six frozen recommendation fixtures per engine, real four-model Compare/picker/limit/tabs/differences/share/remove/history/reload/clear, additional responsive widths, actual Chromium clipboard.
- [Raw regression report](quiz-compare/browser-results.json).

## Retained initial diagnostics

The first incomplete run found real category minimum-width overflow at 768px, 390px and 1024px portrait. The application CSS was fixed before final acceptance. A separate harness issue compared viewport coordinates recorded after separate lazy-image scrolling; final geometry uses document coordinates with the original row/column/containment/overflow thresholds. Both initial incomplete reports are retained under `diagnostic-before-category-fix/` and `diagnostic-incomplete-quiz-compare/`; they are not counted as final passing suites.

The subsequent `diagnostic-font-navigation/` run passed all42 functional/layout groups but correctly failed overall because rapid Practice-to-Home hard navigation cancelled one WebKit Instrument Serif italic font request. Before final acceptance the harness was changed to await two actual paint frames and document.fonts.ready before leaving a page, with no application changes and the zero-cancellation criterion retained. The final42-case focused run was rerun fully on the same frozen application build; the already clean13-case original Quiz/Compare result was retained.

Tall raw component screenshots can contain fixed navigation in the stitched capture. Individual final mode-card captures avoid most of that artifact without hiding product CSS.
