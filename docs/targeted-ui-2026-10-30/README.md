# Fretline — Targeted Premium UI Refinement

ทำงานต่อจาก `d8b91b67eb89404dc9be0d2243e8ac6472a4a93f` บน branch ใหม่ `feature/targeted-premium-ui-thai` ไม่มี Push, Deploy หรือ Merge เข้า master ในรอบนี้

## ขอบเขตที่ทำ

- การ์ดประเภทกีตาร์เป็นทรงแคปซูลแนวนอน: 4 คอลัมน์เมื่อกว้างตั้งแต่ 1024px, 2 คอลัมน์บนแท็บเล็ตแนวตั้ง และ 1 คอลัมน์บนโทรศัพท์ ภาพเป็นกีตาร์แยกพื้นหลังจากไฟล์ที่มีอยู่ในโปรเจกต์ ไม่ใช้ภาพห้อง/คน/ฉากจากการ์ดเดิม ไม่ใช้ภาพหน้าจอเป็นพื้นหลัง
- จำนวนรุ่นและลิงก์ยังมาจาก `CATEGORIES` และ Catalog เดิม: ไฟฟ้า 90 / โปร่ง 73 / คลาสสิก 20 / เบส 17 ไม่เขียนจำนวนลงในคอมโพเนนต์
- แบนเนอร์ฝึกใช้ **ไฟล์ Les Paul สีดำที่เจ้าของแนบมาโดยตรง** คัดลอก JPEG ตรงทุก Byte ไม่สร้างหรือแต่งภาพใหม่ วางข้อความ/ไอคอน/ปุ่มเดิมทางซ้าย และภาพทางขวา บนโทรศัพท์จัดภาพเหนือข้อความให้เห็นตัวกีตาร์และกดปุ่มได้ชัดเจน
- รักษาโครงกลุ่มการ์ด Practice / Find My Guitar / Compare เดิม การ์ด Find My Guitar และ Compare ยังใช้ภาพ ปุ่ม และข้อความหลักเดิม เปลี่ยนเฉพาะป้ายภาษาอังกฤษเป็นภาษาไทยตามคำสั่งแปล UI
- แปลข้อความ UI บนหน้าผู้เข้าชมทั้งหมด รวม Catalog, Quiz, Compare, Favorites, แบรนด์, 404 และเครดิตภาพ ส่วน Admin แปลหัวข้อ ปุ่ม สถานะ และข้อความแสดงผล โดยเก็บค่า `draft`, `published`, `publish`, `hide`, ID, API/RPC, URL และคำสั่งเดิม
- ชื่อแบรนด์ รุ่น คอร์ด ศัพท์เทคนิค ค่าข้อมูลสินค้า และชื่อสิทธิ์/ผู้สร้างภาพคงตามต้นฉบับ ประเทศแสดงป้ายภาษาไทย แต่ตัวกรองและ URL ยังคงใช้ `USA` / `Japan` เดิม

ไม่มีการเพิ่ม Theme ครอบเว็บใหม่ ไม่เปลี่ยน Navigation layout, Footer layout, Global typography/colors, ระบบ Gallery, Catalog/Search logic, Compare, Quiz scoring หรือ 3D Trainer

## Hero และความปลอดภัยของข้อมูล

Hero, ภาพสีน้ำเงิน, ปุ่ม, ช่องค้นหา และสถิติยังเป็นคอมโพเนนต์/Stylesheets เดิม แปลเฉพาะ Eyebrow เป็น “ค้นหา · เปรียบเทียบ · ฝึกกีตาร์” ขนาดและพิกัด Hero, หัวข้อ, ปุ่ม, Search, Navigation และสถิติตรงกับก่อนแก้ในช่วงคลาดเคลื่อนไม่เกิน 1px ทั้ง Chromium/WebKit ที่ Desktop, iPad landscape, iPad portrait และ Mobile

`node scripts/check-targeted-ui.mjs` ตรวจ:

- ไฟล์ Runtime/Data/Assets/Backend ที่ป้องกัน **282 ไฟล์** ตรงทุก Hash รวม Hero, ข้อมูลกีตาร์, รูปสินค้า, Brands, Chords, 3D, ShopContext, Auth, Supabase, Schema, RLS, SQL, Seed, Config และ Dependency files
- เปรียบเทียบ AST ของ **22 โมดูลที่อนุญาตให้แปล UI** โดยยกเว้นเฉพาะข้อความแสดงผลและ Formatter ที่กำหนดไว้ ตรวจโครงสร้าง ฟอร์ม Event handlers, Control flow และ API/RPC arguments ให้คงเดิม
- ข้อมูลที่โหลดจริงทุก Field ของกีตาร์ รวมรายการ Archived เดิม, แบรนด์, คอร์ด, คำอธิบาย ราคา สเปก แหล่งอ้างอิง และ Gallery relationships ตรงกับก่อนแก้
- **200 รุ่น / 200 ID / 10 แบรนด์ × 20 รุ่น / 42 คอร์ด / 13 Routes**
- JPEG ที่ใช้ในแบนเนอร์ตรง SHA-256 ของไฟล์แนบต้นฉบับ
- CSS ใหม่มี Scope เฉพาะ Category Cards และ Practice Banner บน Home

หลักฐาน: [safety-baseline.json](safety-baseline.json), [before-layout.json](before-layout.json), [practice-image.json](practice-image.json), [tests/data-safety.json](tests/data-safety.json)

## ภาพที่ใช้จริง

| ส่วน | ไฟล์ | หลักฐาน/บทบาท |
| --- | --- | --- |
| กีตาร์ไฟฟ้า | `src/assets/home-categories/electric-300.webp` | ภาพกีตาร์ไฟฟ้า Fender แบบแยกพื้นหลังเดิม, CC BY-SA 4.0; เป็นภาพประเภท ไม่ใช่หลักฐาน SKU |
| กีตาร์โปร่ง | `src/assets/home-categories/acoustic-231.webp` | ภาพโปร่งสายเหล็กเดิม, CC BY-SA 3.0 |
| กีตาร์คลาสสิก | `src/assets/home-discovery/category-classical-400.webp` | ภาพคลาสสิกสายไนลอนเดิม, CC BY-SA 2.0 DE |
| เบส | `src/assets/home-discovery/category-bass-313.webp` | ภาพเบส 4 สายเดิม พร้อมข้อมูลสิทธิ์เดิม |
| แบนเนอร์ฝึก | `src/assets/home-practice/practice-black-gold-les-paul.jpg` | ไฟล์แนบ `4-รูปภาพ-4.jpg`, 1061×1280; ใช้ประกอบแบนเนอร์ ไม่ผูกเป็นภาพสินค้ารุ่นใด |

ไม่แก้ไฟล์ภาพเดิมหรือ Supabase Storage เครดิต ผู้สร้าง License และข้อจำกัดของภาพยังอยู่ที่ `/image-credits` แปลข้อความประกอบหลักฐานที่รู้จักในชั้นแสดงผล โดยเก็บข้อมูลต้นฉบับและลิงก์สิทธิ์ไว้ครบ

## ผลการตรวจ

| รายการ | ผล |
| --- | --- |
| `npm run build` | ผ่าน; คำเตือนขนาด Three.js chunk เดิมประมาณ 709 kB ยังคงอยู่ |
| Data / scope / UI logic guard | ผ่าน 282 Protected files และ 22 UI modules |
| `npm run admin:check` | 9/9 |
| `npm run deploy:test` | 7/7 — ตรวจสิทธิ์/การตั้งค่าในเครื่อง ไม่ได้ Deploy |
| `npm run phase4:check` | 19/19 |
| `npm run phase5:check` | 15/15 |
| `npm run practice:check` | 56/56 |
| `npm run catalog:check` / `npm run images:check` | ผ่าน จำนวน/ID/แบรนด์และภาพสินค้าเดิมคงครบ |
| ทุก Route และ Responsive | 130/130: 13 เส้นทาง × 5 ขนาด × 2 Engines |
| Catalog/Search/Detail/Compare regression เดิม | 38/38 |
| Quiz/Compare regression เดิม | 31/31: ตัวเลือก 22 ค่าเดิม ครบ 5 คำถาม คะแนนและผลลัพธ์เดิม สูงสุด 4 รุ่น |
| การกดใช้งาน | 22/22: คลิกการ์ดครบ 4 ประเภท, ปุ่ม 3 โหมด, แท็บยอดนิยม, Brand/Country filters, Favorites, Gallery/Lightbox, 3D และตำแหน่งนิ้วเดิม 6 คอร์ด |
| เก็บสีพื้นหลังแบนเนอร์รอบสุดท้าย | Home อีก 10/10: ตรวจ Hero geometry, ภาพ/ข้อความไม่ทับกัน, ขนาด Pill และภาพเต็มกรอบอีกครั้งบน Final build |

ไม่มี Console/Runtime errors ที่ตรวจพบในชุด Browser ที่รายงานผ่าน ไม่พบ Horizontal Overflow ของหน้า พื้นที่เลื่อนรายการและตารางเดิมยังใช้งานได้

ขนาดที่ตรวจ: 1440×1000, 1194×834, 768×1024, 390×844 และ 320×740 ใช้ Chromium และ WebKit; **ยังไม่ได้ทดสอบ Safari บน iPad เครื่องจริง**

ไม่มี Lint/Typecheck script แยกในโปรเจกต์ ไม่ได้รายงานว่าได้รันคำสั่งที่ไม่มีอยู่ หลักฐานใน [tests/](tests/)

## ภาพก่อน/หลังจาก Browser จริง

| ส่วน | ก่อน | หลัง |
| --- | --- | --- |
| Category Desktop | [ก่อน](screenshots/before-desktop-categories.png) | [หลัง](screenshots/after-desktop-categories.png) |
| Practice Desktop | [ก่อน](screenshots/before-desktop-practice.png) | [หลัง](screenshots/after-desktop-practice.png) |
| Category iPad Landscape | [ก่อน](screenshots/before-landscape-categories.png) | [หลัง](screenshots/after-landscape-categories.png) |
| Category iPad Portrait | [ก่อน](screenshots/before-portrait-categories.png) | [หลัง](screenshots/after-portrait-categories.png) |
| Category Mobile | [ก่อน](screenshots/before-mobile-categories.png) | [หลัง](screenshots/after-mobile-categories.png) |
| Practice Mobile | [ก่อน](screenshots/before-mobile-practice.png) | [หลัง](screenshots/after-mobile-practice.png) |
| Home Desktop | [ก่อน](screenshots/before-desktop-home.png) | [หลัง](screenshots/after-desktop-home.png) |
| Home Mobile | [ก่อน](screenshots/before-mobile-home.png) | [หลัง](screenshots/after-mobile-home.png) |

ภาพเฉพาะส่วนซ่อนแถบนำทางแบบตรึงเฉพาะระหว่างจับภาพ เพื่อเห็นการ์ดครบใบ ภาพเต็มหน้ายังคงเมนูจริงไว้ การทดสอบการกดปุ่มและลิงก์ใช้ UI ปกติทั้งหมด ไม่ได้ซ่อนเมนูในขั้นทดสอบการใช้งาน

## จุดสำรองและข้อจำกัด

จุดก่อนแก้: `backup/fretline-before-targeted-ui-20261030-d8b91b6` → `d8b91b67eb89404dc9be0d2243e8ac6472a4a93f` ตรวจ Working tree สะอาดก่อนเริ่ม และเก็บ Hash ไฟล์ Git tracked 4,767 รายการใน `.local-preview/targeted-ui/before-files.json`

ตรวจต้นฉบับใน Worktree แยกได้โดยไม่ลบงานใหม่:

```bash
git worktree add -b feature/review-before-targeted-ui ../fretline-before-targeted-ui backup/fretline-before-targeted-ui-20261030-d8b91b6
```

- ยังไม่มีค่าการเชื่อม Supabase ใน Workspace จึงไม่อ้างว่าทดสอบ Hosted Login/Upload/Publish ผ่านแล้ว โค้ดเชื่อมต่อและฐานข้อมูลไม่ได้เปลี่ยน การตรวจ Admin รอบนี้เป็น Unit/Contract/Display checks
- รูปสินค้าและราคาที่ยังขาดใน Catalog คงสถานะเดิม ไม่สร้างภาพ ราคา หรือสเปกทดแทน
- ยังไม่ Push, Deploy หรือ Merge ดังนั้นลิงก์เว็บทดสอบเดิมยังเป็นเวอร์ชันก่อนการปรับครั้งนี้
- เจ้าของควรตรวจภาพกีตาร์และความหนาแน่นของการ์ดบน iPad จริงก่อนอนุญาตให้เผยแพร่

## ตรวจซ้ำ

```bash
node scripts/check-targeted-ui.mjs
npm run build
npm run preview -- --host 127.0.0.1 --port 4184 --strictPort
```

จากอีก Terminal ที่ติดตั้ง Python Playwright, Chromium และ WebKit แล้ว:

```bash
python docs/targeted-ui-2026-10-30/browser-targeted.py --url http://127.0.0.1:4184 --output .local-preview/targeted-review/routes
python docs/targeted-ui-2026-10-30/browser-interactions.py --url http://127.0.0.1:4184 --output .local-preview/targeted-review/interactions
```

อย่า Build ทับระหว่าง Browser tests ทำงาน รายชื่อไฟล์ที่แก้: [CHANGED-FILES.md](CHANGED-FILES.md)
