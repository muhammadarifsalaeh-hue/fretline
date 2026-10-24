# Stage 3.1 — final rig/weight evidence and remaining blockers

This is a gated research/authoring handoff, not a completed teaching pose. No app or catalog file was edited by this audit. Source hand ©2026 Emma L. D. Lieker, CC BY-NC 4.0, pinned creator commit `f27f19f55f8270b3108ea0b53ce5aa81c543ff7c` at https://github.com/emmalieker/anatomical-hand-model . Preserve source attribution, license and modification notice. Source .blend is a newer Blender4.5 file opened by installed4.3.2; that environment warning is not a universal statement about the author's asset.

## Skeleton, controls and real source state

There are21bones: radius/ulna root; four `meta→prox→midd→dist` finger chains; thumb `trapez→meta→prox→dist`. LocalY follows the segment. LocalZ is the main flexion hinge; localX spread and localY twist matter as well. Source metacarpals and finger MCP/prox bones use **QUATERNION** rotation mode; PIP/DIP bones generally useXYZ. Any script assigning Euler angles must explicitly set every controlled bone toXYZ, or supply the equivalent quaternion.

Author Copy Rotation copies `midd_meta` localXYZ into pinky/ring/index metacarpals at influence1 and thumb_trapez at influence.8. It does not provide PIP/DIP coupling. The source has only Armature modifiers, no corrective-shape or corrective-smooth modifier. Native source supports up to6weights per vertex; GLB stores4normalized weights. Use exact exported4-weight geometry as final collision authority.

## Audit correction and verified controls

The original16case `rig-deformation-audit.json` setXYZ explicitly and remains valid: rest0selfcrossings; oldC export4LBS402, DQ369; originalconstraints restored358LBS/361DQ. DQ/constraints alone do not fix the pose.

An initial follow-up helper incorrectly assigned Euler channels while MCP/meta bones remainedQUATERNION. Its MCP sweeps/profile claims were invalid and have been withdrawn. Such files were renamed `*-INVALID-quaternion-mode.json`; do not distribute them as passing evidence. Corrected helper `audit-rig-deformation.py` setsXYZ before every controlled experiment. Corrected native Blender and the actual GLB now both reproduce **113**self-crossing pairs for V2 on the same painted0pose, not the earlier erroneous72. All5534native/rest triangle triplets match the original actual GLB; topology was not the discrepancy.

Corrected `joint-bend-sweep.json` has150cases. Original finger PIP45° is0crossings, PIP60°12–19pairs. Original MCP is not universally clean: indexMCP75°4/90°29; middleMCP60°3/90°21; ringMCP75°12/90°20; pinkyMCP75°18/90°28. Corrected `painted-mcp-sweep.json`36cases confirms that V1 IP-only repaint does not fix MCP90–120compound bends. These are deformation observations, not human clinical ROM limits.

## Genuine but partial weight-only correction

`build-weight-repairs.py` deterministically rebuilds:

1. V1: nearest eligible fingerPIP/DIP and thumbMCP/IP joint-local linear parent/child ramp over±1.0source unit, radial radius1.25, requiring at least.8existing family influence.
2. V2: additional non-thumb MCP parent-meta/child-prox ramp over±1.0source unit, radial radius1.8, same.8family threshold. It adds166native vertices toV1 and does not add another thumb repaint merely to fit the incorrect old thumb contact.

No rest vertex, UV, normal, index, skeleton or nail geometry is moved/hidden/replaced. Influence count stays≤4 and normalized. V2changes918of2829native Hand weights, corresponding to998of3148UV-split exported vertices. Nails remain single-weight and unchanged.

**Fair same-pose actual-GLB self-intersection comparison:** painted0C has133pairs originalGLB,127V1,113V2. This is a20pair reduction, not a repair from402to113on the same pose. The latter comparison would mix different poses. MCP/index-ring, thumb/web and combined-pose defects remain. Isolated hinge experiments cannot approve a fullCpose.

Exact asset: `anatomical-hand-weight-repaired-v2.glb`,3,363,664bytes, SHA256 `c05abb56202970afae7dfd78abacd44ac11e11f88ef8effdcd3f639af041ec13`.

Exact native-index weight authority: `fk-source-patched-v2.json`. `weight-patch-v2-integrity.json` proves only HandJOINTS_0/WEIGHTS_0 accessor bytes changed; all other binary bytes and mesh/skeleton/nail data unchanged. `weight-patch-v2-validation.json`: Khronos0errors,3existing warnings,1info. Structural validity is not anatomical/contact approval.

## Anatomical landmark and physical pose findings

Source isRIGHT: dorsal non-thumb nails lie on native+Y, palm/pulp on−Y, thumb on−X, fingers longitudinal+Z. A reflection is required for the frettingLEFT hand.

Old thumb face2017 is a nail-rim/tip-side landmark, nearest nail vertex only.113source-unit. It must not be forced into the neck as a palmar pad. Broad palmar thumb candidate4957 has normal[.244,−.963,−.117]. Old finger faces4420/3157/4646 are ventral tips, but index is strongly lateral and middle tip-axis heavy. Centered palmar-tip candidates2557/4974/1834 have more ventral normals; all match actual GLB triangle IDs exactly. Selection still needs visual and full-surface contact verification, not endpoint fitting alone.

`physical-root-seeds.json` and `contact-anatomy-notes.md` describe a distinct quarter-yaw orientation family for a high-E-side grip, rather than translating the old low-E wrapping branch. No seed is a validatedCpose. Global rotation bounds can exclude the needed orientation family, and wrong target normals can force impossible rolled/nail-first contacts.

The latest semantic point-IK candidate reported by the independent gate has near-perfect selected points and only2selfpairs but still **Handwood≈10.48mm and Nailswood≈7.96mm penetration**. It fails decisively. Do not present endpoint convergence, validation0errors, or reduced fold counts as a completed human hand trainer.

## Necessary next authoring work

Use the editable Blender hand with actual exported weights, correct thumb/pulp landmarks and a physically plausible wrist/palm branch. Manually adjust bone rotations/weight painting and, if needed, legitimate anatomy-preserving corrective shapes; export and rerun the exactGLB gate. Do not hide fingers, replace geometry with cylinders, push a point through wood, or applyDQ and assume an ordinaryLBSGLB reproduces it. If the rig cannot achieve the pose naturally, use an appropriate purpose-built left fretting hand with a suitable license. Current assets remain explicitly unapproved for teaching and must not be adopted into `/practice` until all relevant gates pass.
