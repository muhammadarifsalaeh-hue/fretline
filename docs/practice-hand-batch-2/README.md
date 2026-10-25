# Fretline hand repair — Batch 2

Continues `feature/guitar-practice-3d` from `1f71d34`; no master merge.

**Geometric acceptance: 3/42. Approved teaching poses: 0/42.**

| Measure | Previous delivery | This batch |
|---|---|---|
| Corrected geometric candidates | C | C, Cmaj7, Am7 |
| Poses rejected for self-collision | 41 | 39 |
| Verified teaching hands | 0 | 0 |
| Musical chord diagrams | 42 | 42, unchanged |
| Guitar catalog | 200 / 10 brands / 20 each | Unchanged |

## Repairs that were actually made

- **C:** increased proximal joint flexion to improve the extended-finger
  silhouette, refined the actual flesh surface against the strings and retained
  a real forearm/counter-wrist reframe. All combined skin/sleeve and guitar
  intersections are zero. Assigned B/D/A clearances are approximately 0.008 mm;
  open high-e/G clearances are 1.835 / 2.780 mm. This is a real bone pose, not a
  mesh stretch or hidden finger. [Measurements and bounded trial history](presentation/README.md).
- **Cmaj7 `x32000`:** released the unused index PIP by 4° from the pinned audited
  C seed. Actual middle D2 and ring A3 flesh coordinates are unchanged; open B
  has 1.328 mm clearance. Exact combined self/guitar crossings are zero.
- **Am7 `x02010`:** relaxed the unused ring to PIP/DIP 25°/25°. Actual index B1
  and middle D2 coordinates are unchanged; open A has 2.500 mm clearance.
  Exact combined self/guitar crossings are zero.

The original generator optimizes unused digits/thumb too freely and has no
hand-self-collision objective. An excellent fingertip target fit therefore did
not prevent hundreds of triangle crossings. This batch uses a pinned, audited
pose and changes only the necessary chains, with actual-mesh rejection tests
before accepting any geometric improvement. It does not claim the original
whole-library optimizer has been solved for every chord.

Rest-relative authoring MCP deltas are **not** anatomical zero angles: the
source joints already have rest flexion. The recorded bone lengths do not show
an artificially stretched hand. See [the independent review](review.md).

## New mechanical regression gate

[`check-hand-geometry.py`](../../scripts/practice/check-hand-geometry.py) reads the
unchanged central chord data, actual saved root/22-bone rotations and exported
GLB weights. It checks all 42 current combined skin/cloth meshes for nonadjacent
and coplanar crossings. Self-colliding poses are rejected immediately; zero-self
candidates additionally receive:

- exact crossing tests against the runtime guitar triangles;
- dense vertex/edge/face-centre tests against the wood solid;
- whole-skin clearance to **actual runtime exported** open string paths;
- correct-owner palmar distal contact in the selected string/fret region.

Each report binds the real pose transform, model, musical source and runtime
guitar export hashes. All 42 rows and compressed raw crossing evidence are
retained. `testSuitePassed` means the required repaired batch passes and no
rejected pose is falsely labelled verified; `all42GeometricPassed` remains
**false**. See the [42-row table](CHORD-STATUS-42.md).

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/check-hand-geometry.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/test-hand-geometry.py
node scripts/practice/check-fingerprint.mjs
```

Python NumPy/SciPy are authoring/test tools, not browser dependencies. The four
real-mesh negative regressions reject an unchanged C hand relabelled Cmaj7,
a hand driven into wood, fingertips displaced to the wrong fret, and a verified
label without independent review evidence. Fixtures
never edit the musical or runtime production data.

## Performance without changing the rendered model

Camera diagnostics previously scanned all neck position buffers repeatedly.
The new Practice-only fingerprint caches actual position/index buffers by
reference and GPU update version, with weak geometry keys. Matrices still affect
the result, and replaced pressed strings invalidate it. Six real-geometry
mutation tests pass, including index topology changes and a Uint16 triangle.
One hundred camera/static checks require no additional buffer scans. Rendering,
mesh quality, textures and the 22-bone hand are unchanged.

This reduces repeat CPU work; it is not a physical-iPad FPS claim. Three.js and
assets remain lazy-loaded only on Practice, with existing disposal/fallbacks.

## Tests and remaining limits

Build, catalog, images, music, runtime, pressed-string and new mechanical tests
have separate transcripts in this directory. [Browser evidence](tests/README.md)
includes the full Chromium/WebKit suites, original site regressions and actual
multi-angle C/Cmaj7/Am7 captures. Read the final summary for actual completed
counts, rather than an interim log.

Historical Phase 5–9 static commands still fail the same stale price/logo/Yamaha
snapshot assumptions. Their current logs are in [legacy-static](legacy-static/summary.json);
the [previous isolated baseline proof](../practice-trainer/tests/reports/legacy-static-baseline.md)
is retained. They are not counted as passing. No product data or old assertion
was changed to hide these failures.

All three repaired poses remain **needs-review**: final natural hand/forearm
presentation is not approved. The finite cropped arm source remains visible in
some orbit views; genuine full-arm/garment authoring remains work for a later
batch. Other 39 poses still fail self-collision. No unapproved hand is shown as
a teaching example; explicit prototype inspection retains its warning.

No physical iPad Safari was available. Linux WebKit, synthetic touch and desktop
software graphics do not establish real iPad performance or native Safari.

## Open the current feature on iPad

In the existing Fretline Codespace, save local edits without discarding them:

```sh
git fetch origin
git switch feature/guitar-practice-3d
git pull --ff-only origin feature/guitar-practice-3d
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

Open **Ports → 5173 → Open in Browser**, then `/practice?chord=C`,
`/practice?chord=Cmaj7` or `/practice?chord=Am7`. Use explicit prototype inspection
to review the unapproved hand. Test portrait/landscape, pinch/drag/reset, switching
chords closing inspection, all seven camera presets, Back/Forward and repeated
navigation to Catalog/Compare/Wishlist/Quiz. Record the device/iPadOS version and
any frame stalls or reloads before any merge approval.
