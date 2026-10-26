# Batch 3 — actual validation

Runtime source was frozen before browser QA. Only documentation and test evidence changed afterward.

| Check | Actual result |
|---|---|
| Production build | Pass; existing lazy Three.js chunk warning retained |
| Catalog and image checks | Pass; 200 / 10 / 20; image registry unchanged |
| Practice data/geometry | 56/56 |
| Independent musical/fingering audit | 86/86 |
| Hand runtime/loading/trust/disposal | 17/17 |
| Physical fretted string paths | 42/42 |
| Geometry fingerprint mutation/cache | 6/6 |
| Bounded appearance reveal | 10/10 |
| Real-mesh negative rejection tests | 4/4 |
| All42 real-mesh endpoints | 7 pass / 35 rejected |
| Approved teaching hands | 0/42 |
| Chromium full trainer | 21/21 |
| Linux WebKit full trainer | 21/21 |
| Original site/browser regressions | 107/107 |
| Camera supplement | 2/2 engine cases; all seven presets, rotate, zoom, reset |
| Actual candidate rendering | 4/4 engine/viewport cases; C, Em7, E7, Fmaj7, Dm in four views |
| Actual reveal/lifecycle rendering | 4/4 engine/motion cases |
| Historical Phase4 | Pass, 19/19 |
| Historical Phase5–9 | Five command failures retained; unchanged baseline assertions |
| Physical iPad Safari | Not tested |

## Completed source-bound evidence

Runtime library SHA-256: `2e2816f7adf533f80fba931e4d73b592a670a614ea014406903da162b5f01aa1`. All 42 transform hashes bind the actual integrated root and local bone rotations. The frozen browser reports match the same current library/build. The runtime commit is `43785e22c2edbebbb577ecd645efe84d508512b2`.

The ordinary lesson keeps all hands hidden because the anatomical/multi-view teaching gates are still false. Seven geometric endpoints pass: **C, Dm, E7, Cmaj7, Fmaj7, Em7, Am7**. The remaining 35 are rejected before later contact/guitar stages; those unrun stages are not passes. All original chord/voicing data and the GLB/skin weights are unchanged.

The actual Chromium and Linux WebKit runs each complete all 21 trainer cases. The existing startup-settlement adapter retains the original 800 ms idle assertion; its measured justification is documented in batch2. This batch does not replace a failed full run with a focused case. Any initial failure or rerun is retained separately and must be read with its final report.

Source reports: [browser summary](tests/reports/final-summary.json), [core checks](node-checks.json), [all 42 geometry](geometry/summary.json), [mechanical review](MECHANICAL-REVIEW.md), and [source preservation](source-preservation.json).

## Historical failures and execution context

The initial static check invocation used the restricted network sandbox and logged a Vite HMR listen warning. Its original logs are retained. The six Phase4–9 commands were then rerun with the supported network-enabled execution context; Phase4 passes and Phase5–9 still fail their old product-data/logo/price assertions. [Clean execution reports](legacy-static/network-enabled/summary.json) distinguish these baseline assertion failures from the original environment warning. No product data or old assertion was changed to force success. The earlier [isolated baseline proof](../practice-trainer/tests/reports/legacy-static-baseline.md) remains applicable; protected site/data files are unchanged.

## Performance and device limits

The 160ms reveal changes opacity only; saved bone/root transforms remain exact. Normal-motion and reduced-motion WebGL cases check actual pixels, cancellation, route exit, and stopped idle rendering. One documented controlled-clock case captures half/final opacity reproducibly under software graphics; a separate native-clock case tests completion. No physical/swept chord morph has been certified.

Three.js, the rig and pose library remain Practice-only lazy resources. Existing and new lifecycle checks cover cancellation/disposal and repeat navigation. No dependency, polygon count or texture size was increased. Software-rendered timing/memory results are browser regression evidence, not iPad hardware FPS or GPU-memory certification. **Physical iPad Safari is not tested.** Use the device checklist in [README](README.md) before any merge approval.
