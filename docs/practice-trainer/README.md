Final deadline handoff: [3D demo, strict fallback and shared-solver closeout](../practice-final-delivery/README.md).

Latest continuation: [Batch 3 — seven geometric candidates, zero teaching approvals](../practice-hand-batch-3/README.md).

# Fretline Guitar Practice Studio — feature delivery

Latest continuation: [Hand repair Batch 2](../practice-hand-batch-2/README.md)
and its [current 42-pose table](../practice-hand-batch-2/CHORD-STATUS-42.md).
The initial delivery evidence below is retained as the `1f71d34` snapshot.

This extends the existing project on `feature/guitar-practice-3d`, starting from
`b21bd6a` with rollback checkpoint `17bd035`. It is **not a completed, approved
42-pose human-hand trainer**. The stable original website remains on master;
this branch must not be merged without the user's review.

## What works

- `/practice` has 42 conventional voicings in the six requested groups, standard
  tuning, explicit fingering/barres, notes, open/muted strings and Thai/English
  instructions. Original chord IDs and choices are retained.
- Independent musical and actual full/compact SVG audits establish all 42
  diagrams. Search, type filters, previous/next, keyboard selection and URL
  Back/Forward work without a page reload.
- A real Three.js PBR study neck has six gauged strings, twelve correctly spaced
  frets, nut, headstock/tuners and fret markers. Default camera keeps the head
  right/up and physical strings E–A–D–G–B–e top to bottom. It frames the first
  six frets; **Full neck** shows the complete study model. Rotate, zoom, camera
  presets and reset work with pointer, keyboard and touch.
- One real MakeHuman skinned left hand/forearm and a fitted real black shirt
  sleeve use 22 deform bones. Forty-two different root/bone poses are stored;
  the engine checks the exact GLB SHA and original named rig before applying any.
- Only Practice fetches the 3D code, GLB, embedded textures and pose library.
  Rendering is on demand. Unmount, failed/late loading, context loss and model
  retry dispose resources or abort pending requests. Diagrams remain usable
  without WebGL or a loaded model.

## Honest hand status

**42 verified diagrams; 0 approved teaching hands; 42 needs-review candidates.**

C has been repaired using actual skin triangles and bone transforms: no
  self-intersection or guitar intersection in the audited combined skin/sleeve
  mesh; assigned contacts are about 0.008 mm from the string surface, high-e
  clearance 0.557 mm, G clearance 2.683 mm. The thumb's palmar flesh faces the
  back of the neck. A counter-rotated wrist improves the forearm direction while
  preserving the finger contacts. This is a geometric correction, **not a
  completed visual acceptance**: the finite cut forearm remains visible in some
  orbit views and the finger/palm silhouette still needs refinement.

All other 41 poses have actual skin crossings (255–755 pairs per pose). Some
also intersect sampled wood volumes or open strings. None is shown as a valid
practice example. The explicit **Inspect prototype hand** control reveals an
unapproved pose with a warning; changing the chord closes that inspection.
No intermediate transition is animated through an unverified pose.

See [the complete 42-row status table](CHORD-STATUS-42.md),
[C geometry/contact evidence](pose-solver/README.md),
[the four-view visual review](visual-review/C-arm-independent-review.md) and
[all other candidate rejection reports](pose-candidates/runtime-review/README.md).
Anatomy/visual approval remains false even when collision/contact gates pass.

## Models, licensing and authoring

The GLB is 1,012,288 bytes: 14,760 skin triangles, 1,304 sleeve triangles and two
embedded textures. Body, rig, skin and weights are MakeHuman CC0. The sleeve is
adapted from Elvaerwyn's CC-BY shirt, with attribution in the deployed Practice
page and retained source/provenance. No downloaded product image, fake hand
primitive or 2D stand-in was introduced.

[Model sources, licences and derivation](models/README.md) include the packed,
editable Blender source and repeatable audit scripts. Removing disconnected
ornamental cuff/button details preserved the continuous cloth and every original
hand/rig attribute. No model licence gate or catalog image-rights gate was removed.

## Validation

The [test guide](tests/README.md) describes the independent browser/music checks,
fault injection and unchanged site regressions. Final transcripts, browser
versions, asset hashes, unexpected errors and actual screenshots are retained in
`tests/reports/`. Use the final report, rather than a previous interim run.

The extra historical `phase5:check` through `phase9:check` commands still fail
their old no-price/no-logo or frozen Yamaha snapshot assumptions. The exact same
failures were reproduced on isolated `b21bd6a` source; 368 protected files match
the baseline. They are **failed**, not counted as passing regressions, and no
assertion or product data was changed to conceal them. See the
[baseline comparison](tests/reports/legacy-static-baseline.md).

Build retains Vite's warning for a large **lazy Practice-only** Three.js chunk.
This is not a main-route download. Linux software WebGL measurements do not
establish native iPad GPU speed, GPU memory usage or Safari compatibility.

The catalog, product data, IDs, prices, image-rights records, Homepage/Marquee,
Brand Directory, Compare, Wishlist and Quiz sources are unchanged from the
baseline. The catalog still contains exactly **200 guitars / 10 brands / 20 each**.

## Open on Codespaces / iPad

Save any local edits first. Do not reset or discard changes to switch branches.
In the existing Fretline Codespace terminal:

```sh
git status
git fetch origin
git switch feature/guitar-practice-3d
git pull --ff-only origin feature/guitar-practice-3d
npm ci
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

Leave the terminal running. Open **Ports → 5173 → Open in Browser** and append
`/practice` to the forwarded HTTPS URL. `localhost` on an iPad refers to the iPad,
so use the Codespaces forwarded URL. Open `/practice?chord=C` for C or
`/practice?chord=F` to inspect the unapproved barre prototype.

## Physical iPad Safari acceptance — still required

Linux WebKit is **not physical iPadOS Safari**. No actual iPad was available in
this environment. Before considering a merge, record device/iPadOS version and:

1. Check portrait and landscape, readable controls, no horizontal page overflow.
2. Load C, inspect E–A–D–G–B–e order and head right/up; rotate, pinch and reset.
3. Verify all unapproved hands are hidden until explicit inspection and retain
   the warning; select another chord and confirm inspection closes.
4. Search/filter all six groups, compare diagram positions/barres with the table,
   use previous/next and Safari Back/Forward, and reload a shared chord URL.
5. Open all camera presets, including Full neck. Inspect the hand/sleeve from
   default, side, back and player views; note cropped ends and contact visibility.
6. Navigate to Catalog/Compare/Wishlist/Quiz, return to Practice several times,
   and note any crash, delayed controls, excessive heat or Safari reload.
7. Test a blocked model/WebGL fallback if available; diagrams must remain usable.

## Remaining work / stable submission fallback

Before approving even C for teaching, finish the natural hand silhouette and a
proper longer arm/garment presentation in the native model, then repeat contact,
self/wood/open-string and four-view checks. Other poses need authored anatomical
joint limits/correctives and separate review; sub-millimetre IK target fit alone
was demonstrated to be insufficient, especially for barres.

This delivery stops on the feature branch. The stable master website is preserved
for the 28 October submission if human poses cannot meet the required standard.
No song, scale, audio, other practice mode or master merge was added.
