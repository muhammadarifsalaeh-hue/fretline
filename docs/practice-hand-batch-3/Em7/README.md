# Em7 candidate — bounded real-skin solve

- Musical voicing remains `020000`: middle finger presses string 5 / A, fret 2;
  strings 6, 4, 3, 2 and 1 are open. No chord source was edited.
- Seed is the exact Am7 record from `74c2076`, saved in
  `seed-Am7-runtime.json`, so reproduction does not depend on a later modified
  runtime library.
- The unused index was released to PIP/DIP deltas 45°/25°. The middle chain was
  fitted against actual palmar flesh and refined against the real string tube.
  Root, wrist, thumb and the relaxed ring/little chains remain the audited seed.
- Repeating the command below produced **0.0 maximum root/bone coordinate
  difference** from this candidate.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/batches/em-am-fit.py \
  Em7 --seed docs/practice-hand-batch-3/Em7/seed-Am7-runtime.json \
  --output /tmp/Em7-reproduced.json --iterations 70
```

The unchanged exact geometry audit passes: combined skin/sleeve self-crossing
pairs **0**, guitar triangle crossings **0**, dense wood-interior samples **0**,
correct-owner palmar contact gap approximately **0.008 mm**. All five open
strings have at least **0.557 mm** whole-skin clearance.

This is a geometric prototype. It remains `needs-review`, `reviewed:false`, with
no anatomical or teaching approval. The finite cropped sleeve/source-arm and
natural presentation limitations remain. Root integration must retain the
normal inspection warning and teaching gate.
