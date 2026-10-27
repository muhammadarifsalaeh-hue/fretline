# Fretline — new Homepage implementation

Baseline: `0f994b4990211acc9151293c9f17a3aa65a156ef` on `feature/premium-quiz-compare`.

This delivery implements the latest **NEW HOME PAGE IMPLEMENTATION** brief. Its full-page reference replaces the previous pending Home composition. Colored annotations, numbered boxes and reference prices are not website content.

## Implemented composition

1. **Hero:** three existing, licensed real photographs; six-second automatic crossfade; horizontal mouse/touch swipe; no thumbnails/arrows/control list. Original title, both actions and working search remain. The introductory paragraph, suggested-search chips and decorative captions are omitted. Statistics still derive from200models/10brands/4categories/MAX_COMPARE4. Reduced-motion stops automatic image changes; offscreen/hidden tabs stop the timer.
2. **Brand rail:** existing seamless native-scroll marquee, preserved30CSSpx/sec, original9standalone logos plus honest Córdoba typography. Touch/mouse input, automatic resume, reduced motion and keyboard access remain. No playback or directional controls. All10brand links use their actual catalog filter.
3. **Categories:**4correct instrument photographs on dark/gold cards, actual counts90/73/20/17, working type-filter routes. Added a publisher-isolated electric photograph and a publisher-black-backdrop acoustic photograph; retained licensed classical/bass originals. No synthetic background removal or wrong-model product substitution.
4. **Find + Compare:** a pair of photographic gateway banners at widths1024pxand above; stacked below1024px for portrait iPad/mobile. Each has one short description and a gold link. There are no Home questions, answer state, progress stepper or comparison table. Links open the original dedicated routes, preserving saved comparison selection.
5. **Featured collection:** retained original featured records and real IDs; compact cards with existing model-bound images, source-backed prices or honest unknown states, Wishlist/Compare actions, touch scrolling and View All. Four tabs: editorial featured selection (`ยอดนิยม`), recently added catalog records (`รุ่นใหม่`, based on existing intake batch metadata, not an inferred product release date), trusted-price descending and ascending, with unknown prices last.
6. Existing navigation, bottom navigation and Footer remain unchanged.

## Files

- Home composition: `src/pages/HomePage.jsx`.
- Hero: `src/components/home/Hero.jsx`, `HeroStats.jsx`, `src/hooks/useHeroSlideshow.js`, `src/styles/home-hero-slideshow.css`.
- Brands/categories/featured: `src/components/home/Brands.jsx`, `Categories.jsx`, `CategoryCard.jsx`, `FeaturedGuitars.jsx`, `src/styles/home-premium.css`.
- Shared Home gateway: `HomeEditorialSection.jsx`, `FindMyGuitar.jsx`, `src/components/compare/CompareSection.jsx`, `src/styles/home-editorial.css`.
- Removed obsolete Home-only inline Quiz/Compare styles. The actual tool styles are retained.
- `SearchBar.jsx`: optional suggested-chip rendering, defaults unchanged for other callers.
- Image files/data/credits: four new responsive WebP files,80,966bytes total, `src/data/homeCategoryAssets.js`, `HomePhotographyCredits.jsx`. Full sources/licenses/checks: [photos/README.md](photos/README.md).

## Scope and limits

- No product record, ID, specification, price, review, chord record or 3D asset was edited. No new dependency.
- Dedicated Find My Guitar and Compare pages, their UI, scoring, selection/context and table behavior remain byte-identical to the baseline.
- The catalog still has197models without a publication-registered model image. Existing exact-model photographs are FG820-12andD-28; Pacifica612VIIFM retains its prior project illustration. Missing images are not filled with another model's photo. The featured section therefore cannot reproduce the reference's six fully photographed guitars honestly yet. Candidate research and rejected edition mismatches are documented in [photos/FEATURED-CANDIDATE-AUDIT.md](photos/FEATURED-CANDIDATE-AUDIT.md).
- Reference instruments, studio lighting and typefaces differ from the licensed photographs available here; no unlicensed reference image was published as a product photograph.
- Córdoba remains typographic because permission for a reusable standalone official logo has not been established. No fake mark was drawn.
- Required authors, sources, licenses and change notices remain on `/image-credits`, linked from the global Footer; brand trademark information remains on `/brands#brand-credits`. See [COPY-AUDIT.md](COPY-AUDIT.md).
- Linux WebKit is not physical iPad Safari. Physical iPad portrait/landscape, real finger momentum, display smoothness and all navigation remain a device-review step. No device pass is claimed.

## Verification and review

Executed Home acceptance: **44/44 passed** across Chromium154.0.8037.57andLinuxWebKit26.5, with zero console/runtime/network/request errors and stable source/build hashes. This includes all3Hero images over the actual0–1–2–0cycle, search/autocomplete,6sections, responsive banner layouts, actual category/brand routes, all4Featured tabs/Wishlist/scrolling, reduced motion and strict marquee input/loop checks.

The actual Hero change intervals were5898–6010ms. Marquee motion measured29.312–30.837CSSpx/sec against the retained27–33band, with at most2px normalized movement at the actual loop boundary and no blank frames. These automation results do not certify physical iPad startup/gesture performance.

Build, Catalog and Images Check passed; Practice56/56, original Quiz/Compare logic19/19andYamaha11/11passed. **123protected files remain byte-identical**, including both standalone tool pages and all original product/chord data. See [core results](tests/core/README.md), [Home report](tests/final/browser-results.json) and [test replay](tests/README.md). The historical stale Phase5–9product-data assumptions were not rewritten or claimed green.

Before captures use a separately frozen production build at0f994b4. Final default captures preserve actual navigation and restore only the product rail's initial scroll position after decoding its images; nothing is hidden or composited into the screenshots.

| View | Before | After |
| --- | --- | --- |
| Desktop Hero | [Before](tests/before/desktop-hero.png) | [Slide1](screenshots/desktop-hero-slide-1.png) · [Slide2](screenshots/desktop-hero-slide-2.png) · [Slide3](screenshots/desktop-hero-slide-3.png) |
| Desktop banners | [Before Find](tests/before/desktop-find.png) | [Paired banners](screenshots/desktop-editorial-pair.png) |
| iPad landscape | — | [Paired banners](screenshots/landscape-editorial-pair.png) · [Featured](screenshots/landscape-featured.png) |
| iPad portrait | [Before Find](tests/before/tablet-find.png) | [Stacked banners](screenshots/tablet-editorial-pair.png) · [Featured](screenshots/tablet-featured.png) |
| Mobile | [Before Find](tests/before/mobile-find.png) | [Stacked banners](screenshots/mobile-editorial-pair.png) · [Featured](screenshots/mobile-featured.png) |

Screenshot source hashes and no-overflow measurements: [default capture report](screenshots/capture-results.json). All original viewport/full-page browser captures remain under `tests/final/`.

Local initial-entry scripts/styles decreased from186,021to178,821gzipbytes while adding the licensed responsive category images. This is a build-artifact observation, not a field speed or Lighthouse claim. No new dependency was added, and no3Dmodule/GLB is requested onHome. See [entry assets](tests/core/entry-assets.json).

The unchanged standalone Quiz/Compare browser suite also passed **25/25** on this same build, with zero browser/network errors. All262common source/build hashes match the44-case Home suite, the standalone suite, the11default captures and the final files. See [executed results](tests/TEST-RESULTS.md) and [frozen-build parity](tests/frozen-build-parity.json).

## Open in Codespaces

```bash
git fetch origin
git switch feature/premium-quiz-compare
git pull --ff-only
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

Open **Ports →5173→Open in Browser**, route `/`. Keep any local edits before switching branches. No public deployment or merge into `master` is part of this change.
