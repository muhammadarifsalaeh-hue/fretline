# Core checks and source preservation

Baseline: `0f994b4990211acc9151293c9f17a3aa65a156ef`.

Actual executed results are in `results.json`; each command has its complete stdout/stderr log. Every command exited0:

- `npm run catalog:check`:200unique catalog models,10brands,20per brand; no data problems.
- `npm run images:check`:registered image file and rights integrity passed.197existing models still lack registered product images; this is retained content debt, not a new broken-load failure.
- `npm run practice:check`:56passed,0failed, including all42chord-data definitions and original six-string fret geometry. This does **not** certify any hand pose as anatomically verified.
- `npm run phase4:check`:19/19original Quiz recommendation / Compare data-trust checks passed.
- `node scripts/check-yamaha-import.mjs`:11/11source-evidence, price/specification and production-image isolation checks passed. The checker's original evidence report bytes were restored after the run, so this Home QA does not rewrite prior delivery evidence.

`check-preservation.py` actually compares123protected source/assets byte-for-byte against the baseline. `preservation.json` lists each baseline/current SHA-256. The original product database/IDs/image-rights records, dedicated Quiz page+components+styling+questions+scoring, dedicated Compare page+table+picker+context+styling, 3D assets/code/chord data and brand motion hook/CSS are unchanged. The Home Brands component is authorized presentation scope; its sole diff removes the small credit link while the existing credit pages and global Footer links remain.

Reproduce from repository root:

```bash
python docs/home-editorial-refinement/tests/core/check-preservation.py
npm run catalog:check
npm run images:check
npm run practice:check
npm run phase4:check
node scripts/check-yamaha-import.mjs
```

A production build must already exist for the Yamaha isolation check. This agent did not run a build or overwrite root's frozen production output. No historical stale Phase5–9 expectations were changed or claimed passed. Physical iPad Safari was not tested here.
