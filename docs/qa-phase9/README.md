# Fretline Phase 9 — ชุดแรก 20 รุ่น

ตรวจเมื่อ **2026-10-20 (UTC)** จาก baseline **`0f00def4f524de10f3f59f711bd43f2d0a50bc8c`** บน `master` โดยต่อยอด repository เดิม ไม่สร้างโปรเจกต์ใหม่

## ผลตรวจและขอบเขต

- ตรวจโครงสร้างข้อมูลในเครื่องครบ **200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 รุ่น** ไม่พบ ID หรือชื่อแบรนด์+รุ่นซ้ำ และไม่เพิ่ม/ลบ/เปลี่ยน ID ชื่อ หรือประเภทของรุ่นใด
- เปิดแหล่งผู้ผลิตเพื่อตรวจซ้ำเฉพาะชุดแรก **20 รุ่น (แบรนด์ละ 2)** ส่วนอีก **180 รุ่นไม่แก้ไขและไม่ได้อ้างว่าได้เปิดตรวจแหล่งข้อมูลใหม่ในรอบนี้**
- ตรวจสเปกรายฟิลด์ใหม่ **174 ช่อง**; เก็บอีก **4 ช่อง** พร้อมหลักฐานรอบเดิมและระบุ `retained` ไม่รวมเป็นช่องที่ตรวจใหม่
- สเปกเปลี่ยน **33 ช่อง** รวมการปรับคำให้ตรงต้นทาง; ในจำนวนนี้ **เติมช่องว่างจริง 11 ช่อง** รายการก่อน/หลังอยู่ใน `audit-summary.json`
- ทั้ง 20 รุ่นยังคง **partial**; **0 รุ่นได้รับสถานะ fully verified** ทั้งฐานข้อมูลยังเป็น partial 200 / sample 0 / verified 0
- เพิ่มภาพจริงที่มีสิทธิ์ใช้ **1 ภาพ / 1 รุ่น (Martin D-28)** พร้อม WebP responsive 2 ขนาดย่อย รวมทั้งเว็บมีภาพจริง 2 รุ่นและ Placeholder 198 รุ่น
- ไม่มีราคา รีวิว น้ำหนัก รูป AI หรือโลโก้ที่สร้างขึ้นเพื่อเติมข้อมูล ไม่มี dependencies ใหม่ของแอป

## เกณฑ์ความน่าเชื่อถือ

คงเกณฑ์ `validateGuitar` เดิมใน `scripts/lib/catalog.mjs`: verified ต้องมีสเปกครบทุกช่องบังคับ รวมทั้งน้ำหนัก สี และราคาเงินบาทที่มีหลักฐานแยกจากสเปก การเปิดหน้าได้ HTTP 200 หรือยืนยันชื่อรุ่นได้เพียงอย่างเดียวไม่เพียงพอ จึงไม่เปลี่ยนเกณฑ์เพื่อให้จำนวน verified เพิ่มขึ้น

`field-evidence.json` แยก `checked` (อ่านหลักฐานใหม่), `retained` (คงค่าพร้อม URL/วันที่เดิม) และ `unknown` (ไม่ทราบ) ทุกฟิลด์ที่มีค่าต้องอยู่ใน `source.fields` ค่า null ยังคงแสดง “ไม่ระบุ / Not specified” ผ่านระบบเดิม ราคาแสดงข้อความยังไม่มีข้อมูลราคา ไม่ใช้ราคาต่างประเทศมาแปลงเป็นบาท

เก็บ URL, วันที่เข้าถึง, HTTP status และ SHA-256 ของเนื้อหาที่ได้รับใน `source-retrievals.json` และ `source.evidence` พร้อมข้อความสเปกสั้นที่อ่านได้ใน `field-evidence.json` ไม่เก็บ HTML/PDF ทั้งฉบับของผู้ผลิตไว้ใน repository ไฟล์ต้นทางอาจเปลี่ยนในอนาคต จึงบันทึก hash ของฉบับที่ใช้ตรวจ ไม่ได้อ้างว่า hash จะเหมือนเดิมเมื่อเปิดภายหลัง

## กีตาร์ที่เลือกและสเปกโครงสร้าง

วันที่เข้าถึงแหล่ง S1–S19 ทุกแหล่ง: **2026-10-20** ตารางนี้แสดงสเปกที่มีหลักฐาน ไม่ยืนยันราคา/น้ำหนัก ทั้งหมดมีสถานะ **partial**

| แบรนด์ / รุ่น | Body / Top / Back / Sides | Neck / Fingerboard | Scale ตามผู้ผลิต | เฟรต | สาย | แหล่ง |
|---|---|---|---|---:|---:|---|
| Yamaha FG800 Dreadnought | Dreadnought Style; Solid Spruce top; Nato/Okume back; Nato/Okume sides | Nato / Rosewood or Walnut | 25.59 in / 650 mm | Not specified | Not specified | S1 |
| Yamaha FG830 | Dreadnought Style; Solid Spruce top; Rosewood back; Rosewood sides | Nato / Rosewood | 25.59 in / 650 mm | Not specified | Not specified | S1 |
| Fender American Professional II Stratocaster | Alder or roasted pine (varies by finish) | Maple / Maple or rosewood (varies by version) | 25.5 in / 648 mm | 22 | 6 (หลักฐานเดิม) | S2 |
| Fender Player II Telecaster | Chambered Ash / Alder / Chambered Mahogany | Maple / Maple / Slab Rosewood | 25.5 in / 648 mm | 22 | Not specified | S3 |
| Squier Classic Vibe '60s Stratocaster | Nyatoh | Maple / Indian laurel | 25.5 in / 648 mm | 21 | 6 (หลักฐานเดิม) | S4 |
| Squier Affinity Series Telecaster | Poplar | Maple / Maple / Indian Laurel | 25.5 in / 648 mm | 21 | Not specified | S5 |
| Gibson Les Paul Standard 60s | Mahogany with AA figured maple top | Mahogany; SlimTaper profile / Rosewood | 24.75 in / 628.65 mm | 22 | 6 | S6 |
| Gibson J-45 Standard | Top: Sitka Spruce; Back: Mahogany; Sides: Mahogany | Mahogany; SlimTaper profile / Rosewood | 24.75 in / 628.65 mm | 20 | 6 | S7 |
| Epiphone Casino Hollowbody | Layered maple; hollowbody | Mahogany; SlimTaper 60s C / Laurel | 24.75 in / 628.65 mm | 22 | 6 | S8 |
| Epiphone Les Paul Standard 50s | Okoume (Gaboon mahogany) or Sapelli; maple cap with AAA flame maple veneer | Mahogany; 1959 Rounded Medium C / Laurel | 24.75 in / 628.65 mm | 22 | 6 | S9 |
| Ibanez RG550 Genesis | Basswood | Super Wizard; 5-piece maple/walnut / Maple | 25.5 in / 648 mm | 24 | 6 | S10 |
| Ibanez SR300E Bass | Okoume | SR4; 5-piece maple/walnut / Jatoba | 34 in / 864 mm | 24 | 4 | S11 |
| Taylor 214ce Grand Auditorium | Torrefied spruce top; layered walnut back and sides; Grand Auditorium | Neo-tropical mahogany / West African Crelicam ebony | 25.5 in | Not specified | 6 | S12 |
| Taylor GS Mini Mahogany | Solid mahogany top; layered sapele back and sides | Mahogany / West African Crelicam ebony | 23.5 in | Not specified | Not specified | S13 |
| Martin D-18 Dreadnought | Spruce top; Mahogany back and sides | Select hardwood; GE Modified Low Oval; High Performance Taper / Ebony | 25.4 in | 20 | Not specified | S14 |
| Martin D-28 | Spruce top; East Indian Rosewood back and sides | Select hardwood; GE Modified Low Oval; High Performance Taper / Ebony | 25.4 in | 20 | Not specified | S15 |
| PRS SE Custom 24 | Mahogany back; maple top with flame maple veneer | Maple; Wide Thin profile / Rosewood | 25 in | 24 | 6 (หลักฐานเดิม) | S16 |
| PRS SE McCarty 594 Singlecut | Maple top with flame maple veneer; mahogany back | Mahogany; Pattern Vintage profile / Rosewood | 24.594 in | 22 | Not specified | S17 |
| Córdoba C5 Classical | Solid western red cedar top; mahogany back and sides | Mahogany / Rosewood | 25.6 in / 650 mm | 19 | 6 | S18 |
| Córdoba C7 CD | Solid western red cedar top; rosewood back and sides | Mahogany / Rosewood | 25.6 in / 650 mm | 19 | 6 | S19 |

ค่าหน่วย mm และนิ้วเก็บตามความละเอียดที่ผู้ผลิตแสดง จึงอาจไม่เท่ากันเป๊ะเมื่อแปลงหน่วย เช่น Yamaha/Córdoba 650 mm และค่าปัดเศษนิ้ว การเปรียบเทียบใช้ mm เป็นหลักเมื่อมี ไม่เดาค่า mm เพิ่มให้รุ่นที่หน้าผู้ผลิตระบุเพียงนิ้ว

## Pickups, Bridge และ Controls

| แบรนด์ / รุ่น | Pickups / Electronics | Bridge | Controls |
|---|---|---|---|
| Yamaha FG800 Dreadnought | None | Rosewood or Walnut | None |
| Yamaha FG830 | None | Rosewood | None |
| Fender American Professional II Stratocaster | 3 × V-Mod II single-coil Stratocaster | 2-point synchronized tremolo; bent-steel saddles; pop-in arm | Master volume, 2 tone controls, 5-way blade selector |
| Fender Player II Telecaster | Neck: Player Series Alnico 5 Tele Single-Coil; Bridge: Player Series Alnico 5 Tele Single-Coil | 6-Saddle String-Through-Body Tele with Block Steel Saddles | Master volume, master tone, 3-way blade selector |
| Squier Classic Vibe '60s Stratocaster | 3 × Fender-Designed Alnico single-coil | 6-saddle vintage-style synchronized tremolo | Master volume, 2 tone controls, 5-way blade selector |
| Squier Affinity Series Telecaster | Neck: Ceramic Single-Coil; Bridge: Ceramic Single-Coil | 6-Saddle Strings-Through-Body Tele | Master volume, master tone, 3-way blade selector |
| Gibson Les Paul Standard 60s | 2 × 60s Burstbucker humbuckers | ABR-1 Tune-O-Matic | 2 volume, 2 tone, 3-way selector |
| Gibson J-45 Standard | Under Saddle Pickup: Baggs VTC | Traditional Belly Up | Soundhole-mounted volume and tone |
| Epiphone Casino Hollowbody | 2 × Epiphone P-90 PRO | LockTone Tune-O-Matic | 2 volume, 2 tone, 3-way toggle |
| Epiphone Les Paul Standard 50s | ProBucker 1 (neck), ProBucker 2 (bridge) | Epiphone LockTone Tune-O-Matic | 2 volume, 2 tone; CTS pots, 50s wiring, 3-way toggle |
| Ibanez RG550 Genesis | V7 (neck H), S1 (middle S), V8 (bridge H) | Edge locking tremolo | Volume, tone, 5-way selector (หลักฐานเดิม) |
| Ibanez SR300E Bass | 2 × PowerSpan Dual Coil | Accu-cast B120 | Volume, pickup balance, 3-band EQ, 3-way Power Tap |
| Taylor 214ce Grand Auditorium | Expression System 2 | West African Crelicam ebony | Not specified |
| Taylor GS Mini Mahogany | No electronics | West African Crelicam ebony | Not specified |
| Martin D-18 Dreadnought | No electronics | Ebony; Golden Era Modern Belly; drop-in saddle | Not specified |
| Martin D-28 | No electronics | Ebony; Golden Era Modern Belly; drop-in saddle | Not specified |
| PRS SE Custom 24 | 2 × PRS 85/15 S humbuckers | PRS Patented Tremolo | Volume, push/pull tone, 3-way blade selector |
| PRS SE McCarty 594 Singlecut | 58/15 LT S neck and bridge | PRS two-piece bridge | 2 volume, 2 push/pull tone controls, 3-way toggle on upper bout |
| Córdoba C5 Classical | None (manufacturer N/A) | Rosewood | None (manufacturer N/A) |
| Córdoba C7 CD | None (manufacturer N/A) | Rosewood | None (manufacturer N/A) |

## แหล่งอ้างอิง

- **S1** — Yamaha FG800, Yamaha FG830: https://my.yamaha.com/en/musical-instruments/guitars-basses-amps/products/acoustic-guitars/fg-series/fg-800/specs.html · เข้าถึง 2026-10-20
- **S2** — Fender American Professional II Stratocaster: https://eu.fender.com/products/american-professional-ii-stratocaster · เข้าถึง 2026-10-20
- **S3** — Fender Player II Telecaster®: https://www.fender.com/products/player-ii-telecaster · เข้าถึง 2026-10-20
- **S4** — Squier Classic Vibe '60s Stratocaster: https://www.fender.com/products/classic-vibe-60s-stratocaster · เข้าถึง 2026-10-20
- **S5** — Squier Affinity Series® Telecaster®: https://www.fender.com/products/affinity-series-telecaster · เข้าถึง 2026-10-20
- **S6** — Gibson Les Paul Standard 60s, Bourbon Burst: https://www.gibson.com/products/gibson-les-paul-standard-60s-figured-top-bourbon-burst · เข้าถึง 2026-10-20
- **S7** — Gibson Gibson J-45 Standard, Vintage Sunburst: https://www.gibson.com/products/gibson-j-45-standard-vintage-sunburst-rs45vsn19 · เข้าถึง 2026-10-20
- **S8** — Epiphone Casino, Natural: https://www.gibson.com/products/epiphone-casino-natural · เข้าถึง 2026-10-20
- **S9** — Epiphone Les Paul Standard 50s, Bourbon Burst — Laurel: https://www.gibson.com/products/epiphone-les-paul-standard-50s-bourbon-burst · เข้าถึง 2026-10-20
- **S10** — Ibanez RG550 — Genesis Collection: https://www.ibanez.com/usa/products/detail/rg550_00_04.html · เข้าถึง 2026-10-20
- **S11** — Ibanez SR300E (Asia product page): https://www.ibanez.com/asia/products/detail/sr300e_1p_05.html · เข้าถึง 2026-10-20
- **S12** — Taylor 214ce — current C-Class model: https://www.taylorguitars.com/guitars/acoustic/214ce · เข้าถึง 2026-10-20
- **S13** — Taylor GS Mini Mahogany (no electronics): https://www.taylorguitars.com/guitars/acoustic/gs-mini-mahogany · เข้าถึง 2026-10-20
- **S14** — Martin D-18 Standard — current GE specifications: https://www.martinguitar.com/guitars/standard-series/D-18.html · เข้าถึง 2026-10-20
- **S15** — Martin D-28: https://www.martinguitar.com/guitars/standard-series/D-28.html · เข้าถึง 2026-10-20
- **S16** — PRS SE Custom 24 — 2025 catalog: https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067#page=4 · เข้าถึง 2026-10-20
- **S17** — PRS SE MCCARTY 594 SINGLECUT — 2025 catalog: https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067#page=3 · เข้าถึง 2026-10-20
- **S18** — Córdoba C5 — Cedar: https://cordobaguitars.com/iberia/c5 · เข้าถึง 2026-10-20
- **S19** — Córdoba C7 CD: https://cordobaguitars.com/iberia/c7-cd · เข้าถึง 2026-10-20

## ข้อจำกัดรุ่นย่อยที่ต้องอ่านประกอบ

- **Yamaha FG800 Dreadnought**: อ่านคอลัมน์ FG800 และ FG830 แยกกันในตาราง FG/FS800 ของ Yamaha Malaysia; คงตัวเลือกไม้ “or” ตามผู้ผลิต ไม่อนุมานจำนวนเฟรตหรือสายจากรูปภาพ
- **Yamaha FG830**: อ่านคอลัมน์ FG800 และ FG830 แยกกันในตาราง FG/FS800 ของ Yamaha Malaysia; คงตัวเลือกไม้ “or” ตามผู้ผลิต ไม่อนุมานจำนวนเฟรตหรือสายจากรูปภาพ
- **Fender American Professional II Stratocaster**: หน้า Fender รวมหลายสีและฟิงเกอร์บอร์ด จึงเก็บตัวเลือกตามรุ่นย่อย ไม่อ้างว่าไม้ทุกตัวเลือกอยู่ในกีตาร์ตัวเดียว; จำนวนสายคงหลักฐานรอบเดิม ไม่อนุมานจากช่วงเบอร์สาย
- **Fender Player II Telecaster**: ตารางสเปกรวมหลายสี/วัสดุ เก็บตัวเลือกตามผู้ผลิต ไม่เลือก SKU หรือวัสดุเพียงค่าเดียวแทนทุกรุ่นย่อย; ไม่อนุมานจำนวนสายจากช่วงเบอร์สาย
- **Squier Classic Vibe '60s Stratocaster**: อ้างอิง Classic Vibe 60s Stratocaster รุ่น Nyatoh/Indian Laurel; ไม่ปะปน Classic Vibe Precision Bass; จำนวนสายคงหลักฐานรอบเดิม
- **Squier Affinity Series Telecaster**: ตารางสเปกรวมหลายสี/วัสดุ เก็บตัวเลือกตามผู้ผลิต ไม่เลือก SKU หรือวัสดุเพียงค่าเดียวแทนทุกรุ่นย่อย; ไม่อนุมานจำนวนสายจากช่วงเบอร์สาย
- **Gibson Les Paul Standard 60s**: อ้างอิง Les Paul Standard 60s Figured Top สี Bourbon Burst ตามหน้าและรหัส LPS600B8NH1; ไม่นำราคาต่างประเทศมาแปลงเป็นราคาไทย
- **Gibson J-45 Standard**: หน้า RS45VSN19 ระบุว่าสินค้ารุ่นอ้างอิงนี้ไม่จำหน่ายแล้วและเก็บไว้เพื่ออ้างอิง สเปกนี้จึงไม่ใช่การยืนยัน J-45 Standard รุ่นผลิตล่าสุด
- **Epiphone Casino Hollowbody**: อ้างอิง Casino Natural รหัส EOCANANH1 ฟิงเกอร์บอร์ด Laurel ไม่ปะปนกับ Casino USA หรือรุ่นย่อยอื่น
- **Epiphone Les Paul Standard 50s**: หน้า EIGLP5BONH1 ระบุว่าไม่จำหน่ายแล้วและเก็บไว้เพื่ออ้างอิง เป็นรุ่น Laurel ไม่แทนด้วยรุ่นใหม่ Rosewood; ตาราง Body Material ระบุ Okoume หรือ Sapelli แม้คำบรรยายใช้คำรวม Mahogany
- **Ibanez RG550 Genesis**: อ้างอิง RG550 Genesis ในเว็บไซต์ Ibanez ปัจจุบัน ไม่ใช้ภาพ RG550 ปีเก่าก่อน Genesis; ปุ่มควบคุมคงหลักฐานรอบเดิมเพราะรอบนี้อ่านตารางและการตั้งสาย ไม่ถอดความแผนผังรูป
- **Ibanez SR300E Bass**: อ้างอิง SR300E รุ่น Okoume/Jatoba/PowerSpan จากหน้า Asia ของ Ibanez; จำนวนสายคำนวณจากการตั้งสายที่ระบุหมายเลข 1–4
- **Taylor 214ce Grand Auditorium**: อ้างอิง 214ce Torrefied Spruce/Layered Walnut ตามหน้าปัจจุบัน ไม่ใช้สเปก Rosewood รุ่นเก่า; จำนวนเฟรตและปุ่มควบคุมยังไม่พบในตารางที่อ่าน
- **Taylor GS Mini Mahogany**: อ้างอิง GS Mini Mahogany เท่านั้น ไม่ปะปน GS Mini Spruce หรือรุ่น -e; ไม่ใช้รีวิวหรือคำถามจากผู้ใช้เป็นสเปก จำนวนเฟรต/สายและปุ่มควบคุมยังไม่ยืนยัน
- **Martin D-18 Dreadnought**: อ้างอิงสเปก Golden Era ของหน้าปัจจุบัน ระบุ Spruce ตามผู้ผลิตโดยไม่เดาชนิดย่อย; จำนวนเฟรตรวม 20 ไม่ใช่ตำแหน่งต่อคอ 14; ไม่อนุมานจำนวนสายจากภาพ
- **Martin D-28**: อ้างอิงสเปก Golden Era ของหน้าปัจจุบัน ระบุ Spruce ตามผู้ผลิตโดยไม่เดาชนิดย่อย; จำนวนเฟรตรวม 20 ไม่ใช่ตำแหน่งต่อคอ 14; ไม่อนุมานจำนวนสายจากภาพ; ภาพเจ้าของ D-28 ปี 2018 แสดงรุ่น D-28 แต่ไม่ใช่ภาพรุ่นสเปก GE ปัจจุบันและไม่ใช้ยืนยันสเปก
- **PRS SE Custom 24**: หน้าเว็บรุ่น SE Custom 24 ตอบ HTTP 403 จึงใช้เอกสารผู้ผลิต PRS ปี 2025 หน้า 4 หัวข้อ SE Custom 24 โดยตรง ไม่ปะปน Floyd/24-08/Quilt; เอกสารไม่ยืนยันคำว่า Multi-ply จึงเหลือ Maple; จำนวนสายคงหลักฐานรอบเดิม
- **PRS SE McCarty 594 Singlecut**: เอกสารผู้ผลิต PRS ปี 2025 หน้า 3 หัวข้อ SE McCarty 594 Singlecut; เป็นสเปกฉบับ 2025 ไม่อ้างว่าเป็นฉบับปี 2026; จำนวนสาย/น้ำหนักและราคาเงินบาทยังไม่ทราบ
- **Córdoba C5 Classical**: อ้างอิงตาราง Córdoba โดยตรง แยก C5/Mahogany กับ C7 CD/Rosewood; เฟรตรวม 19 ไม่ใช่ Frets to Body 12; N/A ของ Electronics/Controls เป็นข้อมูลที่ผู้ผลิตระบุ ไม่ใช่การเดาจากช่องว่าง
- **Córdoba C7 CD**: อ้างอิงตาราง Córdoba โดยตรง แยก C5/Mahogany กับ C7 CD/Rosewood; เฟรตรวม 19 ไม่ใช่ Frets to Body 12; N/A ของ Electronics/Controls เป็นข้อมูลที่ผู้ผลิตระบุ ไม่ใช่การเดาจากช่องว่าง

ระบุ Model Identifier เฉพาะที่พบชัดเจนในหน้าที่ตรวจ: Gibson LPS600B8NH1 / RS45VSN19 และ Epiphone EOCANANH1 / EIGLP5BONH1 รหัสเหล่านี้ระบุรุ่นย่อยของหน้าที่อ้างอิง ไม่ใช่การเปลี่ยน Fretline ID อีก 16 รุ่นใช้ชื่อผู้ผลิตเป็นตัวระบุรุ่นและไม่แต่ง SKU ของรุ่นย่อย

## ภาพและสิทธิ์

เพิ่ม **Martin D-28** ของ **IchiroNakagawa**, ภาพเจ้าของ ถ่าย **11 ธันวาคม 2018**, [แหล่งต้นฉบับ](https://commons.wikimedia.org/wiki/File:Martin_D-28.jpg), [หน้าฉบับที่ตรวจ](https://commons.wikimedia.org/w/index.php?title=File:Martin_D-28.jpg&oldid=1054922929), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) ตรวจสิทธิ์ 2026-10-20 ผู้ถ่ายระบุรุ่น D-28 และตรวจภาพด้านหน้าแล้ว ไม่ทราบปีผลิตเครื่องดนตรี **ไม่ใช่ภาพรุ่นสเปก Golden Era ปัจจุบัน** และไม่ใช้ภาพนี้เป็นหลักฐานสเปก คำอธิบายนี้แสดงใต้ภาพและในเครดิตของเว็บ

แสดงชื่อผู้ถ่าย URL ต้นทาง ใบอนุญาต และรายการปรับไฟล์ในหน้า Detail, Lightbox และ `/image-credits`; ปรับเฉพาะ orientation, ลบ EXIF/GPS, ย่อขนาดโดยไม่ครอป และเข้ารหัส WebP ไม่มีการรีทัช/เปลี่ยนพื้นหลัง/สร้างภาพ AI ไฟล์ดัดแปลงเผยแพร่ภายใต้ CC BY-SA 4.0 เช่นเดียวกัน

| ไฟล์ | ขนาด | ขนาดไฟล์ |
|---|---|---:|
| ภาพหลัก | 1200 × 1594 | 131,458 bytes |
| responsive | 960 × 1275 | 83,140 bytes |
| responsive | 480 × 638 | 20,114 bytes |

ต้นฉบับ JPEG 1,361,844 bytes ไม่ได้ส่งให้เบราว์เซอร์ ภาพหลักเล็กลงประมาณ 90% ใช้ `srcset`, intrinsic dimensions, lazy loading บนการ์ด และ eager เฉพาะภาพหลักตามระบบเดิม SHA-256/ขนาดทุกไฟล์อยู่ใน `imageRights.json` และ `src/assets/guitars/martin-d-28/LICENSE.md`

อีก **19 รุ่นในชุดนี้คง Placeholder** เพราะยังไม่อนุมัติภาพตรงรุ่นพร้อมสิทธิ์ที่เพียงพอ การตรวจครั้งนี้เป็นการค้นหาแบบเจาะชื่อรุ่น ไม่ใช่การรับรองว่าไม่มีภาพใช้ได้ที่ใดในโลก ดู `image-audit.json` สำหรับคำตัดสินทั้ง 20 รุ่นและตัวอย่างที่ปฏิเสธ เช่น RG550 ก่อน Genesis, Fender Telecaster Deluxe แทน Stratocaster และภาพผู้ผลิตที่ไม่มีเส้นทางอนุญาตชัดเจน

## ข้อมูลที่ยังขาดในชุดแรก

| ฟิลด์ | จำนวนรุ่นที่ยังไม่ทราบ |
|---|---:|
| ราคาเงินบาทที่มีหลักฐาน | 20 |
| น้ำหนัก | 20 |
| Controls | 4 |
| เฟรตรวม | 4 |
| จำนวนสาย | 8 |
| ภาพที่อนุมัติสิทธิ์ใช้ได้ | ยังขาด 19 |
| รีวิวที่ยืนยันได้ | 20 |

รวมช่องสเปกหลักที่ยังเป็น null **36 ช่อง** จาก 20 รุ่น (ไม่รวม scaleMm ซึ่งเป็นหน่วยทางเลือก และไม่รวมสี/ราคา/รีวิว) ภาพที่มีอยู่หนึ่งภาพไม่ได้ทำให้ข้อมูลรุ่นนั้นเป็น verified ทั้งรุ่น

## ไฟล์และการรักษาระบบ

- `src/data/catalog/reviewedGuitars.json`: ปรับเฉพาะ override ชุด 20 รุ่น; เก็บ ID/name/category และ source scope เดิมตามหลักฐาน
- `src/data/catalog/imageRights.json`, `src/assets/guitars/martin-d-28/`: ภาพมีสิทธิ์ 1 ภาพ พร้อม responsive derivatives 2 ไฟล์และใบอนุญาต
- `scripts/check-phase9.mjs`, `scripts/lib/phase9.mjs`, `package.json`: ตรวจ batch, หลักฐาน, จำนวน และขอบเขต 180 รุ่นที่ไม่แก้
- `scripts/check-phase6.mjs`, `check-phase7.mjs`, `check-phase8.mjs`: ปรับข้อกำหนดเก่าเรื่องภาพ 1 ภาพ/ข้อมูลห้ามเปลี่ยน ให้รองรับเฉพาะการตรวจ Phase 9 นี้ โดยยังเทียบ 180 รุ่นและภาพเดิมกับ Git baseline
- สคริปต์ Browser Phase 8 สองไฟล์เพิ่มตัวเลือก output directory และ photo ID เพื่อรันซ้ำโดยไม่เขียนทับผลเดิม
- `docs/qa-phase9/`: audit ก่อน/หลัง CSV ครบ 200 รุ่น, CSV สเปกชุด 20, หลักฐาน, log, screenshots และผล Browser
- ไม่แก้ JSX/CSS ของแอป ไม่แก้ Router/ShopContext/Quiz scoring ไม่แตะ archive สองรุ่นเดิม ภาพ Yamaha เดิมและข้อมูลอีก 180 รุ่นไม่เปลี่ยน
- ทดสอบขอบเขตข้อมูลโดยสร้าง effective catalog จาก Git baseline โดยตรง แล้วเปรียบเทียบ ไม่พึ่ง snapshot ที่แก้ได้เพียงอย่างเดียว

## ผลการทดสอบ

ทดสอบบน production build ผ่าน Vite Preview (Chromium/Linux) ผลสุดท้ายอยู่ใน `test-summary.json` และ log ใน `logs/`:

| รายการ | ผล |
|---|---|
| `npm run build` | ผ่าน — Vite 5.4.21, 162 modules |
| `npm run catalog:check` | ผ่าน — 200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 / ไม่พบซ้ำ |
| `npm run images:check -- --write` | ผ่าน — สิทธิ์, SHA-256 และ responsive derivatives ครบ |
| `npm run phase4:check` | 19/19 ผ่าน |
| `npm run phase5:check` | 15/15 ผ่าน |
| `npm run phase6:check` | 21/21 ผ่าน |
| `npm run phase7:check` | 16/16 ผ่าน |
| `npm run phase8:check` | 8/8 และ 10/10 ผ่าน |
| `npm run phase9:check` | 14/14 ผ่าน |
| รวม data/regression assertions | **103/103 ผ่าน** |
| Browser regression เดิม | **54 ข้อผ่าน** — Search, Filters, Sorting, Pagination, Back/Forward, Compare 2–4, ป้องกันซ้ำ, Quiz ครบ/ย้อนแก้/เปิด Detail, Wishlist และ Archive |
| Detail routes | **200/200 เปิดได้** และตารางสเปกทั้ง 20 รุ่นตรงกับข้อมูลที่ตรวจ |
| Browser batch เพิ่มเติม | **12 ข้อผ่าน** — ภาพ D-28, srcset, lazy loading, เครดิต, Lightbox/keyboard, Wishlist/Compare, Image Credits และ fallback เมื่อจงใจบล็อกภาพ |
| Responsive | **50/50 ผ่าน** — 10 หน้าทดสอบ × 1440 / 1024 / 768 / 390 / 320 px ไม่มี document overflow หรือภาพเสีย |
| Console / Runtime / failed requests ใน normal flows | **0 / 0 / 0** |
| `git diff --check` | ผ่าน |

**ยังไม่ได้ทดสอบ Safari บน iPad จริง** การทดสอบ Chromium ที่ขนาดจอเดียวกันไม่ใช่การรับรอง Safari แท้ ไม่มีการเปลี่ยน JSX/CSS ของแอป

ช่วงแรก sandbox ปฏิเสธการเรียก Git จาก Node และการเปิดพอร์ตในเครื่อง (EPERM) จึงรันใหม่ด้วยสิทธิ์เครือข่ายของ environment ที่จำเป็นและผ่านทั้งหมด สคริปต์ Browser ใหม่เลือก status note สองตัวและหารูปภายในตารางสเปกผิดตำแหน่ง ได้แก้ selector แล้ว ผลด้านบนเป็นรอบสุดท้ายที่ผ่านครบ ต่อมาปรับการเรียก Git ภายในชุดทดสอบให้ไม่เปิด stdin ที่ไม่จำเป็น จึงทดสอบ Phase 6–9 ใน sandbox เดิมได้โดยไม่ต้องใช้สิทธิ์เครือข่าย และแก้ชื่อฉบับอ้างอิง SE Custom 24 ให้ตรงเอกสาร PRS 2025 จากนั้น Build/Catalog/Images/Phase 6–9 ผ่านอีกครั้ง

เปิด `npm run preview -- --host 127.0.0.1 --port 4199` แล้วใช้ Browser commands เหล่านี้ (ต้องมี Python Playwright และ Chromium ใน environment):

```bash
FRETLINE_QA_URL=http://127.0.0.1:4199 FRETLINE_QA_OUTPUT="$PWD/docs/qa-phase9" FRETLINE_QA_REPORT=browser-regression-results.json python docs/qa-phase8/browser-phase8.py
FRETLINE_QA_URL=http://127.0.0.1:4199 python docs/qa-phase9/browser-batch.py
FRETLINE_QA_URL=http://127.0.0.1:4199 FRETLINE_QA_OUTPUT="$PWD/docs/qa-phase9" FRETLINE_QA_PHOTO=martin-d-28 python docs/qa-phase8-review/responsive.py
```

Screenshots **53 ภาพ** อยู่โฟลเดอร์นี้ เช่น [Desktop](photo-detail-1440.png), [Tablet 1024](photo-detail-1024.png), [Tablet 768](photo-detail-768.png), [Mobile 390](photo-detail-390.png), [Mobile 320](photo-detail-320.png), [Catalog](catalog-1440.png), [Compare](compare-390.png), [Quiz results](quiz-results-390.png)

## เปิดเวอร์ชันล่าสุดใน Codespaces บน iPad

เปิด repository เดิมบน Safari → Code → Codespaces → เลือก Codespace เดิม แล้วใช้ Terminal:

```bash
git status
git checkout master
git pull --ff-only origin master
npm ci
npm run dev -- --host 0.0.0.0 --port 5173
```

หากมีไฟล์แก้ค้างอยู่ ให้เก็บงานนั้นก่อน pull และอย่าใช้ reset --hard จากนั้นเปิดแท็บ **Ports → 5173 → Open in Browser** เลือกคง port เป็น Private แล้วลงชื่อเข้า GitHub บน Safari ใช้ URL ที่ Codespaces แสดงจริง ไม่ใช่ localhost ของ iPad

จบเฉพาะชุดแรก 20 รุ่น รอคำสั่งก่อนดำเนินการอีก 180 รุ่นหรือ Phase ถัดไป
