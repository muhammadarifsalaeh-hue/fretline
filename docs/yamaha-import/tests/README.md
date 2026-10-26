# Yamaha import browser QA

The `before/` captures use the unchanged production build from `decd5544ade430530ac7c1e37ae463f251c90d50`, before this import. They show the current placeholder/old-data state, with the canonical `brand=Yamaha` filter and the 20-model result count confirmed. `before/baseline.json` binds the capture to the production index SHA-256.

Acceptance will distinguish two environments:

- Ordinary production: updated sourced facts/prices, the existing licensed FG820-12 image preserved, and permission-pending upload images excluded.
- Explicit local `yamaha-preview` mode: the actual supplied images decoded and viewed, including composite views kept intact and original FG820-12 remaining primary. This mode does not establish image rights or authorize public publication.

Tests use Chromium and Linux WebKit, including 1440×1000 desktop, 768×1024 tablet touch, and 390×844 mobile touch. Linux WebKit and synthesized touch are not evidence that physical iPad Safari passed. Browser checks record actual price text, route IDs, image content hashes/natural dimensions, `object-fit: contain`, lightbox behavior, localStorage behavior, console/runtime/network errors, and horizontal overflow. Existing shared interaction regression cases are run only where their frozen price/image assumptions remain applicable; updated data semantics receive explicit fresh assertions.
