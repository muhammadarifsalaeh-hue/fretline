# Guitar Practice: Stage 1–2

An isolated chord-trainer feature. It does not use or mutate the 200-model
catalog, ShopContext, guitar IDs, Compare, Quiz or Wishlist state.

- `data/chords.js`: immutable C, G, D, Em and Am open voicings. Six-value arrays
  run **low E/string 6 → high E/string 1**. `null` = mute, `0` = open.
- `data/fretboard.js`: generic 648mm study scale, twelve equal-tempered frets,
  standard tuning and string coordinates. These are not product specifications.
- `components/ChordDiagram.jsx`: SVG drawn from the same chord object as the 3D
  markers. Six vertical strings and nut plus five horizontal fret boundaries.
- `components/GuitarNeckViewer.jsx`: loading/error/retry lifecycle and accessible
  camera controls. No WebGL engine is imported until Practice mounts.
- `loadScene.js`: isolated module loading and WebKit failed-import recovery.
- `scene/createNeckScene.js`: actual Three.js WebGL2 geometry, OrbitControls,
  render-on-demand, marker updates, resize and resource cleanup.
- `src/pages/PracticePage.jsx`: scoped premium page composition and chord state.

## Model coordinates

Dimensions are millimetres in the data helpers, with 40mm per world unit in the
scene. +X runs nut → body, +Y points out of the fingerboard, and low E has +Z.
Fret wire distance from the nut is `L × (1 − 2^(−n/12))`. The twelfth wire is
half the speaking length. Numbered markers are schematic mid-fret targets,
not physical fingers or an anatomical teaching pose.

## Future human hand integration — deliberately not implemented

Each chord reserves `handPose: null`; no placeholder model pretends to be a hand.
A future approved stage should attach a separately licensed rig/asset to the
scene and define its bone names, rest pose, scale, handedness and joint limits.
Its adapter must map real string/fret targets into the coordinate convention
above and validate fingers/occlusion, rather than deriving an anatomical pose
by treating the current schematic sprites as joints. The scene's `setChord`
entry is the integration point; it must retain one chord selection state.

Do not add song, scale or free-play modes, audio controls, a lesson sequencer or
unimplemented buttons in Stage 1–2. Further work requires the user's review.

## Graphics lifecycle and dependencies

Only one new application dependency: **Three.js 0.186.1 (MIT)**. Procedural wood
grain, meshes and sprites are code-generated study graphics, not catalog photos.
The distributed MIT notice is `public/licenses/three-MIT.txt`.

The Practice page and scene load lazily. `vite.config.js` keeps Three.js out of
the shared React vendor bundle. Frames are requested only after input, resize,
chord changes or document visibility changes; there is no idle animation loop.
Pixel ratio is capped at 1.75. Controls do not auto-rotate or animate the camera.

Unmount/retry disposes geometries, materials, textures, OrbitControls, listeners,
ResizeObserver, renderer and context. Context loss and unavailable WebGL2 show
real recovery UI while the chord diagram stays usable. A rejected module import
uses a fresh URL for the emitted, self-contained engine/scene chunk; WebKit can
cache failed imports even across document reloads. A successful factory is reused
for context recovery, and its retry revision is remembered for the current
session/build when sessionStorage is available. No guitar or Wishlist storage
is changed. The small Vite URL plugin avoids duplicate scene implementations or
unbundled runtime imports, and does not load Three.js on existing pages.

Keyboard: focus the canvas, arrows rotate, `+`/`=` and `-` zoom, `0`/Home resets;
Tab leaves the canvas normally. Touch: one finger rotates and two-finger pinch
zooms. Page scrolling remains available outside the canvas.

Run `npm run practice:check` for independent fret/triad/fingering checks.
Browser evidence and device limitations are in `docs/practice-stage1-2`.
