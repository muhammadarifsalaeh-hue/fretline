# Fmaj7 actual-surface contact repair

This is a geometric candidate, not an approved teaching hand. It retains
`needs-review`, `reviewed: false`, and false independent teaching review gates.
Musical voicing `xx3210`, fingers, model, skin weights and topology are unchanged.

The initial bounded Fmaj7 candidate had zero combined skin/cloth crossings and
zero wood interior samples, but its ring fingertip penetrated physical string D.
The unchanged external gate found 32 actual guitar crossing pairs and a
−0.33 mm ring/string clearance. That rejected evidence remains in `audit/`.

`fmaj7-contact-refine.py` keeps the actual saved root, wrist, thumb and all other
digits unchanged. It lifts the ring's lower flesh surface, then fits the real
ring skin triangles to the **exported runtime D string** using four bounded
local joint parameters. The largest change is below 0.48 degrees. No fingertip,
string or fret target was moved, no finger was hidden, and no mesh was stretched.

## Actual acceptance result

- Combined skin/sleeve self crossing pairs: **0**.
- Actual guitar triangle crossing pairs: **0**.
- Dense wood interior samples (>0.02 mm): **0 of 72,878**.
- Correct-owner palmar contact: ring D3 **0.014258 mm**, middle G2
  **0.017861 mm**, index B1 **0.028868 mm**.
- Open high-e whole-skin clearance: **1.834764 mm**.
- All unchanged geometric gates passed; anatomical and multi-view teaching
  approval are still pending.

Seed SHA-256: `232cbd21978fdb09a1f71476b0f80454726b16c22960a45a1754c8c904029b32`.
Refined file SHA-256: `a5bd94b7d93fe3a273a1f878e0676061568cd27494ace5d7fa01f71b1c3d1882`.
Transform SHA-256: `7e0af3009f1f3d9295a9ed60fbc84ef2c5f0d7575629ab7c9c607a47f912db57`.
Model SHA-256: `23fdb5745e9343b597eb816bcdfcb266c1942ebbbb495cdb3776214343d7f3bc`.
Chord source SHA-256: `622250c559fde01633e629f7c514a5c1fbdc7d3d35bdc078079a6ece5bbfc796`.

## Reproduce

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/batches/fmaj7-contact-refine.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/check-hand-geometry.py --library docs/practice-hand-batch-3/Fmaj7/refined-library.json --chords Fmaj7 --require Fmaj7 --output docs/practice-hand-batch-3/Fmaj7/refined-audit
```

The accompanying F barre trial was rejected: 371 combined self-crossing pairs and
782 interior wood samples. It must not replace the runtime F hand or be labelled
verified. A true index barre needs a separate authored contact/deformation solve.
The Fmaj7 success does **not** certify F or any other chord.
