# Phase 6 — Audit before changes

Baseline: `13f20de4cdf7ec836d764c0842a741ce5da64907` · Audit date: 2026-10-20

36 models / 11 brands. No duplicate IDs or normalized brand/model names detected. 18 sample, 18 partial, 0 verified. 18 unsourced demo prices and 18 unsourced review aggregates. 0 model photos.

The original catalog check counted price gaps only in imported models and did not validate the effective built-in sample records. Phase 6 will audit the data actually used by every page.

## Missing / unverified data by model

| Stable ID | Status | Price | Recorded source | Unknown spec fields | Photo |
|---|---|---|---|---|---|
| `fender-american-professional-ii-stratocaster` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `gibson-les-paul-standard-60s` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `ibanez-rg550-genesis` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `yamaha-pacifica-612viifm` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `prs-se-custom-24` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `epiphone-casino` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `taylor-214ce` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `martin-d-18` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `yamaha-fg800` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `cordoba-c5` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `fender-player-ii-jazz-bass` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `ibanez-sr300e` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `squier-classic-vibe-60s-stratocaster` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `gretsch-g2420-streamliner` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `epiphone-les-paul-standard-50s` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `taylor-gs-mini` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `yamaha-c40` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `fender-player-precision-bass` | sample | Unverified demo amount | None | Demo values — all require evidence | Missing |
| `yamaha-fg850` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, scale, frets, strings, weightKg | Missing |
| `yamaha-fg840` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, scale, frets, strings, weightKg | Missing |
| `yamaha-fg830` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, scale, frets, strings, weightKg | Missing |
| `yamaha-fg820` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, scale, frets, strings, weightKg | Missing |
| `yamaha-fg820-12` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, scale, frets, weightKg | Missing |
| `yamaha-fg820l` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, scale, frets, strings, weightKg | Missing |
| `yamaha-fg800j` | partial | Not supplied | Yes, partial | neck, scale, frets, strings, weightKg | Missing |
| `yamaha-fg800m` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, scale, frets, strings, weightKg | Missing |
| `yamaha-fs850` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, scale, frets, strings, weightKg | Missing |
| `yamaha-fs830` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, scale, frets, strings, weightKg | Missing |
| `yamaha-fs820` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, scale, frets, strings, weightKg | Missing |
| `yamaha-fs800` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, scale, frets, strings, weightKg | Missing |
| `yamaha-fgx830c` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, controls, scale, frets, strings, weightKg | Missing |
| `yamaha-fgx820c` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, controls, scale, frets, strings, weightKg | Missing |
| `yamaha-fgx800c` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, controls, scale, frets, strings, weightKg | Missing |
| `yamaha-fsx830c` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, controls, scale, frets, strings, weightKg | Missing |
| `yamaha-fsx820c` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, controls, scale, frets, strings, weightKg | Missing |
| `yamaha-fsx800c` | partial | Not supplied | Yes, partial | neck, fretboard, bridge, controls, scale, frets, strings, weightKg | Missing |

## Changes required

- Preserve all 36 IDs and routes. Retain legacy raw files in history/source, but replace their public values with source-backed records.
- Remove unsourced public prices, weights, ratings, promotional badges and color claims; never infer missing values.
- Confirm model/variant and record exactly which fields each source supports, its retrieval method, date and any edition caveat.
- Keep partial status while price, weight or other fields remain unknown.
- Accept images only after inspecting model match and recording author, source, license and transformations. Casino VT image is excluded because it has a vibrato variant not represented by the standard Casino record.
- Retain existing placeholders for unresolved models.

Detailed baseline: [audit-before.json](qa-phase6/audit-before.json).
