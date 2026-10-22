> บันทึกก่อนคำสั่งให้นำโค้ดขึ้น GitHub: ขั้นตอนใช้งานล่าสุดอยู่ใน [คู่มือ Codespaces](../PACIFICA_PREVIEW_CODESPACES.md) ซึ่งเลือก JPEG จากเบราว์เซอร์ได้ ไม่ต้องใช้ Patch และไม่อัปโหลดภาพขึ้น GitHub

# PAC612VIIFM — Multi-color Gallery Development Preview

ทำงานในโปรเจกต์ Fretline เดิมบน `master` ต่อจากการทดลองภาพเดี่ยว ไม่สร้างโปรเจกต์ใหม่ **ไม่ได้ Commit / Push / Deploy** เพราะยังไม่มีหลักฐานสิทธิ์ภาพต้นฉบับ HEAD ยังเป็น `1229c669425f79505f9a9064cc5f28978984a793`

## สิ่งที่ทำ

- ใช้ไฟล์แนบครบ 4 ภาพ จับคู่ตามภาพจริง ไม่สร้างภาพ ไม่แก้ภาพ ไม่ครอป ไม่แปลง JPEG เป็น WebP ค่า SHA-256 ที่เสิร์ฟตรงกับไฟล์แนบทุก byte
- เปิด Detail เริ่มที่ Black; Black / Red / Blue / Teal เป็นชื่อใช้แยกภาพประกอบ **ไม่อ้างชื่อสีทางการของ Yamaha**
- Color Selector, thumbnail, ลูกศร, swipe และ Lightbox ใช้ภาพที่เลือกชุดเดียวกัน กดสีแล้วไม่ reload หน้า กรอบสีทองและชื่อสีตรงกับภาพ
- ภาพรวม 3 สีเป็นภาพที่ 4 แยกจากปุ่มเลือกสีทั้งสาม เมื่อเลือกภาพรวมจะไม่ highlight สีใดจนกดเลือกสีเดี่ยว
- ใช้ Gallery, ImageLightbox, ColorSwatches, SmartImage, ShopContext และโครงสร้าง Router เดิม ภาพแสดงด้วย contain โดยไม่ตัดหัว/ฐานกีตาร์ ปิด hover magnification ที่ครอปภาพทดลอง; Lightbox ยังคงดูขนาดใหญ่ได้
- Catalog มีการ์ดรุ่นเดียว ใช้ Black เป็นภาพหลัก พร้อมจุดสีสามจุด ส่วน Compare และ Wishlist ใช้ Black และบันทึก Guitar ID เดิม ไม่สร้างรุ่นแยกตามสี
- เอาป้าย AI / AI Edited / AI Generated ออกจากการ์ดและบริเวณภาพหลัก เก็บ provenance และสถานะสิทธิ์ไว้ใน metadata / image-intake.json และในรายละเอียดแหล่งข้อมูลที่เปิดอ่านได้ ไม่สร้างเครดิตหรือใบอนุญาตที่ไม่มีหลักฐาน
- Gallery ทดลองไม่เปลี่ยน `guitar.gallery`, `guitar.colors`, `hasPhotos`, `imageRights.json` หรือ `source.fields` สีในตารางสเปกยัง “ไม่ระบุ” เนื่องจากชื่อสีทางการยังไม่ยืนยัน
- ภาพทดลองเปิดเฉพาะ `npm run dev:pacifica-preview`; `npm run dev` ปกติและ Production Build ใช้ Placeholder ตามสิทธิ์เดิม ทั้ง Build ปกติและ Build ด้วย `--mode pacifica-preview` ไม่มีภาพ/endpoint ทั้งสี่
- ไม่มีการแก้ข้อมูลกีตาร์ใดในรอบ Multi-color นี้ รวม PAC612VIIFM ราคาแนะนำ ฿34,000 และสเปกจากงานก่อนคงเดิม ตรวจ SHA-256 ของไฟล์ข้อมูลก่อน/หลังใน `data-before-sha256.json` ไม่เพิ่ม dependency

## จับคู่ไฟล์แนบ

เก็บต้นฉบับใน `.local-preview/yamaha-pacifica-612viifm/` ซึ่งถูก Git ignore ไม่ใส่ใน public หรือ src/assets/guitars:

| ไฟล์แนบ | ภาพ | ชื่อไฟล์ Preview | ขนาด |
|---|---|---|---|
| 2-รูปภาพ-2.jpg | Black | `01-black.jpg` | 1024 × 1280 |
| 3-รูปภาพ-3.jpg | Red | `02-red.jpg` | 1024 × 1280 |
| 4-รูปภาพ-4.jpg | Blue / Teal | `03-blue-teal.jpg` | 1024 × 1280 |
| 1-รูปภาพ-1.jpg | All colors | `04-all-colors.jpg` | 1280 × 853 |

สิทธิ์: ไฟล์ผู้ใช้สำหรับทดลองการจัดวาง ไม่มีหลักฐาน author/license/permission ของภาพต้นฉบับ ไม่ยืนยันความตรงรุ่น ฮาร์ดแวร์ หรือสีจากภาพตกแต่งเหล่านี้ ภาพใหม่ทั้ง 4 จึง **ไม่นับเป็น licensed product photos** และไม่ใช้เป็นหลักฐานสเปก

## ผลทดสอบ

| รายการ | ผล |
|---|---|
| npm run build | ผ่าน |
| npm run catalog:check | ผ่าน — 200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 / ไม่มีรุ่นหรือ ID ซ้ำ |
| npm run images:check | ผ่าน — ภาพสิทธิ์ครบยัง 2 รุ่น / Placeholder 198 รุ่นใน Production |
| node scripts/check-pacifica-preview.mjs | 14 checks ผ่าน — รักษาข้อมูล, Data Trust, ราคา, สเปก, original JPEG, route scope, build gating |
| Browser Gallery | 117 checks ผ่าน — สี, golden border, thumbnail, overview, Lightbox, keyboard, touch tap/swipe, same-document, Wishlist, Compare, licensed-gallery regression |
| Production browser และ scan | 14 checks ผ่าน — JPEG ทั้ง 4 / endpoint / ตัวเลือกสีทดลองไม่เข้า Build; URL ภาพคืนภาพไม่ได้ |
| Shared-page smoke tests | 7 checks ผ่าน — Homepage, Brands, Yamaha 20 รุ่น, Quiz results, Mobile Lightbox และสถานะสีหลังปิด |
| Responsive | Chromium 1440, 1024, 768, 390, 320px; ไม่พบ horizontal overflow ในหน้าที่ตรวจ |
| Console / Runtime | ไม่พบ error ในชุดที่ผ่าน |
| Safari / iPad จริง | ยังไม่ได้ทดสอบ; touch เป็น Chromium emulation |

ภาพ Mobile ที่ส่งตรวจเป็นภาพยาวที่ความกว้าง 390px เพื่อดูรูปกับตัวเลือกสีพร้อมกัน โดยเพิ่มความสูง viewport ตอนจับภาพเพื่อให้ fixed bottom navigation ไม่ทับเนื้อหา ชุด interaction ทดสอบที่ 390×844 และ 320×740 จริงตาม viewport จำลอง

บันทึกผลใน `test-summary.json` และ `logs/` ส่วนผล browser แบบละเอียดและ screenshots เก็บใน `.local-preview/multicolor/` ไม่เข้า Git การเริ่ม Browser ครั้งแรกพบ preview server ยังไม่เปิด จึงเปิด server แล้วรันใหม่ผ่านครบ; production server ที่ port 5180 เปิดอยู่แล้วจึงใช้ server เดิมที่อ่าน dist ล่าสุด

## ดู Preview ใน workspace นี้

ใช้โค้ดปัจจุบันและไฟล์ทั้งสี่ที่วางแล้ว:

```bash
npm run dev:pacifica-preview -- --host 0.0.0.0 --port 5173 --strictPort
```

เปิด port 5173 จากแผง Preview/Ports หาก environment รองรับ แล้วเข้า `/guitars/yamaha-pacifica-612viifm` หรือ `/guitars?q=612VIIFM` URL localhost เป็นภายในเครื่องที่รัน Vite ไม่ใช่ลิงก์จาก iPad โดยตรง

## ดูใน GitHub Codespaces เดิม

โค้ดรอบนี้ยังไม่อยู่ใน GitHub การ git pull อย่างเดียวจึงยังไม่ได้ Multi-color Gallery:

1. ดาวน์โหลด `fretline-pacifica-multicolor-code.patch` (ไม่มีภาพ) และอัปโหลดเข้า Codespace เดิมของ Fretline
2. ตรวจ `git status --short` และเก็บงานค้างก่อน Patch นี้ทำจาก baseline `1229c66` รวมงานทดลองเดิมทั้งหมด จึงเหมาะกับ baseline นั้นที่ยังไม่ได้ใช้ patch ภาพเดี่ยว หากใช้ patch เดิมหรือมีการแก้ไขใหม่แล้วให้ตรวจ diff/conflict ก่อน ไม่ใช้ reset หรือ force ทับงาน
3. จาก root ของ repository เดิม รัน `git apply --check /path/to/fretline-pacifica-multicolor-code.patch` ถ้าผ่านจึงรัน `git apply /path/to/fretline-pacifica-multicolor-code.patch`
4. สร้าง `.local-preview/yamaha-pacifica-612viifm/` แล้วอัปโหลด **JPEG ต้นฉบับทั้งสี่** ตั้งชื่อให้ตรงตารางด้านบน ไม่ต้องใช้ PNG จากรอบเก่า
5. หากยังไม่มี node_modules รัน `npm install` แล้วรันคำสั่ง dev:pacifica-preview ด้านบน
6. Ports → 5173 → **Private** → Open in Browser; เปิด path ด้านบนใน Safari

ไม่เพิ่มภาพหรือ screenshots เข้า Git ด้วย git add -f ไม่เผยแพร่ port สู่ Public และไม่ Push/Deploy ภาพจนสิทธิ์ต้นฉบับผ่านการตรวจ

## ไฟล์ที่ปรับสำหรับ Multi-color

- `scripts/vite/developmentImagePreview.mjs`
- `src/utils/developmentImagePreview.js`
- `src/components/guitar/DevelopmentImagePreview.jsx`
- `src/components/guitar/GuitarImage.jsx`
- `src/components/guitar/PreviewColorIndicators.jsx`
- `src/components/catalog/CatalogCard.jsx`
- `src/components/detail/GuitarGallery.jsx`
- `src/components/detail/ColorSwatches.jsx`
- `src/components/detail/DataStatusNote.jsx`
- `src/pages/GuitarDetailPage.jsx`
- `src/i18n/th.js`
- `src/i18n/en.js`
- `scripts/check-pacifica-preview.mjs`
- `docs/qa-pacifica-multicolor/`

`ImageLightbox.jsx`, Compare, Wishlist และข้อมูลราคา/สเปกเดิมถูกใช้ต่อ ไม่มีการแก้ข้อมูลกีตาร์รุ่นอื่น งานภาพเดี่ยวก่อนหน้านี้ยังคงเป็น working-tree changes ที่ไม่ได้ Commit และรวมอยู่ใน patch ล่าสุดเพื่อให้ทดลองได้ครบ
