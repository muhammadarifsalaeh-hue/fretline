> Latest delivery: [Phase 4 — Compare & Find My Guitar](docs/PHASE_4_REPORT.md). Includes scoring rationale, browser evidence, and Codespaces update instructions.

> Latest delivery: [Phase 3 — Catalog & Guitar Detail](docs/PHASE_3_REPORT.md). Includes current test evidence and remaining content gaps.

> Latest delivery: [Phase 1–2 report](docs/PHASE_1_2_REPORT.md). See that report for current verification, screenshots, content limitations, and next steps.

# Fretline — Homepage

React + Vite + Tailwind CSS (v3)

## Run

```bash
npm install
npm run dev      # เปิด http://localhost:5173
npm run build    # build สำหรับ deploy (Vercel / Netlify)
```

## รูปภาพ

**รูปกีตาร์รายรุ่น:** วางไฟล์ที่ `src/assets/guitars/<guitar-id>/01-front.webp` (+ มุมอื่น `02-...`) ระบบดึงไปใช้ทุกหน้าเอง ไม่ต้องแก้โค้ด
รุ่นที่ยังไม่มีรูปจะแสดง "Photo coming soon" ไม่ใช้รูปรุ่นอื่นแทน — ดูรายการที่ขาดใน `MISSING_IMAGES.md` หรือรัน `npm run images:check`

**รูปบรรยากาศ** (Hero, หมวดหมู่, แบรนด์, แถบ Quiz): ตั้งที่ `src/data/images.js` (ตอนนี้เป็น `null` = ใช้ภาพเส้นร่าง)

## เปลี่ยนข้อมูล

| ต้องการแก้ | ไฟล์ |
|---|---|
| กีตาร์ (ชื่อ ราคา สเปก) | `src/data/guitars.js` |
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
| `/guitars/:slug` | Guitar Detail (เวอร์ชันพื้นฐาน) |

หมายเหตุ: ต้องรัน `npm install` ใหม่ เพราะเพิ่ม `react-router-dom`

## Guitar Detail

ข้อมูลรายละเอียดรายรุ่น (description, bridge, controls, สี, รูปหลายมุม) อยู่ที่ `src/data/guitarDetails.js`
ใส่ `gallery: [{ src: '/images/guitars/strat-front.webp', label: 'Front view' }, ...]` เพื่อใช้รูปจริงหลายมุม
(ถ้าไม่ใส่ ระบบจะสร้างมุมมองชั่วคราวจากรูปหลัก)

## Compare (`/compare`)

- เลือกกีตาร์ 2–4 รุ่นจากปุ่ม Compare ทุกหน้า หรือกด "Add guitar" ในหน้า Compare
- แชร์ลิงก์ได้: `/compare?ids=<id1>,<id2>`
- แถวและกลุ่มของตารางแก้ที่ `src/components/compare/compareRows.js`
- คะแนนรีวิวเป็นข้อมูลตัวอย่างใน `src/data/guitarDetails.js` (`RATINGS`)

## Find My Guitar (`/find-my-guitar`)

- คำถาม/ตัวเลือก/โปรไฟล์กีตาร์ทุกรุ่น: `src/data/quiz.js`
- กติกาให้คะแนน (ประเภท 30, ระดับ 20, แนวเพลง 20, งบ 20, ความสำคัญ 10, รีวิว 5): `src/utils/quizScoring.js`
- คำตอบอยู่ใน URL เช่น `/find-my-guitar?type=electric&level=beginner&style=rock&budget=mid&priority=value` จึงแชร์ผลได้
- เพิ่มกีตาร์ใหม่ในแคตตาล็อก → อย่าลืมเพิ่มโปรไฟล์ใน `GUITAR_PROFILES` ด้วย (ไม่มีโปรไฟล์ = ไม่ได้คะแนนระดับ/แนวเพลง)

## Brands และ Wishlist

- `/brands` — แบรนด์ทั้งหมดคำนวณจากข้อมูลกีตาร์ชุดเดียวกับ Catalog (`src/data/brands.js`) ค้นหา/กรองประเภท/ประเทศ/เรียงลำดับได้ ตัวกรองอยู่ใน URL
- `/brands/:id` — กีตาร์ของแบรนด์นั้น (ใช้ `CatalogCard` ตัวเดียวกับ Catalog)
- `/wishlist` — ใช้ Wishlist เดิมใน `ShopContext` (key `fretline:wishlist`) ไม่มีที่เก็บซ้ำ
- โลโก้แบรนด์: วางไฟล์ที่ `src/assets/brands/<brand-id>.svg` (เช่น `fender.svg`) ยังไม่มีไฟล์ = แสดงชื่อแบรนด์เป็นตัวอักษร
- ข้อมูลประเทศ/ปีก่อตั้งแก้ที่ `BRAND_INFO` ใน `src/data/brands.js`

## ข้อมูลกีตาร์ 200 รุ่น และรูปภาพ

- ตอนนี้ 18 รุ่นเป็นข้อมูลตัวอย่าง (`dataStatus: 'sample'`) และยังไม่มีรูปจริง เว็บแสดงภาพประกอบสำรองที่ระบุชัดว่าไม่ใช่สินค้า
- เพิ่มรุ่นใหม่จาก CSV: `npm run catalog:import -- file.csv` (ดู `docs/ADDING_GUITARS.md`)
- ตรวจความคืบหน้า/รายการซ้ำ/ข้อมูลไม่ครบ: `npm run catalog:check`
- ตรวจรูปที่ขาด: `npm run images:check` (เขียนรายการลง `MISSING_IMAGES.md` ด้วย `-- --write`)
- เครดิตรูป (เมื่อไลเซนส์ต้องการ): `IMAGE_CREDITS` ใน `src/data/guitarImages.js` จะแสดงใต้รูปในหน้า Detail

### สถานะข้อมูล (dataStatus) และ "Price on request"

- `sample` = ตัวอย่างยังไม่ตรวจ | `partial` = ตรวจกับแหล่งทางการบางส่วน (ช่องที่ไม่ทราบเว้นว่าง แสดง "Not specified") | `verified` = ตรวจครบและมีราคา
- ราคาที่ยืนยันไม่ได้ = เว้นว่าง แสดง **Price on request** (ไม่เดา ไม่แปลงสกุลเงิน) รุ่นนี้ถูกซ่อนเมื่อกรองตามช่วงราคา และเรียงอยู่ท้ายสุดเสมอ
- ชุดที่ 1: Yamaha FG/FS800 series 18 รุ่น (`data-template/batch-01-yamaha-fg-fs.csv`) ดูรายละเอียดใน `docs/SOURCING_LOG.md` และแผนต่อไปใน `docs/BATCH_PLAN.md`
