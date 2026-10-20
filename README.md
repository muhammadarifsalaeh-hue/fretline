> Latest delivery: [Phase 7 — 200 real guitar models](docs/PHASE_7_REPORT.md). Ten approved brands with twenty models each, preserved archives, manufacturer sources and browser evidence.

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
npm run phase6:check
npm run phase7:check
```

## รูปภาพ

**รูปกีตาร์รายรุ่น:** วางไฟล์ที่ `src/assets/guitars/<guitar-id>/01-front.webp` และบันทึกสิทธิ์/แหล่งที่มา/ผู้ถ่าย/หลักฐานตรงรุ่นใน `src/data/catalog/imageRights.json` รูปที่ไม่มีข้อมูลสิทธิ์ครบถ้วนจะไม่ถูกเผยแพร่ ดู [คู่มือเพิ่มข้อมูล](docs/ADDING_GUITARS.md)
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

ข้อมูลเผยแพร่ใช้ `reviewedGuitars.json` และ `phase7Guitars.json` แสดงเฉพาะฟิลด์ใน `source.fields` พร้อมวันที่ วิธีตรวจ และข้อจำกัดรุ่น/ปีผลิต ช่องที่ยังไม่ทราบเป็น `null` รูปแต่ละมุมต้องมีไฟล์จริงและทะเบียนสิทธิ์ ขนาดย่อยใน `responsive/` ไม่นับเป็นมุมภาพเพิ่ม

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

- Catalog หลักมี **200 รุ่นพอดี / 10 แบรนด์ / แบรนด์ละ 20 รุ่น**: `partial` 200, `verified` 0 ราคาเงินบาทและรีวิวยังไม่มีหลักฐานที่เพียงพอ จึงไม่แสดงตัวเลขสมมติ
- แบรนด์: Yamaha, Fender, Epiphone, Ibanez, Taylor, Córdoba, Gibson, Martin, PRS และ Squier
- ใช้ 34 รุ่นเดิม + เพิ่ม 166 รุ่นจากแหล่งผู้ผลิต เก็บ Gretsch G2420 และ Yamaha C40 ใน Archive แยกจาก Catalog หลัก ลิงก์เก่าและ ID ใน Wishlist/Compare ยังอยู่
- มีภาพจริงที่บันทึกสิทธิ์แล้ว 1 ภาพของ Yamaha FG820-12 (CC BY-SA 4.0) อีก **199 รุ่น** ใช้ Placeholder ภาพนี้ใส่สายไว้ 6 เส้นตามข้อมูลผู้ถ่าย จึงระบุคำอธิบายไว้ชัดเจน ไม่มีการคัดลอกภาพผู้ผลิตเพิ่มใน Phase 7
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
- ไฟล์ CSV และ Sourcing Log รุ่นเก่าคงไว้เป็นประวัติการนำเข้า `reviewedGuitars.json` เป็นค่าที่ผ่านการตรวจล่าสุดและมีลำดับความสำคัญสูงกว่า
