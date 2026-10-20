# Phase 8 QA evidence

The website keeps its existing npm dependencies. Browser checks use the environment's Python Playwright and `/usr/bin/chromium` (override `CHROMIUM_BIN` where a script supports it). They test Chromium on Linux, not physical iPad/Safari.

## App checks

```bash
npm ci
npm run build
npm run catalog:check
npm run images:check
npm run phase4:check
npm run phase5:check
npm run phase6:check
npm run phase7:check
npm run phase8:check
npm run preview -- --host 127.0.0.1 --port 4188 --strictPort
```

## Browser checks

Run in another terminal while the preview server remains running:

```bash
FRETLINE_QA_URL=http://127.0.0.1:4188 python docs/qa-phase8/browser-phase8.py
FRETLINE_QA_URL=http://127.0.0.1:4188 python docs/qa-phase8-review/catalog-history.py
FRETLINE_QA_URL=http://127.0.0.1:4188 python docs/qa-phase8-review/keyboard.py
FRETLINE_QA_URL=http://127.0.0.1:4188 python docs/qa-phase8-review/route-audit.py
FRETLINE_QA_URL=http://127.0.0.1:4188 python docs/qa-phase8-review/brand-links.py
FRETLINE_QA_URL=http://127.0.0.1:4188 python docs/qa-phase8-review/responsive.py
FRETLINE_QA_URL=http://127.0.0.1:4188 python docs/qa-phase8-review/states.py
```

`states.py` deliberately blocks a Catalog JavaScript chunk and the licensed model photo. Its expected fault errors are recorded separately in `states-results.json`. They are not normal-use console errors. The test restores normal requests before checking recovery.

## Accessibility

Use the pinned axe-core testing tool, outside the app's source/dependency tree:

```bash
curl --fail --location https://unpkg.com/axe-core@4.10.3/axe.min.js --output /tmp/fretline-axe.min.js
FRETLINE_QA_URL=http://127.0.0.1:4188 python docs/qa-phase8-accessibility/check-accessibility.py
```

The audit runs WCAG A/AA tags at 1440px and 390px plus five open modal states. `incomplete` entries require manual review; zero automated violations does not certify full WCAG conformance. `initial-findings.json` preserves the first audit's issues, which were corrected before the final results.

## Results and screenshots

- `summary.json`: final counts and evidence paths.
- `final-checks.json`: actual npm exit codes and log filenames.
- `detail-route-results.json`: every active model's browser-rendered identity.
- `responsive-results.json`: 10 routes × 5 CSS widths, no document overflow or broken images. Four real selected models are used in Compare.
- `catalog-*-full.png`, `compare-390-full.png`: additional full-page views. Other screenshots show the requested viewport.
- `performance-review.json`, `final-asset-sizes.json`: filesystem bytes and gzip estimates, not a Lighthouse score or an external network benchmark.

`docs/qa-phase8-static` contains the initial read-only audit. Use this directory's `final-*` files for final build measurements. The source-data and image-rights audit in `phase8:check` compares against the preserved Phase 7 commit.
