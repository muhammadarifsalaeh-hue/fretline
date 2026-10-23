# Fretline — Phase C implementation

> Historical Phase C report for commit14f92ca. Córdoba now has licensed guitar imagery and a genuine photographed wordmark; see [Córdoba follow-up](../cordoba-update/README.md). Initial counts and fallback descriptions below record the earlier version.


Continued the existing project from `621dc31` (approved proposal documents), with
Phase B application baseline `0b187d0`. The resumed worktree initially had no
unfinished application edits. This delivery implements the actual Homepage;
it does not restart the project or begin Phase D.

## What changed

- Cinematic Hero: clear CTA hierarchy, preserved full search/autocomplete and
  five working quick filters, restrained motion, readable navigation background.
- Flat catalog facts from real data: 200 models, ten brands, four instrument
  categories, four simultaneous comparisons.
- Three large editorial collection cards on desktop; two on tablet and a mobile
  carousel. All original featured models, category tabs, arrows, progress,
  keyboard navigation, Wishlist and Compare actions remain available.
- Four compact instrument-category links with real catalog counts.
- Reference-led **ten-card Explore by Brand**, ordered Yamaha, Fender, Gibson,
  Taylor, Ibanez, PRS, Epiphone, Martin, Squier, Córdoba. Five columns on desktop,
  three from 900px, two below 900px. Genuine marks, black canvas, warm gold
  borders, photographic backgrounds, native lazy loading, full-card links and
  gold arrow affordances. Each count is computed by the existing BRANDS data.
- Existing five-question Quiz now has a compact editorial entry, including real
  preselected instrument links into the original URL-driven quiz flow.
- Compact live Home Compare preview, source-backed values and RRP qualifier,
  difference toggle, remove actions, and an accessible expandable full table.
- Existing premium Phase B Navbar, Footer, shared card logic, standalone Catalog,
  Detail, Brands, Wishlist, Compare and Quiz remain in use.

## Files

Sixteen application source files are listed in [modified-files.json](modified-files.json).
The three new CSS files are scoped beneath `.signature-home`. No dependency,
product record, Guitar ID, original image or catalog policy was changed.

New editorial assets are isolated in `src/assets/home-brands/`, outside the
standalone Brands logo-discovery folder. Nine genuine logo files and nine
licensed brand-level photographs have recorded sources, authors, license links,
access date and SHA-256 hashes. They are **not product model photographs**.
The on-page credits disclosure carries attribution, modification notices,
trademark clarification and photo license links.

- [Selected assets and hashes](asset-downloads.json)
- [Logo source evidence](assets-research/brand-logos.json)
- [Photo source evidence](photo-research/README.md)
- [Unchanged product data/images](data-image-integrity.json)

Córdoba has a temporary ordinary text label and neutral background, because no
suitable reusable mark/photo was established. No fake logo or another brand's
instrument was substituted. Squier uses its genuine oval mark with original
white-on-dark contrast. Yamaha SVG's unsupported Adobe foreignObject was removed;
visible paths/geometry are unchanged.

## Actual screenshots

These are rendered production-app screenshots, not the proposal/mockup. The
capture scrolls the actual page, waits for local fonts and real image decoding,
and crops Brands from an unaltered full-page PNG. No screenshot content/style
replacement is used.

| View | Homepage | Explore by Brand |
| --- | --- | --- |
| Desktop 1440px | [Full page](after/home-desktop-full.png) · [Hero](after/home-desktop.png) | [Brands](after/brands-desktop.png) |
| iPad landscape 1024px | [Full page](after/home-tablet-landscape-full.png) | [Brands](after/brands-tablet-landscape.png) |
| Tablet 768px | [Full page](after/home-tablet-full.png) | [Brands](after/brands-tablet.png) |
| Mobile 390px | [Full page](after/home-mobile-full.png) · [Hero](after/home-mobile.png) | [Brands](after/brands-mobile.png) |
| Small mobile 320px | [Full page](after/home-small-mobile-full.png) | [Brands](after/brands-small-mobile.png) |
| Reference width 1280px | [Full page](after/home-reference-desktop-full.png) | [Brands](after/brands-reference-desktop.png) |

Before: the actual Phase B application screenshots remain at
[Desktop](../phase-b/after/home-desktop.png),
[Tablet](../phase-b/after/home-tablet.png),
[Mobile](../phase-b/after/home-mobile.png).
See [visual comparison](visual-comparison.md) for reference fidelity and limits.

## Verification

[verification-summary.json](verification-summary.json) links the actual reports:

- `npm run build`, `npm run catalog:check`, `npm run images:check`: passed.
  Full command output is in [checks/](checks/). Image check retains the expected
  197 product placeholders; no missing photo is passed off as a real image.
- Current catalog-price checks: **22 passed**; DOM scroll/focus checks: **6 passed**.
- Actual Homepage acceptance: **20 passed**, including search/autocomplete,
  keyboard tabs, original featured/category sets, collection scrolling,
  cross-page Wishlist persistence, Compare 2–4/limit/remove, brand destinations,
  real Quiz links, history and five viewport sizes.
- Focused final brand-photo/mark and live Compare checks: **7 passed**.
- Existing shared Phase B acceptance: **18 passed**, including Catalog search,
  intersecting filters, budgets/history, card hover, gallery, Wishlist, Compare,
  full Quiz and responsive visits.
- Existing Pacifica/gallery regression: **79 passed**, preserving colors,
  thumbnails, keyboard, lightbox, source/trust metadata, archived links and routes.
- Asset/evidence and unchanged-data audit: **132 passed**, including 25 unchanged
  product-data/image files, nine logo records and nine photo records.
- Actual screenshots at all five requested widths, plus 1280px reference width.
  Final screenshot reports check no page overflow, equal cards, loaded photos,
  logo containment, count/arrow separation, one H1 and no broken images.
- Browser reports record **zero console errors, runtime errors and failed
  requests** in the tested flows. No forced clicks or mocked responses.

Initial QA caught a real expanded Home Compare remove-button stacking issue;
it is fixed within Homepage CSS and normal clicks now pass. It also caught the
Squier monochrome-filter problem; original contrast is preserved. Capture waits
were improved to decode every brand photo before taking full-page screenshots.
The count matcher now inspects the actual count caption instead of concatenated
positioned card text. Initial local failure screenshots are ignored by Git;
final reports and captures are retained.

[Local performance diagnostics](performance.json): fresh Chromium contexts,
normal motion, no CPU/network throttling, local Vite production preview. CLS was
approximately **0.00051 desktop / 0.00054 mobile**; observed LCP approximately
**1.82s / 1.92s**. These are local observations, not Lighthouse scores or real-user
Core Web Vitals. New images are WebP/lazy-loaded, geometry is reserved, parallax
was removed, reduced-motion is supported, and the full Home comparison defers
its gallery/table rendering until expanded.

Historical Phase 4–9 scripts with earlier fixed data/image assumptions are not
claimed as newly passed. Current catalog validators and the applicable shared,
Homepage, gallery and asset regression suites are the reports above.

## Remaining limits and review

- Physical Safari/iPad testing was unavailable. Chromium viewport/touch emulation
  covered 1440, 1024, 768, 390 and 320px; actual Safari remains a user-device check.
- The licensed photographs differ from the reference's cinematic photography.
  Córdoba is an explicit visual fallback. No pixel-perfect match is claimed.
- The existing 200 records remain partial; 199 prices remain on request and no
  reviews were invented. This UI delivery does not upgrade data verification.
- Stop here for the user's Homepage review. No next phase was started.

## Update the existing Codespace

If Vite is already running, stop that Terminal process with Ctrl+C first:

```bash
git pull --ff-only origin master
npm ci
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

Open **Ports → 5173 → Open in Browser (globe)**. Keep the port Private and sign
into GitHub on Safari. A forwarded URL depends on the actual Codespace; localhost
and this QA environment's port5203 are not a public iPad link. If Git reports local
changes, keep them and resolve that message before pulling; do not reset files.
