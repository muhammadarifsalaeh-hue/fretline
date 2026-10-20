# เพิ่มกีตาร์ให้ครบ 200 รุ่น (ข้อมูลจริง ไม่ซ้ำ ตรวจสอบได้)

เป้าหมายเดิมของชุดนำเข้า: **200 รุ่นที่แตกต่างกัน** ปัจจุบันมี 36 รุ่นที่ตรวจข้อมูลบางส่วน (`partial`) ไม่มีรุ่นที่ตรวจครบ (`verified`) ดูความคืบหน้าได้ทุกเมื่อ:

```bash
npm run catalog:check           # รายงาน: จำนวนรุ่น / verified / รูปจริง / ภาพสำรอง / รายการซ้ำ
```

## หลักการ (ห้ามข้าม)
1. **ไม่แต่งข้อมูล** สเปก/ราคา/รูป ต้องมาจากแหล่งที่เปิดตรวจสอบได้ ไม่เขียนจากความจำ
2. แหล่งสเปก: หน้าสินค้าทางการของผู้ผลิต หรือตัวแทนจำหน่ายในไทย ใส่ลิงก์ใน `source_url` + วันที่ตรวจ `verified_on`
3. ถ้ายังไม่ได้ตรวจสอบ ให้ใส่ `status = sample` (เว็บจะแสดงว่าเป็นข้อมูลตัวอย่าง) ใส่ `verified` ได้เฉพาะที่มีแหล่งที่มา
4. **รูป**: ใช้เฉพาะรูปของ "รุ่นนั้นจริง ๆ" ที่มีสิทธิ์ใช้ (ได้รับอนุญาตจากผู้ผลิต/Press kit, ไลเซนส์เปิดอย่าง CC, หรือถ่ายเอง) รูปจากหน้าร้านค้าไม่ใช่รูปที่เรามีสิทธิ์นำมาใช้ ไม่มีรูป = ใช้ภาพประกอบสำรองอัตโนมัติ
5. ไม่มีรายการซ้ำ (ตรวจอัตโนมัติจาก แบรนด์ + ชื่อรุ่น)

## ขั้นตอน
1. เปิด `data-template/guitars-template.csv` ด้วย Excel/Google Sheets (แถวที่ `status = example` ถูกข้ามอัตโนมัติ ลบทิ้งได้)
2. กรอกทีละรุ่นตามหัวคอลัมน์
   - `category`: electric / acoustic / classical / bass
   - `price_thb`: ราคาบาท (จำนวนเต็ม) ใช้ราคาจากตัวแทนในไทย
   - `colors`: `ชื่อสี|#hex; ชื่อสีอื่น|#hex`
   - `tags`, `levels`, `styles`: คั่นด้วย `;` (levels: beginner/intermediate/advanced, styles: rock/blues/pop/folk/classical ใช้กับ Quiz)
3. Export เป็น CSV (UTF-8) แล้วนำเข้า
   ```bash
   npm run catalog:import -- รุ่นใหม่.csv --dry-run   # ตรวจก่อน ไม่เขียนไฟล์
   npm run catalog:import -- รุ่นใหม่.csv             # นำเข้าจริง
   ```
   ถ้ามีแถวผิดรูปแบบหรือซ้ำ ระบบจะ **ไม่นำเข้าอะไรเลย** และบอกว่าแถวไหนผิดเพราะอะไร
4. บันทึกข้อมูลที่อ่านยืนยันได้พร้อม `source.fields` ใน `reviewedGuitars.json` ตามส่วน Phase 6 ด้านล่าง การนำเข้า CSV เพียงอย่างเดียวยังไม่ยืนยันข้อเท็จจริง
5. ใส่รูป (ถ้ามี) ที่ `src/assets/guitars/<id>/01-front.webp` (+ มุมอื่น) พร้อมทะเบียนสิทธิ์ใน `imageRights.json` แล้ว `npm run images:check`
6. `npm run catalog:check` แล้วเปิดเว็บดู

ข้อมูลที่นำเข้าจะถูกเก็บใน `src/data/catalog/extraGuitars.json` โดยคงระบบ ID เดิมไว้ เมื่อบันทึกหลักฐานรายฟิลด์แล้ว ข้อมูลที่เผยแพร่จะใช้ร่วมกันใน Catalog, Brands, Compare, Wishlist, Quiz และการค้นหา

## Phase 6: reviewed records and image rights

Legacy demo entries remain in source for their stable IDs. The live catalog reads reviewed overrides from `src/data/catalog/reviewedGuitars.json`. Add an entry keyed by the existing guitar ID, record the manufacturer model/edition, source URL, check date, retrieval method and `source.fields`. Non-null specs must appear in that field list. Unknown values stay `null`; price, reviews and weight are never copied from demo records. Do not promote a record to `verified` because a URL or model photo exists.

Run `npm run catalog:check` to validate the effective catalog, including the reviewed built-in entries, then `npm run phase6:check` for cross-page data invariants. A newly imported model without a reviewed record remains visible with unknown factual fields until its evidence is recorded.

For photos, a file alone is insufficient. First check its exact model/variant and reuse rights, then add `src/data/catalog/imageRights.json` metadata: guitar ID, author, source URL, license and license URL, check date, model-match note, changes, dimensions and SHA-256. Add primary files directly in the model folder and responsive sizes in its `responsive/` subfolder. Responsive versions are not separate gallery angles. All delivered derivatives must retain the applicable license and credit chain. Unregistered files are not published; `npm run images:check` reports them.

The only current accepted image is a CC BY-SA 4.0 owner photograph of Yamaha FG820-12; it shows six strings fitted to a twelve-string model, as noted by its author. Other models retain the existing placeholders.
