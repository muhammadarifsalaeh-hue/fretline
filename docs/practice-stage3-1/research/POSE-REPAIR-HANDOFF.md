# Stage 3.1 pose repair — stop gate and Blender handoff

All work here is research under `/tmp/fretline-stage31-assets/pose`.
No application file, catalog ID, route or master branch was modified by this agent.
**No C Major pose is approved. Automatic optimization has stopped.**

## Concrete findings

1. Source nails are on native +Y; flat palmar flesh faces native −Y. The original
   thumb contact face 2017 is a nail-rim/tip-edge face: nearest nail distance
   0.113 source unit, outward normal (−.835,−.216,+.507). It was not a sound
   palmar pad target. Actual thumb palm-side flesh includes face4957, while
   distal palmar-tip flesh also includes5260/2606. A single fixed face is too
   restrictive; use a semantic flesh patch and actual skin contact.
2. Index contact face4420 was a radial-side cap, with normal
   (−.711,−.349,+.610), caused partly by the bone end lying off the actual skin
   center. The native index nail centroid X is−6.213, whereas the distal bone
   tail X is−6.559. Basing skin contact on the bone endpoint alone therefore
   induced extra roll. Middle3157 is central but mostly forward cap normal
   (−.397Y,+.916Z). Ring4646 is flesh but laterally biased. Full measurements and
   alternative faces are in `flesh-pad-landmark-audit.json`.
3. A forward cap facing native +Z transforms differently from a palmar pad
   facing native −Y. With the old global Rx≈.5/Rz≈π basin, forcing a cap normal
   downward can require too much total MCP/PIP/DIP curl and produce a hand
   wrapping from the low-E side. Moving only the wrist translation did not
   repair that orientation.
4. Actual semantic palmar patches were extracted from unchanged V2 geometry:
   native outward normal Y<−.65, distal bone influence>.6, longitudinal fraction
   .6–1.25, distance from actual nail>.3 source unit. Closest barycentric skin
   points were used; no geometry was hidden, fabricated or moved off rig.
5. Exact target contact points are insufficient. The semantic probe matched all
   four targets within .006mm and correct thumb normal but routed the hand
   through the closed neck. It must not be called nearly correct.
6. Native Blender bone modes matter. The rig researcher discovered some source
   MCP/meta bones use QUATERNION mode; setting rotation_euler without first
   setting rotation_mode='XYZ' ignored those changes in some helper sweeps.
   Those isolated MCP-clean claims are withdrawn. Our numeric FK and the
   independent actual-GLB evaluator always applied explicit Euler XYZ matrices.

## Attempts and final rejection

- `balanced-c-attempt-2.json`: exact original GLB four weights, plausible coarse
  contact but independent self-intersection count250 and wrong thumb orientation.
- `painted/balanced-c-attempt-0.json`: V1 reweighted skin, safer flexion limits,
  no fake mesh. Independent gate127 self-crossing triangle pairs and actual
  string intersections. The parent may use the V2 weight version of this pose
  solely as a recognizable failed diagnostic, with prominent failed status.
- `thumb/`: true broad palmar thumb-only optimization with other fingers fixed
  could not orient/contact correctly within source bounds. The wrist/palm
  orientation had to change, rather than force the thumb against a nail edge.
- `palmar-v2/`: full-hand true-pad attempt still failed thumb position/orientation.
- `high-e-v2/`: merely translating the old orientation onto the high-E side failed
  contact by tens of millimetres. This was not a valid chord pose.
- `palmar-patch/patch-ik-0.json`: semantic skin-point IK without obstacles matched
  points but the independent actual-GLB audit found ~10.48mm hand and7.96mm nail
  wood penetration. Its two self-intersection pairs do not make it acceptable.
- `palmar-patch-final/`: last bounded normal-pressure/basin feasibility probe,
  finished in12seconds after vectorization. Warm semantic and distinct physical
  orientation seeds both failed. Found actual whole-mesh witness depths:
  **10.445mm hand /8.520mm nails** and **10.438mm hand /9.544mm nails**.
  The physical seed also left index/middle pressure normals with positive Y and
  thumb normal with negative Y. See `final-probe-rejection.json`.

These found witness depths are not exhaustive global maxima. They suffice to
reject the candidates. No further optimization is scheduled here.

## Recommended manual work

Use the editable Blender scene prepared by the parent, retaining source credit
and the CC BY-NC4.0 educational restriction. The actual exported normalized
four-weight V2 GLB must remain the downstream audit authority.

1. Set every pose bone to explicit XYZ mode before scripted angle assignment.
   Keep the source untouched and work in a derivative. Preserve existing left
   reflection, scale, actual six-string guitar and closed neck collision proxy.
2. Establish a plausible left-hand wrist/palm position from an actual C Major
   reference before moving fingertips. Palm lies outside the high-E edge;
   neither all MCPs at Z≤−25 nor palm Y≤−15 should be treated as universal
   anatomical requirements. Thumb's palmar flesh faces the neck back.
3. Place index B1, middle D2 and ring A3 using visible palmar fingertip flesh,
   not bone endpoints or nail rims. Keep G and high-e open. Adjust root,
   metacarpal spread and all phalanges together, checking side/back/player views.
4. Correct MCP/web and opposition weights/creases with visible mesh wireframe.
   Use proper corrective shape keys/topology where skin compresses at a bend;
   never remove fingers or hide collision geometry to make a screenshot pass.
5. Check the actual depressed string contact arc rather than a sharp V knot
   under a rounded finger pad. The parent has investigated a real tangent
   contact arc. Preserve the following fret support, string identity and note.
6. Export the intended evaluated deformation and joint poses explicitly.
   Blender constraints, dual-quaternion skinning and pose correctives do not
   automatically become equivalent glTF LBS behavior. Reimport the export and
   repeat contact/wood/fret/open-string/self-intersection tests on that file.
7. Only after those pass should the parent integrate with `/practice` and run
   actual browser/viewport/regression tests. Physical iPad Safari remains a
   separate device test.

Weight-repair reductions across different poses must not be presented as an
apples-to-apples percentage improvement. Use the independent same-pose actual
GLB reports for any such comparison. The C prototype remains unapproved.
