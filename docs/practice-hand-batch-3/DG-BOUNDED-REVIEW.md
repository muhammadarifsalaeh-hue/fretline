# Bounded D / G / Dsus2 authoring experiments

These are **rejected authoring candidates**, not additional accepted teaching
poses. No runtime pose library, chord voicing, finger assignment, guitar string,
model, skin weight, or acceptance threshold was changed by these experiments.
The existing exact geometric checker remains authoritative.

## Controlled changes

The initial batch-3 candidates used fixed audited C thumb/little rotations and
bounded root/index/middle/ring IK with actual skin barycentric contact anchors.
Unsigned sampled proximity did not prevent crossing fingers. The new runs add
nearest-surface normal signs to the sampled separate-digit penalty. This is an
optimizer prior, not a mathematical proof of mesh separation.

The last D/G refinement additionally uses every skin vertex for the wood
residual and a stronger distributed PIP/DIP-curl prior. Dsus2 changes only its
required index and ring chains while relaxing the unused middle. Musical data
remain `D xx0232`, `G 320003`, and `Dsus2 xx0230` from the central chord module.

## Actual results

| Candidate | Combined skin/sleeve self crossings | Other rejection evidence |
|---|---:|---|
| D initial bounded-1 | 408 | 143 dense wood samples inside |
| D signed-2 | 25 | 340 wood samples; maximum 1.414 mm; remaining crossings are middle PIP/DIP local folding |
| D signed-3 | 0 | 54 wood samples; maximum 0.343 mm; 174 actual guitar crossings; ring contact 1.545 mm away, middle 0.407 mm away; index intersects its string |
| G initial bounded-1 | 242 | 167 wood samples inside |
| G signed-2 | 0 | 6 dense wood samples, maximum 0.324 mm; 138 guitar crossings; all three assigned fingers penetrate; open D clearance 0.172 mm fails the unchanged 0.2 mm criterion |
| D owned-contact trial 1 | 0 | 106 dense wood samples, maximum 0.963 mm; 200 guitar crossings; middle contact 0.012 mm passes but index penetrates and ring gap 0.624 mm fails |
| G owned-contact trial 1 | 0 | 422 dense wood samples, maximum 1.505 mm; 166 guitar crossings; 1.5 mm root lift shifts thumb/metacarpal into the rear wood solid despite all three assigned contacts near 0.012 mm; whole-skin A-string clearance also remains -0.455 mm |
| Dsus2 signed-1 | 0 | 219 wood samples; maximum 1.597 mm; 226 guitar crossings; open high-e intersects skin |
| Dsus2 contact-lift-2 | 0 | 1 dense wood sample 0.074 mm deep; 58 guitar crossings; index contacts adjacent B, ring touches open high-e; assigned palmar contact gaps 0.340 / 0.186 mm fail |

For the Dsus2 contact refinement, a 2 mm root lift first removes fingertip wood
penetration at vertices. Constrained per-chain actual triangle/string distance
then reaches 0.014 / 0.012 mm to *some* part of those fingers. The stricter final
checker correctly rejects it: the original palmar owned surface in the required
fret zone does not make the assigned contact and adjacent strings still
intersect other surfaces. This illustrates why a whole-finger minimum distance
or bone-end target alone cannot establish a correct fretboard pose.

The final D and G local refinements used actual assigned-owner palmar triangles inside the legal fret region, plus every actual runtime string path, with at most 3 degrees change per degree of freedom. D's middle contact improved but the other contacts did not pass. G's assigned contacts all passed, but the 1.5 mm root lift moved the previously fixed thumb and metacarpal into the rear of the neck. Whole-skin A-string clearance also remains -0.455 mm even though its assigned owner's contact passes. This rejects the whole pose: fitting each assigned contact alone is insufficient when another surface touches that string or root movement affects the thumb. No further fits were attempted after these bounded trials. Refining pad-side
orientation, actual owned palmar correspondence and the thumb/root together is
still necessary; repeating the point-fit without those constraints is not
productive. Any future candidate must retain the unchanged final exact checks
and independent anatomical/multi-view approval.

## Reproduction

Use Python NumPy/SciPy authoring tools with single-thread BLAS. No browser
runtime dependency was added.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/batches/d-g-fit.py D --signed --evaluations 50 --label bounded-signed-2
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/batches/d-g-signed-refine.py D --signed --evaluations 65 --label bounded-signed-3 --seed docs/practice-hand-batch-3/D/bounded-signed-2.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/batches/d-g-signed-refine.py G --signed --evaluations 65 --label bounded-signed-2
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/batches/d-suspended-fit.py Dsus2 --signed --evaluations 65 --label bounded-signed-1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/batches/d-suspended-contact.py --lift 2
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/batches/d-owned-contact-refine.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/batches/g-owned-contact-refine.py
```

For each candidate, substitute **only that candidate** into a temporary copy of
the original library and invoke `scripts/practice/check-hand-geometry.py` with
`--chords D` (or `G`, `Dsus2`) and `--require` set to that ID to demand acceptance.
The saved reject reports were generated with `--require ''`: process success
means the audit ran without mislabelling rejected candidates as verified, while
`geometricPassed` is still **false**. Actual local TRS, hashes, raw crossing pairs
and per-string/contact results are retained in each audit directory.

The source GLB remains SHA-256
`23fdb5745e9343b597eb816bcdfcb266c1942ebbbb495cdb3776214343d7f3bc`;
central chord source remains
`622250c559fde01633e629f7c514a5c1fbdc7d3d35bdc078079a6ece5bbfc796`.
These experiments certify no natural teaching pose or physical iPad performance.
