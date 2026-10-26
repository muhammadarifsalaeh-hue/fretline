# Batch 3 browser validation

These are tests against an already-built, frozen production preview. They do
not edit runtime sources, install dependencies, approve anatomy, or infer iPad
hardware performance from Linux WebKit.

The runner serializes browser processes to avoid competing software renderers:

```sh
python docs/practice-hand-batch-3/tests/run-qa.py \
  --url http://127.0.0.1:5430 \
  --chords C,Em7,E7,Fmaj7,Dm \
  --output docs/practice-hand-batch-3/tests/reports
```

Use `--chords` for the actual integrated candidates (including C for explicit current four-view captures); source-to-rendered
fingerprints bind all saved root and bone transforms. Four actual camera views
(default, side, behind the neck, player), warnings, zoom, reset, and automatic
inspection closure on chord changes are checked on desktop/mobile Chromium and
Linux WebKit. This establishes rendering and application behavior, not natural
anatomical acceptance.

The existing 21-case trainer suite is unchanged. Its owned settlement adapter
adds only documented startup readiness before the same 800 ms idle assertion,
following the previously measured batch-2 queued startup frame. Both browsers
must actually pass all cases. The original 107 shared/gallery/camera checks and
the seven-preset/four-button camera supplement are also run unchanged.

The new hand-reveal suite checks native-clock completion, reduced-motion
immediate display, cancellation on chord change, disposal on navigation, and
stopped idle rendering. For reproducible half-opacity screenshots on software
GPUs, one additional case holds `performance.now` locally at elapsed 80 ms, then
160 ms, before restoring the native clock. Actual production WebGL, material
opacity, mesh geometry and saved bone rotations run unchanged. The half/final
screenshots must differ in real pixels while the exact actual pose and geometry
fingerprints remain equal. This controlled-clock case is not a hardware timing
measurement and does not claim a collision-free physical bone interpolation.

All hands remain hidden until explicit warned prototype inspection unless the
independent strict teaching-review gates already pass. A geometric endpoint
pass does not validate the swept path between two poses.

Completed frozen-build results: [RESULTS.md](RESULTS.md) and [the actual report](reports/final-summary.json).
