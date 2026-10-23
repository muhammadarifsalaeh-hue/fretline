# Fretline Signature Redesign — จุดตรวจ Phase B

สถานะ: **Styleboard ได้รับอนุมัติ และนำ Design System / Shared Components ไปใช้ใน Phase B แล้ว** ดู [รายงานและภาพ Before/After](phase-b/README.md) และ [หน้ารวมภาพเปรียบเทียบ](phase-b/review.html) ก่อนอนุมัติ Phase C: Homepage Redesign

Audit ใช้โปรเจกต์เดิม branch `master`, baseline `82fbe9bdae7cbb9b0d32f356172a37fc7646362a` ตรวจ Remote แล้วตรงกันระหว่างรอบนี้ ไม่ได้สร้าง Vite project ใหม่

## Phase C — ภาพ Homepage รออนุมัติ

[เปิด Mockup Desktop / Mobile และแนวทางเสนอ](phase-c-proposal/README.md) — เอกสารแยกจากแอป ยังไม่ได้แก้ Homepage ตามข้อกำหนดให้อนุมัติภาพก่อน

## เปิดดูภาพ

- [Design System — Desktop](proposals/design-system-desktop.png)
- [Design System — Tablet](proposals/design-system-tablet.png)
- [Design System — Mobile](proposals/design-system-mobile.png)
- [รายละเอียด tokens และแผนนำไปใช้](proposals/DESIGN_SYSTEM.md)
- [Audit ทุกหน้าและผลทดสอบ](audit/AUDIT.md)

**Styleboard คือภาพแนวทางที่อนุมัติ** ภาพเว็บไซต์จริง Before อยู่ใน `audit/before/` และ After อยู่ใน `phase-b/after/` จำนวน36ภาพต่อชุด พร้อมผลตรวจ Responsive 53 มุมมอง

## ขอบเขตที่คงเดิม

ข้อมูล200รุ่น / 10แบรนด์ / แบรนด์ละ20รุ่น, IDs, manufacturer source fields, ราคา, สเปก, รีวิว, รูปทั้งหมดและ image metadata, Router, ShopContext, Compare/Wishlist storage และสูตร Quiz

Phase A เก็บหลักฐานเดิมไว้ ส่วน Phase B ปรับ `src/` และ Tailwind สำหรับระบบดีไซน์ร่วม ไม่มีการเปลี่ยน package/dependency, catalog data หรือ image registries; ค่า SHA-256 ของไฟล์ข้อมูล/ภาพที่ตรวจ25ไฟล์ยังตรงกับ baseline

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
