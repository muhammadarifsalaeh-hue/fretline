# Final delivery acceptance

Run only after the application source and production assets are frozen. The
runner refuses to overwrite an existing report folder, records the entire
production snapshot, and checks the frozen pose-library hash before and after
the actual browser runs.

```sh
python docs/practice-final-delivery/tests/run-final-qa.py \
  --url http://127.0.0.1:5430 \
  --freeze-sha CURRENT_RUNTIME_LIBRARY_SHA256 \
  --output docs/practice-final-delivery/tests/reports/final
```

Use `--changed-chords` only for **integrated** pose changes. Unaccepted authoring
candidates do not receive extra runtime captures or become passing poses. When
the library is unchanged, the canonical C captures and the new camera/gate
captures provide the current default/player visual evidence without recapturing
all old candidate poses.

The complete serial plan requires:

- Chromium: the existing 21-case trainer plan.
- Linux WebKit: the same 21-case plan.
- The unchanged 107 original site/gallery/camera regression checks.
- Both-engine seven-preset and rotate/zoom/reset control checks.
- Both-engine **all 42** inspection-gate checks against the actual source
  root/bone transforms. Every allowed pose is explicitly shown with a warning
  and must change real WebGL pixels; every rejected pose must have no inspection
  control, keep its hand hidden and retain its correct diagram/open strings.
- Six C default/player captures per engine: desktop, tablet and mobile. The
  actual camera must face the fingerboard; low E projects above high e and the
  headstock remains right/up. These assertions catch the old rear-wood player
  direction instead of accepting any camera movement as a good view.
- Normal/reduced-motion appearance reveal, cancellation and disposal checks.
- Any integrated changed-pose four-view captures requested by the command.

The owned adapter preserves the original suite source. It retains the original
800 ms idle no-render assertion and the previously justified startup-settlement
wait. It also **strengthens** the former F prototype-inspection branch: a known
geometry-rejected F must now use a checked SVG diagram and a drawn neck without
revealing its incorrect hand. C's allowed inspection retains real-pixel and
four-camera assertions. The reports record both adaptations explicitly; these
are not described as an unchanged historical test invocation.

No browser result approves hand anatomy, string pressure, a swept physical bone
animation path, or physical iPad Safari. Linux WebKit is an engine test on this
Linux machine, not an iPad/iPadOS/GPU performance certification.

## Runtime restoration after environment restart

System Chromium, Python Playwright and Pillow were already installed. Temporary
WebKit revision 2336 and its missing Debian 13 libraries were restored under
`/tmp` only; no application dependency or system package installation changed.
The Debian package files were checked against the SHA-256 values from the HTTPS
Debian package index before extraction. The bundled WebKit wrapper replaces
`LD_LIBRARY_PATH`, so temporary missing-library symlinks are placed in that
browser's own temporary `sys/lib` folder. The downloaded browser binaries are
unchanged. A real launch and a data-page rendering smoke check succeeded before
the Fretline test plan was started.

The initial `apt-get download` lookup lacked package lists and was replaced by
direct verified Debian-index downloads. An initial browser launch correctly
failed for missing loader libraries; it is setup evidence, not an application
test result. `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1` bypasses only the
system-wide dependency detector, which cannot see these temporary bundle-local
libraries. Actual browser launch and the application suites must still pass.

Use the supported proxy/network-enabled execution context for the preview and
browser commands. A restricted command's isolated localhost does not reach a
preview server started outside that network namespace. Do not change proxy or
TLS verification settings.
