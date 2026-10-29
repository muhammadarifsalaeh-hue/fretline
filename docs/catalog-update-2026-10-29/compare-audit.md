# Compare audit and scoped update

Baseline: `edc293f`, branch `feature/catalog-prices-2026-10-29`.

Existing canonical specification keys already support the requested comparison data: `bodyShape`, `body`, `top`, `back`, `sides`, `neck`, `fretboard`, `strings`, `frets`, `scaleMm` / `scale`, `pickups`, `pickupConfiguration`, `electronics`, `bridge` and `controls`. No alternate product schema or guessed fields are introduced.

Implemented behavior:

- Preserve required body-shape/top/back/sides/electronics rows even when all selected records lack data, and include them in the existing Overview tab.
- Use Compare-local `ไม่มีข้อมูล` / `No data` for unavailable specifications. Preserve `ยังไม่ยืนยัน` when the sample-data safety gate blocks an unverified value.
- Let price use the existing price formatter and trust rules, including `สอบถามราคา` for unknown/untrusted/invalid values. The shared price wording is updated separately in this catalog release.
- Stop the compact cell override from replacing missing prices and specifications with a generic status.
- Compare known values with case/whitespace normalization; convert valid source inches to millimetres using the existing exact conversion. Preserve source presentation. Explicitly different millimetre values are not guessed to be equal.
- `same` requires complete evidence; `diff` requires at least two distinct known values. Unknown values alone do not prove a physical difference. `incomplete` records missing values without presenting them as sameness or confirmed differences.
- Keep the current comparison design and difference background. Known cells in a differing row retain brighter text; unknown cells stay muted and cannot receive best-price markers or difference notes.
- Legitimate zero frets (fretless) and verified zero-star ratings remain known. Zero/negative/non-finite prices and invalid scales cannot render as valid measurements/prices.

New independent fixture checks: `tests/check-compare-fields.mjs`. Fixtures exist only in this audit/test script. They do not modify the product catalog. Test field visibility, missing vs known absence, incomplete vs genuinely different data, string normalization, equivalent units, invalid numbers, trusted THB prices and price fallback, sample safety gates, optional rows, and legitimate zero values.

Historical test impact: comparisons previously counted a known value vs missing data as `diff`; the authorized correction now reports that row as incomplete. Older browser or snapshot assertions that equate null with a confirmed difference must be reported as outdated, not weakened to manufacture a pass. The original phase-4 checks for all-null rows and sample protection remain valid.

## Actual focused test result

`node docs/catalog-update-2026-10-29/tests/check-compare-fields.mjs`: **15/15 PASS**, exit 0. See `tests/compare-fields.log` and `tests/compare-fields-results.json`. This result is the data/row-analysis fixture suite; actual browser verification is reported separately.
