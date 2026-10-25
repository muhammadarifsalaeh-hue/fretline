# Independent trainer acceptance

These tests write only their own reports/screenshots. They do not build the app,
start a server, edit the application, or certify an anatomical hand pose.

`reference-voicings.json` is a separate conventional-voicing fixture. The music
audit also derives absolute notes from standard tuning, checks the named chord
intervals and bass note, and checks that reused fingers have playable declared
barres. Conventional open C7 `x32310` intentionally omits G; that exception must
be declared in the data. Every other entry contains all named chord tones.
Alternative finger assignments are accepted when they satisfy the physical
finger/barre constraints.

```sh
FRETLINE_QA_OUTPUT_DIR=docs/practice-trainer/tests/reports \
node docs/practice-trainer/tests/chord-audit.test.mjs

python docs/practice-trainer/tests/browser-trainer.py \
  --url http://127.0.0.1:5440 --engine chromium \
  --output docs/practice-trainer/tests/reports/chromium

PLAYWRIGHT_BROWSERS_PATH=/tmp/fretline-browser-engines \
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 \
XDG_CACHE_HOME=/tmp/fretline-webkit-cache \
XDG_CONFIG_HOME=/tmp/fretline-webkit-config GSETTINGS_BACKEND=memory \
python docs/practice-trainer/tests/browser-trainer.py \
  --url http://127.0.0.1:5440 --engine webkit \
  --output docs/practice-trainer/tests/reports/webkit

python docs/practice-trainer/tests/run-regressions.py \
  --url http://127.0.0.1:5440 \
  --output docs/practice-trainer/tests/reports/regressions

PLAYWRIGHT_BROWSERS_PATH=/tmp/fretline-browser-engines \
PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1 \
XDG_CACHE_HOME=/tmp/fretline-webkit-cache \
XDG_CONFIG_HOME=/tmp/fretline-webkit-config GSETTINGS_BACKEND=memory \
python docs/practice-trainer/tests/camera-controls.py \
  --url http://127.0.0.1:5440 \
  --output docs/practice-trainer/tests/reports/camera-controls
```

The trainer browser suite has 21 cases: all 42 selected and compact diagrams;
search and six type filters; URL/Back/Forward/reload and keyboard selection;
five viewport widths; deferred loading; unavailable WebGL and real context
loss; actual scene-module HTTP503 with same-document distinct-URL retry;
touch; route lazy loading; repeated SPA unmount/Back navigation; actual hand-GLB
loading and failure/retry; explicit prototype review at desktop, tablet and
mobile; and actual idle-frame/draw-call/repeated-SPA lifecycle measurements. It checks
real SVG circle/text/grid/barre geometry against the independent fret fixture,
not just diagnostic attributes. Actual WebGL screenshots and native Chromium
CDP pinch cover camera rendering. Injected faults are labelled and separated
from unexpected errors.

Hand checks require normal lessons to hide every unapproved candidate. A loaded
candidate must apply its own actual bone/root transform fingerprint; a chord ID
or a precomputed data hash alone is insufficient. Explicit review captures C
and the F barre at the default, side, back and player cameras when candidates
exist. Those screenshots are named `UNAPPROVED-prototype-*` and include separate
warning captures. Their presence establishes rendering/lifecycle behavior only.
If a source pose independently receives all four required anatomical review
gates, its ordinary visible state and four views are checked separately. The
browser suite never supplies those anatomical approvals itself. Reports record
the actual production asset hashes and reject a build changed during a run.

The performance case measures that an idle canvas stops rendering, real zoom
causes a render and then settles, and repeated navigation removes the canvas.
Chromium also reports forced-GC JavaScript heap measurements after three
unmounts; these exclude native driver/GPU allocations and cannot establish
physical iPad frame rate or GPU memory use.

Run heavyweight browser suites serially to avoid software-renderer CPU pressure
making cold loads appear to fail. To regenerate the per-chord evidence matrix
after both engines finish:

```sh
python docs/practice-trainer/tests/summarize-status.py \
  --reports docs/practice-trainer/tests/reports
```

`chord-status-42.json` reports independent music results, full/compact rendered
SVG evidence from each engine, source diagram status, source/candidate hand
status, and actual runtime hand diagnostics separately. It does not change the
application's diagram or hand statuses.

The regression runner invokes the unchanged shared 18-case and Pacifica
79-check Chromium suites, plus the existing five-width camera suite in each
browser: 107 checks total. Its only adaptations are output directories and the
existing browser runtime environment variables. The separate two-engine camera
control supplement checks all seven presets (including Front, Headstock and
Full neck), all four orbit/zoom buttons, real pixel changes, keyboard/button
reset, unchanged model geometry, and the full-neck head/nut/body framing.

Final frozen-build evidence is in `reports/final-chromium`,
`reports/final-webkit`, `reports/final-regressions`, and
`reports/final-camera-controls`; `reports/final-summary.json` joins the counts
and limitations. Initial failure logs/JSON remain available. Only redundant
interim PNGs from this task were archived outside Git; their original paths,
archive paths and exact SHA256 hashes are in
`reports/interim-screenshot-archive.json`. Complete final screenshots remain
with the canonical reports.

Linux WebKit is not physical Safari on iPadOS. These results cannot establish
iPad GPU performance or native iPad pinch behavior. Musical data and SVG
diagram correctness are separate from anatomical hand mesh, contact, skin,
thumb, wrist, arm, sleeve, or pose verification. External learning-source
readings are recorded by the data/reference audit; these tests do not claim to
have independently opened those pages.
