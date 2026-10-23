# Phase C — Final polish and visual review

Baseline: `acdcf09ac1d5e2f6574e7977c36195beaf996ce6`, branch `master`.
This delivery refines the approved Homepage. It does not start Phase D.

## Changes delivered

- Kept the approved Brand Showcase composition, ordering, responsive grid and real counts. Reframed the existing licensed photos around guitar details to reduce room, furniture and carpet distractions. Added restrained black vignettes and warm gold edges.
- Enlarged and optically centered the nine existing genuine marks. Their different shapes are preserved, with separate adjustments for Gibson, Taylor, PRS and Martin. The authentic Squier oval remains; its dark background blends more gently into the photo.
- Replaced Córdoba's previous photographic wordmark overlay with the explicitly approved temporary typographic name in the existing Instrument Serif font. Its licensed guitar background and historical provenance remain intact. No official Córdoba logo is claimed or fabricated.
- Applied a restrained, static Hero color grade to reduce orange saturation while retaining the approved image, text placement and crop. Both CTA rows share a control height; icons cannot collapse.
- Balanced mobile statistic labels, standardized Quiz/Compare panel padding and corner treatment, increased Compare preview text/row spacing and reduced unnecessary panel glow.
- Kept existing navigation, footer, product cards, gallery, search and context behavior. Tested their alignment and interactions rather than introducing unnecessary shared-component changes.

No dependencies, product images, guitar records, prices, specs, ratings or IDs were added or changed. No existing image files were removed. Photo credits remain in the expandable credit section, separate from product presentation.

## Actual Before / After screenshots

These are screenshots of the real production app. The Before build was compiled from the clean baseline **before source edits**, copied into an immutable directory and served independently on port 5210. The final After build is a separate immutable snapshot on port 5213. Capture scripts wait for fonts, native lazy loading, image decoding and real scroll reveals; no screenshot-only content/style substitutions are applied. Brand crops use actual full-page screenshot pixels.

| Viewport | Homepage Before | Homepage After | Explore by Brand Before | Explore by Brand After |
| --- | --- | --- | --- | --- |
| Desktop 1440 × 1000 | [Before](before/home-desktop-full.png) | [After](after/home-desktop-full.png) | [Before](before/brands-desktop.png) | [After](after/brands-desktop.png) |
| Tablet 768 × 1024 | [Before](before/home-tablet-full.png) | [After](after/home-tablet-full.png) | [Before](before/brands-tablet.png) | [After](after/brands-tablet.png) |
| Mobile 390 × 844 | [Before](before/home-mobile-full.png) | [After](after/home-mobile-full.png) | [Before](before/brands-mobile.png) | [After](after/brands-mobile.png) |
| Tablet landscape 1024 × 768 | [Before](before/home-tablet-landscape-full.png) | [After](after/home-tablet-landscape-full.png) | [Before](before/brands-tablet-landscape.png) | [After](after/brands-tablet-landscape.png) |
| Small mobile 320 × 740 | [Before](before/home-small-mobile-full.png) | [After](after/home-small-mobile-full.png) | [Before](before/brands-small-mobile.png) | [After](after/brands-small-mobile.png) |
| Reference width 1280 × 1000 | [Before](before/home-reference-desktop-full.png) | [After](after/home-reference-desktop-full.png) | [Before](before/brands-reference-desktop.png) | [After](after/brands-reference-desktop.png) |

Hero viewport screenshots are also supplied as `before/home-<viewport>.png` and `after/home-<viewport>.png`.

## Comparison with the approved reference

The user-provided 1280 × 853 reference is visible in the conversation. Its original attachment file is no longer present in this runtime; the earlier Phase C review retained its hash and measured composition in [visual-comparison.json](../phase-c/visual-comparison.json). This review uses that composition and manual inspection of the conversation image against actual screenshots. No automated pixel comparison or accuracy percentage is claimed.

| Element | Actual final result | Remaining difference |
| --- | --- | --- |
| Desktop grid | 5 columns × 2 rows in the specified order. At 1280px: left inset 24px, top of grid 284.27px within section, cards 238.39 × 248.31px, 10px gap. These approved dimensions are preserved. | Header font metrics and overall credit-section height differ from the reference. |
| Background and photography | Deep black canvas, guitar-detail backgrounds, black legibility gradients, subtle warm grade. Static crops remove most distracting surroundings. | Existing licensed photos have different guitars, angles and lighting from the reference; they are not the reference's studio images. |
| Brand identity | Nine genuine marks remain large and legible, with balanced optical centers. | Squier retains its authentic oval variant. Córdoba uses temporary typography, not the official mark. |
| Card details | Fine gold edge, aligned real model counts, circular arrows and restrained hover/focus feedback. The photo crop does not zoom on hover. | Gold highlights are deliberately more restrained than the reference's strong staged reflections. |
| Tablet and mobile | 3 columns at 1024px; 2 at 768px, 390px and 320px. No horizontal page overflow, mark/count/arrow overlap or clipped names found. | These are responsive interpretations of a desktop-only reference, not reference-provided mobile designs. |

The manual review does not treat matching box geometry as proof of photographic or typographic fidelity.

## Tests actually performed

| Check | Result | Evidence |
| --- | --- | --- |
| `npm run build` | Passed on final source | [Build output](build.txt) |
| `npm run catalog:check` | Passed: 200 models, 10 brands × 20, no duplicate/data problems | [Catalog output](catalog.txt) |
| `npm run images:check` | Passed registered file/integrity checks; 197 existing product placeholders remain | [Image output](images.txt) |
| Existing catalog-price checks | 22/22 passed | [Output](price-tests.txt) |
| Existing scroll/focus checks | 6/6 passed | [Output](focus-tests.txt) |
| Existing Home acceptance | 20/20 passed | [JSON](home-acceptance.json) |
| Existing shared regression | 18/18 passed, including 40 responsive page visits | [JSON](shared-regression.json) |
| Existing gallery/feature regression | 79/79 assertions passed | [JSON](regression/browser-phase-c-final.json) |
| Final visual/navigation acceptance | 13/13 passed on final After build | [JSON](visual-acceptance.json) |
| Before and final After captures | All 6 widths passed in each snapshot | [Before](capture-before.json), [After](capture-after.json) |
| Asset/data preservation audit | 140/140 passed; all 19 registered Homepage files and 25 baseline product/data files preserved | [Audit](assets-check.json), [Integrity](data-image-integrity.json) |

Functional browser suites cover Header and mobile navigation, touch disclosure at 1024px, keyboard open/Escape/focus restoration, mobile dialog trapping and route closure, search/autocomplete/chips, featured tabs/carousel, all ten brand destinations, Catalog search/filter/sort/pagination/history, Wishlist persistence, Compare 2–4 limit/removal, Quiz completion/previous navigation, product galleries and archive/trust behavior. Final visual cases also inspect painted Header icon geometry, 44px controls, footer clearance, hover stability and reduced-motion behavior.

The 20/18/79 functional suites ran against immutable After snapshot 5211. The only subsequent app changes were Córdoba font sizing, Gibson optical clearance and the brand-card vignette/soft highlight. All final composition, navigation, reduced-motion and six-width screenshot checks ran against snapshot 5213 after those CSS adjustments. No application logic changed between those snapshots.

All recorded browser runs report **zero console errors, runtime errors and failed requests**. An initial reduced-motion test rejected a browser identity matrix as movement; the harness was corrected to accept a mathematically identity transform and rerun successfully. No application workaround was introduced for that test.

Performance scope: no new dependencies, assets or animation loops. Existing lazy loading, explicit image dimensions and reduced-motion support remain. Final main JavaScript gzip size is 51.51kB versus 51.43kB before; vendor and catalog chunks are unchanged. Build duration is not a runtime-performance benchmark. No new Lighthouse, field Core Web Vitals or physical-device performance claim is made.

**Safari/iPad limitation:** viewport/touch tests use Chromium on Linux. Physical iPad Safari and WebKit are unavailable in this environment; they have not been tested. A Safari device check remains necessary before claiming device-specific compatibility.

## Data and asset protection

Catalog remains **200 models, 10 brands, 20 each**: Yamaha, Fender, Gibson, Taylor, Ibanez, PRS, Epiphone, Martin, Squier and Córdoba. IDs, archived records and source/trust rules remain unchanged. The data audit still reports 200 partial records, 199 prices on request and zero verified reviews; this UI work makes no new verification claims.

The ten editorial photos are brand exploration imagery, not proof of any catalog model or finish. Their existing license/source records are retained in [asset-downloads.json](../phase-c/asset-downloads.json). The rights audit verifies recorded reuse bases and unchanged files; it does not manufacture permissions or change product-image trust states.

## Files changed

- `src/styles/home-brands.css`: static guitar framing, grade/gradients, mark sizing/optical alignment, restrained gold edges, responsive Córdoba type.
- `src/styles/home-discovery.css`: Hero grade, CTA/icon alignment, mobile label wrapping.
- `src/styles/home-experiences.css`: shared token spacing, panel consistency, Compare readability.
- `src/data/homeBrandAssets.js`, `src/components/home/Brands.jsx`: explicit Córdoba typographic fallback and accurate credit selection.
- `src/i18n/th.js`, `src/i18n/en.js`: accurate temporary-name and trademark credit copy.
- `docs/signature-redesign/phase-c/asset-downloads.json`: retain historical photographic provenance while recording it as inactive in the UI.
- `docs/signature-redesign/phase-c/tests/support.py`, `assets-check.py`: preserve existing assertions while accepting the explicitly approved typographic fallback.
- `docs/signature-redesign/phase-c-final/`: reproducible capture/acceptance scripts, actual evidence, screenshots and this review.

## Review and Codespaces

Phase C is ready for visual review. No Phase D work has been started. Outstanding review items are the different licensed photography, logo variants, temporary Córdoba typography and actual iPad Safari validation.

To update an existing clean Codespace after the delivery commit is pushed:

```bash
git pull --ff-only origin master
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

If Git reports local changes, preserve them before pulling; do not discard or reset them. In Codespaces open **Ports → 5173 → Open in Browser**. Keep the terminal running while viewing on Safari. The forwarded URL from that Codespace is the preview address; `localhost` on the iPad is not the Codespace.
