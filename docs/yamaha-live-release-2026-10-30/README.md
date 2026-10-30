# Yamaha production images — เตรียมเผยแพร่ 30 ตุลาคม 2026

**สถานะ: ยังไม่ Merge และยังไม่ Deploy** — การตรวจความพร้อมเผยแพร่ไม่ผ่าน เพราะ Hosting ยังไม่มีการตั้งค่า Supabase ไม่ข้ามเงื่อนไขนี้เพื่อให้ Build ดูเหมือนพร้อมใช้งานจริง

## สิ่งที่ทำเสร็จและพร้อมตรวจ

- ตรวจทุก Branch ที่เข้าถึงได้หลัง fetch: ทุกงานเป็นบรรพบุรุษของฐาน `7bb9347` ไม่มีงานสำคัญใน Branch อื่นที่ตกหล่นหรือจำเป็นต้องหยิบ commit ซ้ำ
- ใช้ source ล่าสุดที่รวม Ultimate UI, แถบแบรนด์เดิมที่คืนแล้ว, Catalog/Compare, Quiz, Admin Studio และ Practice ไม่ย้อนดีไซน์
- คัดลอกภาพ Yamaha ต้นฉบับ **20 ไฟล์ / 18 รุ่น** ไปยัง `src/assets/guitars/<id>/` และลงทะเบียนใน `src/data/catalog/projectArtwork.json` ตามคำสั่งให้ใช้บนเว็บจริง
- ทุกภาพตรง SHA-256 ของชุดแนบเดิม ไม่ครอป ไม่เปลี่ยนสี ไม่สร้างภาพ ไม่แยก montage และไม่เปลี่ยนรูปเดิม
- Production build ปกติรวมภาพแล้ว ไม่ต้องใช้โหมด Yamaha Preview
- ป้องกันรูปซ้ำเมื่อเปิดโหมด Preview; ภาพ FG820-12 ที่มีอยู่เดิมเป็นภาพแรกตามเดิม
- ทะเบียนภาพเก็บแหล่งที่มาและสถานะตรวจสอบเดิม ไม่เปลี่ยนภาพประกอบจากผู้ใช้ให้กลายเป็นภาพผู้ผลิตหรือภาพที่ยืนยันสิทธิ์แล้ว
- Yamaha ยังมี 20 รุ่น มีรูป **19 รุ่น** เมื่อรวม Pacifica เดิม ส่วน **FGX830C ยังขาดรูปต้นฉบับ** รายการสินค้าและสเปกเดิมยังอยู่ ไม่เพิ่มซ้ำหรือเติมข้อมูล

## ข้อมูลที่รักษา

Catalog 200 ID ไม่ซ้ำ / 10 แบรนด์ × 20 รุ่น / 42 คอร์ดครบ เปรียบเทียบ hash ของข้อมูล runtime ทุกฟิลด์โดยยกเว้นเฉพาะ image/gallery/hasPhotos ที่ได้รับอนุญาตให้เพิ่ม ราคา สเปก คำอธิบาย ชื่อรุ่น แบรนด์ สถานะ และข้อมูลที่บันทึกไว้ไม่เปลี่ยน

ตรวจไฟล์ tracked ก่อนเริ่ม **4,907 ไฟล์** มีเพียงสองไฟล์เดิมที่เปลี่ยน: ทะเบียนภาพ projectArtwork และการรวม gallery เพื่อกันภาพซ้ำ ส่วนไฟล์เดิมอื่นทั้งหมดเหมือนเดิมทุกไบต์ ไม่มีการลบไฟล์ ไม่แก้ Hero, CSS, Navigation, Admin, Auth, Supabase, schema, RLS, migrations, seed หรือระบบ 3D

รายละเอียด: [Data/image guard](tests/data-and-images.json), [Preservation](tests/preservation.json)

## ผลการทดสอบ

| รายการ | ผล |
| --- | --- |
| `npm run build` | ผ่าน มีคำเตือนขนาด chunk Three.js เดิม |
| `npm run catalog:check` | ผ่าน 200 รุ่น / 10 แบรนด์ |
| `npm run images:check` | ผ่าน ต้นฉบับและทะเบียนภาพตรงกัน |
| `node scripts/check-yamaha-publication.mjs --report` | ผ่าน ยืนยัน 20 ภาพ, 18 รุ่น, ไม่มีรูปซ้ำ และข้อมูลเดิมครบทั้ง production และ Preview |
| `npm run admin:check` | 9/9 unit checks; ไม่ใช่การทดสอบธุรกรรม Supabase จริง |
| `npm run deploy:test` | 7/7 unit checks; ไม่ใช่การ Deploy |
| `npm run phase4:check` | 19/19 |
| `npm run phase5:check` | 15/15 |
| `npm run practice:check` | 56/56 |
| Chromium | **98/98 กลุ่มตรวจ** หลังตรวจซ้ำ selector ของ harness 4 กรณี |
| `npm run deploy:check` | **ไม่ผ่าน — ขาด Supabase production configuration** |

Browser ใช้ production build ปกติ ทดสอบ 13 routes ที่มีอยู่, Catalog Yamaha 20 รุ่น/19 รุ่นมีรูป, pagination/ค้นหา/ลิงก์, 20 หน้ารายละเอียด, ภาพต้นฉบับทุกไฟล์เทียบ SHA จาก HTTP response, thumbnail, สเปก/คำอธิบายเต็ม, Compare 4 รุ่นพร้อมรูปและราคาจริง, Favorites บันทึก/refresh/ลบ, Quiz 5 คำถามไปถึงผลลัพธ์จริง, Practice โหลดคอกีตาร์/มือ 3D, เลือกคอร์ดและปุ่มกล้อง/ค้นหา

ขนาดจอ 1440×1000, 1194×834, 768×1024 และ 390×844 ไม่พบ console/runtime errors, image request เสีย หรือ horizontal overflow ในกรณีที่ทดสอบ ตรวจภาษาไทยและการไม่แสดงลิงก์ Admin ให้ผู้ที่ยังไม่ผ่านการตรวจสิทธิ์

ไม่อ้างว่าผ่าน iPad Safari เครื่องจริง หรือผ่าน Login/Publish/Storage ของ Supabase จริง Browser ตรวจได้ว่า Admin แสดงหน้าตั้งค่าการเชื่อมต่ออย่างถูกต้องและไม่มีการเข้าถึงหน้าจัดการโดยยังไม่ตรวจสิทธิ์

กรณีตรวจซ้ำ: script ใช้ selector `.quiz-results` ที่ไม่มีในเว็บ ปรับเป็น class เดิม `.quiz-results-page` แล้วรัน 4 workflow เดิมผ่าน ไม่มีการแก้ source แอปเพื่อให้ผ่าน เก็บผลแรกและผลตรวจซ้ำไว้ใน `tests/`

หลักฐาน: [Browser](browser-results.json), [Core](tests/core-results.json), [Build](tests/build.txt)

ภาพจาก production build จริง: [Desktop](screenshots/desktop-fg800.png), [แท็บเล็ตแนวนอน](screenshots/landscape-fg800.png), [แท็บเล็ตแนวตั้ง](screenshots/portrait-fg800.png), [มือถือ](screenshots/mobile-fg800.png)

## สิ่งที่บล็อกการเผยแพร่

Native Hosting environment query พบ **0 entries** และทั้ง checkout มีเฉพาะ `.env.example` ไม่มีค่าการเชื่อมต่อที่ตั้งไว้ การตรวจ `npm run deploy:check` รายงานว่าขาด:

- `VITE_SUPABASE_URL`: Project URL ของ Supabase Fretline
- `VITE_SUPABASE_PUBLISHABLE_KEY`: Publishable key สำหรับ frontend เท่านั้น ไม่ใช้ Secret/Service Role key
- `VITE_CATALOG_SOURCE=supabase`: เปิดการอ่านเฉพาะ Published data ตามระบบเดิม หลังเชื่อมและตรวจจำนวนข้อมูลจริงแล้ว

[หลักฐาน deployment preflight](tests/deployment-preflight.txt)

จึงยังไม่สามารถยืนยันการล็อกอิน/เพิ่ม/แก้ไข/Publish/อัปโหลดรูป หรือ RPC `get_published_catalog` ว่ามีกีตาร์ 200 รุ่นจริงได้ ไม่สร้างข้อมูลทดสอบหรือเปลี่ยน Data Source เพื่อให้ตรวจผ่าน และไม่เขียน SQL/แก้ฐานข้อมูลโดยพลการ

ผู้ใช้อนุญาต Merge/Deploy ครั้งนี้แล้ว ไม่ต้องขออนุญาตเผยแพร่ซ้ำ แต่ต้องตั้งค่าการเชื่อมต่อและผ่านการตรวจฐานข้อมูลจริงก่อนตามเงื่อนไขให้หยุดเมื่อพบข้อผิดพลาดสำคัญ ไม่ควรส่งค่าลับผ่านแชท

## เวอร์ชันออนไลน์และจุดย้อนกลับ

เว็บเดิมยังเป็น https://fretline-signature-review.vocalwolf36.chatgpt.site — application `a3e770d`, Site version 3, source `0a2d3dc0b42b7216bfe80d849d2d12d379a600d3` และยัง owner-private ไม่เปลี่ยนเป็น public ก่อนตรวจ release พร้อม

- Master ก่อนงานนี้: `9f7b35d7a0daea8a579976a5534ffb67d90f06a9`
- Tag: `backup/fretline-master-before-live-20261030-9f7b35d`
- Tag ก่อนเพิ่มภาพ: `backup/fretline-before-yamaha-publication-20261030-7bb9347`
- งานเตรียมเผยแพร่: `feature/release-yamaha-live-20261030`

ไม่มีการ Merge, Force Push, Deploy หรือขยาย audience ในงานเตรียมนี้ เมื่อการเชื่อมต่อผ่านจึงค่อย Merge master, Build จาก commit ที่ตรวจแล้ว, Deploy ไป Site เดิม, เปิด public ตามคำสั่ง และตรวจแบบผู้เข้าชมไม่ล็อกอิน
