# FRETLINE — Phase 7 delivery

วันที่ตรวจ 2026-10-20 · Repository: [muhammadarifsalaeh-hue/fretline](https://github.com/muhammadarifsalaeh-hue/fretline) · Branch `master`

Baseline `4fa60f6a5ee885c839324a2a5dc6adc651ad117a` ใช้โปรเจกต์เดิมและรักษาประวัติ Phase 1–6 ไม่มีการสร้าง Git Repository ใหม่ ไม่มี Dependencies ใหม่ ไม่มี Backend และไม่มี Force Push

## ผลงานจริง

เพิ่ม **166 รุ่นจริง** จากข้อมูลผู้ผลิต ใช้ 34 รุ่นเดิม และพัก 2 รุ่นตามที่อนุมัติ ทำให้ **Catalog หลักมี 200 รุ่นพอดี จาก 10 แบรนด์ แบรนด์ละ 20 รุ่น** ไม่พบ ID หรือชื่อแบรนด์/รุ่นซ้ำตามตัวตรวจ และไม่นับตัวเลือกสีเป็นรุ่นเพิ่ม

| แบรนด์ | ใช้รุ่นเดิม | เพิ่มจริง | Catalog หลัก |
|---|---:|---:|---:|
| Yamaha | 20 | 0 | 20 |
| Fender | 3 | 17 | 20 |
| Epiphone | 2 | 18 | 20 |
| Ibanez | 2 | 18 | 20 |
| Taylor | 2 | 18 | 20 |
| Córdoba | 1 | 19 | 20 |
| Gibson | 1 | 19 | 20 |
| Martin | 1 | 19 | 20 |
| PRS | 1 | 19 | 20 |
| Squier | 1 | 19 | 20 |
| **รวม** | **34** | **166** | **200** |

ประเภทตามระบบเดิมรวมเบส: กีตาร์ไฟฟ้า 90, กีตาร์โปร่ง 73, กีตาร์คลาสสิก/ไนลอน 20 และเบส 17

**ทั้ง 200 รุ่นยังเป็น partial ไม่มีรุ่นที่ยืนยันครบเป็น verified** ราคาเงินบาทและน้ำหนักยังไม่ยืนยันทั้ง 200 รุ่น ไม่มีรีวิวที่ยืนยันแล้ว ไม่ใส่ตัวเลขสมมติ ช่องที่ยังไม่มีหลักฐานแสดงตามจริง

รายชื่อทั้ง 200 รุ่น พร้อม ID, แหล่งอ้างอิง, รุ่น/ปี และขอบเขตข้อมูลอยู่ใน [PHASE_7_CATALOG.md](PHASE_7_CATALOG.md) และ [CSV สำหรับตรวจรายการ](qa-phase7/catalog-200.csv)

## หลักฐานที่ตรวจจริง

- รุ่นใหม่ 147 รุ่นใน 8 แบรนด์ตรวจจากหน้าสินค้าทางการรายรุ่น HTTP 200 พร้อม Hash ของเนื้อหาที่เรียกได้
- PRS อีก 19 รุ่นตรวจจาก [แคตตาล็อกทางการปี 2025](https://support.prsguitars.com/hc/en-us/article_attachments/34374903847067) หน้า 3–8 ระบุปีและหน้าในข้อมูล ไม่อ้างว่าเป็นสเปกทุกปีหรือยังมีสินค้าพร้อมขาย
- รวมการเรียกแหล่งผู้ผลิตใหม่ 148 รายการรองรับ 166 รุ่น: 147 หน้ารุ่น + PDF 1 ฉบับ ข้อมูลรุ่นเดิม 34 รุ่นคง Source และ Scope จาก Phase 6 โดยไม่ได้เปิดตรวจหน้าผู้ผลิตของรุ่นเดิมทั้งหมดซ้ำใน Phase นี้
- บันทึกฟิลด์ที่อ่านได้ไว้ใน `source.fields` และ [field-evidence.json](qa-phase7/field-evidence.json) พร้อม [ผลเรียกแหล่งข้อมูล](qa-phase7/source-retrievals.json) และ [ทะเบียนรายรุ่น](qa-phase7/source-register.json)
- วัสดุที่เป็นตัวเลือกของ Fender/Squier คงแสดงเป็นตัวเลือก ไม่เลือกไม้ของทุกสีจากความจำ รุ่นย่อยที่นับแยกมีชื่อ/รหัสผู้ผลิตจริงและความต่างของรุ่น ไม่ใช่ภาพเพิ่มหรือสีเดียวกันหลายรายการ
- ไม่เก็บ HTML หรือ PDF ฉบับเต็มที่มีลิขสิทธิ์ลง Repository เก็บเฉพาะข้อเท็จจริงสั้น ๆ URL, Scope, วันที่ และหลักฐานเรียกข้อมูล

## การพักรุ่นและผลกระทบต่อข้อมูลเดิม

พักจาก Catalog หลัก:

1. **Gretsch G2420 Streamliner Hollow Body** — `gretsch-g2420-streamliner`
2. **Yamaha C40 Classical** — `yamaha-c40`

สำรองข้อมูลใน [archivedGuitars.json](../src/data/catalog/archivedGuitars.json) ประกอบด้วย ID เดิม ข้อมูล Reviewed เดิม แหล่งอ้างอิงเดิม Snapshot ที่เคยเผยแพร่ และข้อความ Source Record เดิม ไม่ลบข้อมูลดิบหรือ Commit เก่า

`GUITARS` และ `GUITARS_BY_ID` มีเฉพาะ 200 รุ่นที่ใช้งานใน Catalog, Search, Filters, Brands, Similar Recommendations และ Quiz ส่วน `SAVED_GUITARS_BY_ID` เพิ่มการค้นหาสองรุ่นที่พักเพื่อรองรับรายการของผู้ใช้

- URL Detail เก่าทั้งสองรุ่นยังเปิดได้ พร้อมข้อความพักจาก Catalog และข้อจำกัดแหล่งข้อมูลเดิม
- Wishlist เดิมยังเก็บ ID และข้อมูลทั้งสองรุ่น ไม่ล้าง Local Storage เอง ผู้ใช้เลือกนำออกได้ตามปกติ
- Shared Compare URL ที่มีรุ่นพักยังเปิดและเปรียบเทียบได้ มีป้ายพักชัดเจน ลบได้ และ Browser Back/Forward คืนรายการถูกต้อง
- Compare Bar และตารางบน Homepage อ่านรายการที่บันทึกผ่าน Resolver เดียวกัน จึงไม่ทำชื่อ/รายการเก่าหายจาก Tray
- ลิงก์ `/brands/gretsch` แสดงสถานะแบรนด์ที่พักพร้อมลิงก์ข้อมูลเดิม แบรนด์ไม่กลับไปเพิ่มยอดใน Directory หลัก
- ไฟล์สำรองเต็มที่มี Snapshot ไม่ถูกนำเข้า Browser Bundle ใช้ข้อมูล Reviewed เดิมสำหรับแสดงผลย้อนหลัง

## การตรวจจำนวนและข้อผิดพลาดที่แก้

- `catalog:check` ตรวจ **เท่ากับ 200**, แบรนด์ตรงกับรายชื่ออนุมัติ และแต่ละแบรนด์ **เท่ากับ 20** บังคับทุกครั้ง ไม่ใช้เพียง “อย่างน้อย 200”
- ตัวนำเข้า CSV ตรวจรายการซ้ำรวมถึงรุ่น Phase 7 และ Archive รวมทั้งปฏิเสธแบรนด์นอกแผน/ยอดเกิน 200/โควตาเกิน 20 ก่อนเขียนไฟล์
- ปรับ Regression Check ของ Phase 6 ที่ผูกกับ 36 รุ่นให้รองรับยอดใหม่ โดยยังรักษาการตรวจข้อมูลเก่า Source Scope สูตร Quiz และสิทธิ์ภาพไว้ครบ
- ระหว่าง QA พบการนับสาย RG652AHM ผิดจากช่องว่างหลังจุลภาคใน Factory Tuning แก้เป็น **6 สาย** ตามรายการ `1E, 2B, 3G, 4D, 5A, 6E` และเพิ่ม Test ที่ตรวจจำนวนสายเทียบหลักฐานทุก Ibanez ใหม่ รวมทั้งกรณี 7 และ 9 สาย
- แยก Static Catalog และ Framework เป็นคนละ Chunk เพื่อให้ข้อมูล 200 รุ่นไม่รวมอยู่ใน JS ก้อนเดียวกับ UI โดยไม่เพิ่ม Dependency ผล Build ล่าสุด: UI entry 127.66 kB, vendor 163.33 kB และ catalog 315.76 kB ก่อน gzip ไม่พบคำเตือน Chunk เกิน 500 kB ไม่มีการอ้างผล Benchmark ที่ไม่ได้วัด

## รูปภาพและข้อจำกัดข้อมูล

ไม่มีการเพิ่มภาพสินค้าใน Phase 7 ใช้ภาพที่มีสิทธิ์เดิมของ Yamaha FG820-12 เพียง 1 รุ่น อีก **199 รุ่นใช้ Placeholder** ไม่ใช้ภาพรุ่นใกล้เคียงหรือคัดลอกภาพผู้ผลิตโดยไม่มีสิทธิ์ ภาพเดิมของ Peternick2468 อยู่ภายใต้ CC BY-SA 4.0 พร้อมเครดิต/เงื่อนไขเดิม และคำอธิบายว่าภาพใส่สายไว้ 6 เส้น

ข้อมูลที่ยังขาดในชุดหลัก: Neck 2, Pickups 2, Bridge 1, Controls 80, Frets 41, Strings 150 และ Weight 200 รุ่น Body และ Scale มีข้อมูลตาม Scope ทั้งชุด ดูค่ารายรุ่นใน [Application Snapshot](qa-phase7/audit-after.json)

รุ่นใหม่ไม่มีการสร้างโปรไฟล์ระดับผู้เล่นหรือแนวเพลงเพื่อเพิ่มคะแนน Quiz สูตรเดิม 30/20/20/20/10 และรีวิว 5 คงอยู่ การขาดโปรไฟล์แสดงเป็นข้อจำกัดและไม่ได้คะแนนส่วนนั้น จึงไม่ได้รับประกันว่ารุ่นใหม่ทุกตัวจะผ่านเกณฑ์แนะนำ ไม่มีการแนะนำรุ่นที่พัก

## ผลการทดสอบ

| การตรวจ | ผลจริง | หลักฐาน |
|---|---|---|
| `npm run build` | ผ่าน exit 0 หลังแก้ข้อมูลรอบสุดท้าย | [build.txt](qa-phase7/build.txt) |
| `npm run catalog:check` | ผ่าน 200/10/20, partial 200, sample 0, verified 0 | [catalog-check.txt](qa-phase7/catalog-check.txt) |
| `npm run images:check -- --write` | ผ่านสิทธิ์/ไฟล์; 1 ภาพ + 2 ขนาดย่อย; รายงานช่องว่าง 199 รุ่น | [images-check.txt](qa-phase7/images-check.txt) |
| `npm run phase4:check` | 19/19 ผ่าน | [phase4-regression.txt](qa-phase7/phase4-regression.txt) |
| `npm run phase5:check` | 15/15 ผ่าน | [phase5-regression.txt](qa-phase7/phase5-regression.txt) |
| `npm run phase6:check` | 21/21 ผ่าน | [phase6-regression.txt](qa-phase7/phase6-regression.txt) |
| `npm run phase7:check` | 16/16 ผ่าน | [phase7-check.txt](qa-phase7/phase7-check.txt) |
| Browser Regression | 79/79 ผ่าน | [ผล](qa-phase7/browser-regression-results.json), [สคริปต์](qa-phase7/browser-regression.py) |
| Browser Phase 7 | 83/83 ผ่าน | [ผล](qa-phase7/browser-phase7-results.json), [สคริปต์](qa-phase7/browser-phase7.py) |
| Browser ตรวจค่าที่แก้รอบสุดท้าย | 2/2 ผ่าน | [corrected-fact-browser.json](qa-phase7/corrected-fact-browser.json) |
| CSV Import Guard (Negative Test) | ปฏิเสธตามคาด exit 1: ID/ชื่อซ้ำ และเกินยอด 200/20 ไม่มีไฟล์ถูกเขียน | [import-guard-check.txt](qa-phase7/import-guard-check.txt) |

รวม Logic **71 ข้อ** และ Browser **164 ข้อ** ผ่าน ไม่มี Console Error, Runtime Error หรือ Failed Request ใน Browser Flow ที่ตรวจ ไม่รัน npm install/npm ci ใหม่ เพราะไม่มี Package หรือ Lockfile เปลี่ยน

Browser ใช้ Python Playwright กับ Chromium บน Linux ทดสอบ Desktop 1440×1100, Tablet 768×1024, Mobile 390×844 และเพิ่มการตรวจบางหน้าที่ 320px ไม่มีการทดสอบ Safari/WebKit หรือ iPad จริง

Browser Coverage: Homepage เดิม, Search, Quick Filters, Brand/Type Filter, Sorting, Pagination ของทั้ง 200 รุ่นถึงหน้า 23 และแต่ละแบรนด์ถึงหน้า 3, Empty State, Detail ของรุ่นใหม่ตัวแทน 9 แบรนด์ + RG652AHM, เครดิต/Lightbox ภาพเดิม, Wishlist เพิ่ม/ลบ/Reload, Compare, Quiz 5 ขั้นตอน/ย้อนแก้/ลิงก์แชร์, Brand Detail, รายการเก่าที่พัก, Back/Forward, Keyboard และ Dev Strict Mode ข้อมูลทั้ง 200 รุ่นตรวจด้วยชุด Logic แต่ไม่ได้เปิด Detail ทุก 200 รุ่นทีละหน้าใน Browser

## Screenshots

รวม 33 ภาพจาก Preview ที่ทดสอบ ดูตัวอย่าง:

- [Brands — 10 แบรนด์ × 20 รุ่น](qa-phase7/brands-200-desktop.png)
- [Catalog — 200 รุ่น](qa-phase7/catalog-200-desktop.png) · [Mobile](qa-phase7/catalog-200-mobile.png)
- [รุ่นใหม่ — Mobile](qa-phase7/new-detail-mobile.png)
- [Compare ที่มีรุ่นพัก — Desktop](qa-phase7/compare-archive-desktop.png) · [Mobile](qa-phase7/compare-archive-mobile.png)
- [Wishlist ที่มีรุ่นพัก — Desktop](qa-phase7/wishlist-archive-desktop.png) · [Mobile](qa-phase7/wishlist-archive-mobile.png)
- [Detail รุ่นพัก — Mobile](qa-phase7/archive-detail-mobile.png)

ตรวจภาพจริงของ Brands, Compare และ Wishlist แล้ว คง Design System ดำ–ทองเดิม ไม่อ้างว่าเปรียบเทียบแบบ Pixel Match กับภาพ Reference ทุกจุด

## ไฟล์ที่เปลี่ยน

- `MISSING_IMAGES.md`
- `README.md`
- `docs/ADDING_GUITARS.md`
- `docs/PHASE_7_CATALOG.md`
- `docs/PHASE_7_REPORT.md`
- `package.json`
- `scripts/check-phase6.mjs`
- `scripts/check-phase7.mjs`
- `scripts/import-csv.mjs`
- `scripts/lib/catalog.mjs`
- `scripts/validate-catalog.mjs`
- `src/components/compare/CompareSection.jsx`
- `src/components/compare/CompareTable.jsx`
- `src/components/layout/CompareBar.jsx`
- `src/components/wishlist/WishlistRow.jsx`
- `src/data/catalog/archivedGuitars.json`
- `src/data/catalog/catalogPolicy.json`
- `src/data/catalog/phase7Guitars.json`
- `src/data/guitars.js`
- `src/i18n/en.js`
- `src/i18n/th.js`
- `src/index.css`
- `src/pages/BrandDetailPage.jsx`
- `src/pages/ComparePage.jsx`
- `src/pages/GuitarDetailPage.jsx`
- `src/pages/WishlistPage.jsx`
- `src/utils/selection.js`
- `vite.config.js`

- `docs/qa-phase7/`: Audit ก่อน/หลัง, สรุปจำนวน, หลักฐานรายฟิลด์, ทะเบียน Source, CSV 200 รุ่น, CLI/Build/Browser logs และ Screenshot 33 ภาพ

## Git และ Codespaces

งานนี้เป็น Commit ใหม่บน `master` จาก Baseline เดิม โดย Fetch ตรวจ Remote ก่อน Push ปกติ ผล Push และ Commit Hash จริงรายงานในข้อความส่งมอบและ `delivery.json` ของไฟล์ส่งมอบ ไม่ฝัง Hash ของ Commit ตัวเองในเอกสารนี้

ใน Codespaces บันทึกงานส่วนตัวก่อน หยุด Vite เดิมด้วย Ctrl+C แล้วรัน:

```bash
git pull --ff-only origin master
npm ci
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

เปิด **Ports → 5173 → Open in Browser** และคง Visibility เป็น Private ใช้บัญชี GitHub ที่มีสิทธิ์ Repository บน Safari ของ iPad หาก Pull ติด Local Changes ให้เก็บงานนั้นก่อน ไม่ Reset ทิ้ง

หยุดที่ Phase 7 ไม่เริ่ม Phase 8 โดยอัตโนมัติ งานคงค้างคือเติมหลักฐานช่องที่ขาด ราคาไทย ภาพที่มีสิทธิ์ และโปรไฟล์ความเหมาะสมของรุ่นใหม่เมื่อมีข้อมูลรองรับ
