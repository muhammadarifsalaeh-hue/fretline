# Dm real-surface contact repair — geometric pass

This experiment derives the unchanged `xx0231` fingering from the actual audited
Fmaj7 seed: middle G2, root/wrist, thumb and unused little remain fixed; index
moves B1→e1 and ring D3→B3. Real skin-based bounded IK and physical string contact
refinement are recorded in `scripts/practice/batches/dm-contact-fit.py`.

Two initial bounded trials plus one targeted contact repair were performed.
No runtime pose or chord data was changed by these scripts. All candidates retain `needs-review` with all independent teaching gates false.

| Trial | Combined self | Wood interior | Guitar crossings | Correct-owner contact |
|---|---:|---:|---:|---|
| Initial `candidate.json` | 0 | 0 | 112 | Ring/index string penetration; rejected |
| Second `refined.json` | 0 | 0 | 22 | Ring/middle pass; index 0.131127 mm > unchanged 0.12 mm limit |
| Surgical `surgical.json` | 0 | 0 | 0 | All three assigned distal palmar contacts pass |

The second trial physical open D-string clearance is 2.079518 mm. Positive whole-string
clearance does not override actual remaining guitar triangle crossings or the
correct-owner palmar contact failure. **These first two candidates did not pass; neither is approved for teaching.** Exact rejected evidence is in `audit/` and
`refined-audit/`; the second trial transform hash is
`d7a00b305aac9426dd645838a5593828c6f736bc19c39240d7d8801e3e7ed444`.

## One surgical follow-up after locating the exact rejection

The root reviewer mapped all 22 remaining actual guitar crossing pairs to
**fret-3 metal**, rather than the string or wood. One bounded follow-up moved the
ring flesh contact 2 mm toward the nut within the unchanged legal contact region
(`wire−6` through `wire−1.1`), and refined the index against the exact same
correct-owner distal palmar triangles used by the gate. The gate and its
thresholds were not changed.

The final `surgical.json` result passes all unchanged geometric tests:

- Combined skin/sleeve crossings: **0**.
- Actual guitar triangle crossings: **0**.
- Dense wood interior samples: **0**.
- Correct-owner contacts: index e1 **0.060017 mm**, middle G2
  **0.017861 mm**, ring B3 **0.010000 mm**.
- Open D whole-skin clearance: **2.079518 mm**.

Root/wrist/thumb/middle/little and source mesh/weights are unchanged. Both
rejected trials above remain historical evidence; they are not relabelled pass.
`Dm` remains **needs-review**, not anatomically approved for teaching.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/batches/dm-surgical-refine.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/check-hand-geometry.py --library docs/practice-hand-batch-3/Dm/surgical-library.json --chords Dm --require Dm --output docs/practice-hand-batch-3/Dm/surgical-audit
```


Final transform SHA-256: `56ff33568eee61559066f036872b086a5a5531a6646aa022e25291449c3fe4db`.
Final file SHA-256: `99ceb12462e2a9f2809f98f49a940471810aecfcbb4e347db8c4ae8894bd8fe1`.
