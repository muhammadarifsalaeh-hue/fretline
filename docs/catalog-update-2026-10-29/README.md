# Fretline — อัปเดตแคตตาล็อกและ Compare 29 ตุลาคม 2026

Branch: `feature/catalog-prices-2026-10-29` สร้างจาก `edc293f` ซึ่งเป็นหน้า Home ล่าสุด ไม่มีการ Merge เข้า master

## ผลลัพธ์ข้อมูลจริง

| รายการ | ก่อน | หลัง |
|---|---:|---:|
| รุ่นกีตาร์ / แบรนด์ | 200 / 10 | 200 / 10 |
| จำนวนรุ่นต่อแบรนด์ | 20 | 20 |
| รุ่นที่มีราคา THB พร้อมแหล่งอ้างอิง | 18 | 27 |
| รุ่นที่ต้องสอบถามราคา | 182 | 173 |
| รุ่นที่มีสเปกบางส่วน | 200 | 200 |
| รุ่นที่มีสเปกครบทุกช่องตามรายการที่ขอ | 0 | 0 |

เพิ่มราคาจริง 9 รุ่นของ Fender จากหน้าสินค้า Music Arms ตรงรุ่น ตรวจชื่อรุ่นและ Product JSON-LD Offer ราคา/สกุลเงิน THB วันที่ 2026-10-29 เป็นราคาขายของร้าน ไม่ใช่ราคาขายปลีกแนะนำผู้ผลิต และไม่รับรองสต็อก

- Player II Telecaster, Player II Stratocaster, Player II Mustang: ฿30,600
- Player II Telecaster HH, Player II Stratocaster HSS, Player II Jaguar: ฿31,500
- Player II Modified Stratocaster HSS: ฿39,600
- Player II Modified Stratocaster HSS Floyd Rose: ฿43,200
- Player II Modified Telecaster: ฿37,800

เพิ่มสเปกที่ยังว่าง 9 ช่องใน 2 รุ่น:

- Yamaha FGX830C: bodyShape, top, back, sides, electronics=SYSTEM66 จากตารางผู้ผลิต Yamaha Malaysia แยกคอลัมน์รุ่นจริง
- Fender Player II Stratocaster: bodyShape=Stratocaster, pickupConfiguration=SSS, nutWidthMm=42, fingerboardRadiusMm=241 จากตาราง Music Arms ตรงรุ่น หน้า Fender ตาม URL ในไฟล์ตอบ 403 จึงไม่อ้างว่าเป็นการยืนยันใหม่จากผู้ผลิต

## สิ่งที่รักษาและสิ่งที่ไม่รับเข้า

- ตรวจ JSON รวม + JSON แยกแบรนด์ 10 ไฟล์ + CSV 10 ไฟล์ ทุกชุดตรงกัน 200 IDs ไม่มีรายการซ้ำ อ่าน CSV ที่มี BOM ถูกต้อง
- รักษา ID ลำดับ ชื่อรุ่น แบรนด์ หมวดหมู่ คำอธิบายเดิมที่ละเอียดกว่า รูปภาพ สี รีวิว ราคาเดิมทั้ง 18 รุ่น และสเปกเดิมที่มีค่า
- ZIP มีราคาจริงเพียง 17 รุ่น ไม่ใช่ 200 รุ่น: Yamaha 8 รุ่น (7 ราคาเท่าของเดิม อีก 1 เป็นราคาอีกร้าน) และ Fender 9 รุ่นใหม่
- FG820-12 รักษาราคาหลักเดิม ฿16,500 พร้อมแหล่ง/วันที่เดิม; ฿18,200 เป็นราคาจากอีกร้าน เก็บเป็นหลักฐานในรายงาน ไม่เปลี่ยนราคาหลักเงียบ ๆ
- รักษา Thunderbird ’64 เป็น bass แม้ ZIP ระบุ electric และไม่สร้างหมวด acoustic-electric เพิ่มนอก 4 หมวดเดิม
- ไม่ใช้ Nato/Okume ของ FG800J จากไฟล์ เพราะตารางผู้ผลิตระบุ Nato/Mahogany
- ไม่เปลี่ยนตัวเลือกไม้/ฟิงเกอร์บอร์ด Fender ที่ครอบคลุมหลาย SKU เป็น Alder/Maple เฉพาะสีเดียว และไม่อนุมานจำนวนสายจากชื่อชุดสาย รูปภาพ หรือชื่อรุ่น
- null ช่องว่างและราคาศูนย์ไม่เขียนทับข้อมูลเดิม ไม่ใช้คำอธิบายทั่วไปหรือ Google search เป็นหลักฐานสเปก

## Compare และการแสดงราคา

- รักษาดีไซน์ ตาราง แท็บ ระบบเลือก 2–4 รุ่น แชร์ เพิ่มและลบเดิม
- แสดงแถวที่ขอครบในแท็บหลัก รวมทรงบอดี้ ไม้หน้า/หลัง/ข้าง และอิเล็กทรอนิกส์; สเปกที่ไม่ทราบแสดง “ไม่มีข้อมูล”
- ราคาไม่ยืนยันแสดง “สอบถามราคา” ใน Catalog, Detail, ช่องเลือก Compare และตาราง ไม่แสดงศูนย์บาทแทนราคาที่ไม่ทราบ
- เลขศูนย์ในช่องงบขั้นต่ำยังเป็นงบ ฿0 ที่ถูกต้อง แยกจากราคาสินค้าที่ไม่ทราบ
- เน้นความต่างเมื่อมีข้อมูลที่ยืนยันได้อย่างน้อยสองค่าที่ต่างกัน; ข้อมูลขาดอย่างเดียวไม่ถูกอ้างเป็นความต่างทางกายภาพ และไม่ถูกแสดงว่าเหมือนกัน
- เปรียบเทียบข้อความโดยไม่ถือช่องว่าง/ตัวพิมพ์เป็นความต่าง และใช้สเกลมิลลิเมตรเมื่อมีแหล่งอ้างอิง; ไม่ปัดค่าจากแหล่งต่างกันให้เท่ากันเอง
- แหล่งราคาและวันที่ตรวจแยกจากแหล่งผู้ผลิตเดิม แสดงลิงก์ร้านพร้อมวันที่ในรายละเอียดสินค้า

## ข้อมูลที่ยังขาด

ยังไม่มีรุ่นที่ครบทุกช่องตามรายการ ทั้งเกณฑ์เต็มและเกณฑ์แยกประเภท ไม่ถือว่า null เป็นไม่มีอุปกรณ์หรือไม่เกี่ยวข้อง และไม่ใช้สถานะ partial/verified แทนจำนวนช่องข้อมูลจริง

ช่องสำคัญที่ยังขาด: ทรงบอดี้ 180 รุ่น, จำนวนสาย 149 รุ่น, เฟรต 41 รุ่น, ไม้คอ 2 รุ่น, ปิ๊กอัป 1 รุ่น, อิเล็กทรอนิกส์ 181 รุ่น ราคาขาด 173 รุ่น ดูรายการช่องที่ขาดแยกรุ่นและเกณฑ์ครบที่ [completeness.json](completeness.json) และ [CSV](completeness-by-model.csv)

## ไฟล์แอปที่เปลี่ยน

- `src/data/catalog/reviewedGuitars.json`, `src/data/catalog/phase7Guitars.json`: เติมเฉพาะข้อมูลที่รับเข้า
- `src/components/compare/compareRows.js`, `compareCategories.js`, `CompareTable.jsx`, `ComparisonSlots.jsx`: แถวข้อมูล ข้อมูลขาด การเน้นความต่าง และข้อความราคา
- `src/components/detail/SpecTable.jsx`: ราคาไม่ทราบใช้ข้อความเดียวกัน
- `src/utils/dataTrust.js`: ราคาที่เผยแพร่ต้องผ่านหลักฐาน; รองรับแหล่งราคาจากร้านที่ตรวจใหม่โดยไม่ผูกกับ batch Yamaha เดิม
- `src/i18n/th.js`: ข้อความ “สอบถามราคา”
- `scripts/import-catalog-prices-20261029.mjs`: importer แบบ dry-run เป็นค่าเริ่มต้น พร้อม --apply และ pure merge tests

ไม่เปลี่ยนไฟล์ Home, Hero, แถบแบรนด์, Quiz logic, Practice, CSS หรือ assets ของเว็บไซต์ ตรวจไฟล์ที่ป้องกัน 329 ไฟล์ตรงกับ baseline ทุกไบต์ ดู [preservation.json](preservation.json)

## ผลตรวจ

- Build ผ่าน พร้อมคำเตือนขนาด chunk 3D เดิม ซึ่งไม่ได้แก้ในงานนี้
- catalog:check ผ่าน 200 รุ่น / 10 แบรนด์ × 20; images:check ผ่านโดยไม่เปลี่ยนรูปเดิม
- practice:check 56/56, phase4:check 19/19
- Importer 30/30, Compare fields 15/15, public prices 5/5, independent catalog preservation 9/9
- นำเข้าแล้วรันซ้ำ 0 รุ่น / 0 ช่อง / 0 ไฟล์เปลี่ยน ดู [ผล apply ครั้งแรก](merge-report.json) และ [ผล idempotence](tests/importer-idempotence.json)
- Browser Tests **38/38 ผ่านจริง**: Chromium 154 และ Linux WebKit 26.5 บน Desktop, iPad landscape, iPad portrait และ Mobile แบบจำลอง; Console/runtime/HTTP/request errors 0 และ source/build คงเดิมตลอดการตรวจ ไม่อ้างว่าทดสอบ iPad เครื่องจริง ดู [ผลรวม](tests/browser-summary.json), [รายงาน](tests/browser-report.md), [ภาพหน้าจอจริง](tests/browser-screenshots.html)
- Build HTML SHA-256 ที่ตรวจจริง: `530349624ebd042cedf55c3a217f8017421195bc47027b0a9294486f51761d84`
- รันเฉพาะชุดตรวจที่ระบุ ไม่เขียนทับรายงานเก่าหรือกล่าวอ้างว่าสคริปต์ snapshot เก่าทั้งหมดผ่านกับฐานข้อมูลใหม่

รายละเอียด importer และการแปลงเลข JSON 650.0 เป็น 650 ซึ่งมีค่าเท่ากันอยู่ที่ [importer README](tests/importer-README.md)

## หลักฐาน

- [ตรวจ ZIP และข้อขัดแย้ง](intake-audit.md)
- [ราคา Fender 9 รุ่น](verification/fender-sources.json)
- [สเปก Fender](verification/fender-specs.json)
- [ราคา/สเปก Yamaha](verification/yamaha-sources.json)
- [ข้อมูลก่อน](baseline-effective.json) / [ข้อมูลหลัง](final-effective.json)
- [Core commands และ logs](tests/core/results.json)

## เปิดทดสอบใน Codespaces เดิม

เปิด Terminal ใหม่ใน repository เดิม แล้วใช้ Branch นี้เพื่อทดสอบก่อน Merge:

```bash
git fetch origin
git switch feature/catalog-prices-2026-10-29
git pull --ff-only
```

รีเฟรช Preview พอร์ต 5173 เดิม โดยคง Vite ที่รันอยู่ ไม่มีการตั้งเว็บไซต์ใหม่ เปลี่ยนรูป Home หรือ Merge เข้า master
