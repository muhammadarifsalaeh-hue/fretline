# Changed files

## Application and build integration

- `.gitignore`
- `package.json`
- `src/components/compare/CompareVerdicts.jsx`
- `src/components/detail/DataStatusNote.jsx`
- `src/components/detail/SpecTable.jsx`
- `src/components/guitar/PriceSourceNote.jsx`
- `src/data/additionalSpecifications.js`
- `src/data/catalog/reviewedGuitars.json`
- `src/data/guitarImages.js`
- `src/i18n/en.js`
- `src/i18n/th.js`
- `src/pages/GuitarDetailPage.jsx`
- `src/utils/dataTrust.js`
- `vite.config.js`

## New validation and preview code

- `scripts/check-yamaha-import.mjs`
- `scripts/check-yamaha-preview.mjs`
- `scripts/vite/yamahaImportPreview.mjs`

## Import evidence and review artifacts

- `docs/yamaha-import/preview-assets/`: all 20 unchanged uploaded images; development-only.
- `preview-manifest.json`, `original-metadata/`, `review/`: 18 archive mappings, original source material, actual image inspection and hashes.
- `sources-a/`, `sources-b/`: model-specific Yamaha/Music Arms evidence and input conflicts.
- `tests/`: actual checks, final/earlier raw reports, fixed-build browser tests, Before/After captures and preservation proof.
- `README.md`, `SCREENSHOTS.md`, `TEST-RESULTS.md`: delivery and viewing steps.

No Homepage/CSS/Quiz/Wishlist/3D dependency or product-ID change. Compare receives only a one-class repair to its existing verdict grid item; its logic is unchanged.
