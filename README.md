> Latest update: [Pacifica color gallery — เปิดใน Codespaces บน iPad](docs/PACIFICA_PREVIEW_CODESPACES.md). ใส่ภาพที่ผู้ใช้จัดหาครบ 4 ภาพแล้ว เปิดด้วย `npm run dev` ได้ทันที พร้อมเลือกสีดำ แดง ฟ้าอมเขียว และดูภาพรวม ราคาแนะนำ Yamaha ประเทศไทย 34,000 บาท

> Previous delivery: [Phase 9 — first 20-model evidence review](docs/qa-phase9/README.md). Two models per brand rechecked against manufacturer specifications, field-level evidence and one additional licensed owner photograph. All 200 records remain partial.

> Previous delivery: [Phase 8 — UI/UX Polish & Quality Assurance](docs/PHASE_8_REPORT.md). Shared black-and-gold styling, labelled placeholders, accessible controls, URL history and responsive browser evidence.

> Previous delivery: [Phase 7 — 200 real guitar models](docs/PHASE_7_REPORT.md). Ten approved brands with twenty models each, preserved archives, manufacturer sources and browser evidence.

> Previous delivery: [Phase 6 — Real Guitar Data & Images](docs/PHASE_6_REPORT.md).

> Previous delivery: [Phase 5 — Brands & Wishlist](docs/PHASE_5_REPORT.md).

> Previous delivery: [Phase 4 — Compare & Find My Guitar](docs/PHASE_4_REPORT.md).

> Previous delivery: [Phase 3 — Catalog & Guitar Detail](docs/PHASE_3_REPORT.md).

> Previous delivery: [Phase 1–2 report](docs/PHASE_1_2_REPORT.md).

# Fretline — Guitar Discovery & Comparison

React + Vite + Tailwind CSS (v3)

## Run

```bash
npm ci
npm run dev      # http://localhost:5173
npm run build
npm run catalog:check
npm run images:check
```

Historical phase4–phase9 and private-preview checks retain their original data snapshots; they are not current catalog acceptance checks after the authorized Pacifica price/specification and project-artwork updates. Current gallery browser checks are in `docs/qa-pacifica-project/browser-gallery.py`.

Phase 8 browser scripts and reproducible checks are documented in [the QA report](docs/PHASE_8_REPORT.md). They use Python Playwright and a separately installed Chromium; these tools are not runtime dependencies of the website.

Phase 9 results, the 20-model specification tables, dated manufacturer links and reusable browser commands are in [the batch report](docs/qa-phase9/README.md). The remaining 180 records were not rechecked against live sources in this batch.

## รูปภาพ

**รูปกีตาร์รายรุ่น:** วางไฟล์ที่ `src/assets/guitars/<guitar-id>/01-front.webp` ภาพถ่ายที่มีใบอนุญาตใช้ทะเบียน `src/data/catalog/imageRights.json` ส่วนภาพประกอบที่ผู้ใช้ขอให้นำมาใช้ในโครงงานใช้ `src/data/catalog/projectArtwork.json` โดยเก็บที่มาและการตกแต่งไว้แยกกัน ดู [คู่มือเพิ่มข้อมูล](docs/ADDING_GUITARS.md)
รุ่นที่ยังไม่มีรูปจะแสดง "Photo coming soon" ไม่ใช้รูปรุ่นอื่นแทน — ดูรายการที่ขาดใน `MISSING_IMAGES.md` หรือรัน `npm run images:check`

**รูปบรรยากาศ** (Hero, หมวดหมู่, แบรนด์, แถบ Quiz): ตั้งที่ `src/data/images.js` (ตอนนี้เป็น `null` = ใช้ภาพเส้นร่าง)

## เปลี่ยนข้อมูล

| ต้องการแก้ | ไฟล์ |
|---|---|
| ข้อมูลที่ตรวจสอบแล้ว พร้อมขอบเขตและแหล่งอ้างอิง | `src/data/catalog/reviewedGuitars.json` |
| 166 รุ่นใหม่พร้อมหลักฐานรายฟิลด์ | `src/data/catalog/phase7Guitars.json` |
| ข้อกำหนด 200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 | `src/data/catalog/catalogPolicy.json` |
| สำรองสองรุ่นที่พัก พร้อม ID และแหล่งอ้างอิงเดิม | `src/data/catalog/archivedGuitars.json` |
| ID/ลำดับเดิม และการประกอบข้อมูลเผยแพร่ | `src/data/guitars.js` |
| หมวดหมู่ / แบรนด์ | `src/data/categories.js`, `src/data/brands.js` |
| ข้อความ/สถิติ/hotspot ใน Hero | `src/data/hero.js` |
| เมนู / Footer | `src/data/navigation.js` |
| สีและฟอนต์ | `tailwind.config.js` |
| UI polish และ responsive rules ที่ใช้ร่วมกัน | `src/styles/polish.css` |
| แถวในตารางเปรียบเทียบ | `src/components/compare/compareRows.js` |

## Routes

| Path | หน้า |
|---|---|
| `/` | Homepage |
| `/guitars` | Catalog — filter ผ่าน URL เช่น `?type=electric&brand=Fender&min=10000&max=50000&sort=price-asc&q=strat` |
| `/guitars/:slug` | Guitar Detail, สเปก, แกลเลอรี, Lightbox และแหล่งอ้างอิง |
| `/compare` | เปรียบเทียบ 2–4 รุ่น |
| `/find-my-guitar` | แบบสอบถาม 5 ขั้นตอน |
| `/brands`, `/brands/:id` | Brands และ Brand Detail |
| `/wishlist` | รายการโปรด |
| `/image-credits` | แหล่งที่มาและสิทธิ์ภาพ |

## Guitar Detail

ข้อมูลเผยแพร่ใช้ `reviewedGuitars.json` และ `phase7Guitars.json` แสดงเฉพาะฟิลด์ใน `source.fields` พร้อมวันที่ วิธีตรวจ และข้อจำกัดรุ่น/ปีผลิต ช่องที่ยังไม่ทราบเป็น `null` รูปแต่ละมุมต้องมีไฟล์จริงและทะเบียนที่มา ขนาดย่อยใน `responsive/` ไม่นับเป็นมุมภาพเพิ่ม

`guitarDetails.js` และค่าดิบเดิมคงไว้เพื่อรักษางานเก่า แต่ราคา รีวิว และสเปกตัวอย่างไม่ได้ถูกนำไปเผยแพร่ผ่าน Catalog ปัจจุบัน

## Compare (`/compare`)

- เลือกกีตาร์ 2–4 รุ่นจากปุ่ม Compare ทุกหน้า หรือกด "Add guitar" ในหน้า Compare
- แชร์ลิงก์ได้: `/compare?ids=<id1>,<id2>`
- แถวและกลุ่มของตารางแก้ที่ `src/components/compare/compareRows.js`
- ไม่มีคะแนนรีวิวเผยแพร่ในชุดปัจจุบัน รีวิวต้องมีหลักฐานตรวจสอบแยกจากสเปก
- ลิงก์และรายการเดิมที่มี Gretsch G2420 หรือ Yamaha C40 ยังเปิดได้ พร้อมป้ายพักจาก Catalog และไม่รวมในยอด 200 รุ่น

## Find My Guitar (`/find-my-guitar`)

- คำถาม/ตัวเลือก/โปรไฟล์กีตาร์ทุกรุ่น: `src/data/quiz.js`
- กติกาให้คะแนน (ประเภท 30, ระดับ 20, แนวเพลง 20, งบ 20, ความสำคัญ 10, รีวิว 5): `src/utils/quizScoring.js`
- คำตอบอยู่ใน URL เช่น `/find-my-guitar?type=electric&level=beginner&style=rock&budget=mid&priority=value` จึงแชร์ผลได้
- รุ่นที่ยังไม่มีโปรไฟล์ไม่ถูกเดาความเหมาะสมด้านระดับ/แนวเพลง จะแสดงข้อจำกัดและไม่ได้คะแนนส่วนนั้น รุ่นใหม่ 166 รุ่นยังไม่ได้เพิ่มโปรไฟล์เชิงประเมิน สูตรและเกณฑ์เดิมคงอยู่ และไม่แนะนำรุ่นที่พัก

## Brands และ Wishlist

- `/brands` — แบรนด์ทั้งหมดคำนวณจากข้อมูลกีตาร์ชุดเดียวกับ Catalog (`src/data/brands.js`) ค้นหา/กรองประเภท/ประเทศ/เรียงลำดับได้ ตัวกรองอยู่ใน URL
- `/brands/:id` — กีตาร์ของแบรนด์นั้น (ใช้ `CatalogCard` ตัวเดียวกับ Catalog)
- `/wishlist` — ใช้ Wishlist เดิมใน `ShopContext` (key `fretline:wishlist`) ไม่มีที่เก็บซ้ำ
- โลโก้แบรนด์: วางไฟล์ที่ `src/assets/brands/<brand-id>.svg` (เช่น `fender.svg`) ยังไม่มีไฟล์ = แสดงชื่อแบรนด์เป็นตัวอักษร
- ข้อมูลประเทศ/ปีก่อตั้งแก้ที่ `BRAND_INFO` ใน `src/data/brands.js`

## ข้อมูลกีตาร์ 200 รุ่น และรูปภาพ

- Catalog หลักมี **200 รุ่นพอดี / 10 แบรนด์ / แบรนด์ละ 20 รุ่น**: `partial` 200, `verified` 0 PAC612VIIFM มีราคาแนะนำ Yamaha ประเทศไทย ฿34,000 พร้อมหลักฐาน ส่วนอีก 199 รุ่นยังสอบถามราคา และไม่แสดงคะแนนรีวิวที่ไม่มีหลักฐาน
- แบรนด์: Yamaha, Fender, Epiphone, Ibanez, Taylor, Córdoba, Gibson, Martin, PRS และ Squier
- ใช้ 34 รุ่นเดิม + เพิ่ม 166 รุ่นจากแหล่งผู้ผลิต เก็บ Gretsch G2420 และ Yamaha C40 ใน Archive แยกจาก Catalog หลัก ลิงก์เก่าและ ID ใน Wishlist/Compare ยังอยู่
- มีภาพจริงที่บันทึกสิทธิ์แล้ว **2 ภาพ / 2 รุ่น** (CC BY-SA 4.0) อีก **198 รุ่น** ใช้ Placeholder: Yamaha FG820-12 ใส่สายไว้ 6 เส้นตามข้อมูลผู้ถ่าย; Martin D-28 เป็นภาพเจ้าของปี 2018 ไม่ทราบปีผลิต และไม่ใช่ภาพรุ่นสเปก Golden Era ปัจจุบัน มีคำอธิบาย/เครดิตกำกับ ไม่มีการคัดลอกภาพผู้ผลิตโดยไม่มีสิทธิ์
- เครื่องมือ CSV เดิมยังอยู่ แต่จะปฏิเสธรายการซ้ำ แบรนด์นอกแผน หรือการนำเข้าที่เกินโควตา 200/20 (ดู `docs/ADDING_GUITARS.md`)
- ตรวจความคืบหน้า/รายการซ้ำ/ข้อมูลไม่ครบ: `npm run catalog:check`
- ตรวจรูปที่ขาด: `npm run images:check` (เขียนรายการลง `MISSING_IMAGES.md` ด้วย `-- --write`)
- เครดิต/เงื่อนไขภาพ: `src/data/catalog/imageRights.json` แสดงใน Detail, Lightbox และ `/image-credits` โดยมีลิงก์จาก Footer ทุกหน้า

### สถานะข้อมูล (dataStatus) และ "Price on request"

- `sample` = ตัวอย่างยังไม่ตรวจ | `partial` = ตรวจกับแหล่งทางการบางส่วน (ช่องที่ไม่ทราบเว้นว่าง แสดง "Not specified") | `verified` = ตรวจครบและมีราคา
- ราคาที่ยืนยันไม่ได้ = เว้นว่าง แสดง **Price on request** (ไม่เดา ไม่แปลงสกุลเงิน) รุ่นนี้ถูกซ่อนเมื่อกรองตามช่วงราคา และเรียงอยู่ท้ายสุดเสมอ
- ราคายังไม่มีหลักฐานทั้งชุด: ช่องช่วงราคาจะอธิบายข้อจำกัด ลิงก์ที่ระบุช่วงราคาจะเข้าสู่ Empty State ที่ล้างตัวกรองได้
- หลักฐาน Phase 6: [Audit ก่อนแก้](docs/PHASE_6_AUDIT_BEFORE.md), [ข้อมูลหลังแก้และแหล่งอ้างอิง](docs/PHASE_6_SOURCES.md), [ผลทดสอบและข้อจำกัด](docs/PHASE_6_REPORT.md)
- หลักฐาน Phase 7: [รายชื่อ 200 รุ่นพร้อมแหล่งอ้างอิง](docs/PHASE_7_CATALOG.md), [ผลทดสอบและการรักษารายการเดิม](docs/PHASE_7_REPORT.md)
- หลักฐาน Phase 9: [สเปก 20 รุ่น แหล่งอ้างอิง สิทธิ์ภาพ และผลทดสอบ](docs/qa-phase9/README.md)
- ไฟล์ CSV และ Sourcing Log รุ่นเก่าคงไว้เป็นประวัติการนำเข้า `reviewedGuitars.json` เป็นค่าที่ผ่านการตรวจล่าสุดและมีลำดับความสำคัญสูงกว่า
