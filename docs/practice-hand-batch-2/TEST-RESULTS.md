# Batch 2 validation

The application was frozen before browser QA. Musical data, the model/weights,
and 197 protected original site files are unchanged from `1f71d34`.

| Test | Actual result |
|---|---|
| `npm run build` | Pass; existing large lazy Three.js chunk warning remains |
| `npm run catalog:check` | Pass; 200 models / 10 brands / 20 each |
| `npm run images:check` | Pass; product images and rights records unchanged |
| Existing Practice data/geometry | 56/56 |
| Independent musical/fingering checks | 86/86 |
| Hand runtime trust/loading/disposal | 17/17 |
| Actual pressed-string paths | 42/42 |
| New actual 42-pose geometric audit | 3 pass, 39 rejected; required corrected batch passes |
| New real-mesh negative regressions | 4/4 |
| New fingerprint/cache mutation regressions | 6/6 |
| Chromium browser coverage | 21 cases accepted: 20 original passes + corrected focused idle case |
| Linux WebKit full browser suite | 21/21 |
| Original site/browser regressions | 107/107 |
| All seven camera presets and rotate/zoom/reset buttons | Pass in both engines |
| New Cmaj7/Am7 desktop/mobile rendering | 4/4 engine/viewport cases, 32 view captures |
| Historical Phase 4 static checks | Pass, 19/19 |
| Historical Phase 5–9 static commands | **5 failures retained**, same stale assumptions as baseline |
| Verified teaching hands | **0/42** |
| Physical iPad Safari | **Not tested** |

Source transcripts are the `*-check.txt`, `geometry-run.txt`,
`geometry-negative-tests.txt`, `fingerprint-tests.txt` and `build.txt` files in
this folder. The [42-row mechanical table](CHORD-STATUS-42.md) and its
[full measurements](geometry/summary.json) distinguish actual geometric success
from anatomical acceptance. The all-42 checker immediately rejects self-colliding
poses; it does not claim the unrun contact stages pass for those 39 poses.

## Browser evidence and an investigated failure

The original Chromium run passed 20/21 cases. The idle-performance case initially
failed; that failure is preserved unchanged. An exclusive timeline probe measured
one pending hand-publish frame: `assetReady` was set before the first hand frame
completed under software graphics. The frame counter then remained stable for
more than five seconds; there was no continuous render loop.

An owned copy of the test harness waits for queued startup animation frames and
bounded stable layout before the **same unchanged 800 ms idle assertion**.
The focused corrected Chromium case passed. Chromium coverage is therefore
20 original cases plus one focused corrected case, not a relabelled passing
initial run. No app change was made to hide the failure. The original shared
browser test file was retained.

The full Linux WebKit run uses that documented settlement adaptation. Browser
versions, exact results for Chromium/WebKit, original 107 site regressions, all
seven camera presets and Cmaj7/Am7 four-view desktop/mobile checks are recorded in
the [final QA report](tests/reports/final-summary.json). Deliberately injected
WebGL/module/model failures are separated from unexpected errors.

Actual source-to-rendered root/bone fingerprints matched for C, Cmaj7 and Am7.
The application/build assets did not change between the inspected runs.

## Limits retained

- Geometric acceptance does not approve a natural teaching hand. The finite
  cropped forearm and overall skin/silhouette presentation remain unresolved.
- All hands remain hidden in ordinary lessons; prototype inspection is explicit
  and warned. Changing chords closes inspection.
- The original 39 bad candidates remain needs-review. No musical voicing, finger
  assignment, guitar ID, price, spec or rights record was edited to force a pass.
- The new weak-key cache avoids repeated vertex/index buffer scans for camera
  movement without changing rendering quality. Six real mutation tests verify
  invalidation; this is not a hardware iPad FPS or GPU-memory measurement.
- Linux WebKit/software graphics are not physical iPadOS Safari. Use the device
  steps in [README.md](README.md) before any future merge review.

The historical static failures are rerun in [legacy-static](legacy-static/summary.json)
and remain failed. Their protected source/data inputs match the original
[isolated baseline investigation](../practice-trainer/tests/reports/legacy-static-baseline.md).
