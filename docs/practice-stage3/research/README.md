# Reproduce the failed feasibility inspection

These files are offline inspection tools and evidence, not production feature
modules. The experimental C pose fails collision/teaching gates. Do not import
it into the app, change its status to approved, or present its captures as a
finished Fretline Practice route.

The source hand is ©2026 Emma L. D. Lieker, CC BY-NC 4.0. Keep the adjacent
`third-party-hand-LICENSE.txt`, attribution, source link and modification notice
with any locally downloaded model and generated captures. This research is for
the user's noncommercial educational project. Commercial reuse requires a
suitable separate grant or another asset.

The GLB and Blender binary are intentionally not committed. The source URLs and
original SHA256 are in `asset-audit.json`; the optimized SHA256 and byte-for-byte
mesh accessor comparisons are in `anatomical-hand-optimized.optimization.json`.
Preparation needs Blender, Python with NumPy/SciPy/Pillow, and the project's
existing Three.js. No app dependency was installed for this inspection.

Prepare a temporary folder containing copies of these research scripts/data and
`inspection/`. Download the exact pinned source `exports/hand_model.glb` as
`anatomical-hand.glb` and `blender/hand_model.blend` as `anatomical-hand.blend`.
Keep the source binaries unchanged. Point `FRETLINE_STAGE3_DIR` to that folder.
Run commands from that folder:

```bash
python optimize_hand_glb.py anatomical-hand.glb anatomical-hand-optimized.glb
blender --background --python extract-fk.py
python prove-runtime-transfer.py
python build-gltf-compatible-fk.py
blender --background --python audit-pose-surface.py -- --runtime
node audit-guitar-mesh.mjs
```

`prove-runtime-transfer.py` first records the original native-six-weight versus
GLB-four-weight discrepancy. The compatible proof then records an exact
four-weight comparison and emits conditional joint matrices. Matrix correctness
does not approve the pose. The runtime collision audit intentionally records a
failed status in JSON; an exit code of zero means the measurement script ran,
not that the hand passed.

The scene builder imports the existing project's `three`. Expose the project's
`node_modules` to the temporary folder for the import map and Node audit; do not
initialize another npm project. Serve the temporary folder over local HTTP and
open `/inspection/`. This serves only the independent diagnostic viewer; the
Fretline routes and catalog remain untouched. Captures must retain the visible
failed-gate banner and source credits. `FRETLINE_INSPECTION_URL` and
`FRETLINE_STAGE3_DIR` can be supplied to the capture scripts.

GLB skin's original grayscale height image was incorrectly assigned as a normal
map. The inspector corrects it to a bump map at runtime; it does not claim that
merely loading the unmodified material is visually correct. Nail constant maps
were folded into factors. Both original and optimized GLBs passed Khronos
structural validation with zero errors, but structural validation does not
test hand anatomy, string contact, realism or iPad frame rate.

Inspect `pose-surface-runtime-audit.json` for actual triangle IDs, barycentric
witness coordinates and exact self-intersection hits. `nearSurfaceSignedGapMm`
is explicitly diagnostic, since nearest-face normals are unreliable for inside
tests on a folded/self-intersecting mesh. Unsigned nearest-surface distance minus
string radius provides the reported tube/surface intersection evidence.

The existing app regressions were rerun using the unchanged commands in
`../../practice-stage1-2/tests/README.md`, with output redirected to
`docs/practice-stage3`. They verify the still-existing Stage 1–2 application.
