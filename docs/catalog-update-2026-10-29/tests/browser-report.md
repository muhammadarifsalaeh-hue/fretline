# Catalog import — actual browser verification

**38/38 checks passed**: Chromium 19/19 and WebKit 19/19 on the same frozen production build.

- Browser versions: Chromium 154.0.8037.57, WebKit 26.5.
- Viewports: Desktop 1440×1000, iPad landscape 1194×834, iPad portrait 768×1024 and Mobile 390×844.
- Console errors, runtime errors, HTTP errors and failed requests: **0**.
- Source and build files stayed byte-identical during each complete run. Served HTML SHA-256: `530349624ebd042cedf55c3a217f8017421195bc47027b0a9294486f51761d84`.
- No physical iPad/iPadOS Safari test is claimed.

## Executed scenarios

Each engine exercised actual Catalog pagination over all 200 IDs (without duplicates), the exact original ID set, all 10 brands at 20 models each, and all 27 known prices via the explicit zero-minimum budget filter. Fender has 20 models without the budget filter and 9 known-price models with it. Search, ascending/descending price sort and the Thunderbird bass category were checked through the live interface.

The actual product pages showed the new Fender price, precise Music Arms URL and `2026-10-29` check date; all four new Fender specification fields and five new FGX830C fields were asserted. The broader old Fender body materials and the sourced old Yamaha body descriptions remain intact. Missing string counts were not replaced by an inferred six. Existing Pacifica ฿34,000 and FG820-12 ฿16,500 prices were checked in Catalog. Unknown prices show `สอบถามราคา` on Catalog cards, product headers/spec tables, Compare selection cards and price rows; they are never zero-baht product prices. The budget slider’s legitimate zero minimum was not confused with a product price.

Actual Compare checks covered four selected models, all requested Overview fields, all six category tabs, verified prices/cheapest highlighting, precise differences and `ไม่มีข้อมูล` cells. Equal known values plus unknown values remain incomplete without claiming all models equal or different. Rosewood/Mahogany back woods are highlighted as different; equal Solid Spruce top/SYSTEM66 values with unknowns are not. Known `None` electronics remains distinct from unknown data. Difference-only collapse, native horizontal table scrolling, real picker add-four/fifth-disabled, share fallback URL, remove/reload, cancel/confirm clear, and invalid/duplicate/oversized share IDs were exercised.

Home’s three-slide Hero, 10-brand rail, four categories, three feature cards and Featured tabs remain present. The actual brand directory and Fender link, Hero search, saved favorites, five-question Quiz and 42-card Practice library/chord selection were checked. The actual 3D neck reported `ready` in both engines; no anatomical hand approval is implied. Quiz assertions validate current catalog IDs and current sourced prices, not obsolete frozen scores from the pre-price-import data.

## Evidence

- [Combined machine summary](browser-summary.json)
- [Chromium report](browser-chromium/browser-results.json)
- [WebKit report](browser-webkit/browser-results.json)
- [Actual screenshot gallery](browser-screenshots.html)
- [Lossless screenshot manifest](browser-screenshot-manifest.json)
- [Temporary runtime setup](browser-runtime.json)

Twelve actual viewport screenshots were stored as lossless WebP. Every capture was decoded and compared with its original PNG using ImageMagick absolute error **AE=0**. Original report JSON bytes are preserved as gzip before screenshot filenames were updated; no assertions or result values were changed by packaging.

The managed environment did not retain the earlier WebKit temporary runtime. One official WebKit browser download and three specific official Debian libraries were prepared under `/tmp`; no project dependencies or system packages changed. The headless WPE engine was executed and tested. Only validation for the unused GTK desktop frontend was skipped. Initial missing-library setup errors are recorded in the runtime notes and are not reported as application failures.

## Re-run

The harness is `browser-catalog-import.py`. Run it against an explicitly frozen production Preview with `--url` and `--output`; `--engines chromium webkit` defaults to both engines, and `--sizes desktop landscape portrait mobile` defaults to all four sizes. Use the paths and temporary libraries documented in the runtime record if the environment needs WebKit setup again. Hard navigation waits for actual paint, fonts, network idle and Practice scene startup so the harness does not cancel valid pending resources.
