# Stage 3 — ผลตรวจความเป็นไปได้ของมือจับ C Major

วันที่ตรวจ: **24 ตุลาคม 2026** · Branch: `feature/guitar-practice-3d`.
Baseline: `ef2df44fa0f368a6e82cb72058a970f5f2600e88`.

**Stage 3 ยังไม่ผ่านเกณฑ์นำเข้าเว็บไซต์** พบโมเดลมือที่มีรูปทรงทางกายวิภาคและ
Rig จริงแล้ว แต่ท่า C ที่ทดลองยังชนสายเปิด คอ และผิวมือด้วยกัน จึงหยุดที่การตรวจ
ความเป็นไปได้ตามข้อกำหนดของผู้ใช้ ไม่ได้นำท่าที่ผิดไปแสดงเป็นบทเรียนใน `/practice`.
หน้าเว็บยังเป็น Stage 1–2 และไม่มีการ Merge หรือ Push เข้า `master`.

## งานที่ทำจริง

- ตรวจประวัติและ Fetch ทั้ง `master` กับ feature branch แล้ว Feature ตรงกับ Remote
  และ Working Tree สะอาดก่อนเริ่มรอบนี้ Master ยังเป็น `9f7b35d`.
- ตรวจโมเดลมือ 4 แหล่ง พร้อมใบอนุญาตและข้อจำกัด รายละเอียดใน
  [asset audit](research/asset-audit.json).
- ทดลองโมเดลมือมนุษย์ที่เป็น Skinned Mesh จริง: 21 กระดูก, มือและเล็บแยกกัน,
  5,790 สามเหลี่ยม ไม่ได้ใช้แท่งเรขาคณิตหรือภาพถ่ายแทนมือ.
- สร้างคอกีตาร์ทดลองที่มีไม้แบบ Procedural, คอ D, ฟิงเกอร์บอร์ดโค้ง,
  เฟรตโลหะ, นัตมีร่อง, สายต่างขนาด และลูกบิด 3+3 จริงในฉาก Three.js เดียวกับมือ.
  นี่เป็นโมเดลเพื่อศึกษา ไม่ใช่สเปกหรือภาพกีตาร์ใน Catalog.
- ทดลองเฉพาะท่า C Major: นิ้วชี้สาย 2 เฟรต 1, นิ้วกลางสาย 4 เฟรต 2,
  นิ้วนางสาย 5 เฟรต 3; สาย G และ E สูงเปิด, ไม่เล่น E ต่ำ.
- ลดไฟล์ทดลอง 12,291,880 → 3,363,120 ไบต์ โดย Accessor ของเมช/Rig ไม่เปลี่ยน.
  ภาพผิวสามชุดลดเหลือ 1024px; Map เล็บที่เป็นสีคงที่แทนด้วยค่า Material.
  การลดไฟล์ไม่ได้แก้ท่ามือหรือรอยพับที่ผิด.
- สร้าง **เครื่องมือตรวจฉากแยกเฉพาะ Research** มี Orbit/Zoom และมุม Front,
  Side, Player, Context ใช้ GLB และแสง/PBR จริง ไม่มีการแทน Canvas ด้วยภาพ.
  เครื่องมือนี้ไม่ใช่ Route ใหม่และไม่ใช่เว็บ Fretline เวอร์ชันเผยแพร่.

## ภาพจริงสำหรับตรวจปัญหา

ภาพต่อไปนี้จับจาก **Linux WebKit ที่แสดงฉาก Research จริง** ไม่ใช่ Mockup หรือ
ภาพเรนเดอร์ของผู้สร้างโมเดล ป้าย FAILED ในภาพระบุว่าท่านี้ยังใช้สอนไม่ได้.
ภาพแสดงรายละเอียดผิว/รอยพับที่ยังไม่ถึงคุณภาพ Reference และไม่ได้อ้างว่ามือสมจริงสมบูรณ์แล้ว.

| มุม | ภาพ |
| --- | --- |
| ด้านหน้า | [Front](screenshots/inspection/webkit-failed-contact-front.png) |
| ด้านข้าง | [Side](screenshots/inspection/webkit-failed-contact-side.png) |
| ผู้เล่น | [Player](screenshots/inspection/webkit-failed-contact-player.png) |
| คอกีตาร์และมือร่วมฉาก | [Context](screenshots/inspection/webkit-failed-contact-context.png) |

Hand ©2026 **Emma L. D. Lieker**, [anatomical-hand-model](https://github.com/emmalieker/anatomical-hand-model),
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
การดัดแปลงในภาพ: สะท้อนเป็นมือซ้าย, ท่า C ทดลอง, ลดขนาด Texture, แก้การใช้
Grayscale Height Map เป็น Bump แทน Normal Map, จัดแสงและกล้องใหม่.
ใช้ตรวจงานการศึกษาที่ไม่แสวงหากำไร ไม่ได้ถือเป็นใบอนุญาตใช้งานเชิงพาณิชย์.

## เกณฑ์ตำแหน่งมือ: ไม่ผ่าน

ตรวจเมช **GLB ที่ส่งออกจริงและใช้น้ำหนัก 4 กระดูกต่อจุด** ไม่ได้สรุปจากการดูภาพ
หรือวัดเฉพาะจุดกึ่งกลางปลายนิ้ว ใช้ผิวมือ/เล็บกว่า 350,000 จุดตัวอย่าง,
BVH ของสามเหลี่ยม และตรวจเส้นสายทุก 0.1 มม.

| การตรวจ | ผลจริง |
| --- | --- |
| ผิวมือชนเนื้อไม้ | ทะลุอย่างน้อย **0.190 มม.** ณจุดตัวอย่างที่บันทึกไว้ |
| เล็บนิ้วโป้งชนคอ | ทะลุอย่างน้อย **0.798 มม.** |
| สาย G ซึ่งต้องปล่อยเปิด | ผิวมือชนท่อสาย ช่องว่างต่ำสุด **−0.215 มม.** มีความเสี่ยงดับเสียง |
| สาย E สูงเปิด | ผ่านในท่านี้ ช่องว่างผิวต่ำสุดประมาณ **3.534 มม.** |
| เมชมือซ้อนตัวเอง | ยืนยัน **402 คู่สามเหลี่ยม** ไม่ใช่ 402 เหตุการณ์ทางกายวิภาคแยกกัน |
| จุดปลายนิ้วที่เลือก | ใกล้เป้าหมาย แต่ทางเดินสายหลังจุดกดยังทะลุผิว จึงสรุปว่ากดถูกไม่ได้ |

ตัวเลขการชนเนื้อไม้เป็น Witness ที่พบจากการสุ่มผิวละเอียด ไม่ใช่หลักฐานว่าไม่มี
จุดอื่นชนลึกกว่านี้ ค่า Signed Nearest Normal ใน JSON เป็น Diagnostic เท่านั้น
เพราะผิวที่พับซ้อนทำให้เครื่องหมาย Inside/Outside ไม่แน่นอน การชนสายที่รายงานใช้
**ระยะถึงผิวแบบ Unsigned ลบรัศมีสาย** การซ้อนมือยืนยันด้วย Edge/Triangle Intersection
เพิ่มเติมจาก Bounding Boxes พร้อมพิกัดหลักฐาน.

ดู [ผลตรวจ GLB เต็ม](research/pose-surface-runtime-audit.json) และ
[สคริปต์ตรวจ](research/audit-pose-surface.py).

## ปัญหา Rig และการส่งออกที่ค้นพบ

ต้นฉบับ Blender ให้น้ำหนักได้ถึง 6 กระดูกต่อจุด ขณะที่ GLB เก็บ 4 กระดูก การใช้
มุมข้อต่อชุดเดียวกันจึงทำให้ผิวบางจุดต่างกันถึง **1.444 มม.** ระหว่างสองไฟล์.
นี่เป็นผลจาก Skin Weights ไม่ใช่การลด Texture หรือความผิดพลาดของกล้อง.

ได้สร้างตัวแทนที่ใช้น้ำหนักตรงกับ GLB แล้ว การแปลงแกน/เมทริกซ์ตรงกันในระดับ
Numerical Precision และตรวจเทียบ `Three.js getVertexPosition()` จาก Browser
กับชุดพิกัดตรวจการชนอีกครั้ง รายงานอยู่ใน
[runtime transfer](research/runtime-transfer-audit.json),
[GLB-weight transfer](research/runtime-transfer-gltf-compatible-audit.json) และ
[หลักฐานจาก Browser](research/inspection).
การแปลงตรงกันยืนยันว่ากำลังตรวจท่าเดียวกับที่ Browser แสดง **ไม่ได้ทำให้ท่านี้ผ่าน**.

ข้อต่ออยู่ในช่วง Limit Rotation ของ Rig เดิม แต่ Blender Constraints ไม่ได้ติดมากับ
GLB และ Copy Rotation ถูกปิดเพื่อทดสอบท่าอย่างชัดเจน ช่วงมุมที่ไม่เกิน Limit
ไม่ได้รับประกันว่าผิวจะพับตามธรรมชาติหรือท่านั้นเล่นกีตาร์ได้.

## คอกีตาร์ทดลอง

[การตรวจเรขาคณิต 12 ข้อผ่าน](research/guitar-mesh-audit.json): 6 สาย, 12 เฟรตตาม
Equal Temperament, Scale 648 มม., Octave ที่ 324 มม., นัต 43 มม., รัศมีบอร์ด
350 มม., คอรวมบอร์ดหนา 21 มม., แยกไม้/โลหะ/นัต และลูกบิดครบหกตัว.
ข้อมูลเหล่านี้เป็นมิติที่ออกแบบสำหรับต้นแบบ ไม่ได้เพิ่มลงฐานข้อมูลสินค้า.

แก้ความสูงสายเปิดในต้นแบบให้พ้นเฟรต: ท้องสายเหนือบอร์ด 1.4 มม. ที่นัต และ
3.0 มม. ที่เฟรต 12; ช่องว่างต่ำสุดเหนือ Crown จากการตรวจเรขาคณิต 0.577 มม.
จุดกด C อยู่ก่อนเฟรตประมาณ 4.55 / 4.05 / 4.10 มม. และไม่ย้ายไปผิดสาย/ผิดช่อง.
รวม 15,544 สามเหลี่ยม / 70 Meshes การผ่านนี้เป็นการตรวจโครงสร้างคอ ไม่ได้ผ่าน
การจับมือหรือรับประกันความสมจริงและ Frame Rate บน iPad.

## แหล่งอ้างอิงที่ตรวจ

เข้าถึงวันที่ **2026-10-24**; รายการและข้อจำกัดบันทึกใน Asset Audit.

- โมเดลหลัก: [Creator repository](https://github.com/emmalieker/anatomical-hand-model/tree/f27f19f55f8270b3108ea0b53ce5aa81c543ff7c),
  [ใบอนุญาต](https://github.com/emmalieker/anatomical-hand-model/blob/f27f19f55f8270b3108ea0b53ce5aa81c543ff7c/LICENSE),
  [GLB ต้นฉบับ](https://raw.githubusercontent.com/emmalieker/anatomical-hand-model/f27f19f55f8270b3108ea0b53ce5aa81c543ff7c/exports/hand_model.glb).
- [WebXR input profiles](https://github.com/immersive-web/webxr-input-profiles/tree/main/packages/assets):
  MIT ครอบคลุม Asset แต่ไฟล์มือที่ตรวจไม่มี Texture จึงไม่เลือกเป็นคำตอบด้านความสมจริง.
- [Innerscene CC0 hand](https://www.innerscene.com/tools/library/3d-parts/posable-anatomical-right-hand-f6098b4f):
  อ่านหน้ารายละเอียดได้ แต่ Download ตอบ 403 ไม่ได้ข้ามข้อจำกัดหรือยืนยันคุณภาพไฟล์จริง.
- [BlendSwap rigged hands](https://blendswap.com/blend/22269): หน้าแหล่งข้อมูลระบุ CC0
  แต่ต้อง Sign In เพื่อดาวน์โหลดและไม่มี Texture จึงยังไม่ได้เลือกใช้.
- [Fender: C chord](https://www.fender.com/articles/chords/learn-how-to-play-c-guitar-chord)
  และ [การอ่านผังคอร์ด](https://www.fender.com/articles/chords/how-to-read-a-chord-chart):
  ใช้ตรวจสาย/เฟรต ไม่ได้คัดลอกภาพผังคอร์ดมาใช้.

## Build และ Regression ของเว็บไซต์เดิม

**ตารางนี้ทดสอบเว็บไซต์ Stage 1–2 ที่ยังคงเดิม ไม่ใช่การรับรองว่ามือ Stage 3 พร้อมแล้ว.**

| รายการ | ผล |
| --- | --- |
| `npm run build` | [ผ่าน](build.txt); ยังมีคำเตือน Chunk Three.js 589 KB ที่โหลดเฉพาะ Practice |
| `npm run catalog:check` | [ผ่าน](catalog.txt): 200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 / ID ไม่ซ้ำ |
| `npm run images:check` | [ผ่าน](images.txt); ภาพสินค้าเดิมและสถานะสิทธิ์ไม่เปลี่ยน |
| `npm run practice:check` | [13/13 ผ่าน](practice.txt) |
| Practice ใน Linux WebKit | [15/15 ผ่าน](browser-webkit.json): 5 ขนาดหน้าจอ, กล้อง, Touch, Recovery, Lazy Loading |
| Shared UI Regression ใน Chromium | [18/18 ผ่าน](shared-regression.json): Search/Filter, Navigation, Gallery, Wishlist, Compare, Quiz, Responsive |
| Gallery/Existing Function Regression ใน Chromium | [79/79 ผ่าน](regression/browser-stage3-gate.json) |
| Protected Source | [208 ไฟล์เหมือน Baseline ทุกไบต์](protected-source.json) รวมข้อมูล/ID/สิทธิ์ภาพ/หน้าเดิม |
| ฉาก Research | ใช้ Browser จริงทั้ง Chromium และ Linux WebKit; รูปสามมุมและ Runtime Proof แยกจาก App |
| ท่า C พร้อมสอน | **ไม่ผ่าน**: Open G / เล็บ / ผิวซ้อน ต้องแก้ก่อนนำเข้า App |

Normal App Runs ไม่มี Console/Runtime/Network Error ที่ไม่คาดคิด.
การจำลอง WebGL หาย, Context Lost และ Module HTTP503 อยู่ในชุดทดสอบ Fault
แยกจากผลปกติ ผลผ่านของ Regression ไม่ได้ลบล้างข้อบกพร่องของโมเดลมือ.

ไม่มี iPad จริงหรือ macOS Safari ในสภาพแวดล้อมนี้ Linux WebKit ช่วยตรวจ Engine
แต่ไม่ใช่ผลรับรอง iPadOS Safari, GPU, Memory, อุณหภูมิ หรือแบตเตอรี่.

## ทางเลือกก่อนพัฒนาต่อ

1. **แนะนำ: แก้ท่าและ Skin Weights ของมือซ้ายใน Blender โดยใช้ GLB ที่ส่งออกจริงเป็นหลัก.**
   แก้เล็บ/นิ้วโป้ง, ยกนิ้วที่แตะสาย G, แก้รอยพับนิ้วก้อยกับนิ้วนางและจุดซ้อน,
   ตรวจทางเดินสายทั้งเส้น แล้วส่งออกและตรวจการชนซ้ำก่อนผูกกับ `/practice`.
   ต้องตรวจความเป็นธรรมชาติร่วมกับตำแหน่งจับคอร์ด ไม่ใช่บังคับปลายกระดูกให้ตรงจุดอย่างเดียว.
2. ใช้หรือจัดหาโมเดลมือซ้ายที่ทำมาเพื่อจับเครื่องดนตรี พร้อม Rig/Skinning ที่เหมาะสม
   และสิทธิ์เผยแพร่ชัดเจน แล้วเริ่มตรวจ C Major ชุดเดียวด้วยเกณฑ์เดิม.

ตามคำสั่ง **“หากยังทำโมเดลมือที่วางนิ้วถูกต้องไม่ได้ ให้รายงานปัญหาและทางเลือกก่อนดำเนินงานต่อ”**
จึงส่งหลักฐานและหยุดที่จุดนี้ ยังไม่แก้ App, ไม่เพิ่มคอร์ด/เสียง/บทเรียน และไม่ Merge/Push master.
ไฟล์ใหม่รอบนี้มีเฉพาะ `docs/practice-stage3/` ได้แก่รายงาน เครื่องมือตรวจออฟไลน์
ผลทดสอบ และภาพหลักฐาน ไม่ได้เพิ่ม GLB หรือไฟล์ Blender ลง `src` หรือ `public`.
