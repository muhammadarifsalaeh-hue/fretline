# Homepage copy audit — latest brief

Baseline: `0f994b4`, `feature/premium-quiz-compare`. The final NEW HOME PAGE IMPLEMENTATION replaces the previous pending Home composition.

## Implemented

- Home Hero no longer renders the descriptive paragraph, quick-search chips, atmospheric/photo-credit caption, or source-purpose tagline beneath its catalog statistics. Original title, two actions, search, and all four actual counts remain.
- Homepage Find and Compare are photographic gateways with one short description and one route link. No embedded quiz questions, progress stepper, sample comparison table, demonstration note or comparison state is present.
- Removed the repeated credit link underneath the brand rail. Trademark/source records remain on `/brands#brand-credits`; photograph licenses remain on `/image-credits`, accessible through the existing global Footer.
- The optional SearchBar `showSuggestions` defaults to `true`; only the Home caller disables the quick-search chips. Autocomplete and search retain their behavior.

## Scope and purposeful retention

- The standalone Quiz and Compare routes, their UI/styles/logic, global Footer, MobileMenu, and translation files are byte-identical to the baseline. An earlier provisional cleanup of these files was restored when the latest brief explicitly protected the dedicated pages.
- Source-backed prices, unknown-data markers, missing-model-image disclosures, errors, image author/source/license records, and modification notes remain. These are accuracy and licensing information.
- No decorative AI branding is added. Existing artwork provenance in rights records and development-only disclosures is not relabeled or removed. The retired unused `hero.artNote` dictionary key is not visible Home copy.
- Product data/IDs, Practice, and all42chords remain outside this presentation task.

Final browser and preservation results are recorded separately; this source audit does not substitute for execution.
