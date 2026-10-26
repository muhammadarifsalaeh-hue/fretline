# Independent rig, weights and presentation review

Reviewed the existing `74c2076` delivery before batch-3 pose integration. This
review changes no chord, model, runtime pose or approval flag. Existing saved
batch-2 exact collision reports were mapped back to their original GLB vertex
owners; they were not presented as newly rerun collision tests.

## What was inspected

- Actual `rig-data.json` bone rest matrices, hierarchy, skin joints and four
  influences per vertex, and the current pose-library local quaternions.
- `solve-hand-poses.py`, `generate-pose-library.py`, the batch-2 geometric gate,
  and the exact triangle/coplanar rejection script.
- All four actual desktop C captures in batch 2: default, side, behind-neck and
  player. No browser or physical iPad test was performed by this review.
- Blender is available at `/usr/bin/blender`; no installation was attempted.

## Source geometry and skin weights

There are 22 real bones: three segments for each of five digits, four
metacarpals, a wrist and two forearm bones. Thumb base articulation is represented
by the first thumb bone attached to the wrist; it is not a separate complete
anatomical CMC model. Source hand dimensions and bone lengths have not changed.

| Mesh | Vertices | Triangles | Weight-sum range |
|---|---:|---:|---|
| Black long-sleeve forearm | 734 | 1,304 | 0.9999999404–1.0000000894 |
| MakeHuman hand/forearm | 7,888 | 14,760 | 0.9999998882–1.0000001155 |

Both meshes have zero nonfinite weights, zero vertices with a zero influence sum,
and no vertex with more than four active influences. The exported original rest
mesh and repaired C have existing zero-crossing reports. These observations
provide no evidence of wholesale skeleton or weight corruption. A pose can
nevertheless fold the skin at an extreme bend: normalized weights do not
guarantee a good deformation, and linear blend skinning has no corrective shape
for a particular deep MCP/PIP fold.

## Principal source of the rejected poses

The generator optimizes target positions, sparse wood/open-string clearance and
soft angular priors. It has no actual hand-versus-hand collision term and permits
large independent spread/curl changes. Its numerical target fit is therefore
not a safe acceptance criterion. Examples from actual saved old candidates:

- Am: unused little-finger PIP delta 130° and DIP 69.6°; ring spread +35°.
- Em: little spread −35°/PIP 85.3°; ring spread +35°; thumb spread −70°.
- D: thumb spread −70°, DIP 85°; little spread −35°.
- F: middle PIP delta 123° while DIP is 0°.

These are **rest-relative solver deltas**, not clinical joint angles. The source
rest skeleton already has flexion. They still expose how independent degrees of
freedom are driven to optimizer bounds without a deformation or collision gate.

Mapping the original combined-mesh reports to the dominant skin-bone owner gives
the following useful rejection diagnostics. Counts are triangle-pair crossings,
not the number of intersecting fingers or a penetration depth.

| Old pose | Total crossing pairs | Main actual regions |
|---|---:|---|
| Em | 530 | Middle/ring distal 106; proximal 81; PIP regions 66; little local fold 43 |
| Am | 741 | Middle/ring distal 108; proximal 102; PIP regions 85; little local folds 80/62 |
| G | 352 | Middle proximal/ring PIP 53; little local fold 48; ring local fold 45 |
| D | 370 | Middle/ring PIP 85; proximal 56; index/palm 60 |
| F | 516 | Middle/ring proximal 99/90; middle local fold 69; ring/little distal 40 |

Thumb/palm crossings are present too, but fixing only the thumb or unused little
finger cannot repair the active adjacent chains. On same-fret adjacent strings,
about 7 mm of string separation is smaller than typical full distal pad width.
The fingers need staggered contact within the unchanged legal fret region,
appropriate side tilt and distributed curl, rather than coincident pad-centre
point targets. Do not move the strings or change the fingering to hide this.

## Concrete bounded authoring recommendations

1. Preserve the audited seed root, wrist, thumb and unused chains when those
   regions remain valid; change only chains needed by the musical fingering.
2. Use actual palmar distal skin triangles and the real runtime string path.
   Contact should be close behind the fret wire, with room to stagger fingers
   inside that region. A bone-head or eight-vertex average alone is insufficient.
3. Constrain neighboring active phalanges as surfaces or conservative capsules
   during fitting; keep the final exact skin/sleeve crossing rejection unchanged.
   Reject adjacent-finger contact, local MCP/PIP skin folding and wood separately.
4. Do not solve a deep curl solely by increasing one PIP while leaving DIP at its
   extreme or compensating with maximum MCP spread. Use a bounded distributed
   curl prior derived from the actual rest skeleton. Constrain the unused little
   and thumb instead of including them freely in a fingertip solve.
5. If a needed deep/barre deformation repeatedly folds despite viable joint
   positions, author local corrective shapes/weights in the existing Blender
   source. Preserve native topology and named chains, then re-export with a new
   model signature and re-audit every affected stored pose. Do not globally alter
   otherwise valid weights without local evidence.
6. Bone interpolation is not certified by valid endpoints. Use a checked swept
   trajectory, or an explicitly described presentation transition that changes
   the pose only while the hand is fully invisible. Never show unchecked
   intermediate intersections as instruction.

## Visual findings from the real C captures

The C hand is recognizably a skinned human hand with five digits, continuous
wrist/forearm and a black sleeve. It is not a set of primitive finger objects.
The default view has the intended headstock on the right, low-to-high string
order and actual fret contact. Nevertheless the image does not yet match the
reference's curled, relaxed silhouette: the proximal fingers appear rather
extended, the palm sits conspicuously below the neck, the skin reads flatter
than the photographic reference, and the finite sleeve termination is visible
when orbiting. The side/back/player views reveal these presentation limits.

Moving the palm closer to the lower neck edge and redistributing curl may help,
but must be solved against the complete real mesh because it can introduce
thumb/wood and adjacent-digit contact. Hiding fingers, adding a rough forearm,
or placing a dark object over the cut arm would not solve the source limitation.
A genuine longer arm/garment needs the original licensed complete source assets.

## Scope of a geometric pass

The strengthened gate checks actual FK/LBS skin and sleeve triangles, self and
guitar crossings including coplanar overlap, dense wood samples, whole-skin
open-string clearance, and correct-owner palmar contact inside the correct fret
region. It is a useful rejection gate and must not be loosened for this batch.

It does not certify muscle/joint comfort, pressure, skin volume at all curls,
fully enclosed self-solid overlap, surface appearance, or a swept animation
trajectory. It also does not substitute for multiple-view visual acceptance or
physical iPad Safari. Geometric success must therefore remain separate from
`anatomyPassed`, `multiViewReviewed` and teaching `verified` status.

## Performance implications

The existing 16,064 total mesh triangles and approximately 1 MB GLB are modest;
offline exact collision solving should remain outside the browser. Source
weights fit the existing GPU skinning path. Keep on-demand rendering, Practice
lazy loading, proper geometry/material/texture disposal, and the existing
fingerprint cache. A smoother-looking hand should first use better authored
poses/corrective deformation, not indiscriminate subdivision or larger textures.
Linux WebKit and software rendering provide no physical-iPad frame-rate result.
