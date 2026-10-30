# Fretline — งานปรับประสบการณ์ผู้เข้าชมและคืนแถบแบรนด์เดิม

ทำงานบน `feature/fretline-ultimate-experience` ต่อจาก `f8084ef8f1cf8db65d150bc500c4ea9b6f851c35` เท่านั้น ไม่มีการ Push, Merge หรือ Deploy และไม่ได้เปลี่ยนฐานข้อมูล

## สถานะและขอบเขตล่าสุด

งาน Ultimate ปรับรูปลักษณ์หน้า Home, Brands, Catalog, รายละเอียดกีตาร์, Compare, Find My Guitar, รายการโปรด, Practice, เครดิตภาพ, QR และหน้าที่ไม่พบ ตามเส้นทางเดิม บันทึกสถานะที่พัฒนาไว้เป็น checkpoint `4902be0` ก่อนรับคำสั่งคืน Brand Marquee

หลัง checkpoint นี้แก้ **เฉพาะ Brand Marquee บน Home**: นำกรอบและพื้นหลังรายโลโก้ออกจากสไตล์ใหม่ คืน component, hook และพฤติกรรมรางเลื่อนให้ตรงกับ `f8084ef` และนำ animation reveal ของหัวข้อแถบแบรนด์ออกจากตัวครอบ presentation ส่วนอื่นคงตาม checkpoint ทุกไฟล์ ตรวจยืนยันใน [หลักฐานขอบเขตการคืนแถบแบรนด์](tests/marquee-restoration-proof.json)

## สิ่งที่พัฒนา

| ส่วน | ผลลัพธ์ |
| --- | --- |
| Design system | สี Charcoal, Champagne และ Warm Ivory, ระยะห่าง ตัวอักษร ปุ่ม focus และพื้นผิวที่สอดคล้องกัน สไตล์ครอบเฉพาะ `.fretline-experience` |
| Home | Hero ใช้ภาพเดิม 3 ฉาก ตัวอักษรไทยเด่นขึ้น สถิติจากข้อมูลจริง การ์ดหมวดแบบแคปซูล และส่วนแนะนำกีตาร์เดิมครบ |
| Brand Marquee | **คืนรางเดิมจาก Git** โลโก้เรียงต่อกัน ไม่มีการ์ดหรือกรอบรายโลโก้ เลื่อนขวาไปซ้ายด้วยความเร็วเดิม 30 CSS px/วินาที รองรับลาก/ปัด โฟกัสคีย์บอร์ด และ Reduced Motion |
| Brands | จัดแกลเลอรีภาพแบรนด์เดิมให้สมดุลขึ้น โลโก้และเส้นทางเข้าหมวดเดิมไม่เปลี่ยน |
| Catalog | แกลเลอรีสินค้า ช่องค้นหา หมวด ตัวกรอง การเรียงลำดับ จำนวนผลลัพธ์ และ pagination ใช้ตรรกะเดิมทั้งหมด |
| รายละเอียดกีตาร์ | ขยายพื้นที่ gallery และ thumbnail จัดชื่อรุ่น ราคา แหล่งอ้างอิง ปุ่ม และสเปกตามลำดับการอ่าน ภาพขยายและการเลือกสีใช้ระบบเดิม |
| Compare | ปรับขนาดการ์ด ตาราง แถบหมวดข้อมูล และเส้นเน้นแถวที่แตกต่าง โดยไม่เปลี่ยนการคำนวณหรือเพดาน 4 รุ่น |
| Find My Guitar | จัด progress, คำถาม ตัวเลือก ปุ่มและผลลัพธ์ใหม่ด้วยสไตล์เดียวกัน คำถาม 5 ข้อ ตัวเลือก 22 ข้อ คะแนนและผลลัพธ์เดิม |
| รายการโปรด | จัดรายการเป็นคอลเลกชันที่อ่านง่าย การบันทึก การลบ การยืนยัน และข้อมูลใน localStorage เดิม |
| Practice | ปรับเฉพาะสี พื้นผิว ระยะห่างและขนาดพื้นที่ฝึก ระบบ renderer/โมเดลมือ/กล้อง/ตำแหน่งนิ้ว/คอร์ดไม่เปลี่ยน |
| Home Practice banner | ใช้ไฟล์ Les Paul สีดำที่เจ้าของส่งมา ไฟล์ต้นฉบับไม่เปลี่ยน ข้อความ ไอคอน จำนวนคอร์ดและ CTA เดิมอยู่ครบ |
| Navigation และเส้นทางอื่น | ปรับเมนู ปุ่ม เมนูมือถือ Bottom Bar, Footer, Loading, QR และหน้าไม่พบ ให้เป็นระบบเดียวกัน พร้อมพื้นที่สำหรับแถบลอย |
| Motion | Reveal ระยะสั้นและ hover ด้วย transform/opacity, ไม่เพิ่ม animation library, ยกเว้น Admin, รองรับ Reduced Motion และแสดงเนื้อหาเสมอหากไม่มี IntersectionObserver |
| ภาษาไทย | คง UI ภาษาไทยจากงานก่อนหน้า พร้อมแปลข้อความตกแต่งที่หลงเหลือใน Practice/collection ชื่อรุ่น แบรนด์ รหัสและศัพท์เทคนิคไม่เปลี่ยน |

### แถบแบรนด์ที่คืนแล้ว

- [Desktop หลังคืนรางเดิม](screenshots/after-desktop-marquee.png)
- [Desktop ก่อนคืนรางเดิม — ระหว่าง Ultimate](screenshots/before-restore-desktop-marquee.png)
- [iPad แนวนอน](screenshots/after-landscape-marquee.png)
- [iPad แนวตั้ง](screenshots/after-portrait-marquee.png)
- [มือถือ](screenshots/after-mobile-marquee.png)
- [ปลายรางที่แสดงแบรนด์ชุดถัดไป](screenshots/after-desktop-marquee-end.png)

มี 10 แบรนด์ครบตามข้อมูลเดิม ใช้โลโก้ไฟล์เดิม 9 แบรนด์ และชื่อ Córdoba เดิม เนื่องจากโปรเจกต์ไม่มีโลโก้ Córdoba แยกที่ยืนยันไว้ ไม่สร้างโลโก้ใหม่หรือใช้โลโก้ผู้อื่นแทน

## การป้องกันข้อมูลและระบบ

- สถานะก่อนเริ่มสะอาด ไม่มี uncommitted changes จุดย้อนกลับ Git: `backup/fretline-before-ultimate-20261030-f8084ef`
- ก่อนแก้เก็บ SHA ของไฟล์ tracked ทั้ง 4,820 ไฟล์ และสำเนา production build ไว้ใน `.local-preview/ultimate-experience/` ซึ่งไม่ถูกเผยแพร่
- ก่อนคืนแถบแบรนด์เก็บ archive และ patch ของงานที่ยังไม่ส่งมอบไว้เพิ่มเติม แล้ว commit checkpoint `4902be0`
- ตรวจ SHA ไฟล์ runtime/ข้อมูล/asset/ระบบเดิม **302 ไฟล์** และ SHA ของข้อมูลที่คำนวณแล้วทุกฟิลด์ให้ตรงกับ baseline
- กีตาร์ **200 รุ่น / 200 ID ไม่ซ้ำ / 10 แบรนด์ × 20 รุ่น / 4 ประเภท**: ไฟฟ้า 90, โปร่ง 73, คลาสสิก 20, เบส 17
- คอร์ด 42 คอร์ด รูปแบบการจับ สถานะการตรวจท่ามือและแหล่งอ้างอิงไม่เปลี่ยน
- ราคา ชื่อรุ่น คำอธิบาย สเปก แหล่งอ้างอิง วันที่ตรวจ รูปภาพและความสัมพันธ์กับรุ่น สถานะสินค้า รวมรายการเก่าที่บันทึกไว้ ไม่เปลี่ยน
- ราคาอ้างอิงเดิม 27 รุ่น อีก 173 รุ่นใช้การแสดง “สอบถามราคา” เดิม
- รุ่นที่มีไฟล์ภาพผูกอยู่เดิม 3 รุ่น อีก 197 รุ่นใช้สถานะไม่มีภาพเดิม การทดสอบไม่ถือว่าการไม่มีภาพต้นทางเป็น broken image และไม่เติมภาพคนละรุ่นแทน
- Admin source, Authentication, Supabase client, RLS/schema/SQL/seed, Published/Draft, API, routes, scoring, filter/search, comparison และ localStorage ไม่เปลี่ยน
- Admin ได้รับ stylesheet ใหม่ใน bundle แต่ selector ของทุก rule จำกัดที่ visitor boundary ซึ่งไม่ใช้กับ `/admin` ตรวจ computed styles เทียบก่อน/หลังทั้ง 6 ขนาดในสอง engine

ผล: [Data safety](tests/data-safety.json), [Baseline](safety-baseline.json), [สรุปรวม](tests/summary.json)

## ผลทดสอบ

| การตรวจ | ผล |
| --- | --- |
| `npm run build` | ผ่าน มีคำเตือน chunk Three.js ประมาณ 709 kB เดิม |
| `npm run catalog:check` | ผ่าน 200 รุ่น 10 แบรนด์ ราคาและข้อมูลที่ยังไม่ทราบถูกต้อง |
| `npm run images:check` | ผ่าน การลงทะเบียนภาพ สิทธิ์และ SHA ไฟล์เดิม |
| `npm run admin:check` | 9/9 |
| `npm run deploy:test` | 7/7 — เป็นการทดสอบเท่านั้น ไม่ได้ Deploy |
| `npm run phase4:check` | 19/19 |
| `npm run phase5:check` | 15/15 |
| `npm run practice:check` | 56/56 |
| Data/route/Admin/3D safety guard | ผ่านทุกเงื่อนไข |
| Catalog browser suite | 38/38 |
| Quiz/Compare browser suite | 31/31 |
| Interaction suite | 22/22 หลังตรวจซ้ำ workflow ที่ติด deadline ใน WebKit |
| Public routes / responsive / Admin isolation / marquee | 180/180 กลุ่มตรวจไม่ซ้ำ หลังตรวจซ้ำกรณี Cache 304 |

รวม **106 unit checks + 271 browser check groups** บน Chromium และ Linux WebKit ใช้ข้อมูลจริงของโปรเจกต์ ไม่มี mock ข้อมูลหรือคำสั่งเขียนฐานข้อมูล

ขนาดจอ: Desktop 1440×1000, iPad Landscape 1194×834, iPad Portrait 768×1024, Mobile Portrait 390×844, จอแคบ 320×740 และ Mobile Landscape 844×390

ตรวจทุก public route, การค้นหา/กรอง/เรียงลำดับ/แบ่งหน้า, รายละเอียดและสเปก, thumbnail/lightbox/คีย์บอร์ด, favorites และ persistence, คำถาม/ผลลัพธ์/คะแนน Quiz, Compare สูงสุด 4 รุ่นและแถวข้อมูลจริง, ปุ่ม Home ทั้งสาม, การแตะเข้าหมวดและแบรนด์ทั้ง 10, เมนูมือถือ, 3D พร้อมโหลดจริง ปุ่มกล้อง การค้นหาคอร์ดและตำแหน่งนิ้ว 6 voicing ตามข้อมูลเดิม ไม่มี horizontal overflow, broken image หรือ console/runtime error จากการเปลี่ยนแปลง

การตรวจรอยต่อแถบแบรนด์วัดตำแหน่งเลื่อนจริงใกล้จุดวน ตรวจลากและกลับมาอัตโนมัติ รวมทั้งการหยุดเมื่อโฟกัสคีย์บอร์ดและไม่มี autoplay เมื่อ Reduced Motion

เก็บหลักฐานกรณีตรวจซ้ำใน [recheck-evidence.json](tests/recheck-evidence.json): 9 กรณี WebKit เดิมไม่รับ HTTP 304 ที่เป็น Cache revalidation สำเร็จ และ 1 workflow โหลด lazy route 3D เกิน deadline 5 วินาทีระหว่างรันหลาย browser พร้อมกัน ตรวจกรณีเดิมซ้ำผ่านโดยรองรับ 200/304 และใช้ deadline 15 วินาที ไม่มีการแก้ข้อมูลหรือระบบเพื่อให้ทดสอบผ่าน

โปรเจกต์ไม่มีสคริปต์ Lint/Typecheck จึงไม่ได้อ้างว่ารันสองรายการนี้

## Performance

ใช้ฟอนต์ไทยในโปรเจกต์และ preload น้ำหนักปกติ ให้ภาพ Hero แรกมี priority สูง เลื่อนโหลดภาพรองเดิมออกไป 2.5 วินาที ขนาด responsive image สอดคล้องพื้นที่จริง รูปที่ไม่ใช่ Hero ใช้ lazy loading เดิม 3D/โมเดลมือยังโหลดเฉพาะหน้า Practice ไม่เพิ่ม dependencies หรือ animation library

วัดก่อน/หลัง 3 ครั้งต่อเวอร์ชัน บน Chromium จอ 390×844 จำลอง CPU ช้าลง 4 เท่า, latency 40 ms, download 10 Mbps, cache ใหม่ต่อครั้ง หลังชุด browser อื่นจบแล้ว:

| ค่าจาก local lab | ก่อน | หลัง |
| --- | --- | --- |
| LCP มัธยฐาน | 1.592 s | 1.532 s |
| CLS มัธยฐาน | 0 | 0 |
| Event timing สูงสุดที่สังเกตใน workflow ตัวอย่าง | 72 ms | 56 ms |

ค่า event timing เป็นตัวอย่าง interaction ใน lab ไม่ใช่การรับรอง field INP ไม่ได้อ้างว่าผ่าน Core Web Vitals บน production หรือ iPad เครื่องจริง ผลและเงื่อนไขครบใน [performance-lab.json](tests/performance-lab.json)

## ภาพก่อน–หลัง

| หน้า | ก่อน Ultimate (`f8084ef`) | หลัง — รวมการคืนรางแบรนด์ |
| --- | --- | --- |
| Home Desktop | [ก่อน](screenshots/before-desktop-home.png) | [หลัง](screenshots/after-desktop-home.png) |
| Home iPad แนวนอน | [ก่อน](screenshots/before-landscape-home.png) | [หลัง](screenshots/after-landscape-home.png) |
| Home iPad แนวตั้ง | [ก่อน](screenshots/before-portrait-home.png) | [หลัง](screenshots/after-portrait-home.png) |
| Home Mobile | [ก่อน](screenshots/before-mobile-home.png) | [หลัง](screenshots/after-mobile-home.png) |

ภาพหน้าอื่นหลังปรับ: [Catalog](screenshots/after-desktop-catalog.png), [Brands](screenshots/after-desktop-brands.png), [รายละเอียด](screenshots/after-desktop-detail.png), [Compare](screenshots/after-desktop-compare.png), [Quiz](screenshots/after-desktop-quiz.png), [Practice](screenshots/after-desktop-practice.png), [Favorites](screenshots/after-desktop-favorites.png), [QR](screenshots/after-desktop-qr.png)

ภาพทั้งหมดมาจาก browser ที่รัน production build จริง ไม่มีการแต่งภาพ ภาพ viewport ปกติมี Navigation จริง ส่วนภาพเฉพาะรางแบรนด์ซ่อนเฉพาะ fixed navigation ระหว่าง capture เพื่อให้เห็นรางครบ ไม่แก้ source หรือพฤติกรรมในการทดสอบคลิก

## สิ่งที่ยังต้องตรวจเพิ่มเติม

1. Safari บน iPad/iPhone เครื่องจริง — WebKit บน Linux และ touch emulation ไม่ใช่อุปกรณ์จริง
2. Login/Logout, เพิ่ม/แก้ไข, Draft/Publish, Storage upload และการอ่าน Published จาก **Supabase จริง** — workspace/หน้าเว็บทดสอบไม่มีการเชื่อมต่อที่ตั้งค่าไว้ ตรวจ source/validation/UI isolation ได้ แต่ไม่อ้างว่าทดสอบธุรกรรมจริง ไม่มีการขอหรือแสดงคีย์ลับ
3. Core Web Vitals จากโดเมนจริงและผู้ใช้จริงหลังได้รับอนุญาต Deploy
4. ภาพรุ่นที่ขาด 197 รุ่นและโลโก้ Córdoba แยกยังเป็นข้อจำกัดเดิม ไม่เติมหรืออ้างภาพใหม่เป็นสินค้าจริง

## วิธีตรวจงานและย้อนกลับ

ไม่มี URL ใหม่ที่เผยแพร่ เพราะเจ้าของยังไม่อนุญาต Deploy เว็บเดิมจึงยังไม่เปลี่ยน ภาพและผลตรวจในรายงานนี้เป็นสถานะล่าสุดใน feature branch

รันตรวจ source/build ได้ด้วย:

```sh
node scripts/check-ultimate-experience.mjs
npm run catalog:check
npm run images:check
npm run admin:check
npm run phase4:check
npm run phase5:check
npm run practice:check
npm run build
```

ตรวจแบบ local ผ่าน `npm run dev -- --host 0.0.0.0 --port 5173 --strictPort` ใน checkout branch นี้ URL Codespaces ต้องได้จากแถบ Ports ของ Codespace ที่รันโค้ด branch นี้จริง ไม่ควรนำ URL เก่ามาอ้างว่าเป็นเวอร์ชันล่าสุด

ย้อนตรวจดีไซน์ก่อน Ultimate ใน checkout แยก โดยไม่ลบงานปัจจุบัน:

```sh
git worktree add -b feature/review-before-ultimate ../fretline-before-ultimate backup/fretline-before-ultimate-20261030-f8084ef
```

`4902be0` เป็น checkpoint งาน Ultimate ก่อนคืนแถบแบรนด์ ทั้งสองจุดยังอยู่ ไม่ใช้ `reset --hard`, force push, database restore หรือการ revert ทั้งโปรเจกต์

รายชื่อไฟล์: [CHANGED-FILES.md](CHANGED-FILES.md)
