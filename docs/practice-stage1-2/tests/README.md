# Stage 1–2 external browser QA

Run against a production Vite preview of the existing branch. These scripts use
external Python Playwright/Pillow and existing browsers, not app dependencies.
They do not start servers, mutate source/data, or manufacture preview images.

```bash
FRETLINE_QA_URL=http://127.0.0.1:5410 FRETLINE_QA_ENGINE=chromium \
python docs/practice-stage1-2/tests/browser.py
```

Chromium uses its real software WebGL2 renderer (`--use-angle=swiftshader`,
`--enable-unsafe-swiftshader`), not a static image or substituted canvas. WebKit
uses the actual Linux WPE engine prepared in `/tmp` by the earlier display fix:

```bash
XDG_CACHE_HOME=/tmp/fretline-webkit-cache \
XDG_CONFIG_HOME=/tmp/fretline-webkit-config \
GSETTINGS_BACKEND=memory \
PLAYWRIGHT_BROWSERS_PATH=/tmp/fretline-browser-engines \
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 \
FRETLINE_QA_URL=http://127.0.0.1:5410 FRETLINE_QA_ENGINE=webkit \
python docs/practice-stage1-2/tests/browser.py
```

The isolated WebKit libraries/setup are recorded in
`docs/signature-redesign/brands-display-fix/webkit-libraries.json`. A real WebGL2
context probe succeeded in both engines before the new app was ready. These
commands are not themselves evidence that app tests passed; inspect the saved
`browser-<engine>.json` report after execution.

Fifteen cases cover five responsive widths, actual canvas paint/context,
camera changes/reset/presets, native pointer/keyboard input, five chord diagrams,
route-level lazy loading, deferred-chunk loading state, unavailable WebGL,
actual context loss/retry, scene-module HTTP503 recovery with a distinct URL, repeated SPA
unmount/Back navigation, touch tap and (Chromium only) CDP native multitouch
pinch. Chord checks read actual horizontal/vertical SVG line geometry as well as
accessible string/fret descriptions. `FRETLINE_QA_CASES=rendering,camera-controls`
limits a diagnostic run.
The keyboard case also preserves Ctrl/Command/Alt browser shortcuts while the
canvas is focused; these modifier checks accompany real normal-key/pointer input.
Normal screenshots never replace DOM/CSS/canvas content. Explicit fault cases
intercept only the named capability or resource and are clearly labelled.

The WebGL-unavailable test intentionally returns `null` from WebGL context
creation, then restores the native factory and exercises Retry. The context-loss
test calls the actual `WEBGL_lose_context` extension. The module-failure test
returns HTTP503 for the real combined Three/scene chunk, then restores networking
and requires the actual Retry button to obtain a distinct module URL, preserve
the selected G chord in the same document, and also recover from a subsequent
real context loss. It does not navigate around a failed import from the harness.
Fault diagnostics are kept
separate from unexpected console/runtime/network/HTTP errors.

Linux WebKit is **not physical Safari on iPad**. Viewport, touch and real engine
coverage do not establish exact iPadOS/GPU, battery, memory or thermal behavior.
WebKit native touch-button taps are covered; native multi-finger pinch injection
is available through Chromium CDP only. Physical iPad pinch remains untested.

Existing regressions can run without replacing historical evidence:

```bash
FRETLINE_QA_URL=http://127.0.0.1:5410 \
python docs/practice-stage1-2/tests/shared-regression.py

FRETLINE_QA_URL=http://127.0.0.1:5410 \
FRETLINE_QA_OUTPUT_DIR=/workspace/fretline/docs/practice-stage1-2 \
FRETLINE_QA_RUN=practice-stage1-2 \
python docs/signature-redesign/phase-c-final/tests/regression-gallery.py
```

The shared-regression adapter changes only the existing test script's output
directory. Its eighteen test cases and assertions remain unchanged.

Vite development mode can be smoke-tested separately in either actual engine:

```bash
FRETLINE_QA_URL=http://127.0.0.1:5410 \
FRETLINE_QA_DEV_URL=http://127.0.0.1:5412 FRETLINE_QA_ENGINE=chromium \
python docs/practice-stage1-2/tests/dev-smoke.py
```

For WebKit, use the external runtime variables above and set
`FRETLINE_QA_ENGINE=webkit`. This checks actual WebGL2, chord selection, rotation,
zoom and reset on Vite Dev and captures the production workspace. Reports are
`dev-smoke-<engine>.json`; this does not validate Codespaces port forwarding.

`http-module-recovery.py` serves the unchanged production files on a temporary
local HTTP server. It initially returns a real HTTP503 for the engine chunk,
then restores the server and uses the actual Retry button. It never intercepts
Playwright requests or substitutes canvas pixels. Its recorded module/HTML
checksums identify the exact build tested. Pre-fix diagnostics are kept separate
from the final passing report.
