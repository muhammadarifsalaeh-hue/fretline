# Phase 6 — Data and source register

Reviewed on **2026-10-20** against the existing 36-model catalog. All stable IDs, routes, brands, categories and order are retained. This is a field-scoped review, not certification of every production year, finish or instrument.

## Coverage and limitations

- 36 models / 11 brands, all **partial**; 0 fully verified.
- Main evidence: 33 records read via HTTP, 1 via the browser/web reader (PRS), 2 via manufacturer search-index excerpts (Gretsch G2420, archived Yamaha C40). These counts are models, not unique URLs.
- 19 distinct main/supplemental URLs are recorded. Main and supplemental sources must be interpreted within each record’s declared field scope.
- 36 unknown THB prices, no verified reviews, 36 unknown instrument weights. Foreign-currency prices were not converted or presented as THB.
- 1 accepted model photo, 2 responsive derivatives; 35 models retain labelled placeholders.
- `source.verifiedOn` records when the stated evidence was checked; it does not change a `partial` record to `verified`.

## Missing spec fields

A known “None” for electronics is different from an unknown `null`. Scale length is recorded in original mm when supplied; inch equivalents are rounded only for display.

| Field | Models still missing |
|---|---|
| `body` | 0 |
| `neck` | 0 |
| `fretboard` | 0 |
| `pickups` | 2 |
| `bridge` | 2 |
| `controls` | 6 |
| `scale` | 0 |
| `frets` | 22 |
| `strings` | 23 |
| `weightKg` | 36 |

## Manufacturer sources by model

Each source applies to the stated edition/variant. All prices and review scores remain unknown regardless of spec coverage. See [effective values](qa-phase6/audit-after.json) and [field-level source register](qa-phase6/source-register.json) for the exact supported fields.

| Stable ID | Manufacturer model / edition | Access | Source | Remaining spec gaps |
|---|---|---|---|---|
| `fender-american-professional-ii-stratocaster` | American Professional II Stratocaster | http | [Fender](https://eu.fender.com/products/american-professional-ii-stratocaster) | weightKg |
| `gibson-les-paul-standard-60s` | Les Paul Standard 60s, Bourbon Burst | http | [Gibson](https://www.gibson.com/products/gibson-les-paul-standard-60s-figured-top-bourbon-burst) | weightKg |
| `ibanez-rg550-genesis` | RG550 — Genesis Collection | http | [Ibanez](https://www.ibanez.com/usa/products/detail/rg550_00_04.html) | weightKg |
| `yamaha-pacifica-612viifm` | PAC612VIIFM | http | [Yamaha](https://ph.yamaha.com/en/musical-instruments/guitars-basses-amps/products/electric-guitars/pacifica/specs.html) | strings, weightKg |
| `prs-se-custom-24` | SE Custom 24 — 2026 page | web-page | [PRS](https://prsguitars.com/electrics/model/se_custom_24) | weightKg |
| `epiphone-casino` | Casino, Natural | http | [Epiphone](https://www.gibson.com/products/epiphone-casino-natural) | weightKg |
| `taylor-214ce` | 214ce — current C-Class model | http | [Taylor](https://www.taylorguitars.com/guitars/acoustic/214ce) | controls, frets, weightKg |
| `martin-d-18` | D-18 Standard — current GE specifications | http | [Martin](https://www.martinguitar.com/guitars/all-guitars/D-18.html) | controls, strings, weightKg |
| `yamaha-fg800` | FG800 | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `cordoba-c5` | C5 — Cedar | http | [Córdoba](https://cordobaguitars.com/iberia/c5) | pickups, bridge, weightKg |
| `fender-player-ii-jazz-bass` | Player II Jazz Bass | http | [Fender](https://www.fender.com/products/player-ii-jazz-bass) | controls, weightKg |
| `ibanez-sr300e` | SR300E (Asia product page) | http | [Ibanez](https://www.ibanez.com/asia/products/detail/sr300e_1p_05.html) | weightKg |
| `squier-classic-vibe-60s-stratocaster` | Classic Vibe '60s Stratocaster | http | [Squier](https://www.fender.com/products/classic-vibe-60s-stratocaster) | weightKg |
| `gretsch-g2420-streamliner` | G2420 Streamliner with Chromatic II, Village Amber — 2817000520 | search-index | [Gretsch](https://www.gretschguitars.com/gear/build/hollow-body/g2420-streamliner-hollow-body-with-chromatic-ii-tailpiece/2817000520) | bridge, strings, weightKg |
| `epiphone-les-paul-standard-50s` | Les Paul Standard 50s, Bourbon Burst — Laurel | http | [Epiphone](https://www.gibson.com/products/epiphone-les-paul-standard-50s-bourbon-burst) | weightKg |
| `taylor-gs-mini` | GS Mini Mahogany (no electronics) | http | [Taylor](https://www.taylorguitars.com/guitars/acoustic/gs-mini-mahogany) | controls, frets, strings, weightKg |
| `yamaha-c40` | C40 — Yamaha Europe 2013–2014 catalog | search-index | [Yamaha](https://at.yamaha.com/files/download/brochure/6/330666/YamahaPMDcatalog1314.pdf) | pickups, controls, frets, strings, weightKg |
| `fender-player-precision-bass` | Player II Precision Bass | http | [Fender](https://www.fender.com/products/player-ii-precision-bass) | controls, weightKg |
| `yamaha-fg850` | FG850 | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fg840` | FG840 | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fg830` | FG830 | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fg820` | FG820 | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fg820-12` | FG820-12 | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, weightKg |
| `yamaha-fg820l` | FG820L | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fg800j` | FG800J | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fg800m` | FG800M | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fs850` | FS850 | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fs830` | FS830 | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fs820` | FS820 | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fs800` | FS800 | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fgx830c` | FGX830C | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fgx820c` | FGX820C | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fgx800c` | FGX800C | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fsx830c` | FSX830C | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fsx820c` | FSX820C | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |
| `yamaha-fsx800c` | FSX800C | http | [Yamaha](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html) | frets, strings, weightKg |

## Model/edition caveats

Do not combine specs across production years or variants. The unchanged display names and IDs are catalog identifiers; the manufacturer edition below defines which facts were checked.

- **Fender American Professional II Stratocaster** (`fender-american-professional-ii-stratocaster`): หน้าผู้ผลิตมีหลายสีและฟิงเกอร์บอร์ด วัสดุลำตัว Alder/Roasted Pine และฟิงเกอร์บอร์ด Maple/Rosewood ขึ้นกับตัวเลือก ไม่เหมารวมว่าเป็นสเปกของทุกสี
- **Gibson Les Paul Standard 60s** (`gibson-les-paul-standard-60s`): อ้างอิง Standard 60s Figured Top สี Bourbon Burst ไม่รวมรุ่น Faded, Plain Top หรือรุ่นสั่งทำ
- **Ibanez RG550 Genesis** (`ibanez-rg550-genesis`): อ้างอิง RG550 Genesis Collection ปัจจุบัน ไม่ใช้สเปก RG550 รุ่นดั้งเดิมหรือรุ่นปีอื่น
- **Yamaha Pacifica 612VIIFM** (`yamaha-pacifica-612viifm`): อ้างอิงคอลัมน์ PAC612VIIFM เท่านั้น ไม่ใช้ PAC612VIIFMX/PAC612VII และคง ID Pacifica เดิม
- **PRS SE Custom 24** (`prs-se-custom-24`): ตรวจอ่านหน้าผู้ผลิตผ่าน Web tool; การดาวน์โหลดโดยตรงได้ HTTP 403 ไม่ใช้สเปกรุ่น Core Custom 24 หรือรุ่น Floyd
- **Epiphone Casino Hollowbody** (`epiphone-casino`): อ้างอิง Casino Natural รุ่นมาตรฐาน ไม่รวม USA Casino, Casino Coupe, รุ่น Vibrato หรือรุ่น Rosewood ใหม่ที่เป็นคนละหน้าสินค้า
- **Taylor 214ce Grand Auditorium** (`taylor-214ce`): อ้างอิง 214ce ปัจจุบันที่ใช้ C-Class Bracing ไม่ใช้ Layered Rosewood/Sapele จากตัวอย่างรุ่นเก่า และไม่เดาจำนวนเฟรต
- **Martin D-18 Dreadnought** (`martin-d-18`): อ้างอิง D-18 Standard รุ่นปรับปรุงปัจจุบัน ไม่ใช้รุ่น Custom Shop, Authentic หรือรุ่นสั่งทำ
- **Yamaha FG800 Dreadnought** (`yamaha-fg800`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ คำค้น beginner อ้างอิงการจัดวางรุ่นโดยผู้ผลิตในหน้า Lineup ไม่ใช่ผลรีวิว
- **Córdoba C5 Classical** (`cordoba-c5`): อ้างอิง C5 Cedar ไม่ใช้ C5 SP, C5-CE หรือรุ่น Limited ช่อง Bridge/Pickups ที่ยังไม่ได้ตรวจข้อความชัดเจนเว้นว่าง คำค้น nylon/beginner มาจากคำอธิบายรุ่นสำหรับผู้เริ่มเล่นของผู้ผลิต ไม่ใช่คะแนนรีวิว
- **Fender Player II Jazz Bass** (`fender-player-ii-jazz-bass`): ฟิงเกอร์บอร์ด Maple หรือ Slab Rosewood ตามรุ่นย่อย; คง ID เดิมแม้ ID ของ Precision Bass ไม่ได้มีคำว่า II
- **Ibanez SR300E Bass** (`ibanez-sr300e`): อ้างอิงหน้ารุ่น sr300e_1p_05 สำหรับภูมิภาค Asia วัสดุของรุ่นปีเก่าอาจต่างกัน ไม่ใช้ข้อมูล PJ/Mahogany/Jatoba neck จากตัวอย่างเดิม
- **Squier Classic Vibe '60s Stratocaster** (`squier-classic-vibe-60s-stratocaster`): อ้างอิงหน้า Classic Vibe ’60s Stratocaster ปัจจุบันของ Fender; ไม่ใช้ Poplar จากข้อมูลตัวอย่างเดิม
- **Gretsch G2420 Streamliner Hollow Body** (`gretsch-g2420-streamliner`): ตรวจจากข้อความหน้า Gretsch ที่ระบบค้นหาดัชนีไว้ หน้าโดยตรงตอบ 403 ใช้เฉพาะฟิลด์ที่อ่านได้ ไม่ยืนยันสเปก Bridge หรือจำนวนสายจากข้อมูลเดิม
- **Epiphone Les Paul Standard 50s** (`epiphone-les-paul-standard-50s`): ใช้ตารางรายละเอียดของหน้า Bourbon Burst รุ่น Laurel ซึ่งระบุไม้ลำตัว Okoume หรือ Sapelli ไม่ใช้สเปกรุ่น Rosewood ที่ชื่อใกล้กัน
- **Taylor GS Mini Mahogany** (`taylor-gs-mini`): อ้างอิง GS Mini Mahogany แบบไม่มี e ไม่ใช้ GS Mini Spruce หรือ GS Mini-e จำนวนเฟรต/สายที่ไม่ระบุในตารางยังเว้นว่าง
- **Yamaha C40 Classical** (`yamaha-c40`): อ้างอิงแคตตาล็อกย้อนหลัง 2013–2014 ที่ระบบค้นหาดัชนีไว้เท่านั้น ดาวน์โหลด PDF โดยตรงได้ 403 ไม่ใช้ตาราง C40II/CX40 ปัจจุบันแทนรุ่น C40 และไม่อ้างว่ายังวางจำหน่าย
- **Fender Player II Precision Bass** (`fender-player-precision-bass`): ฟิงเกอร์บอร์ด Maple หรือ Slab Rosewood ตามรุ่นย่อย; คง ID เดิมแม้ ID ของ Precision Bass ไม่ได้มีคำว่า II
- **Yamaha FG850** (`yamaha-fg850`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FG840** (`yamaha-fg840`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FG830** (`yamaha-fg830`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FG820** (`yamaha-fg820`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FG820-12** (`yamaha-fg820-12`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FG820L** (`yamaha-fg820l`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ หน้า Lineup ระบุ Lefty Model จึงใช้คำค้น left-handed; ไม่ใช้ข้อความเปรียบว่าเป็น FG800 แทนสเปกคอลัมน์ FG820L
- **Yamaha FG800J** (`yamaha-fg800j`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ คำค้น beginner อ้างอิงการจัดวางรุ่นโดยผู้ผลิตในหน้า Lineup ไม่ใช่ผลรีวิว
- **Yamaha FG800M** (`yamaha-fg800m`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FS850** (`yamaha-fs850`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FS830** (`yamaha-fs830`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FS820** (`yamaha-fs820`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FS800** (`yamaha-fs800`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FGX830C** (`yamaha-fgx830c`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FGX820C** (`yamaha-fgx820c`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FGX800C** (`yamaha-fgx800c`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FSX830C** (`yamaha-fsx830c`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FSX820C** (`yamaha-fsx820c`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ
- **Yamaha FSX800C** (`yamaha-fsx800c`): อ้างอิงตาราง FG/FS800 ของ Yamaha Malaysia วัสดุที่ระบุ “or” อาจต่างกันตามช่วงผลิต ไม่เดาจำนวนเฟรต น้ำหนัก หรือราคาที่ไม่มีในตาราง ค่า scale นิ้วคำนวณจาก mm ที่ผู้ผลิตระบุ

## Supplemental evidence

The Yamaha FG/FS800 [lineup](https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/lineup.html), read through the web reader on 2026-10-20, explicitly identifies FG820-12 as twelve-string, FG820L as left-handed, and FG800/FG800J as beginner-oriented. The FG820L prose refers to FG800; its wood specifications are taken from the FG820L **specification column**, not inherited from FG800. Malaysian RM prices on this page are excluded.

## Important corrections

- Ibanez SR300E: current referenced Asia page lists **Okoume**, a maple/walnut neck, Jatoba fingerboard and PowerSpan dual-coil pickups, replacing unrelated demo values.
- Taylor GS Mini Mahogany: mahogany top, not the inherited spruce demo top. Current 214ce uses torrefied spruce/layered walnut; it is labelled as the current C-Class version.
- PRS SE Custom 24: 2026 page specifies 85/15 **S** pickups; this is not a claim about every older SE Custom 24. Direct fetch returned 403; the web reader exposed the full page.
- Squier Classic Vibe ’60s Stratocaster: current referenced body material is Nyatoh, not the old Poplar demo value.
- Fender Player II Jazz Bass uses two single-coil pickups, not a split-coil demo description. American Professional II body/fingerboard alternatives remain alternatives, not a guessed finish.
- Gretsch G2420: 24.75-inch scale and the stated BT-3S variant are supported by manufacturer search-index text. The full page returned 403; bridge, strings and weight remain unknown.
- Yamaha C40: only the archived **2013–2014** manufacturer catalog excerpt was readable. Full PDF access returned 403. Current C40II/CX40 tables are not used as C40 evidence; current availability is not asserted.
- Yamaha FG/FS800 table: read each model column independently, preserving “Rosewood or Walnut” options, 634/650 mm values and unknown fret counts rather than applying generic acoustic defaults.

## Image source and rights

Only the Yamaha FG820-12 owner photograph by **Peternick2468** was accepted: [Wikimedia Commons source](https://commons.wikimedia.org/wiki/File:12_string_Yamaha_acoustic_guitar.jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), checked 2026-10-20. The author identifies the twelve-string model, but only **six strings are fitted in this photograph**; that limitation is visible in the gallery caption. This is not a manufacturer studio image.

Changes: EXIF orientation, resize, WebP encoding only. No cropping, retouching, background removal or AI modification. The code is not relicensed by the photo license; source and responsive image derivatives retain CC BY-SA 4.0.

| Delivered file | Dimensions | Bytes |
|---|---|---|
| `src/assets/guitars/yamaha-fg820-12/01-front.webp` | 1200 × 1600 | 168,650 |
| `src/assets/guitars/yamaha-fg820-12/responsive/01-front-480.webp` | 480 × 640 | 38,716 |
| `src/assets/guitars/yamaha-fg820-12/responsive/01-front-960.webp` | 960 × 1280 | 115,424 |

Photo review/rejections: [image-review.json](qa-phase6/image-review.json). Author, original source, reuse terms, model-match notes, hashes and transformations are in [imageRights.json](../src/data/catalog/imageRights.json) and [the image license file](../src/assets/guitars/yamaha-fg820-12/LICENSE.md). A global footer link opens `/image-credits`, with additional credit under Detail/Lightbox images.

The Casino VT photograph was rejected because a vibrato variant does not match the catalog’s standard Casino. Another Casino photo was too small, and the C40 candidate showed only a soundhole detail. Manufacturer images were not copied merely because they were publicly visible.

## Reproducible evidence

- [Before audit](PHASE_6_AUDIT_BEFORE.md) and [before snapshot](qa-phase6/audit-before.json). Historical demo amounts in that snapshot are explicitly unverified; the snapshot is documentation, not application input.
- [After snapshot](qa-phase6/audit-after.json), [summary](qa-phase6/audit-summary.json), [source register](qa-phase6/source-register.json), [HTTP retrieval outcomes](qa-phase6/source-retrievals.json).
- Retrieved manufacturer HTML and full copyrighted source pages are not redistributed in the repository. The register records factual fields, URLs, dates and edition caveats.
- A successful catalog/image check validates structure and recorded evidence; it does not grant new photo rights or independently authenticate every fact.

## Remaining content work

Obtain Thai price sources with dates/currency, missing spec evidence and matching photo permissions. Recheck the two index-only sources against their complete official documents before treating those fields as full-page verified. Keep all unresolved fields null and leave the current partial statuses intact. This delivery does not begin Phase 7.
