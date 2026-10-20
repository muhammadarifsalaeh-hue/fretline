# FRETLINE — Phase 6 delivery

วันที่ตรวจ: **2026-10-20** · Repository: [muhammadarifsalaeh-hue/fretline](https://github.com/muhammadarifsalaeh-hue/fretline) · Branch: `master`

ต่อยอดจาก `13f20de4cdf7ec836d764c0842a741ce5da64907` โดยรักษา Commit เดิม รวมถึง `f74f79c`, `c8b1bf3` และงาน Phase 4–5 ใช้โปรเจกต์เดิม ไม่มี `git init`, ไม่มี Force Push และไม่มี Dependencies ใหม่

## ผลงานและสถานะข้อมูล

ตรวจรายการเดิม 36 รุ่น / 11 แบรนด์ ไม่พบ ID หรือชื่อแบรนด์/รุ่นซ้ำ ใช้ข้อมูลเผยแพร่ชุดเดียวกันใน Homepage, Catalog, Guitar Detail, Compare, Quiz, Brands และ Wishlist โดยคง ID, URL, ลำดับรุ่น, ShopContext และสูตร Quiz เดิม

| รายการ | ก่อน Phase 6 | หลัง Phase 6 |
|---|---:|---:|
| จำนวนรุ่น | 36 | 36 |
| sample | 18 | 0 |
| partial | 18 | 36 |
| verified ทั้งรายการ | 0 | 0 |
| ราคาตัวอย่างที่ไม่มีหลักฐานในข้อมูลเผยแพร่ | 18 | 0 |
| คะแนนรีวิวที่ไม่มีหลักฐานในข้อมูลเผยแพร่ | 18 | 0 |
| รุ่นที่มีรูปจริงพร้อมสิทธิ์ | 0 | 1 |
| รุ่นที่ใช้ Placeholder | 36 | 35 |

**ยังไม่ยืนยันราคาเงินบาททั้ง 36 รุ่น ไม่มีรีวิวที่ยืนยันแล้ว และไม่ยืนยันน้ำหนักทั้ง 36 รุ่น** ช่องที่ยังไม่ทราบเป็น `null` และแสดงข้อความตามจริง ไม่คัดลอกค่าจาก Demo เดิม ทุกข้อมูลยังคงเป็น partial

บันทึกแหล่งข้อมูล รุ่น/ปี/ตัวเลือกวัสดุ วันที่ วิธีเข้าถึง และขอบเขตฟิลด์ใน `reviewedGuitars.json` พร้อมแสดงข้อจำกัดในหน้า Detail แหล่งหลักอ่านผ่าน HTTP 33 รุ่น, Web reader 1 รุ่น และข้อความดัชนีค้นหา 2 รุ่น จำนวนนี้เป็นจำนวนรุ่น ไม่ใช่จำนวนเว็บไซต์ มี URL หลัก/เสริมที่แตกต่างกัน 19 URL

รายละเอียดรายรุ่น ค่าที่ขาด แหล่งอ้างอิง และเงื่อนไขภาพอยู่ใน [PHASE_6_SOURCES.md](PHASE_6_SOURCES.md) และ [Audit ก่อนแก้](PHASE_6_AUDIT_BEFORE.md) สองรายการที่อ่านได้จำกัดคือ Gretsch G2420 และ Yamaha C40 ซึ่งแยกวิธีเข้าถึงอย่างชัดเจน ไม่กล่าวอ้างว่าอ่านเอกสารฉบับเต็มแล้ว

## สิ่งที่เพิ่มและแก้ไข

- แยกค่าตัวอย่างเดิมออกจากข้อมูลที่ใช้แสดงผล และตรวจสเปกกับคอลัมน์/รุ่น/ปีที่อ้างอิง เช่น SR300E, GS Mini Mahogany, 214ce, Squier Classic Vibe และ Yamaha FG/FS800
- แสดงขอบเขตแหล่งข้อมูลและข้อจำกัดรุ่น/ปี ใช้ `source.fields` ป้องกันค่า Demo หลุดไปแสดงหรือใช้ให้คะแนน
- เพิ่มภาพจริง **1 ภาพของ Yamaha FG820-12** โดย Peternick2468 ภายใต้ [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) จาก [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:12_string_Yamaha_acoustic_guitar.jpg) ภาพใส่สายไว้ 6 เส้นตามผู้ถ่าย จึงมีคำอธิบายแสดงชัดเจน
- บันทึกผู้ถ่าย แหล่งที่มา ไลเซนส์ วันที่ หลักฐานตรงรุ่น การแปลงไฟล์และ SHA-256 เพิ่ม `/image-credits` และเครดิตใน Detail/Lightbox พร้อมลิงก์จาก Footer ทุกหน้า
- สร้าง WebP 1200px และขนาดย่อย 480/960px รวม 3 ไฟล์จากภาพเดียว ขนาดย่อยไม่ถูกนับเป็นมุมภาพ ใช้ Lazy Loading, `srcset`, `sizes` และขนาดภาพเดิม; รูปหลัก Detail โหลดล่วงหน้า มี Placeholder เมื่อโหลดไม่สำเร็จ
- แก้ตัวกรองราคาเดิมที่คำนวณเป็น Infinity เมื่อไม่มีราคา ขณะนี้อธิบายข้อจำกัดแทน Slider และลิงก์ช่วงราคามี Empty State ที่ล้างตัวกรองได้ ไม่ใช้ราคาแต่งเพื่อให้ตัวกรองทำงาน
- คง Quick Search จากหลักฐานเฉพาะรุ่น เช่น FG820L สำหรับมือซ้าย และรุ่นที่ผู้ผลิตวางตำแหน่งสำหรับผู้เริ่มต้น
- ใช้หน่วย mm เดิมของผู้ผลิตเมื่อมี เพื่อไม่ให้ค่ากีตาร์สเกลเท่ากันถูกมองว่าต่างจากการปัดเศษนิ้ว
- ป้องกันค่า URL เช่น `sort=constructor` และ ID จาก Prototype ของ Object ทำให้หน้าเดิมเปิดได้ปลอดภัย
- เพิ่ม Summary ของเครดิตภาพในวงจร Keyboard Focus ของ Dialog และรักษาการปิด Lightbox ด้วย Escape/คืน Focus

ไม่มีการเปลี่ยนโครงสร้างหลักของ Homepage, Catalog หรือ Guitar Detail โทนดำ–ทองเดิมคงอยู่ การเปลี่ยน Homepage จำกัดข้อความข้อมูลที่ไม่มีหลักฐานและใช้ค่าที่ตรวจตามขอบเขตแล้ว

## ผลการทดสอบ

| การตรวจ | ผล | หลักฐาน |
|---|---|---|
| `npm run build` | ผ่าน, exit 0 | [build.txt](qa-phase6/build.txt) |
| `npm run catalog:check` | ผ่าน: 36 รุ่น, 11 แบรนด์, partial 36, verified 0 | [catalog-check.txt](qa-phase6/catalog-check.txt) |
| `npm run images:check` | ผ่านทะเบียนสิทธิ์/ไฟล์; 1 ภาพ + 2 ขนาดย่อย, ขาดรูป 35 รุ่น | [images-check.txt](qa-phase6/images-check.txt) |
| `npm run phase6:check` | 21/21 ผ่าน | [logic-tests.txt](qa-phase6/logic-tests.txt) |
| `npm run phase4:check` | 19/19 ผ่าน, สูตรและน้ำหนักเดิม | [phase4-regression.txt](qa-phase6/phase4-regression.txt) |
| `npm run phase5:check` | 15/15 ผ่าน, Brands/Wishlist เดิม | [phase5-regression.txt](qa-phase6/phase5-regression.txt) |
| Production Browser | 79/79 ผ่าน | [browser-results.json](qa-phase6/browser-results.json), [สคริปต์](qa-phase6/browser-qa.py) |
| Dev Strict Mode และกรณีพิเศษ | 20/20 ผ่าน | [browser-edges-results.json](qa-phase6/browser-edges-results.json), [สคริปต์](qa-phase6/browser-edges.py) |

Browser Automation ใช้ Python Playwright กับ Chromium บน Linux ไม่ได้ทดสอบ Safari/WebKit หรือ iPad จริง

Production flow ครอบคลุม Quick Search, Search, Brand/Type Filter, Sorting, Pagination, ล้างตัวกรองราคา, การเปิด Detail, สเปกจริง/ช่องว่าง, รีวิวว่าง, เครดิตภาพ, Lightbox/Keyboard/Escape, Compare, Wishlist เพิ่ม/ลบ/Reload, Brands/จำนวนรุ่น, Quiz 5 ขั้นตอน/ย้อนแก้คำตอบ/ผลลัพธ์/เปิด Detail/Browser Back และหน้าเครดิต

กรณีพิเศษครอบคลุมการย้ายรายการเก่าจาก Local Storage, ขจัด ID ซ้ำ/ไม่รู้จัก, Shared Compare ใน Strict Mode, เพิ่มรุ่นที่ 3–4, ป้องกันรุ่นที่ 5, Remove, Browser Back/Forward, รูปโหลดไม่สำเร็จ, เลือกภาพตามหน้าจอ และภาษาอังกฤษ ไม่พบ Console/Runtime Error ใน Production flow และ Dev Strict Mode ปกติ ไม่พบ Failed Request ใน Production flow ปกติ

มีการจงใจ Abort รูปภาพ **2 Requests** ใน Browser Context แยกเพื่อทดสอบ Placeholder จึงไม่นับเป็นข้อผิดพลาดของการโหลดปกติ และไม่มี Runtime Error ตามมา บน Mobile DPR 1 โหลดไฟล์ 480px จริง ขนาด 38,716 ไบต์ แทนต้นฉบับ 2.2 MB

ตรวจ 7 หน้าในขนาด 1440×1100, 768×1024 และ 390×844 ไม่พบ Document Overflow และตรวจเพิ่มที่ 320px สำหรับ Detail, Wishlist และ Credits ทดสอบแนวนอนของ Compare ภายในพื้นที่ตาราง โดยไม่ให้ทั้งหน้าเลื่อนออกนอกจอ ตรวจภาพ Screenshot จริงของหน้า Detail และ Catalog แล้ว ไม่มีการอ้างว่า Pixel Match กับ Reference ทุกจุด

ไม่ได้รัน `npm install`/`npm ci` ใหม่ เพราะ Dependencies และ Lockfile เดิมเพียงพอ ไม่มีการเพิ่ม Package

## Screenshots

Full-page screenshots จาก Production Preview และภาพ Mobile Viewport รวม 16 ภาพ:

| หน้า | Desktop | Tablet | Mobile |
|---|---|---|---|
| Catalog | [ภาพ](qa-phase6/catalog-desktop.png) | [ภาพ](qa-phase6/catalog-tablet.png) | [ภาพ](qa-phase6/catalog-mobile.png) |
| Guitar Detail | [ภาพ](qa-phase6/detail-desktop.png) | [ภาพ](qa-phase6/detail-tablet.png) | [ภาพ](qa-phase6/detail-mobile.png) |
| Compare | [ภาพ](qa-phase6/compare-desktop.png) | [ภาพ](qa-phase6/compare-tablet.png) | [ภาพ](qa-phase6/compare-mobile.png) |
| Wishlist | [ภาพ](qa-phase6/wishlist-desktop.png) | [ภาพ](qa-phase6/wishlist-tablet.png) | [ภาพ](qa-phase6/wishlist-mobile.png) |
| Image Credits | [ภาพ](qa-phase6/credits-desktop.png) | [ภาพ](qa-phase6/credits-tablet.png) | [ภาพ](qa-phase6/credits-mobile.png) |

[Detail — Mobile Viewport](qa-phase6/detail-mobile-viewport.png) อ่านรายละเอียดได้โดยไม่ย่อภาพเต็มหน้ายาว

## ไฟล์ที่เปลี่ยน

- `MISSING_IMAGES.md`
- `README.md`
- `docs/ADDING_GUITARS.md`
- `docs/PHASE_6_AUDIT_BEFORE.md`
- `docs/PHASE_6_REPORT.md`
- `docs/PHASE_6_SOURCES.md`
- `package.json`
- `scripts/check-images.mjs`
- `scripts/check-phase6.mjs`
- `scripts/lib/catalog.mjs`
- `scripts/validate-catalog.mjs`
- `src/App.jsx`
- `src/assets/guitars/yamaha-fg820-12/01-front.webp`
- `src/assets/guitars/yamaha-fg820-12/LICENSE.md`
- `src/assets/guitars/yamaha-fg820-12/responsive/01-front-480.webp`
- `src/assets/guitars/yamaha-fg820-12/responsive/01-front-960.webp`
- `src/components/catalog/PriceRange.jsx`
- `src/components/compare/compareRows.js`
- `src/components/detail/DataStatusNote.jsx`
- `src/components/detail/GuitarGallery.jsx`
- `src/components/detail/ImageAttribution.jsx`
- `src/components/detail/ImageLightbox.jsx`
- `src/components/detail/SpecTable.jsx`
- `src/components/guitar/GuitarImage.jsx`
- `src/components/home/Brands.jsx`
- `src/components/layout/Footer.jsx`
- `src/components/ui/SmartImage.jsx`
- `src/data/catalog/imageRights.json`
- `src/data/catalog/reviewedGuitars.json`
- `src/data/guitarImages.js`
- `src/data/guitars.js`
- `src/hooks/useCatalogFilters.js`
- `src/hooks/useDialogFocus.js`
- `src/i18n/en.js`
- `src/i18n/th.js`
- `src/index.css`
- `src/pages/CatalogPage.jsx`
- `src/pages/ImageCreditsPage.jsx`
- `src/utils/dataTrust.js`
- `src/utils/format.js`
- `src/utils/imageRights.js`

- `docs/qa-phase6/`: Audit ก่อน/หลัง, สรุปช่องว่าง, ทะเบียนแหล่งอ้างอิง, ผลเรียก HTTP, ตรวจสิทธิ์ภาพ, Build/CLI/Browser logs, สคริปต์ Playwright และภาพหน้าจอ 16 ภาพ

## ข้อจำกัดที่ยังเหลือ

- ขาดภาพที่ตรงรุ่นและมีสิทธิ์ใช้สำหรับอีก 35 รุ่น ไม่ใช้ภาพสินค้าใกล้เคียงแทนและไม่คัดลอกจากผู้ผลิตโดยถือว่ามีสิทธิ์อัตโนมัติ
- ราคาเงินบาท 36 รุ่นและน้ำหนัก 36 รุ่นยังไม่มีหลักฐาน จำนวนเฟรตยังขาด 22 รุ่น จำนวนสายขาด 23 รุ่น รวมถึงรายละเอียดบางช่อง ดูตารางใน Sources
- Gretsch G2420 อ่านหน้าเต็มโดยตรงไม่ได้ (403) ใช้เฉพาะฟิลด์ที่ปรากฏในข้อความดัชนีค้นหาผู้ผลิต ส่วน Yamaha C40 ใช้แคตตาล็อกเก่า 2013–2014 จากข้อความดัชนี ไม่ใช้ข้อมูล C40II/CX40 แทนและไม่ยืนยันว่ายังวางขาย
- ข้อมูลรุ่นปัจจุบันของ Taylor, Martin, PRS และตัวเลือกวัสดุของ Fender/Epiphone อาจไม่ครอบคลุมกีตาร์ปีผลิตอื่น จึงมี Edition Note และคง partial
- โปรไฟล์ความเหมาะสมของ Quiz เป็นการประเมินตามระบบเดิม มีคำอธิบาย ไม่อ้างเป็นข้อรับรองจากผู้ผลิต/ผู้รีวิว น้ำหนักยังเป็น 30/20/20/20/10 และรีวิว 5; ไม่มีข้อมูลรีวิวจึงไม่ได้คะแนนส่วนนี้
- ยังไม่ได้ทดสอบบน Safari ของ iPad จริง การตรวจ Responsive เป็น Chromium ที่กำหนด Viewport

## Git และการเปิด Codespaces

ตรวจ `origin` เป็น Repository เดิมและ Fetch ก่อนส่งมอบ Remote `master` ยังตรงกับ Baseline โดยไม่มี Commit ใหม่จากฝั่งอื่น การส่งมอบใช้ Commit ใหม่บน `master` และ Push ปกติ ไม่มีการเขียนทับประวัติ ผล Push และ Hash จริงอยู่ในข้อความส่งมอบ/ไฟล์ `delivery.json` ของ ZIP และตรวจต่อได้ด้วย `git log -1` ไม่ฝัง Hash ของ Commit เองไว้ในรายงาน

บันทึกงานส่วนตัวใน Codespaces ก่อน แล้วหยุด Vite เดิมด้วย Ctrl+C จากนั้น:

```bash
git pull --ff-only origin master
npm ci
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

ใน Codespaces เปิดแท็บ **Ports** → พอร์ต **5173** → **Open in Browser** ใช้ Forwarded URL บน Safari ของ iPad โดยล็อกอิน GitHub ที่มีสิทธิ์เข้าถึง Repository และคง Port Visibility เป็น Private หาก Pull ติด Local Changes ให้เก็บ/Commit งานของตนก่อน ไม่ใช้คำสั่ง Reset ทิ้งงาน

หยุดที่ Phase 6 ยังไม่เริ่ม Phase 7 การเติมหลักฐาน/ภาพที่ขาดเป็นงานคงค้างสำหรับคำสั่งครั้งถัดไป
