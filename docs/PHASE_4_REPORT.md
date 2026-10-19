# Fretline — Phase 4: Compare Guitars & Find My Guitar

พัฒนาต่อจาก `c8b1bf3` บน branch `master` ใน Git repository เดิม.
Repository: https://github.com/muhammadarifsalaeh-hue/fretline

## ผลงานที่ส่งมอบ

### Compare

- ปรับ `/compare` ตามภาพอ้างอิงเดิมในบทสนทนา: Dark Luxury ดำ–ทอง
  Breadcrumb, หัวข้อไทย, count, แถบเครื่องมือ, การ์ด และตารางแบ่งหมวด
- เลือก 2–4 รุ่น เพิ่มผ่าน Picker/Catalog/Detail ลบรายรุ่นได้ รวมกรณีเหลือ 1 รุ่น
  รองรับ Empty State, คู่ตัวอย่างเดิม และรุ่นใกล้เคียง
- Picker ค้นหาจริง แสดงข้อมูล/สถานะที่มีอยู่ และปิดการเพิ่มเมื่อครบ 4 รุ่น
  ใช้ modal focus trap, Escape และคืน focus จาก hook เดิม
- Normalize รายการที่เก็บ/แชร์: รับเฉพาะ id ที่มีจริง ไม่ซ้ำ จำกัด 4 รุ่น
  เก็บผ่าน ShopContext/localStorage เดิม และจัดการ storage รูปแบบผิดได้
- เพิ่ม Brand/Model/Type ให้ตาราง Compare พร้อมโครงสร้าง ARIA table,
  กลุ่มข้อมูล, ตัวกรองเฉพาะส่วนต่าง, scrolling แนวนอนที่ใช้คีย์บอร์ดได้,
  และ sticky ชื่อรุ่นภายในพื้นที่เลื่อนตาราง
- URL `?ids=...` สะท้อนรายการปัจจุบัน รองรับ reload, Browser Back/Forward,
  การเปิดลิงก์ตรง, ค่าซ้ำ/ไม่รู้จัก และการแก้รายการจาก state กลาง
- แก้ race เมื่อ React Strict Mode เรียก effect ซ้ำใน dev server:
  ต้องรอ context รับข้อมูลจาก URL ก่อนทำเครื่องหมายว่าอ่าน URL แล้ว
- Clear มี dialog ยืนยัน/ยกเลิก และกลับไป focus ที่ Add หลังล้าง
  Wishlist ไม่ถูกล้างตาม
- แชร์ผ่าน clipboard และมีช่อง URL ที่เลือกคัดลอกเองได้เมื่อ clipboard ถูกปฏิเสธ
- ค่าไม่ทราบแสดง “ไม่ระบุ” ส่วน sample specs/price ซ่อนไว้เป็น “ยังไม่ยืนยัน”
  ตามค่าเริ่มต้น มีสวิตช์เปิดดูตัวอย่างพร้อมป้าย/คำอธิบายชัดเจน
- Verdict ราคาต่ำสุด/น้ำหนักเบาสุด ใช้เฉพาะข้อมูลที่มีแหล่งอ้างอิง
  แถว/อันดับรีวิวใช้เฉพาะรีวิวที่มีสถานะและแหล่งตรวจสอบของรีวิวเอง
- ซ่อน compare tray ลอยเฉพาะ Compare/Quiz เพื่อไม่บังเนื้อหาและปุ่ม
  รายการยังอยู่ครบ และเปิดได้จาก Navbar/BottomBar; หน้าอื่นใช้ tray เดิม

### Quiz

- ปรับ `/find-my-guitar` เป็นภาษาไทย ใช้สี ฟอนต์ ปุ่ม และภาพประกอบเดิม
  มี Welcome, progress, selected states, Previous/Next และผลลัพธ์
- คงคำถามทั้ง 5 ข้อและ option ids/values เดิม: type, level, style, budget, priority
  เพิ่มภาษาใน i18n ทั้งไทยและอังกฤษ ไม่มีคำถามใหม่
- ใช้ภาพประกอบประเภทกีตาร์เดิม ไม่อ้างว่าเป็นภาพของรุ่นใด
- คำตอบและขั้นตอนอยู่ใน URL เป็นแหล่ง state ของ flow จึง reload/แชร์/
  Browser Back/Forward ได้ ไม่สร้าง answer state ซ้ำในหลาย component
- เปลี่ยนจากการข้ามข้ออัตโนมัติเมื่อคลิกเป็นการยืนยันด้วย Next เพื่อให้ตรวจและ
  แก้คำตอบได้ชัด ลด timer race และใช้ native radio keyboard behavior ได้
- Edit Answers เก็บคำตอบเดิม; Retake เริ่มใหม่จาก Welcome
- แสดงรุ่นที่มีจริงใน catalog, เหตุผล, ข้อจำกัด, สถานะ sample/partial,
  รายละเอียด, Compare, Wishlist และ Compare top results
- ผลลัพธ์ไม่แสดงราคาตัวอย่างเป็นราคาจริง แสดง “ราคายังไม่ยืนยัน” แทน
  รวมถึงไม่มีดาว/จำนวนรีวิวตัวอย่าง
- Empty Results ทำงานเมื่อไม่มีคะแนนถึงเกณฑ์ ไม่สมมติว่าต้องมีอันดับแรกเสมอ
- เปอร์เซ็นต์ระบุว่าเป็นคะแนนสอดคล้องเบื้องต้นจาก heuristic profiles
  ไม่ใช่คะแนนรีวิวหรือความเหมาะสมที่ผู้ผลิตรับรอง

## สูตรคะแนน: สิ่งที่คงไว้และเหตุผลที่แก้

คงน้ำหนักเดิมทั้งหมด: ประเภท 30, ระดับผู้เล่น 20, แนวเพลง 20,
งบประมาณ 20, priority 10, verified rating สูงสุด 5. รวมเต็ม 105.
คงการหารด้วย 105, ปัดเป็นเปอร์เซ็นต์, cap 99%, type mismatch คูณ 0.35,
ระดับใกล้เคียง 8, งบยืดหยุ่น 14, ไม่ทราบราคา 6 และ tolerance งบเดิม.

ปรับเฉพาะความน่าเชื่อถือของ input และเงื่อนไขแสดงผล:

1. รีวิวต้องมี `rating.verified: true`, `rating.source.url`,
   `rating.source.verifiedOn`, score 0–5 และ count จำนวนเต็มมากกว่า 0.
   สถานะ verified ของตัวกีตาร์ไม่ทำให้รีวิว verified ตามไปด้วย.
   Catalog ปัจจุบันไม่มีรีวิวที่เข้าเงื่อนไข จึงไม่ให้ bonus/tie-break จากรีวิวตัวอย่าง.
2. ราคา/น้ำหนักของ record ที่ไม่มี provenance หรือเป็น sample ถือเป็น unknown
   จึงเข้า branch เดิมของ unknown price (6 เมื่อกำหนดงบ) และไม่ให้ lightweight
   points จากน้ำหนักที่ยังไม่ยืนยัน ไม่มีการคาดเดาค่าเพื่อเติมคะแนน.
3. โปรไฟล์ระดับผู้เล่น/แนวเพลงเดิมยังเป็นการประเมินเพื่อสาธิต จึงแสดง caveat
   ในทุกผลลัพธ์ และใช้คำอธิบายที่ไม่อ้างการยืนยันจากผู้ผลิต.
4. ยกเลิกข้อยกเว้น “อันดับแรกแสดงเสมอ” ทุกอันดับต้องได้อย่างน้อย 40%.
   เหตุผลคือไม่บังคับเสนอรุ่นที่คะแนนต่ำกว่าเกณฑ์ และรองรับ Empty State จริง.
5. เมื่อไม่มี review bonus แม้ main criteria ได้ 100 คะแนน จะได้ 95% บนสเกล
   105 เดิม ไม่เปลี่ยน denominator เพื่อทำให้ดูเหมือนคะแนนสูงขึ้น.

`src/utils/dataTrust.js` ใช้ metadata ของ catalog เดิม ไม่ได้ตรวจผู้ผลิตสดใหม่
และไม่อ้างว่าราคาใน dataset เป็นราคาปัจจุบัน. ตัวเลขทดสอบใน logic tests เป็น
fixture ที่แยกจาก production catalog เท่านั้น.

## Files modified / added

- Pages: `src/pages/ComparePage.jsx`, `src/pages/FindMyGuitarPage.jsx`
- Compare: `CompareEmpty`, `CompareTable`, `CompareVerdicts`, `GuitarPicker`,
  `compareRows.js` ใน `src/components/compare/`
- Quiz: `QuizIntro`, `QuizFlow`, `QuizProgress`, `QuizOption`, `QuizResults`,
  `MatchCard`, `MatchButtons` ใน `src/components/quiz/`
- State/data/logic: `src/context/ShopContext.jsx`, `src/data/quiz.js`,
  `src/utils/quizScoring.js`; เพิ่ม `src/utils/dataTrust.js`, `src/utils/selection.js`
- UI: เพิ่ม `src/components/ui/ConfirmDialog.jsx`, `ShareLink.jsx`;
  ปรับ `src/components/layout/CompareBar.jsx` เฉพาะการแสดงบนสองหน้า
- Routing/style/language: `src/App.jsx`, `src/index.css`, `src/i18n/th.js`, `en.js`
- Tooling: `scripts/check-phase4.mjs`, script `phase4:check` ใน package.json
- Docs: README, รายงานนี้ และ `docs/qa-phase4/`

ไม่ได้แก้ source ของ Homepage, Catalog, Guitar Detail หรือ records กีตาร์.
ไม่มี dependency ใหม่; package-lock/dependency inputs เดิม.
Shared comparison component ซ่อนรีวิวตัวอย่างใน home preview ด้วย เป็นการแก้
ความน่าเชื่อถือของข้อมูล โดยไม่เปลี่ยนดีไซน์หลักของ Homepage.

## Tests performed

- `npm run build`: ผ่าน ดูขนาด chunk จริงใน `docs/qa-phase4/build.txt`
- `npm run catalog:check`: ผ่าน โครงสร้างข้อมูล 36 รุ่นไม่พบปัญหา
- `npm run images:check`: exit 0 แต่ยังรายงานรูปจริง **0/36** ไม่ใช่ภาพครบ
- `npm run phase4:check`: **19/19** — weights, score normalization, unknown
  inputs, verified rating bonus/cap, sample review exclusion, budget boundaries,
  type penalty, no forced results, URL parsing, ids normalization และ row analysis
- Production Chromium browser suite: **86/86** — 2–4 รุ่น, cap, remove,
  duplicate links, clear/cancel, URL Back/Forward/reload, sharing fallback,
  Catalog/Detail integration, quiz ทุกขั้นตอน, previous/edit/retake,
  wishlist, recommendations→details/compare, keyboard, focus, reduced motion,
  malformed storage และ regression routes
- Development/React Strict Mode suite: **7/7** — empty results ผ่าน catalog
  ที่ทำให้ว่างเฉพาะหน่วยความจำ browser, edit/reload restore, quiz sharing
  fallback, picker search empty และลบรุ่นเดียวที่เลือกไว้
- รวม **112/112 checks ผ่าน**. Production normal interactions ไม่พบ page error,
  console error หรือ failed request; JSON เก็บผลจริงไว้ใน docs/qa-phase4
- ตรวจ Compare, Quiz welcome/question/results ที่ 320, 390, 768, 1024, 1440px:
  ไม่พบ document horizontal overflow. ตารางเปรียบเทียบเลื่อนภายในได้
- Screenshot desktop 1440px, tablet 768px และ mobile 390px มาจาก browser จริง
  เทียบแนวทางกับ reference เดิมด้วยสายตา ไม่มีการอ้าง pixel-diff score
- `git diff --check`: ผ่าน

ยังไม่มี WebKit/Safari binary ใน environment จึงไม่ได้ทดสอบ Safari จริงหรือ
ฮาร์ดแวร์ iPad. Clipboard paths ทดสอบด้วย API stubs ไม่อ้าง OS clipboard จริง.
Empty fixture ไม่ถูกบันทึกลง source/production catalog และคืนข้อมูลเมื่อ reload.

## Performance และขอบเขต

Compare และ Quiz ใช้ lazy routes/DiscoveryRoute เดิม ไม่เพิ่ม library.
ตารางวิเคราะห์ตามรายการที่เลือก และผลลัพธ์ใช้ memoized ranking.
Initial JS ประมาณ 323 KB (gzip ประมาณ 98 KB); chunk จริงดู build log.
ไม่ได้อ้าง Lighthouse score หรือ accessibility certification ทั้งระบบ.

## Remaining issues

- ยังขาดภาพจริงที่มีสิทธิ์ใช้ทั้ง 36 รุ่น จึงยังเป็นภาพสำรองที่ระบุไว้
- มี sample 18 รุ่น และ partial 18 รุ่น ไม่มี verified records ครบทุกข้อมูล
- ไม่มี verified review sources; review bonus จึงเป็น 0 กับ dataset ปัจจุบัน
- Profile การเล่น/แนวเพลงเดิมเป็นการประเมินเบื้องต้น ต้องจัดทำข้อมูลที่ยืนยัน
  ได้เพิ่มเติมหากต้องการยกระดับความน่าเชื่อถือของ recommendation
- ยังไม่ได้ตรวจ Safari/iPad จริง หรือทุกเบราว์เซอร์และอุปกรณ์
- งานนี้จบที่ Phase 4 ไม่เริ่ม Phase 5 และไม่เปลี่ยนหน้า Brands/Wishlist โดยไม่จำเป็น

## Git / Codespaces handoff

รักษา `f74f79c`, `c8b1bf3` และประวัติเดิม. ตรวจ remote ก่อน push,
ส่ง commit Phase 4 บน `master` แบบปกติ ไม่ force push. Commit hash และผล
ตรวจอ่านกลับจาก GitHub อยู่ใน Git history/ข้อมูลส่งมอบพร้อม ZIP.

ใน Codespaces ให้หยุด Vite เดิมด้วย Ctrl+C แล้วตรวจสถานะงานของคุณก่อน pull:

```sh
git status --short
git pull --ff-only origin master
npm ci
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

ถ้ามีการแก้ไฟล์ของคุณค้างอยู่ ให้เก็บ commit ก่อนดึงโค้ด. เปิด Ports → 5173 →
Open in Browser บน Safari ของ iPad โดยคง visibility เป็น Private และใช้บัญชี
GitHub ที่เข้าถึง repository ได้. ไม่ต้องสร้างโปรเจกต์หรือ repository ใหม่.
