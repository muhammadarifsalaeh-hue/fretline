# C Major pose correction and geometric audit

The final runtime **candidate** is `C-arm-variant.json`, derived from the
contact-corrected `C-contact-refined.json` below. It changes the forearm direction
with a root rotation and counter-wrist adjustment; the finger/hand world geometry
is retained. `C-arm-variant-audit-binding.json` binds its actual authored root and
22 bone rotations to the exact geometric reports. `audit_c_contacts.py` reads
these actual transforms, and never uses the old source-solver provenance vector.
The independently reconstructed combined mesh matches the mesh used for the
zero-crossing audit to 1.14e-13 mm with identical indices.

Four actual runtime views have been inspected. The final candidate remains
**needs-review**, with `anatomyPassed=false`: although the contacts are
geometrically correct and hand/wrist/forearm/sleeve are continuous, the finite
sleeve end is visibly floating in the freely rotated side/player views and the
silhouette still falls short of the approved natural reference. This is not
presented as an approved teaching hand. Its final string clearances, in physical
string order 1–6, are `0.557241 / 0.008003 / 2.682643 / 0.008002 / 0.008003 /
4.213400` mm.

`C-contact-refined.json` is the earlier contact-corrected geometric candidate,
not an independently approved anatomical lesson. It uses the actual exported MakeHuman rig and skin
weights, with the plain licensed shirt, asset SHA-256
`23fdb5745e9343b597eb816bcdfcb266c1942ebbbb495cdb3776214343d7f3bc`.
No finger or thumb is hidden, replaced, or edited into a 2D image.

The reconstruction starts from the saved C solver parameters. The unused little
finger is relaxed to MCP/spread/PIP/DIP `0/10/15/5` degrees. Thumb MCP flexion is
18 degrees and axial opposition 30 degrees. The source palmar flesh vertex 5190
faces the back/side of the neck, with a 0.254 mm analytical back-surface gap.
This replaces the earlier nail-side near-contact.

The first relaxed candidate eliminated the wrong B-string contact but still had
114 intersections between intended fingertip pads and their own pressed strings.
These were **not** accepted as collision-free. `refine_c_contacts.py` makes small
bone corrections, at most 0.55 degrees per joint parameter, against the actual
skinned triangle surface. Actual fretted string paths use the runtime controller.

| Check | Final geometric result |
|---|---:|
| Skin nonadjacent triangle crossings / coplanar overlaps | 0 / 0 |
| Combined hand, forearm and plain sleeve self crossings / overlaps | 0 / 0 |
| Skin versus all 15,556 actual guitar triangles | 0 crossings |
| Combined skin and sleeve versus all actual guitar triangles | 0 crossings |
| Skin/cloth samples inside conservative neck volume | 0 of 72,878 |
| Index/B1 skin-to-circumscribed-string clearance | 0.008 mm |
| Middle/D2 clearance | 0.008 mm |
| Ring/A3 clearance | 0.008 mm |
| Open high-e whole-skin triangle clearance | 0.557 mm |
| Open G whole-skin triangle clearance | 2.683 mm |
| Muted low-E whole-skin triangle clearance | 4.213 mm |
| Independent analytical distance test fixtures | 9 passed |

The microscopic positive contact tolerance avoids accepting intersections and is
below display resolution. It is measured against a circular tube circumscribing
the actual six-sided string mesh. The three closest points remain on the intended
distal flesh triangles, behind the appropriate fret wire. The ring/A3 closest
point is approximately 1.18 mm behind fret 3's center; the exact metal-wire audit
also has zero intersections. Open-string values use all 14,760 skin triangles,
rather than only vertices or fingertip landmarks.

The GLB and root/bone transform hash binding is recorded in
`C-contact-refined-audit-binding.json`. The original and intermediate rejection
reports are retained so the correction is reviewable.

## Reproduce

From the repository root, with Python NumPy/SciPy installed:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python docs/practice-trainer/pose-solver/refine_c_contacts.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python docs/practice-trainer/pose-solver/audit_c_contacts.py
node docs/practice-trainer/pose-solver/export-study-collision-mesh.mjs C /tmp/C-actual-guitar.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/audit-hand-self-collisions.py docs/practice-trainer/pose-solver/C-contact-refined.json --output /tmp/C-self-audit.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/audit-hand-self-collisions.py docs/practice-trainer/pose-solver/C-contact-refined.json --against /tmp/C-actual-guitar.json --output /tmp/C-guitar-audit.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/audit-hand-self-collisions.py /tmp/fretline-trainer-pose/C-contact-refined-full-mesh.json --mesh --output /tmp/C-combined-self-audit.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/audit-hand-self-collisions.py /tmp/fretline-trainer-pose/C-contact-refined-full-mesh.json --mesh --against /tmp/C-actual-guitar.json --output /tmp/C-combined-guitar-audit.json
python docs/practice-trainer/pose-solver/contact-distance.test.py
```

To reproduce the final authored forearm variant's contact audit:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python docs/practice-trainer/pose-solver/audit_c_contacts.py --candidate docs/practice-trainer/pose-solver/C-arm-variant.json --output /tmp/C-arm-clearances.json --combined-mesh /tmp/C-arm-full-mesh.json
```

The crossing auditor uses triangle AABB broad phase, bidirectional segment/face
crossings and coplanar interior-area overlap, excluding triangles sharing an
index. A crossing test alone cannot rule out complete solid containment, hence
the additional dense analytical wood-volume samples and conservative whole-skin
string-distance checks. No anatomical approval follows solely from these tests.
Actual front, side, back-of-neck and player-view inspection remains required.
Physical iPad Safari must also be checked separately from Linux WebKit.
