# Fretline — Homepage Premium Redesign

ต่อยอดโค้ดเดิมจาก Commit `4bbecf8` บน Branch `feature/premium-quiz-compare` ตามคำขอให้ใช้ Feature Branch ปัจจุบัน ไม่สร้างโปรเจกต์ใหม่ และไม่ Merge เข้า `master`

## งานที่พัฒนาจริง

### Explore by Brand

- แถบแบรนด์ 10 รายการ ใช้ชุดซ้ำที่มีขนาดเท่ากันเพื่อวนอย่างต่อเนื่อง และคำนวณความเร็วจากเวลา
- เลื่อนอัตโนมัติที่ 30 CSS px/วินาที รองรับ Native Touch Swipe, Mouse Drag และการกลับมาเลื่อนต่อหลังผู้ใช้ปล่อย
- ไม่มีปุ่มเริ่ม/หยุด ลูกศรเลื่อน ข้อความสถานะการเลื่อน หรือ Scrollbar
- ป้องกันการเปิดลิงก์โดยไม่ตั้งใจหลัง Drag และหยุดการเลื่อนอัตโนมัติขณะนิ้วยังแตะค้าง
- รองรับ Keyboard Focus และ Enter ไปยัง Catalog ที่กรองแบรนด์จริง
- Reduced Motion ใช้แถบคงที่ซึ่งยังเลื่อนด้วยมือและคีย์บอร์ดได้ ส่วนที่อยู่นอกจอหรือแท็บที่ซ่อนจะไม่รัน Animation Frame
- คงเครดิตและไฟล์โลโก้เดิม 9 แบรนด์ ส่วน Córdoba ยังคงชื่อแบรนด์แบบตัวอักษรตามข้อจำกัดสิทธิ์ที่ระบุด้านล่าง

### Find My Guitar บน Home

- จัดสองคอลัมน์ตาม Reference: ภาพกีตาร์ไฟฟ้าจริง หัวข้อขาว–ทอง CTA และจำนวนจริง 200 รุ่น / 10 แบรนด์ / 4 ประเภท
- การ์ดแบบทดสอบมี Progress 1–5 ภาพถ่ายจริงสำหรับประเภทไฟฟ้า/โปร่ง/คลาสสิก/เบส และ Selected State สีทอง
- ทำคำถามครบ 5 ขั้นได้บน Home พร้อม Back/Next และการเก็บคำตอบระหว่างขั้น
- คงตัวเลือกเดิมทั้ง **22 ตัวเลือก** รวม “ยังไม่แน่ใจ” จำนวนแต่ละขั้น 5/3/5/5/4
- ส่งคำตอบไปยัง `/find-my-guitar` เพื่อใช้ระบบจัดอันดับ คะแนน เหตุผล และหน้าผลลัพธ์เดิม ไม่มีการสร้าง Recommendation Logic ใหม่

### Side by Side บน Home

- ภาพบรรยากาศจริงที่มีกีตาร์ไฟฟ้าและโปร่ง หัวข้อขาว–ทอง CTA และการ์ดจุดเด่น 3 รายการ
- ตัวอย่างเริ่มต้นใช้ **Yamaha FG820-12 กับ Martin D-28** ซึ่งมีภาพถ่ายที่ลงทะเบียนตรงกับ Guitar ID จริง โดยไม่เพิ่มสองรุ่นนี้ลงรายการของผู้ใช้เอง
- เมื่อผู้ใช้เลือก Compare ไว้ 2–4 รุ่น จะแสดงรายการจริงนั้น พร้อมปุ่มลบและเชื่อมต่อ ShopContext เดิม
- แสดงข้อมูลจริง 8 แถว: คอ ตัวกีตาร์ ฟิงเกอร์บอร์ด ปิ๊กอัพ สเกล เฟรต น้ำหนัก และราคา ข้อมูลที่ไม่ทราบยังคงไม่ระบุ
- Switch “แสดงเฉพาะส่วนที่ต่างกัน” ทำงานจริง สามารถขยายตารางเดิมและเปิดหน้า Compare พร้อม ID ของรุ่นที่กำลังแสดง
- ตารางเลื่อนแนวนอนเมื่อพื้นที่จำกัด ไม่มีการสร้างสเปกหรือคัดลอกตัวเลขจากภาพ Reference

### ภาพและองค์ประกอบร่วม

- Hero หน้า Home ใช้ภาพถ่ายจริงที่มีสิทธิ์ใช้งาน พร้อมคง Search, CTA และสถิติเดิม
- การ์ดหมวดกีตาร์ใช้ภาพจริงทั้ง 4 ประเภทและจำนวนที่คำนวณจาก Catalog
- ลดความสูง Hero และระยะห่างบางส่วน จัดหมวดเป็น 4 คอลัมน์ Desktop / 2 คอลัมน์ Tablet และ Mobile
- ไม่เปลี่ยน Navbar, Bottom Navigation, Catalog, Wishlist, หน้ารายละเอียด หรือระบบ Practice
- ไม่เพิ่ม Dependencies หรือข้อความโฆษณาเกี่ยวกับ AI

## ภาพจริงและสิทธิ์ใช้งาน

เพิ่มภาพต้นทางที่เลือกใช้ใหม่ 4 ภาพ แปลงเป็น WebP 9 ไฟล์ รวม **373,690 bytes** และใช้ภาพห้องดนตรีกับภาพ Martin ที่มีสิทธิ์อยู่แล้วซ้ำอย่างเหมาะสม มี `srcSet`, ขนาดภาพ และ Lazy Loading สำหรับภาพนอกหน้าจอแรก

แหล่งที่มา ผู้ถ่าย สัญญาอนุญาต และ SHA-256 อยู่ใน [รายงานภาพ](photos/README.md) / [Manifest](photos/manifest.json) ภาพหมวดใช้แสดงประเภทกีตาร์ ไม่ถูกนำไปอ้างว่าเป็นภาพของสินค้าอีกชื่อรุ่นหนึ่ง ภาพในการ์ด Compare ยังคงใช้ Registry ของแต่ละ Guitar ID

เครดิตบนเว็บไซต์: `/image-credits#home-photography` ภาพ CC BY-SA และไฟล์ดัดแปลงยังอยู่ภายใต้สัญญาอนุญาตของแต่ละภาพ

## ภาพผลลัพธ์จากเว็บจริง

ภาพด้านล่างเป็น Viewport Screenshot จาก Production Build จริง โดยคง Navigation บนจอไว้ ภาพ Section แบบยาวและ Before อยู่ในชุด QA เพิ่มเติม

| ขนาดจอ | Hero | แถบแบรนด์ | Find My Guitar | การ์ด Quiz | Side by Side | การ์ด Compare |
|---|---|---|---|---|---|---|
| Desktop | [ภาพ](screenshots/desktop-hero.png) | [ภาพ](screenshots/desktop-brands.png) | [ภาพ](screenshots/desktop-quiz.png) | [ภาพ](screenshots/desktop-quiz-panel.png) | [ภาพ](screenshots/desktop-compare.png) | [ภาพ](screenshots/desktop-compare-panel.png) |
| Tablet | [ภาพ](screenshots/tablet-hero.png) | [ภาพ](screenshots/tablet-brands.png) | [ภาพ](screenshots/tablet-quiz.png) | [ภาพ](screenshots/tablet-quiz-panel.png) | [ภาพ](screenshots/tablet-compare.png) | [ภาพ](screenshots/tablet-compare-panel.png) |
| Mobile | [ภาพ](screenshots/mobile-hero.png) | [ภาพ](screenshots/mobile-brands.png) | [ภาพ](screenshots/mobile-quiz.png) | [ภาพ](screenshots/mobile-quiz-panel.png) | [ภาพ](screenshots/mobile-compare.png) | [ภาพ](screenshots/mobile-compare-panel.png) |

[Before ที่ผูกกับ Commit เดิม](tests/before/) · [ภาพและผล Browser QA หลังพัฒนา](tests/final/) · [ผลตรวจภาพอิสระ 20 กรณี](visual-review/README.md)

Long Element Screenshot อาจบันทึก Fixed Navbar/Skip Link ในตำแหน่งจากการ Stitch ภาพ เอกสาร Visual Review มีหลักฐาน Viewport จริงว่า Skip Link ซ่อนอยู่นอกจอเมื่อไม่ได้ Focus จึงไม่ได้แก้ระบบ Accessibility เพื่อปกปิดอาการจากการจับภาพ

## ผลทดสอบ

รายละเอียดคำสั่ง ผลผ่าน/ไม่ผ่าน และข้อจำกัดอยู่ใน [TEST-RESULTS.md](tests/TEST-RESULTS.md) โดยเก็บผลที่ไม่ผ่านก่อนแก้ไขไว้ด้วย ไม่ลดเกณฑ์เพื่อให้ผ่าน

- Home Production Browser Acceptance **32/32 ผ่าน** บน Chromium 154 และ Linux WebKit 26.5 ไม่พบ Console/Runtime/Request/HTTP Error และ Source/Build ไม่เปลี่ยนระหว่างรัน ความเร็วแถบแบรนด์ที่วัดได้ทั้งหกกรณีอยู่ที่ **29.390–30.615 px/s** จุดวนรอบที่ตรวจมีระยะเคลื่อนต่อเฟรมสูงสุด 1px โดยไม่พบช่องว่าง
- Regression ของหน้า Quiz/Compare เดิม **25/25 ผ่าน** บน Production Build เดียวกัน โดยไม่เปลี่ยน Script หรือเกณฑ์ทดสอบเดิม ตรวจไฟล์ที่ต้องรักษา **180 ไฟล์** ตรงกับ Commit ก่อนแก้ทุก byte
- Build, Catalog Check, Images Check, Practice Check และ Quiz/Compare Logic เดิมได้รับการรันจริง
- ภาพใหม่ผ่านการตรวจ 39 ข้อ ทั้งการ Decode, Hash, สัดส่วน, ความโปร่งใสของต้นทาง และขนาดไฟล์
- ตรวจข้อมูลและระบบที่ต้องรักษาเทียบ Commit เดิมแบบ Byte-for-byte รวมฐานข้อมูล 200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 รุ่น, Guitar ID, หน้า Quiz/Compare แยกจาก Home และ Practice/คอร์ด 42 แบบ
- Browser QA ครอบคลุม Chromium และ Linux WebKit, Desktop/Tablet/Mobile, จอแคบ 320px และแนวนอน, Touch, Drag, Loop, Reduced Motion, Quiz และ Compare

Linux WebKit และการส่ง Touch Gesture ผ่าน Browser Automation **ไม่ใช่การทดสอบบน iPad Safari เครื่องจริง** จึงยังไม่อ้างว่าผ่านอุปกรณ์จริง

พบและแก้ข้อผิดพลาดการนับเวลา Animation: เพดานเวลาต่อเฟรม 48ms เดิมทำให้ช่วงที่ WebKit ส่งเฟรมช้าเลื่อนแบรนด์ช้ากว่าที่กำหนด จึงเปลี่ยนให้นับเวลาจริงและ Reset Clock เมื่อกลับมาแสดงผล วัดตำแหน่งและเวลาที่ตรงกับเฟรมจริงได้ 29.866 / 30.414 / 30.084 px/s ทั้งสามขนาดจอ รายละเอียดและผลก่อนแก้อยู่ใน [WebKit Motion Fix](tests/webkit-motion-fix/README.md)

แก้การตัดแรงเลื่อน Native ของ WebKit ด้วย: การรับ Scroll Event เดิมเขียน `scrollLeft` ค่าเดิมกลับไปโดยไม่จำเป็น ซึ่งยกเลิก Wheel/Touch Momentum จึงเปลี่ยนให้เขียนเฉพาะเมื่อต้องเลื่อนจริงหรือย้ายไปชุดซ้ำเมื่อวนรอบ เก็บ Raw Trace ก่อนแก้ใน [webkit-wheel-trace.json](tests/webkit-wheel-trace.json)

ยังพบช่วงเริ่มต้นที่ Linux WebKit แบบ Software Rendering ส่งเฟรมห่างกันหลายร้อย ms การรอ Decode ภาพ/ฟอนต์หรือทดลอง Compositor Promotion ไม่ช่วยอย่างมีนัยสำคัญ จึงไม่ได้เพิ่มวิธีแก้ที่ไม่มีหลักฐานรองรับ และไม่อ้างว่าช่วงโหลดแรกหรือ iPad จริงลื่นผ่านเกณฑ์แล้ว

ขนาด Entry JavaScript เพิ่มประมาณ 7.54kB gzip และ CSS เพิ่มประมาณ 4.31kB gzip จาก Build ก่อนหน้า ไม่มี Dependency ใหม่ ภาพใหม่โหลดตามตำแหน่งที่ใช้และไฟล์ที่ใช้ซ้ำไม่ถูกทำสำเนา Three.js/GLB ยังไม่ถูกโหลดจาก Home ส่วน Build Warning ของ Three.js Chunk ขนาดเดิมยังคงอยู่

## สิ่งที่ยังขาดและข้อแตกต่างจาก Reference

1. **โลโก้ Córdoba:** ยังคงใช้ชื่อแบรนด์แบบตัวอักษร เนื่องจาก [ข้อกำหนดเจ้าของแบรนด์](https://yamahaguitargroup.com/trademark-guidelines/) จำกัดการใช้ Designed Logo และยังไม่มีสิทธิ์ที่ยืนยันได้ ไม่สร้างโลโก้ปลอม
2. **ภาพสินค้า:** ภาพสินค้าของ Catalog เดิม 197 รุ่นยังไม่มีไฟล์ที่เผยแพร่ได้ และ Pacifica มีภาพประกอบเดิมซึ่งไม่ได้อ้างว่าเป็นภาพถ่าย ดู [รายการรุ่นที่ยังขาดภาพ](MISSING-PRODUCT-PHOTOS.md) ส่วน Featured Collection เดิมยังคงพฤติกรรมและ Fallback เดิม ไม่ถูกเติมภาพคนละรุ่น
3. **คู่ Compare เริ่มต้น:** เป็นกีตาร์โปร่งสองรุ่นที่มีภาพจริง แทนคู่ไฟฟ้า/โปร่งใน Reference ไม่มีการสลับภาพ Stratocaster ที่ไม่ตรงรุ่นมาใช้
4. **ภาพบรรยากาศ:** เป็นภาพห้องดนตรีจริงและกีตาร์บนผ้าสีเข้ม ไม่ใช่ฉากสตูดิโอเดียวกับภาพต้นแบบ ใช้ CSS Gradient เพื่อให้ข้อความอ่านได้
5. **ข้อมูลจริง:** จำนวนหมวด สเปกที่ยังไม่ทราบ และราคายึดตาม Catalog ไม่คัดลอกตัวเลขในภาพต้นแบบ
6. ยังต้องให้ผู้ใช้ตรวจ Safari บน iPad จริง และยังไม่ได้เผยแพร่แทน `master`

## กลุ่มไฟล์ที่แก้

- `src/components/home/Brands.jsx`, `src/hooks/useBrandMarquee.js`, `src/styles/home-brands.css`
- `src/components/home/FindMyGuitar.jsx`, `src/styles/home-quiz-premium.css`
- `src/components/compare/CompareSection.jsx`, `src/styles/home-compare-premium.css`
- `src/components/home/Hero.jsx`, `CategoryCard.jsx`, `src/pages/HomePage.jsx`, `src/styles/home-premium.css`
- `src/assets/home-discovery/`, `src/data/homeDiscoveryAssets.js`
- `src/components/detail/HomePhotographyCredits.jsx`, `src/pages/ImageCreditsPage.jsx`
- เอกสาร แหล่งภาพ Screenshot และผลทดสอบในโฟลเดอร์นี้

## เปิดดูบน Codespaces / iPad

ใช้ Repository เดิมและ Branch ที่ Push งานนี้:

```bash
git fetch origin
git switch feature/premium-quiz-compare
git pull --ff-only origin feature/premium-quiz-compare
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

จาก **Ports → 5173 → Open in Browser** ให้เปิด HTTPS URL ของ Codespaces แล้วเข้า `/` ไม่ใช้ `localhost` จาก Safari บน iPad หากมีไฟล์ที่แก้ค้างใน Codespaces ให้เก็บงานนั้นก่อนเปลี่ยน Branch ไม่ใช้คำสั่งลบทิ้ง

ตรวจบน iPad จริงทั้งแนวตั้ง/แนวนอน: ปล่อยแถบแบรนด์เลื่อนหลายรอบ Swipe/แตะค้าง/ปล่อย/แตะลิงก์แบรนด์, ทำ Quiz 5 ขั้นและย้อนกลับ, เลือก Compare 2–4 รุ่น ลบ เปลี่ยน Switch เปิดตารางเต็ม และตรวจว่าไม่มีภาพเสียหรือหน้าเว็บล้นแนวนอน
