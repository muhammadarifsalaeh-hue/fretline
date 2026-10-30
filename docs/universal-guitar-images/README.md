# Fretline — ระบบภาพสินค้ามาตรฐาน 1:1

งานอยู่บน `feature/universal-guitar-images` ต่อจาก `a350919285fb098d7e870948b503bcad215f9bc4` ไม่เปลี่ยนภาพต้นฉบับ ไม่เพิ่มภาพสินค้า และไม่เขียนฐานข้อมูล

## สิ่งที่ปรับ

- ใช้ `ProductImage` ร่วมกัน: กรอบจัตุรัส พื้นดำ `#000000` ภาพอยู่กลาง ใช้ `contain` ไม่มี padding หรือการซูมตายตัว ภาพไม่ล้นกรอบ และจำกัดการขยายตามขนาดต้นฉบับที่มี metadata
- ครอบคลุม Catalog, ผลค้นหา, รายการสินค้าในหน้าแบรนด์, Favorites, Compare, ผล Find My Guitar, Detail, Thumbnail และ Lightbox รวมถึงภาพสินค้าย่อยในเมนูและหน้าเครดิตภาพ
- ภาพที่ไม่มีหรือโหลดไม่สำเร็จใช้กรอบดำขนาดเท่ากัน ไม่ใส่ภาพรุ่นอื่น ไม่มีไอคอนภาพเสียหรือภาพกีตาร์ที่แต่งขึ้น
- คง gallery, ลำดับภาพ, เครดิต, ลิงก์ต้นทาง และรูปปกเดิมทั้งหมด เปลี่ยนภาพด้วย Thumbnail, ปุ่ม, คีย์บอร์ด และ Lightbox ได้ตามเดิม ยกเลิกการซูมอัตโนมัติเมื่อเลื่อนเมาส์เพื่อรักษาภาพครบทั้งตัว
- Catalog ให้ความสำคัญกับ 3 ภาพแรก ภาพที่เหลือใช้ native lazy loading ใช้ `srcSet` ที่มีอยู่และ `sizes` ตามหน้า มีกรอบจองพื้นที่ก่อนภาพโหลด ไม่แสดงภาพเต็ม 200 ไฟล์พร้อมกัน
- Admin ตรวจ JPG/PNG/WebP และขนาดจริง แนะนำ 1200 × 1200 px แสดงตัวอย่างจากไฟล์ที่เตรียมแล้ว **ก่อนติดต่อ Storage**
- ภาพไม่จัตุรัสต้องเลือก “จัดลงกรอบดำโดยไม่ตัดภาพ” หรือเลือกภาพใหม่ ระบบไม่ตัด ไม่ยืด ไม่ขยายภาพเล็ก เตรียมสำเนาใหม่ขนาดไม่เกิน 1200 px เป็น WebP หรือ PNG ตามความสามารถเบราว์เซอร์
- คงการยืนยันสิทธิ์ใช้ภาพและความตรงรุ่น อัปโหลดโดยผูก Guitar ID ที่เปิดอยู่ ใช้ชื่อ UUID และ `upsert: false` พร้อม cache 86400 วินาที การเปลี่ยนภาพได้ URL ใหม่จึงไม่ติด cache ของไฟล์เก่า
- เก็บรายการภาพรอตรวจเมื่อเปลี่ยนแท็บ ป้องกันบันทึก/เผยแพร่โดยลืมอัปโหลด ถ้าอัปโหลดได้บางไฟล์ ให้ลองซ้ำเฉพาะไฟล์ที่เหลือ ไม่เพิ่มไฟล์ที่สำเร็จแล้วซ้ำ
- คง Save Draft / Publish เดิม ภาพที่เพิ่มยังไม่เปลี่ยนหน้าผู้ชมจนเผยแพร่ ไม่แก้ราคา สเปก หรือรายละเอียดจากงานภาพนี้

## หลักฐานข้อมูลและจุดย้อนกลับ

จุดย้อนกลับผ่าน Git: `backup/fretline-before-universal-images-a350919` → `a350919285fb098d7e870948b503bcad215f9bc4` สร้างก่อนเริ่มแก้จาก working tree ที่สะอาด

- [Baseline](baseline.json): checksum ของข้อมูลกีตาร์เต็มรายการ รายการที่บันทึก แบรนด์ และคอร์ด รวมความสัมพันธ์ gallery
- [ผลตรวจข้อมูล](tests/data-safety.json): **200 IDs ไม่ซ้ำ, 10 แบรนด์ แบรนด์ละ 20 รุ่น, 42 คอร์ด** checksum ข้อมูลตรงฐานเดิมทุกค่า ตรวจ protected files 203 ไฟล์แบบ byte comparison
- [รายการไฟล์เดิม](tests/file-inventory.json): ตรวจไฟล์เดิม 4,955 ไฟล์ ไม่มีไฟล์ถูกลบ มีเพียง 20 ไฟล์แสดงผล/อัปโหลดที่แก้ตามขอบเขต
- มีภาพลงทะเบียนอยู่จริง **20 รุ่น** อีก **180 รุ่นใช้ placeholder** ตามข้อมูลเดิม ระบบพร้อมรับภาพรุ่นเหล่านี้ภายหลัง ไม่ได้อ้างว่ามีรูปใหม่ครบ 200 รุ่น
- ไม่เปลี่ยน `src/data`, `src/assets`, `public`, Supabase schema/RLS/SQL/seed, Auth/config, Homepage, Hero, Brand Marquee, การคำนวณ Compare/Quiz หรือข้อมูลและการทำงาน 3D Trainer

## วิธีใช้งานจาก iPad เมื่อ Supabase เชื่อมพร้อมแล้ว

1. เข้า `/admin` แล้วล็อกอินด้วยบัญชีผู้ดูแลเดิม เลือกรุ่น ตรวจชื่อและ ID ให้ตรง
2. เปิดแท็บ **รูปภาพ** ยืนยันว่ามีสิทธิ์ใช้ภาพและภาพตรงรุ่น
3. กด **เลือกภาพจาก Photos หรือ Files** เลือก JPG, PNG หรือ WebP แนะนำภาพจัตุรัส 1200 × 1200 px ให้ตัวกีตาร์สูงประมาณ 85–90% ของภาพ
4. ตรวจภาพตัวอย่าง ถ้าสัดส่วนไม่ตรง กด **จัดลงกรอบดำโดยไม่ตัดภาพ** หรือ **นำออกจากรายการอัปโหลด** แล้วเลือกไฟล์ใหม่ ไม่มีการครอปอัตโนมัติ
5. กด **อัปโหลด … ภาพที่ตรวจแล้ว** จัดลำดับ/ตั้งรูปปก จากนั้น **บันทึกแบบร่าง** หรือ **เผยแพร่** ตามต้องการ
6. เปิดหน้ารุ่นนั้นและ Catalog แล้ว Refresh เพื่อตรวจภาพที่เผยแพร่ การบันทึกร่างเพียงอย่างเดียวไม่ควรเปลี่ยนภาพหน้าผู้ชม

ขนาด 85–90% เป็นคำแนะนำการจัดภาพต้นฉบับ ระบบไม่เดาขอบตัวกีตาร์ ไม่ขยายเพื่อตัดพื้นที่ว่างของไฟล์เดิม และไม่แก้ไขไฟล์ต้นฉบับใน Storage

## การทดสอบ

ผลรอบสุดท้ายอยู่ใน [รายงานสรุปแบบ JSON](tests/final-summary.json) พร้อมขอบเขตและข้อจำกัด

| การตรวจ | หลักฐาน |
| --- | --- |
| Production build | [build.txt](tests/build.txt) |
| Unit checks เดิม 106 ข้อ และ image codec/planning ใหม่ 8 ข้อ | [core-results.json](tests/core-results.json) |
| Catalog และทะเบียนภาพ | [catalog-check.txt](tests/catalog-check.txt), [images-check.txt](tests/images-check.txt) |
| Public routes และระบบเดิม 98 กลุ่มบน 4 viewport | [browser-results.json](browser-results.json) |
| ภาพ 4 ประเภท, 3 formats, Upload/Draft/Publish 8 กลุ่ม | [admin-upload-browser.json](tests/admin-upload-browser.json) |
| ขนาดภาพจริง, การไม่ล้นกรอบ, Lightbox, lazy loading และภาพเสีย 15 กลุ่ม | [final-image-browser.json](tests/final-image-browser.json) |
| Production configuration guard | [deploy-readiness.txt](tests/deploy-readiness.txt) |

Viewport: Desktop 1440 × 1000, iPad แนวนอน 1194 × 834, iPad แนวตั้ง 768 × 1024 และ Mobile 390 × 844 ใช้ Chromium กับ touch emulation ใน viewport ที่เกี่ยวข้อง **ยังไม่ได้ทดสอบ Safari บน iPad จริงหรือ WebKit**

การทดสอบ Admin ใช้คอมโพเนนต์จริง, การอ่าน/บีบอัดไฟล์จริง, ตัวอย่างภาพจริงในโปรเจกต์ และ public resolver จริง แต่ Storage/RPC เป็น **บริการจำลองในหน่วยความจำ** ใช้ ID ทดสอบแยก ไม่เขียนสินค้าเดิม ไม่ได้ยืนยัน Auth/RLS หรือ Supabase จริง Test harness อยู่ใน docs และไม่ได้รวมใน production bundle

ระหว่าง QA พบและแก้ inherited background ของ Compare, กรอบใน flex card ที่หด และ img ที่สูงเกินกรอบเมื่อรับภาพแนวตั้ง จึงเพิ่มเงื่อนไขตรวจขนาดขั้นต่ำและตรวจ bounds ของ img ภายในกรอบ แล้วรันทดสอบบน build ที่แก้ครบอีกครั้ง เก็บผลก่อนแก้ใน `tests/*before*fix.json` เพื่อแยกจากผลรอบสุดท้าย

การทดสอบภาพเสียเป็นการจงใจขัดขวาง request ของภาพเพียงรายการเดียวใน browser context แยก เพื่อพิสูจน์ fallback และขนาดกรอบที่ไม่เปลี่ยน ไม่ใช่ภาพเสียที่พบระหว่าง regression ปกติ

Build ยังมีคำเตือน chunk ของ Three.js ประมาณ 709 kB ที่มีอยู่เดิม งานนี้ไม่เพิ่ม dependency หรือแก้ระบบ 3D ไม่ได้อ้างผล Core Web Vitals จากสภาพแวดล้อมจริง

## ภาพก่อน–หลังจากเบราว์เซอร์

ก่อน: source `a350919` ที่ยังไม่แก้ระบบภาพ หลัง: build จาก branch งานนี้ ภาพไม่ได้ถูกแต่งหรือสร้างใหม่ รูป Catalog เป็น element screenshot ของ grid ทั้งหน้า ซึ่งอาจมีแถบนำทางแบบ sticky พาดผ่านขณะ capture

| หน้าจอ | Catalog ก่อน / หลัง | Detail ก่อน / หลัง |
| --- | --- | --- |
| Desktop | [ก่อน](screenshots/before-desktop-catalog.png) · [หลัง](screenshots/after-desktop-catalog.png) | [ก่อน](screenshots/before-desktop-detail.png) · [หลัง](screenshots/after-desktop-detail.png) |
| iPad แนวนอน | [ก่อน](screenshots/before-landscape-catalog.png) · [หลัง](screenshots/after-landscape-catalog.png) | [ก่อน](screenshots/before-landscape-detail.png) · [หลัง](screenshots/after-landscape-detail.png) |
| iPad แนวตั้ง | [ก่อน](screenshots/before-portrait-catalog.png) · [หลัง](screenshots/after-portrait-catalog.png) | [ก่อน](screenshots/before-portrait-detail.png) · [หลัง](screenshots/after-portrait-detail.png) |
| Mobile | [ก่อน](screenshots/before-mobile-catalog.png) · [หลัง](screenshots/after-mobile-catalog.png) | [ก่อน](screenshots/before-mobile-detail.png) · [หลัง](screenshots/after-mobile-detail.png) |

ตัวอย่างการ์ดเดี่ยวหลังแก้: [Desktop](screenshots/after-desktop-first-card.png), [iPad แนวนอน](screenshots/after-landscape-first-card.png), [iPad แนวตั้ง](screenshots/after-portrait-first-card.png), [Mobile](screenshots/after-mobile-first-card.png)

ตัวอย่าง Admin: [แนวนอน](screenshots/admin-preview-landscape.png), [แนวตั้ง](screenshots/admin-preview-portrait.png), [Mobile](screenshots/admin-preview-mobile.png)

## ไฟล์โค้ดที่เปลี่ยน

ไฟล์ใหม่:

- `src/components/guitar/ProductImage.jsx`
- `src/styles/product-images.css`
- `src/features/admin/AdminImageUpload.jsx`

ไฟล์เดิมที่ปรับ:

- `src/components/ui/SmartImage.jsx`
- `src/components/guitar/GuitarImage.jsx`, `DevelopmentImagePreview.jsx`, `ImagePlaceholder.jsx`, `GuitarCard.jsx`
- `src/components/catalog/CatalogCard.jsx`
- `src/components/compare/CompareTable.jsx`, `ComparisonSlots.jsx`, `GuitarPicker.jsx`
- `src/components/detail/GuitarGallery.jsx`, `ImageLightbox.jsx`
- `src/components/wishlist/WishlistRow.jsx`
- `src/components/quiz/MatchCard.jsx`
- `src/components/layout/MegaMenu.jsx`
- `src/pages/ImageCreditsPage.jsx`
- `src/features/admin/AdminEditor.jsx`, `images.js`
- `src/styles/admin-studio.css`
- `src/i18n/th.js`, `en.js` เฉพาะคำอธิบาย placeholder

เพิ่ม QA ใน `scripts/check-universal-images.mjs`, `scripts/test-product-images.mjs` และโฟลเดอร์รายงานนี้ ไม่มีการเพิ่ม npm dependencies

## สถานะเผยแพร่และสิ่งที่ยังต้องทำ

**ยังไม่ Merge master และยังไม่ Deploy ระบบภาพนี้** เพราะ production guard ตรวจพบว่ายังไม่มี public configuration ของ Supabase ใน build workspace และ Hosting ตรวจจาก Sites API ล่าสุดพบ Environment Variables 0 รายการ revision 0

เว็บเดิม `https://fretline-signature-review.vocalwolf36.chatgpt.site` ยังเป็น Site version 3 และจำกัดเฉพาะเจ้าของ ไม่ใช่การเผยแพร่ระบบภาพใหม่นี้ ผู้ใช้อนุญาตเผยแพร่แล้ว แต่ต้องผ่านการเชื่อมต่อและตรวจ Published data จริงก่อน ไม่เปลี่ยนไปใช้ static data เพื่อข้าม guard

สิ่งที่เจ้าของต้องทำบน iPad: จากโปรเจกต์ Supabase **เดิม** นำ Project URL และ **Publishable key** ไปตั้งในหน้า `/admin` ของเว็บเดิม จากนั้นเปิด **ตั้งค่า Supabase และเปิดใช้บนเว็บไซต์ → เปิดข้อมูล Published ให้ทุกคน → ดาวน์โหลดการตั้งค่าเว็บไซต์** แนบเฉพาะไฟล์ตั้งค่าสาธารณะที่ปุ่มนี้สร้าง ไม่ส่ง Secret/Service Role key, รหัสผ่าน หรือ Access Token และไม่ Commit `.env.local`

เมื่อมี public config ต้องตรวจ Auth, สิทธิ์ Admin/Storage, การอัปโหลด/บันทึก/Publish จริง และข้อมูล Published ของ 200 รุ่น รวม gallery ของ Yamaha ก่อนเผยแพร่ ห้ามรัน setup/seed/migration เพื่อทดแทนการตรวจนี้ และห้ามเขียนทับ Published/Draft เดิมด้วย null หรือ snapshot เก่า

## วิธีย้อนกลับ

งานนี้ไม่เปลี่ยนฐานข้อมูลหรือไฟล์ภาพต้นฉบับ การย้อน frontend จึงไม่ต้องลบ/ย้อนข้อมูลสินค้า

หากต้องการเปิดโค้ดก่อนงานนี้เพื่อตรวจ ให้สร้าง worktree แยกจาก tag สำรอง ไม่ reset working tree ปัจจุบัน:

```sh
git worktree add --detach ../fretline-before-image-system backup/fretline-before-universal-images-a350919
```

หากเผยแพร่ในอนาคตแล้วต้องย้อน ให้ build source จาก checkpoint นี้ด้วย public configuration ของโปรเจกต์เดิมและใช้กระบวนการ Hosting เดิม ห้ามรัน SQL หรือแก้ Storage เพื่อย้อนดีไซน์ เวอร์ชัน Hosting ปัจจุบันยังไม่ได้ถูกแทนที่ในงานนี้
