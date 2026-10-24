# Stage 3.3 — hand, forearm and black long-sleeve feasibility

Accessed 2026-10-24. This is a source/model inspection, not asset adoption or C Major approval. No repository, application, guitar database, package or dependency was edited. Files downloaded only into this temporary research folder. No purchase or account sign-in was attempted.

**Decision: no inspected model currently meets the full requested combination of a realistic left hand, continuous forearm, natural black long sleeve, and an anatomically/collision-correct C Major.** The existing Stage 3.1 hand is still rejected. Adding a primitive forearm/cylinder sleeve or silently using a stylized asset would not satisfy the reference. The user explicitly requires alternatives to be approved before that substitution.

| Candidate | What was actually inspected | License/cost | Decision |
| --- | --- | --- | --- |
| Existing Emma L. D. Lieker hand | Existing Stage 3.1 GLB/Blender evidence: anatomical hand/wrist, 21-bone rig; C still fails open-G, skin-fold and posture gates. No supplied full forearm/black garment. | CC BY-NC 4.0, credited educational use; not a commercial grant | Cannot treat it as a complete sleeved performer or approved C pose. Extending/garment authoring needs proper Blender work. |
| Blender Studio Rain v3.3 | Official ZIP actually downloaded (67,579,177 bytes), native `rain_v3.2.blend` inspected in Blender 4.3.2 with auto-execution disabled. Rig has 2,166 total bones including controls/helpers; body base 20,462 triangles with 72 shape keys, and real continuous left-hand/forearm groups. Top has 3,112 base triangles/17 shape keys and upper-arm groups but no forearm/wrist groups; it is not a supplied long black sleeve. | Free CC BY 4.0. Required credit: `Rain Rig (CC) Blender Foundation | studio.blender.org` | Production animation source is promising for an authoring experiment, but visibly stylized and not a ready realistic sleeved guitar hand. Would need asset choice approval, clothing work, rig pruning/baking, GLB export and full C validation. No C pose was attempted. |
| Blender Studio Snow v4 | Official creator page fetched normally and CC BY 4.0 link/credit inspected. Binary was **not** downloaded or inspected. Creator describes this character family as stylized. | Free CC BY 4.0, credit required | Page-level candidate only; cannot claim its mesh/garment/GLB meets the requirement. |
| WRAD ARMS | Pinned creator GLB actually downloaded and parsed: 456,328 bytes, 1,196 triangles, 872 GLTF vertices, 50 joints for both arms/hands, one skin-albedo material and no separate cloth mesh. | Creator README explicitly CC0 1.0, free | Genuine rigged arm geometry but deliberately retro/low-poly. Reject for the realistic reference; do not repaint it black and call it realistic clothing. |
| MakeHuman / MPFB asset pipeline | Official license/asset pages inspected: CC0 base/system assets and arm/hand morph targets; Shirts02 contains CC-BY long-sleeve garments with individual author credits. No assembled character, rigged garment or C GLB was generated or validated. | Free assets, CC0 and CC-BY depending on the selected item | Potential realistic authoring route, not a ready replacement. Needs approval to choose/body-fit a specific garment, rig and pose it, create appropriate correctives, bake/export and validate C. Morph packs are not an already valid guitar grip. |
| Fab: Oleg Shuldiakov, `Man Arms - Male Hand - First Person Arm - Coat Sleeve - FPS - RIGGED - animated` | Primary listing only: advertised 8,596 triangles, 2048 color/normal/specular textures, rigged/animated, black coat-sleeve tags, FBX and converted GLB. No binary, finger weighting, left-hand anatomy or C pose was inspected. | Listing requires selecting a license and `Buy now`. Exact price was not exposed by the fetched page; do not quote one. | Most visually relevant shortlist entry, but requires legitimate acquisition and suitable web-project license, followed by actual inspection. Do not assume listing photographs prove rig or C correctness. No purchase made. |

## Primary sources

- Existing hand: https://github.com/emmalieker/anatomical-hand-model/tree/f27f19f55f8270b3108ea0b53ce5aa81c543ff7c
- Rain: https://studio.blender.org/characters/rain/v3/
- Rain actual creator download: https://studio.blender.org/download-source/files/ee/a7/eea73e55dba1cea31c09848df6a794b2-4.zip
- Rain/Snow license: https://creativecommons.org/licenses/by/4.0/
- Snow: https://studio.blender.org/characters/snow/v4/
- WRAD pinned README: https://raw.githubusercontent.com/wwwriks/wrad-arms/f3987244176c33d2c20d4f9e139980af12684d87/README.md
- WRAD actual GLB: https://raw.githubusercontent.com/wwwriks/wrad-arms/f3987244176c33d2c20d4f9e139980af12684d87/arms.glb
- MakeHuman license: https://static.makehumancommunity.org/about/license.html
- Asset packs (license sections matter): https://static.makehumancommunity.org/assets/assetpacks.html
- Long-sleeved collection: https://static.makehumancommunity.org/assets/assetpacks/shirts02.html
- Paid shortlist: https://www.fab.com/listings/cf7404fb-58a1-45dc-a30d-1842cdffc33a?lang=en

## Binary evidence and limits

`download-audit.json` contains exact URLs, HTTP200 results, byte counts and SHA256 hashes. `wrad-binary-inspection.json` records actual GLB data. `rain-native-inspection.json` and `inspect-rain.py` record actual Blender objects, bones, groups, shape keys and modifiers. The Rain ZIP SHA256 is `80217f163f6392dc829233d63c2cfb5e1376775bc34101ad14f39631fea70d24`.

Rain contains embedded `cloudrig.py` and `rain_shading.py`; they were deliberately not auto-executed for this data inspection. No statement that its full authoring rig, custom drivers, animation or skin export works in this environment is warranted. The 2,166 count includes helper/control bones, not the number of required final web skin joints. Total raw mesh triangles include hidden variants/proxies and are not a measured visible-frame budget. No iPad GPU test was performed on any candidate.

A search-provider fetch reported HTTP402 for the Blender pages, but normal permitted HTTP to the same official pages and public download returned HTTP200. Therefore do not report the official models as inaccessible or paywalled based on that provider error.

## Alternatives requiring user choice before further model work

1. **Recommended quality route:** obtain a suitable purpose-built licensed left hand + continuous arm + natural long-sleeve garment, or have a model artist adapt the existing Blender source with genuine anatomical corrective deformations. Inspect the actual source file and license, then make and audit C Major before website integration. The Fab item is only a shortlist example, not an approved purchase or verified C solution.
2. **Free-source authoring route:** approve choosing a specific MakeHuman/MPFB body and CC-BY long-sleeve asset as the new modeling base, including author credits. This requires manual clothing fitting/cloth folds, hand rig/correctives, left-hand C posing, web export optimization and a new full collision audit. It is not an automatic ready-made fix or a new Fretline website.

Camera/layout work can proceed independently. Do not add an invented sleeve, hide an incorrect hand behind clothing, imply this research completes Stage 3.3, or merge master. The user's physical-iPad Safari check remains required before merge approval.
