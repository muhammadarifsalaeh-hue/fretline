# Premium Quiz & Compare — implementation delivery

ทำต่อจาก Fretline เดิมที่ `f2168ef` บน Branch `feature/premium-quiz-compare` เท่านั้น ไม่มีการ Merge เข้า `master` และไม่มีการเปลี่ยนข้อมูลสินค้า เกณฑ์แนะนำ หรือระบบ Practice

## สิ่งที่เปลี่ยนจริง

- `/find-my-guitar`: Hero ภาพจริง ตัวอักษรขาว–ทอง ปุ่มเริ่มแบบทดสอบ 5 หมวด Progress 1–5 ภาพเล่นกีตาร์สามช่อง การ์ดคำตอบพร้อม Selected/Keyboard Focus และผลลัพธ์จากระบบแนะนำเดิม
- คงคำถามและตัวเลือกเดิมทั้ง 22 ตัวเลือก จำนวนแต่ละขั้นคือ **5 / 3 / 5 / 5 / 4** ไม่ตัดตัวเลือกเพื่อบังคับให้เหมือนภาพต้นแบบ
- `/compare`: Hero ภาพจริง ปุ่มเพิ่ม/แชร์/ล้าง จำนวนที่เลือก การ์ด 4 ช่อง ภาพสินค้าผูกกับ Guitar ID หมวดข้อมูล 6 แท็บ ปุ่มแสดงเฉพาะความต่าง ตารางเลื่อนแนวนอน และ Empty State เดิมที่ปรับให้เข้าธีม
- เพิ่มการควบคุมแท็บด้วย Arrow/Home/End, Focus States, Touch Targets หลักอย่างน้อย 44px และรองรับ Reduced Motion
- แก้ระยะหัวหน้า Compare ให้ breadcrumb ไม่ถูก Navbar แบบ Fixed บัง
- ส่วนเปรียบเทียบบน Homepage ยังคงใช้รูปแบบเดิมของ Shared CompareTable; CSS ใหม่จำกัดอยู่ในสองหน้า
- มีหน้าเครดิตภาพจริงที่ `/image-credits#discovery-photography` ไม่เพิ่มข้อความโฆษณาเกี่ยวกับ AI

## ภาพจริงที่เพิ่ม

ภาพต้นทาง 5 ภาพ: Quiz Hero, Compare Hero, ผู้เล่นกีตาร์ไฟฟ้า, ผู้เล่นกีตาร์โปร่ง และมือจับสาย แปลงเป็น **WebP 15 ไฟล์** รวม **839,000 bytes** พร้อม `srcSet`, ขนาดภาพคงที่ และ Lazy Loading สำหรับภาพประกอบ

เครดิต: Wes Hicks, Masha, Mila Vasileva, Alexander Mass และ Alex Kolundzija / Unsplash License รายละเอียดแหล่งที่มา หลักฐานตรวจสิทธิ์ และ SHA-256 อยู่ใน [รายงานภาพ](photos/README.md) และ [Manifest](photos/manifest.json)

ภาพ Hero เป็นภาพประกอบบรรยากาศ ไม่ใช้แทนภาพของรุ่นสินค้า การ์ด Compare/ผล Quiz ยังคงใช้ภาพตามข้อมูลรุ่นเดิม รุ่นที่ไม่มีภาพหรือข้อมูลยืนยันยังใช้ Fallback ตามจริง

## ภาพจากเว็บจริง

ภาพด้านล่างมาจาก Chromium ที่เปิด Production Build จริง คง Navbar และ Bottom Navigation ตามการแสดงผล ไม่มีการสร้างภาพ Mockup แทน Screenshot

| ขนาดจอ | Quiz Hero | Quiz แบบทดสอบ | Compare Hero | Compare Workspace |
|---|---|---|---|---|
| Desktop 1440×1000 | [ภาพ](screenshots/quiz-desktop-hero.png) | [ภาพ](screenshots/quiz-desktop-workspace.png) | [ภาพ](screenshots/compare-desktop-hero.png) | [ภาพ](screenshots/compare-desktop-workspace.png) |
| Tablet 768×1024 | [ภาพ](screenshots/quiz-tablet-hero.png) | [ภาพ](screenshots/quiz-tablet-workspace.png) | [ภาพ](screenshots/compare-tablet-hero.png) | [ภาพ](screenshots/compare-tablet-workspace.png) |
| Mobile 390×844 | [ภาพ](screenshots/quiz-mobile-hero.png) | [ภาพ](screenshots/quiz-mobile-workspace.png) | [ภาพ](screenshots/compare-mobile-hero.png) | [ภาพ](screenshots/compare-mobile-workspace.png) |

ภาพ Before ของทั้งสองหน้า 3 ขนาดจออยู่ใน [tests/before](tests/before/) และผูกกับ Commit เดิมใน `baseline.json` ภาพ Full Page/ผลลัพธ์/Compare 0–4 รุ่นหลังพัฒนาอยู่ใน [tests/final](tests/final/)

## เทียบกับภาพต้นแบบ

คงโครงสร้าง Hero ข้อความซ้าย ภาพกีตาร์ขวา สีดำ–ทอง ไอคอนวงกลม ภาพสามช่อง การ์ดคำตอบสองคอลัมน์ การ์ด Compare 4 ช่อง และตารางแบบกะทัดรัด

ข้อแตกต่างที่ตั้งใจเก็บตามหลักฐานจริง:

- ภาพ Quiz เป็นห้องดนตรีจริง ไม่ใช่ฉากสตูดิโอเดียวกับ Reference
- ภาพ Compare เป็นหน้าร้านกีตาร์จริงหลายตัว ไม่ใช่ฉากที่มีกีตาร์ไฟฟ้า 3 ตัวตรงตาม Reference
- รักษาลำดับคำถามและตัวเลือกเดิมของ Quiz; ปุ่มรองอธิบายการใช้งานจริง ไม่อ้างว่ามีวิดีโอที่ยังไม่มี
- ไม่คัดลอกราคา สเปก หรือภาพสินค้าจากภาพต้นแบบ ข้อมูลที่ยังไม่ยืนยันยังแจ้งตามจริง
- Navbar, Footer และเมนูของเว็บไซต์เดิมคงไว้ ไม่สร้างเมนูบัญชีหรือการทำงานที่ไม่มีอยู่

## การทดสอบและขอบเขต

Production Build ผ่าน; ชุดทดสอบหน้าใหม่ **25/25** บน Chromium 154 และ Linux WebKit 26.5 ครอบคลุม Desktop/Tablet/Mobile และจอแคบ 320px โดยไม่พบ Console/Runtime/Network Error ขณะทดสอบ ภาพและแหล่งที่มา **34/34**, การคงรูปแบบ Compare บน Homepage **8/8**, ชุด Gallery เดิมที่เลือกแท็บข้อมูลทั้งหมดก่อนตรวจ **79/79**, Practice **56/56**, Hand Runtime **20/20**, Quiz/Compare Logic **19/19** และ Yamaha Import **11/11** ผ่าน

ชุดทดสอบประวัติ Phase 5–9 และ Price Filter Fixture หนึ่งกรณียังไม่ผ่านเพราะอ้างอิงราคา/ข้อมูลก่อนงานนำเข้า Yamaha รายงานเก็บผลล้มเหลวไว้ ไม่ได้แก้ตัวเลขหรือผ่อนเกณฑ์เพื่อให้ผ่าน ส่วน Gallery เดิมแบบไม่เลือกแท็บทั้งหมดจะหยุดที่ข้อมูลวัสดุซึ่งย้ายเข้าหมวดแล้ว จึงเก็บทั้งผลเดิมและผล Adapter ที่กดแท็บจริงโดยคง Assertions เดิมครบ

ผลคำสั่งทั้งหมด รวมข้อผิดพลาดจาก Legacy Fixtures ที่ยังคงเปิดเผย อยู่ใน [final-checks.md](tests/final-checks.md) ผลตรวจภาพจริงอยู่ใน [photos/checks.json](photos/checks.json) และผลตรวจ Screenshot/Keyboard/เครดิต/การโหลดภาพอยู่ใน [delivery-checks.json](screenshots/delivery-checks.json)

ไฟล์ที่ต้องรักษาเดิม 108 ไฟล์ตรงกับ Commit ก่อนแก้ทุก byte; กีตาร์ 200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 รุ่น และ ID คงเดิม ผลแนะนำครบ 1,500 ชุดคำตอบ / 4,020 รายการตรงกับ Baseline ทั้งลำดับ คะแนน เหตุผล และข้อจำกัด

ไม่อ้างว่า Linux WebKit หรือการจำลอง Touch คือการทดสอบบน iPad Safari จริง ยังต้องตรวจอุปกรณ์จริงตามขั้นตอนด้านล่าง Build ยังคงเตือนขนาด Three.js Chunk เดิม ซึ่งไม่ถูกโหลดจากสองหน้านี้ ไม่มีการติดตั้ง Dependency เพิ่ม

การวัด Chromium บน Local Production Server พบ CLS 0–0.000316 สำหรับหกกรณีหน้า/ขนาดจอที่บันทึก ไม่มีการโหลด Three.js หรือ GLB จากสองหน้านี้ ตัวเลขนี้เป็นผลสังเกตในสภาพแวดล้อมทดสอบ ไม่ใช่คะแนน Lighthouse หรือผลเครือข่ายจริงบน iPad

ข้อจำกัดข้อมูลสินค้าเดิมยังคงอยู่: `images:check` ระบุ 197 รุ่นที่ไม่มีภาพสินค้าสำหรับเผยแพร่ทั่วไป ภาพประกอบใหม่ทั้งห้าภาพไม่ได้ใช้ปกปิดช่องว่างนี้ และไม่ได้เปลี่ยนเงื่อนไขสิทธิ์ของภาพ Yamaha ที่รอตรวจ

## เปิดดูบน Codespaces / iPad

งานนี้อยู่บน Feature Branch ยังไม่ได้แทนที่เว็บไซต์บน `master` ให้ใช้ Terminal ใน Codespaces ของ Repository เดิม:

```bash
git fetch origin
git switch feature/premium-quiz-compare
git pull --ff-only origin feature/premium-quiz-compare
npm install
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

หาก Codespaces แจ้งว่ามีไฟล์ที่แก้ค้าง ให้เก็บงานนั้นก่อนเปลี่ยน Branch อย่าใช้คำสั่งลบทิ้ง จากแท็บ **Ports → 5173 → Open in Browser** จะได้ HTTPS URL ของ Codespaces จริง ไม่ใช้ `localhost` บน iPad

เปิดเส้นทาง:

- `/find-my-guitar`
- `/compare`
- `/compare?ids=yamaha-pacifica-612viifm,yamaha-fg820-12,martin-d-28` — ตัวอย่างเลือกรุ่นที่มีภาพใน Registry อยู่แล้ว ไม่ใช่การเลือกค่าอัตโนมัติให้ทุกคน

บน iPad Safari ให้ตรวจแนวตั้งและแนวนอน: เริ่ม Quiz เลือกครบ 5 ขั้น ย้อนกลับ/แก้คำตอบ/ดูรายละเอียดผลลัพธ์; Compare เพิ่ม 2–4 รุ่น ลบ แชร์ เปลี่ยนแท็บ เลื่อนตาราง และล้างแบบยืนยัน หาก Clipboard ถูกจำกัด ช่องลิงก์สำรองต้องคัดลอกได้ รูปสินค้าต้องไม่ถูกตัด และหน้าเว็บต้องไม่เลื่อนล้นแนวนอน

## กลุ่มไฟล์ที่แก้

- `src/components/quiz/`: QuizIntro, QuizFlow, QuizOption, QuizProgress, QuizResults และ QuizHero/QuizVisuals ใหม่
- `src/pages/ComparePage.jsx` และ `src/components/compare/`: ComparisonSlots, ComparisonIcon, compareCategories ใหม่ และ CompareTable ที่มี Compact Mode แบบเลือกใช้
- `src/styles/premium-quiz.css`, `src/styles/premium-compare.css`
- `src/assets/discovery/`, `src/data/discoveryPhotography.js`
- `src/pages/ImageCreditsPage.jsx`, `src/components/detail/DiscoveryPhotographyCredits.jsx`
- เอกสาร แหล่งภาพ Screenshot และผลทดสอบในโฟลเดอร์นี้

ไม่แก้ Homepage, Navbar, Footer, ฐานข้อมูลสินค้า, Quiz Scoring, ShopContext, Catalog, Wishlist หรือ Practice/คอร์ด 42 แบบ
