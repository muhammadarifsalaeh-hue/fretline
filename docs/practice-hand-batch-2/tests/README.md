# Batch 2 browser acceptance

This directory contains the new batch checks and their reports. It does not
alter application code, musical voicings, images or hand approval statuses.

After the application source and production build are frozen, keep the preview
server running on port 5430 and run:

```sh
python docs/practice-hand-batch-2/tests/run-qa.py \
  --url http://127.0.0.1:5430 \
  --output docs/practice-hand-batch-2/tests/reports
```

The runner serializes the unchanged 21-case trainer suite in Chromium and Linux
WebKit, the unchanged 107-check browser regressions, the seven-preset/four-button
camera supplement and the new Cmaj7/Am7 actual-rendering checks. Serial execution
avoids competing software WebGL renderers. Existing known Phase 5–9 static
baseline failures remain separately reported; no assertion is rewritten here.

The new batch rendering checks compare the **actual applied root and bone
quaternion fingerprint** with the normalized saved source transforms. Merely
changing a chord label, a source-data hash or a precomputed diagnostic identifier
does not satisfy that check. Each engine captures Cmaj7 and Am7 at Desktop and
Mobile widths from default, side, behind-the-neck and player views, with the
unapproved warning. Changing chord must hide the prototype again; explicit
inspection, actual WebGL pixel changes, zoom and camera reset are verified.

Reports pin the production asset hashes before/after the run. The test fails if
the source pose library or build changes during a run. It does **not** certify
anatomy, physical contact, skin deformation, collision freedom or physical iPad
Safari. Those require separate mesh/contact and visual evidence.

The final reports distinguish unexpected Console/Runtime/Network errors from
deliberately injected failure cases in the original trainer suite. New batch
tests do not inject faults and expect zero unexpected errors.

## Observed initial idle timing failure

The initial Chromium run is retained as **20/21, failed**. Its performance case
sampled frame 2 after asset-ready while one hand-publish animation frame was
already queued. The diagnostic timeline records that frame executing later,
then frame 3 remaining unchanged for over five seconds with no further app rAF.
This was not a continuous render loop; the readiness signal preceded rendering.

`run-trainer-settled.py` loads the exact unchanged original suite and adds only
performance startup readiness: await two existing animation frames, then bounded
300ms stable actual canvas size/frame count. The original 250ms first-sample
delay and 800ms no-render assertion remain unchanged. The original application
and original suite file are not edited. A manifest pins the source/adapted
harness hashes. The focused Chromium retry is reported separately; its passing
case may combine with the original 20 passing cases from the same frozen build
as 21-case **coverage**, without relabelling the initial run as passed. WebKit's
full run uses the explicit readiness adaptation.
