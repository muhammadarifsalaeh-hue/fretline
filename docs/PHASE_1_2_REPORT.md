# Fretline — Phase 1–2 delivery

Date: 2026-10-19. Scope: audit the supplied project and improve the design system,
navigation, and homepage. This is a continuation of `fretline.zip`, not a new app.
No hosting or GitHub repository was supplied; delivery is local source, commits,
build output, screenshots, and a ZIP.

## Phase 1 — audit completed

- Inspected the ZIP, supplied HTML preview, workbook sheets/shared strings,
  source tree, dependencies, routes, data import/check scripts, and existing hooks.
- Original stack retained: React 18, Vite 5, JSX, Tailwind 3, React Router 6.
  No runtime dependencies added. Added a package lock for repeatable installation.
- Retained all existing routes: Home, Catalog, Detail, Compare, Quiz, Brands,
  Brand Detail, Wishlist, and Not Found; retained contexts, storage keys, filters,
  search aliases, import tools, galleries, and recommendation logic.
- The workbook describes 18 models, but the ZIP currently contains 36: 18 sample
  records plus 18 partially sourced records. Zero fully verified records; 18 prices
  unknown; zero real model photos. These are existing content gaps.
- Existing `docs/REDESIGN_STATUS.md` contains historical claims from the attachment.
  A notice now separates those claims from checks performed in this session.

## Phase 2 — implemented

- Dark/gold editorial hero with the existing Thai headline, warm acoustic-guitar
  atmosphere, responsive image sources, and optimized WebP assets (~148 KB desktop,
  ~44 KB smaller image). Image is AI-generated, generic, and explicitly labelled;
  it is never used as a model photograph.
- Reduced desktop hero height and moved Featured Guitars directly after the hero,
  keeping Categories and all subsequent homepage features.
- Compact six-column desktop carousel, refined cards, borders, typography, hover,
  category tabs, navigation arrows, and existing wishlist/compare controls.
- Sample-data labels accompany unverified homepage card prices/specifications.
  Catalog counts are calculated from the existing data; no invented reviews,
  prices, model counts, or specification claims were added.
- Kept Thai word-breaking, heading line height, font fallbacks, keyboard focus,
  reduced-motion handling, and mobile bottom navigation.
- Bundled Anuphan and Instrument Serif fonts locally in WOFF format with their
  SIL Open Font Licenses. Removed Google Fonts network requests from index.html.
- Added a localized homepage document title.

## Bugs fixed

- Escape dismissed autocomplete but retained its active item; a later Enter could
  unexpectedly open an old result. Enter now selects only while the list is open,
  and Escape clears the active item. Added aria-activedescendant references.
- Search icons on pages without an input did nothing. A shared navigation hook
  now returns to the homepage search and focuses it, for Navbar and BottomBar.
- Mobile menu now traps Tab/Shift+Tab, handles Escape, restores focus and previous
  body overflow, and exposes its expanded state and dialog relationship.
- The narrow homepage comparison column overflowed at desktop/tablet widths.
  Its own comparison container now scrolls horizontally without changing the
  standalone comparison page's scrolling/sticky behavior.
- Fixed an unsupported opacity utility on shortcut borders.
- Browser QA initially saw certificate failures for externally hosted fonts;
  bundled fonts remove those requests entirely.

## Files modified / added

Layout: `src/components/layout/{Navbar,MobileMenu,BottomBar,ScrollManager}.jsx`.
Home: `src/components/home/{Hero,HeroStats,FeaturedGuitars}.jsx`,
`src/pages/HomePage.jsx`.
Shared UI: `src/components/guitar/GuitarCard.jsx`,
`src/components/search/SearchBar.jsx`, `src/components/compare/CompareTable.jsx`.
Styles/content: `src/index.css`, `src/data/{hero,images}.js`,
`src/i18n/{th,en}.js`, `index.html`.
New hook: `src/hooks/useSearchNavigation.js`.
Assets: `public/images/hero/*`, `public/fonts/*` (including licenses).
Tooling/docs: `README.md`, `.gitignore`, `package-lock.json`, `MISSING_IMAGES.md`,
`docs/REDESIGN_STATUS.md`, this report, and `docs/qa/*`.

## Tests performed

- `npm install`: success, 132 packages installed; no application dependency changes.
- `npm run build`: success (136 modules; JS ~361.26 KB / 104.66 KB gzip,
  CSS ~62.94 KB / 11.26 KB gzip). Existing routes remain eagerly bundled;
  route-level splitting remains a possible later optimization.
- `npm run catalog:check`: exit 0, no structural data problems; content limitations
  above remain. This does not independently verify manufacturer data.
- `npm run images:check` and `-- --write`: exit 0, reports 0/36 model photos;
  refreshed MISSING_IMAGES.md. Successful execution does not mean photos are complete.
- Chromium: **35/35 assertions passed**, with zero page errors, console errors,
  or failed requests on the final production-build run. Browser checks use the actual built app (`vite preview`), including
  homepage widths 320/390/768/1024/1440, search and autocomplete, shortcut filters,
  carousel/tabs, wishlist/compare persistence, differences toggle, route rendering,
  five-step quiz, navigation search, focus trap, Escape, and reduced motion.
  See `docs/qa/results.json` for exact assertions and console/request results.
- Screenshots in `docs/qa/`: desktop 1440px, mobile 390px, and full homepage after
  scrolling through sections to trigger the existing reveal animations.
- Visual review against the supplied reference was manual. No pixel-diff metric,
  Lighthouse score, cross-browser certification, or physical-device testing claimed.

## Remaining issues

- Actual, licensed model-specific photography is still missing for all 36 models.
  Placeholders are intentional; generic AI images cannot replace real model photos.
- 18 sample records remain explicitly unverified. Existing detail pages expose data
  status. Manufacturer verification is separate content work.
- Some existing Compare, Quiz, Brands and Wishlist copy remains English; retained
  for the later pages phase. Phase 2 does not claim all-page Thai localization.
- Catalog/detail layout refinements, full accessibility audit, full filter/sort/
  pagination/gallery regression, and cross-browser/mobile-device checks remain.
- The UI is closer to the reference, but the missing model photos and retained
  later-page layouts prevent a claim of visual parity or production readiness.

## Next phase

Phase 3: reference-led Catalog and Guitar Detail refinements, including category
navigation, brand filter search, pagination, thumbnail rail, specification tabs,
and responsive behavior. Keep all existing data and source verification notes.
Then Phase 4 covers Compare, Quiz, Brands, Wishlist and their Thai copy; Phase 5–6
cover broader performance/accessibility/SEO and release validation.

## Run locally

```sh
npm ci
npm run dev
npm run build
npm run preview
```

The ZIP contains source and `dist/`, excludes `node_modules/` and `.git/`, and
includes a patch plus commit metadata for review. Browser QA uses Python
Playwright and system Chromium; it is tooling for this delivery, not a new app
runtime dependency. Its script starts from an empty browser context.
