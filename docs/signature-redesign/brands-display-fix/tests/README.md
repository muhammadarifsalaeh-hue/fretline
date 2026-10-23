# Brand Directory display-fix browser QA

These scripts target the existing production app. They do not install browser
engines, start servers, edit app files, mutate the catalog, or visit/replace Home.
Root supplies an immutable Vite preview and runs each available engine. Existing
Python Playwright, Pillow and Chromium are external QA tools, not new app dependencies.

```bash
FRETLINE_QA_ENGINE=chromium FRETLINE_QA_URL=http://127.0.0.1:5304 FRETLINE_QA_STAGE=before python docs/signature-redesign/brands-display-fix/tests/capture.py
PLAYWRIGHT_BROWSERS_PATH=/tmp/fretline-browser-engines FRETLINE_QA_ENGINE=webkit FRETLINE_QA_URL=http://127.0.0.1:5304 FRETLINE_QA_STAGE=before python docs/signature-redesign/brands-display-fix/tests/capture.py
FRETLINE_QA_ENGINE=chromium FRETLINE_QA_URL=http://127.0.0.1:5305 FRETLINE_QA_STAGE=after python docs/signature-redesign/brands-display-fix/tests/capture.py
PLAYWRIGHT_BROWSERS_PATH=/tmp/fretline-browser-engines FRETLINE_QA_ENGINE=webkit FRETLINE_QA_URL=http://127.0.0.1:5305 FRETLINE_QA_STAGE=after python docs/signature-redesign/brands-display-fix/tests/capture.py
FRETLINE_QA_ENGINE=chromium FRETLINE_QA_URL=http://127.0.0.1:5305 python docs/signature-redesign/brands-display-fix/tests/acceptance.py
PLAYWRIGHT_BROWSERS_PATH=/tmp/fretline-browser-engines FRETLINE_QA_ENGINE=webkit FRETLINE_QA_URL=http://127.0.0.1:5305 python docs/signature-redesign/brands-display-fix/tests/acceptance.py
```

Ports above are examples. This run used port 5400 for the immutable baseline and
5402 for the final app. Reports record the actual base URL, engine version, user agent,
geometry, image responses and paint observations. `FRETLINE_QA_OUTPUT_DIR` selects
the evidence directory. `FRETLINE_QA_VIEWPORTS=desktop,tablet,mobile` limits captures;
`FRETLINE_QA_CASES=rendering,photo-404` selects acceptance prefixes.

## Actual Before / After captures

Five sizes: 1440×1000, 1024×768, 768×1024, 390×844 and 320×740. Each produces actual
viewport/full-page PNGs plus a native-scrolled card-grid viewport. Native scrolling
triggers lazy loading; local fonts and loaded images are decoded. There is no
screenshot-only DOM/style replacement or generated image. Normal screenshots use
the real reduced-motion preference to avoid irrelevant reveal timing; Directory
does not depend on an entrance animation.

Before records actual geometry/rendering, even if it is broken; a capture pass
means evidence was collected, not that the baseline UI passed. After requires ten
correct-brand photos, nine genuine marks plus the Córdoba name, non-collapsed
cards, actual counts/URLs, and no page overflow. Each card is also natively scrolled
into view and captured to memory for bright identity-pixel evidence. That paint
check supports visible lettering; it does not independently authenticate a
photographic subject. Root must review actual screenshots against the reference.

## Explicit reduced-layout-support diagnostic

```bash
FRETLINE_QA_ENGINE=chromium FRETLINE_QA_URL=http://127.0.0.1:5304 FRETLINE_QA_STAGE=before FRETLINE_QA_DISABLE_ASPECT=1 FRETLINE_QA_VIEWPORTS=tablet python docs/signature-redesign/brands-display-fix/tests/capture.py
FRETLINE_QA_ENGINE=chromium FRETLINE_QA_URL=http://127.0.0.1:5305 FRETLINE_QA_STAGE=after FRETLINE_QA_DISABLE_ASPECT=1 FRETLINE_QA_VIEWPORTS=tablet python docs/signature-redesign/brands-display-fix/tests/capture.py
```

These separate artifacts deliberately disable `aspect-ratio` with an injected
style to test resilience when ratio sizing is unavailable or ignored. They are
labelled `diagnostic-aspect-disabled`, `syntheticLayoutFault: true`, and explicitly
**are not claimed as a recording of physical Safari behavior**. Before reports
observed collapsed heights; After must preserve useful card height and artwork.

## Twelve acceptance cases per available engine

- Five normal responsive/rendering cases: ten brands, 200 unique source guitars,
  20 per brand, correct asset mapping, loaded dimensions, visible/non-collapsed
  card/mark boxes, actual white lettering pixels and clean normal requests.
- One separately labelled lost-ratio fault case, using the deliberate CSS above.
- One actual destination case clicks all ten cards and checks Catalog brand query,
  20-result total and that visible guitar IDs belong to the requested brand.
- One existing-function case covers search, all sorts, type/country combinations,
  empty/clear and Back/Forward. Country data remains explicitly unverified.
- Four intentional image failures: photo 404, logo 404, photo corrupt 200 and logo
  corrupt 200. Requests are intercepted only in these labelled fault cases. They
  require visible name/photo fallbacks, real counts, useful card height and an
  actual filtered-Catalog navigation. Expected network/decode errors are retained
  separately from clean normal-run errors; runtime errors always fail.

The app must expose `data-photo-status="error"` / `data-logo-status="error"` on a
card or its appropriate descendant, visible `[data-brand-fallback]` name text,
and `[data-brand-photo-fallback]` or `[data-photo-fallback]` photo fallback. These
are failure-state observations, not permission to promote image trust metadata.

WebKit on Linux provides real WebKit engine coverage. It is **not physical iPad
Safari**, and does not validate the exact iPadOS/GPU/network environment. If the
engine cannot launch, retain its harness failure and report that limitation;
never substitute a Chromium user-agent string and call it Safari. Root records
actual results only after execution. Commands above do not establish a pass.

## Combined failure and this run's external WebKit environment

`all-image-failure.py` additionally fails all ten photos and nine image logos
together at 320px. It verifies visible typography/photo fallbacks, checks every
rendered text line is contained (including Epiphone), checks counts and paint,
and clicks through to the correct filtered Catalog. All faults are deliberate
HTTP404 interceptions and remain separately recorded.

```bash
FRETLINE_QA_ENGINE=chromium FRETLINE_QA_URL=http://127.0.0.1:5402 python docs/signature-redesign/brands-display-fix/tests/all-image-failure.py
```

For each WebKit command in this managed environment the runner also supplied
these per-command variables (including the combined-failure script):

```bash
XDG_CACHE_HOME=/tmp/fretline-webkit-cache \
XDG_CONFIG_HOME=/tmp/fretline-webkit-config \
GSETTINGS_BACKEND=memory \
PLAYWRIGHT_BROWSERS_PATH=/tmp/fretline-browser-engines \
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 \
FRETLINE_QA_ENGINE=webkit FRETLINE_QA_URL=http://127.0.0.1:5402 \
python docs/signature-redesign/brands-display-fix/tests/all-image-failure.py
```

The isolated WebKit runtime used four official Debian libraries, extracted under
`/tmp` and linked into the downloaded engine's bundled library directory; hashes
are in `../webkit-libraries.json`. Optional GTK GUI validation is skipped because
the working headless WPE engine does not require those GUI libraries. This is a
record of a working external QA runtime, not an app dependency or a claim that
every host dependency check passed. It does not grant physical Safari coverage.
