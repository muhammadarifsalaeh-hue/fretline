# Phase C browser checks

These scripts inspect the actual application served by the existing production
preview. They do not start a server, install dependencies, mock network responses,
change product records, replace images, or inject screenshot styles.

Use the existing Python Playwright/Chromium and Pillow environment. From the repo:

```bash
FRETLINE_QA_URL=http://127.0.0.1:5203 python docs/signature-redesign/phase-c/tests/home-acceptance.py
FRETLINE_QA_URL=http://127.0.0.1:5203 python docs/signature-redesign/phase-c/tests/capture.py
FRETLINE_QA_URL=http://127.0.0.1:5203 FRETLINE_QA_RUN=production python docs/signature-redesign/phase-c/tests/regression-gallery.py
```

`home-acceptance.py` records actual Home search/autocomplete, five quick filters,
featured collection tabs and original models, carousel, Wishlist/Compare controls,
four category counts and routes, all ten brand collections, keyboard focus,
working Quiz entry links, and the compact/full live comparison. Geometry checks
use 1440, 1024, 768, 390 and 320px viewports, including equal brand-card heights,
five/three/two columns, contained logos or explicit text fallbacks, whole-card
links, 44px arrow affordances and page overflow. Source logo-slot counts describe
rendered UI; image rights must also pass the repository asset checks.

The identity reader in `support.py` reads only local IDs, category and featured
flags to compare the UI with the existing catalogue. It does not replace
`npm run catalog:check`, `npm run images:check` or the existing Phase 4–9 checks.
It does not implement another public-data trust or scoring algorithm.

`capture.py` saves real Home viewport/full-page and Brands screenshots in
`phase-c/after/`. It first scrolls the real document to trigger native lazy
loading and reveal observers, then waits for fonts, decoded painted images and
animation frames. Brands screenshots are crops of the untouched full-page PNG
using recorded document bounds, which avoids fixed-navbar overlap in the section
review. Screenshots are captured at all five widths, so the required desktop,
tablet and mobile images are available along with the two additional QA widths.

`regression-gallery.py` preserves the Phase B 79-check Pacifica/shared-feature
suite; only its default port, run label and output directory change. For the full
existing Phase B flow tests, also run its original `acceptance.py` against port5203
with an explicitly named output report to avoid overwriting earlier evidence.

Focused reruns:

```bash
FRETLINE_QA_CASES=brands,compare FRETLINE_QA_REPORT=home-focused.json python docs/signature-redesign/phase-c/tests/home-acceptance.py
FRETLINE_QA_VIEWPORTS=desktop,mobile FRETLINE_QA_REPORT=capture-focused.json python docs/signature-redesign/phase-c/tests/capture.py
```

JSON reports preserve passed and failed cases, console/runtime errors, failed
requests, measurements and screenshot paths. An unsuccessful case/error produces
a nonzero exit code. Functional cases use separate browser contexts, resetting
only test-owned Wishlist/Compare storage once per context while preserving it
across page changes/reloads.

These are Chromium/Linux tests with touch emulation where appropriate. They do
not claim physical Safari/iPad testing. Layout assertions do not establish visual
fidelity to the attached reference: compare the actual screenshots manually and
record typography/photo/logo limitations honestly. No pixel-diff score is claimed
without a local copy of the original reference image.

Additional current checks:

```bash
python docs/signature-redesign/phase-c/tests/assets-check.py
python docs/signature-redesign/phase-c/tests/reference-capture.py
python docs/signature-redesign/phase-c/tests/performance.py
node docs/signature-redesign/phase-b/tests/catalog-price.mjs
node docs/signature-redesign/phase-b/tests/scroll-focus.mjs
```

The asset check is offline consistency/safety/evidence validation, not a new
permission grant. The extra reference capture measures actual layout at1280px.
Performance diagnostics use fresh local production browser contexts and normal
motion, without throttling; they are not Lighthouse or real-user measurements.
