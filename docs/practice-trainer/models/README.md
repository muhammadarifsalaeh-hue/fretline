# Practice trainer hand model

The runtime model is [`makehuman-left-arm-sleeved.glb`](../../../src/features/practice/assets/makehuman-left-arm-sleeved.glb). It combines a continuous MakeHuman left hand and forearm, the MakeHuman default hand rig and skin weights, an official MakeHuman skin texture, and a fitted sleeve adapted from Elvaerwyn's shirt. The body, rig, weights and skin are CC0; the sleeve is CC-BY. The combined model must retain the sleeve attribution.

> Black long sleeve shirt adapted from **elvs_male_shirt_untucked_bd1** by **Elvaerwyn** (2019), **CC-BY**, via [MakeHuman Community](https://static.makehumancommunity.org/assets/assetpacks/shirts02.html). Cropped to the left forearm, refitted, subdivided, rigged, ornamental cuff/button parts removed and materials adjusted for Fretline.

The official shirt listing says `CC-BY`; its OBJ and MHCLO headers say `CC_by`. They do not state a license version. This project preserves those terms and does not assign a version or relabel the sleeve as CC0. The original asset URL recorded by the official pack is <http://www.makehumancommunity.org/node/1800>; the official pack/listing links below provide the retained source route.

## Source and license record

| Component | Exact source | License and retained evidence |
| --- | --- | --- |
| hm08 body mesh | [MakeHuman commit `a8bc2d54ff0ac92e78ff71431b1023eda42bf482`](https://github.com/makehumancommunity/makehuman/tree/a8bc2d54ff0ac92e78ff71431b1023eda42bf482), `makehuman/data/3dobjs/base.obj` | CC0 1.0 Universal; [original mesh header](licenses/base-obj-header.txt), [MakeHuman license](licenses/MAKEHUMAN-LICENSE.md) |
| Default rig | Same commit, `makehuman/data/rigs/default.mhskel` | CC0; [embedded notice](licenses/default.mhskel-notice.json) |
| Default skin weights | Same commit, `makehuman/data/rigs/default_weights.mhw` | CC0; [embedded notice](licenses/default_weights.mhw-notice.json) |
| Skin albedo | `skins/young_caucasian_male/young_lightskinned_male_diffuse.png` in the [official CC0 system asset pack](https://files2.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip), [listing](https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html) | CC0, explicitly released September 2020; copyright holders at release: Data Collection AB, Joel Palmius, Jonas Hauquier; [original material notice](licenses/young_caucasian_male.mhmat) |
| Sleeve geometry, fitting map and albedo | `clothes/elvs_male_shirt_untucked_bd1/` in the [official CC-BY Shirts02 pack](https://files2.makehumancommunity.org/asset_packs/shirts02/shirts02_ccby.zip), [listing](https://static.makehumancommunity.org/assets/assetpacks/shirts02.html) | Elvaerwyn, created/changed 2019-03-31, CC-BY; [OBJ notice](licenses/shirt-obj-header.txt), [MHCLO notice](licenses/shirt-mhclo-header.txt), [original material](licenses/mens_shirt_untuck_elvbhp1f.mhmat) |

The MakeHuman asset license is separate from its application's AGPL source-code license. The source application's program logic is not part of this model. MakeHuman's retained license explains the distinction and links to its [full asset legal statement at the pinned commit](https://github.com/makehumancommunity/makehuman/blob/a8bc2d54ff0ac92e78ff71431b1023eda42bf482/LICENSE.ASSETS.md). The canonical CC0 text is <https://creativecommons.org/publicdomain/zero/1.0/legalcode>.

The source files were acquired during the 2026-10-24 UTC authoring session. The garment and skin manifests retain the recorded retrieval date, original pack metadata, selected ZIP member information and source SHA-256 digests. The MakeHuman manifest records the pinned commit, source URLs, source digests and the available date evidence:

- [MAKEHUMAN_PROVENANCE.json](licenses/MAKEHUMAN_PROVENANCE.json)
- [BLACK_SHIRT_PROVENANCE.json](licenses/BLACK_SHIRT_PROVENANCE.json)
- [SKIN_PROVENANCE.json](licenses/SKIN_PROVENANCE.json)
- [DERIVED_SKIN_PROVENANCE.json](licenses/DERIVED_SKIN_PROVENANCE.json)

## Authoring and exported model

The editable native source is [`authoring/MakeHuman_Left_Arm_Source_UNPOSED.blend`](authoring/MakeHuman_Left_Arm_Source_UNPOSED.blend). It retains the separate body and garment meshes, 22 deform bones, skinning groups, materials and packed texture images. The Blender authoring script is [`authoring/build_makehuman_arm.py`](authoring/build_makehuman_arm.py). Its external input root defaults to `/tmp/fretline-trainer-assets` and can be set with `FRETLINE_MODEL_SOURCE`.

The body was cropped from the authored hm08 mesh using its left arm skin influences, preserving one continuous hand-to-forearm surface. Source topology was subdivided once, UVs and weights were transferred, and each vertex's largest four weights were normalized. The wrist is the origin; MakeHuman's original handedness is retained. Source MakeHuman units were converted to metres (one source unit = 100 mm), with Blender Z-up converted back to glTF Y-up on export. The final runtime scale is 1,000 mm per GLB unit.

The sleeve was selected from the real shirt mesh, fitted with its MHCLO base-vertex barycentric map and offsets, cropped to the left forearm, subdivided once, assigned transferred body weights and iteratively adjusted toward 1 mm clearance against the refined body surface. The complete continuous cloth panel was retained; four disconnected ornamental cuff/button components were removed after triangle-crossing inspection found 318 intersections involving those details at rest. The authoring script selects the cloth component by its spatial extent. It does not implement the full MakeHuman shear-reference fitting algorithm. The shirt's original charcoal albedo is embedded with a rough cloth material. A white sheen layer was removed after native and GLB render inspection because it washed out the black cloth. The original skin PNG was converted to an embedded RGB JPEG at quality 88 with its 2048-pixel dimensions retained. No separate skin normal or bump texture was supplied by the source pack.

The exported GLB contains two skinned meshes and two embedded textures. The skin has 7,888 exported vertices and 14,760 triangles; the sleeve has 734 exported vertices and 1,304 triangles. UV seams account for the difference between exported skin vertices and the native body's 7,407 vertices / 7,380 polygons. The native sleeve has 678 vertices / 652 polygons. The model has 22 named deform bones: two forearm bones, the wrist, four metacarpals and three joints for each of five digits.

At this documentation revision, the runtime GLB is **1,012,288 bytes** with SHA-256 **`23fdb5745e9343b597eb816bcdfcb266c1942ebbbb495cdb3776214343d7f3bc`**. [`makehuman-left-arm.metadata.json`](../../../src/features/practice/assets/makehuman-left-arm.metadata.json) records the runtime asset signature and named chains. [`authoring/rig-data.json`](authoring/rig-data.json), generated by [`inspect_exported_rig.py`](authoring/inspect_exported_rig.py), records the actual GLB transforms, mesh buffers, weights and inverse bind matrices for both skinned meshes. [`authoring/hand-rig-equivalence.json`](authoring/hand-rig-equivalence.json) confirms that the sleeve cleanup preserved every hand attribute byte, triangle index, inverse bind matrix and bone node. The final native and GLB hashes and modifications are recorded in [`licenses/MODEL_DERIVATION.json`](licenses/MODEL_DERIVATION.json).

## Model audit and anatomical reference

[`authoring/model-audit.json`](authoring/model-audit.json) records the final GLB checks: finite positions, normals and matrices; unit normals; normalized nonnegative weights; valid joint and vertex indexes; and inverse-bind rest reconstruction error below 0.000001 metres. After merging duplicate positions at UV seams, the skin is one connected component of 7,407 vertices and the sleeve is one connected component of 678 vertices. [`authoring/native-audit.json`](authoring/native-audit.json) records the editable model's continuity, identity pose transforms and packed images. The native source includes the actual 1024px shirt PNG and 2048px derived skin JPEG; it has no external texture dependency.

[`authoring/rest-triangle-crossing-audit.json`](authoring/rest-triangle-crossing-audit.json) reports zero nonadjacent segment/triangle crossings or coplanar interior overlaps in the combined final skin and sleeve at rest. The rest check reconstructs the actual exported mesh-node world transforms and can be repeated with [`audit_source_rest.py`](authoring/audit_source_rest.py). The retained C candidate diagnostic also reports zero segment/triangle crossings with the same final garment; that older candidate check omitted coplanar contact. These are rejection diagnostics and do not certify a guitar pose. Removing the ornamental parts reduced the model by 103,372 bytes while retaining the complete cloth panel and unchanged hand.

The two-sided textured review confirms that the model's palmar normal in glTF coordinates is **`[-0.819485, -0.563422, -0.104883]`**. Define `F = middle MCP - wrist` and `W = little MCP - index MCP`; the palmar direction is `normalize(W × F)`. The opposite `normalize(F × W)` view shows the fingernails. In [`review/palmar-landmarks.png`](review/palmar-landmarks.png), red markers identify the positive surface patches on the five fleshy distal pads. In [`review/dorsal-landmarks.png`](review/dorsal-landmarks.png), blue markers identify the negative patches on the nail side. The existing positive/negative landmark keys are preserved, with explicit palmar/dorsal aliases added to metadata and rig data. These renders inspect the exported GLB; review markers are excluded from the model.

To repeat the audit from the repository root:

```sh
python docs/practice-trainer/models/authoring/inspect_exported_rig.py
python docs/practice-trainer/models/authoring/audit_source_rest.py
blender -b --python docs/practice-trainer/models/authoring/audit_native_source.py
FRETLINE_REVIEW_GLB=1 FRETLINE_REVIEW_MARKERS=1 blender -b --python docs/practice-trainer/models/authoring/render_anatomy_review.py
```

The buffer inspection script uses NumPy and SciPy. The Blender review uses Cycles CPU rendering without a denoiser and writes two images under `/tmp/fretline-trainer-assets/review/`.

This is an unposed anatomical source. Exporting, rendering or passing geometry checks does not certify any guitar chord pose. Chord-contact, palm orientation, thumb placement and collision evidence must be evaluated for each actual scene pose.
