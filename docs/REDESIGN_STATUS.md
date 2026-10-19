# Redesign status (Reference-based Thai UI)

Rule set: keep dark/grey + gold, Thai first with Anuphan, no fake data, no dead buttons, keep every working feature.

## Phase 1: DONE (tested)
- Design system: Anuphan (Thai + body), Instrument Serif for the logo and Latin names, Thai typography rules in `src/index.css` (heading line-height >= 1.3, no negative letter-spacing, dictionary word breaking).
- Language layer `src/i18n/` (`th.js` main, `en.js` fallback). Switch with `localStorage['fretline:lang'] = 'en' | 'th'`. Add strings to both files; every `t('key')` must exist in both.
- Layout in Thai: Navbar (active page underline, Account button removed because there is no account system), mobile menu, mega menu, bottom bar, compare bar, footer (dead links and the fake newsletter form removed).
- Home in Thai: hero with real stats panel, search with working shortcut chips, categories, featured guitars (dark), brands, compare preview, quiz call to action.
- Thai search aliases (e.g. typing "เบส" finds bass guitars).
- Removed untrue copy: free shipping / returns / warranty claims on the mobile menu, brand taglines.

## Phase 2: DONE for text and honesty fixes (tested), layout polish still TODO
Done: Catalog and Guitar Detail fully in Thai (toolbar, filters, sort, cards, gallery, lightbox, specs, status notes, similar guitars); dark theme for the "similar guitars" section; removed the fake "free shipping / 30-day returns / 1-year warranty" list and the "VAT included" claim; data-status pill on Detail; search fix so Thai terms match whole words (typing "เบส" no longer returns Basswood guitars).
Still TODO from the reference image (layout only): category icon tabs row above the catalog grid, brand search box inside the brand filter, numbered pagination (currently "load more"), thumbnail rail on the left of the Detail image, "รายละเอียด / สเปก" tabs on Detail (the reviews tab is intentionally left out: no real reviews exist).
## Phase 3: TODO  Compare page + Find My Guitar quiz (Thai strings, image option cards need illustrations or photos).
## Phase 4: TODO  Wishlist (row layout), Brands page, 404, final responsive pass.

## Not buildable without your input
| Item in the brief | Why |
|---|---|
| Real, model-accurate guitar photos | No licensed photos available. Placeholders stay labelled as illustrations. |
| Brand logos (Yamaha, Fender, ...) | Trademarks, no files. Brand names are shown as text. Drop SVGs in `src/assets/brands/<id>.svg`. |
| Login / Account, Admin dashboard | No backend or account system exists. Not creating buttons that do nothing. |
| Contact page with a working form | Needs an email address or an endpoint to send to. |
| Guides / Articles | No content exists. Needs real articles. |
| Statistics like "200+ models, 10,000+ users" | Not true. Real numbers are shown. |

## Test notes
- Regression suites run with `localStorage['fretline:lang']='en'` (English strings preserved): 66/66 and 53/53 pass after Phase 1.
- Thai smoke test for Home/layout: 16/16 pass. Thai Catalog + Detail test: 25/25 pass.
- The test browser has no Tailwind CSS, so visual layout and responsive appearance are NOT verified. Open the preview and report anything that looks off.
