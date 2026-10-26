# Independent final guard and rig review

Reviewed the pending changes on `feature/guitar-practice-3d` against `96e0449`.
This review changes no runtime code, chord data, model, weights, acceptance
threshold or teaching approval. No browser, physical iPad, heavy pose fit or
new model was created by this review.

## Completed quick checks

| Command | Actual result |
|---|---|
| `node scripts/check-hand-runtime.mjs` | 20/20 passed |
| `node scripts/practice/check-final-camera.mjs` | Passed at desktop, tablet and mobile aspects |
| `node scripts/practice/check-hand-reveal.mjs` | 10/10 passed |

Logs and exit codes are in [quick-tests.json](quick-tests.json) and the adjacent
`*-check.txt` files. These are Node state/geometry checks; they do not certify
actual browser rendering or anatomical accuracy.

## Guard behavior

- Actual GLB SHA-256, metadata/library SHA references, schema, units and the
  unique named rig must match before a candidate can be applied.
- A complete candidate remains applied to the **hidden** real rig for diagnostic
  bone/root fingerprints. This retains all 42 distinct poses without exposing
  a rejected hand in the visible scene.
- Inspection now requires both `collisionPassed === true` and
  `contactPassed === true`. Missing values, `false`, the string `"true"`, numbers
  and null do not grant inspection. The tests cover direct programmatic calls,
  not only the absence of a button.
- A rejected inspection request clears `reviewMode`, leaves the wrapper hidden,
  and publishes `inspectionAllowed: false`. The scene's string/marker controller
  uses actual visibility, so a hidden hand retains the diagram/gold-marker
  fallback and open study-string geometry.
- The React viewer only offers inspection when the current chord, ready asset,
  pending-review status and strict inspection flag agree. Old chord state does
  not expose a new chord's inspection control.
- Teaching approval remains stricter: status `verified`, `reviewed === true`,
  and all four collision/contact/anatomy/multi-view gates must explicitly pass.
  Geometry-only inspection never changes those teaching conditions.
- The new actual-library test binds a completed 42-row mesh report to the current
  library and model hashes. It confirms the allowed inspection set equals the
  exact geometric acceptance set. With the current source this is seven:
  C, Cmaj7, Am7, Em7, E7, Fmaj7 and Dm. There are no verified teaching hands.

No blocking defect was found in this guard change. The original 17 runtime
checks remain, with three stricter checks added rather than removed. Their
renderable fixture now represents a geometrically passed but anatomically
unapproved pose, matching the seven eligible real candidates.

The old browser prototype case allowed rejected F to be revealed. The final
owned harness must instead assert that F's inspection control is absent, the
hand stays hidden, and the actual correct diagram/marker fallback remains.
That is a stronger display policy, so it should be described as an adapted
21-case plan rather than an entirely unchanged historical suite.

One minor handover behavior merits the existing rapid-change browser check:
React's scene chord synchronization uses a passive effect and the renderer
redraws on requestAnimationFrame. Source inspection alone cannot establish
whether an old canvas image is retained for a display frame while the warning
changes. This review did not reproduce such an artifact and does not claim it
as a confirmed bug. Programmatic state rejection itself passed.

## Camera correction

The former player direction had negative world Y, placing the eye behind the
fretboard and exposing rear wood. The new player direction uses positive Y
while retaining the low-E-edge view. The quick perspective checks confirm the
board face is nearer than the rear neck, low E projects above high e, and the
headstock projects right/up at three aspect ratios. The original default
camera direction is unchanged. Actual browser screenshots remain a separate
acceptance step.

## Rig and source findings

The existing [measured source report](../rig/measurements.json) is consistent
with the inspected authoring/runtime code:

- 22 real bones, five articulated digit chains, a wrist, metacarpals and forearm.
- Skin: 7,888 vertices and 14,760 triangles. Sleeve: 734 vertices and 1,304
  triangles. Both have finite nonnegative normalized weights, no zero-weight
  vertices, and no more than four active influences per vertex.
- Weight-sum ranges are approximately 0.999999888–1.000000116 for skin and
  0.999999940–1.000000089 for the sleeve. These small floating-point variations
  do not indicate a globally corrupt skinning export.
- The initial alignment basis has determinant +1. All measured positive
  one-degree flex rotations curl toward the original palmar normal. No global
  mirror or reversed flex-axis defect was established.
- In current C, the palmar world normal is approximately
  `[-0.210, -0.641, +0.738]`. The default front-side camera sees the dorsal side;
  flipping the hand to correct its flat-looking texture would be unjustified.
- Current C MCP heads lie at z approximately −52 to −57 mm and y +13 to +22 mm,
  well outside the study board's lower edge around z −23 mm. The source fitting
  objective can satisfy distal targets while accepting this extended hand
  placement. A root/palm-placement objective and neighboring-surface clearance
  are relevant central-solver constraints.
- Actual combined bone-axis angles include source rest bend and abduction. For
  example C's index/middle/ring MCP axis angles are about 35.49°, 27.51°, 45.35°.
  These are **not clinical isolated joint-flexion measurements** and should not
  be confused with rest-relative authoring deltas.
- Measured distal skin spans are roughly 12–13 by 14 mm for index/middle/ring,
  versus about 7 mm string spacing. The unchanged accepted contact region has
  4.9 mm longitudinal range. Adjacent same-fret contacts therefore require
  careful approach angle, distributed curl and surface placement. This is a
  constraint to solve, not proof of impossibility and not a reason to loosen
  the test threshold today.

Normalized weights do not guarantee a good deep bend or prevent local skin
folding. The source rig has no authored corrective shape for every deep or
barre pose. These observations justify central placement/collision work; they
provide no evidence for a speculative wholesale rewrite of otherwise intact
skin weights.

## Material and cropped-source limits

`build_makehuman_arm.py` requests Blender Principled subsurface weight 0.07 and
radius `(1, 0.4, 0.22)` for skin. The actual exported GLB material JSON contains
core metallic/roughness parameters, base-color textures, roughness approximately
0.52 for skin and 0.88 for cloth, and **no material extensions**. It contains no
exported subsurface, normal-map or roughness-map property. The runtime hand
loader does not add a custom subsurface implementation. Thus the Blender
subsurface request is not represented by the exported web material. This can
contribute to flat skin appearance; it does not establish that lighting alone
will produce the reference-level hand.

The source is a cropped hand/forearm with a connected real black sleeve. It does
not provide an entire elbow/upper arm. A source-correct full-arm continuation
and artist-authored corrective deformation remain unresolved. Adding transparent
skin or primitive arm geometry would not prove those requirements satisfied.

The source and license metadata remain unchanged: CC0 body/rig/weights/skin and
CC-BY sleeve, with version unspecified by the source. [source-bindings.json](source-bindings.json)
records byte equality to `96e0449` for model, rig data, musical definitions and
runtime pose library at this review point. No new asset-rights claim is made.

**This review grants zero anatomical or teaching approvals.** Final browser QA
and physical iPad Safari remain separate from the mechanical/Node evidence.
