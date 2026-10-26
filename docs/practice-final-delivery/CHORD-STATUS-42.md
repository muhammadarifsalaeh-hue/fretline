# All 42 delivery statuses

Runtime poses and their exact-mesh evidence are byte-bound to the unchanged library `2e2816f7adf533f80fba931e4d73b592a670a614ea014406903da162b5f01aa1`. The final shared solver attempted 35 replacements, rejected all 35 under the original exact gate and preserved 7. No geometry threshold or musical definition changed. The browser inspector was separately checked across all 42 in both engines.

| Chord | Voicing E–A–D–G–B–e | Diagram / neck | Hand geometry | Prototype inspection | Natural teaching hand |
|---|---|---|---|---|---|
| C | `x32010` | Available | Pass | Explicit warning required | Not approved |
| D | `xx0232` | Available | Rejected | Blocked; diagram fallback | Not approved |
| E | `022100` | Available | Rejected | Blocked; diagram fallback | Not approved |
| F | `133211` | Available | Rejected | Blocked; diagram fallback | Not approved |
| G | `320003` | Available | Rejected | Blocked; diagram fallback | Not approved |
| A | `x02220` | Available | Rejected | Blocked; diagram fallback | Not approved |
| B | `x24442` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Cm | `x35543` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Dm | `xx0231` | Available | Pass | Explicit warning required | Not approved |
| Em | `022000` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Fm | `133111` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Gm | `355333` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Am | `x02210` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Bm | `x24432` | Available | Rejected | Blocked; diagram fallback | Not approved |
| C7 | `x32310` | Available | Rejected | Blocked; diagram fallback | Not approved |
| D7 | `xx0212` | Available | Rejected | Blocked; diagram fallback | Not approved |
| E7 | `020100` | Available | Pass | Explicit warning required | Not approved |
| F7 | `131211` | Available | Rejected | Blocked; diagram fallback | Not approved |
| G7 | `320001` | Available | Rejected | Blocked; diagram fallback | Not approved |
| A7 | `x02020` | Available | Rejected | Blocked; diagram fallback | Not approved |
| B7 | `x21202` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Cmaj7 | `x32000` | Available | Pass | Explicit warning required | Not approved |
| Dmaj7 | `xx0222` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Emaj7 | `021100` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Fmaj7 | `xx3210` | Available | Pass | Explicit warning required | Not approved |
| Gmaj7 | `320002` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Amaj7 | `x02120` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Bmaj7 | `x24342` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Cm7 | `x35343` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Dm7 | `xx0211` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Em7 | `020000` | Available | Pass | Explicit warning required | Not approved |
| Fm7 | `131111` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Gm7 | `353333` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Am7 | `x02010` | Available | Pass | Explicit warning required | Not approved |
| Bm7 | `x24232` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Csus2 | `x35533` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Dsus2 | `xx0230` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Asus2 | `x02200` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Csus4 | `x33011` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Dsus4 | `xx0233` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Esus4 | `022200` | Available | Rejected | Blocked; diagram fallback | Not approved |
| Asus4 | `x02230` | Available | Rejected | Blocked; diagram fallback | Not approved |

Geometry reuses the existing full runtime audit because the GLB, weights and all 42 saved transforms are unchanged. It is not described as a newly rerun runtime-mesh audit. The 35 **new central candidates** were actually fitted and exactly audited in [the final solver batch](solver/final-batch-v2/exact-audit/summary.json), with zero accepted replacements. Original unrun later stages for self-rejected runtime poses remain unrun, never counted as passes. See [the full runtime measurements](../practice-hand-batch-3/geometry/summary.json).
