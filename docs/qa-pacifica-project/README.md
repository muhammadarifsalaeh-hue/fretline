# Pacifica 612VIIFM — shipped four-image gallery

The project owner requested including the four supplied illustrations directly in the website, replacing the earlier preview-only restriction. All four original JPEGs are now registered under the existing model ID and work in ordinary Vite development and the production build. No image selection or upload step is needed in Codespaces.

## Delivered behavior

- Black is the Catalog and Detail default. Red and Blue / Teal switch instantly without navigation. The overview remains a separate fourth gallery image.
- Color radios, thumbnails, keyboard navigation, touch/swipe and Lightbox share selection state. Gold focus/selected borders and the original full image proportions are retained.
- No AI badge appears on cards or the main image. User source, AI editing history and the instruction to use the images remain in `src/data/catalog/projectArtwork.json`; these are separate from existing licensed-photo records. No license, exact-image model or official-finish verification is asserted.
- Details and the Yamaha Thailand recommended retail price of 34,000 THB retain the existing manufacturer-source records. No guitar facts or source fields were changed in this update.
- The existing stable ID is used by Homepage, Catalog, Detail, Compare, Quiz, Brands and Wishlist. There are no per-color guitar records.

## Validation

| Check | Result |
|---|---|
| `npm run build` | Passed; all four JPEGs included in output |
| `npm run catalog:check` | Passed; 200 models, 10 brands, 20 each, no duplicate model/ID |
| `npm run images:check -- --write` | Passed; 2 licensed photos plus 4 project illustrations; 197 placeholder models |
| Production browser regression | 79 checks passed |
| Normal `npm run dev` browser regression | 79 checks passed |
| Responsive widths | 1440, 1024, 768, 390, 320 px, no page overflow |
| Console/runtime errors and failed requests | None in either browser run |
| Original JPEG bytes | All four HTTP responses match supplied SHA-256 values |
| Existing data | Reviewed catalog, Phase 7 data, extras, archives, policy and licensed-photo records byte-for-byte unchanged from 23b7faa |
| Physical Safari/iPad | Not tested; Chromium touch emulation only |

Browser coverage includes default/three colors, overview, thumbnails, Lightbox, keyboard, touch, refresh, Back/Forward, RRP/specification display, Wishlist persistence, Compare, Homepage, Yamaha's 20-card brand page, Quiz results, an existing licensed gallery and an unchanged placeholder model.

## Reproduce

Start a production build preview, then run the externally installed Playwright/Chromium test:

```bash
npm run build
npm run preview -- --host 0.0.0.0 --port 5185 --strictPort
```

In another terminal:

```bash
FRETLINE_QA_URL=http://127.0.0.1:5185 FRETLINE_QA_RUN=production python docs/qa-pacifica-project/browser-gallery.py
```

For ordinary development, start `npm run dev -- --host 0.0.0.0 --port 5175 --strictPort` and set `FRETLINE_QA_URL=http://127.0.0.1:5175 FRETLINE_QA_RUN=development` when running the same test. No website dependencies were added. Previous private-preview reports retain their historical assumptions and are not current production-image acceptance tests.

Screenshots and machine-readable results are alongside this report. Some mobile screenshots use a taller 390 px review frame to keep fixed navigation outside the hero capture; interaction/overflow tests use 390×844 and 320×740.

## Changed files

- Four JPEG assets under `src/assets/guitars/yamaha-pacifica-612viifm/`; project artwork manifest.
- Shared image lookup/rendering, gallery/caption and color indicators; Detail selector integration.
- Image credits and Thai/English labels.
- Catalog image counts/checker and image-registration checker.
- Image-gap report, README, intake/Codespaces documentation and this reproducible QA bundle.

No other model data, rating, specification, ID, catalog count, dependency or commit history was changed. No next phase was started.
