# Natural C hand presentation: measured feasibility, not lesson approval

The authoring scripts here do not edit production files. The final candidate was
subsequently selected into the runtime pose library by the root batch workflow;
the model, camera and musical data remain unchanged.
The source is the actual MakeHuman GLB and exported skin weights. No finger is
hidden, replaced with a primitive, stretched or substituted with a 2D image.

## Correct interpretation of the rig

The authoring MCP parameters are **deltas from the exported rest rotations**,
not anatomical zero angles. In the saved C-arm pose, projected bone-axis MCP
flexion is approximately 16.26° index, 11.96° middle and 19.07° ring, even though
the corresponding authoring deltas are near zero. Those source rest joints are
already flexed 15.75°, 12.49° and 16.40°. These are bone-axis proxies, not a
clinical measurement or ergonomic certification.

Actual MCP-to-tip bone-chain lengths are 70.99 / 81.51 / 76.33 mm for index,
middle and ring. The most distal index/middle skin projects 175.82 mm from the
wrist along the hand's source forward axis. There is no evidence that the mesh
was arbitrarily stretched to reach the strings. Silhouette quality must be
reviewed in actual images, rather than inferred from a parameter labelled MCP.
`inspect_proportions.py` reproduces [measurements.json](measurements.json).

## One bounded natural-C experiment and rejection evidence

`try_natural_c.py` runs one 50-evaluation solve with increased proximal-joint
flexion while preserving the three existing *actual barycentric flesh contact
anchors* and the thumb anchor. The objective also includes conservative wood
and open-string sampling. It retains the existing musical C targets exactly.

The numerical solve reached its evaluation limit, so it is **not reported as
optimizer success**. It fitted the three anchors within 0.0013–0.0021 mm and had
zero sampled wood vertices, but exact tests rejected that first candidate:

- 42 ring/little skin crossing pairs;
- B-string skin clearance −0.0564 mm (penetration).

Increasing unused little-finger spread to +20° made matters worse: 260 crossing
pairs. That failed trial is retained. It demonstrates why a small-looking joint
change and excellent fingertip target fit cannot establish a correct hand.

The existing bounded triangle-surface contact refinement removed the B-string
penetration, and relaxing the unused little-finger spread to 0° removed the
ring/little intersections. The final authoring pose is
[`C-natural-arm.json`](C-natural-arm.json): increased proximal flexion, actual
contact refinement and a +25° real forearm/counter-wrist reframe. That reframe
preserves every hand joint position within 0.0000067 mm.

| Exact final geometric check | Result |
|---|---:|
| Combined actual skin and sleeve nonadjacent/coplanar intersections | 0 |
| Combined actual skin and sleeve vs all actual C guitar triangles | 0 |
| B1 skin-to-circumscribed-string clearance | 0.008003 mm |
| D2 clearance | 0.008001 mm |
| A3 clearance | 0.008003 mm |
| Open high-e clearance, all skin triangles | 1.834764 mm |
| Open G clearance, all skin triangles | 2.780196 mm |
| Muted low-E clearance | 4.224914 mm |

The used fingers' rest-relative MCP deltas are now about 15° / 15° / 23°.
The model's hand mesh and skin weights are unchanged. The microscopic positive
contact tolerance is below display resolution and avoids claiming an intersecting
surface is collision-free. [The binding](C-natural-arm-binding.json) pins the
actual candidate, transform, GLB, rig, combined mesh and report hashes.

**All approval gates remain false in the saved authoring candidate.** It needs
actual four-view inspection and independent natural-hand acceptance before any
teaching approval. The genuine finite forearm remains cropped; this experiment
does not claim to fix the cut sleeve termination or photorealism.

## Repeat the successful authoring sequence

From the existing repository root, with NumPy/SciPy available:

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python docs/practice-hand-batch-2/presentation/try_natural_c.py
python docs/practice-hand-batch-2/presentation/set_little_spread.py docs/practice-hand-batch-2/presentation/C-natural-experiment.json docs/practice-hand-batch-2/presentation/C-natural-little20.json 20
python docs/practice-trainer/pose-solver/refine_c_contacts.py --input docs/practice-hand-batch-2/presentation/C-natural-little20.json --output docs/practice-hand-batch-2/presentation/C-natural-refined.json
python docs/practice-hand-batch-2/presentation/set_little_spread.py docs/practice-hand-batch-2/presentation/C-natural-refined.json docs/practice-hand-batch-2/presentation/C-natural-little0.json 0
python docs/practice-hand-batch-2/presentation/reframe_natural_arm.py
python docs/practice-trainer/pose-solver/audit_c_contacts.py --candidate docs/practice-hand-batch-2/presentation/C-natural-arm.json --output /tmp/C-natural-arm-clearances.json --combined-mesh /tmp/C-natural-arm-combined.json
node scripts/practice/export-guitar-collision-mesh.mjs C /tmp/C-natural-guitar.json
python scripts/practice/audit-hand-self-collisions.py /tmp/C-natural-arm-combined.json --mesh --output /tmp/C-natural-arm-self.json
python scripts/practice/audit-hand-self-collisions.py /tmp/C-natural-arm-combined.json --mesh --against /tmp/C-natural-guitar.json --output /tmp/C-natural-arm-guitar.json
```

## Native Blender work still needed for the arm

The packed native `.blend` contains the cropped hand/forearm and sleeve only.
The original full body and shirt inputs under `/tmp/fretline-trainer-assets`
are absent, so a genuine elbow/full sleeve cannot be recovered from that cropped
native source alone. No large asset pack was downloaded by this task.

1. Retrieve the exact original CC0 hm08 body/rig/skin and Elvaerwyn CC-BY shirt
   using the recorded source URLs and SHA evidence in
   [`models/README.md`](../../practice-trainer/models/README.md). Retain credit.
2. Rebuild from the **complete real left arm and shirt topology**, including the
   elbow/longer sleeve as needed, rather than extruding a rough substitute from
   the cut edge or hiding the cut with a dark object.
3. Keep original hand dimensions, UVs, anatomical bone hierarchy, positive scale
   and named finger chains. Use native weight painting and corrective shapes
   where real MCP/PIP folds need volume support. Do not change chord notes,
   finger assignments, string locations or guitar dimensions to fit the model.
4. If the rig or GLB changes, publish a new asset signature and explicitly retarget
   every stored pose from actual root/local-bone transforms. Verify unchanged
   contact worlds where claimed; never bypass the runtime hash/rig guard.
5. Repeat combined skin/clothing self tests, full guitar contact/wood/open-string
   checks and actual default/side/behind/player visual review for each pose.
   Keep needs-review if the image still has unnatural silhouette or floating cuts.
6. Recheck draw calls, triangle/texture budgets, lazy loading/disposal and physical
   iPad Safari. Exporting a model or Linux WebKit passing does not establish that
   device's native appearance or performance.
