# Conservative importer checks

The importer is `scripts/import-catalog-prices-20261029.mjs`. Its default mode is read-only for the application datastores. It writes a proposed audit to `merge-report.json`; `--apply` is guarded to the isolated `feature/catalog-prices-2026-10-29` branch.

## Actual result

- `node docs/catalog-update-2026-10-29/tests/importer.test.mjs`: **30/30 passed**.
- First apply: **9 new THB prices + 9 missing specification fields**, across **10 existing models**.
- Existing sourced price coverage: **18 → 27**. All 200 original IDs remain, ten brands with twenty models each.
- First apply evidence: [importer-first-apply.json](importer-first-apply.json). The normal [merge-report.json](../merge-report.json) also retains the first applied eighteen field changes.
- A separate dry-run after applying produced **zero changed models, zero field changes and zero changed datastore files**: [importer-idempotence.json](importer-idempotence.json).

## Commands

```bash
node scripts/import-catalog-prices-20261029.mjs --dry-run
node docs/catalog-update-2026-10-29/tests/importer.test.mjs
node scripts/import-catalog-prices-20261029.mjs --apply
node scripts/import-catalog-prices-20261029.mjs --dry-run --report docs/catalog-update-2026-10-29/tests/importer-idempotence.json
```

An ordinary default dry-run replaces the normal merge report. Use a separate `--report` path when checking idempotence to preserve the first applied audit.

## What the tests verify

The pure merge does not mutate its inputs, create/delete IDs, rename products, change categories or images, copy generic editorial descriptions, replace existing prices with null/blank/zero, narrow existing material variants, promote partial status, infer string counts, infer electronics or accept missing/HTTP403/search-only evidence. Price source remains retailer-listed rather than manufacturer RRP; availability remains unknown. A sourced fretless zero is valid for fret count, while zero price, string count and scale are invalid.

The actual archive tests compare all ten JSON and ten UTF-8-BOM CSV representations; check original200IDs and20-per-brand counts; preserve Thunderbird as bass, FG820-12 primary price16500, FG800J materials, all eighteen original prices and broader Player II Stratocaster material choices; and verify exact source-backed metric radius241 rather than inventing241.3mm precision.

The first attempt in the default execution sandbox stopped at a historical `git show` subprocess EPERM before integration checks. The full unchanged test file was rerun in the managed execution namespace; all30checks then passed. No assertions or evidence criteria were relaxed.

## JSON formatting

Datastores are written as two-space JSON with existing key/record order preserved. JavaScript serialization normalizes some existing numeric lexemes such as `650.0` to `650`; these have identical JSON numeric values and are not specification changes. This formatting-only churn is accepted for this batch. Semantic field preservation and idempotent bytes after the first apply were verified independently. No follow-up serializer or datastore edits were made after the application build freeze.
