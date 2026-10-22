> บันทึกก่อนคำสั่งให้นำโค้ดขึ้น GitHub: ขั้นตอนใช้งานล่าสุดอยู่ใน [คู่มือ Codespaces](../PACIFICA_PREVIEW_CODESPACES.md) ซึ่งเลือก JPEG จากเบราว์เซอร์ได้ ไม่ต้องใช้ Patch และไม่อัปโหลดภาพขึ้น GitHub

> บันทึกประวัติการทดลองภาพเดี่ยว: UI และคำสั่งเตรียมภาพในเอกสารนี้เป็นเวอร์ชันก่อน Multi-color Gallery ดูงานปัจจุบันที่ [Multi-color Preview](../qa-pacifica-multicolor/README.md) ชุด browser test ในโฟลเดอร์นี้ยึด UI เก่า ไม่ใช่ผลทดสอบ Gallery ปัจจุบัน

# PAC612VIIFM — การทดลองภาพเฉพาะ Development Preview

สถานะ: โค้ดและข้อมูลแก้ไขใน working tree ของโปรเจกต์เดิมบน master เท่านั้น **ไม่ได้ Commit, Push หรือ Deploy** ฐานก่อนทดลองคือ `1229c669425f79505f9a9064cc5f28978984a793` และไม่ได้แก้ข้อมูลกีตาร์อีก 199 รุ่น

## ผลลัพธ์

- แสดงไฟล์ PNG เดิม 1254 × 1254 พิกเซลโดยไม่แก้ไข ไม่ครอป ไม่สร้างภาพใหม่ ใช้ object-contain พร้อม intrinsic dimensions และ lazy loading บนการ์ด
- แสดงเฉพาะ ID `yamaha-pacifica-612viifm` ในโหมดทดลอง พร้อมป้าย Development Preview / AI และข้อความว่ายังไม่ยืนยันรุ่น รายละเอียด สี หรือสิทธิ์ต้นฉบับ
- ภาพคอปิ๊กอัพดูคล้ายแบบสองแถว จึงใช้ภาพนี้ยืนยันฮาร์ดแวร์ HSS ของรุ่นจริงไม่ได้ ชื่อรุ่นที่พิมพ์ในภาพไม่ใช่หลักฐานความตรงรุ่น
- ไม่เพิ่มภาพนี้ใน gallery, imageRights.json หรือยอดภาพสินค้าที่ผ่านสิทธิ์ ไม่มี thumbnail/zoom ที่ทำให้ภาพทดลองดูเป็นแกลเลอรีสินค้าที่ตรวจสอบแล้ว
- ภาพและ screenshots อยู่ใน `.local-preview/` ซึ่ง Git ignore ไว้ และปิดการเข้าถึงไฟล์โดยตรงผ่าน Vite
- Build ปกติและ `vite build --mode pacifica-preview` ไม่รวมภาพ/endpoint นี้ หน้า Production ยังคง Placeholder ของ PAC612VIIFM
- ใช้ข้อมูลราคาและสเปกที่ตรวจจาก Yamaha ชุดเดียวใน Catalog, Detail, Compare และ Wishlist พร้อมคำกำกับราคาแนะนำ
- ไม่เพิ่ม dependencies และไม่เปลี่ยนจำนวน 200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 รุ่น

## แหล่งข้อมูล — เข้าถึงจริง 22 ตุลาคม 2026, HTTP 200

1. [Yamaha ประเทศไทย: lineup และราคาแนะนำ](https://th.yamaha.com/th/musical-instruments/guitars-basses-amps/products/electric-guitars/pacifica/lineup.html)
2. [Yamaha ประเทศไทย: ตารางสเปก](https://th.yamaha.com/th/musical-instruments/guitars-basses-amps/products/electric-guitars/pacifica/specs.html)
3. [Yamaha USA: เทียบคอลัมน์ PAC612VIIFM](https://usa.yamaha.com/products/musical_instruments/guitars_basses/el_guitars/pacifica/specs.html)

ตารางสเปกใช้คอลัมน์ PAC612VIIFM (model index 4) เท่านั้น ไม่ใช้ PAC611/PAC612VIIFMX/PAC612VII มี URL, วันที่, HTTP status และ SHA-256 ของหน้าอ้างอิงใน `manufacturer-evidence.json` ไม่จัดเก็บ HTML เต็มใน repository

| รายการ | ข้อมูลสำหรับแสดงผล |
|---|---|
| Series | Pacifica |
| Body | Alder with Flamed Maple Veneer |
| Shape | ไม่ระบุ — ยังไม่พบคำยืนยันจากข้อความผู้ผลิตที่ตรวจ |
| Neck | Maple |
| Fingerboard | Rosewood |
| Neck Finish | Gloss Polyurethane (แก้จาก Satin ตามคอลัมน์ PAC612VIIFM) |
| Scale Length | 25.5 inches / 648 mm |
| Fingerboard Radius | 350 mm |
| Frets | 22 |
| Nut | Graph Tech TUSQ |
| Bridge Pickup | Seymour Duncan Custom 5 TB-14 Humbucker |
| Middle Pickup | Seymour Duncan SSL-1 RwRp |
| Neck Pickup | Seymour Duncan SSL-1 — ไม่ใช่ SP90-1 |
| Pickup Configuration | HSS |
| Controls | Master Volume, Master Tone with Push/Pull Coil Split |
| Pickup Selector | 5-Position Lever Switch |
| Bridge | Wilkinson VS50-6 Vibrato |
| Tuners | Grover Locking Tuners |
| Color | ไม่ระบุ — ไม่ยืนยันสีจากภาพ AI |
| Price | ฿34,000 — ราคาขายปลีกแนะนำโดย Yamaha ประเทศไทย; ไม่รับประกันราคาของร้านค้า |

ข้อมูลรวมยังเป็น **partial** ไม่ยกระดับเป็น fully verified เพราะยังไม่ทราบบางฟิลด์ เช่น น้ำหนัก จำนวนสายที่ระบุโดยตรงในคอลัมน์ และสีของภาพทดลอง ฟิลด์ที่ไม่ทราบคง null / “ไม่ระบุ” ไม่มีรีวิวหรือคะแนนสร้างขึ้น `source.fields` ระบุขอบเขตของราคาและทุกสเปกที่มีค่า ส่วนราคามี `priceSource` สกุล THB แยกต่างหาก ยอดผ่อน ฿40,800 ไม่ถูกใช้แทนราคาแนะนำ ฿34,000

## ผลทดสอบ

- `npm run build`: ผ่าน
- `npm run catalog:check`: ผ่าน; 200 รุ่น, 10 แบรนด์, 20 รุ่นต่อแบรนด์, ไม่มี ID/รุ่นซ้ำ
- `npm run images:check`: ผ่าน; ภาพที่มีเอกสารสิทธิ์ยังเป็น 2 รุ่น, Placeholder 198 รุ่น (รวม PAC612VIIFM ใน Production)
- `node scripts/check-pacifica-preview.mjs`: 13 checks ผ่าน ครอบคลุมขอบเขตข้อมูลอีก 199 รุ่น, Data Trust, source.fields, ตัวเลขราคา, unknowns, Compare, Quiz และการแยกภาพออกจาก Build
- Chromium + Playwright: 76 checks ผ่าน ตรวจ Catalog/Detail/specs/Wishlist/Compare ที่ 1440, 1024, 768, 390, 320px; ไม่พบ page-level horizontal overflow; Wishlist บันทึก/โหลดใหม่/ลบได้; ไม่พบ Console/Runtime/failed-request error ใน flow ปกติ
- Production browser + scan: 7 checks ผ่าน; ทั้ง Build ปกติและ Build ด้วยโหมดทดลองไม่มีภาพหรือ endpoint; Catalog/Detail ยังคง Placeholder; URL ภาพไม่คืน bytes PNG
- PNG ที่เสิร์ฟใน Preview มี SHA-256 ตรงกับไฟล์แนบทุก byte ไม่มีการแก้ขนาดหรือแปลงภาพ
- ยังไม่ได้ทดสอบ Safari หรือ iPad จริง
- เก็บ logs ไว้ใน `logs/`; ผล browser และ screenshot ที่มีภาพทดลองเก็บเฉพาะ `.local-preview/`
- การรัน Browser หนึ่งครั้งหยุดเพราะ preview server ขาดการเชื่อมต่อหลัง execution service restart; เปิด server ใหม่แล้วรันชุดสุดท้ายผ่านทั้งหมด
- ชุด snapshot ประวัติ Phase 6–9 เดิมยึดข้อมูลก่อนงานนี้ จึงไม่อ้างว่ารันชุดเก่าทั้งหมดผ่าน ใช้ชุดตรวจเฉพาะการเปลี่ยน PAC612VIIFM นี้แทน

## วิธีดูใน workspace นี้

เปิด port 5173 จากแผง Preview/Ports ของ environment หากมี:

- `/guitars?q=612VIIFM`
- `/guitars/yamaha-pacifica-612viifm`

`http://localhost:5173` เป็น URL ภายในเครื่องที่รัน Vite ไม่ใช่ลิงก์สาธารณะสำหรับเปิดตรงจาก iPad

## วิธีนำชุดทดลองไป Codespaces เดิมบน iPad

โค้ดทดลองยังไม่อยู่ใน GitHub ดังนั้น `git pull` อย่างเดียวจะยังไม่ได้งานรอบนี้ ใช้ patch ที่แนบซึ่ง **ไม่มีภาพ** และใช้ repository เดิม:

1. เปิด Codespace ของ repository Fretline เดิม ตรวจ `git status --short` และสำรองงานค้างก่อน หากเป็น baseline 1229c66 ที่ไม่มีการแก้ค้าง สามารถใช้ patch ได้ตรง ๆ หากมีงานใหม่ให้ตรวจ conflict ก่อน ห้าม force/reset งานเดิม
2. ดาวน์โหลด `fretline-pacifica-preview-code.patch` และอัปโหลดเข้า Codespace; ใช้ `git apply --check /path/to/fretline-pacifica-preview-code.patch` ก่อน แล้วจึง `git apply /path/to/fretline-pacifica-preview-code.patch` เมื่อ check ผ่าน
3. สร้างโฟลเดอร์ `.local-preview` ใน repository เดิม และอัปโหลดไฟล์ PNG ต้นฉบับที่คุณแนบเข้าไป เปลี่ยนชื่อเป็น `yamaha-pacifica-612viifm-preview.png` โดยไม่แก้เนื้อภาพ
4. รัน `npm install` เฉพาะเมื่อยังไม่มี node_modules จากนั้น `npm run dev:pacifica-preview -- --host 0.0.0.0 --port 5173`
5. แท็บ Ports → 5173 → ตั้ง Visibility เป็น **Private** → Open in Browser แล้วเปิด path ด้านบนบน Safari ไม่เผยแพร่ port สู่ Public
6. คำสั่ง `npm run dev` ปกติหรือ Production Build ไม่แสดงภาพนี้ หากโหมดทดลองยังไม่ได้ไฟล์ PNG จะหยุดพร้อมแจ้งให้วางไฟล์ ไม่มีการดาวน์โหลดภาพเอง

ห้ามเพิ่ม `.local-preview/` หรือ screenshots เข้า Git ด้วย `git add -f` การดู Preview ได้ไม่เท่ากับมีสิทธิ์เผยแพร่ภาพ ต้องมีหลักฐานสิทธิ์ต้นฉบับและตรวจความตรงรุ่นก่อนพิจารณาใช้เป็นภาพสินค้า

## ไฟล์ที่แก้/เพิ่มในงานทดลองนี้

- `.gitignore`
- `package.json`
- `scripts/lib/catalog.mjs`
- `src/components/catalog/CatalogCard.jsx`
- `src/components/compare/CompareTable.jsx`
- `src/components/compare/compareRows.js`
- `src/components/detail/DataStatusNote.jsx`
- `src/components/detail/DetailTabs.jsx`
- `src/components/detail/GuitarGallery.jsx`
- `src/components/detail/SpecTable.jsx`
- `src/components/detail/StickyGuitarBar.jsx`
- `src/components/guitar/GuitarCard.jsx`
- `src/components/guitar/GuitarImage.jsx`
- `src/components/wishlist/WishlistRow.jsx`
- `src/data/catalog/reviewedGuitars.json`
- `src/data/guitars.js`
- `src/i18n/en.js`
- `src/i18n/th.js`
- `src/pages/GuitarDetailPage.jsx`
- `src/utils/dataTrust.js`
- `vite.config.js`
- `docs/qa-pacifica-preview/audit-before.json`
- `docs/qa-pacifica-preview/browser-preview.py`
- `docs/qa-pacifica-preview/browser-production.py`
- `docs/qa-pacifica-preview/logs/browser-preview.txt`
- `docs/qa-pacifica-preview/logs/browser-production.txt`
- `docs/qa-pacifica-preview/logs/build.txt`
- `docs/qa-pacifica-preview/logs/catalog-check.txt`
- `docs/qa-pacifica-preview/logs/data-preview-check.txt`
- `docs/qa-pacifica-preview/logs/images-check.txt`
- `docs/qa-pacifica-preview/logs/preview-mode-build.txt`
- `docs/qa-pacifica-preview/manufacturer-evidence.json`
- `docs/qa-pacifica-preview/test-summary.json`
- `scripts/check-pacifica-preview.mjs`
- `scripts/vite/developmentImagePreview.mjs`
- `src/components/guitar/DevelopmentImagePreview.jsx`
- `src/components/guitar/PriceSourceNote.jsx`
- `src/data/additionalSpecifications.js`

เอกสาร `docs/image-intake/yamaha-20.*` จากงานก่อนหน้ายังคงเดิม ไม่รวมใน patch งานนี้
