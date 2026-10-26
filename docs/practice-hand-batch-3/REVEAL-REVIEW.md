# Hand appearance transition review

Reviewed the uncommitted batch-3 `handReveal.js` and its integration into
`handPoseEngine.js`. This is a **160 ms appearance reveal**, not a physical
finger movement between chords. No anatomical or swept-collision approval is
claimed.

The engine applies exact saved root and local bone rotations while the wrapper
is hidden. It then reveals only a pose allowed by the unchanged approval gate,
or one deliberately opened in warned prototype inspection. Selecting another
chord still closes inspection and cancels the reveal immediately. It never
interpolates unchecked intermediate bone poses.

Material opacity and transparency return to each original value on completion,
cancellation, reset and disposal; depth-write and alpha-test settings are not
changed. Shared materials are recorded once. Reset drops old material references
before the GLB is disposed, and cancellation removes the queued animation frame.
The short reveal invalidates renders only while active and leaves no continuous
animation loop. Missing animation-frame support uses an immediate reveal.

Reduced motion skips the reveal. This review also fixed the case where the user
enables reduced motion *during* an active reveal: the next queued frame now
restores the complete original appearance and schedules no further frame.

## Executed checks

```sh
node scripts/practice/check-hand-reveal.mjs
node scripts/check-hand-runtime.mjs
```

- Appearance tests: **10 passed, 0 failed**, including exact unchanged bone/root
  values throughout, original per-material alpha restoration, bounded idle work,
  initial and mid-reveal reduced motion, rapid toggling, retry replacement,
  disposal and a runtime without animation frames.
- Existing hand runtime tests: **17 passed, 0 failed**, including the strict
  independent review gates, inspection closing on chord change, actual different
  applied bone signatures, request/parse cancellation, asset failure/retry and
  one-time disposal of shared GPU/image resources.

The first appearance run before the mid-reveal improvement was 9/9; the final
10/10 result includes the additional behavior and regression. Existing runtime
cases were unchanged. Browser normal-motion/reduced-motion, actual rendered
pixels, cancellation and idle-frame checks are assigned separately to batch-3
QA and are not claimed passed by this Node review. Physical iPad Safari has not
been tested here.

## Remaining limitation

A smooth physical transition requires a separately checked swept hand path.
Valid endpoint poses cannot prove that fingers avoid the neck and each other
between those endpoints. The present reveal safely improves presentation
without presenting an unchecked animation as instruction.
