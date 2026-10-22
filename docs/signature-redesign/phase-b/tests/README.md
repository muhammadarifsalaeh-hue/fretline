# Phase B browser checks

Run from the existing Fretline root **after** building and starting its production preview on port 5201. These scripts do not install dependencies, start a server, alter catalog data, or publish changes. They require the existing Python Playwright package and `/usr/bin/chromium`.

```sh
FRETLINE_QA_URL=http://127.0.0.1:5201 python docs/signature-redesign/phase-b/tests/acceptance.py
FRETLINE_QA_URL=http://127.0.0.1:5201 python docs/signature-redesign/phase-b/tests/capture-after.py
FRETLINE_QA_URL=http://127.0.0.1:5201 python docs/signature-redesign/phase-b/tests/measure-after.py
python docs/signature-redesign/phase-b/tests/build-review.py
```

`acceptance.py` records individual failures, failure screenshots, console/runtime errors and failed requests. Its exit code fails on any recorded functional/browser error. Use `FRETLINE_QA_CASES=price,filters` to rerun a specific case while fixing a failure. Full coverage includes URL price bounds and history, combined filters/search, sorting/pagination, actual hover image paint bounds, equal-value comparison contrast, desktop navigation disclosure, mobile navigation/filter dialog, touch gallery, persistent Wishlist, Compare 2–4 and duplicate URL normalization, complete Quiz with a previous-answer edit, and eight routes at 1440/1024/768/390/320 pixels.

`capture-after.py` matches the 36 Audit Before screenshot filenames (ten routes at Desktop/Tablet/Mobile, three full pages, three mobile empty states). Its 53 measurements include the additional iPad landscape and 320-pixel sizes. It records broken images and overflow; small-control observations are review evidence, not an automatic WCAG failure. Visible images must complete, decode, and paint before capture. Full-page shots first use real scrolling to activate and settle lazy images, then restore the top; no image source, loading attribute, or style is changed. Capture the same content and storage state before comparing the PNGs.

`measure-after.py` records 14 single-sample local production observations including layout-shift session windows and JS/CSS transfer sizes. It writes `performance/after.json`, preserving the audit baseline. Results are unthrottled local Chromium diagnostics; they are not Lighthouse scores or field Core Web Vitals.

`build-review.py` generates `review.html` with relative Before/After image links and explicitly marks missing captures. It can run without a browser. All results go under `docs/signature-redesign/phase-b/`.

The existing `docs/qa-pacifica-project/browser-gallery.py` remains the deeper 79-check Pacifica/data/image/archived-link regression suite and should also be run against the final build. These scripts do not replace catalog, image, unit tests, or the production build. Physical Safari/iPad remains untested unless the reviewer uses that environment.

Final reports: `../acceptance-final.json` (18 cases), `../category-layout.json` (5 viewport cases), `../regression/browser-phase-b.json` (79 existing checks). Earlier incomplete/flaky harness observations are preserved under `../diagnostics/`; they are not the final acceptance result. A final source-credit CSS correction was verified in the refreshed 53-view screenshot run after the full functional run.

Additional focused checks:

```sh
node docs/signature-redesign/phase-b/tests/catalog-price.mjs
node docs/signature-redesign/phase-b/tests/scroll-focus.mjs
python docs/signature-redesign/phase-b/tests/category-layout.py
```

The current canonical browser command is:

```sh
FRETLINE_QA_REPORT=acceptance-final.json FRETLINE_QA_URL=http://127.0.0.1:5201 python docs/signature-redesign/phase-b/tests/acceptance.py
```

Historical `phase4`–`phase9` scripts preserve earlier catalog/image snapshot assertions. They were not claimed as passing current-catalog acceptance; the existing current Pacifica regression plus catalog/images validators and focused Phase B checks are reported individually.
