# Actual production-browser results

The final application passed **44/44 Home acceptance scenarios** and the unchanged **25/25 standalone Quiz/Compare regression scenarios**. Both suites ran against the same frozen production build. Chromium was **154.0.8037.57**, Linux WebKit was **26.5**. Both suites recorded zero console errors, runtime errors, failed requests or HTTP errors.

Actual reports: [Home44](final/browser-results.json), [standalone25](standalone-regression/browser-results.json), [same-build proof](frozen-build-parity.json), [90-file preservation](preservation.json), [replay](README.md).

## Home behavior checked

- One main heading, actual 200/10/4/4 statistics, working search submission and keyboard autocomplete, no shortcut chips, no old explanatory Hero caption, no inline Quiz fields/progress and no inline Compare table or switch.
- Order: Hero/stats, Brands, Categories, paired Find/Compare gateways, Featured collection. Banners share a row at desktop/1194px landscape and stack at 768px portrait/390px mobile.
- All four category links and all ten brand links actually opened the filtered Catalog. Category count captures match the unchanged 200-model catalog: electric90, acoustic73, classical20, bass17.
- Home Find opens the original Quiz and its first step. The original complete five-step flow, all22 option values, six frozen recommendation fixtures, back/edit/retake, scores, reasons and caveats passed in the standalone suite.
- Home Compare creates no demo selection and retains all four real saved IDs. Original Compare add/remove2–4 models, category tabs, difference controls, horizontal table scroll, share fallback/native clipboard, clear confirmation, browser back/forward and reload passed in the standalone suite.

## Actual motion and touch evidence

All six Hero scenarios observed the real 0–1–2–0 DOM-state cycle. Browser-measured intervals were **5,898–6,010ms** against the 6,000ms timer. Mouse swipes changed photographs in both directions, search controls remained usable, native Chromium touch changed the photograph on tablet/mobile, and reduced-motion preference held the initial scene static.

All six marquee scenarios retained the preceding strict accepted probe unchanged. Measured automatic speeds were **29.312–30.837 CSS px/s**, within the unchanged27–33 band around30. Each probe crossed an actual loop boundary with no blank frames; the largest normalized frame movement was **2px**, below the unchanged3px ceiling. Mouse drag, native horizontal wheel, automatic resume, keyboard links and reduced-motion behavior passed. Chromium native touch held a finger down for1.25seconds without autoplay fighting the gesture, then resumed after release. No playback or arrow controls or visible scrollbar were added.

Featured checks preserved the original featured model order and exercised all four tabs. Recently added contains18 records backed by existing intake metadata; this is not a product release-date claim. Both price orders contain the original200 records, with18 source-backed prices sorted and unconfirmed prices last. Wishlist toggle changed actual localStorage and reverted correctly. Keyboard tab navigation, desktop/tablet arrows and mobile native horizontal input moved the real product rail.

## Screenshots and preservation

The new [delivery captures](../screenshots/capture-results.json) contain11 actual viewport screenshots: three Hero scenes, four paired/stacked banner layouts and four default Featured views. Default product-rail captures restore its genuine initial left edge after image decoding, because decoding an offscreen image can itself move native horizontal scroll. No navigation or UI was hidden for capture. Other section and full-page evidence for both engines is in `final/`; the12 before screenshots remain bound to commit0f994b4 in `before/`.

The90-file Git-bound preservation check passed. Both standalone tool pages, Quiz components/style/scoring/data, product data, selection context, Practice source/models and existing marquee hook remained byte-identical. A separate core audit protects a larger shared-site set; see [core results](core/README.md).

## Limits

**Physical iPad Safari was not tested.** Linux WebKit and Chromium's native automated touch input do not certify a real iPad. Portrait/landscape finger swipe, momentum, tap accuracy, search, Quiz and Compare still need physical-device review. Linux WebKit software startup painting can be less fluent than its steady motion; passing the steady-state timing and loop checks is not a hardware performance certification.

Catalog photo gaps are preserved honestly:197 of200 models have no registered publishable product photo, Pacifica retains its original illustration, and the two previously licensed exact-model photographs remain. Generic category and editorial photos never replace missing model photos. Córdoba remains its existing typographic fallback because permission for a standalone logo was not established.

Two interrupted preliminary runs retain test-setup mistakes in separate folders. They were corrected using canonical Compare URLs, actual browser slide timestamps and real selection-route setup. No product motion criterion or data rule was weakened. Historical stale Phase5–9 fixture assumptions from the preceding Yamaha import were not rewritten or claimed green; core Build/Catalog/Images/Practice/Quiz checks are recorded separately.
