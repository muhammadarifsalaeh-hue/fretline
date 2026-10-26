# Fretline — final 3D demo handoff

Baseline: `96e0449`, branch `feature/guitar-practice-3d`. No master merge.
This delivery closes 3D implementation for the current deadline. Product data,
Quiz, Compare, Wishlist, Catalog, Homepage and brands remain unchanged.

## What is usable

| Scope | Count | Meaning |
|---|---:|---|
| Correct diagrams, instructions and interactive neck positions | 42/42 | The standard-tuning musical data and diagrams remain verified |
| Geometrically accepted hand endpoints | 7/42 | C, Cmaj7, Am7, Em7, E7, Fmaj7, Dm; explicit warned inspection only |
| Anatomically approved realistic teaching hands | **0/42** | No unapproved pose is presented as a correct human-hand lesson |
| Rejected runtime hands blocked from inspection | 35/42 | Diagram and gold markers remain; no known colliding hand can be revealed |

Among the eight requested basic shapes, C and Dm pass geometry. G, D, Em, Am,
full-barre F and E still use the diagram/neck fallback. Fmaj7 is not F; E7 is
not E. All eight have working correct diagrams, but none has final natural-hand
teaching approval.

## The shared cause and changes

The existing source rig has 22 real bones, normalized original skin weights and
proper handedness/flex-axis signs. The review did not establish global weight
or mirrored-axis corruption. Arbitrarily rewriting those weights would risk
otherwise valid poses.

The old objective aimed for fingertip targets without sufficiently constraining
palm placement, neighboring skin and open-string obstruction. It also froze
formerly fretted seed fingers when those fingers became unused in a new chord.
A finger could therefore remain on an open string even though the new chord
had no assignment for it.

The new **single offline solver** handles all 42 central definitions, selecting
audited seeds by fingering topology. It adds a shared MCP/palm placement prior,
bounded distributed flexion and side approach, actual palmar skin contact,
legal contact staggering, signed neighboring/string barriers and a generic
unused-digit release policy. Only formerly fretted or actually obstructing
unused fingers are released, with tight bounds/strong priors. Clear unused
fingers remain fixed. The iPad loads saved poses; the expensive offline solve
is not placed in the browser.

One completed common batch processed all 42: **7 preserved + 35 fitted and
exactly audited**. No new candidate passed every unchanged physical criterion.
All 35 replacements were rejected, including 16 with zero self crossings but
remaining guitar/contact/open-string defects. No accepted endpoint was lost,
no chord was altered and no threshold was relaxed. See
[solver closeout](solver/CLOSEOUT.json), [solver evidence](solver/README.md), and
[rig/guard review](review/GUARD-AND-RIG-REVIEW.md).

## The final runtime

- Known rejected/unaudited hand meshes cannot be revealed, including through
  the engine's inspection API. Complete hidden poses remain available for
  source-to-rendered diagnostics. Only explicit boolean contact/collision passes
  enable prototype inspection; teaching still requires all four review gates.
- Selection closes the previous inspection and synchronizes the rig in a layout
  effect before UI paint. A rejected chord keeps its correct SVG diagram and
  open-string/gold-marker neck view.
- The existing player camera now looks from the fingerboard side. Its former
  negative-Y direction showed rear wood and obscured the fingering. The default
  angle, low-E-above-high-e order, headstock direction and guitar coordinates
  remain unchanged. Rotate, zoom and Reset are retained.
- Three.js/model loading remains Practice-only; no dependency, model triangle
  count, texture size, song mode or other feature is added.

## Honest limits

This is a usable diagram/neck demo with seven reviewable geometric hand
prototypes, not a completed realistic 42-hand trainer. The palm/proximal curl,
thumb support, finite cropped arm/sleeve and skin presentation still require
anatomical/model authoring. The GLB uses core metallic/roughness materials; the
Blender source's subsurface settings are not exported as a skin shader. A build
or target fit cannot fix or certify these issues.

The existing bounded opacity reveal is not physical bone interpolation between
chords. No swept trajectory has been certified. No physical iPad Safari was
available: Linux WebKit/synthetic touch/software graphics do not establish iPad
GPU FPS, memory behavior or native Safari approval.

## Validation and images

Fresh results are recorded in [TEST-RESULTS.md](TEST-RESULTS.md), with an honest
initial harness preparation failure and the targeted trainer retry retained.
The accepted summary binds every completed suite to the same production bytes.
[SCREENSHOTS.md](SCREENSHOTS.md) links actual desktop/tablet/mobile renders and
corrected default/player views. [Preservation evidence](preservation.json)
records 197 unchanged site files and unchanged musical/model sources.

## Open the final feature on iPad

Use the existing Fretline Codespace. Stop an already-running Vite server with
**Ctrl+C**, save local changes without discarding them, then run:

```sh
git fetch origin
git switch feature/guitar-practice-3d
git pull --ff-only origin feature/guitar-practice-3d
git log -1 --oneline
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

Choose **Ports → 5173 → Open in Browser**. Append `/practice` to the HTTPS URL
in Safari's address bar. C or Dm offers **ตรวจต้นแบบมือ** with a warning; F/G/D/
Em/Am/E use diagrams and markers. The route is not a terminal command.

Test portrait/landscape, drag/pinch, player/default/Reset, quick chord changes,
Back/Forward, reduced motion and repeated Practice→Catalog/Compare/Quiz visits.
Record the physical iPad model/iPadOS version and any reload/stall before a
future merge decision. This delivery does not merge master or start product
curation; the preserved 200-model database is ready for that separate work.
