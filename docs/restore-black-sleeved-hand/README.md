# Fretline — กู้คืนมือ 3D พร้อมแขนเสื้อดำ

พัฒนาต่อจาก `cb6d8195c1fcb18da10429e9991365e7497e0b4c` บน `feature/restore-black-sleeved-hand` โดยไม่ Merge branch เก่าทั้งก้อน ไม่เปลี่ยนข้อมูลสินค้า และไม่แก้ Admin Studio

## สิ่งที่พบและกู้คืน

Branch ต้นทาง `origin/feature/guitar-practice-3d` คือ `decd5544ade430530ac7c1e37ae463f251c90d50` โมเดล GLB, rig, pose library, ข้อมูลคอร์ด และ scene ในเวอร์ชันล่าสุดตรงกับต้นทางอยู่แล้วทั้ง 13 ไฟล์ แต่การปรับ UI ภายหลังนำปุ่มแสดงมือและปุ่ม retry โมเดลออก ท่าที่รอตรวจทานจึงถูกซ่อนตลอด

งานนี้กู้คืนการควบคุมเดิมใน `GuitarNeckViewer` และเชื่อมกับ scene จริงที่อยู่ในหน้า `/practice` อยู่แล้ว:

- แสดงโมเดลมือและแขนเสื้อดำเมื่อโมเดลโหลดจริงและคอร์ดนั้นผ่าน geometry/contact gate เดิม แสดงคำเตือนว่าท่ามือยังรอตรวจทาน ไม่อ้างว่าเป็นท่าสอนที่ตรวจครบแล้ว
- เลือกคอร์ดแล้วใช้ root/bone transforms ของคอร์ดนั้นจริง คงผังคอร์ดและจุดนิ้วจากข้อมูลเดิม ไม่ใส่มือของคอร์ดอื่นแทน
- คืนปุ่มซ่อน/แสดงมือ และจำการเลือกนี้ระหว่างเปลี่ยนคอร์ดในหน้าที่เปิดอยู่ ท่าที่ตรวจไม่ผ่านยังไม่มีทางถูกเปิดผ่าน UI หรือ engine
- คืนปุ่มลองโหลดโมเดลมืออีกครั้งเมื่อการดาวน์โหลดล้มเหลว โดยไม่ต้องเปลี่ยนคอร์ดหรือรีเซ็ตกล้อง
- คงคอกีตาร์ 6 สาย, กล้อง 7 มุมมอง, หมุน/ซูม/รีเซ็ต, drag, touch/pinch, keyboard, context-loss recovery และ resource cleanup เดิม แก้พื้นที่โปร่งใสของเมนูมุมมองที่บังปุ่มกล้องเมื่อเปิดเมนูบนจอแคบ
- ใช้ transition เฟดสั้น 160 ms จากระบบเดิมขณะเปลี่ยนท่า ไม่มีการเพิ่ม bone interpolation ที่ยังไม่ได้ตรวจเส้นทางการเคลื่อนไหวผ่านคอหรือผ่านนิ้วอื่น
- Three.js `0.186.1` และ dependencies ที่ต้องใช้มีอยู่ครบแล้ว ไม่มีการติดตั้ง dependency ใหม่

## ข้อจำกัดของ 42 คอร์ดที่ต้องบอกตามจริง

ข้อมูลคอร์ดและผังมี **42 คอร์ดครบ** แต่ท่ามือที่ผ่านการตรวจ geometry/contact มีเพียง **7 คอร์ด**: C, Dm, E7, Cmaj7, Fmaj7, Em7 และ Am7

ท่าที่ใช้สอนและตรวจยืนยันครบทุกด้านมี **0 คอร์ด** สถานะทั้ง 42 คอร์ดยังคง `needs-review` เหมือนต้นทาง ไม่เปลี่ยน audit flags เพื่อให้แสดงผลผ่าน

อีก **35 คอร์ด** มีท่าต้นฉบับที่ไม่ผ่านการตรวจการชน/สัมผัส จึงใช้ผังคอร์ดและจุดวางนิ้วต่อไป ไม่แสดงมือที่ทราบว่าตรวจไม่ผ่าน การกู้คืน UI ไม่สามารถแก้ข้อผิดพลาดในท่าต้นฉบับเหล่านี้ได้ และยังไม่ถือว่าส่งมอบท่ามือที่ถูกต้องครบ 42 คอร์ด

หลักฐานเดิมครบ 42 แถวอยู่ที่ [สถานะท่ามือเดิม](../practice-hand-batch-3/CHORD-STATUS-42.md) ส่วน solver รุ่นปิดงานยืนยันว่าไม่มีท่าใหม่ผ่านเพิ่มใน [CLOSEOUT.json](../practice-final-delivery/solver/CLOSEOUT.json) งานนี้ไม่สร้างท่าทดแทนขึ้นมาเอง

## โมเดลจริงและความปลอดภัยข้อมูล

- GLB เดิมขนาด **1,012,288 bytes** SHA-256 `23fdb5745e9343b597eb816bcdfcb266c1942ebbbb495cdb3776214343d7f3bc`
- Mesh `Black_LongSleeve_ForearmMesh` และ `MakeHuman_Left_Hand_ForearmMesh`; material แขนเสื้อ `Black_Cotton_LongSleeve_Elvaerwyn`
- Pose library เดิม SHA-256 `2e2816f7adf533f80fba931e4d73b592a670a614ea014406903da162b5f01aa1`
- ใช้ skin/rig/weights และเครดิต MakeHuman CC0 / Elvaerwyn CC-BY เดิม ไม่ใช้ภาพนิ่งหรือ rig จำลองแทนโมเดลจริง
- [ตรวจข้อมูลและต้นทาง](tests/source-and-data.json): กีตาร์ 200 IDs ไม่ซ้ำ, 10 แบรนด์ แบรนด์ละ 20 รุ่น และ 42 คอร์ด ข้อมูลรวม gallery/ราคา/สเปก/คำอธิบายมี checksum ตรงฐานเดิม
- ไม่เปลี่ยน assets, ราคา, สเปก, ชื่อรุ่น, Supabase/SQL/schema/RLS, Auth, Catalog, Home, Hero, Brand Marquee, Compare, Favorites, Find My Guitar หรือระบบภาพที่เพิ่งพัฒนา

## ไฟล์ที่แก้

โค้ดแอปแก้เพียง:

1. `src/features/practice/components/GuitarNeckViewer.jsx` — คืนการแสดงมือ, สถานะที่ตรงจริง, toggle, retry และ preference ที่มีผลเฉพาะ pose ที่ engine อนุญาต
2. `src/features/practice/components/viewer.css` — จัดแถบควบคุมมือและแก้ hit area ของเมนูมุมมองให้ไม่บังปุ่มหมุน/ซูม

เพิ่มสคริปต์ตรวจ `scripts/check-restored-hand.mjs` และหลักฐานในโฟลเดอร์เอกสารนี้ ไม่มีการเปลี่ยนไฟล์โมเดลหรือข้อมูลคอร์ด

## ผลตรวจและหลักฐาน

ผลรวมและขอบเขตที่ยืนยันได้: [final-summary.json](tests/final-summary.json)

| การตรวจ | หลักฐาน |
| --- | --- |
| Build | [build.txt](tests/build.txt) |
| Runtime hand gates, loading, abort, retry, disposal 20 ข้อ | [hand-runtime.txt](tests/hand-runtime.txt) |
| Transition/reduced motion 10 ข้อ | [hand-reveal.txt](tests/hand-reveal.txt) |
| ข้อมูลคอร์ดและโครงสร้าง 56 ข้อ | [practice.txt](tests/practice.txt) |
| ตรวจเรขาคณิตใหม่ของ 7 ท่าที่เปิดได้ | [geometry/summary.json](tests/geometry/summary.json) |
| ต้นทางโมเดลและข้อมูลสินค้า | [source-and-data.json](tests/source-and-data.json) |
| Catalog และภาพ | [catalog.txt](tests/catalog.txt), [images.txt](tests/images.txt) |
| Browser ท่ามือ/กล้อง/การกู้คืน | [browser-hand.json](tests/browser-hand.json) |
| ตรวจกล้องซ้ำหลังแก้พื้นที่เมนูทั้ง 4 viewport | [browser-camera-recheck.json](tests/browser-camera-recheck.json) |
| Regression ทั้งเว็บ | [browser-results.json](browser-results.json) |
| ความพร้อมเผยแพร่ | [deploy-readiness.txt](tests/deploy-readiness.txt) |

Browser ทดสอบ WebGL และ GLB ของจริงจาก production build ไม่มี model fixture ใช้ Chromium บน Desktop 1440×1000, iPad แนวนอน 1194×834, iPad แนวตั้ง 768×1024 และ Mobile 390×844 มี touch/pinch ผ่าน Chromium CDP บน viewport สัมผัส **ไม่ได้เท่ากับการทดสอบ Safari บน iPad เครื่องจริง**

Build ผ่านโดยยังมีคำเตือนขนาด chunk Three.js เดิมประมาณ 709 kB ไม่มีการเพิ่ม dependency หรือรวม Three.js เข้ากับ bundle หน้าสินค้าใหม่จากงานนี้

ทดสอบการเลือกครบ 42 คอร์ดแต่ละ viewport, signatures ของ bone/root ที่เปลี่ยนจริง, 7 มือที่เปิดได้/35 ท่าที่ถูกซ่อน, ความต่างของ pixels ใน canvas เมื่อซ่อนมือโดยกล้องไม่เปลี่ยน, การโหลด GLB ล้มเหลวและ retry, WebGL context loss และ recovery, เฟดปกติและ reduced motion รวมถึงไม่มี render loop ตอนว่าง

ผลทดสอบเรขาคณิตใหม่ยืนยันเฉพาะ endpoints ทั้ง 7 ไม่ยืนยันกายวิภาค ความเป็นธรรมชาติ การจับกีตาร์จริงบน iPad หรือเส้นทาง bone animation ต่อเนื่อง

รอบ browser แรกผ่าน 21 จาก 23 กลุ่ม อีก 2 กลุ่มพบเมนูมุมมองบังปุ่มกล้องในแนวตั้ง/มือถือ จึงแก้เฉพาะ CSS hit area แล้วตรวจกล้องใหม่ทั้ง 4 viewport โดยใช้ pointer/touch จริง ไม่ใช้ force click รายงานก่อนแก้เก็บใน `tests/browser-before-menu-hit-area-fix.json`; รายงานรวมใช้ผลตรวจกล้องใหม่แทนรายการเดิม โค้ด rig/poses/scene และ JavaScript ของหน้าไม่เปลี่ยนระหว่างสองรอบนี้

## ภาพก่อน–หลังจากหน้า Practice จริง

| หน้าจอ | ก่อน | หลัง |
| --- | --- | --- |
| Desktop | [ก่อน](screenshots/before-desktop.png) | [หลัง](screenshots/after-desktop.png) |
| iPad แนวนอน | [ก่อน](screenshots/before-landscape.png) | [หลัง](screenshots/after-landscape.png) |
| iPad แนวตั้ง | [ก่อน](screenshots/before-portrait.png) | [หลัง](screenshots/after-portrait.png) |
| Mobile | [ก่อน](screenshots/before-mobile.png) | [หลัง](screenshots/after-mobile.png) |

ภาพ capture จาก WebGL จริง ไม่ได้สร้างหรือแต่งภาพมือ

## สถานะเว็บไซต์จริงและขั้นตอนเจ้าของบัญชี

**ยังไม่ Merge master และยังไม่ Deploy งานนี้** Hosting ของ `https://fretline-signature-review.vocalwolf36.chatgpt.site` ยังเป็น Site version 3 จำกัดเฉพาะเจ้าของ และมี Environment Variables 0 รายการ revision 0 การตรวจ `npm run deploy:check` จึงหยุดเพราะขาด public Supabase configuration

ค่าที่จำเป็นใน build/hosting: `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_CATALOG_SOURCE=supabase` และ `VITE_SITE_URL` เป็นโดเมนจริงสำหรับหน้า QR ไม่ต้องใช้ Secret Key หรือ Service Role ใน frontend

บน iPad:

1. เปิด [Admin เดิม](https://fretline-signature-review.vocalwolf36.chatgpt.site/admin) ด้วยบัญชีเจ้าของ ถ้ามีการเชื่อมต่อเดิมบน Safari แล้วใช้การเชื่อมต่อเดิม
2. หากยังไม่มี ให้นำเฉพาะ Project URL และ Publishable key จาก **โปรเจกต์ Fretline เดิม** ไปใส่ในฟอร์มการเชื่อมต่อ ไม่พิมพ์คีย์ลงแชท
3. กด **บันทึกการเชื่อมต่อบนเครื่องนี้** แล้วเปิด **ตั้งค่า Supabase และเปิดใช้บนเว็บไซต์**
4. เลื่อนไป **เปิดข้อมูล Published ให้ทุกคน** แล้วกด **ดาวน์โหลดการตั้งค่าเว็บไซต์**
5. แนบเฉพาะไฟล์ public configuration ที่ปุ่มนี้สร้าง ไม่แนบไฟล์ credentials/.env อื่น รหัสผ่าน Secret/Service Role หรือ Access Token

ยังไม่ต้องรัน SQL หรือสร้างฐานข้อมูลใหม่ เมื่อมีการตั้งค่าต้องตรวจ Published catalog และ gallery references จริงก่อนเผยแพร่ โดยรักษาข้อมูลเดิม การบันทึกการเชื่อมต่อบน Safari อย่างเดียวไม่เปลี่ยน static build สำหรับผู้เข้าชมอื่น

ไม่ได้อ้างว่า Login, RLS, Storage หรือ Published Supabase ผ่านแล้ว เพราะยังเชื่อมจาก execution workspace นี้ไม่ได้ ไม่ข้าม deployment guard ด้วยการเปลี่ยน Data Source ไม่มีการแก้ฐานข้อมูลหรือ Storage ระหว่างงานนี้

นอกจากการตั้งค่า Hosting งานท่ามืออีก 35 คอร์ดและการรับรองกายวิภาคยังเหลืออยู่ จึงยังไม่ใช่ระบบมือสอนคอร์ดที่ถูกต้องครบ 42 คอร์ด

## จุดย้อนกลับ

Git tag `backup/fretline-before-hand-restore-cb6d819` ชี้ source เวอร์ชันล่าสุดก่อนงานนี้ ไม่ reset หรือเขียนทับ working tree

เปิด checkpoint แยกเพื่อตรวจได้ด้วย:

```sh
git worktree add --detach ../fretline-before-hand-restore backup/fretline-before-hand-restore-cb6d819
```

การย้อน UI นี้ไม่ต้องย้อนฐานข้อมูล ราคา สเปก ภาพสินค้า หรือ Storage และ Hosting เวอร์ชันเดิมยังไม่ได้ถูกแทนที่
