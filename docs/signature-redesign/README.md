# Fretline Signature Redesign — จุดตรวจ Audit

สถานะ: **Phase A เสร็จ พร้อมข้อเสนอ Design System สำหรับตรวจ** ยังไม่ได้นำ tokens ไปใช้กับเว็บจริง และยังไม่เริ่ม Redesign Homepage/Catalog/Detail ตามข้อกำหนดให้ตรวจงานก่อนขึ้นขั้นต่อไป

Audit ใช้โปรเจกต์เดิม branch `master`, baseline `82fbe9bdae7cbb9b0d32f356172a37fc7646362a` ตรวจ Remote แล้วตรงกันระหว่างรอบนี้ ไม่ได้สร้าง Vite project ใหม่

## เปิดดูภาพ

- [Design System — Desktop](proposals/design-system-desktop.png)
- [Design System — Tablet](proposals/design-system-tablet.png)
- [Design System — Mobile](proposals/design-system-mobile.png)
- [รายละเอียด tokens และแผนนำไปใช้](proposals/DESIGN_SYSTEM.md)
- [Audit ทุกหน้าและผลทดสอบ](audit/AUDIT.md)

**Styleboard เป็นข้อเสนอ ไม่ใช่ภาพ After ของเว็บไซต์จริง** ภาพ Before ทั้ง36ภาพอยู่ใน `audit/before/` พร้อมหลักฐานปัญหาใน `audit/focused/` รอบนี้ยังไม่มีภาพ After ของเว็บจริงเพราะเป็นจุดตรวจ Audit ก่อนแก้ implementation

## ขอบเขตที่คงเดิม

ข้อมูล200รุ่น / 10แบรนด์ / แบรนด์ละ20รุ่น, IDs, manufacturer source fields, ราคา, สเปก, รีวิว, รูปทั้งหมดและ image metadata, Router, ShopContext, Compare/Wishlist storage และสูตร Quiz

มีเฉพาะเอกสาร ข้อเสนอ tokens และเครื่องมือ/ผล Audit ใต้ `docs/signature-redesign/` ไม่มีการเปลี่ยนไฟล์ `src/`, `public/`, package/dependency หรือ image registries

## ลำดับงานและจุดตรวจถัดไป

1. **Audit** — ผลชุดนี้ พร้อม Before และข้อเสนอ Design System
2. **Design System / Shared Components** — หลังตรวจแนวทาง: tokens, typography, Button/IconButton, focus, loading geometry, Navbar/MobileMenu/Footer และแก้ P1 ที่ตกลงขอบเขต พร้อม Before/After
3. **Homepage** — Hero, Featured Collection, Brands, Quiz/Compare entry points; ตรวจภาพก่อน Catalog
4. **Catalog** — Card variants, grid/search/filter/sort/empty/loading states; เก็บ URL/Back/Forward
5. **Guitar Detail** — Gallery, selectors,ข้อมูล/สเปกและ actions; รักษา Pacifica4ภาพ
6. **Compare / Quiz / Brands / Wishlist** — นำระบบดีไซน์เดียวกันไปใช้โดยคง logic และ context
7. **Interaction / Mobile & iPad** — ตรวจ touch, sticky layers, safe-area, reduced motion ทุกขั้น
8. **Final QA / Performance / SEO** — ทดสอบกับเว็บที่ปรับครบแล้ว รวมการทดสอบ Safari จริงเมื่อมีอุปกรณ์

ทุกขั้น implementation ต้องผ่าน Build, data/image integrity, regression และภาพ Desktop/Tablet/Mobile ก่อนส่งตรวจขั้นถัดไป
