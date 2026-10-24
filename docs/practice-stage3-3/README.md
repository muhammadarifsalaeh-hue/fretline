# Stage 3.3 — ปรับกล้องและคอกีตาร์แล้ว; มือพร้อมแขนเสื้อดำยังไม่ผ่าน

วันที่ตรวจ: 24 ตุลาคม 2026 · Branch `feature/guitar-practice-3d` · Baseline `6dbfe05`.

**นี่เป็น Camera / Fretboard Preview ไม่ใช่การอนุมัติ Stage 3.3 หรือท่า C Major ของมือมนุษย์.**
ยังไม่มีโมเดลมือ–แขน–เสื้อที่เหมาะสมและผ่านเกณฑ์ให้ใช้ จึงไม่ใส่แขนทรงกระบอก ไม่ซ่อนมือที่ผิดท่า และไม่ใช้ภาพ 2D แทนโมเดล.
ทำส่วนกล้องและคอกีตาร์ที่เป็นอิสระก่อน ตามคำสั่งให้รายงานทางเลือกก่อนใช้โมเดลทดแทน.

## สิ่งที่พัฒนาจริง

- Default Camera มองเข้าหน้าฟิงเกอร์บอร์ดแบบเฉียง หัวกีตาร์อยู่ขวาบน ปลายคอฝั่งตัวกีตาร์อยู่ซ้ายล่าง.
  แกนคอเอียง 15 องศา สายจริงบนจอเรียง E–A–D–G–B–e และ Low E มีเส้นผ่านศูนย์กลางมากที่สุด.
- กำหนดแกน Up ก่อนสร้าง OrbitControls; หมุนและ Reset ด้วยแกนเดียวกัน ไม่พลิกเมชหรือสลับหมายเลขสายเพื่อแต่งภาพ.
  มีมุมเริ่มต้น ด้านหน้า จากหัวกีตาร์ ด้านข้าง หลังคอ และมุมผู้เล่น. กล้องด้านหลังย่อมเปลี่ยนด้านที่เห็นตามกายภาพ.
- Fit กล้องจากขอบเขตเมชจริง รวมความลึก มุมกล้อง อัตราส่วนจอ และพื้นที่ป้าย; Resize รักษาทิศทางกับอัตราซูมของผู้ใช้.
- เปลี่ยนคอทรงกล่องเดิมเป็นคอ D-section ฟิงเกอร์บอร์ดโค้งและกว้างไล่ระดับ นัตเซาะร่อง เฟรตโค้งทรง Crown,
  หัวกีตาร์เอียง 14 องศา ลูกบิด 3+3 พร้อมโพสต์/แหวน/ตัวเรือน/แกน/ปุ่ม และสายทั้ง 6 ที่ขนาดต่างกันจริง.
  เป็นแบบจำลองทั่วไปที่เขียนขึ้นเอง ไม่ใช่สเปกกีตาร์ใน Catalog.
- วัสดุ PBR สำหรับไม้ โลหะ และนัต พร้อมลายไม้สร้างด้วยโค้ด แสงด้านหลัง และ Studio Environment ขนาด 64 px ที่สร้างครั้งเดียว; ไม่ดาวน์โหลดภาพผลิตภัณฑ์มาใช้.
  เรนเดอร์เมื่อมีการเปลี่ยนแปลง ไม่หมุนเองหรือรัน Render Loop ขณะนิ่ง; จำกัด DPR 1.75.
- พื้นที่ 3D ใหญ่ขึ้น มีผังคอร์ด/คำอธิบายอยู่ด้านข้างบน Desktop และตัวเลือกคอร์ดอยู่ด้านล่าง.
  คงคอร์ดเดิมทั้ง 5 เป็นผัง/จุดหมายเลขเท่านั้น ไม่ได้เพิ่มท่ามือคอร์ดอื่นก่อน C ผ่าน.
- ระบบ 3D ยังโหลดเฉพาะ `/practice`; Loading, Error, Retry, WebGL Context Loss Recovery และ Keyboard Controls คงอยู่.

## สิ่งที่ยังไม่ผ่าน

| เกณฑ์ | สถานะ |
| --- | --- |
| กล้องเริ่มต้นและลำดับสาย | ตรวจด้วยพิกัดที่ Project จากเมชจริงและภาพ WebGL |
| มือซ้ายสมจริงพร้อมแขนและเสื้อดำ | ยังไม่มีโมเดลที่ผ่านเกณฑ์ให้ใช้ |
| C Major: ปลายนิ้วสัมผัส B1 / D2 / A3 | ผังคอร์ดและจุดหมายเลขถูกต้อง; ยังไม่ผ่านการตรวจสัมผัสของมือมนุษย์ |
| นิ้วโป้ง / สาย G และ e เปิด / ผิวมือไม่ซ้อน | โมเดล Stage 3.1 ยังถูกปฏิเสธ; ไม่อ้างว่าปัญหาได้รับการแก้แล้ว |
| Safari บน iPad จริงและประสิทธิภาพ GPU ของ iPad | ยังไม่มีอุปกรณ์จริงให้ทดสอบ; Linux WebKit ใช้แทนการอนุมัตินี้ไม่ได้ |
| Merge / Push เข้า master | ไม่ดำเนินการ |

การหมุนกล้องไม่ได้เป็นหลักฐานว่ามือจับคอร์ดถูกต้อง. รูปชุดนี้ตั้งใจแสดงโมเดลคอและจุดหมายเลขที่มีอยู่จริงเท่านั้น.

## โมเดลที่ตรวจและเหตุผลที่หยุดส่วนมือ

[รายงานแหล่งโมเดลและข้อจำกัด](research/model-feasibility.md) บันทึก URL, License และวันที่เข้าถึง.
ตรวจไฟล์จริงของ Rain ใน Blender โดยปิด Auto-execution และตรวจ Binary ของ WRAD; ไม่มีการนำเข้าทั้งสองในเว็บไซต์.

| โมเดล | ผลตรวจ |
| --- | --- |
| Lieker hand เดิม | มีมือ/ข้อมือ แต่ไม่มีแขนและเสื้อยาว; C ยังมีข้อบกพร่องจาก Stage 3.1 |
| Blender Studio Rain, CC BY 4.0 | มีแขนต่อเนื่องและ Rig จริง แต่สไตล์ตัวละครและเสื้อแขนสั้นไม่ตรง Reference |
| WRAD Arms, CC0 | มี Rig แต่ Low-poly 1,196 สามเหลี่ยม ไม่มีผ้า ไม่เหมาะกับความสมจริงที่ขอ |
| MakeHuman / MPFB | มีฐานตัวละครและเสื้อแขนยาวที่ระบุ License แต่ยังต้องทำโมเดล ผ้า Rig และ Correctives จริง |
| Fab แขนเสื้อโค้ต | ตรวจได้เพียง Listing; ยังไม่ได้ซื้อ ตรวจ Binary หรือพิสูจน์ท่า C |

ตามคำสั่งผู้ใช้ “หากไม่มีโมเดลมือและแขนที่เหมาะสม ให้รายงานข้อจำกัดและขออนุมัติทางเลือกก่อน”
จึงหยุดส่วนโมเดลเพื่อเลือกว่าจะใช้โมเดลสมจริงที่มีสิทธิ์และไฟล์ต้นฉบับพร้อมแก้
หรืออนุมัติทำโมเดลต่อใน Blender / MakeHuman / MPFB. ยังไม่ซื้อโมเดลหรือเริ่ม Stage 4.

## ไฟล์แอปที่แก้

- `src/features/practice/scene/studyGuitar.js`: รูปทรงคอและวัสดุ PBR ที่ใช้จริง.
- `src/features/practice/scene/cameraMath.js`: มุมกล้อง/แกน Up และ Perspective Fit.
- `src/features/practice/scene/createNeckScene.js`: เชื่อมโมเดล กล้อง การควบคุม การแสดงจุด และ Diagnostics จากเมชจริง.
- `src/features/practice/components/GuitarNeckViewer.jsx` / `viewer.css`: ตัวเลือกมุมกล้องและพื้นที่แสดงผล.
- `src/pages/PracticePage.jsx` / `src/styles/practice.css`: จัดลำดับ Viewer กับ Chord Library และ Responsive.

ไม่มี Dependency ใหม่ ไม่มีการแก้ข้อมูลกีตาร์ รูปสินค้า Guitar ID หรือหน้าระบบเดิม.

## การรันทดสอบเพิ่มเติม

```sh
npm run build
npm run catalog:check
npm run images:check
npm run practice:check
node docs/practice-stage3-3/tests/guitar-geometry.test.mjs
node docs/practice-stage3-3/tests/camera-projection.test.mjs
```

## ผลทดสอบที่ได้จริง

| ชุดตรวจ | ผล |
| --- | --- |
| `npm run build` | ผ่าน; Scene Chunk `practice-three-CyceKmSN.js` 611.60 kB / 157.12 kB gzip |
| `npm run catalog:check` | ผ่าน — 200 รุ่น, 10 แบรนด์, แบรนด์ละ 20, ID เดิม |
| `npm run images:check` | ผ่าน — 197 รุ่นยังใช้ Placeholder ตามเดิม; ไม่มีการเพิ่มภาพสินค้า |
| `npm run practice:check` | 13 ผ่าน — ข้อมูลคอร์ดเดิมถูกต้อง; ไม่ใช่การตรวจมือมนุษย์ |
| [รูปทรงเมชจริง](results/guitar-geometry.json) | 12 ผ่าน — 15,520 สามเหลี่ยม, 70 เมช; ระยะสายเปิดถึงเฟรตต่ำสุด 0.577 มม. |
| [คณิตศาสตร์กล้องกับเมชจริง](results/camera-math.json) | 153 ผ่าน — 10 อัตราส่วนจอ, 6 มุมกล้อง, Fit/Reset/Geometry Invariance |
| [Chromium — กล้องจริง](results/browser-camera-chromium.json) | 5/5 ผ่าน — 1440, 1024, 768, 390, 320 px |
| [WebKit — กล้องจริง](results/browser-camera-webkit.json) | 5/5 ผ่าน — 1440, 1024, 768, 390, 320 px |
| [จำลองจีบ 2 นิ้ว](results/synthetic-pinch.json) | ผ่าน — กล้องซูมจริง ภาพเปลี่ยน พิกัดสายและเมชไม่เปลี่ยน |
| [Regression](results/regression/final-regression-summary.json) | 117 ผ่าน — Shared 18, Pacifica Gallery 79, Practice Chromium 10 + WebKit 10 |
| Safari / Touch บน iPad เครื่องจริง | ยังไม่ได้ทดสอบ จึงยังอนุมัติ Merge จากผลชุดนี้ไม่ได้ |
| ท่ามือ C Major / แขนเสื้อดำ | ยังไม่ผ่าน — ไม่มีโมเดลที่เหมาะสมถูกนำเข้าหรืออนุมัติ |

Regression ของ Practice รันซ้ำหลังแก้ PMREM/Back Light. Shared/Pacifica ตรวจใน Build ก่อนหน้าโดยไฟล์และ Asset ของหน้ากลุ่มนั้นไม่เปลี่ยนจากการแก้แสง. Fault Injection มีเหตุการณ์จำลองที่คาดไว้ 6 รายการ; ไม่พบข้อผิดพลาดที่ไม่คาดไว้.

การเปิด WebKit ครั้งแรกติด Host Dependency Validator ของเครื่องมือ; เก็บ [ผลครั้งแรก](results/webkit-initial-host-validation-failure.json) ไว้ และรันสำเร็จหลังใช้ค่ารัน Headless ของ Environment เดิม. ไม่ได้ข้ามการทดสอบหน้าเว็บหรือใช้ภาพปลอมแทน Browser.

Camera Browser Runs ทั้งสองไม่มี Console Errors/Warnings, Runtime Errors, Failed Requests หรือ HTTP Errors.
ตรวจภาพ Default / Side / Back / Player แล้ว; พบด้านหลังคอมืดเกินใน Build แรกและแก้แสงก่อนรันทดสอบซ้ำด้วย Build สุดท้าย.
แกนฟิงเกอร์บอร์ดเอียง 15 องศา; เส้นระหว่างจุดศูนย์กลางหัวกีตาร์ที่เอียงกับปลายบอร์ดอยู่ประมาณ 16.3 องศาในภาพจริง.

Chromium 154 ใช้ Software Rendering (SwiftShader) ใน Linux; WebKit 26.5 บน Linux ไม่ใช่ Safari บน iPadOS.
การจำลอง Touch ไม่ใช่การทดสอบฮาร์ดแวร์จริง. Build มีคำเตือนขนาด Chunk 500 kB;
คง Scene กับ Three เป็น Chunk เดียวที่แยกโหลดเฉพาะ Practice เพื่อรักษา Retry ของ Failed ES Modules ใน WebKit.
ไม่มี Benchmark FPS หรือคำรับรองประสิทธิภาพ GPU ของ iPad จากการทดสอบชุดนี้.

## ภาพจริงจากหน้า `/practice`

ไม่มีการแทน Canvas ด้วยรูปนิ่ง และไม่มีการสร้างภาพมือเพื่อทำให้ดูเหมือนผ่านเกณฑ์.
รูปสี่มุมแสดงคอ 3D และจุดหมายเลข ไม่มีมือ/แขน/เสื้อดำ.

| มุม / อุปกรณ์ | ภาพ |
| --- | --- |
| Default พร้อมผังคอร์ดและปุ่ม | [Desktop Workspace](screenshots/desktop-workspace.png) |
| Default Canvas | [มุมเริ่มต้น](screenshots/default-view.png) |
| ด้านข้าง | [Side](screenshots/side-view.png) |
| หลังคอ | [Back](screenshots/back-view.png) |
| มุมผู้เล่น | [Player](screenshots/player-view.png) |
| Tablet แนวนอน | [1024 px](screenshots/tablet-landscape-workspace.png) |
| Tablet แนวตั้ง | [768 px](screenshots/tablet-portrait-workspace.png) |
| Mobile 390 px — ภาพจริงเต็ม Viewport | [Canvas/Controls](screenshots/mobile-canvas-controls.png) · [ผัง/ตัวเลือกคอร์ด](screenshots/mobile-diagram-choices.png) |
| Mobile 320 px — ภาพจริงเต็ม Viewport | [Canvas/Controls](screenshots/small-mobile-canvas-controls.png) · [ผัง/ตัวเลือกคอร์ด](screenshots/small-mobile-diagram-choices.png) |
| ก่อนปรับกล้อง/โมเดลรอบนี้ | [Desktop](screenshots/before-desktop-canvas.png) · [Tablet](screenshots/before-tablet-canvas.png) · [Mobile](screenshots/before-mobile-canvas.png) |
| ก่อนแก้แสงด้านหลัง | [ภาพที่พบว่ามืดเกินไป](screenshots/before-back-lighting.png) |

[Source Protection](results/source-protection.json) ตรวจว่าไฟล์แอปที่เปลี่ยนทั้ง 7 ไฟล์อยู่เฉพาะ Practice.
โค้ดหน้าอื่น ข้อมูล IDs รูปสินค้า Package/Vite และ master คงเดิม.

## Browser Automation

มี Python Playwright และ Pillow อยู่ใน Environment ทดสอบแล้ว; ไม่ได้เพิ่มเป็น Dependency ของเว็บไซต์.
เปิด Production Preview ที่ Port 5430 แล้วใช้:

```sh
python docs/practice-stage3-3/tests/browser-camera.py --url http://127.0.0.1:5430 --engine chromium --output /tmp/fretline-stage33-camera-chromium
python docs/practice-stage3-3/tests/browser-camera.py --url http://127.0.0.1:5430 --engine webkit --output /tmp/fretline-stage33-camera-webkit
python docs/practice-stage3-3/tests/browser-pinch.py
```

`browser-pinch.py` เก็บเป้าหมาย Localhost:5430 และโฟลเดอร์ชั่วคราวที่ใช้รันจริง.
Browser Engines อยู่ใน `/tmp/fretline-browser-engines` ของ Environment นี้; WebKit ใช้ `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1`,
`XDG_CACHE_HOME=/tmp/fretline-webkit-cache`, `XDG_CONFIG_HOME=/tmp/fretline-webkit-config`, `GSETTINGS_BACKEND=memory`.
เครื่องอื่นต้องเตรียม Runtime Libraries/Engines ของ Playwright ให้เหมาะสมก่อนรัน.
Regression ใช้สคริปต์เดิม `docs/practice-stage1-2/tests/browser.py`, `shared-regression.py`
และ `docs/signature-redesign/phase-c-final/tests/regression-gallery.py`.

## เปิดดูใน Codespaces / Workspace

เก็บงานที่แก้ค้างใน Codespaces ก่อนสลับ Branch. ใช้ Feature Branch สำหรับตรวจรอบนี้:

```sh
git fetch origin
git switch feature/guitar-practice-3d
git pull --ff-only origin feature/guitar-practice-3d
npm ci
npm run dev -- --host 0.0.0.0 --port 5173
```

เปิดแท็บ Ports → 5173 → Open in Browser แล้วเติม `/practice` ใน URL.
การตรวจบน Feature Branch ไม่ใช่การอัปเดต master; ยังต้องตรวจ Safari บน iPad จริงและอนุมัติก่อน Merge.
โมเดลมือและแขนเสื้อดำยังรออนุมัติแนวทางและยังไม่ถูกนำเข้า.
