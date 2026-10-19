# Phase 3 verification

- Production browser suite: 64/64 assertions.
- Gallery suite: 13/13 assertions with in-memory SVG fixtures only.
- Final build smoke: 5/5 assertions, including the retained #specs deep link.
- Normal production interactions: no page/console errors or failed requests.
- Deliberately rejected route chunks and missing fixture images are fault tests,
  not production catalog data. See results JSON and logs for exact evidence.

The production browser suite ran before the final #specs compatibility addition;
the final smoke ran after that addition and recaptured Catalog/Detail screenshots
from the latest build. The gallery source was unchanged between these checks.

Dependencies for QA are Python Playwright and system Chromium, available in the
execution environment. They are not dependencies of the app.

```sh
npm run build
npm run preview -- --host 127.0.0.1 --port 4173
# another terminal
python docs/qa-phase3/browser-qa.py
python docs/qa-phase3/final-smoke.py
# Gallery fixture tests additionally use the dev server:
npm run dev -- --host 127.0.0.1 --port 5173
# another terminal
python docs/qa-phase3/gallery-qa.py
```

Optional variables: FRETLINE_QA_URL, FRETLINE_DEV_URL, CHROMIUM_BIN.
Synthetic touch events verify the handler; no physical mobile-device claim.
Screenshots fast-forward finite animations; no substitute product photos are used.
