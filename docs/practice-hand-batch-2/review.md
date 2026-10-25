# Independent review of the restricted C-neighbour batch

Reviewed against feature baseline `1f71d34`. This review changes no product data,
runtime model, chord voicing, hand status or production pose library.

## Findings from the original generator

`scripts/practice/generate-pose-library.py` fits skin contact patches and applies
sparse wood/open-string penalties. Its residual has **no hand-versus-hand
self-collision term**. It also re-optimizes the thumb and unused digits. The
angle-sum and preferred-angle terms are soft penalties, not hard geometric
constraints. `solve-hand-poses.py` permits PIP flexion up to 130 degrees and DIP
up to 95 degrees; this is not a guarantee that the exported skin can deform
without folding at those angles.

The previous actual-mesh rejection report contains 19,018 skin crossing pairs
across 41 rejected poses. The rest/source model and the repaired C pose have zero
audited crossings. This supports a pose-constraint failure; it does not establish
general corruption of the skeleton hierarchy or source skin weights. Changing
skin weights globally is not justified by these findings alone.

The safer batch strategy is to preserve the repaired C root, wrist, thumb,
unused digits and already correct contacts, then change only the finger joints
required by a related voicing. Wood, open-string and self-collision constraints
still need actual mesh checks. A contact-only optimizer or a smaller numerical
target error must never automatically promote a pose.

## Cmaj7

The central musical voicing remains `x32000`: middle finger D2 and ring finger
A3; G, B and high-e open. This is a strict contact subset of the repaired C.

Independent actual FK/LBS reconstruction found:

- Root transform unchanged.
- Only `finger2-2.L` changes in the saved candidate, releasing index PIP by four
  degrees. No thumb, wrist, metacarpal or assigned middle/ring joint changes.
- All 16 sampled **actual distal flesh vertex coordinates** of the assigned
  middle and ring pads have exactly **0.0 mm** maximum coordinate difference
  from the audited C pose. This verifies physical contact inheritance separately
  from reusing finger labels.
- Existing full-skin triangle distance results: D and A contact clearances
  0.008002 / 0.008003 mm; open G 2.682643 mm, B 1.327905 mm, high-e 0.557241 mm.
- Existing exact skin self, combined skin/sleeve self, and combined mesh versus
  actual guitar reports each contain **zero crossings and zero coplanar
  overlaps**. Dense wood samples have zero interior samples.

The saved report binds the contact calculation to transform SHA
`c46c954aa85d3323f42c33e9a59b8117a2c76f6645467d1e8af1090f5ec553bb`.
The C seed transform is
`9360c6ed2b6cc0decbcf6a79b646bf3e045faba3686e6620306222ef6a10a157`.

Before treating the evidence as repeatable, pin the C seed instead of reading a
future mutable production C record, require the rig-data asset SHA to match the
actual GLB/candidate SHA, and bind the exact crossing reports to the candidate
transform and exported guitar mesh SHA. Reports that only name `/tmp` mesh paths
do not alone prove which bytes were audited.

## Am7

The central musical voicing remains `x02010`: middle D2 and index B1; A, G and
high-e open. The authoring script releases the now-unused ring PIP/DIP to
25/25 degrees while retaining the repaired C root/wrist and other digits.

Independent in-memory reconstruction of that script found:

- The pinned seed matches the current audited C runtime record.
- Only `finger4-2.L` and `finger4-3.L` rotations change.
- All 16 actual assigned index/middle distal flesh vertex coordinates have
  exactly **0.0 mm** maximum difference from C.
- The script asserts the exact central Am7 frets and fingering and checks actual
  GLB, pinned seed and rig-data asset SHA equality.

This establishes the intended restricted operation, **not a completed Am7 mesh
approval**. At review time the Am7 full triangle/collision reports were pending.
The parent must use the subsequently generated reports to decide whether the
candidate passes the geometric criteria.

## Approval remains separate

Both candidates inherit the C presentation limitations: a finite cropped
forearm and a hand silhouette that has not met the reference acceptance. They
must remain `needs-review` until actual multiple-view inspection accepts the
hand/wrist/arm presentation. Numerical collision/contact passes are separate
from anatomical teaching approval, native iPad Safari performance and musical
diagram verification.

No chord or fingering should be changed to make a hand-pose test pass. Barre
chords and other unrelated voicings cannot be approved by this contact-subset
operation and need independent authored poses and audits.

## Final runtime and geometric-checker code review

Reviewed the final `geometryFingerprint.js` integration and the actual
`check-hand-geometry.py` / `test-hand-geometry.py` tools. The current 42-row
geometry report's chord-source and runtime-library SHA-256 values match the
actual current files. Three poses pass the geometric checks, 39 are rejected,
and zero are anatomically approved.

The fingerprint cache has no blocking defect for the study model's actual plain
BufferAttributes. It tracks attribute objects, backing arrays, version counters,
index objects/arrays/versions, and every mesh world matrix. Matrix-only movement
does not rescan buffers, while pressed-string geometry replacement changes the
key. WeakMap keys do not retain replaced geometries. Scene cleanup cancels the
render callback and removes the root's resources, so this cache adds no separate
strong list of disposed geometry. The six mutation tests exercise real model
buffers and restoration rather than merely hashing expected constants.

The geometric checker now uses runtime-exported pressed-string paths, actual
skin and garment triangles, self/guitar intersections, dense wood rejection,
whole-skin open-string clearance, and assigned-digit palmar contact near the
specified fret. This is materially stronger than the original target-fit-only
generator. The three negative fixtures reject an unchanged C hand labelled
Cmaj7, wood penetration, and wrong fret-region displacement. Positive numerical
results still do not approve anatomy, wrist comfort or reference quality.

One reporting/CI hardening issue was sent to the parent: at code-review time a
raw `status: verified` record was rejected only when its geometry failed, and
`verifiedTeachingHands` counted that raw status without checking `reviewed` and
all four review gates. The runtime itself correctly downgrades missing evidence.
The checker should also reject any verified source record missing those gates
and count only strictly approved records. A negative fixture for a geometrically
valid C record with a missing anatomy gate will protect that boundary. This does
not affect the current zero-approved library or require application/GPU changes.

## Resolution after review

The Cmaj7 seed is now pinned in its batch directory and all fit/audit scripts check the actual rig-data SHA against the GLB and candidate. The new all-42 geometry gate binds actual root/bone transforms and runtime guitar exports; correct-owner palmar contact is measured directly. The verified-status guard now requires reviewed=true and all four review gates. Four real-mesh negative regressions, including unearned verified status, passed. The runtime approval guard was retained throughout.
