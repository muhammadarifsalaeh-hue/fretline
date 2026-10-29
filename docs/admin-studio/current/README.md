# Fretline Admin Studio — โค้ดระบบและการตั้งค่าครั้งแรก

พัฒนาต่อจาก `27f5209` บน `feature/fretline-admin-studio` ไม่ Merge เข้า `master`

## สถานะจริง

เตรียมฐานข้อมูลและโค้ด Admin แล้ว ทดสอบด้วย PostgreSQL 17 + PostgREST ในสภาพแวดล้อมทดสอบแยก **ยังไม่ได้เชื่อมต่อ รัน SQL หรือนำเข้าข้อมูลใน Supabase โปรเจกต์ของเจ้าของ** เพราะยังไม่มีค่าเชื่อมต่อใน Workspace นี้

การทดสอบ Browser ของ Admin ใช้ฐานข้อมูล/RPC/RLS จริงในเครื่องทดสอบ แต่ส่วน Supabase Auth และ Storage HTTP เป็น Contract Fixtures ไม่ใช่บริการ Supabase จริง ต้องทดสอบล็อกอิน อีเมล และอัปโหลดกับ Project ของเจ้าของอีกครั้งก่อนเปิดใช้จริง ไม่อ้างว่าผ่านบน iPad เครื่องจริง

## ส่วนที่พัฒนาแล้ว

- `/admin`: ตั้งค่าการเชื่อมต่อบนเครื่อง ล็อกอิน/ออกจากระบบ และโฟลว์ขอเปลี่ยนรหัสผ่านด้วย Supabase Auth ไม่มีบัญชีหรือรหัสผ่านเริ่มต้น ไม่มีฟอร์มสมัครผู้ดูแลเอง
- Dashboard: จำนวนรุ่น แบรนด์ รูป ราคา สเปกหลักที่ครบ/ขาด Draft/Published ค้นหา กรอง และแบ่งหน้า
- เพิ่ม/แก้รุ่นผ่าน ID เดิม บันทึก Draft, Publish, ซ่อนโดยไม่ลบสินค้า ป้องกัน ID ซ้ำ และป้องกันการเขียนทับจากคนละหน้าจอด้วย Revision
- แก้คำอธิบายไทย/อังกฤษ สเปก General/Materials/Neck/Hardware/Additional และหลักฐานอ้างอิง ค่าที่ไม่ทราบคงเป็น `null`
- อัปโหลด JPG/PNG/WebP หลายรูป ย่อด้านยาวไม่เกิน 1800 px กำหนดรูปปกและลำดับด้วยปุ่มที่กดบน iPad ได้ นำออกจากร่างก่อน Publish ลบไฟล์ที่ไม่อ้างอิงแล้วโดยยืนยันก่อน
- รูปเดิมเก็บเป็น Legacy References ไปยัง Asset เดิม ไม่คัดลอกรูปผิดรุ่นหรือทำให้ URL ที่ Build สร้างขึ้นฝังตายตัวในฐานข้อมูล ไม่ลบ Asset เดิม
- ราคา THB มากกว่า 0 พร้อม URL/วันที่ แยกราคาแนะนำผู้ผลิตกับราคาหน้าร้าน เก็บประวัติเมื่อเปลี่ยนราคา ไม่มีราคาแสดง “สอบถามราคา”
- Audit Logs ระบุผู้แก้ไขและข้อมูลก่อน/หลัง เขียนผ่าน RPC เท่านั้น ผู้ดูแลบน Browser แก้/ลบประวัติหรือข้อมูลสินค้าอย่างถาวรไม่ได้
- Published snapshot อ่านเข้าข้อมูลชุดเดียวก่อนเริ่มแอป ทำให้ Catalog, Brand counts, Search, Detail, Compare, Quiz และรายการโปรดอ้างอิง ID ชุดเดียวกัน Refresh แล้วรับข้อมูลใหม่ ไม่ต้องเปลี่ยนดีไซน์เดิม
- ไม่เปลี่ยน Home, ภาพสินค้า, Brand directory, Quiz scoring, Compare layout หรือข้อมูล/โมเดล Practice 42 คอร์ด

## สิ่งที่ต้องกดบน iPad

### 1. เปิดหน้า Admin รุ่นล่าสุด

Codespaces ต้องใช้ Branch `feature/fretline-admin-studio` ที่อัปเดตแล้ว เปิด Preview เดิมของ Port 5173 แล้วเติม `/admin` หลังโดเมน ไม่มี URL Codespaces เต็มที่ตรวจสอบได้ในสภาพแวดล้อมนี้ จึงไม่สร้างลิงก์ Preview ขึ้นเอง

หน้า Admin จะมี **เชื่อมต่อโปรเจกต์ Fretline**:

1. ใน Supabase เลือก Project `Fretline`
2. **Project Settings → Data API** คัดลอก **Project URL** ไปกรอกช่อง Project URL ใน `/admin`
3. **Project Settings → API Keys** คัดลอก **Publishable key** ที่ขึ้นต้น `sb_publishable_` ไปกรอกช่อง Publishable key ใน `/admin`
4. กด **บันทึกการเชื่อมต่อบนเครื่องนี้** ไม่มีการส่งค่าเหล่านี้ผ่านแชท และคีย์นี้เป็นคีย์สำหรับ Frontend ไม่ใช่สิทธิ์แอดมิน

ห้ามใช้ Database password, JWT secret, Access token, Service Role หรือ `sb_secret_` ในฟอร์มนี้ หน้า Admin จะปฏิเสธคีย์ที่ไม่ใช่ Publishable key

ชื่อเมนู Supabase อาจต่างเล็กน้อย ให้ใช้ **Connect** ที่หน้า Project เป็นอีกทางเพื่อดู Project URL และ Publishable key ถ้าเมนูซ้ายซ่อนบน iPad ให้กดปุ่มเมนูซ้ายบนหรือ Safari → Request Desktop Website

### 2. รัน SQL ครั้งเดียว

1. ใน `/admin` เปิด **ตั้งค่า Supabase และเปิดใช้บนเว็บไซต์**
2. กด **คัดลอก SQL ตั้งค่าทั้งหมด** แล้ว **เปิด SQL Editor** ซึ่งชี้ตรงไปยัง Project ที่กรอกไว้
3. ใน Supabase **SQL Editor → New query** วาง SQL แล้วกด **Run** หากมีหน้าต่างยืนยันการเปลี่ยนนโยบายสิทธิ์ ให้ตรวจว่ากำลังอยู่ Project Fretline ก่อนยืนยัน
4. ผลท้ายควรเป็น `total_guitars = 200` และ `brands = 10` สำหรับ Project ว่างที่เพิ่งสร้าง

SQL ประกอบด้วย Migration และ Seed รวมกัน ดาวน์โหลดได้จากปุ่ม **ดาวน์โหลด SQL** เช่นกัน หาก Safari ไม่อนุญาต Clipboard

รันซ้ำได้: สินค้าใช้ `ON CONFLICT(id) DO NOTHING` ไม่เขียนทับ Draft/Published ที่เจ้าของแก้แล้ว และไม่เขียน `null` ทับข้อมูลเดิม ไม่ต้องปิด RLS หรือเปิด Bucket เป็น Public

### 3. สร้างบัญชีเจ้าของ

1. Supabase **Authentication → Users → Add user → Create new user**
2. กรอกอีเมลของคุณ ตั้งรหัสผ่านที่เดายากอย่างน้อย 12 ตัวใน Supabase โดยตรง และเปิด **Auto Confirm User** สำหรับบัญชีเจ้าของที่สร้างเอง
3. กลับ `/admin` ในส่วนตั้งค่า กรอกอีเมลเดียวกันแล้วกด **คัดลอก SQL กำหนดสิทธิ์**
4. กลับ **SQL Editor → New query → วาง → Run** ต้องได้ `admin_accounts` อย่างน้อย 1 สำหรับการตั้งค่าครั้งแรก
5. กลับ `/admin` ล็อกอินด้วยอีเมลและรหัสผ่านที่คุณตั้งเอง ไม่ต้องส่งรหัสผ่านในแชท

บัญชี Supabase Dashboard กับบัญชีผู้ใช้ใน **Authentication → Users** เป็นคนละส่วน ต้องทำขั้นตอนสร้างผู้ใช้ของเว็บไซต์ด้วย

### 4. จำกัดการสมัครและตั้งค่ารหัสผ่าน

- **Authentication → Sign In / Providers → Allow new users to sign up** ปิด แล้ว **Save**
- **Authentication → URL Configuration → Site URL** ใส่โดเมนเว็บไซต์
- **Redirect URLs → Add URL** เพิ่ม URL เต็มของ `/admin?recovery=1` แล้ว **Save changes** เพื่อให้ปุ่มลืมรหัสผ่านทำงาน เปิดลิงก์ใน Safari เครื่องเดียวกับที่กดขอรหัสผ่านเพราะใช้ PKCE

### 5. ทดลองแก้ข้อมูล

เลือกสินค้า → **แก้ไข** → เปลี่ยนราคา/สเปก → **บันทึก Draft** ข้อมูลบนเว็บไซต์ยังไม่เปลี่ยน จากนั้นกด **Publish** และ **ดูหน้า Published ↗** หรือ **ดูข้อมูล Published** แล้ว Refresh

ภาพ: บันทึก Draft ครั้งแรก → แท็บ **รูปภาพ** → ยืนยันสิทธิ์ภาพและรุ่น → เลือก Photos/Files ได้หลายรูป → ตั้งรูปปก/ย้ายลำดับ → บันทึก Draft/Publish ภาพใน Storage ยังเป็น Private จนถูกอ้างอิงใน Published ภาพเดิมที่นำออกจาก Draft ยังไม่ถูกลบทันที

รองรับไฟล์ละไม่เกิน 25 MB ก่อนย่อ และไม่เกิน 8 MB หลังย่อ Bucket จำกัด MIME เป็น JPEG/PNG/WebP สูงสุด 30 รูปต่อรุ่น ไฟล์ HEIC ต้องแปลง/Export เป็น JPEG/PNG/WebP ก่อน

### 6. เปิดใช้กับผู้เข้าชมทุกคน

การกรอกค่าเชื่อมต่อใน Safari เก็บเฉพาะ Public Config บนเครื่องนั้น ปุ่ม **ดูข้อมูล Published** เป็นโหมดทดสอบบนเครื่อง และจำในแท็บนั้นเพื่อไม่ให้โหมดหลุดเมื่อกรอง/Refresh ไม่ใช่การ Deploy เว็บสาธารณะแล้ว

เมื่อทดสอบ Project จริงครบแล้ว ตั้งค่าระบบ Hosting หรือ `.env.local` ใน Codespaces:

```dotenv
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=sb_publishable_your_public_key
VITE_CATALOG_SOURCE=supabase
```

มีปุ่ม **ดาวน์โหลดการตั้งค่าเว็บไซต์** เตรียมไฟล์ให้ ไม่รวม Password/Secret ต้อง Restart Vite หลังเปลี่ยน Environment และต้อง Build/Deploy ใหม่สำหรับเว็บ Production ไม่มีการ Deploy หรือ Merge อัตโนมัติในรอบนี้

## ฐานข้อมูลและสิทธิ์

ไฟล์หลัก: [Migration](../../../supabase/migrations/202610290001_admin_studio.sql), [Seed](../../../supabase/seed.sql), [SQL รวม](../../../supabase/setup.sql)

ตาราง `brands`, `guitars`, `guitar_specifications`, `guitar_images`, `guitar_prices`, `admin_users`, `audit_logs`, `catalog_state` เปิด RLS ทั้งหมด

ข้อมูลที่แก้อยู่ใน `guitars.draft`; สำเนา `guitars.published` เปลี่ยนเฉพาะ Publish พร้อมสถานะและ Revision ใน Transaction ตาราง Specs เป็นรายละเอียด Draft และตาราง Prices เก็บประวัติ Draft แบบเพิ่มแถว การอ่านสาธารณะผ่าน `get_published_catalog()` คืนเฉพาะ Published ไม่มี Endpoint อ่าน Draft สำหรับผู้เยี่ยมชม

ผู้ดูแลบน Browser ไม่มีสิทธิ์เขียนตารางโดยตรง ใช้ RPC ที่ตรวจสิทธิ์ `admin_users.active` จาก `auth.uid()` เท่านั้น ไม่มีวิธีให้ผู้ใช้ทั่วไปเพิ่มตัวเองเป็นแอดมิน ต้องกำหนดผ่านเจ้าของ Project ใน SQL Editor

Bucket `guitar-images` เป็น Private ไม่อนุญาต Update/เขียนทับไฟล์เดิม ใช้ชื่อไฟล์ UUID ใหม่เสมอ Signed URLs ของภาพ Published มีอายุ 24 ชั่วโมง ลิงก์ที่ออกไปแล้วอาจยังใช้ได้จนหมดอายุแม้ซ่อนสินค้า แต่การขอลิงก์ใหม่ของภาพที่ซ่อนจะถูกปฏิเสธ

ลบไฟล์ได้เมื่อไม่มีการอ้างอิงทั้ง Draft/Published โดยยกเลิก Registry ภายใต้ Product Lock ก่อนลบ Storage เพื่อป้องกันการ Publish ไฟล์ที่กำลังลบ กรณี Storage ลบไม่สำเร็จ ยังลองลบซ้ำได้

## Import และข้อมูลที่ยังขาด

เตรียม Seed ได้ **200 รุ่น / 10 แบรนด์ × 20** ทุก ID เดิม ราคาที่มีหลักฐาน 27 รุ่น, ไม่มีราคายืนยัน 173 รุ่น, มี Gallery เดิม 3 รุ่น, อีก 197 รุ่นคง Placeholder และไม่มีรุ่นที่ครบทุกช่องสเปกที่เคยร้องขอ

นำเข้าจริงในฐานข้อมูลทดสอบแยกได้ 200 รุ่น และยืนยันรันซ้ำหลังแก้ข้อมูลแล้วไม่ทำให้ข้อมูลหาย **จำนวนที่นำเข้าใน Supabase ของเจ้าของยังยืนยันไม่ได้** จนกว่าจะรัน SQL และตรวจ Project นั้น

ตัวนับสเปกใน Dashboard หมายถึงสเปกหลักที่เหมาะกับประเภท ได้แก่ Body Shape/Strings/Body/Neck/Fretboard/Frets/Bridge/Scale และ Top/Back/Sides สำหรับ Acoustic/Classical หรือ Pickups/Electronics สำหรับ Electric/Bass ไม่ได้อ้างว่าตรวจยืนยัน Optional ทุกช่องหรือเปลี่ยน `dataStatus` เป็น Fully Verified

## Deploy และ Rollback

1. ก่อนเปิดจริง สำรองฐานข้อมูลและไฟล์ Storage ของ Project ตามแผน Supabase ที่ใช้ ทดสอบกับ Project แยกถ้ามีข้อมูลอื่นอยู่แล้ว
2. เปิด `VITE_CATALOG_SOURCE=supabase` หลังตรวจ Auth/RLS/Storage/Import กับ Project จริงผ่านแล้วเท่านั้น ไม่มี Service Role Key ใน Frontend
3. หากต้องหยุด Backend ชั่วคราว ให้ปิดเว็บสาธารณะหรือแสดง Maintenance แล้วเปลี่ยนกลับ `VITE_CATALOG_SOURCE=static` และ Build/Deploy เวอร์ชันก่อนหน้า ข้อมูลเดิมใน Git ยังอยู่ครบ
4. Static Rollback จะแสดงรายการเดิมจาก Git รวมสินค้าที่อาจเพิ่งถูกซ่อนใน Supabase ต้องตรวจสถานะก่อนเปิดสาธารณะอีกครั้ง ห้ามใช้ Static Fallback อัตโนมัติเมื่อ API ล้มเหลว
5. อย่า Drop ตารางหรือ Bucket เพื่อ Rollback UI เก็บฐานข้อมูล ราคา ประวัติ และภาพไว้ หากต้องย้อน Draft ที่ยังไม่ Publish ใช้แท็บ **ประวัติ → คืนร่างจาก Published ล่าสุด** แล้วบันทึก

เมื่อเปิด Remote แล้ว API ใช้งานไม่ได้ หน้าเว็บแสดงข้อผิดพลาดและปุ่มลองใหม่ ไม่แสดงข้อมูลเก่าจาก Static โดยเงียบ ๆ

## การทดสอบ

- Build ผ่าน, Admin unit/data 9/9, PostgreSQL/RLS 37/37, Admin Browser/API 12/12 และเว็บไซต์เดิม 38/38 รวม Browser 50/50
- Catalog/Images/Practice/Quiz scoring/Price/Compare scripts ผ่านทั้งหมด Practice คง 42 คอร์ดและผ่าน 56 checks
- มีคำเตือนขนาด Chunk 3D เดิม แต่ไม่มี Build Error
- ตรวจไฟล์เดิมใน `src`/`public` ที่อยู่นอก 6 ไฟล์ที่ต้องแก้เพื่อเชื่อมระบบ รวม 277 ไฟล์ ไม่เปลี่ยนแม้แต่ไบต์เดียว
- [ผลรวมและขอบเขตที่ยังรอ](summary.json)
- [Core checks และ Build SHA-256](core-results.json)
- [หลักฐานการรักษาไฟล์เดิม](preservation.json)
- [Unit/data checks](unit-results.json)
- [PostgreSQL/RLS checks](database-security-results.json)
- [Admin Browser/API checks](browser-results.json)
- [Existing website browser regression](regression/browser-results.json)
- [Seed manifest: 200 stable IDs](seed-manifest.json)

Browser ใช้ Chromium และ WebKit บน Desktop 1440×1000, iPad Landscape 1194×834, iPad Portrait 768×1024, Mobile 390×844 การตรวจ API ของ Admin ใช้ PostgREST จริง ส่วน Auth/Storage HTTP จำลองสัญญา API อย่างเปิดเผย WebKit Multipart Interception ไม่ส่ง File Bytes ให้ Playwright จึงเก็บ Blob ที่ Browser ย่อจริงผ่าน Test Instrumentation ก่อนส่ง ไม่แก้ Uploader หรือแทนภาพปลอมในโค้ดเว็บ

สิ่งที่ยังต้องตรวจบน Supabase จริง: Auth/อีเมลรีเซ็ตรหัสผ่าน, Storage HTTP/Quota/RLS ของ Project จริง, Public Config บน Hosting, Production Deployment และ iPad Safari เครื่องจริง
