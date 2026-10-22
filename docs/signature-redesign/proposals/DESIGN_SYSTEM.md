# Signature Design System — ข้อเสนอสำหรับตรวจรอบแรก

สถานะปัจจุบัน: **ได้รับอนุมัติและนำไปใช้ใน Phase B** ดู [ระบบ tokens ที่ใช้งานจริง](../../../src/styles/tokens.css) และ [รายงาน Phase B](../phase-b/README.md)

บันทึกตอนเสนอ Phase A: **Proposal ยังไม่ได้นำเข้าเว็บไซต์จริง** `tokens.css` อยู่ในโฟลเดอร์เอกสารและไม่มีการ import จาก `src/main.jsx` หรือ Tailwind config ภาพ Styleboard ไม่ใช่ภาพ After ของ Homepage/Catalog

## ทิศทาง

ให้ภาพกีตาร์เป็นจุดเด่น ใช้พื้นที่ว่างและตัวอักษรสร้างลำดับข้อมูล คงดำ–ทองของ Fretline พร้อมสีข้อความรองที่อ่านง่ายขึ้น ทองอ่อนใช้เฉพาะ CTA หลักหรือสถานะสำคัญ เส้นขอบใช้เพื่อแบ่งกลุ่ม แทนการซ้อน border/ring/glow ทุกใบ

ไฟล์สำหรับตรวจ:

- [Desktop Styleboard](design-system-desktop.png)
- [Tablet Styleboard](design-system-tablet.png)
- [Mobile Styleboard](design-system-mobile.png)
- [เอกสาร HTML](design-system.html) เปิดผ่าน Vite เดิมที่ `/docs/signature-redesign/proposals/design-system.html`
- [Token proposal](tokens.css)

## สี

| Role | ค่าเสนอ | การใช้งาน |
|---|---|---|
| Canvas | `#0A0A0A` | พื้นหลังหลัก คงสีเดิม |
| Surface | `#141414` | กลุ่มเนื้อหา/การ์ด |
| Raised surface | `#1C1C1C` | เมนูและส่วนที่ยกจากพื้น |
| Text | `#F5F5F2` | หัวข้อและข้อมูลหลัก |
| Secondary text | `#B3B3AA` | ข้อความอธิบาย |
| Muted text | `#96968E` | metadata ที่ยังต้องอ่านได้ |
| Accent | `#C8A15A` | เอกลักษณ์ทองเดิม/สถานะเลือก |
| Champagne / Focus | `#E0C58C` | CTA หลักและ focus ring |
| Border | `#2A2A2A` | แบ่งกลุ่มอย่างเบา |
| Strong border | `#46463E` | Controls ที่ต้องเห็นขอบชัด |

ไม่ลด opacity ของข้อความที่ต้องใช้ตัดสินใจเพื่อทำให้ดูหรู ให้แยกน้ำหนักด้วยลำดับ ตำแหน่ง และพื้นผิวแทน เป้าหมายข้อความขนาดปกติอย่างน้อย 4.5:1 และทดสอบคู่สีจริงหลังใช้งาน

## Typography

ใช้ฟอนต์ local เดิม ไม่เพิ่ม font service หรือ dependency

| Role | Desktop | Mobile | ฟอนต์/หลักการ |
|---|---|---|---|
| Display | 64–72px | 44–48px | Instrument Serif สำหรับอังกฤษ / Anuphan สำหรับไทย |
| Page title | 44–48px | 34–38px | แยก role จาก Section |
| Section title | 32–40px | 28–32px | จังหวะเดียวกันทุกหน้า |
| Product name | 22–24px | 20–22px | รักษาชื่อรุ่น อ่านได้หลายบรรทัด |
| Body | 16px / 1.8 | 16px / 1.8 | Anuphan |
| Control / supporting | 14px | 14–16px | ไม่บีบเพื่อใส่ทุกอย่างในบรรทัดเดียว |
| Caption | 13px | 13px | จำกัดไว้ที่ข้อมูลรอง |

ภาษาไทยใช้ line-height ประมาณ 1.4 สำหรับหัวข้อและ tracking ธรรมชาติ หลีกเลี่ยง blanket `!important` ที่เปลี่ยนชื่อรุ่นภาษาอังกฤษด้วย Field บน touch ใช้อย่างน้อย16pxตามแนวทางป้องกัน iOS focus zoom ที่มีอยู่แล้ว ราคาใช้ tabular numbers โดยไม่เปลี่ยนรูปแบบ/ความหมายราคา

## Spacing / Grid / Shape

- Base scale: 4, 8, 12, 16, 24, 32, 48, 64, 96px
- Container: สูงสุด1280px; gutters20 / 32 / 40px พร้อม safe-area ด้านซ้าย–ขวา
- Breakpoints ที่ใช้ตรวจ: 360, 640, 768, 1024, 1280px; ยืนยันที่320และ390pxเพิ่มเติม
- Design grid: 4 columns มือถือ / 8 Tablet / 12 Desktop; จำนวนการ์ดขึ้นกับความกว้างที่อ่านชื่อรุ่นได้ ไม่บังคับทุกหน้าเป็น layout เดียว
- Controls: radius8px, card12px, dialog20px; pill ใช้กับ chips/filters อย่างมีเหตุผล
- Touch target เป้าหมาย44×44px, primary controlสูง48px; แยก visual size จากพื้นที่กดสำหรับ slider/ไอคอน
- Shadow: ใช้2ระดับ คือ card hover และ modal ไม่ซ้อน glow จำนวนมาก

## Shared Components

### Buttons

Primary / Secondary / Quiet / Icon / Destructive มีความสูง การวางไอคอน สถานะ focus/disabled/busy ชุดเดียวกัน ไอคอน18–20pxและช่องไฟ8–12px ปุ่ม Compare/Wishlist คง handlers และ ShopContext เดิม

### Headings

รวมบทบาท Page/Section/Product พร้อม kicker/description ตามจังหวะเดียวกัน ทำให้แต่ละหน้ามีเอกลักษณ์ได้โดยไม่เปลี่ยนความหมาย semantic heading

### Product imagery และ Cards

แสดงกีตาร์เต็มภาพ ยกเลิกการขยาย full-bleed artwork จนตัดขอบ ใช้ border/surface/label feedback แทน กำหนด Editorial/Compact variants ที่มีข้อมูลลำดับเดียวกัน ได้แก่ brand → name → type/available attributes → source-qualified price → actions ไม่เพิ่มราคาหรือรีวิวให้การ์ดดูเต็ม

Styleboard ใช้ภาพและราคา Pacifica ที่มีอยู่จริงในโปรเจกต์ ภาพยังมี provenance เดิม ไม่มีป้าย AI ตกแต่งบนการ์ดหรือรูปหลัก สีในภาพไม่ใช่การเพิ่ม Guitar ID หรือการอ้างชื่อ finish ทางการ

### Fixed navigation และ overlays

ใช้ tokens สำหรับความสูง header, bottom nav, tray, sticky actions และ safe-area ร่วมกัน กำหนด layers: tray40 / nav50 / drawer60 / lightbox80 / toast90 / skip100 ทดสอบการเปิดหลายส่วนร่วมกันก่อนใช้งานจริง

### Motion

Feedback160ms, panel/selection240ms, editorial entrance420ms ใช้ transform/opacity เฉพาะจุด ไม่ animate layout dimensions ทั้ง CSS และ JavaScript scrolling ต้องเคารพ reduced-motion

## แผนนำไปใช้หลังตรวจอนุมัติ

1. นำ tokens เข้าระบบเดิม พร้อม map aliases ของ Tailwind โดยยังไม่จัดหน้า Homepage/Catalog/Detail ใหม่
2. ปรับ Button, IconButton, headings และ focus/readability ให้ใช้ role เดียวกัน
3. ปรับ Navbar/MobileMenu/Footer และ fixed offsets; ตรวจ touch1024pxและ safe-area
4. Build + data/image checks + existing integration regression + responsive screenshots Before/After
5. ส่งจุดตรวจ Shared Components ก่อนเริ่ม Homepage Redesign

ข้อผิดพลาดราคาและภาพที่พบใน Audit ต้องมี regression case ก่อนแก้ การแก้ filter ไม่จำเป็นต้องเปลี่ยนข้อมูลราคาหรือ Guitar ID

## สิ่งที่ไม่ควรเปลี่ยนระหว่างวางรากฐาน

ฐานข้อมูล200รุ่น/10แบรนด์/20ต่อแบรนด์, IDs, manufacturer sources, image registriesและไฟล์ภาพ, Router, ShopContext, สูตร Quiz, storage Wishlist/Compare และภาษาไทยเดิม

การทดสอบต่อไปต้องรายงาน Chrome/Chromium emulation แยกจาก Safari/iPad จริง ห้ามเรียก Styleboard หรือการจำลอง touch ว่าเป็นผลทดสอบ Safari
