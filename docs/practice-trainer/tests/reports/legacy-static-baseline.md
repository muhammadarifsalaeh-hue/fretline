# Legacy static failures: isolated baseline comparison

All five commands still **fail**. Identical failures reproduced on isolated source from `b21bd6adb8fd1cead2d5fc2aeb0929d2f56eb431`, before the current trainer work. These are not counted as passes.

| Command | Current / baseline exit | Passed before failure | First failing assertion | Cause |
| --- | --- | ---: | --- | --- |
| `npm run phase5:check` | 1 / 1 | 6 | `scripts/check-phase5.mjs:46` | Frozen Phase5 requires no brand price ranges or logos. Baseline already has logos and the Yamaha source-backed THB34,000 recommended retail price. |
| `npm run phase6:check` | 1 / 1 | 4 | `scripts/check-phase6.mjs:35` | Frozen Phase6 requires every public price to be null; baseline Yamaha PAC612VIIFM is THB34,000. |
| `npm run phase7:check` | 1 / 1 | 3 | `scripts/lib/phase9.mjs:35; scripts/check-phase7.mjs:38` | Old Phase9 batch boundary rejects the later approved PAC612VIIFM description, price, specs and sources as an out-of-batch change. |
| `npm run phase8:check` | 1 / 1 | 5 | `scripts/check-phase8.mjs:43` | Frozen Phase8 requires all prices null; baseline PAC612VIIFM is THB34,000. The second npm && script check-phase8-catalog.mjs is not reached. |
| `npm run phase9:check` | 1 / 1 | 0 | `scripts/check-phase9.mjs:23` | Frozen docs/qa-phase9/audit-after.json predates the later PAC612VIIFM update and no longer equals readCatalog(). |

## Evidence and method

- Extracted baseline source, scripts, config, package files and Phase6/7/9 snapshots with `git archive` into `/tmp/fretline-legacy-baseline-b21bd6a`. No working application reset or source modification.
- Shared installed `node_modules` via symlink. A `.git` pointer permitted historical `git show` and ancestry assertions; no checkout, commit or Git state write.
- Ran exact commands serially with sockets permitted. Baseline logs have no socket errors. Current restricted runs had `listen EPERM` for Phase5–7; these warnings are separate from the reproduced assertion failures.
- Every assertion-error body and preceding ordered PASS list match exactly after normalizing repository paths and ignoring an unrelated trailing npm version-update notice. Phase9 output was redirected straight to a file to avoid Node uncaught-exception pipe truncation.
- **368 / 368 protected files have identical SHA-256**, including legacy checks, data records, image/logo assets, data-trust utilities, hooks, comparison helpers, translations, Vite config and audit snapshots. Practice files are explicitly excluded from this preservation manifest.
- No legacy assertion, product data, price, source reference, catalog count, image or logo was changed to force a pass.

The scripts stop at their first failed assertion. Later assertions were not executed. The `phase8:check` npm command does not reach its second `&&` script. Browser regressions and current catalog/image checks are reported separately.

## Retained evidence

- [Structured comparison](legacy-static-baseline.json)
- [Protected file hashes](legacy-static-baseline-file-hashes.json)
- [Baseline command executions](legacy-static-baseline-executions.json)
- Phase5: [current](phase5-final.txt) / [isolated baseline](phase5-baseline-b21bd6a.txt)
- Phase6: [current](phase6-final.txt) / [isolated baseline](phase6-baseline-b21bd6a.txt)
- Phase7: [current](phase7-final.txt) / [isolated baseline](phase7-baseline-b21bd6a.txt)
- Phase8: [current](phase8-final.txt) / [isolated baseline](phase8-baseline-b21bd6a.txt)
- Phase9: [current](phase9-final.txt) / [isolated baseline](phase9-baseline-b21bd6a.txt)
