# Homepage marquee restoration and Brand Directory redesign

Starting commit: `3b35de897fca64b33e1aaa47661d45a037f91fdc` on `master`.
This is the requested placement correction. **No Phase D work is included.**

## History checked before implementation

The restoration source is **`0b187d0` (approved Phase B)**, the latest pre-Phase-C Homepage with its Animated Brand Marquee.

| Commit | Relevant behavior |
| --- | --- |
| `6894db1` | Original attachment baseline already contains the marquee. |
| `f74f79c` | Retains the animated brand row. |
| `0f00def` | Adds keyboard `focus-within` pause. |
| `0b187d0` | Preserves that improved marquee in the approved Phase B design system. |
| `14f92ca` | Replaces the marquee with the static photographic brand-card grid. |

Only the two-copy, 40-second linear loop and its hover/focus behavior were restored. The project was not reset, historical commits were not replaced, and the old three-featured-brand-card section was not reinstated. Current Hero, typography, navigation and product functionality remain in place.

## Correct placement

**Homepage `/`:** Cinematic Hero and real statistics → Animated Brand Marquee → existing Featured Guitars → categories → Quiz and Compare. The photographic brand-card grid is no longer on Home. The marquee uses the nine existing genuine marks and Córdoba typography, real catalog counts and filtered-Catalog destinations. Hover pauses it; a persistent pause/resume control is also available. Previous/Next buttons and keyboard focus switch to a unique native-scroll row so all ten brands remain reachable. The decorative duplicate is hidden from assistive technology and excluded from the tab order, while its visible links still work with pointer input. Reduced motion disables animation, hides the duplicate and retains manual scrolling. Small repeating logos load eagerly to avoid blank late-loading items in the loop; larger Directory photographs remain lazy-loaded.

**Brand Directory `/brands`:** Ten photographic cards with centered genuine marks or honest typography, black gradients, restrained gold edges, stable image framing and subtle hover/focus feedback. Cards show real model counts and guitar categories. Each card opens `/guitars?brand=<exact brand name>` directly. The existing `/brands/:id` detail routes remain available elsewhere. Search, type/country filters, sorting, result counts, clear filters, empty states and query/history behavior use the unchanged existing logic. Country metadata keeps its existing unverified label.

Directory layout is five columns at wide desktop sizes, three on medium widths and two on narrow screens. Under 640px, compact real-count text avoids splitting the Thai catalog label. Directory search targets are at least 44px high. Credits moved with the photographic cards to the Directory; Home links to that credit section. No new logos, photographs, product records or dependencies were added.

## Actual screenshots

| Requested view | Final screenshot |
| --- | --- |
| Homepage Desktop | [Full page](after/home-desktop-full.png) · [Hero viewport](after/home-desktop.png) · [Marquee viewport](after/home-marquee-desktop.png) |
| Homepage Mobile | [Full page](after/home-mobile-full.png) · [Hero viewport](after/home-mobile.png) · [Marquee viewport](after/home-marquee-mobile.png) |
| Brand Directory Desktop | [Full page](after/directory-desktop-full.png) · [Top/controls](after/directory-desktop.png) · [Cards viewport](after/directory-cards-desktop.png) |
| Brand Directory Mobile | [Full page](after/directory-mobile-full.png) · [Top/controls](after/directory-mobile.png) · [Cards viewport](after/directory-cards-mobile.png) |
| Tablet 768px | [Home](after/home-tablet-full.png) · [Marquee](after/home-marquee-tablet.png) · [Directory](after/directory-tablet-full.png) |
| Tablet landscape 1024px | [Home](after/home-tablet-landscape-full.png) · [Directory](after/directory-tablet-landscape-full.png) |
| Small mobile 320px | [Home](after/home-small-mobile-full.png) · [Directory](after/directory-small-mobile-full.png) · [Cards](after/directory-cards-small-mobile.png) |

Before evidence from the unchanged starting build: [Home Desktop](before/home-desktop-full.png), [Home Mobile](before/home-mobile-full.png), [Directory Desktop](before/directory-desktop-full.png), [Directory Mobile](before/directory-mobile-full.png).

Before is an immutable build of `3b35de8` served on port 5300. Final After is a separate immutable build served on port 5303. Captures use the real application, local fonts, native lazy loading and scrolling, with the normal-motion animation running naturally. No screenshot-only DOM, style, source or animation-time substitutions are used. Different captures may show different positions in the running marquee. Full-page captures can show fixed navigation at its original viewport position; the separately supplied native-scrolled viewports show the actual visible navigation context.

## Tests actually performed

| Test | Result | Evidence |
| --- | --- | --- |
| `npm run build` | Passed on final source | [Output](build.txt) |
| `npm run catalog:check` | Passed: 200 unique models, 10 brands, 20 each | [Output](catalog.txt) |
| `npm run images:check` | Passed registered image integrity; 197 existing product placeholders remain | [Output](images.txt) |
| New marquee/Directory acceptance | 13/13 passed on final port 5303 | [JSON](acceptance.json) |
| Final captures/responsive measurements | 5/5 widths passed: 1440, 1024, 768, 390, 320px | [JSON](capture-after.json) |
| Before capture | Desktop and Mobile passed | [JSON](capture-before.json) |
| Existing unaffected Home cases | 10/10 passed | [JSON](home-acceptance.json) |
| Existing shared regression | 18/18 passed, including 40 responsive route visits | [JSON](shared-regression.json) |
| Existing product gallery/feature regression | 79/79 assertions passed | [JSON](regression/browser-home-brand-directory.json) |
| Existing catalog-price checks | 22/22 passed | [Output](price-tests.txt) |
| Existing scroll/focus checks | 6/6 passed | [Output](focus-tests.txt) |
| Existing asset/data integrity audit | 140/140 passed; 19 registered editorial assets and 25 baseline data/product-image files preserved | [JSON](assets-check.json), [Integrity](data-image-integrity.json) |
| Additional protected-source comparison | All 72 files byte-identical to `3b35de8` | [JSON](protected-sources.json) |

The new browser suite checks actual timed linear movement, equal duplicate groups and the half-track loop keyframe, hover/button pause, resume, keyboard access to all ten brands, Previous/Next scrolling, a click on a naturally arriving duplicate link, reduced motion, all ten Directory-to-Catalog destinations with 20 real matching results, combined search/type/country/sort, Back/Forward, empty/clear states, correct image/mark mapping, touch targets, visual containment and stable hover framing.

All recorded final browser runs report **zero console errors, runtime errors and failed requests**. Initial QA identified late-loading offscreen marquee logos and the Directory's 40px input; these were corrected before the final run. A separate overlap assertion was corrected to measure visible text ranges rather than paragraph padding/borders; genuine logo/photo, containment and visible-text overlap checks remain enabled.

Existing 10/18/79 functional regressions ran on immutable snapshot 5301. Subsequent application changes only preload the small marquee marks and increase the Directory search target to 44px. All 13 new acceptance cases and five final capture widths ran on final snapshot 5303 after those changes. Historical tests asserting the deliberately removed Home card grid or the superseded Directory-to-Brand-Detail destination were not misreported as regressions or claimed to pass unchanged.

## Data protection and reference review

Catalog remains **200 guitars / 10 brands / 20 each**, with unchanged IDs, archived records, product data, trust states and image provenance. Existing Hero, navigation, footer, ShopContext, Catalog, product Detail, Compare, Wishlist and Quiz source files are covered by the byte comparisons or unchanged baseline-data hashes. No verification status, price, spec or review was invented or promoted.

The latest user-provided composite reference is the placement guide: marquee on Home, photographic cards in the separate Directory. Final screenshots were inspected against that image for composition, large individual brand identities, black gradients, gold framing and bottom captions. Remaining differences are the available licensed photographic angles/lighting, the genuine oval Squier logo variant and Córdoba's approved temporary typography. Directory's existing alphabetical tie-break remains when all brand counts are equal; sorting was not replaced with an invented ranking. No pixel-match score is claimed.

**Safari limitation:** tests use Chromium/Linux with viewport and touch emulation. Physical iPad Safari and WebKit are unavailable here; actual Safari compatibility is not claimed as tested. A physical-device review remains necessary.

## Files changed

- `src/components/home/Brands.jsx`, `src/styles/home-brands.css`, `src/pages/HomePage.jsx`: restore only the marquee, controls, motion accessibility and placement.
- `src/components/brands/BrandCard.jsx`, new `BrandMark.jsx` and `BrandCredits.jsx`: reusable actual brand identity/credits and direct Catalog cards.
- `src/pages/BrandsPage.jsx`, new `src/styles/brand-directory.css`, `src/main.jsx`: scoped photographic Directory layout, with existing filtering logic retained.
- `src/data/homeBrandAssets.js`, `src/assets/home-brands/README.md`: describe shared brand-level editorial use accurately; asset bytes and rights records unchanged.
- `src/i18n/th.js`, `src/i18n/en.js`: compact model counts and accessible marquee controls.
- `docs/signature-redesign/home-brand-directory/`: reproducible tests, screenshots and actual results.

## Open the updated version in Codespaces

In the existing clean Codespace, stop the old Vite process with Ctrl+C, then:

```bash
git pull --ff-only origin master
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

Preserve any local changes before pulling; do not discard them. Open **Ports → 5173 → Open in Browser** and use its forwarded URL in Safari. Keep the Vite terminal running. This correction stops for visual approval before Phase D.
