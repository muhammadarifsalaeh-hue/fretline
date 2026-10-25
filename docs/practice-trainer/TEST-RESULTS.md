# Final validation — 25 October 2026

Validated the actual production build without changing its source/assets during
the canonical browser runs. This report does **not** certify 42 human poses.

| Check | Result | Evidence |
|---|---|---|
| Production build | Pass; Vite lazy-chunk size warning remains | [Transcript](tests/reports/build.txt) |
| Catalog | Pass; 200 unique IDs, 10 brands, exactly 20 each | [Check](tests/reports/catalog-final.txt), [ID snapshot](tests/reports/catalog-id-snapshot.json) |
| Images | Pass; existing product rights/registration retained | [Transcript](tests/reports/images-final.txt) |
| Practice data/geometry | 56/56 | [Transcript](tests/reports/practice-final.txt) |
| Independent musical/fingering audit | 86/86 | [Transcript](tests/reports/music-final.txt) |
| Physical pressed-string paths | 42/42 | [Transcript](tests/reports/strings-final.txt) |
| Hand runtime/loading/trust/disposal | 17/17 | [Transcript](tests/reports/runtime-final.txt) |
| Analytical contact-distance fixtures | 9/9 | [Transcript](pose-solver/contact-distance-tests.txt) |
| Chromium 154.0.8037.57 | 21/21 acceptance cases | [Report](tests/reports/final-chromium/browser-trainer-chromium.json) |
| Linux WebKit 26.5 | 21/21 acceptance cases | [Report](tests/reports/final-webkit/browser-trainer-webkit.json) |
| Existing shared site/browser regression | 18/18 | [Report](tests/reports/final-regressions/shared-regression.json) |
| Existing product gallery/integration regression | 79/79 | [Report](tests/reports/final-regressions/regression/browser-practice-trainer.json) |
| Existing five-width camera regression | 5/5 Chromium + 5/5 WebKit | [Summary](tests/reports/final-regressions/regression-summary.json) |
| All seven camera presets, rotate/zoom buttons and both resets | Pass in both engines | [Report](tests/reports/final-camera-controls/camera-controls.json) |
| Historical Phase 4 static checks | 19/19 | [Transcript](tests/reports/phase4-final.txt) |
| Historical Phase 5–9 static commands | **5 commands fail**, same failures on isolated baseline | [Comparison and exact assertions](tests/reports/legacy-static-baseline.md) |
| Anatomical teaching-hand approval | **0/42; all needs-review** | [Complete status table](CHORD-STATUS-42.md) |
| Actual iPadOS Safari | **Not tested** | [Manual device checklist](README.md#physical-ipad-safari-acceptance--still-required) |

The two new browser suites cover all 42 full and compact diagrams against an
independent voicing fixture; note pitches, base-fret labels and barres; search,
filters, history, keyboard, five widths (1440/1024/768/390/320), loading, actual
WebGL loss, real lazy-module/GLB HTTP failure and retry, touch, lazy route loading,
SPA disposal, actual per-chord rig transforms and explicit prototype inspection.
Both canonical suites have **zero unexpected console/runtime/network errors**.
Deliberately injected fault responses are recorded separately.

The unchanged original browser suites total **107 checks**, not 117. Shared
18 and gallery79 suites use Chromium; the camera suite and the new Practice
acceptance suite also run in WebKit. This distinction is retained in the reports.

## Performance evidence and limits

- Both engines stop rendering at idle. A zoom produces a new frame then settles;
  there is no continuous animation loop.
- At the measured viewport: hidden hand 78 draw calls / 15,500 rendered triangles;
  visible actual hand 68 calls / 30,912 triangles / 18 textures. Hidden schematic
  markers account for the different draw-call count.
- Three Chromium SPA unmount/GC samples: 8.42 → 8.84 → 9.07 MB JS heap, one
  document throughout. This is a bounded lifecycle check, not proof of zero leaks
  over unlimited use, and it does not measure native GPU memory.
- Actual unsupported-WebGL → pointer Retry recovery: Chromium 1.908 s, WebKit
  0.879 s in this environment. Intentional model/module faults recover separately.
- Three.js chunk 706.48 kB (184.46 kB gzip estimate), pose JSON 477.37 kB
  (101.45 kB gzip estimate), GLB 1.012 MB. All are Practice-only; Vite's large lazy
  chunk warning is retained rather than hidden.

Linux software graphics and WebKit are not native iPad performance/Safari
evidence. No physical-iPad pass, native GPU-memory figure, FPS guarantee or full
WCAG certification is claimed.

## Preservation and hand review

[197 protected application/config/assets](tests/reports/source-protection.json)
are byte-identical to `b21bd6a`; the expanded legacy-failure investigation also
matches 368 protected source, asset, script and snapshot hashes. Product IDs,
prices, specifications, image rights and the original site were not edited.

The [pose library audit](tests/reports/pose-library-integrity.json) confirms 42
different sets of actual bone rotations **excluding root transforms**. Both
browser engines also measure actual applied rig fingerprints. Distinct poses
are not evidence of correct human contact or anatomy.

C has zero audited hand/sleeve/guitar intersections and correct contact
clearances, but remains needs-review after four-view visual inspection. Other
41 candidates have 255–755 skin crossings each. No unapproved hand is visible in
the normal lesson. See [screenshots](SCREENSHOTS.md) and the
[42-row status table](CHORD-STATUS-42.md).

Interim timeout/harness failures are retained with an archive manifest; they are
not relabelled passing. Canonical reruns use the corrected fault-injection
harness, unchanged final production assets and explicit real-click retries.
