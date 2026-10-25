# Independent C Major visual review

Reviewed 2026-10-25 UTC from the actual rendered **C-arm-variant** prototype. The
candidate, GLB and four screenshot hashes are recorded in
[C-arm-independent-review.json](C-arm-independent-review.json).

**Local finding: the wrist and individual digits look plausible in these four
views. Final acceptance: C Major remains `needs-review`, not an approved teaching
hand.** The separate C-pose reviewer still flags an elongated hand silhouette
and the exposed finite arm end, which can appear to float and does not meet the
strict reference requirement. The conservative project decision is
`anatomyPassed: false`; the positive local observations below do not override it.
Matching contact/collision success does not establish anatomical or
photorealistic production acceptance.

| Actual view | Visual observation |
| --- | --- |
| [Default](C-arm-angle.png) | Distinct curved fingers reach the fingerboard; wrist and forearm are connected. The revised forearm projects downward rather than appearing as a short foreshortened stump. |
| [Side](C-arm-side.png) | Human digits bend around the neck from behind. No grossly detached joint, folded skin or finger duplication is visible. Exact contact remains a geometric check because this view is nearly edge-on. |
| [Behind the neck](C-arm-back.png) | Thumb remains behind the wood. Palm, wrist and real sleeved forearm form a continuous surface without a visible disconnection. |
| [Player](C-arm-player.png) | The wrist direction is plausible and the arm remains connected. This freely rotated view exposes the finite forearm crop, which remains a presentation limitation. |

The +25° authored forearm rotation is compensated at the wrist. Every wrist,
metacarpal and finger joint retains its world position within 0.000007 mm; all
skin vertices without a forearm influence change by less than 0.0000072 mm.
Thus this adjustment preserves the independently audited string/fret finger
arrangement. It is not a new inverse-kinematics solution.

The finite source forearm has an open cut end visible in some orbit views. The
asset does **not** include an elbow, upper arm or torso. Lighting and the source
skin texture also remain less photographic than the reference. These limits
and the elongated silhouette remain unresolved parts of the user's visual
acceptance criteria. No full realistic musician or all-42-chords approval is
implied. The candidate remains hidden as a teaching example and can be opened
only in the explicitly labelled prototype inspection mode.

The inspection used actual Linux Chromium WebGL rendering. Physical iPad
Safari remains a separate acceptance step.
