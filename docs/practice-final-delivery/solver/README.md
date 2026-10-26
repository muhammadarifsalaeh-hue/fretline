# Central hand solver closeout

This is one offline actual-skin authoring pipeline for the immutable 42-chord
library. It does not run collision optimization on an iPad, edit product data,
or automatically publish numerical candidates as teaching examples.

## Common cause and correction

The earlier generator fit fingertip locations without a sufficient neighboring
skin barrier or stable palm frame. In addition, its pending replacement retained
formerly fretted seed digits when those digits became unused. That could mute
a newly open string even if every active fingertip reached its target.

The final common solver now:

- Selects a seed from the existing mesh-audited endpoints using actual
  string/fret/finger topology. Known passing endpoints are preserved by default.
- Uses the original GLB rest transforms, skin weights and named local bone
  rotations; no finger is replaced with a primitive or a static image.
- Solves root/palm placement, active chains and thumb together, with coupled
  curl priors and actual owned palmar triangle correspondences.
- Automatically staggers contacts inside the **unchanged** original legal
  contact region. Barre strings share one contact-X variable and one actual
  index chain instead of six unrelated fingertip points.
- Gives bounded, strongly regularized release controls only to unused digits
  that were fretted in the seed or actually obstruct an open string. Other
  unused chains stay fixed; this avoids the old unrestricted unused-digit folds.
- Uses signed neighboring-surface and string-side penalties, sampled wood and
  fret-crown barriers. These sampled fitting priors are **not** an acceptance
  proof. The original exact geometry checker remains authoritative.

The actual regression examples are Dsus2 from Dm (release the former middle G2
contact) and Em7 from C (release index/ring; the old index intersects the newly
open B string). Clear unused little-finger geometry remains fixed.

## Acceptance and evidence

The selector binds the actual proposal bytes, model, musical source and each
saved root/bone transform to a completed exact audit. Missing/duplicate rows,
missing/wrong owner contacts, actual wood/guitar/self collisions, malformed
string states and stale source hashes cannot be promoted. The original
0.12 mm palmar-contact, 0.2 mm open-string and other geometric thresholds remain
unchanged. Passing a numerical objective never sets anatomical approval.

Every selected new endpoint is forced to `needs-review`, `reviewed: false`,
`anatomyPassed: false` and `multiViewReviewed: false`. Rejected candidates leave
the prior runtime record intact. No script in this folder writes runtime data.

- `math-check.txt`: actual math, source-rig, owned-skin, all-42 topology and
  unused-digit release regressions: **9/9 passed**.
- `selection-check.txt`: actual passing/rejected source fixtures, stale evidence,
  unchanged threshold, false approval and CLI guards: **14/14 passed**.
- The earlier bounded C/Em/Am proof is retained in this folder. Em and Am were
  rejected (37 and 31 combined self crossings respectively).
- `final-batch/` is explicitly interrupted after a saved checkpoint when the
  unused-digit omission was identified. It has no completed exact audit and is
  not counted as a successful 42-pose run.
- `final-batch-v2/` is the one complete final generic batch after that correction;
  its manifest and exact audit contain the actual result, not inferred success
  from an optimizer cost or budget exhaustion.

## Reproduce without overwriting evidence

Use a fresh output directory. NumPy/SciPy are offline tools already used by the
project; they are not added browser dependencies.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/final_solver/test_math.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/final_solver/test_selection.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/practice/final_solver/solve.py --chords all --max-evaluations 12 --audit --output /tmp/fretline-central-new-run
```

The batch order prioritizes C, G, D, Em, Am, F, E and Dm. It preserves the seven
existing geometric endpoints instead of replacing them with an unaudited
attempt. The maximum evaluations are an explicit time budget; reaching that
budget does not mean convergence or anatomical correctness. No per-chord patch
script or musical fingering exception is used by this pipeline.

## Actual final outcome

The complete final batch processed **42 chords**: seven existing audited poses
were preserved and 35 replacements received the same bounded common fit and
unchanged exact audit. **None of those 35 replacements passed every physical
check.** 16 reached zero combined self crossings but still failed another
physical criterion; zero self crossings alone did not make them acceptable.
The runtime authoring output is byte-identical to the prior seven-endpoint
library. **No anatomical/teaching approval was added.** No further fitting is
planned for this delivery.

The definitive counts/source bindings are in [CLOSEOUT.json](CLOSEOUT.json),
[final manifest](final-batch-v2/manifest.json), and
[actual35-row exact audit](final-batch-v2/exact-audit/summary.json). The final
runtime set remains C, Cmaj7, Am7, Em7, E7, Fmaj7 and Dm, all `needs-review`.

To avoid committing dozens of duplicate full collision meshes, the new derived
`*-guitar.json` exports were removed after validation. Their original byte
counts, hashes and exact reproduction argv are in
[derived-exports.json](derived-exports.json). One G export was regenerated,
verified byte-identical, and removed again. Candidate TRS, fit records, pinned
libraries, original failure logs and compressed raw crossing evidence remain.
No older batch3 artifact, product data or runtime asset was removed.
