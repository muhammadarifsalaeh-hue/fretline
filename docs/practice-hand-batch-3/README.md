# Fretline — Batch 3: contact-constrained hand prototypes

Continues `74c2076` on `feature/guitar-practice-3d`. No master merge.

**Seven geometric endpoints pass; zero teaching hands are approved.** This is
an inspection build with a stable 42-diagram fallback, not a production-ready
42-hand lesson. The original three passing endpoints are retained. Four new
actual bone poses are integrated only after exact mesh acceptance:

| Chord | Immutable voicing | Actual change |
|---|---|---|
| Em7 | `020000` | Release unused digits; middle finger contacts A2 |
| E7 | `020100` | Index contacts G1; Em7 middle A2 contact is unchanged |
| Fmaj7 | `xx3210` | Index B1, middle G2, ring D3; real ring contact refined |
| Dm | `xx0231` | Index e1, middle G2, ring B3; ring contact staggered 2 mm toward nut inside the original permitted fret region |

Together with **C, Cmaj7, Am7**, these form the seven accepted geometric
candidates. **D, G, Em, Am and full-barre F have not passed.** Fmaj7 is not a
substitute for F. Rejected authoring experiments are kept as evidence and are
not promoted into the runtime library.

## What changed

- The same licensed MakeHuman human mesh, 22-bone rig, continuous forearm and
  black sleeve remain. No primitive fingers, photography or prerecorded hand
  animation replace the actual 3D rig. Model, skin weights and original musical
  data are byte-identical to the baseline.
- Bounded local finger IK works on actual saved root/bone rotations and
  original weighted skin. Numerical fingertip fit alone is rejected: all
  accepted endpoints pass combined skin/sleeve self-crossing, exact guitar
  crossing, dense wood, actual open-string and assigned-digit palmar contact
  checks. No threshold or chord fingering was relaxed.
- Same-fret neighboring fingers need real surface clearance and contact
  staggering. Dm's ring-fret collision was corrected by moving its contact
  nutward inside the unchanged legal region, rather than moving a fret or
  changing the chord.
- A bounded **160 ms appearance reveal** is added to allowed hand inspection.
  The hand pose changes while invisible. Bones do not interpolate through an
  unchecked path. Closing inspection, changing a chord, retrying or leaving
  Practice cancels immediately. Reduced motion completes immediately, including
  a preference change during a reveal. The reveal stops scheduling frames when
  complete. This is not a certified physical chord-change animation.

## Truth and remaining limits

All 42 records remain `needs-review`, with `reviewed: false`,
`anatomyPassed: false` and `multiViewReviewed: false`. Contact/collision gates
alone never make a teaching hand visible. Ordinary lessons use the verified
musical diagram and real guitar; **ตรวจต้นแบบมือ** is an explicit warned review.
Switching chord closes inspection.

The hand silhouette still differs from the reference: some proximal fingers
look extended, skin rendering is less natural, and the cropped sleeve end is
visible in some orbit views. Thumb and neighboring-digit constraints still
prevent a correct full-barre/42-pose solution. A new rest-relative rotation is
not a clinical joint-angle measurement. The existing source has no authored
corrective shapes for all deep flexions. See [rig review](RIG-REVIEW.md),
[bounded D/G review](DG-BOUNDED-REVIEW.md), and
[rejected Am/Em trials](Em-Am-EXPERIMENTS.md).

A collision-free endpoint also does not certify a collision-free swept path.
Physical chord-to-chord interpolation remains unavailable. No physical iPad
Safari is accessible in this environment; Linux WebKit, synthetic touch and
software graphics do not establish native Safari, hardware FPS or GPU memory.

## Evidence and reproduction

- [All 42 runtime chord statuses](CHORD-STATUS-42.md)
- [Actual final 42-pose mesh report](geometry/summary.json)
- [Build, core and browser tests](TEST-RESULTS.md)
- [Actual multi-view screenshots](SCREENSHOTS.md)
- [Source/model preservation](source-preservation.json), [197 protected site files](protected-site.json)
- [Safe reveal review](REVEAL-REVIEW.md), [integration review](INTEGRATION-REVIEW.md)

```sh
python scripts/practice/batches/integrate-batch-3.py
python scripts/practice/batches/check-batch-3-preservation.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/check-hand-geometry.py --require C,Cmaj7,Am7,Em7,E7,Fmaj7,Dm --output docs/practice-hand-batch-3/geometry
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/test-hand-geometry.py
node scripts/practice/check-hand-reveal.mjs
```

`testSuitePassed` is the required seven-endpoint regression gate, not a claim
that all 42 hands pass. The table preserves rejected/unrun stages. The raw
crossing evidence, candidate source hashes, original failed trials and exact
successful transforms are retained. Python/SciPy/Blender are offline authoring
and validation tools, not new browser dependencies. Production changes are
limited to Practice; no dependency was added.

## Open on iPad in the existing Codespace

First stop a running Vite server with **Ctrl+C**. Save existing local edits;
do not discard them or use a hard reset. Then run in the Fretline terminal:

```sh
git fetch origin
git switch feature/guitar-practice-3d
git pull --ff-only origin feature/guitar-practice-3d
git log -1 --oneline
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

Open **Ports → 5173 → Open in Browser**. In Safari's address bar append
`/practice?chord=Em7`, `/practice?chord=E7`, `/practice?chord=Fmaj7` or
`/practice?chord=Dm`. Do not enter the route as a terminal command. Open
**ตรวจต้นแบบมือ** to inspect the actual hand with its warning.

On a physical iPad, record model/iPadOS/Safari versions and test:

1. Portrait and landscape, no horizontal page overflow; labels and touch targets.
2. Drag rotation, pinch zoom, all camera presets and Reset; low E remains above
   high e in the default view and the headstock remains right/up.
3. Each accepted candidate in default, side, behind-neck and player views.
   Check real palmar string/fret contact, relaxed wrist, thumb behind the neck,
   open strings, the five digits and continuous sleeve. Do not approve from a
   single attractive camera view.
4. Change chords quickly and use Back/Forward; old inspection closes immediately.
   Test reduced motion in iPadOS Settings and repeated reveal toggles.
5. Navigate Practice → Catalog/Compare/Wishlist/Find My Guitar → Practice several
   times. Watch for reloads, lost WebGL contexts, stutters and memory pressure.
6. Verify Homepage/brand marquee, all ten brands and existing catalog functions.

A failed `git pull` must be resolved without discarding local work. No public
feature deployment or master merge is made by this batch.
