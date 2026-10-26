# E7 candidate — single-chain extension of audited Em7

Original voicing `020100` and original assignments are preserved: middle finger
A2 and index finger G1; low E, D, B and high e are open. Only the index local
chain changes from `../Em7/candidate.json`. The actual middle distal flesh
coordinates remain **exactly unchanged (0.0 mm maximum delta)**.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/batches/e7-fit.py \
  E7 --seed docs/practice-hand-batch-3/Em7/candidate.json \
  --output /tmp/E7-reproduced.json --iterations 60
```

The unchanged exact geometry audit passes: combined self **0**, actual guitar
triangle crossings **0**, dense wood-interior samples **0**, both correct-owner
palmar gaps approximately **0.008 mm**, all four open strings at least
**0.557 mm** clear. Model/weights, musical source and scale remain unchanged.

The pose is `needs-review`, not a verified teaching example. Passing this
mechanical rejection gate does not approve natural joint comfort, source arm
presentation or real iPad performance.
