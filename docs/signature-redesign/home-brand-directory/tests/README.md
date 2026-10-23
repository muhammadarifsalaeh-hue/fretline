# Home marquee and Brand Directory correction QA

These tests run against the existing production app. Root supplies an immutable
Vite preview; these scripts do not start a server, install dependencies, mutate
application content/styles, replace images, or intercept requests. They reuse
the existing catalog identity reader and application-agnostic browser helpers.
Python Playwright, Pillow and Chromium are external QA tools, not app dependencies.

```bash
FRETLINE_QA_URL=http://127.0.0.1:5214 python docs/signature-redesign/home-brand-directory/tests/acceptance.py
FRETLINE_QA_URL=http://127.0.0.1:5214 FRETLINE_QA_STAGE=after python docs/signature-redesign/home-brand-directory/tests/capture.py
```

Ports above are examples. `FRETLINE_QA_OUTPUT_DIR` changes evidence destination.
`FRETLINE_QA_CASES=responsive,marquee-motion` selects matching acceptance cases;
`FRETLINE_QA_VIEWPORTS=desktop,tablet,mobile` selects capture sizes. Optional
`FRETLINE_QA_STAGE=before` captures the baseline without asserting the new design.

## Thirteen acceptance cases

- Five responsive cases: 1440×1000, 1024×768, 768×1024, 390×844 and 320×740.
  Home has a marquee after Hero and before Featured, without a photo-card grid.
  Its primary row contains ten unique actual brands, nine genuine marks and one
  Córdoba text fallback. Reduced motion disables animation, hides the duplicate
  group and retains a manually scrollable unique row. Directory has ten matching
  real photos/marks, actual20model counts, contained marks, equal cards, correct
  filtered-Catalog URLs and44px toolbar controls. No page horizontal overflow or
  broken image is accepted.
- Two normal-motion cases sample real animation frames on Desktop and Mobile,
  verify identical duplicate-group widths/order and linear half-track keyframes,
  then exercise real hover, pause/resume control and restored movement. The
  clone remains pointer-usable while excluded from screen-reader/tab order.
- Two keyboard cases focus and Tab through all ten primary links, requiring
  each focused link to enter the real viewport while animation is stopped. They
  also verify native Previous/Next scrolling and a hidden clone in manual mode.
- One live-clone case waits for the naturally moving duplicate row to reach the
  viewport, then uses actual mouse input to navigate its visible link. It never
  seeks animation time or substitutes a transform. This may take a full animation
  duration (maximum120seconds) before the clone enters view.
- One destination case clicks every Directory card and verifies the existing
  Catalog receives the correct brand, shows20actual results and displays only
  guitar IDs belonging to that brand in the source catalog.
- One filter/history case exercises search, clear, type, country, sorting,
  combined filters, empty state and Browser Back/Forward. Existing unverified
  country metadata is tested as existing behavior, never promoted to verification.
- One feedback case checks real Directory hover/focus feedback while image crops
  and card dimensions stay stable.

## Real captures

For each of the five sizes, capture Home and Directory viewport/full-page PNGs,
plus actual section crops. Native scrolling reveals content and loads lazy
images. Fonts and visible images are decoded before capture. The Home marquee
uses a natural frame of its default running animation; consecutive captures may
show different brand positions. Optional `FRETLINE_QA_MOTION=reduce` captures the
real reduced-motion layout instead. Motion functionality is exercised separately. Section crops are pixels
from actual full-page screenshots, not a reconstructed UI.

Every run records console errors, runtime errors and failed requests and exits
nonzero when any case or recorded error fails. Historical Home `brands` and
`responsive` cases assert the deliberately removed card-grid design; leave those
historical files untouched and use this suite for the replacement behavior.
Unaffected existing feature/regression suites should also run separately.

No claims are made about physical iPad Safari/WebKit, reference-image pixel
accuracy, brand-photo subject authenticity beyond recorded source mapping, or
field performance. Root must inspect screenshots and report remaining visual
differences and actual execution results. Commands here are instructions, not
evidence of a pass until root runs them.
