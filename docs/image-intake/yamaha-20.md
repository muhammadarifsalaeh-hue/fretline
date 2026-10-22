# Yamaha — image intake preparation

ตรวจจาก commit `1229c669425f79505f9a9064cc5f28978984a793` วันที่ 2026-10-22 เฉพาะ Catalog หลัก: Yamaha 20 รุ่น มีภาพจริง 1 รุ่นและ Placeholder 19 รุ่น ทั้งเว็บยังมี 200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 รุ่น ไม่มีการค้นหา ดาวน์โหลด เพิ่ม หรือแทนภาพในรอบนี้

| ชื่อรุ่นใน Catalog | Guitar ID | ภาพปัจจุบัน | ชื่อไฟล์รับเข้าแนะนำ |
|---|---|---|---|
| Yamaha Pacifica 612VIIFM | `yamaha-pacifica-612viifm` | Placeholder | `yamaha-pacifica-612viifm-front.webp` |
| Yamaha FG800 Dreadnought | `yamaha-fg800` | Placeholder | `yamaha-fg800-front.webp` |
| Yamaha FG850 | `yamaha-fg850` | Placeholder | `yamaha-fg850-front.webp` |
| Yamaha FG840 | `yamaha-fg840` | Placeholder | `yamaha-fg840-front.webp` |
| Yamaha FG830 | `yamaha-fg830` | Placeholder | `yamaha-fg830-front.webp` |
| Yamaha FG820 | `yamaha-fg820` | Placeholder | `yamaha-fg820-front.webp` |
| Yamaha FG820-12 | `yamaha-fg820-12` | มีภาพจริง | `yamaha-fg820-12-front.webp` |
| Yamaha FG820L | `yamaha-fg820l` | Placeholder | `yamaha-fg820l-front.webp` |
| Yamaha FG800J | `yamaha-fg800j` | Placeholder | `yamaha-fg800j-front.webp` |
| Yamaha FG800M | `yamaha-fg800m` | Placeholder | `yamaha-fg800m-front.webp` |
| Yamaha FS850 | `yamaha-fs850` | Placeholder | `yamaha-fs850-front.webp` |
| Yamaha FS830 | `yamaha-fs830` | Placeholder | `yamaha-fs830-front.webp` |
| Yamaha FS820 | `yamaha-fs820` | Placeholder | `yamaha-fs820-front.webp` |
| Yamaha FS800 | `yamaha-fs800` | Placeholder | `yamaha-fs800-front.webp` |
| Yamaha FGX830C | `yamaha-fgx830c` | Placeholder | `yamaha-fgx830c-front.webp` |
| Yamaha FGX820C | `yamaha-fgx820c` | Placeholder | `yamaha-fgx820c-front.webp` |
| Yamaha FGX800C | `yamaha-fgx800c` | Placeholder | `yamaha-fgx800c-front.webp` |
| Yamaha FSX830C | `yamaha-fsx830c` | Placeholder | `yamaha-fsx830c-front.webp` |
| Yamaha FSX820C | `yamaha-fsx820c` | Placeholder | `yamaha-fsx820c-front.webp` |
| Yamaha FSX800C | `yamaha-fsx800c` | Placeholder | `yamaha-fsx800c-front.webp` |

## ชื่อไฟล์และตำแหน่งจริง

ชื่อในตารางเป็นชื่อรับเข้าที่ไม่ซ้ำกันในชุดไฟล์เดียว ไม่ใช่การเพิ่มระบบจับคู่ภาพอัตโนมัติ เมื่อได้รับภาพและตรวจรุ่น/สิทธิ์แล้ว จะใช้ CSV จับคู่กับ ID เดิม และลงทะเบียนผ่านระบบภาพเดิมที่ `src/assets/guitars/<guitar-id>/01-front.webp` ไม่เพิ่มแถวกีตาร์ใน Catalog

รับไฟล์ JPG, PNG หรือ WebP ได้ หากส่ง PNG/JPG ให้คงนามสกุลจริง เช่น `yamaha-fg830-front.png` ไม่เปลี่ยนนามสกุลเฉย ๆ เป็น WebP การย่อและเข้ารหัสจะทำตอนนำเข้าตามภาพต้นฉบับและเงื่อนไขสิทธิ์ที่ได้รับ ไม่สร้างภาพกีตาร์ใหม่ ไม่ใช้ภาพรุ่นอื่นแทน

มุมเพิ่มเติมใช้ `<guitar-id>-back`, `<guitar-id>-angle`, `<guitar-id>-headstock` และจะแปลงเป็น `02-back.webp`, `03-angle.webp` ฯลฯ ตามมุมที่ได้รับจริงเท่านั้น ส่วนขนาดย่อยเพื่อ performance อยู่ใน `responsive/` และไม่นับเป็นมุมภาพเพิ่ม

FG820-12 มี `01-front.webp` ของ Peternick2468 ภายใต้ CC BY-SA 4.0 อยู่แล้ว ภาพนี้ใส่สายไว้ 6 เส้นตามคำอธิบายผู้ถ่าย แม้มีลูกบิด 12 ตัว ต้องคงเครดิตและข้อจำกัดเดิม ไม่แทนหรือเปลี่ยนภาพหลักอัตโนมัติเมื่อได้รับภาพใหม่

## การรับทีละชุด

1. เลือกส่งเฉพาะบางแถวของ CSV ได้ ชื่อไฟล์/ID ที่ไม่ได้รับภาพยังใช้ Placeholder หรือภาพเดิมต่อไป
2. กรอกชื่อผู้ถ่าย/เจ้าของสิทธิ์ แหล่งที่มา หลักฐานสิทธิ์ให้ Fretline ใช้ เครดิตที่ต้องแสดง และข้อความยืนยันรุ่นในคอลัมน์ว่างของ CSV ช่องว่างไม่ได้ถือว่าได้รับอนุญาตแล้ว
3. ตรวจภาพกับรุ่น/รุ่นย่อยและสิทธิ์ก่อนวางใน runtime assets, บันทึกขนาด SHA-256, alt text, การปรับไฟล์และหลักฐานในทะเบียนภาพ ภาพที่ยังไม่ผ่านตรวจไม่นำไปวางให้เว็บไซต์เผยแพร่
4. เมื่อได้รับคำสั่งให้นำเข้าจริง จึงตรวจ Catalog, Detail, Compare และ Wishlist ด้วยภาพชุดนั้น รวม fallback, lazy loading และ responsive แล้วรัน catalog/images checks อีกครั้ง

## ข้อจำกัดสิทธิ์ของระบบเดิม

ปัจจุบัน `hasImageRights` รับเฉพาะ Creative Commons ที่อยู่ใน allowlist และต้องมี HTTPS source/license URL การเป็นผู้ส่งภาพไม่ทำให้ระบบถือว่าภาพเป็น CC โดยอัตโนมัติ หากเป็นภาพที่ผู้ใช้ถ่ายเองหรืออนุญาตให้ Fretline ใช้โดยเฉพาะ ต้องเก็บหลักฐานและปรับเกณฑ์/เครดิตให้รองรับสิทธิ์นั้นก่อนนำเข้าจริง ไม่บังคับให้ผู้ใช้เปิดภาพเป็น CC และไม่ใส่สัญญาอนุญาตแทนเจ้าของ

ในรอบนี้เตรียมรายการรับภาพและตรวจความพร้อมเท่านั้น ไม่ผ่อนเกณฑ์สิทธิ์หรืออ้างว่าสิทธิ์ทุกแบบรองรับแล้ว

## เส้นทางข้อมูลภาพที่ตรวจจากโค้ด

- `src/data/guitarImages.js`: ค้นไฟล์ตามโฟลเดอร์ ID, ตรวจทะเบียนสิทธิ์, เลือกภาพลำดับแรกเป็น primary และประกอบ gallery/srcset
- `src/data/guitars.js`: `withImages` ผูก `image`, `gallery`, `hasPhotos` จาก ID เดิมให้ข้อมูลที่ทุกหน้าใช้
- Catalog: `CatalogCard` → `GuitarImage` → `SmartImage`
- Guitar Detail: `GuitarGallery` → `GuitarImage` พร้อม thumbnails/lightbox และเครดิต
- Compare: `CompareTable` → `GuitarImage` จากรายการ ID เดิม
- Wishlist: `SAVED_GUITARS_BY_ID` → `WishlistRow` → `GuitarImage`; บันทึก ID ใน localStorage ไม่แยกสำเนารูป
- `SmartImage` ใช้ lazy loading ตามเดิม, ภาพหลัก Detail ใช้ eager, แสดง Placeholder ของรุ่นเดิมเมื่อภาพไม่มีหรือโหลดไม่ได้

## ผลตรวจในรอบนี้

- `npm run catalog:check`: ผ่าน — 200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 ไม่มีรายการซ้ำ
- `npm run images:check`: ผ่าน — รูปที่เผยแพร่ทั้งเว็บมีทะเบียนสิทธิ์และ hash ถูกต้อง
- ตรวจโค้ดการเชื่อมภาพทั้งสี่หน้าตามเส้นทางด้านบน ไม่ได้รันทดสอบ Browser ใหม่ในรอบเตรียมตารางนี้
- ไม่แก้ React, CSS, Context, Router, ข้อมูลกีตาร์ หรือทะเบียนสิทธิ์ และยังไม่ได้เปลี่ยนภาพใด

ข้อควรแยกรุ่น: FG กับ FS, FGX กับ FSX เป็นคนละรุ่น; FG800/FG800J/FG800M ไม่ใช้ภาพแทนกัน; FG820L เป็นรุ่นมือซ้าย และ FG820-12 เป็นรุ่น 12 สาย Pacifica 612VIIFM ต้องตรงรุ่นผู้ผลิต PAC612VIIFM

หยุดรอคำสั่งถัดไปก่อนรับเข้าหรือเผยแพร่ภาพชุดแรก
