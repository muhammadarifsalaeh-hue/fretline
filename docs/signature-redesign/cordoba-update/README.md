# Córdoba brand-card completion

Continues the existing Fretline project from `14f92ca` and fills the Córdoba card
in Homepage → Explore by Brand. No next phase, product record, Guitar ID, model
count, price, specification or original product image was changed.

## Delivered

- A genuine Córdoba classical-guitar background, framed from the left wall of
  the2020NAMM booth, excluding the Guild instruments and performer on the right.
- The actual printed Córdoba wordmark from the same photograph, presented as a
  warm wood/ink photographic detail. No generic replacement font, invented logo,
  AI image or traced letterform is used. Original photographed ink remains intact.
- A single1920×1280 WebP (248,512bytes) supplies both areas; the browser reuses the
  same resource. Static CSS frames and reserved geometry support lazy loading.
- Existing ten-brand layout, whole-card link,20-model count, gold arrow, hover,
  touch and keyboard focus remain available. Córdoba opens its20 existing models.
- Source, photographer, license, modification notice and exact hashes are stored;
  the page's credits disclosure identifies the photographic wordmark honestly.

## Source / scope

[2020 NAMM Show — Justin Higuchi](https://www.flickr.com/photos/jus10h/50783452413/),
[Commons file](https://commons.wikimedia.org/wiki/File:2020_NAMM_Show_(50783452413).jpg),
[CC BY2.0](https://creativecommons.org/licenses/by/2.0/), accessed2026-10-23.

This is a licensed photograph depicting the brand, including its printed
wordmark. It is not a separately licensed manufacturer vector-logo file, an
endorsement, or model/finish evidence. Exact guitar models in the scene remain
unidentified. No catalog product gallery uses this background. The official
vector/press material was researched but was not copied into the website merely
because it was accessible. See [photo research](photo-research.md),
[logo research](logo-research.md), and [selected asset](asset.json).

## Actual screenshots

| View | Córdoba card | Full brand grid |
| --- | --- | --- |
| Desktop1440px | [Card](after/cordoba-card-desktop.png) | [Grid](after/brands-desktop.png) |
| Landscape1024px | [Card](after/cordoba-card-tablet-landscape.png) | [Grid](after/brands-tablet-landscape.png) |
| Tablet768px | [Card](after/cordoba-card-tablet.png) | [Grid](after/brands-tablet.png) |
| Mobile390px | [Card](after/cordoba-card-mobile.png) | [Grid](after/brands-mobile.png) |
| Smallmobile320px | [Card](after/cordoba-card-small-mobile.png) | [Grid](after/brands-small-mobile.png) |

Screenshots show the actual built application with native scrolling, real image
loading and local-font waits. Grid images are crops of unaltered full-page
screenshot pixels; no screenshot-only CSS/content replacement is used.

## Verification

- `npm run build`: passed ([output](build.txt)).
- `npm run catalog:check`: passed ([output](catalog.txt));200 unique guitars,
  ten brands,20 per brand. All existing verification/price/review statuses remain.
- `npm run images:check`: passed ([output](images.txt)); expected197 product
  placeholders remain. This update adds brand editorial photography, not a new
  catalog-model photo.
- [Asset/evidence integrity](assets-check.json):140 checks passed.19 registered
  assets now comprise9 standalone logo files plus10 brand photos; Córdoba's
  genuine photographic wordmark reuses the same photo. All25 original product
  data/image files retain exact bytes/hashes ([proof](data-image-integrity.json)).
- [Focused browser](browser.json):6 cases passed. Córdoba at all5 widths;
  every brand destination resolves its20 unique actual models; keyboard/touch,
  Browser Back, labels, source-image reuse, image loading, no page overflow and
  count/arrow separation checked. Zero console/runtime errors/failed requests.
- [Screenshot report](capture.json): final rendered card/grid captures at1440,
  1024,768,390 and320px. Final wordmark readability and crop manually reviewed.

Chromium/Linux touch emulation was available; physical Safari/iPad was not tested.
The printed logo remains a photographic detail with its source wood, so its
texture differs from the other nine vector/PNG marks. It is intentionally not
presented as a clean vector supplied or approved by the manufacturer.

## Files

App: `Brands.jsx`, `homeBrandAssets.js`, `home-brands.css`, Thai/English credits,
`src/assets/home-brands/photos/cordoba.webp` and its asset README. Updated the
existing asset source manifests and regression helpers to check10photos and the
photographic mark's visible frame. Initial Phase C reports remain historical;
this follow-up contains current evidence and screenshots.

## Update existing Codespace

Stop an existing Vite Terminal with Ctrl+C if needed, then:

```bash
git pull --ff-only origin master
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

Open **Ports →5173→ Open in Browser**. No dependency changes or new project are
required. Preserve any local edits if Git reports them; do not reset files.
