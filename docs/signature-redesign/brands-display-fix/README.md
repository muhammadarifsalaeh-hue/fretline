# Brand Directory: WebKit display fix

Scope: `/brands` only. Baseline: `32dc82d54ee19c986d11db497e111b8333ae4896`.
This is a display/recovery fix, not Phase D or a new visual direction.

## Reproduced cause

The unmodified baseline actually collapses every card in Linux WebKit 26.5.
At 768 × 1024 each card measures **2 × 2.4375px**, while its grid column is
346px wide. The screenshots reproduce the reported black area and gold dots.
All photo/logo descendants were absolutely positioned; the grid item relied on
automatic width, `aspect-ratio` and `min-height: 0` for all its dimensions.
WebKit's intrinsic sizing reduces this otherwise empty item to its border, and
`overflow: hidden` clips the artwork and text. Chromium stretches it, masking the
problem. Paths, decoded assets, opacity, stacking and lazy loading were checked;
none explained the original collapse.

The fix explicitly fills/stretches the grid column, reserves height with a
normal-flow percentage spacer, and retains a minimum height. It does not rely
on `aspect-ratio` for an otherwise empty box. The final WebKit card at 768px is
**346 × 421.5px**. Existing responsive proportions, photographs, gradients,
genuine marks, typed Córdoba name, borders and hover/focus styling remain.

[Root-cause measurements](root-cause-webkit.json) separate the unmodified
baseline from deliberate CSS diagnostic variants. Injected diagnostics are
**not** the actual After screenshots or a recording of physical iPad behavior.

## Before / After evidence

These are actual production builds: baseline on port 5400, final code on 5402.
The actual captures do not replace content, images or styles for screenshots.
Native scrolling triggers lazy loading and checks painted lettering per card.
The same real reduced-motion preference is used for both builds.

| WebKit viewport | Before | After |
| --- | --- | --- |
| Desktop 1440 × 1000 | [Full page](before/webkit/actual/directory-desktop-full.png) | [Full page: all ten](after/webkit/actual/directory-desktop-full.png) |
| Tablet landscape 1024 × 768 | [Full page](before/webkit/actual/directory-tablet-landscape-full.png) | [Full page](after/webkit/actual/directory-tablet-landscape-full.png) |
| Tablet portrait 768 × 1024 | [Full page](before/webkit/actual/directory-tablet-full.png) | [Full page](after/webkit/actual/directory-tablet-full.png) |
| Mobile 390 × 844 | [Full page](before/webkit/actual/directory-mobile-full.png) | [Full page](after/webkit/actual/directory-mobile-full.png) |
| Small mobile 320 × 740 | [Full page](before/webkit/actual/directory-small-mobile-full.png) | [Full page](after/webkit/actual/directory-small-mobile-full.png) |

The matching `directory-*-cards.png` files are native-scrolled **viewports** for
inspecting real sticky-header/bottom-navigation context. Full-page captures can
show fixed navigation at the initial viewport boundary; the app has not been
altered to remove it. Chromium Before captures at desktop/tablet/mobile document
that the old UI did not exhibit this WebKit-specific collapse.

Manual review confirms ten photos, nine genuine image marks and the approved
Córdoba typography, with counts and links visible. Source photographs still
differ from the cinematic reference; Gibson/Ibanez macro crops can look softer
than other photos. No assets or rights metadata were replaced in this fix.

## Recovery behavior

- A failed photo becomes a visible dark/gold fallback with the existing abstract
  guitar icon and localized unavailable-image message.
- A failed logo becomes the real brand name as ordinary typography. It is not a
  fabricated logo. Names fit even at 320px.
- Counts, native Catalog links and keyboard focus remain available during a
  failure. A failed decorative header photo is removed without a broken icon.
- HTTP 404 **and** invalid image bytes served as HTTP 200 are tested separately
  for photos and logos. Another case fails all ten photos and nine marks together.

[All-artwork failure at 320px, WebKit](faults/webkit/all-images-404-small-mobile.png).
Fault screenshots intentionally show fallbacks, not missing production assets.

## Completed validation

| Check | Result / evidence |
| --- | --- |
| `npm run build` | Passed: [output](build.txt) |
| `npm run catalog:check` | Passed: [200 models; ten brands; twenty each; no duplicates](catalog.txt) |
| `npm run images:check` | Passed: [output](images.txt); 197 existing product placeholders remain |
| Existing offline asset/rights-record audit | [140/140 passed](assets-check.json); all 19 brand assets valid; existing rights evidence retained |
| Protected source comparison | [172/172 files byte-identical](protected-sources.json) to baseline outside the five allowed source edits |
| WebKit acceptance | [12/12 passed](acceptance-webkit.json): five viewports, sizing diagnostic, all ten Catalog destinations, search/filter/sort/history, four image-failure cases |
| Chromium acceptance | [12/12 passed](acceptance-chromium.json), same coverage |
| Combined artwork failure, 320px | [WebKit 1/1](all-image-failure-webkit.json), [Chromium 1/1](all-image-failure-chromium.json): readable names/counts, contained text, working Catalog link |
| Actual final responsive captures | [WebKit 5/5](capture-after-webkit-actual.json), [Chromium 5/5](capture-after-chromium-actual.json) |
| Existing shared UI regression | [18/18 passed](shared-regression.json), including 40 responsive route visits |
| Existing gallery/function regression | [79/79 passed](regression/browser-brands-display-fix.json) |

Normal production visits have zero console/runtime errors, failed requests or
bad HTTP responses. Expected, deliberately injected HTTP/decode failures are
recorded separately in fault reports; they are not presented as clean requests.
A Before capture's `passed` means evidence collection succeeded, **not** that
the broken baseline passed visual acceptance.

The existing regressions exercise Catalog, Search/Filter/Sort, Back/Forward,
Guitar Detail, multi-color gallery, lightbox, Compare, Wishlist, Quiz and keyboard
navigation. All ten Directory links are actually clicked and checked for the
correct brand query, twenty-result count and matching model IDs.

## Changed source and protected work

Only five source files change:

- `src/styles/brand-directory.css`: robust grid sizing and visible failure styling.
- `src/components/brands/BrandCard.jsx`: photo/logo error recovery.
- `src/pages/BrandsPage.jsx`: decorative-header image error recovery.
- `src/i18n/th.js` and `src/i18n/en.js`: unavailable-image message.

Home, Animated Brand Marquee, shared BrandMark, product data, IDs, assets,
licensing/trust records, routes and business logic remain byte-identical. No
application dependency was added. The database remains **200 / 10 × 20**.

## Browser limitation and reproduction

WebKit 26.5 runs as a real Linux WPE engine through Playwright 1.62.0; Chromium
154.0.8037.57 is a second engine. This is **not a physical iPad Safari test**.
An iPad/macOS Safari device and its exact OS/GPU environment were unavailable.
The exact reported symptom was reproduced in the unmodified WebKit baseline,
then removed in the final build. Final confirmation on the user's iPad remains.

WebKit and four official Debian runtime libraries were prepared under `/tmp`
only. [Runtime package checksums](webkit-libraries.json) and
[test commands/coverage](tests/README.md) document the setup. Optional GTK GUI
host validation was skipped; the actual headless WPE engine launched and
rendered all evidence. No system/application package was installed for this fix.

## View the pushed fix in Codespaces

Stop an existing Vite process with Ctrl+C, then in the existing repo terminal:

```bash
git pull --ff-only origin master
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

Open **Ports → 5173 → Open in Browser**, navigate to `/brands`, then refresh the
old Safari tab. A GitHub push updates the repository; the existing Codespace
needs the pull/restarted preview above. Do not clear website storage or remove
Wishlist data to refresh this CSS fix. Stop here pending review; no Phase D.
