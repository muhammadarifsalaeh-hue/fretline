# เพิ่มกีตาร์ให้ครบ 200 รุ่น (ข้อมูลจริง ไม่ซ้ำ ตรวจสอบได้)

Phase 7 มี **200 รุ่นพอดี จาก 10 แบรนด์ แบรนด์ละ 20 รุ่น** ทั้งหมดตรวจบางส่วน (`partial`) ไม่มีรุ่นที่ตรวจครบ (`verified`) ดูความคืบหน้าได้ทุกเมื่อ:

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

For licensed photos, record `src/data/catalog/imageRights.json` metadata: guitar ID, author, source URL, license and license URL, check date, model-match note, changes, dimensions and SHA-256. User-supplied artwork explicitly requested for project use is registered separately in `src/data/catalog/projectArtwork.json`; preserve its source and editing history without claiming license or manufacturer verification. Add primary files directly in the model folder and responsive sizes in its `responsive/` subfolder. Responsive versions are not separate gallery angles. Licensed derivatives retain the applicable credit chain. Unregistered files are not published; `npm run images:check` reports them.

The accepted images are CC BY-SA 4.0 owner photographs of Yamaha FG820-12 and Martin D-28. The Yamaha photo shows six strings fitted to a twelve-string model, as noted by its author. The D-28 photo dates from 2018, its production year is unknown, and it does not illustrate the current Golden Era specification edition. Keep those caveats visible and do not infer specifications from either photograph. Other models retain the existing placeholders.

## Phase 7: exact quotas and archived records

- `catalogPolicy.json` records the approved brands, exact 200-model target and 20-per-brand quota. Changing the target is a product decision; do not change it merely to make a failed check pass.
- `phase7Guitars.json` contains 166 new source-scoped records. The 34 retained originals continue to use their previous IDs and reviewed overrides.
- `archivedGuitars.json` is the complete backup of Gretsch G2420 and Yamaha C40, including the previous published snapshot, legacy source text and original source metadata. Do not delete or silently substitute these IDs.
- `GUITARS` and `GUITARS_BY_ID` contain active models only. Brand totals, catalog filters and quiz recommendations use that same collection.
- `SAVED_GUITARS_BY_ID` also resolves the two archived records for old Detail URLs, Wishlist and shared Compare links. The UI explicitly marks these records as archived. They never increase the 200-model catalog total.
- The CSV importer checks duplicates across active and archived IDs, rejects unapproved brands and rejects imports above either quota. At 200 models, adding another model requires an approved replacement plan; do not append records silently.
- `npm run catalog:check` enforces exact totals, not just a minimum. `npm run phase7:check` additionally checks archived sources, old saved IDs, actual manufacturer retrieval metadata and source scopes. Existing Phase 4–6 checks remain available.
- Do not create quiz experience/style profiles just to boost new models' scores. Missing profiles remain explicitly unknown under the original scoring rules.

See [the 200-model source register](PHASE_7_CATALOG.md) and [Phase 7 report](PHASE_7_REPORT.md).

## Phase 9: field-level rechecks without changing identities

The first batch reviews only 20 existing models, two per brand. Use reviewed overrides even for Phase 7 additions; do not edit the historical import or replace IDs. Record successful retrieval metadata, model/edition limitations, `source.recheckedFields` and any `source.retainedFields`. Detailed evidence in `docs/qa-phase9/field-evidence.json` distinguishes freshly checked, retained and unknown fields. A retained field is not a fresh verification claim.

Run `npm run phase9:check` in addition to the existing checks. The check reconstructs the Phase 8 catalog from Git and protects all 180 models outside the approved batch. Its explicit boundary must be reviewed for any separately authorized future batch. Keep the existing fully verified criteria; missing prices, weights or other required evidence mean a record stays partial. See the [batch report and source tables](qa-phase9/README.md).
