# ตรวจค้นและสำรองต้นฉบับ Yamaha — 30 ตุลาคม 2026

ตรวจจากเวอร์ชันล่าสุด `a3e770d7d07f6a10dac9788cd6765c6bf6f028dc` บน Branch งานแยก `feature/recover-yamaha-files-20261030` ไม่ Push, Merge หรือ Deploy และไม่ติดต่อหรือแก้ฐานข้อมูล

## ผลที่ยืนยันจากไฟล์จริง

- พบไฟล์ที่แตกจากชุดแนบเดิม **18 ชุด / 70 ไฟล์**: รูปต้นฉบับ **20 ไฟล์** และ JSON/ข้อความ/เอกสาร **50 ไฟล์**
- ตรวจ SHA-256 และขนาดไฟล์ทั้ง 70 รายการตรงกับ manifest ของการนำเข้าเดิม และสำเนา `.yamaha-intake/` ทุกไฟล์
- นำเข้าครั้งแรกใน Commit `f2168efb6f260194e5732647073b05c8b36fe73a` บน `feature/yamaha-19-import`; commit นี้เป็นบรรพบุรุษของเวอร์ชันล่าสุด
- รูป เอกสาร manifest และข้อมูลสินค้า 18 รุ่นใน `reviewedGuitars.json` **เหมือนตอนนำเข้าทุกไบต์/ทุกฟิลด์** การปรับ UI ล่าสุดไม่ได้ลบต้นฉบับ
- Catalog ฝั่งแอปมี **200 ID ไม่ซ้ำ / 10 แบรนด์ × 20 รุ่น** โดย Yamaha **20 รุ่น** ทุกหน้ามีรายละเอียดและลิงก์ที่ทดสอบได้ ไม่เพิ่มสินค้าซ้ำ
- ในแฟ้ม reviewed มี Yamaha 21 ระเบียนเมื่อรวม C40 ซึ่งเก็บอยู่ใน archive ตามนโยบายเดิม ไม่ใช่จำนวนสินค้า public; ไม่ลบหรือเปลี่ยน archive
- ยังไม่พบชุดแนบต้นฉบับของ **FGX830C (`yamaha-fgx830c`)**: ขาดรูปและไฟล์รายละเอียด/JSON ที่ผู้ใช้ส่ง รุ่นนี้ยังอยู่ใน Catalog พร้อมสเปกอ้างอิงเดิม จึงไม่ต้องสร้างสินค้าใหม่
- ไม่ทราบชื่อไฟล์ FGX830C เดิมที่แน่นอน จึงไม่สร้างชื่อ ZIP หรือชื่อภาพขึ้นมาอ้างว่าเคยได้รับ

## เหตุที่รูปไม่ปรากฏบนเว็บปกติ

โค้ดเดิมใน `vite.config.js` เปิดรูปนำเข้าเหล่านี้เฉพาะ `command === 'serve' && mode === 'yamaha-preview'` ตั้งแต่ก่อนปรับดีไซน์ เมื่อ Build ผลิตจริงหรือรัน dev ปกติ โมดูลภาพชุดนี้เป็น `{}` จึงไม่รวม 20 ภาพในเว็บไซต์

Manifest เดิมบันทึกว่าสิทธิ์เผยแพร่และความตรงรุ่นของชุดภาพยังไม่ได้ยืนยัน (`licenseVerified: false`, `modelMatchVerified: false`) งานตรวจครั้งนี้รักษาค่าและพฤติกรรมเดิม ไม่เปลี่ยนให้เป็นภาพผู้ผลิตหรือภาพที่ตรวจยืนยันแล้ว รูปเป็นภาพประกอบจากผู้ใช้หลายไฟล์ จึงตรวจได้ว่าไฟล์ตรงต้นฉบับ ไม่ใช่รับรองรายละเอียดกีตาร์จากภาพ

| โหมดที่ทดสอบ | Yamaha ใน Catalog | รุ่นที่มีรูปในหน้าเว็บ |
| --- | ---: | ---: |
| Production build ปกติ | 20 | 2: Pacifica และภาพ FG820-12 ที่มีอยู่เดิม |
| Opt-in Yamaha Preview | 20 | 19: 18 รุ่นจากชุดแนบ + Pacifica เดิม |

รูป FG820-12 ที่มีอยู่เดิมยังเป็นรูปแรก และรูปจากไฟล์แนบเป็นรูปเพิ่มเติมเฉพาะ Preview; ไม่แทนที่ภาพเดิม

ข้อมูลชื่อรุ่น คำอธิบาย สเปก และราคาที่มีหลักฐานของทั้ง 18 รุ่นแสดงใน Production อยู่แล้ว ไม่ได้จำกัดเฉพาะ Preview ทดสอบข้อความคำอธิบายเต็มและตารางสเปกใน browser แล้ว ราคาที่ยืนยันได้มี 18/20 รุ่นเมื่อรวม Pacifica; FG800J และ FGX830C ยังแสดง “สอบถามราคา” ตามเดิม ไม่เติมราคา 0 หรือคาดเดาราคา

## หลักฐานรายรุ่น

คอลัมน์ “รูปแนบ” นับไฟล์ภาพจริง ไม่แยกภาพหลายสีที่อยู่ในไฟล์เดียวให้กลายเป็นภาพใหม่

| รุ่น | รูปแนบ | รูปบนเว็บปกติ | รูปใน Preview | สถานะและไฟล์ต้นฉบับ |
| --- | ---: | ---: | ---: | --- |
| Pacifica 612VIIFM | 0 | 4 | 4 | ไฟล์ Pacifica เดิม 4 ภาพ นอกชุดนำเข้า |
| FG800 Dreadnought | 3 | 0 | 3 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fg800-natural.webp](../yamaha-import/preview-assets/yamaha-fg800/01-supplied-yamaha-fg800-natural.webp)<br>[02-supplied-yamaha-fg800-black.webp](../yamaha-import/preview-assets/yamaha-fg800/02-supplied-yamaha-fg800-black.webp)<br>[03-supplied-yamaha-fg800-sunburst.webp](../yamaha-import/preview-assets/yamaha-fg800/03-supplied-yamaha-fg800-sunburst.webp) |
| FG850 | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fg850-mahogany-black.webp](../yamaha-import/preview-assets/yamaha-fg850/01-supplied-yamaha-fg850-mahogany-black.webp) |
| FG840 | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fg840-natural-black-background.webp](../yamaha-import/preview-assets/yamaha-fg840/01-supplied-yamaha-fg840-natural-black-background.webp) |
| FG830 | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fg830-three-colors.jpg](../yamaha-import/preview-assets/yamaha-fg830/01-supplied-yamaha-fg830-three-colors.jpg) |
| FG820 | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fg820-five-colors-black.jpg](../yamaha-import/preview-assets/yamaha-fg820/01-supplied-yamaha-fg820-five-colors-black.jpg) |
| FG820-12 | 1 | 1 | 2 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fg820-12-natural.png](../yamaha-import/preview-assets/yamaha-fg820-12/01-supplied-yamaha-fg820-12-natural.png) |
| FG820L | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fg820l-natural-black-background.png](../yamaha-import/preview-assets/yamaha-fg820l/01-supplied-yamaha-fg820l-natural-black-background.png) |
| FG800J | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fg800j-natural.jpg](../yamaha-import/preview-assets/yamaha-fg800j/01-supplied-yamaha-fg800j-natural.jpg) |
| FG800M | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fg800m-natural-black-background.png](../yamaha-import/preview-assets/yamaha-fg800m/01-supplied-yamaha-fg800m-natural-black-background.png) |
| FS850 | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fs850-black-background.png](../yamaha-import/preview-assets/yamaha-fs850/01-supplied-yamaha-fs850-black-background.png) |
| FS830 | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fs830-three-colors.png](../yamaha-import/preview-assets/yamaha-fs830/01-supplied-yamaha-fs830-three-colors.png) |
| FS820 | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fs820-four-colors.jpg](../yamaha-import/preview-assets/yamaha-fs820/01-supplied-yamaha-fs820-four-colors.jpg) |
| FS800 | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fs800-three-colors.jpg](../yamaha-import/preview-assets/yamaha-fs800/01-supplied-yamaha-fs800-three-colors.jpg) |
| FGX830C | 0 | 0 | 0 | **ยังไม่พบต้นฉบับ FGX830C** |
| FGX820C | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fgx820c-02.png](../yamaha-import/preview-assets/yamaha-fgx820c/01-supplied-yamaha-fgx820c-02.png) |
| FGX800C | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fgx800c-three-colors.jpg](../yamaha-import/preview-assets/yamaha-fgx800c/01-supplied-yamaha-fgx800c-three-colors.jpg) |
| FSX830C | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fsx830c-natural-black.png](../yamaha-import/preview-assets/yamaha-fsx830c/01-supplied-yamaha-fsx830c-natural-black.png) |
| FSX820C | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-yamaha-fsx820c-two-colors.jpg](../yamaha-import/preview-assets/yamaha-fsx820c/01-supplied-yamaha-fsx820c-two-colors.jpg) |
| FSX800C | 1 | 0 | 1 | พบไฟล์แนบเดิม — [01-supplied-FSX800C.jpg](../yamaha-import/preview-assets/yamaha-fsx800c/01-supplied-FSX800C.jpg) |

ดู [รายการไฟล์จริง 70 รายการ พร้อม SHA-256 และเส้นทางเดิม](audit.json) และ [ตาราง 20 รุ่นสำหรับตรวจต่อ](models.csv)

## ขอบเขตการค้นหา

Fetch จาก origin แบบไม่ลบ refs ตรวจทุก local/remote branch ที่เข้าถึงได้ พร้อมประวัติ Git ทั้ง 46 commits และไฟล์ `src/assets`, `public`, Catalog, เอกสาร และโฟลเดอร์ intake ตรวจ ZIP เพิ่มเติมใน workspace 11 ไฟล์ ไม่พบไฟล์ที่มีชื่อ FGX830C และ Git history ไม่มี ZIP ที่ถูกติดตามไว้

Branches หลังนำเข้า เช่น `feature/yamaha-19-import`, `feature/premium-quiz-compare`, `feature/catalog-prices-2026-10-29`, `feature/fretline-admin-studio` และ `feature/fretline-ultimate-experience` เก็บไฟล์ต้นฉบับครบ ส่วน master กับ branch 3D เก่าอยู่ก่อนนำเข้า จึงไม่มีชุดนี้ ไม่ย้อนทั้งเว็บหรือ Merge เพื่อนำไฟล์ซ้ำกลับมา

ไฟล์ ZIP แนบดั้งเดิมไม่อยู่ในพื้นที่แนบปัจจุบัน แต่ไฟล์ที่แตกไว้และสำเนาที่ติดตามด้วย Git ยังอยู่ครบตามรายการที่ได้รับ 18 ชุด จัดชุดสำรอง ZIP ใหม่จากไฟล์เหล่านี้ได้โดยไม่เปลี่ยนเนื้อหา ไม่อ้างว่า ZIP สำรองใหม่เป็น ZIP ดั้งเดิม

## ผลทดสอบครั้งนี้

- `npm run build`: ผ่าน มีคำเตือนขนาด chunk Three.js เดิม ไม่ใช่ error
- `npm run catalog:check` และ `npm run images:check`: ผ่าน
- `node scripts/check-yamaha-recovery.mjs --report`: ผ่าน ตรวจต้นฉบับ, history, Catalog และการผูกรูปจริงในสองโหมด
- `node scripts/check-yamaha-preview.mjs`: 13/13 ผ่าน รวม SHA, MIME, URL, การป้องกัน path traversal และการแยก Preview จาก production
- `node scripts/check-ultimate-experience.mjs`: ผ่าน ข้อมูล/asset/ระบบเดิม 302 ไฟล์, 200 รุ่น, 10 แบรนด์ และ 42 คอร์ดไม่เปลี่ยน
- Chromium: **54/54 กลุ่มตรวจ** ใน production และ Preview ครบ 20 หน้าสินค้าต่อโหมด รวม pagination, ค้นหา, ลิงก์, รายละเอียดเต็ม, ตารางสเปก, SHA ภาพจริง, thumbnail/lightbox และ responsive
- ขนาดจอ 1440×1000, 1194×834, 768×1024 และ 390×844; ไม่พบ console/runtime errors, request รูปเสีย หรือ horizontal overflow ใน workflow ที่ตรวจ
- ไม่ได้ทดสอบ Safari บน iPad จริง และไม่ได้อ่าน/แก้ข้อมูล Published จาก Supabase ของผู้ใช้ จึงไม่รับรองสถานะฐานข้อมูลจริงจากการตรวจ source นี้
- ตรวจ SHA ของไฟล์ tracked ก่อนเริ่ม **4,889 ไฟล์**: ไม่มีไฟล์เดิมเปลี่ยนหรือลบ เพิ่มเฉพาะรายงานและเครื่องมือตรวจครั้งนี้

หลักฐาน: [Browser](browser-results.json), [Data safety](tests/data-safety.json), [Build](tests/build.txt), [การรักษาไฟล์เดิม](preservation.json)

ภาพที่แสดงจาก browser จริง:

- [Production — FG800 บนแท็บเล็ตแนวตั้ง](screenshots/production-tablet-portrait-fg800.png)
- [Preview — FG800 บนแท็บเล็ตแนวตั้ง](screenshots/preview-tablet-portrait-fg800.png)
- [Preview — แท็บเล็ตแนวนอน](screenshots/preview-tablet-landscape-fg800.png)
- [Preview — มือถือ](screenshots/preview-mobile-fg800.png)
- [แผ่นรวมรูปต้นฉบับเดิมทั้ง 20 ไฟล์](../yamaha-import/review/contact-sheet.jpg)

## เปิดตรวจไฟล์แนบโดยไม่ย้อนเวอร์ชันเว็บ

ใช้ checkout เวอร์ชันปัจจุบันที่มี import นี้ ไม่ต้องสลับกลับไป branch เก่า หยุด Vite ตัวเดิมก่อนหาก port 5173 ถูกใช้อยู่ แล้วรัน:

```sh
npm run dev:yamaha-preview -- --host 0.0.0.0 --port 5173 --strictPort
```

ใน Codespaces เปิด **Ports → 5173 → Open in Browser** แล้วใช้ `/guitars?brand=Yamaha` หรือ `/guitars/yamaha-fg800` ปุ่มสเปกแสดงข้อมูลที่นำเข้าอยู่เดิม URL local ในผลทดสอบไม่ใช่ลิงก์สาธารณะสำหรับ iPad และไม่ได้เปลี่ยนเว็บที่ Deploy อยู่

## สิ่งที่ยังขาดและจุดย้อนกลับ

ต้องใช้ไฟล์ต้นฉบับ **FGX830C** เพิ่ม: ภาพและไฟล์รายละเอียด/JSON จากชุดที่ต้องการนำเข้า พร้อมระบุรุ่นให้ตรง ID เดิม เมื่อได้ไฟล์จะเชื่อมรุ่นเดิม ไม่เพิ่มสินค้าใหม่

จุดย้อนกลับก่อนตรวจคือ tag `backup/fretline-before-yamaha-recovery-20261030-a3e770d` → `a3e770d`; source เว็บไซต์ไม่ถูกแก้ จึงไม่ต้องย้อนข้อมูลหรือฐานข้อมูลเพื่อยกเลิกงานตรวจนี้ ไม่มี Push, Merge หรือ Deploy ในงานนี้
