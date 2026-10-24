# Experimental rig transfer evidence — not app adoption

The native Blender Hand mesh uses up to six influences; the original exported GLB retains four normalized influences. The unchanged optimized GLB preserves those original GLB accessors exactly. Comparing the same C pose through these two authorities gives **1.444338 mm maximum skin displacement difference**, with **108 of 3148 GLB vertices over 0.1 mm**. Nails are single-weight and match. This is not a transform bug: hierarchy reconstruction differs by only 2.67e-15, and rest positions map exactly.

`prove-runtime-transfer.py` records that discrepancy in `runtime-transfer-audit.json`.

`build-gltf-compatible-fk.py` builds `fk-source-gltf-compatible.json` by mapping the original GLB four weights back onto unchanged native positions/triangles. All UV-split duplicate vertices carry identical weights, and all native vertices have a match. Against this explicit exported-weight authority, the runtime joint-local matrix proof matches to **8.99e-14 mm**. This only proves coordinate conversion and matrix baking, **not a playable or collision-free pose**.

- `runtime-transfer-gltf-compatible-audit.json`: exact exported-weight mathematical comparison.
- `c-major-runtime-pose.json`: conditional column-major joint locals and outer transform, explicitly marked unapproved. Do not adopt it while collision gate fails.
- `hand-runtime-transfer-points.npz`, `nails-runtime-transfer-points.npz`: `gltfPosedMM` and `triangles` contain the actual original exported-mesh C pose for collision audit, not an assumed native deformation. Other keys preserve rest positions and native mapping.

No app files, dependencies, source-model geometry, or original GLB weights were changed. No custom shader was introduced. If continuing after user review, use the actual exported GLB four-weight mesh as the **single pose/collision authority**, manually correct thumb/nail positioning and self-contact, and rerun full-triangle contact and wood/fret/open-string clearance audits. Do not tune only native six-weight coordinates then assume runtime equivalence. The rig source remains CC BY-NC 4.0 by Emma L. D. Lieker; source attribution, license and modification notice remain necessary for adoption.
