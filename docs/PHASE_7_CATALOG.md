# FRETLINE — Phase 7 catalog and manufacturer sources

Checked on 2026-10-20. Exactly **200 active models / 10 approved brands / 20 models per brand**. Added 166 real models, retained 34 original models, archived 2 approved originals. All active data remains **partial**; no complete verification is claimed.

## Counts

| Brand | Before | Retained | Added | Active | Archived |
|---|---:|---:|---:|---:|---:|
| Yamaha | 21 | 20 | 0 | 20 | 1 |
| Fender | 3 | 3 | 17 | 20 | 0 |
| Epiphone | 2 | 2 | 18 | 20 | 0 |
| Ibanez | 2 | 2 | 18 | 20 | 0 |
| Taylor | 2 | 2 | 18 | 20 | 0 |
| Córdoba | 1 | 1 | 19 | 20 | 0 |
| Gibson | 1 | 1 | 19 | 20 | 0 |
| Martin | 1 | 1 | 19 | 20 | 0 |
| PRS | 1 | 1 | 19 | 20 | 0 |
| Squier | 1 | 1 | 19 | 20 | 0 |
| Gretsch | 1 | 0 | 0 | 0 | 1 |
| **Total** | **36** | **34** | **166** | **200** | **2** |

## Evidence and scope

- The 147 new non-PRS models were checked on their individual manufacturer product pages, each with a successful HTTP 200 retrieval and content hash. Vendor/type listings were used to discover models; facts are scoped to the model page, not guessed from neighboring instruments.
- The 19 new PRS models were checked against the official [2025 PRS product catalog](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067), pages 3–8, effective January 14, 2025. This is dated model-year evidence, not a claim of current stock or identical specs in every production year.
- The 34 retained models keep Phase 6 source URLs, dates, scopes and factual values. Their manufacturer pages were not all retrieved again in this phase.
- Exactly 148 new successful manufacturer retrievals support 166 additions: 147 product pages plus one PRS PDF covering 19 distinct models. No source HTML or full copyrighted PDF is redistributed in this repository.
- Names, IDs and normalized brand/model pairs are unique. Color options do not become separate models. Documented design/model differences such as CE electronics, 12 strings, pickup configurations, body design or manufacturer model codes can define distinct model variants.
- Fender/Squier material/fingerboard alternatives remain alternatives when the manufacturer page offers multiple options. Cedar/Spruce or electronics variants use the exact distinct manufacturer model names/codes, not invented labels.
- Scale length preserves manufacturer mm where supplied. The source scope states when string count is derived from the explicitly numbered factory tuning. RG652AHM was rechecked against its six listed strings after correcting comma-space parsing.
- New models have no fabricated experience/style suitability profiles. The existing Quiz formula remains unchanged and discloses missing profiles; a newly added model is not guaranteed a recommendation when supporting profile data is absent.

## Missing factual fields

| Field | Active models still missing |
|---|---:|
| `body` | 0 |
| `neck` | 2 |
| `fretboard` | 0 |
| `pickups` | 2 |
| `bridge` | 1 |
| `controls` | 80 |
| `scale` | 0 |
| `frets` | 41 |
| `strings` | 150 |
| `weightKg` | 200 |

All 200 prices remain unknown in THB and there are no verified review scores. Values not established in the recorded field scope remain `null` and are displayed as unknown. A source-backed identity does not verify an entire record.

## Image rights

No new guitar images were added in Phase 7. The existing [Yamaha FG820-12 owner photograph](https://commons.wikimedia.org/wiki/File:12_string_Yamaha_acoustic_guitar.jpg) by Peternick2468 remains under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). It has six strings fitted to a twelve-string model, disclosed in the UI. **1 active model has a rights-documented photo; 199 use labelled placeholders.** Manufacturer photos were not copied from product pages.

## Active inventory

“New” means added in Phase 7. Each URL supports only the scoped facts and edition in the record. Refer to [field evidence](qa-phase7/field-evidence.json), [retrieval metadata](qa-phase7/source-retrievals.json), [source register](qa-phase7/source-register.json), [application snapshot](qa-phase7/audit-after.json) and [CSV export](qa-phase7/catalog-200.csv).

## Yamaha — 20 models

| Model | Stable ID | Origin | Status | Manufacturer source |
|---|---|---|---|---|
| Pacifica 612VIIFM | `yamaha-pacifica-612viifm` | Retained | partial | [Yamaha](https://ph.yamaha.com/en/musical-instruments/guitars-basses-amps/products/electric-guitars/pacifica/specs.html) |
| FG800 Dreadnought | `yamaha-fg800` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FG850 | `yamaha-fg850` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FG840 | `yamaha-fg840` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FG830 | `yamaha-fg830` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FG820 | `yamaha-fg820` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FG820-12 | `yamaha-fg820-12` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FG820L | `yamaha-fg820l` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FG800J | `yamaha-fg800j` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FG800M | `yamaha-fg800m` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FS850 | `yamaha-fs850` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FS830 | `yamaha-fs830` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FS820 | `yamaha-fs820` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FS800 | `yamaha-fs800` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FGX830C | `yamaha-fgx830c` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FGX820C | `yamaha-fgx820c` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FGX800C | `yamaha-fgx800c` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FSX830C | `yamaha-fsx830c` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FSX820C | `yamaha-fsx820c` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |
| FSX800C | `yamaha-fsx800c` | Retained | partial | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) |

## Fender — 20 models

| Model | Stable ID | Origin | Status | Manufacturer source |
|---|---|---|---|---|
| American Professional II Stratocaster | `fender-american-professional-ii-stratocaster` | Retained | partial | [Fender](https://eu.fender.com/products/american-professional-ii-stratocaster) |
| Player II Jazz Bass | `fender-player-ii-jazz-bass` | Retained | partial | [Fender](https://www.fender.com/products/player-ii-jazz-bass) |
| Player II Precision Bass | `fender-player-precision-bass` | Retained | partial | [Fender](https://www.fender.com/products/player-ii-precision-bass) |
| Player II Telecaster | `fender-player-ii-telecaster` | New | partial | [Fender](https://www.fender.com/products/player-ii-telecaster) |
| Player II Telecaster HH | `fender-player-ii-telecaster-hh` | New | partial | [Fender](https://www.fender.com/products/player-ii-telecaster-hh) |
| Player II Jazzmaster | `fender-player-ii-jazzmaster` | New | partial | [Fender](https://www.fender.com/products/player-ii-jazzmaster) |
| Player II Stratocaster | `fender-player-ii-stratocaster` | New | partial | [Fender](https://www.fender.com/products/player-ii-stratocaster) |
| Player II Mustang | `fender-player-ii-mustang` | New | partial | [Fender](https://www.fender.com/products/player-ii-mustang) |
| Player II Stratocaster HSS | `fender-player-ii-stratocaster-hss` | New | partial | [Fender](https://www.fender.com/products/player-ii-stratocaster-hss) |
| Player II Jaguar | `fender-player-ii-jaguar` | New | partial | [Fender](https://www.fender.com/products/player-ii-jaguar) |
| Player II Mustang Bass PJ | `fender-player-ii-mustang-bass-pj` | New | partial | [Fender](https://www.fender.com/products/player-ii-mustang-bass-pj) |
| Player II Modified Stratocaster | `fender-player-ii-modified-stratocaster` | New | partial | [Fender](https://www.fender.com/products/player-ii-modified-stratocaster) |
| Player II Modified Telecaster SH | `fender-player-ii-modified-telecaster-sh` | New | partial | [Fender](https://www.fender.com/products/player-ii-modified-telecaster-sh) |
| Player II Modified Active Precision Bass | `fender-player-ii-modified-active-precision-bass` | New | partial | [Fender](https://www.fender.com/products/player-ii-modified-active-precision-bass) |
| Player II Modified Stratocaster HSS | `fender-player-ii-modified-stratocaster-hss` | New | partial | [Fender](https://www.fender.com/products/player-ii-modified-stratocaster-hss) |
| Player II Modified Stratocaster HSS Floyd Rose | `fender-player-ii-modified-stratocaster-hss-floyd-rose` | New | partial | [Fender](https://www.fender.com/products/player-ii-modified-stratocaster-hss-floyd-rose) |
| Player II Modified Telecaster | `fender-player-ii-modified-telecaster` | New | partial | [Fender](https://www.fender.com/products/player-ii-modified-telecaster) |
| Player II Modified Active Jazz Bass V | `fender-player-ii-modified-active-jazz-bass-v` | New | partial | [Fender](https://www.fender.com/products/player-ii-modified-active-jazz-bass-v) |
| Player II Modified Active Jazz Bass | `fender-player-ii-modified-active-jazz-bass` | New | partial | [Fender](https://www.fender.com/products/player-ii-modified-active-jazz-bass) |
| CC-60S All-Mahogany Concert | `fender-cc-60s-all-mahogany-concert` | New | partial | [Fender](https://www.fender.com/products/cc-60s-all-mahogany-concert) |

## Epiphone — 20 models

| Model | Stable ID | Origin | Status | Manufacturer source |
|---|---|---|---|---|
| Casino Hollowbody | `epiphone-casino` | Retained | partial | [Epiphone](https://www.gibson.com/products/epiphone-casino-natural) |
| Les Paul Standard 50s | `epiphone-les-paul-standard-50s` | Retained | partial | [Epiphone](https://www.gibson.com/products/epiphone-les-paul-standard-50s-bourbon-burst) |
| Futura Les Paul Custom | `epiphone-futura-les-paul-custom` | New | partial | [Epiphone](https://www.gibson.com/products/futura-les-paul-custom) |
| ES-335 Figured with Rosewood Fretboard | `epiphone-es-335-figured-with-rosewood-fretboard` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-es-335-figured-with-rosewood-fretboard-blueberry-burst) |
| SG Bass with Rosewood Fretboard | `epiphone-sg-bass-with-rosewood-fretboard` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-sg-bass-with-rosewood-fretboard-ebony) |
| Thunderbird '64 with Rosewood Fretboard | `epiphone-thunderbird-64-with-rosewood-fretboard` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-thunderbird-64-with-rosewood-fretboard-ember-red) |
| Wilshire P-90 with Rosewood Fretboard | `epiphone-wilshire-p-90-with-rosewood-fretboard` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-wilshire-p-90-with-rosewood-fretboard-cherry) |
| Riviera with Rosewood Fretboard | `epiphone-riviera-with-rosewood-fretboard` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-riviera-with-rosewood-fretboard-sparkling-burgundy) |
| Coronet with Rosewood Fretboard | `epiphone-coronet-with-rosewood-fretboard` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-coronet-with-rosewood-fretboard-ebony) |
| Sheraton with Rosewood Fretboard | `epiphone-sheraton-with-rosewood-fretboard` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-sheraton-with-rosewood-fretboard-antique-natural) |
| Embassy Bass with Rosewood Fretboard | `epiphone-embassy-bass-with-rosewood-fretboard` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-embassy-bass-with-rosewood-fretboard-sparkling-burgundy) |
| Crestwood Custom with Rosewood Fretboard | `epiphone-crestwood-custom-with-rosewood-fretboard` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-crestwood-custom-with-rosewood-fretboard-cherry) |
| ES-339 with Rosewood Fretboard | `epiphone-es-339-with-rosewood-fretboard` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-es-339-with-rosewood-fretboard-vintage-sunburst) |
| Broadway with Rosewood Fretboard | `epiphone-broadway-with-rosewood-fretboard` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-broadway-with-rosewood-fretboard-vintage-sunburst) |
| ES-335 with Rosewood Fretboard | `epiphone-es-335-with-rosewood-fretboard` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-es-335-with-rosewood-fretboard-cherry) |
| Joan Jett Olympic Special | `epiphone-joan-jett-olympic-special` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-joan-jett-olympic-special-vintage-sunburst) |
| Explorer | `epiphone-explorer` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-explorer-vice-city-blue-exclusive) |
| Les Paul Custom | `epiphone-les-paul-custom` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-les-paul-custom-vice-city-blue-exclusive) |
| SG Standard 60s | `epiphone-sg-standard-60s` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-sg-standard-60s-vice-city-pink-exclusive) |
| Flying V | `epiphone-flying-v` | New | partial | [Epiphone](https://www.gibson.com/products/epiphone-flying-v-vice-city-blue-exclusive) |

## Ibanez — 20 models

| Model | Stable ID | Origin | Status | Manufacturer source |
|---|---|---|---|---|
| RG550 Genesis | `ibanez-rg550-genesis` | Retained | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/rg550_00_04.html) |
| SR300E Bass | `ibanez-sr300e` | Retained | partial | [Ibanez](https://www.ibanez.com/asia/products/detail/sr300e_1p_05.html) |
| AZ2402 | `ibanez-az2402` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/az2402_00_02.html) |
| AZS2200 | `ibanez-azs2200` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/azs2200_00_02.html) |
| AZ24027 | `ibanez-az24027` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/az24027_00_02.html) |
| AZ2204 | `ibanez-az2204` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/az2204_00_02.html) |
| AZ2204N | `ibanez-az2204n` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/az2204n_00_02.html) |
| AZES31 | `ibanez-azes31` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/azes31_1p_01.html) |
| RG8870 | `ibanez-rg8870` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/rg8870_00_02.html) |
| RG5120M | `ibanez-rg5120m` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/rg5120m_00_01.html) |
| RG652AHM | `ibanez-rg652ahm` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/rg652ahm_02.html) |
| RG421 | `ibanez-rg421` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/rg421_1p_06.html) |
| RG470DX | `ibanez-rg470dx` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/rg470dx_1p_04.html) |
| RG450DXB | `ibanez-rg450dxb` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/rg450dxb_1p_06.html) |
| RG653DX | `ibanez-rg653dx` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/rg653dx_00_01.html) |
| RG460DX | `ibanez-rg460dx` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/rg460dx_1p_01.html) |
| RG9PB | `ibanez-rg9pb` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/rg9pb_1p_02.html) |
| RGR52ET | `ibanez-rgr52et` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/rgr52et_1p_02.html) |
| RG5121RET | `ibanez-rg5121ret` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/rg5121ret_00_01.html) |
| RG8570 | `ibanez-rg8570` | New | partial | [Ibanez](https://www.ibanez.com/usa/products/detail/rg8570_00_07.html) |

## Taylor — 20 models

| Model | Stable ID | Origin | Status | Manufacturer source |
|---|---|---|---|---|
| 214ce Grand Auditorium | `taylor-214ce` | Retained | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/214ce) |
| GS Mini Mahogany | `taylor-gs-mini` | Retained | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/gs-mini-mahogany) |
| Big Baby Taylor (BBT) | `taylor-big-baby-taylor-bbt` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/big-baby-taylor-bbt) |
| BT1e | `taylor-bt1e` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/bt1e) |
| Baby Mahogany (BT2) | `taylor-baby-mahogany-bt2` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/baby-mahogany-bt2) |
| GS Mini-e Mahogany | `taylor-gs-mini-e-mahogany` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/gs-mini-e-mahogany) |
| GS Mini-e Rosewood Plus | `taylor-gs-mini-e-rosewood-plus` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/gs-mini-e-rosewood-plus) |
| GS Mini-e Koa | `taylor-gs-mini-e-koa` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/gs-mini-e-koa) |
| Academy 22e | `taylor-academy-22e` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/academy-22e) |
| Academy 10e | `taylor-academy-10e` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/academy-10e) |
| 150ce | `taylor-150ce` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/150ce) |
| 222ce-K DLX | `taylor-222ce-k-dlx` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/222ce-k-dlx) |
| 214ce-K | `taylor-214ce-k` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/214ce-k) |
| 224ce-K DLX | `taylor-224ce-k-dlx` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/224ce-k-dlx) |
| Next Generation 314ce | `taylor-next-generation-314ce` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/next-generation-314ce) |
| Next Generation 324ce | `taylor-next-generation-324ce` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/next-generation-324ce) |
| Next Generation 414ce | `taylor-next-generation-414ce` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/next-generation-414ce) |
| Next Generation 454ce | `taylor-next-generation-454ce` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/next-generation-454ce) |
| Gold Label 510e | `taylor-gold-label-510e` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/gold-label-510e) |
| 612ce | `taylor-612ce` | New | partial | [Taylor](https://www.taylorguitars.com/guitars/acoustic/612ce) |

## Córdoba — 20 models

| Model | Stable ID | Origin | Status | Manufacturer source |
|---|---|---|---|---|
| C5 Classical | `cordoba-c5` | Retained | partial | [Córdoba](https://cordobaguitars.com/iberia/c5) |
| C3M | `cordoba-c3m` | New | partial | [Córdoba](https://cordobaguitars.com/iberia/c3m) |
| C4-CE | `cordoba-c4-ce` | New | partial | [Córdoba](https://cordobaguitars.com/iberia/c4-ce/) |
| C5-CE | `cordoba-c5-ce` | New | partial | [Córdoba](https://cordobaguitars.com/iberia/c5-ce) |
| C5 SP | `cordoba-c5-sp` | New | partial | [Córdoba](https://cordobaguitars.com/iberia/c5-sp) |
| C7 CD | `cordoba-c7-cd` | New | partial | [Córdoba](https://cordobaguitars.com/iberia/c7-cd) |
| C7 SP | `cordoba-c7-sp` | New | partial | [Córdoba](https://cordobaguitars.com/iberia/c7-sp) |
| C7-CE CD | `cordoba-c7-ce-cd` | New | partial | [Córdoba](https://cordobaguitars.com/iberia/c7-ce-cd) |
| C9-CD | `cordoba-c9-cd` | New | partial | [Córdoba](https://cordobaguitars.com/luthier/c9-cd) |
| C9 Parlor | `cordoba-c9-parlor` | New | partial | [Córdoba](https://cordobaguitars.com/luthier/c9-parlor) |
| C9 Crossover | `cordoba-c9-crossover` | New | partial | [Córdoba](https://cordobaguitars.com/luthier/c9-crossover) |
| C10 CD | `cordoba-c10-cd` | New | partial | [Córdoba](https://cordobaguitars.com/luthier/c10-cd) |
| C10 SP | `cordoba-c10-sp` | New | partial | [Córdoba](https://cordobaguitars.com/luthier/c10-sp) |
| C10 Crossover | `cordoba-c10-crossover` | New | partial | [Córdoba](https://cordobaguitars.com/luthier/c10-crossover) |
| C12 CD | `cordoba-c12-cd` | New | partial | [Córdoba](https://cordobaguitars.com/luthier/c12-cd) |
| C12 SP | `cordoba-c12-sp` | New | partial | [Córdoba](https://cordobaguitars.com/luthier/c12-sp) |
| F7 Flamenco | `cordoba-f7-flamenco` | New | partial | [Córdoba](https://cordobaguitars.com/iberia/f7-flamenco) |
| F7 Paco | `cordoba-f7-paco` | New | partial | [Córdoba](https://cordobaguitars.com/iberia/f7-paco) |
| F10 | `cordoba-f10` | New | partial | [Córdoba](https://cordobaguitars.com/luthier/f10) |
| GK Studio | `cordoba-gk-studio` | New | partial | [Córdoba](https://cordobaguitars.com/iberia/gk-studio) |

## Gibson — 20 models

| Model | Stable ID | Origin | Status | Manufacturer source |
|---|---|---|---|---|
| Les Paul Standard 60s | `gibson-les-paul-standard-60s` | Retained | partial | [Gibson](https://www.gibson.com/products/gibson-les-paul-standard-60s-figured-top-bourbon-burst) |
| Dove Original | `gibson-dove-original` | New | partial | [Gibson](https://www.gibson.com/products/gibson-dove-original-vintage-cherry-sunburst-ocssdovcs) |
| J-45 Standard | `gibson-j-45-standard` | New | partial | [Gibson](https://www.gibson.com/products/gibson-j-45-standard-vintage-sunburst-rs45vsn19) |
| Hummingbird Standard | `gibson-hummingbird-standard` | New | partial | [Gibson](https://www.gibson.com/products/gibson-hummingbird-standard-vintage-sunburst-mcsshbvs) |
| SJ-200 Original | `gibson-sj-200-original` | New | partial | [Gibson](https://www.gibson.com/products/gibson-sj-200-original-antique-natural-ocjb20an) |
| L-00 Original | `gibson-l-00-original` | New | partial | [Gibson](https://www.gibson.com/products/gibson-l-00-original-vintage-sunburst-ocsbl0vs) |
| SJ-200 Standard | `gibson-sj-200-standard` | New | partial | [Gibson](https://www.gibson.com/products/gibson-sj-200-standard-maple-tri-burst-tri-burst-mcjb20tb) |
| LG-2 50s Original | `gibson-lg-2-50s-original` | New | partial | [Gibson](https://www.gibson.com/products/gibson-lg-2-50s-original-antique-natural-ocsblgan) |
| J-45 Standard 12-String | `gibson-j-45-standard-12-string` | New | partial | [Gibson](https://www.gibson.com/products/gibson-j-45-standard-12-string-vintage-sunburst-mcrs4512vs) |
| Songwriter Recording Artist | `gibson-songwriter-recording-artist` | New | partial | [Gibson](https://www.gibson.com/products/gibson-songwriter-recording-artist-antique-natural-mcssswraan) |
| Hummingbird Standard EC | `gibson-hummingbird-standard-ec` | New | partial | [Gibson](https://www.gibson.com/products/gibson-hummingbird-standard-ec-heritage-cherry-sunburst-mcsshbechcs) |
| Parlor Rosewood EC | `gibson-parlor-rosewood-ec` | New | partial | [Gibson](https://www.gibson.com/products/gibson-parlor-rosewood-ec-rosewood-burst-mcsbprrb) |
| Songwriter Recording Artist EC | `gibson-songwriter-recording-artist-ec` | New | partial | [Gibson](https://www.gibson.com/products/gibson-songwriter-recording-artist-ec-antique-natural-mcssscraan) |
| SJ-200 60s Original | `gibson-sj-200-60s-original` | New | partial | [Gibson](https://www.gibson.com/products/gibson-sj-200-60s-original-heritage-cherry-sunburst-ocjb2060hcs) |
| Les Paul Special | `gibson-les-paul-special` | New | partial | [Gibson](https://www.gibson.com/products/gibson-les-paul-special-miami-pink-exclusive) |
| Les Paul Junior Double Cut | `gibson-les-paul-junior-double-cut` | New | partial | [Gibson](https://www.gibson.com/products/gibson-les-paul-junior-double-cut-miami-pink-exclusive) |
| SG Standard '61 Stop Bar | `gibson-sg-standard-61-stop-bar` | New | partial | [Gibson](https://www.gibson.com/products/gibson-sg-standard-61-stop-bar-miami-pink-exclusive) |
| Victory Baritone | `gibson-victory-baritone` | New | partial | [Gibson](https://www.gibson.com/products/gibson-victory-baritone-graphite-metallic) |
| ES-335 60s | `gibson-es-335-60s` | New | partial | [Gibson](https://www.gibson.com/products/gibson-es-335-60s-dark-walnut) |
| ES-335 50s | `gibson-es-335-50s` | New | partial | [Gibson](https://www.gibson.com/products/gibson-es-335-50s-ebony) |

## Martin — 20 models

| Model | Stable ID | Origin | Status | Manufacturer source |
|---|---|---|---|---|
| D-18 Dreadnought | `martin-d-18` | Retained | partial | [Martin](https://www.martinguitar.com/guitars/all-guitars/D-18.html) |
| D-28 | `martin-d-28` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/D-28.html) |
| HD-28 | `martin-hd-28` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/HD-28.html) |
| HD-35 | `martin-hd-35` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/HD-35.html) |
| D-35 | `martin-d-35` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/D-35.html) |
| D-41 | `martin-d-41` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/D-41.html) |
| D-42 | `martin-d-42` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/D-42.html) |
| D-45 | `martin-d-45` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/D-45.html) |
| OM-28 | `martin-om-28` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/OM-28.html) |
| OM-42 | `martin-om-42` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/OM-42.html) |
| OM-45 | `martin-om-45` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/OM-45.html) |
| 000-18 | `martin-000-18` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/000-18.html) |
| 000-28 | `martin-000-28` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/000-28.html) |
| 000-42 | `martin-000-42` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/000-42.html) |
| 00-18 | `martin-00-18` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/00-18.html) |
| 00-28 | `martin-00-28` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/00-28.html) |
| J-40 | `martin-j-40` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/J-40.html) |
| SC-18E | `martin-sc-18e` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/SC-18E.html) |
| SC-28E | `martin-sc-28e` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/SC-28E.html) |
| HD12-28 | `martin-hd12-28` | New | partial | [Martin](https://www.martinguitar.com/guitars/standard-series/HD12-28.html) |

## PRS — 20 models

| Model | Stable ID | Origin | Status | Manufacturer source |
|---|---|---|---|---|
| SE Custom 24 | `prs-se-custom-24` | Retained | partial | [PRS](https://prsguitars.com/electrics/model/se_custom_24) |
| SE McCarty 594 Singlecut | `prs-se-mccarty-594-singlecut` | New | partial | [PDF p. 3 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE McCarty 594 | `prs-se-mccarty-594` | New | partial | [PDF p. 3 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE CE 24 | `prs-se-ce-24` | New | partial | [PDF p. 3 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE CE 24 Standard Satin | `prs-se-ce-24-standard-satin` | New | partial | [PDF p. 3 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE Custom 24-08 | `prs-se-custom-24-08` | New | partial | [PDF p. 4 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE Custom 24 Floyd | `prs-se-custom-24-floyd` | New | partial | [PDF p. 4 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE Custom 24 Semi-Hollow Piezo | `prs-se-custom-24-semi-hollow-piezo` | New | partial | [PDF p. 4 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE Swamp Ash Special | `prs-se-swamp-ash-special` | New | partial | [PDF p. 5 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE NF3 | `prs-se-nf3` | New | partial | [PDF p. 5 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE 277 | `prs-se-277` | New | partial | [PDF p. 6 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE Hollowbody Standard | `prs-se-hollowbody-standard` | New | partial | [PDF p. 6 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE Hollowbody Standard Piezo | `prs-se-hollowbody-standard-piezo` | New | partial | [PDF p. 6 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE Hollowbody II Piezo | `prs-se-hollowbody-ii-piezo` | New | partial | [PDF p. 6 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE Silver Sky | `prs-se-silver-sky` | New | partial | [PDF p. 7 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE Zach Myers | `prs-se-zach-myers` | New | partial | [PDF p. 8 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE Santana | `prs-se-santana` | New | partial | [PDF p. 8 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE Mark Holcomb | `prs-se-mark-holcomb` | New | partial | [PDF p. 8 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE Paul's Guitar | `prs-se-paul-s-guitar` | New | partial | [PDF p. 8 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |
| SE DGT | `prs-se-dgt` | New | partial | [PDF p. 8 (2025)](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) |

## Squier — 20 models

| Model | Stable ID | Origin | Status | Manufacturer source |
|---|---|---|---|---|
| Classic Vibe '60s Stratocaster | `squier-classic-vibe-60s-stratocaster` | Retained | partial | [Squier](https://www.fender.com/products/classic-vibe-60s-stratocaster) |
| Affinity Series Telecaster | `squier-affinity-series-telecaster` | New | partial | [Squier](https://www.fender.com/products/affinity-series-telecaster) |
| Affinity Series Stratocaster | `squier-affinity-series-stratocaster` | New | partial | [Squier](https://www.fender.com/products/affinity-series-stratocaster) |
| Affinity Series Jazz Bass | `squier-affinity-series-jazz-bass` | New | partial | [Squier](https://www.fender.com/products/affinity-series-jazz-bass-1) |
| Affinity Series Precision Bass PJ | `squier-affinity-series-precision-bass-pj` | New | partial | [Squier](https://www.fender.com/products/affinity-series-precision-bass-pj-1) |
| Classic Vibe Jaguar Bass | `squier-classic-vibe-jaguar-bass` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-jaguar-bass) |
| Classic Vibe Custom Telecaster SH with Bigsby | `squier-classic-vibe-custom-telecaster-sh-with-bigsby` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-custom-telecaster-sh-with-bigsby) |
| Classic Vibe Custom Esquire | `squier-classic-vibe-custom-esquire` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-custom-esquire) |
| Classic Vibe '50s Stratocaster HT | `squier-classic-vibe-50s-stratocaster-ht` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-50s-stratocaster-ht) |
| Classic Vibe Duo-Sonic HS | `squier-classic-vibe-duo-sonic-hs` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-duo-sonic-hs) |
| Classic Vibe Active '70s Jazz Bass V | `squier-classic-vibe-active-70s-jazz-bass-v` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-active-70s-jazz-bass-v) |
| Classic Vibe Active '70s Jazz Bass | `squier-classic-vibe-active-70s-jazz-bass` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-active-70s-jazz-bass) |
| Classic Vibe '70s Stratocaster HT HSS | `squier-classic-vibe-70s-stratocaster-ht-hss` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-70s-stratocaster-ht-hss) |
| Classic Vibe Telecaster Bass | `squier-classic-vibe-telecaster-bass` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-telecaster-bass) |
| Classic Vibe '50s Precision Bass | `squier-classic-vibe-50s-precision-bass` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-50s-precision-bass) |
| Classic Vibe '70s Telecaster Thinline | `squier-classic-vibe-70s-telecaster-thinline` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-70s-telecaster-thinline) |
| Classic Vibe '60s Mustang | `squier-classic-vibe-60s-mustang` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-60s-mustang) |
| Classic Vibe '60s Telecaster Thinline | `squier-classic-vibe-60s-telecaster-thinline` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-60s-telecaster-thinline) |
| Classic Vibe Baritone Custom Telecaster | `squier-classic-vibe-baritone-custom-telecaster` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-baritone-custom-telecaster) |
| Classic Vibe '70s Telecaster Deluxe | `squier-classic-vibe-70s-telecaster-deluxe` | New | partial | [Squier](https://www.fender.com/products/classic-vibe-70s-telecaster-deluxe) |

## Preserved archived records — excluded from the 200 total

| Model | Original ID | Preserved source |
|---|---|---|
| Gretsch G2420 Streamliner Hollow Body | `gretsch-g2420-streamliner` | [Gretsch](https://www.gretschguitars.com/gear/build/hollow-body/g2420-streamliner-hollow-body-with-chromatic-ii-tailpiece/2817000520) |
| Yamaha C40 Classical | `yamaha-c40` | [Yamaha](https://at.yamaha.com/files/download/brochure/6/330666/YamahaPMDcatalog1314.pdf) |

Complete backups, original IDs, previous published snapshots, original source metadata and legacy source record text remain in [archivedGuitars.json](../src/data/catalog/archivedGuitars.json). The existing raw/reviewed files and Git history are retained. Old detail, Wishlist and shared Compare links resolve archival records with visible labels. Search, active brand counts, catalog pagination and Quiz recommendations exclude them.
