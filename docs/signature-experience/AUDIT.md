# Fretline Signature Experience — Audit และขอบเขตความปลอดภัย

ฐานโค้ด: `302ce43def126e4785460c4b0297eae973dbccfb` จาก `feature/fretline-admin-studio` Working Tree สะอาดก่อนเริ่ม งานดีไซน์แยกบน `feature/fretline-signature-experience` ไม่มี Push/Merge/Deploy

## จุดย้อนกลับที่ตรวจแล้ว

- Local tag: `backup/fretline-before-signature-20261029-302ce43` ชี้ไปยัง Commit ฐานแน่นอน
- Source archive: `.local-preview/signature-experience/source-before.tar` ตรวจ SHA-256 ของไฟล์ 4,725 รายการใน archive เทียบไฟล์ต้นฉบับครบทุกไฟล์
- Archive checksum และไฟล์ที่ป้องกันบันทึกใน `safety-baseline.json`
- ไม่มี Uncommitted Change ตอนเริ่ม ไม่ใช้ Reset/Revert และไม่มี Secret ใน Archive: tracked environment file มีเพียง `.env.example`
- ไม่แตะ `.env.local`, Credentials, Supabase Storage, Schema, RLS, Migrations หรือ Seed

## ข้อมูลฐาน

Catalog 200 รุ่น / 200 ID ไม่ซ้ำ, 10 แบรนด์, คอร์ด 42 คอร์ด ราคาที่มีหลักฐาน 27 รุ่น ภาพสินค้าเดิม 3 รุ่น ที่เหลือคงข้อมูลไม่ทราบ/Placeholder ตามเดิม ไม่สร้างรูป ราคา หรือสเปกเพื่อทดแทน

Snapshot ครอบคลุมกีตาร์ทั้งหมดและรายการ Archived เดิม, Brands, Chords รวมชื่อ รุ่น ประเภท คำอธิบาย สเปก ราคา หลักฐาน วันที่ และ Gallery references ทุกช่อง เก็บใน `.local-preview/signature-experience/catalog-before.json` และตรวจ checksum เทียบหลังแก้ด้วย `node scripts/check-signature-safety.mjs`

ไฟล์ที่ป้องกัน 179 ไฟล์รวม `src/data`, Assets, Public Assets/Fonts/Licenses, Admin Studio/Styles/Context, Supabase integration, ทุก SQL, Scene/Geometry/Chord Data, Utils/Hooks, ShopContext, main bootstrap, package/lock และ root Tokens

## Routes ที่ตรวจ

`/`, `/guitars`, `/guitars/:slug`, `/brands`, `/brands/:id`, `/compare`, `/wishlist`, `/find-my-guitar`, `/practice`, `/image-credits`, `/qr`, `*` และ `/admin` ที่คงหน้าตา/การทำงานเดิม

ไม่มี Lint/Typecheck script ในโปรเจกต์นี้ ตรวจ Vite Build, Unit Scripts ที่มี, Browser Regression และ Safety Hash โดยไม่ลบข้อมูลเพื่อแก้ข้อผิดพลาด

## การเชื่อมต่อจริง

Workspace ไม่มีค่าเชื่อม Supabase จึงไม่อ้างว่าสำรองฐาน Cloud หรือทดสอบ Hosted Auth/Upload สำเร็จ Preview Codespaces ล่าสุดที่เจ้าของส่งตอบ 404 จากภายนอก การเปลี่ยนแปลงครั้งนี้เป็น Presentation เท่านั้น ไม่เปลี่ยนแหล่งข้อมูลหรือการเชื่อมต่อ

การทดสอบหน้า Public ใช้ข้อมูลจริงที่มีในโปรเจกต์ตามค่าเดิม ส่วนการตรวจ API/สิทธิ์ด้วย HTTP Fixture จะระบุขอบเขตแยก ไม่ใช้ผลจำลองอ้างว่า Supabase จริงผ่านแล้ว

## แนวทางดีไซน์

Deep Black / Charcoal, Champagne Gold เฉพาะจุดเน้น, Warm Ivory สำหรับข้อความ Anuphan สำหรับภาษาไทยและ Instrument Serif สำหรับชื่อรุ่น/ชื่อแบรนด์ ใช้ภาพเดิมในโปรเจกต์ ไม่มีการสร้างภาพสินค้าแทนรุ่นจริง ภาพประกอบ Yamaha ที่เจ้าของเคยอนุญาตให้นำเข้าไว้ยังคงเดิม พร้อมสถานะรอตรวจสิทธิ์ต้นฉบับ ความตรงรุ่น และชื่อสี ไม่อ้างว่าเป็นภาพสินค้าที่ยืนยันแล้ว และไม่เปลี่ยน Metadata เดิม

Theme ใหม่ครอบด้วย `.fretline-signature` เฉพาะ Public routes หน้า `/admin` อยู่นอก Theme โดยตรง เปรียบเทียบ Screenshot ก่อน/หลังและตรวจ checksum ของโค้ด Admin/Auth ทุกครั้ง

ข้อมูลสินค้าไม่ถูกตัด: คำอธิบายเต็มยังอยู่ในแท็บภาพรวม สเปกและแหล่งข้อมูลอยู่ครบในแท็บ/Accordion รูปทุกใบและ Lightbox ใช้ Gallery เดิม ไม่ซ่อนราคา ข้อจำกัด ความถูกต้อง หรือเครดิตที่ต้องแสดง
