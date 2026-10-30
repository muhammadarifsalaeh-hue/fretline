# Fretline — Signature Experience

> งาน Signature นี้ถูกยกเลิกตามคำขอเจ้าของ และคืนดีไซน์ก่อนเริ่มแล้ว ดู [บันทึกการคืนดีไซน์](RESTORATION.md) รายงานด้านล่างเป็นประวัติของงาน Signature

ปรับดีไซน์ฝั่งผู้เข้าชมบน `feature/fretline-signature-experience` จากฐาน `302ce43def126e4785460c4b0297eae973dbccfb` ของ `feature/fretline-admin-studio` ไม่ Push, Merge หรือ Deploy งานนี้

## สิ่งที่เปลี่ยน

ใช้ Deep Black, Charcoal, Champagne Gold และ Warm Ivory พร้อม Anuphan สำหรับภาษาไทย และ Instrument Serif สำหรับชื่อรุ่น ปรับสัดส่วนและพื้นที่ว่างแยกตามงานของแต่ละหน้า ใช้ภาพและโลโก้เดิม ไม่เพิ่มภาพสินค้าหรือข้อมูลสมมติ

| ส่วน | ผลลัพธ์ |
| --- | --- |
| ระบบกลาง | สีและ Typography เฉพาะ Public routes, Navigation, Mobile Drawer/Bottom Bar, ปุ่ม ช่องกรอก Dialog, Skeleton, Focus และการเปลี่ยนหน้า |
| หน้าแรก | Hero ขนาดแคมเปญพร้อมภาพเดิม 3 ภาพ, สถิติ, Marquee โลโก้จริง, หมวดกีตาร์แบบภาพใหญ่, Practice ซ้าย/ค้นหาและเปรียบเทียบขวา, คอลเลกชันยอดนิยมเดิม |
| แบรนด์ | การจัดภาพและโลโก้แบบ Editorial, ค้นหา/กรองแบรนด์ และหน้ารุ่นทั้งหมดของแบรนด์ |
| แคตตาล็อก | Product Gallery พร้อม Search, Filters, Sort, Pagination และ Empty State เดิม |
| รายละเอียดกีตาร์ | ภาพหลักขนาดใหญ่, Thumbnail แนวนอน, Lightbox, ชื่อรุ่น/ราคา/การกระทำที่ชัดเจน ข้อมูลเต็มยังอยู่ในแท็บเดิม |
| เปรียบเทียบ | พื้นที่เลือก 4 รุ่น, ตารางและหมวดสเปกเดิม เน้นแถวที่มีข้อมูลแตกต่างโดยใช้ผลการคำนวณเดิม |
| ค้นหากีตาร์ที่ใช่ | หัวข้อไทย, Progress, การเลือกคำตอบและ Transition พร้อมคำถาม ตัวเลือก คะแนน และผลลัพธ์เดิมทั้งหมด |
| รายการโปรด | คอลเลกชันส่วนตัวแบบสองคอลัมน์บนจอกว้าง, รายการเต็มความกว้างบนมือถือ พร้อมบันทึก/ลบ/เปรียบเทียบและหน้าต่างยืนยันเดิม |
| โหมดฝึก | ขยายคอกีตาร์ 3D, จัดรายละเอียดคอร์ด/นิ้ว/สาย/เฟรตให้อ่านง่าย และ Library 7/5/3 คอลัมน์ตามจอ ไม่แก้ข้อมูลหรือโมเดล |
| เส้นทางอื่น | หน้าเครดิตภาพ, QR และ 404 ใช้ระบบเดียวกัน ไม่เพิ่ม Route ใหม่ |

UI ใช้ภาษาไทยเป็นหลัก คงชื่อแบรนด์ รุ่น และชื่อคอร์ดไว้ แปลข้อความการปรับไฟล์ภาพเดิมสำหรับผู้เข้าชม โดยคง Author, Source, License และข้อกำหนด CC BY-SA ทั้งหมด ข้อมูลต้นฉบับในไฟล์สิทธิ์และ Metadata ไม่เปลี่ยน

Motion ใช้ Opacity/Transform อย่างจำกัด รองรับ `prefers-reduced-motion` และใช้ระบบปัด/ลาก/เลื่อนเดิม ไม่มี Animation library หรือ Dependency ใหม่

## การรักษาข้อมูลและ Admin

- กีตาร์ **200 รุ่น / 200 ID**, **10 แบรนด์ × 20 รุ่น**, คอร์ด **42 คอร์ด**
- จำนวนหมวดจากข้อมูลจริง: ไฟฟ้า 90, โปร่ง 73, คลาสสิก 20, เบส 17
- ราคาอ้างอิง 27 รุ่น; อีก 173 รุ่นยังใช้สถานะสอบถามราคาตามข้อมูลเดิม
- เก็บทุก Field ของข้อมูลกีตาร์ รวม Archived entries, Brands, Chords, ราคา หลักฐาน วันที่ คำอธิบาย สเปก และความสัมพันธ์ Gallery ตรวจ SHA-256 ของข้อมูลที่โหลดจริงเทียบก่อนแก้ตรงกันทั้งหมด
- ไฟล์ที่ป้องกัน 179 ไฟล์ยังตรงกับฐาน รวม Admin/Auth, ShopContext, Supabase integration, SQL, Data, Assets, 3D/Chord logic, Utils/Hooks, Bootstrap และ Package/Lock
- ทุก Route เดิม 13 สัญญายังคงเดิม หน้า Admin อยู่นอก `.fretline-signature` โดยตรง ภาพ Admin ก่อน/หลังตรงกันทุกพิกเซลใน Chromium ทั้ง Desktop และ Mobile
- ไม่แก้ฐานข้อมูล, Schema, RLS, Migrations, Seed, Credentials หรือ Environment files และไม่ได้รัน SQL

รายละเอียด Audit: [AUDIT.md](AUDIT.md) และ [Safety baseline](safety-baseline.json)

## ผลทดสอบ

| การตรวจ | ผล |
| --- | --- |
| `npm run build` | ผ่าน; มีคำเตือนขนาด Chunk ของ Three.js เดิมประมาณ 709 kB |
| `node scripts/check-signature-safety.mjs` | ผ่าน: 179 Protected files, ทุก Field ของข้อมูลตรงกัน, Routes เดิมครบ |
| `npm run catalog:check` | ผ่าน: 200 รุ่น / 10 แบรนด์ × 20 |
| `npm run images:check` | ผ่านการลงทะเบียนและ SHA-256 ของไฟล์ภาพเดิม |
| `npm run admin:check` | 9/9 เป็นการทดสอบข้อมูล/Validation ในเครื่อง |
| `npm run phase4:check` | 19/19 Quiz และ Compare |
| `npm run phase5:check` | 15/15 แบรนด์และรายการโปรด |
| `npm run practice:check` | 56/56 ข้อมูลคอร์ดและ Geometry |
| `npm run deploy:test` | 7/7 การตั้งค่าและ Access checks ในเครื่อง ไม่มีการ Deploy |
| `python scripts/test-supabase-setup.py` | 13/13 ใช้ HTTP mocks ภายในเท่านั้น ไม่เชื่อม/เปลี่ยนฐานจริง |
| Browser routes | 130/130: 13 Routes × 5 ขนาด × Chromium/WebKit |
| Catalog browser regression เดิม | 38/38: Catalog, Search, Filters, Sort, ราคา, Detail และ Compare |
| Quiz/Compare browser regression เดิม | 31/31: 22 ตัวเลือกเดิม, ครบ 5 คำถาม, คะแนน/คำอธิบายเดิม, เพิ่ม/ลบ/แชร์/จำกัด 4 รุ่น |
| Signature interactions | 22/22: Marquee/ลาก, Hero, หมวด/แท็บ, แบรนด์, Favorites persistence, Gallery/Lightbox, คอร์ด 6 ชุดเทียบตำแหน่งนิ้วเดิม, 3D และปุ่มกล้อง |
| Public accessibility/composition | 8/8: Skip link, เมนูมือถือ/คืน Focus, Reduced motion, การจัดการ์ด, เครดิตภาพและข้อความผู้เข้าชม |

Browser suites ที่รายงานผ่านไม่มี Console/Runtime errors ที่ตรวจพบ ไม่พบ Horizontal Overflow ของหน้า (พื้นที่เลื่อนการ์ดและตารางยังเลื่อนได้ตามปกติ)

ขนาดที่ตรวจ: 1440×1000, 1194×834, 768×1024, 390×844 และ 320×740 การทดสอบ WebKit เป็น Browser automation ในเครื่อง **ยังไม่ใช่ Safari บน iPad จริง**

สคริปต์ Phase 5 เก่าเคยสมมติว่าทุกแบรนด์ไม่มีราคาและโลโก้ ซึ่งขัดกับฐานที่นำเข้าราคาไปแล้ว แก้เฉพาะการทดสอบให้ตรวจช่วงราคาที่มีหลักฐานและทดสอบลำดับราคา/ราคาไม่ทราบด้วย Fixture ไม่ลบราคาหรือแก้ข้อมูลเพื่อให้ Test ผ่าน

โปรเจกต์ไม่มี Script สำหรับ Lint/Typecheck แยก จึงไม่รายงานว่าได้รันคำสั่งที่ไม่มีอยู่

หลักฐานใน [tests/](tests/) และภาพใน [screenshots/](screenshots/)

## ภาพก่อนและหลัง

| ภาพ | ก่อน | หลัง |
| --- | --- | --- |
| หน้าแรก Desktop | [ก่อน](screenshots/before-desktop-home.png) | [หลัง](screenshots/after-desktop-home.png) |
| หน้าแรก Mobile | [ก่อน](screenshots/before-mobile-home.png) | [หลัง](screenshots/after-mobile-home.png) |
| การ์ดสามโหมด | — | [แนวนอน](screenshots/after-ipad-landscape-modes.png) · [แนวตั้ง](screenshots/after-ipad-portrait-modes.png) |

ภาพหน้าอื่น: [แบรนด์](screenshots/after-desktop-brands.png), [Catalog](screenshots/after-desktop-catalog.png), [รายละเอียด](screenshots/after-desktop-detail.png), [Compare](screenshots/after-desktop-compare.png), [Quiz](screenshots/after-mobile-quiz.png), [Practice](screenshots/after-desktop-practice.png)

## ข้อจำกัดและงานที่ยังต้องตรวจจริง

1. Workspace ไม่มีค่าการเชื่อม Supabase จึงยังยืนยัน Hosted Login, Upload, Publish หรือการอ่าน Published ของฐานจริงไม่ได้ โค้ดเชื่อมต่อและข้อมูลไม่เปลี่ยน ต้องทดสอบกับโปรเจกต์ของเจ้าของก่อนรับรองการใช้งานจริง
2. รูปสินค้าเดิมลงทะเบียน 3 รุ่น: ภาพที่มีข้อมูลสิทธิ์ 2 รุ่น และภาพประกอบ Yamaha ที่เจ้าของเคยจัดหา 1 รุ่น อีก 197 รุ่นยังไม่มีรูป ไม่ใช้ภาพรุ่นอื่นหรือสร้างภาพแทน รายการอยู่ใน [IMAGE-GAPS.md](IMAGE-GAPS.md)
3. ภาพประกอบ Yamaha 4 ใบยังมี Metadata เดิมว่ารอการยืนยันสิทธิ์ต้นฉบับ ความตรงรุ่น และชื่อสี คงข้อจำกัดนี้ไว้ในหน้าข้อมูลภาพ ไม่อ้างว่าเป็นภาพผู้ผลิตที่ยืนยันแล้ว
4. ข้อมูลสเปกยังมีช่องไม่ทราบและสถานะ Partial ตามฐานเดิมทั้งหมด ไม่อนุมานข้อมูลใหม่
5. Preview ใช้ตรวจในเครื่องที่ `http://127.0.0.1:4184` เท่านั้น ไม่ใช่ลิงก์สาธารณะ URL Codespaces เดิมที่เจ้าของเคยให้ตอบ 404 จากภายนอก จึงไม่มีลิงก์สาธารณะใหม่ที่ยืนยันได้ งานนี้ยังไม่ Push/Deploy ตามคำสั่ง

## ตรวจซ้ำ

```bash
npm run build
node scripts/check-signature-safety.mjs
npm run preview -- --host 127.0.0.1 --port 4184 --strictPort
```

จากอีก Terminal ที่มี Python Playwright, Chromium และ WebKit:

```bash
python docs/signature-experience/browser-routes.py --url http://127.0.0.1:4184 --output .local-preview/signature-review/routes
python docs/signature-experience/browser-interactions.py --url http://127.0.0.1:4184 --output .local-preview/signature-review/interactions
python docs/signature-experience/browser-accessibility.py --url http://127.0.0.1:4184 --output .local-preview/signature-review/accessibility
```

สคริปต์ Browser ใช้ Chromium ที่ `/usr/bin/chromium` และ WebKit จาก Playwright ต้องติดตั้ง Browser dependencies ก่อนในเครื่องอื่น ชุด Routes ใช้ Pillow เพื่อเปรียบเทียบภาพ Admin ได้ด้วย `--before .local-preview/signature-experience/before` เมื่อมีชุดภาพ Audit เดิม ส่วน Interactions อ่านข้อมูลจริงผ่าน Vite SSR และตรวจ Baseline ได้แม้ไม่มี Snapshot ที่เก็บเฉพาะในเครื่อง

อย่า Build ทับระหว่าง Browser suite ทำงาน เพราะไฟล์ Chunk ที่เปลี่ยนชื่ออาจทำให้ผลทดสอบคลาดเคลื่อน

## วิธีคืนดีไซน์เดิมโดยรักษางานใหม่

จุดย้อนกลับที่ตรวจแล้ว: `backup/fretline-before-signature-20261029-302ce43` → `302ce43def126e4785460c4b0297eae973dbccfb`

เปิดต้นฉบับใน Worktree ใหม่ โดยไม่แตะ Working tree หรือ Branch งานดีไซน์:

```bash
git worktree add -b feature/fretline-before-signature-review ../fretline-before-signature backup/fretline-before-signature-20261029-302ce43
```

สำรองอิสระอีกชุด: `.local-preview/signature-experience/source-before.tar` ขนาด 1,064,519,680 bytes ตรวจไฟล์ Git tracked ทั้ง 4,725 รายการครบก่อนแก้ ไม่มี Runtime secrets ในชุดสำรอง

SHA-256: `441252b25870f34f362d1f510aa0bb2110ccbfdd6fac9df7a80dcf77e2bfadb9`

Tag และ Archive อยู่เฉพาะ Workspace นี้ ยังไม่ได้ Push/Upload การย้อนกลับเป็นงาน Source/Presentation เท่านั้น งานนี้ไม่ได้เปลี่ยนฐานข้อมูลจึงไม่ต้องรัน SQL Rollback

รายชื่อไฟล์: [CHANGED-FILES.md](CHANGED-FILES.md)
