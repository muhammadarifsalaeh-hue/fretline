# Phase C final polish QA

These scripts inspect the real existing production app. They do not start a
server, install packages, change product data, intercept requests or replace DOM
content/styles for screenshots. Python Playwright, Chromium and Pillow are the
existing external QA environment, not new application dependencies.

## Before and after captures

Capture baseline **before any app edits** using a separately served immutable
baseline production build. The current baseline has the photographic Córdoba
wordmark. The final app uses the user-approved temporary typography instead.

```bash
FRETLINE_QA_URL=http://127.0.0.1:5210 FRETLINE_QA_STAGE=before python docs/signature-redesign/phase-c-final/tests/capture.py
FRETLINE_QA_URL=http://127.0.0.1:5213 FRETLINE_QA_STAGE=after python docs/signature-redesign/phase-c-final/tests/capture.py
```

Ports above are examples; root supplies the actual servers. Optional
`FRETLINE_QA_VIEWPORTS=desktop,tablet,mobile` selects named viewports. Default six
captures:1440desktop,1024tablet-landscape,768tablet,390mobile,320small-mobile,
1280reference-desktop. Reports and screenshots default to `phase-c-final/`;
`FRETLINE_QA_OUTPUT_DIR` can select another output directory.

Each capture scrolls the actual document, waits for native lazy loading, image
decoding and local fonts, then captures the unchanged Home viewport/full page.
Brands images are crops of those full-page pixels using measured document
bounds. Reports contain actual image source dimensions, brand geometry, Hero
text/image bounds, icon alignment and section spacing. Cropping a real screenshot
does not establish photographic/typographic similarity to the reference; root
must inspect the images and disclose differences.

## Focused polish acceptance

```bash
FRETLINE_QA_URL=http://127.0.0.1:5213 python docs/signature-redesign/phase-c-final/tests/visual-acceptance.py
```

Thirteen cases:

- Six widths: no page overflow, one H1, no broken images, ten loaded correct-brand
  photographs, nine genuine image marks and one explicitly typographic Córdoba,
  equal cards,44px arrow areas, separate count/arrow positions, aligned count
  baselines, contained marks and coherent Hero text/action/search flow.
- Five widths: real desktop/Mobile navigation from Home; keyboard open/Escape
  restores focus, touch1024 disclosure, Mobile dialog trapping/route closure,
  Browser Back and actual search focusing via Header or BottomBar.
- Normal-motion desktop: restrained hover feedback appears while photo crop and
  card size stay unchanged; genuine keyboard focus is visible.
- Reduced motion: duration limits apply, reveals remain visible/untransformed.

Artwork frames may have deliberately different optical centers; frame positions
are recorded, not forced into an artificial equality that distorts real logos.
Exact guitar subject cropping, logo ink legibility, vintage color and visual
fidelity require manual screenshot review. No physical Safari/iPad claim is made.

## Existing functional regression suites

Run the existing Home acceptance against the final app with its output directed
here. Its shared brand assertion now accepts the final typed Córdoba while
strictly requiring the nine original marks and ten licensed backgrounds.

```bash
FRETLINE_QA_URL=http://127.0.0.1:5211 FRETLINE_QA_OUTPUT_DIR=/workspace/fretline/docs/signature-redesign/phase-c-final python docs/signature-redesign/phase-c/tests/home-acceptance.py
FRETLINE_QA_URL=http://127.0.0.1:5211 FRETLINE_QA_REPORT=/workspace/fretline/docs/signature-redesign/phase-c-final/shared-regression.json python docs/signature-redesign/phase-b/tests/acceptance.py
FRETLINE_QA_URL=http://127.0.0.1:5211 python docs/signature-redesign/phase-c-final/tests/regression-gallery.py
FRETLINE_QA_OUTPUT_DIR=/workspace/fretline/docs/signature-redesign/phase-c-final python docs/signature-redesign/phase-c/tests/assets-check.py
```

The copied79gallery regression preserves all original assertions; only the
report directory and run label change. Existing Home/shared suites cover actual
search, filters/sorting/history, category/brand destinations, featured tabs,
carousel, Wishlist persistence,2–4 Compare limit/removal, full Quiz/navigation,
real product galleries and source/trust/archive behavior. The offline asset
audit retains19registered asset hashes, nine mark reuse bases, ten photo sources
and25unchanged product-data/image hashes. It records Córdoba's historical
photographic-wordmark evidence as inactive in the final UI, and never grants or
invents new logo permission.

All commands above are **instructions to run**, not claims they have passed.
Root records actual results only after execution. Browser JSON reports retain
failed cases and console/runtime/request failures; any such failure exits nonzero.
