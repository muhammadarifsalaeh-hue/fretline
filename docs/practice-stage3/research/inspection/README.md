# Failed Stage 3 feasibility inspector

This is an isolated diagnostic, not a live Fretline feature and not a valid chord lesson. It deliberately shows the rejected experimental C pose so that contact failures can be reviewed from multiple angles. No source catalog data or application route is imported.

The real rigged GLB hand and original modeled study neck share one Three.js scene. Front, side, player and context cameras, OrbitControls drag/wheel/pinch and camera reset are functional. Frames render on demand. The skin height texture is assigned to `bumpMap` rather than the source file's incorrect tangent normal binding. No 2D hand or photograph overlay is used.

Expected file layout (serve the assets root, not this subdirectory):

- `inspection/index.html`, `inspection/viewer.js`
- `buildStudyGuitar.mjs`
- `c-major-runtime-pose.json`
- `anatomical-hand-optimized.glb`
- `node_modules/three` accessible under `/node_modules/three`

The current temporary setup serves `/tmp/fretline-stage3-assets` at `http://localhost:8766/inspection/`. The root contains a symlink to the existing project's node_modules; no new dependency is installed. When preserving the research directory inside a repository, use a static server rooted at the repository or adjust the import map to point at the existing installed Three package. Do not add this failed pose to `/practice`.

Capture scripts use external Python Playwright, not app dependencies. Real Chromium and Linux WebKit screenshots are `failed-contact-{front,side,player,context}.png` and `webkit-failed-contact-{front,side,player,context}.png`. Linux WebKit coverage is not physical Safari/iPad testing. No FPS, GPU memory or iPad thermal benchmark was performed.

`runtime-proof.json` and `webkit-runtime-proof.json` record actual bone positions and scene counts. `runtime-transfer-validation.json` compares all actual Three.js skinned vertices against the independently transferred runtime pose: Hand3148 vertices, maximum position difference0.0000111mm; Nails204 vertices, maximum difference below1e-12mm. This validates transfer only; it does not validate playable technique or collision freedom.

Hand copyright ©2026 Emma L. D. Lieker. Source: https://github.com/emmalieker/anatomical-hand-model at f27f19f55f8270b3108ea0b53ce5aa81c543ff7c. License: CC BY-NC4.0, https://creativecommons.org/licenses/by-nc/4.0/. Modifications: left-hand reflection, experimental joint pose, optimized textures, constant nail-map removal, corrected skin height binding. Noncommercial educational research only under this license. Include the creator license and modification notice with any preserved copy.
