# Actual runtime hand candidate rejection audit

Actual root and local bone quaternions reconstructed through exported GLB skin weights. Skin-only triangle crossings include coplanar interior overlaps. Wood/open-string rejection uses actual skin and garment vertices, triangle centroids and edge midpoints against conservative analytical solids. Sampling is not proof of absence of collisions. This report never certifies a pose.

The snapshots below are immutable inputs for this audit; later C refinements must be assessed against their own transform hash. No runtime status or approval gate was changed.

| Chord | Skin crossing pairs | Wood samples >0.25 mm | Smallest open-string sampled clearance (mm) | Status at snapshot |
|---|---:|---:|---:|---|
| C | 0 | 0 | 0.173 | needs-review |
| D | 355 | 26 | 3.325 | needs-review |
| E | 722 | 0 | 2.047 | needs-review |
| F | 516 | 218 | — | needs-review |
| G | 349 | 0 | 2.882 | needs-review |
| A | 453 | 19 | 1.588 | needs-review |
| B | 284 | 414 | — | needs-review |
| Cm | 458 | 283 | — | needs-review |
| Dm | 363 | 0 | 2.701 | needs-review |
| Em | 528 | 0 | 1.678 | needs-review |
| Fm | 416 | 222 | — | needs-review |
| Gm | 502 | 235 | — | needs-review |
| Am | 741 | 0 | 2.122 | needs-review |
| Bm | 395 | 249 | — | needs-review |
| C7 | 308 | 0 | 1.435 | needs-review |
| D7 | 600 | 0 | 3.171 | needs-review |
| E7 | 562 | 0 | 0.550 | needs-review |
| F7 | 322 | 165 | — | needs-review |
| G7 | 327 | 10 | 1.977 | needs-review |
| A7 | 448 | 0 | 0.086 | needs-review |
| B7 | 255 | 4 | 2.987 | needs-review |
| Cmaj7 | 377 | 0 | 1.429 | needs-review |
| Dmaj7 | 522 | 25 | -0.285 | needs-review |
| Emaj7 | 755 | 0 | 0.988 | needs-review |
| Fmaj7 | 363 | 0 | 1.617 | needs-review |
| Gmaj7 | 358 | 7 | 1.451 | needs-review |
| Amaj7 | 597 | 0 | 1.792 | needs-review |
| Bmaj7 | 428 | 198 | — | needs-review |
| Cm7 | 321 | 176 | — | needs-review |
| Dm7 | 598 | 446 | -0.117 | needs-review |
| Em7 | 481 | 0 | 0.842 | needs-review |
| Fm7 | 509 | 84 | — | needs-review |
| Gm7 | 625 | 71 | — | needs-review |
| Am7 | 585 | 0 | 0.714 | needs-review |
| Bm7 | 351 | 165 | — | needs-review |
| Csus2 | 482 | 338 | — | needs-review |
| Dsus2 | 478 | 0 | 0.911 | needs-review |
| Asus2 | 528 | 0 | 1.862 | needs-review |
| Csus4 | 443 | 337 | -0.098 | needs-review |
| Dsus4 | 313 | 3 | 2.739 | needs-review |
| Esus4 | 439 | 39 | 1.354 | needs-review |
| Asus4 | 561 | 0 | 1.615 | needs-review |

42 actual poses audited; 42 distinct transform fingerprints; 41 have skin crossing/overlap rejections.

Raw triangle indices, bone categories and crossing locations are retained in the gzip reports. See `summary.json` for complete contact reconstruction, per-mesh and per-open-string measurements, source hashes and limitations.
