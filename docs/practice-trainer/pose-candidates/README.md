# Rigged hand candidates: authoring diagnostics

Every row is a different candidate fitted through the actual MakeHuman skin weights and bind matrices. All candidates remain **needs-review**, with every review gate false. These are authoring artifacts, not validated practice examples.

The table and `authoring-metrics.json` preserve the original numerical authoring
pass against asset `d46b7545…`. The final plain-sleeve asset `23fdb574…` preserves
every hand attribute, triangle index, bone and inverse bind matrix exactly;
[`hand-rig-equivalence.json`](../models/authoring/hand-rig-equivalence.json) records
that comparison. The C seed has been explicitly retargeted with that evidence.
These historical authoring metrics are not a current anatomical approval.

The separate [`runtime-review/README.md`](runtime-review/README.md) records actual
runtime pose snapshots and rejection diagnostics against the final rig. It
reconstructs local bone quaternions and root transforms, rather than trusting
cached optimizer metrics, then tests nonadjacent skin triangles and dense
wood/open-string samples. The full raw crossing reports are retained as gzip
JSON. A later C correction has its own pose-solver audit and must be compared by
transform hash; it must not inherit the status of an older snapshot.

Contacts are measured against real deformed skin triangles. Ordinary fingers also report the distal flesh patch anchor error. Barre contacts independently select a barycentric point on the index palmar surface for every inclusive string, including strings fretted higher by another finger.

Targets use the pressed string top (board top + 1 mm fret height + string gauge) at 4 mm behind the fret wire. This does not simulate compliant flesh. Wood measurements sample every skin vertex in a conservative neck solid. They do not rule out triangle crossings. Inter-finger gaps and open-string clearances are vertex diagnostics. Full triangle collision, self-collision, anatomy and four-view review remain pending.

| Chord | Max skin contact error (mm) | RMS (mm) | Wood vertices >0.25 mm | Max wood depth (mm) | Min open-string clearance (mm) | Barre skin triangles |
|---|---:|---:|---:|---:|---:|---:|
| C | 0.339 | 0.245 | 0 | 0.008 | 1.547 | — |
| D | 0.112 | 0.087 | 4 | 0.424 | 3.325 | — |
| E | 0.317 | 0.251 | 0 | 0.000 | 2.436 | — |
| F | 0.438 | 0.229 | 33 | 1.257 | None | 6 |
| G | 0.300 | 0.227 | 0 | 0.000 | 2.894 | — |
| A | 0.242 | 0.192 | 4 | 0.466 | 1.654 | — |
| B | 0.970 | 0.504 | 62 | 1.238 | None | 5 |
| Cm | 0.717 | 0.321 | 45 | 1.273 | None | 5 |
| Dm | 0.342 | 0.255 | 0 | 0.000 | 2.701 | — |
| Em | 0.301 | 0.226 | 0 | 0.000 | 1.678 | — |
| Fm | 0.450 | 0.241 | 33 | 1.267 | None | 6 |
| Gm | 0.499 | 0.365 | 32 | 1.259 | None | 6 |
| Am | 0.318 | 0.248 | 0 | 0.000 | 2.506 | — |
| Bm | 0.421 | 0.226 | 33 | 1.266 | None | 5 |
| C7 | 0.336 | 0.256 | 0 | 0.000 | 1.435 | — |
| D7 | 0.315 | 0.255 | 0 | 0.000 | 3.171 | — |
| E7 | 0.312 | 0.263 | 0 | 0.000 | 0.908 | — |
| F7 | 0.375 | 0.175 | 23 | 1.201 | None | 6 |
| G7 | 0.341 | 0.251 | 1 | 0.259 | 1.977 | — |
| A7 | 0.313 | 0.238 | 0 | 0.000 | 0.086 | — |
| B7 | 0.287 | 0.188 | 0 | 0.006 | 3.223 | — |
| Cmaj7 | 0.445 | 0.351 | 0 | 0.195 | 1.429 | — |
| Dmaj7 | 0.395 | 0.232 | 3 | 0.375 | 0.792 | 3 |
| Emaj7 | 0.339 | 0.256 | 0 | 0.099 | 0.988 | — |
| Fmaj7 | 0.335 | 0.244 | 0 | 0.000 | 1.617 | — |
| Gmaj7 | 0.336 | 0.247 | 1 | 0.385 | 1.451 | — |
| Amaj7 | 0.308 | 0.250 | 0 | 0.000 | 1.792 | — |
| Bmaj7 | 0.304 | 0.189 | 27 | 1.255 | None | 5 |
| Cm7 | 0.505 | 0.260 | 25 | 1.191 | None | 5 |
| Dm7 | 0.719 | 0.578 | 56 | 1.180 | 0.504 | 2 |
| Em7 | 0.336 | 0.336 | 0 | 0.000 | 0.848 | — |
| Fm7 | 0.377 | 0.211 | 13 | 0.929 | None | 6 |
| Gm7 | 0.399 | 0.229 | 10 | 0.804 | None | 6 |
| Am7 | 0.310 | 0.259 | 0 | 0.000 | 1.116 | — |
| Bm7 | 0.689 | 0.319 | 22 | 1.189 | None | 5 |
| Csus2 | 0.396 | 0.274 | 47 | 1.594 | None | 5 |
| Dsus2 | 0.286 | 0.217 | 0 | 0.000 | 0.911 | — |
| Asus2 | 0.315 | 0.238 | 0 | 0.000 | 1.862 | — |
| Csus4 | 0.660 | 0.364 | 47 | 0.875 | 0.112 | 2 |
| Dsus4 | 0.112 | 0.080 | 1 | 0.271 | 2.739 | — |
| Esus4 | 0.260 | 0.164 | 7 | 1.115 | 1.463 | — |
| Asus4 | 0.356 | 0.288 | 0 | 0.000 | 1.666 | — |

The exact numeric angles, per-string target/actual coordinates, source triangle indices and barycentric coordinates, per-open-string clearances, optimizer termination and pose fingerprints are in `authoring-metrics.json` and `hand-pose-candidates.json`.

Rebuild the initial library with:

```sh
OPENBLAS_NUM_THREADS=1 python scripts/practice/generate-pose-library.py
```

Use `--resume path/to/hand-pose-candidates.json --chords A,Dmaj7,Fm7,Gm7,Csus4 --evaluations 64` for a bounded refinement pass. Resume preserves unselected chord candidates. The checked-in natural C seed keeps authoring reproducible without relying on temporary files. The final artifacts include related-voicing warm starts and a short refinement pass; `authoring-run.json` records that provenance. No command sets a review gate to true.

Resume requires an exact current asset and rig signature. The historical
`d46b7545…` library is intentionally preserved, so it cannot be silently resumed
against the changed sleeve. Start a new authoring pass with the retargeted seed,
or prepare an explicitly documented matching-asset input. Do not weaken the
signature check.

To repeat the runtime rejection audit serially:

```sh
OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python docs/practice-trainer/pose-candidates/audit_runtime_candidates.py
```

This command writes only reports and snapshots under `runtime-review`; it does
not edit production poses or promote any review gate.
