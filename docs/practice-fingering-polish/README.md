# Fretline — ผลพัฒนา Guitar Practice Studio

**มือ 3D ผ่านเกณฑ์เมชและสัมผัสสาย 13/42 คอร์ด จากเดิม 7 คอร์ด เพิ่ม 6 คอร์ด: B7, C7, Dm7, Dsus2, G7, Gmaj7 งานตำแหน่งมือยังไม่เสร็จครบ 42 คอร์ด อีก 29 คอร์ดใช้ผังคอร์ดเดิมและซ่อนมือที่ไม่ผ่าน**

การตรวจเมชตรวจจาก GLB มือและแขนเสื้อสีดำต้นฉบับ รวมผิวมือและเสื้อ ไม่ใช่เฉพาะจุดบนกระดูกหรือรูปภาพ ทุกคอร์ดตรวจด้วยกฎเดิม: self/guitar triangle crossings ต้องเป็น 0, ตรวจผิวไม้แบบ dense, สายเปิดเว้นอย่างน้อย 0.2 mm และผิวฝ่ามือของนิ้วที่ระบุอยู่ภายในระยะสัมผัส 0.12 mm คงข้อมูลสาย เฟรต หมายเลขนิ้ว และคอร์ดเดิมทั้งหมด

**ยังไม่มีท่าใดได้รับการรับรอง anatomical/teaching จากผู้สอนอิสระ** การแสดงมือเหมาะสำหรับสาธิตระบบ 3D และดูร่วมกับผังคอร์ดเดิม ไม่อ้างว่าทั้ง 42 ท่าหรือท่าใดผ่านการรับรองเพื่อฝึกตามมืออย่างเดียว

## สิ่งที่เปลี่ยน

- รวมท่าที่ผ่านใหม่เข้ากับ pose library ของเว็บจริงบน branch ล่าสุด โดยรักษา 7 ท่าเดิมทุกค่าและคงท่าที่ถูกปฏิเสธไว้ในข้อมูลเบื้องหลัง
- เอากล่องสถานะการพัฒนาและคำเตือนรอตรวจทานออกจาก Canvas และแถวสถานะ ไม่ปิดระบบตรวจสอบ
- ปุ่มแสดง/ซ่อนมือแบบเรียบง่าย มีเฉพาะท่าที่ผ่านเมชและสัมผัสสาย ปุ่มหมุน ซูม และมุมกล้องเดิมยังอยู่ครบ
- ปรับแถวควบคุมให้กะทัดรัดบน Mobile ข้อผิดพลาดโหลดมือแสดงสั้น ๆ พร้อมปุ่มลองใหม่อยู่นอก Canvas
- เครื่องมือ authoring อ่าน baseline จาก Git อย่างปลอดภัย และนำท่าที่ทำสำเร็จแล้วกลับมาใช้เป็นฐานผ่านรายงานตรวจจริงได้ โดยไม่ Reset หรือแก้ runtime ระหว่างคำนวณ

## ผลทดสอบ

| การตรวจ | ผล |
|---|---|
| Production Build | ผ่าน มีคำเตือนขนาด chunk เกิน 500 kB ที่มีอยู่เดิม |
| Public routes / Catalog / Yamaha / Compare / Favorites / Quiz / Practice / หน้า Admin แบบผู้เยี่ยมชม | 98/98 ผ่าน บน 4 ขนาดหน้าจอ |
| WebGL / GLB จริง / เลือกครบ 42 / กล้อง / ลาก / จีบซูม / Reduced Motion / Error Recovery | 23/23 ผ่าน |
| ข้อมูลคอร์ดและเรขาคณิตพื้นฐาน | 56/56 ผ่าน |
| Runtime hand gates และ resource lifecycle | 20/20 ผ่าน |
| Animation reveal / Reduced Motion | 10/10 ผ่าน |
| Admin data tests ออฟไลน์ | 9/9 ผ่าน ไม่ใช่การทดสอบ CRUD บน Supabase จริง |
| Exact mesh audit | ตรวจครบ 42: 13 ผ่าน, 29 ไม่ผ่านและไม่เปิดแสดงมือ |
| ข้อมูลสินค้า | 200 ID ไม่ซ้ำ, 10 แบรนด์ แบรนด์ละ 20; checksum ข้อมูล/ราคา/สเปก/รูป/คอร์ดเหมือนเดิม |
| Console / Runtime / Broken Image errors ใน regression ปกติ | 0 |

ทดสอบ Chromium ที่ 1440×1000, 1194×834, 768×1024 และ 390×844 พร้อม touch events จริงผ่าน browser automation ยังไม่ได้ทดสอบ Safari บน iPad เครื่องจริง ไม่มีการตั้งค่า Hosting หรือ Supabase หรือเขียนฐานข้อมูลในงานนี้

ตรวจรูปเดิมผ่าน `npm run images:check`: 20 รุ่นมีภาพที่ลงทะเบียน อีก 180 รุ่นใช้ placeholder เดิม เป็นช่องว่างข้อมูลที่มีอยู่ก่อน ไม่ได้แทนรูปด้วยรุ่นอื่น ไม่มี dedicated lint/typecheck script ใน package.json; ตรวจ Build, Git diff whitespace และ Python compilation เพิ่มเติมแล้ว

## หลักฐาน

- [ผลรายคอร์ดครบ 42](CHORD-STATUS-42.md)
- [ผลตรวจเมชจริงรอบสุดท้าย](tests/geometry/summary.json)
- [การปรับและตรวจ 35 คอร์ดที่เหลือ](tests/attempts-35.json) พร้อม candidate, raw crossings และ summary ใน `attempts/`
- [ท่าที่นำเข้าและหลักฐานรายท่า](accepted/)
- [ยืนยันข้อมูลเดิมและขอบเขตไฟล์](tests/data-safety.json)
- [ผล Browser 3D](tests/browser-hand.json), [ผลระบบเดิม](browser-results.json), [Build log](tests/build-final.txt)
- [ตรวจการนำท่าที่ทำสำเร็จแล้วกลับมาใช้](tests/pinned-shared-context.json)
- [ภาพหลายมุมของท่าใหม่](tests/new-pose-captures.json)

ผล `testSuitePassed` ของชุด geometry หมายถึงท่าที่อนุญาตให้แสดงผ่านเกณฑ์ และท่าที่ไม่ผ่านไม่ถูกติดป้าย verified **ไม่ได้หมายความว่าทั้ง 42 ท่าผ่าน** รายงานเก่าชุด 10 ท่าเก็บไว้ใน `tests/checkpoint-10-*` แยกจากผลสุดท้าย

## ภาพก่อนและหลัง

ภาพก่อนมาจาก commit 218eab5 (รายละเอียด hash ใน `tests/before-provenance.json`) ภาพหลังจับจาก Production Build จริง ไม่มีการสร้างหรือแต่งภาพโมเดลขึ้นแทน

| ขนาด | ก่อน | หลัง |
|---|---|---|
| iPad แนวนอน | [ดูภาพ](screenshots/before-landscape.png) | [ดูภาพ](screenshots/after-landscape.png) |
| iPad แนวตั้ง | [ดูภาพ](screenshots/before-portrait.png) | [ดูภาพ](screenshots/after-portrait.png) |
| Mobile | [ดูภาพ](screenshots/before-mobile.png) | [ดูภาพ](screenshots/after-mobile.png) |
| Desktop | [ดูภาพ](screenshots/before-desktop.png) | [ดูภาพ](screenshots/after-desktop.png) |

## เปิดบน iPad

ทำตาม [คู่มือเปิด Codespaces และสาธิต](IPAD-DEMO.md) ดึง branch `feature/restore-black-sleeved-hand` แล้วรัน Vite ด้วย `--host 0.0.0.0 --port 5173 --strictPort` จาก `/workspaces/fretline` จึงเปิด `/practice?chord=C` ผ่านแท็บ Ports → Open in Browser ไม่ต้อง Deploy

## ไฟล์โค้ดที่เปลี่ยน

- `scripts/check-hand-runtime.mjs`
- `scripts/check-practice-fingering.mjs`
- `scripts/practice/fit-missing-poses.py`
- `scripts/practice/import-audited-poses.py`
- `scripts/practice/lift-pose.py`
- `scripts/practice/repair-pose-batch.py`
- `scripts/practice/source-pose-context.py`
- `src/features/practice/assets/hand-poses.json`
- `src/features/practice/components/GuitarNeckViewer.jsx`
- `src/features/practice/components/viewer.css`

เอกสาร รายงาน raw audit และภาพหน้าจอทั้งหมดอยู่ใน `docs/practice-fingering-polish/` ไม่เปลี่ยน Home, Brand Marquee, Admin Studio, database/schema/.env, ข้อมูลสินค้า หรือ dependency

## ทำงานตำแหน่งมือที่เหลือต่อ

ใช้ Python NumPy/SciPy และ Node dependencies เดิม เครื่องมือ authoring ใช้ commit 218eab5 เป็น baseline ที่ตรวจ hash ไว้ และ adopt ท่าที่สำเร็จแล้วทั้งหมดจาก `accepted/` ผ่าน exact reports โดยไม่แตะ runtime:

```bash
python scripts/practice/repair-pose-batch.py --chords Em --output .local-preview/next-em --shared docs/practice-fingering-polish/accepted --iterations 80 --rounds 3 --seconds 120 --all-fingers --full-polish
```

นี่เป็นการสร้าง candidate ต้องผ่าน `scripts/practice/check-hand-geometry.py` บนเมชจริงทุกครั้งก่อนนำเข้า การ convergence ของ optimizer ไม่ใช่ผลผ่าน ท่าที่ไม่ผ่านเก็บไว้เป็นหลักฐานและไม่เปิดเผยใน UI ข้อผิดพลาดตัวช่วยคำนวณ D7 เมื่อไม่มีหน้าผิวใกล้สายได้รับการแก้แล้ว เก็บ trace ก่อนแก้ใน `tests/d7-resolved-authoring-error.json`; D7 รอบตรวจจริงยังไม่ผ่านและยังซ่อนมือ

ระบบตรวจอนุมัติอัตโนมัติปฏิเสธข้อเสนอเร่ง broad phase ของตัวตรวจการชน เพราะเสี่ยงพลาดการชน จึงใช้ตัวตรวจเดิมต่อ ไม่มีการเปลี่ยน tolerance หรือกฎยอมรับเพื่อเพิ่มจำนวนคอร์ด

## จุดย้อนกลับ

Branch: `feature/restore-black-sleeved-hand` · baseline: `218eab5a1b72125b7981b01ebe8aa417dd58fef7` · tag: `backup/fretline-before-practice-fingering-218eab5`

ตรวจเวอร์ชันสำรองในโฟลเดอร์แยกได้ด้วย `git worktree add --detach /tmp/fretline-practice-before backup/fretline-before-practice-fingering-218eab5` โดยไม่เปลี่ยนไฟล์งานปัจจุบัน ไม่มี Reset, Force Push, Merge master หรือ Deploy ในงานนี้
