# Fretline — Homepage visual update

Baseline: `3c1d70e` on `feature/premium-quiz-compare`.
Scope: the four Home category cards, the Practice gateway, and the explicitly requested shorter Home Compare description. No new training engine or product-data edits.

## Delivered appearance

- Category cards use four separate clean cinematic backgrounds, a two-column grid at 640px and above, and a single column below 640px. Category names, counts and destinations continue to come from the existing catalog; expected current counts are 90 / 73 / 20 / 17.
- The Practice gateway uses the actual long-haired guitarist photograph supplied as reference image 3. The requested two-line heading, description, three benefits and existing Practice destination are live HTML.
- Landscape keeps Practice large on the left, matching the combined height of Find My Guitar, the gap and Compare on the right. iPad portrait and mobile stack Practice, Find, Compare.
- Find My Guitar keeps its original blue electric photograph, heading, body and gold action. Compare keeps its original music-room photograph and gold action; its body changes only to the explicitly requested wording.
- Hero, brand marquee, Featured, actual Quiz/Compare/Catalog/Practice routes, stored favorites and original product/chord records are preserved.

## Images actually used

- `src/assets/home-scenes/practice-long-haired-guitarist-{480,960,1280}.webp`: proportional WebP derivatives of the supplied image 3. Original and hashes: [practice-photo.json](practice-photo.json), [original](sources/practice-player-original.jpg).
- `src/assets/home-scenes/category-{electric,acoustic,classical,bass}-{480,960,1440}.webp`: four newly reconstructed generic scenes based on the supplied category reference. The image-generation editing tool removed all reference UI, text, counts, arrow buttons and branding. These are category illustrations, never catalog product photographs. Source/generation and derivative hashes: [category-scenes.json](category-scenes.json).
- Original Find/Compare images and shared licensed photos were neither replaced nor edited. Their original required credits remain in the existing Image Credits page and Footer link.
- Images are local, use responsive source sets and lazy loading. Practice source selection accounts for the larger image width needed when a landscape photograph covers a tall card.

## Source files

Modified:
- `src/components/home/CategoryCard.jsx`
- `src/components/home/GuitarPracticeCard.jsx`
- `src/components/compare/CompareSection.jsx` (Home gateway only)
- `src/styles/home-feature-restoration.css`

Added:
- `src/data/homeCategoryScenes.js`
- `src/styles/home-category-scenes.css`
- 15 responsive WebP files in `src/assets/home-scenes/`

## Verification

- `npm run build`: PASS. The existing 709.18 kB `practice-three` chunk warning remains; the 3D engine was not changed.
- `npm run catalog:check`: PASS, 200 models / 10 brands, original stable IDs.
- `npm run images:check`: PASS for registered original image integrity; existing 197 missing-product-photo records remain unchanged.
- `npm run practice:check`: 56/56, preserving the 42 original voicings and geometry checks.
- `npm run phase4:check`: 19/19, original recommendation and comparison rules.
- Actual browser checks: **55/55** (42 focused Home/responsive/navigation checks and 13 unchanged Quiz/Compare regression groups). Chromium 154 and Linux WebKit 26.5; 1440×1000, 1194×834, 768×1024, 390×844, 320×740 and 1024×1366. Zero final console errors, page errors, HTTP errors or failed requests.
- Source and frozen build stayed unchanged during final browser checks; served HTML SHA-256: `37ad79d1e4f440d7244bee226cef5ff4805e18694695df1d411919fa4b887765`.
- Core command logs: [tests/core](tests/core/). Final browser summary: [tests/summary.json](tests/summary.json). Before/After gallery: [tests/before-after.html](tests/before-after.html).
- **300** protected tracked source/config/script files were compared byte-for-byte with baseline, with zero unexpected changes: [preservation.json](preservation.json).
- The first browser run found real category overflow from `aspect-ratio` plus `min-height`; explicit scoped width constraints fixed it. Another run captured a font-request cancellation when the test navigated before the late font settled; the harness now waits for actual paint/font readiness. The zero-failed-request criterion is unchanged. Original diagnostics and provenance are retained under `tests/`.
- These are the commands actually run for this Home change; historical repository checks and reports have not been overwritten or described as newly passing.
- Native iPad Safari is not available in this execution environment. Linux WebKit and responsive/touch emulation are reported separately from physical-device verification.
- Existing product photo gaps and unfinished anatomical hand work are unchanged and outside this visual request. The supplied Practice photograph is illustrative; it does not certify a hand pose or represent a catalog product model.

## View in the existing Codespace

After this feature branch is pushed, update the same branch with `git pull --ff-only origin feature/premium-quiz-compare` and refresh the existing forwarded port 5173 Preview. No branch switch or master merge is required. The user's authenticated Preview URL was not supplied in full; no new public URL or replacement hosting was created.
