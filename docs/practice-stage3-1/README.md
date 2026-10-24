# Stage 3.1 — แก้ Rig บางส่วนแล้ว แต่ C Major ยังไม่ผ่าน

วันที่ตรวจ: 24 ตุลาคม 2026 · Branch `feature/guitar-practice-3d` · Baseline `3e4b21e`.

**ยังไม่สำเร็จตามเกณฑ์ Stage 3.1 และยังไม่นำมือเข้า `/practice`.** รอบนี้แก้ไฟล์
Skin Weights จริงและเตรียม Blender Workspace แล้ว แต่ยังแก้ท่า C ทั้งมือให้ไม่ชน
สาย/คอและมีท่านิ้วโป้งเป็นธรรมชาติไม่ได้ จึงหยุดตามเงื่อนไขที่ผู้ใช้กำหนด.
ไม่มีการเริ่ม Stage 4, Merge หรือ Push เข้า master.

## สิ่งที่แก้จริง

- ตรวจ Skeleton 21 กระดูก, Bone Hierarchy, แกนข้อต่อ และน้ำหนักผิวจากไฟล์จริง.
- สร้าง Weight Patch สองขั้นสำหรับรอยพับข้อนิ้วและโคนนิ้ว โดยใช้เมชมือเดิม
  ไม่ซ่อนนิ้ว ไม่เปลี่ยนเป็นทรงกระบอก และไม่ใช้ภาพ 2D แทนมือ.
- V2 เปลี่ยนน้ำหนัก 918 จุดของเมชต้นฉบับ หรือ 998 จุดเมื่อรวม UV Seams ใน GLB;
  จำกัดไม่เกิน 4 กระดูกต่อจุดและ Normalize. ตำแหน่งจุด, UV, Normal, สามเหลี่ยม,
  Skeleton และเมชเล็บเหมือนเดิมทุกไบต์ ตาม [Integrity Report](research/weight-patch-v2-integrity.json).
- แก้จุดอ้างอิงนิ้วโป้งที่เดิมอยู่ใกล้ขอบเล็บ และทดลอง Palmar Surface Patch
  แทนการบังคับจุดปลายกระดูกให้ชนคออย่างเดียว.
- ทดลองทิศทางข้อมือและจุดสัมผัสหลายชุด ตรวจเมชทั้งมือ/เล็บหลังส่งออกจริง.
  ท่าที่จุดสัมผัสตรงแต่ส่วนอื่นทะลุไม้กว่า 10 มม. ถูกปฏิเสธ ไม่ได้นำไปแสดงว่าแก้สำเร็จ.
- เตรียมไฟล์ Blender ที่แก้ต่อได้ มีมือ Rigged, Weight V2, กีตาร์จริงในฉากเดียวกัน,
  Texture แบบ Packed, กล้อง 4 มุม และข้อความกำกับสถานะยังไม่ผ่าน.
- แก้ Winding กลับด้านที่พบระหว่างทดสอบ Export และแยก Grayscale Height Texture
  ที่ Blender Exporter ผูกผิดเป็น Normal Map ออกไว้ใน Metadata. ไม่แก้ภาพหรือซ่อนเมช.

ไฟล์โมเดลที่แก้:

- [GLB — Weight V2 ยังไม่อนุมัติท่า C](models/hand-weight-repaired-v2-UNAPPROVED.glb)
- [Blender — Workspace สำหรับแก้ท่าและผิวต่อ](models/Fretline-C-Major-Repair-UNAPPROVED.blend)
- [ท่า C ที่ใช้ถ่ายภาพตรวจสอบ ยังไม่ผ่าน](research/C-pose-UNAPPROVED.json)
- [บันทึกวิเคราะห์ Rig และวิธีสร้าง Weight Patch](research/RIG-ANATOMY-REPAIR-NOTES.md)

## ผลตรวจที่ยังไม่ผ่าน

เปรียบเทียบ **ท่าเดียวกันกับ GLB จริง** เพื่อแยกผลของ Skin Weights:

| โมเดล | คู่สามเหลี่ยมผิวมือที่ตัดกัน |
| --- | ---: |
| น้ำหนักเดิม | 133 |
| Weight V1 | 127 |
| Weight V2 | 113 |

นี่คือการแก้ได้บางส่วน ไม่ใช่การกำจัดรอยซ้อนทั้งหมด. ตัวเลข 402 คู่จาก Stage 3
ใช้คนละท่า จึงไม่นำมาอ้างเป็นเปอร์เซ็นต์ความสำเร็จของ Weight Patch.

| การตรวจ C ในภาพส่งงาน | ผล |
| --- | --- |
| นิ้วชี้ B เฟรต 1 | อยู่ในบริเวณนิ้วที่ถูกต้อง แต่จุดกดที่กำหนดยังลอยประมาณ 0.155 มม. |
| นิ้วกลาง D เฟรต 2 / นิ้วนาง A เฟรต 3 | จุดสัมผัสใกล้เป้าหมาย แต่ทางเดินสายและผิวส่วนอื่นยังชน |
| สาย G เปิด | ไม่ผ่าน — ช่องว่างท่อสายกับผิวต่ำสุด −0.217 มม. |
| สาย e เปิด | ผ่านในท่านี้ — ช่องว่างประมาณ 3.739 มม. |
| นิ้วโป้ง | ไม่พบเล็บตัดไม้จริงใน Snapshot นี้ แต่ทิศอุ้งนิ้วยังไม่ถูกต้องเป็นธรรมชาติ |
| ผิวมือซ้อนกัน | ยังมี 113 คู่สามเหลี่ยม |
| เมชมือกับกีตาร์ | ยังมี 161 คู่สามเหลี่ยมตัดกัน รวมสายและบอร์ด; ไม่ใช่ 161 เหตุการณ์แยกกัน |
| E ต่ำ | ผังคอร์ดระบุไม่ดีด; การทะลุท่อสายที่พบยังเป็นข้อบกพร่องทางภาพ/เรขาคณิต |

[ผลตรวจเต็มและพิกัดหลักฐาน](research/FINAL-AUDIT-SUMMARY.json) เก็บทั้ง Triangle
Intersections, ผิวที่อยู่ภายใน Solid และระยะถึงสาย ไม่ถือว่าจุดกึ่งกลางนิ้วตรง
หรือ GLB Validator ผ่านแล้วแปลว่าจับคอร์ดถูกต้อง.

การทดสอบผิวละเอียดพบความต่างเล็กน้อยระหว่างรูปคอแบบสมการกับคอที่สร้างเป็น
สามเหลี่ยม จึงตรวจเมชกีตาร์จริงซ้ำด้วย ไม่ใช้ Tolerance กลบข้อบกพร่องที่ยังเห็นอยู่.
ท่าและรอยพับในภาพยังไม่ถึงระดับความสมจริงของ Reference.

## ภาพจริง 4 มุม

ภาพจากฉาก Three.js ที่ใช้ GLB V2 และกีตาร์ร่วมฉากจริง มีป้าย UNVALIDATED ชัดเจน.
เป็นเครื่องมือตรวจ Research แยกจากเว็บที่เผยแพร่ ไม่ใช่ภาพ Mockup และไม่ใช่ท่า C ที่อนุมัติ.

| มุม | Linux WebKit | Chromium |
| --- | --- | --- |
| ด้านหน้า | [Front](screenshots/webkit-front.png) | [Front](screenshots/chromium-front.png) |
| ด้านข้าง | [Side](screenshots/webkit-side.png) | [Side](screenshots/chromium-side.png) |
| ด้านหลังคอ | [Back](screenshots/webkit-back.png) | [Back](screenshots/chromium-back.png) |
| มุมผู้เล่น | [Player](screenshots/webkit-player.png) | [Player](screenshots/chromium-player.png) |

กล้องด้านหน้าใช้ +Z เป็นด้านสาย E ต่ำที่อยู่ด้านบน ไม่กลับภาพเพื่อทำให้ท่ามือผิด
ดูเหมือนถูกต้อง. ภาพ Capture ตรงกับพิกัด GLB ที่ตรวจการชน คลาดเคลื่อนสูงสุด
ประมาณ 0.000012 มม. จากการเทียบจุดผิวจริงใน Three.js กับเครื่องมือตรวจอิสระ.

## Build และ Regression ของเว็บเดิม

| รายการ | ผล |
| --- | --- |
| `npm run build` | [ผ่าน](tests/build.txt); คงคำเตือน Three.js Chunk 589 KB ที่โหลดเฉพาะ Practice |
| `npm run catalog:check` | [ผ่าน](tests/catalog.txt): 200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 |
| `npm run images:check` | [ผ่าน](tests/images.txt) |
| `npm run practice:check` | [13/13 ผ่าน](tests/practice.txt) |
| Shared UI / Catalog / Compare / Quiz / Wishlist | [18/18 ผ่าน](tests/shared-regression.json) |
| Gallery และฟังก์ชันเดิม | [79/79 ผ่าน](tests/gallery-regression.json) |
| Practice ใน WebKit รอบแรก | [14/15](tests/initial-browser-webkit.json): Desktop แรกรอ Loading เกิน 30 วินาที; ไม่มี Console/Network Error |
| Practice รันซ้ำแยกจากงาน Capture | [15/15 ผ่าน](tests/recheck-browser-webkit.json); ไม่ยืนยันสาเหตุ Timeout จากการรันเดียว |
| ฉากตรวจโมเดล | Chromium และ Linux WebKit ผ่าน 4 มุม × 1440/1024/390/320px ต่อ Engine; Orbit/Zoom/Reset/Touch ไม่มี Console/Network Error |
| GLB Weight V2 | [Khronos 0 Errors / 3 Warnings](research/weight-patch-v2-validation.json); เป็นการตรวจรูปแบบไฟล์ ไม่ใช่ท่าทาง |
| Protected Source | [208 ไฟล์เหมือน Baseline ทุกไบต์](tests/protected-source.json) |
| ท่า C พร้อมใช้งานสอน | **ไม่ผ่าน** |

ไม่มี iPad จริงหรือ macOS Safari ให้ทดสอบ Linux WebKit ไม่ใช่การรับรอง iPadOS,
Frame Rate, GPU Memory, อุณหภูมิ หรือแบตเตอรี่. Performance ของมือใหม่ในเว็บ
Production ยังไม่สามารถรับรองได้ เพราะยังไม่นำเข้า App.

## ข้อแก้ไขในการตรวจสอบ

ระหว่างตรวจพบว่า Helper ทดสอบ MCP ชุดหนึ่งใส่ค่า Euler ทั้งที่กระดูกยังอยู่ในโหมด
Quaternion ทำให้ตัวเลขผ่านบางชุดไม่ถูกต้อง. ถอนผลชุดนั้นและรันใหม่โดยตั้ง XYZ
ทุกกระดูกแล้ว ผลใหม่ตรงกับ GLB จริงที่ 113 คู่. **ไม่ได้แก้โคนนิ้วทั้งหมดสำเร็จ**.
รายงานใช้ผลแก้ไขแล้วเท่านั้น.

Blender ที่ติดตั้งคือ 4.3.2 ขณะที่ไฟล์ผู้สร้างเขียนด้วย 4.5 มีคำเตือนความเข้ากันได้.
ไม่ได้สรุปว่า Rig ของผู้สร้างเสียในทุกสภาพแวดล้อม; ผลนี้คือสิ่งที่ตรวจได้จริงในรอบนี้.

## ขั้นตอนแก้ใน Blender และทางเลือก

1. เปิด Workspace ที่ให้ เลือก `C_MAJOR_REPAIR_RIG` และเข้า Pose Mode. โหมดหมุน
   ของกระดูกถูกตั้ง XYZ และใช้ Weight สูงสุด 4 อิทธิพลให้ตรง GLB.
2. ปรับทิศข้อมือและอุ้งมือทั้งชุดก่อน โดยให้มือซ้ายเข้าหาคออย่างเป็นธรรมชาติ.
   ตรวจ Front/Side/Back/Player ไม่พยายามแก้ด้วยการกดจุดปลายนิ้วผ่านไม้.
3. ใช้ผิวอุ้งนิ้วโป้งจริงแทนขอบเล็บ ตรวจนิ้วชี้สาย B เฟรต 1 / นิ้วกลางสาย D เฟรต 2 / นิ้วนางสาย A เฟรต 3,
   เปิด G/e และไม่ดีด E ต่ำ. Guide Empties ในไฟล์เป็นจุดอ้างอิง ไม่ใช่ IK Controllers.
4. แก้ Weight Paint และสร้าง Corrective Shapes ที่รักษากายวิภาคสำหรับรอยพับ
   MCP/Web ที่ยังซ้อนกัน ไม่ซ่อนนิ้วหรือแทนส่วนใดด้วยภาพ.
5. ส่งออกไฟล์แยก แล้วตรวจผิว GLB จริงอีกครั้ง รวม Winding, Height/Normal Binding,
   นิ้วลอย สายเปิด และทางเดินสายทั้งเส้น ก่อนพิจารณานำเข้า `/practice`.

ถ้าต้องการไปต่อด้วยคุณภาพตาม Reference แนะนำให้ให้ผู้ทำโมเดลปรับไฟล์นี้ใน
Blender หรือเปลี่ยนเป็น Rig มือซ้ายที่มี Corrective Deformation สำหรับการจับ
เครื่องดนตรี พร้อมสิทธิ์ใช้งานที่เหมาะสม. เครื่องมืออัตโนมัติที่ทดลองรอบนี้ยัง
ทำให้ C Major ผ่านทุกข้อไม่ได้ จึงหยุดก่อนเริ่ม Stage 4 ตามคำสั่ง.

## แหล่งที่มาและสิทธิ์

Hand ©2026 **Emma L. D. Lieker**, [anatomical-hand-model](https://github.com/emmalieker/anatomical-hand-model/tree/f27f19f55f8270b3108ea0b53ce5aa81c543ff7c),
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
[ใบอนุญาต](research/HAND-CC-BY-NC-4.0.txt) และ
[รายการดัดแปลง](research/HAND-MODIFICATIONS.txt) ต้องอยู่กับไฟล์ที่ส่งต่อ.
การใช้งานนี้เป็นงานการศึกษาที่ไม่แสวงหากำไร ไม่ใช่ใบอนุญาตใช้เชิงพาณิชย์.
Three.js ใช้ MIT ตาม Dependencies เดิม ไม่ได้เพิ่ม Runtime Dependencies.

ไฟล์ที่เพิ่มอยู่ใน `docs/practice-stage3-1/` เท่านั้น. Homepage, Brands, Catalog,
Compare, Wishlist, Quiz, ข้อมูลกีตาร์, Guitar IDs และสิทธิ์ภาพสินค้าเดิมไม่ได้แก้ไข.
