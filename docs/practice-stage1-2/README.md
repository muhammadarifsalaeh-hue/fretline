# Fretline 3D Chord Trainer — Stage 1–2

Baseline: `9f7b35d7a0daea8a579976a5534ffb67d90f06a9`.
Working branch: `feature/guitar-practice-3d`. Master was fetched and matched the
baseline; the working tree was clean before creating this branch. No reset,
replacement project, catalog edits or work on other practice modes was used.

## Implemented scope

- New lazy `/practice` route, plus a working Practice entry in the existing
  desktop/mobile navigation. Existing page compositions remain unchanged.
- Page-scoped black/charcoal, champagne-gold and warm-white design, using the
  existing typography/tokens. Responsive layout covers 1440, 1024, 768, 390 and
  320px. No new hero photo, fake hand, audio or lesson controls were added.
- A **real WebGL2 / Three.js** study neck, six strings, nut, twelve correctly
  spaced curved fret wires, inlays and a generic headstock. Procedural grain and
  geometry are not catalog product photography or model specifications.
- Native drag orbit, pinch zoom, keyboard orbit/zoom, zoom buttons, three camera
  presets and Reset Camera. Camera changes render different actual canvas pixels.
- C, G, D, Em and Am use one immutable data source for selectors, SVG diagrams,
  finger/string labels and schematic numbered 3D markers. Open/muted strings are
  explicit. These markers are **not an anatomical hand model**.
- Loading state, unavailable-WebGL fallback, context-loss recovery and failed
  module recovery, with a functioning Retry button. The 2D chord information
  remains available when 3D is unavailable.
- No continuous render loop or auto-rotation; frames follow interaction, resize
  or chord changes. Pixel ratio is capped at 1.75. GPU resources/listeners are
  disposed on retry and route exit. Keyboard Tab is not trapped.

## Design reference and remaining work

The supplied reference guides the black/gold studio, chord choices, large viewer,
camera controls and adjacent chord information. This stage deliberately shows a
generic isolated neck rather than claiming the reference's photoreal human hand
and full guitar are implemented. The whole-neck default view is relatively thin
on mobile; interactive zoom is available for a closer view.

Human hand asset/rig, anatomical finger poses, step-by-step instruction and chord
audio remain unimplemented, pending review. No song, scale or free-play mode was
started. The data reserves `handPose: null`; coordinate/rig integration is
documented in [feature architecture](../../src/features/practice/README.md).

## WebKit failure found and fixed during QA

Testing exposed WebKit caching a failed ES module URL **across document reloads**.
A real local HTTP503 server reproduced it without Playwright interception: after
the server recovered, Reload still did not fetch the failed scene URL. Importing
that URL with a fresh query succeeded. Clearly labelled pre-fix diagnostic
evidence is retained in [diagnostics](diagnostics).

The final loader uses a small Vite plugin to emit the **bundled module URL**,
keeping the scene/engine in one self-contained lazy chunk. A failed import Retry
uses a fresh query, without reloading the page or losing the chosen chord. A
successful module factory is reused for context recovery and SPA return visits;
its recovery revision is retained for this build/session where storage permits.
No Wishlist, Compare or guitar data storage is changed. Source code is not
duplicated into alternative retry modules.

## Dependencies and performance boundary

Only **Three.js 0.186.1 (MIT)** was added, with an exact lockfile entry. Its full
notice ships as `public/licenses/three-MIT.txt`. React Three Fiber, Drei, animation
libraries, hand assets and additional runtime packages were not added.

The final production engine/scene chunk is approximately **589KB minified /
150KB gzip**. Vite reports its normal >500KB chunk warning; the build succeeds.
This warning was not hidden by raising the limit. The chunk is loaded only when
Practice mounts; actual network tests check that Home, Brands and Catalog do not
request it. Battery life, thermal behavior and physical-device frame rates have
not been measured.

## Test evidence

| Check | Result / evidence |
| --- | --- |
| `npm run build` | [Passed](build.txt), with the explicitly retained engine chunk-size warning |
| `npm run catalog:check` | [Passed](catalog.txt): 200 unique guitars, ten brands, twenty each |
| `npm run images:check` | [Passed](images.txt): existing images/rights/placeholders unchanged |
| `npm run practice:check` | [13/13 passed](chord-geometry-tests.txt): equal temperament, octave position, standard tuning, exact voicings, triads and finger data |
| Actual Chromium production suite | [15/15 passed](browser-chromium.json) |
| Actual Linux WebKit production suite | [15/15 passed](browser-webkit.json) |
| Vite Dev smoke | Passed in [Chromium](dev-smoke-chromium.json) and [WebKit](dev-smoke-webkit.json): real WebGL2, chord change, rotate/zoom/reset |
| Real HTTP503 recovery in WebKit | [Passed](http-module-recovery-webkit.json), without request interception; fingerprints match the final build |
| Existing shared UI regressions | [18/18 passed](shared-regression.json), including 40 responsive route visits |
| Existing gallery/function regressions | [79/79 passed](regression/browser-practice-stage1-2.json) |
| Bundle isolation and notice | [Passed](build-isolation.json): self-contained engine, unchanged shared vendor content hash, matching MIT notice |

The fifteen browser cases cover real WebGL2/pixels at all five widths, camera
orbit/zoom/reset/presets, keyboard and pointer drag, real SVG chord geometry,
all chord choices, lazy-route isolation, loading state, unavailable WebGL,
actual context loss, HTTP503 module recovery, repeated SPA exit/Back and touch.
The final keyboard case also checks that Ctrl/Command/Alt shortcuts are not
intercepted by the canvas. Native multi-touch pinch is tested through Chromium
CDP; WebKit button taps are tested without claiming physical iPad pinch coverage.

Normal runs have zero unexpected console/runtime errors, failed requests or bad
HTTP responses. Deliberate HTTP/decode/context failures are separately retained
as expected fault evidence. See the [reproduction commands](tests/README.md).

Actual screenshots for review:

| View | Capture |
| --- | --- |
| Desktop 1440px | [Full page](screenshots/webkit/practice-desktop.png) |
| Tablet landscape 1024px | [Full page](screenshots/webkit/practice-tablet-landscape.png) |
| Tablet portrait 768px | [Full page](screenshots/webkit/practice-tablet.png) |
| Mobile 390px | [Full page](screenshots/webkit/practice-mobile.png) |
| Small mobile 320px | [Full page](screenshots/webkit/practice-small-mobile.png) |
| Actual 3D canvas | [Neck, desktop](screenshots/webkit/neck-desktop.png) |
| Chords, viewer and controls together | [Desktop workspace](screenshots/webkit/workspace-desktop.png) |

Screenshots are real application/browser output, not mockups or substituted
canvas images. File names beginning `intentional-` deliberately exercise loading
or failure UI; they do not represent an unexpected normal production failure.
Full-page screenshots can show the existing fixed bottom navigation at the
initial viewport boundary. Separate `neck-*.png` captures show actual canvas
pixels without changing the application.

## Protected existing work

[Protected-source evidence](protected-source.json) compares all **173 existing
source files outside the four allowed integration edits** byte-for-byte against
the baseline. This includes Home, Animated Brand Marquee, Brand Directory,
product data/images/rights, Catalog, Compare, Quiz and Wishlist. Guitar IDs and
the 200-model / ten-brand / twenty-per-brand database remain unchanged.

Existing integration edits are limited to App's lazy route, the navigation entry,
TH/EN labels, Vite chunk/loading configuration and package metadata. New feature
files are isolated under `src/features/practice`, `PracticePage.jsx` and the
page-scoped stylesheet. QA scripts and the feature checker are separate from
the production page.

## Device limitations

Actual Linux WebKit 26.5 and Chromium 154 are exercised, including real WebGL2
rendering. Chromium uses SwiftShader software rendering. **No physical iPad or
macOS Safari was available**; these results do not establish exact iPadOS/GPU,
memory, thermal or battery behavior. Touch button input is covered in WebKit;
native multi-finger pinch injection is covered in Chromium only. Physical iPad
pinch remains a user-device verification item.

Stop after Stage 1–2 and review the screenshots before developing the human hand.
No merge or push to master is part of this delivery.

## Open this feature in the existing Codespace

Stop an old Vite process with Ctrl+C, then use the feature branch:

```bash
git fetch origin
git switch feature/guitar-practice-3d
git pull --ff-only origin feature/guitar-practice-3d
npm install
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

Open **Ports → 5173 → Open in Browser**, then `/practice` or the new Practice
navigation entry. This leaves master alone. Codespaces port forwarding itself
is operated from the user's account, not validated by the local browser smoke.
