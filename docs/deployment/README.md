# Fretline — เตรียมเผยแพร่บน Vercel

ทำบน `feature/fretline-admin-studio` จาก `894522a` โดยไม่ Merge `master` ไม่เปลี่ยน Home รูปสินค้า ข้อมูล 200 รุ่น หรือระบบฝึก 42 คอร์ด

## สถานะที่ต้องรู้ก่อน

เตรียมโค้ด Deploy แล้ว แต่ **ยังไม่มีเว็บไซต์ Production หรือลิงก์ QR จริงที่ยืนยันได้** ใน Workspace ไม่มีค่าเชื่อมต่อ Supabase และไม่มีสิทธิ์ Vercel ของเจ้าของ ไม่ได้รัน `setup.sql` ไม่ได้สร้างบัญชี หรือแก้ฐานข้อมูลจริง การอนุมัติรัน SQL จากงานก่อนยังคงรออยู่

ข้อมูลเดิมในไฟล์ครบ 200 ID / 10 แบรนด์ แบรนด์ละ 20; มีราคาอ้างอิง 27 รุ่น และ 173 รุ่นแสดงสอบถามราคา ไม่มีราคา 0 บาท จำนวนบน Supabase จริงต้องตรวจหลังตั้งค่าฐานข้อมูลที่ได้รับอนุมัติแล้ว ไม่ใช้ผลทดสอบจำลองเป็นหลักฐานว่านำเข้าจริงสำเร็จ

## สิ่งที่เตรียมแล้ว

- เมนู **Admin Studio** ในแถบหลักและเมนูมือถือ แสดงเมื่อ `auth.getUser()` ยืนยันตัวตนจาก Supabase และ RPC `fretline_is_admin()` ตอบ `true` เท่านั้น ไม่ใช้ flag ในเครื่อง อีเมล หรือ cached session เป็นสิทธิ์แอดมิน เมื่อออกจากระบบ/ตรวจสิทธิ์ล้มเหลวเมนูจะหาย ตรวจใหม่เมื่อกลับเข้าแท็บ/ออนไลน์ และทุก 60 วินาทีที่เปิดหน้าอยู่
- เมนูเป็นเพียงการแสดง UI การเข้าถึงข้อมูลยังต้องผ่าน Supabase Auth, RLS และ RPC เดิม ผู้เยี่ยมชมเปิด `/admin` ได้เฉพาะหน้าล็อกอิน ไม่มีสิทธิ์แก้ข้อมูล
- `vercel.json`: Vite → `dist`, SPA deep links รวม `/admin`, `/qr`, `/guitars/:id`, `/brands/:id`, `/compare`, `/practice` และ Quiz พร้อมข้อกำหนด cache/security headers แยก asset ที่มี hash
- ข้อมูล Published จาก Supabase ถูกโหลดก่อนสร้างดัชนี Catalog/Brands/Search/Compare/Quiz จึงใช้ ID ชุดเดียวกัน Refresh เพื่อรับการ Publish ล่าสุด ไม่มีการนำข้อมูล static เก่ามาแสดงแทนอย่างเงียบ ๆ หากฐานข้อมูลขัดข้อง หน้า Admin และ QR ยังเข้าถึงได้ ส่วนหน้าสินค้าจะแจ้งให้ลองใหม่
- ใช้ AbortController สำหรับ timeout เพื่อไม่ผูกกับ `AbortSignal.timeout()` ที่ Safari บางรุ่นไม่มี
- `/qr` พร้อมลิงก์ Footer: สร้าง QR ใน Browser ไม่ส่ง URL ให้เว็บสร้าง QR ภายนอก ดาวน์โหลด PNG 1024 px มีพื้นที่ขาวรอบภาพ และคัดลอกลิงก์ได้
- QR อ่านเฉพาะ `VITE_SITE_URL` ที่เจ้าของกำหนด ไม่อ่าน `location.origin` ไม่ใช้ Codespaces, localhost หรือ URL ที่มีรหัสผ่าน/Query หากยังไม่ตั้งค่า ไม่มี QR หลอกแสดงขึ้นมา
- คำสั่ง Build สำหรับ Vercel ตรวจ Public Config และบังคับ `VITE_CATALOG_SOURCE=supabase`; ทั้ง Vite dev/build ปฏิเสธตัวแปร `VITE_` ที่มี Secret, Access Token, Service Role หรือ Password ที่ตรวจพบ ไม่พิมพ์ค่าลง log

## Environment Variables — กรอกใน Vercel เท่านั้น

Vercel Project → **Settings → Environment Variables → Add Environment Variable** เลือก Production และ Preview ของ branch นี้ตามที่ใช้ แล้ว Save

| Name | Value / ดูจากที่ไหน |
| --- | --- |
| `VITE_SUPABASE_URL` | Supabase Fretline → **Project Settings → Data API → Project URL** |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | **Project Settings → API Keys → Publishable key** ต้องขึ้นต้น `sb_publishable_` |
| `VITE_CATALOG_SOURCE` | `supabase` |
| `VITE_SITE_URL` | URL โดเมน Production แบบ `https://…` จาก Vercel **Settings → Domains** หลัง Deploy จริง ไม่ใส่ `/admin`, `/qr`, query หรือ hash |

สองค่า Supabase แรกเป็น Public Frontend Config ไม่ใช่สิทธิ์แอดมิน ระบบนี้ไม่รับ Legacy anon JWT แทน Publishable key

**ไม่ใส่** Service Role / `sb_secret_`, Supabase Personal Access Token / `sbp_`, Database password, connection string, JWT Secret หรือ Vercel Token ในตัวแปร `VITE_`, Git, ฟอร์มเว็บ หรือแชท ไม่ต้องส่งค่าทั้งหมดมาให้ Codex ค่าใน Vite ถูกฝังในไฟล์ JS ที่ผู้ชมอ่านได้ แม้ตั้งเป็น Sensitive ใน Vercel ก็ไม่ทำให้ `VITE_` เป็นความลับ

## ขั้นตอนเจ้าของกดเองบน iPad

### 1. เตรียม Supabase โดยไม่ข้ามขั้นอนุมัติเดิม

หากยังไม่ได้รัน SQL ให้ตรวจและยืนยันงานฐานข้อมูลแยกตาม [วิธีตรวจ/อนุมัติ setup](../admin-studio/database-setup-review.md) ก่อน คู่มือนั้นมีวิธีใช้ Codespaces Secrets และรันจากไฟล์โดยไม่ต้องวาง SQL ทั้งไฟล์บน iPad ห้ามถือว่าการเตรียม Deploy รอบนี้อนุมัติให้รัน SQL แล้ว

หลัง setup ที่อนุมัติสำเร็จ ต้องตรวจ 200 รุ่น / 10 แบรนด์, สร้างผู้ใช้เจ้าของใน **Authentication → Users → Add user → Create new user** และกำหนดสิทธิ์ `admin_users` ตาม [คู่มือบัญชีแอดมิน](../admin-studio/current/README.md#3-สร้างบัญชีเจ้าของ) บัญชี Supabase Dashboard ไม่ใช่บัญชีล็อกอินเว็บไซต์โดยอัตโนมัติ อย่าปิด RLS หรือเปิด Bucket เป็น Public เพื่อแก้สิทธิ์

### 2. Import GitHub ไป Vercel

1. เปิด [Vercel Dashboard](https://vercel.com/dashboard) → **Add New… → Project**
2. ใน **Import Git Repository** เชื่อม GitHub แล้วเลือก repo **fretline → Import** ให้สิทธิ์เฉพาะ repo ที่จำเป็น
3. Framework Preset **Vite**, Root Directory ราก repo (ตำแหน่ง `package.json`), Build Command **`npm run build:vercel`**, Output Directory **`dist`**, Install Command **`npm ci`** ใช้ Node.js **22.x** หรือรุ่น LTS ที่ Vercel รองรับ
4. เพิ่มสามค่า Supabase ด้านบนใน **Environment Variables** ตอนนี้เว้น `VITE_SITE_URL` ได้ หน้า QR จะยังไม่สร้างภาพจนได้โดเมนจริง
5. ต้อง Deploy จาก **`feature/fretline-admin-studio`** และตรวจ Source commit ก่อนส่งลิงก์ ถ้าหน้า Import เลือก Branch ได้ ให้เลือก branch นี้ หากเลือกไม่ได้ ให้สร้าง Project แล้วตั้งค่าขั้นต่อไปก่อนถือว่าเป็นเว็บรุ่นล่าสุด การ Build แรกจาก `master` อาจ Fail เพราะไม่มีคำสั่ง `build:vercel` ซึ่งต้องแก้ด้วยการเลือก branch ไม่ใช่ย้อนโค้ดหรือ Merge

### 3. ใช้ feature branch เป็น Production โดยไม่ Merge master

1. เปิด Project → **Settings → Environments → Production → Branch Tracking**
2. ใส่ **`feature/fretline-admin-studio` → Save** ไม่เปลี่ยน default branch ของ GitHub
3. เปิด **Deployments → Create Deployment** เลือก/กรอก branch นี้ แล้ว **Deploy** หาก UI มี **Create Deployment** ในเมนู `…` ให้ใช้ตำแหน่งนั้น หลังเปลี่ยน Branch Tracking การ Push ครั้งถัดไปบน branch นี้จะสร้าง Production Deployment อัตโนมัติ
4. ตรวจรายละเอียด Deployment: **Source** ต้องเป็น branch นี้และ commit ของงานล่าสุด สถานะ **Ready**, Environment **Production** ใช้โดเมนจาก **Settings → Domains** ไม่ใช้ URL ของ branch Preview
5. ใน **Settings → Deployment Protection** ตรวจว่าโดเมน Production เปิดให้ผู้ชมทั่วไปได้ โดยไม่ต้องล็อกอิน Vercel ทดสอบ Safari **Private Tab** ก่อนส่งอาจารย์ การเปิดเว็บสาธารณะไม่ได้ยกเลิก Supabase Auth/RLS ของ `/admin`

### 4. ตั้ง URL จริงและทำ QR

1. เปิดลิงก์ Production จาก **Domains** ตรวจว่าเป็น Fretline ล่าสุดและเปิดจาก Safari Private Tab ได้จริง
2. คัดลอกเฉพาะ origin `https://…` ไปตั้ง **Settings → Environment Variables → `VITE_SITE_URL`** เป็นโดเมนนั้น เลือก Production (และ Preview หากต้องการให้ Preview ชี้ QR ไป Production)
3. **Deployments → Deployment ล่าสุดของ branch → … → Redeploy** เพราะเปลี่ยน Env ต้อง Build ใหม่
4. ใน Supabase **Authentication → URL Configuration → Site URL** ใส่โดเมน Production และ **Redirect URLs → Add URL** เพิ่ม URL เต็ม `${โดเมนจริง}/admin?recovery=1` → **Save changes** อย่าใช้ wildcard ทุกโดเมน เปิดลิงก์กู้รหัสผ่านใน Safari เครื่องเดียวกับที่ขอเพราะใช้ PKCE
5. เปิด `${โดเมนจริง}/qr` → **ดาวน์โหลด QR Code** บน iPad หากไฟล์แสดงเป็นภาพ ให้แตะค้าง **Save to Photos** หรือ Share → **Save Image / Save to Files** สแกนด้วยกล้องอีกเครื่องแล้วตรวจว่าปลายทางเป็นโดเมน Production เดียวกัน
6. ส่งอาจารย์ได้ทั้ง URL หน้า Home, URL `/qr` และ PNG ที่ดาวน์โหลดจากเว็บจริง ไม่ใช้ภาพ QR จากโฟลเดอร์ Tests ซึ่งเป็นโดเมนจำลอง

### 5. ตรวจรับบนเว็บจริงก่อนแชร์

- ผู้ชมทั่วไปไม่เห็นเมนู Admin Studio เปิด `/admin` ได้หน้าล็อกอินเท่านั้น ผู้ใช้ที่ล็อกอินแต่ไม่มีสิทธิ์ก็ไม่เห็นเมนู
- ผู้ดูแลล็อกอินแล้วเห็นเมนูทั้งแนวนอน/แนวตั้ง ออกจากระบบเมนูหาย
- Catalog มี 200 รุ่น/10 แบรนด์ในชุดเริ่มต้น รูปเดิมไม่ถูกสลับ Search/Filter/Brand/Detail/Compare สูงสุด 4 รุ่น/Quiz/Practice ใช้งานได้
- ทดลองแก้หนึ่งรุ่นเป็น Draft แล้วเปิดอีกแท็บแบบไม่ล็อกอินต้องยังเป็น Published เดิม จากนั้น Publish/Refresh ต้องเห็นข้อมูลใหม่ คืนค่าที่ใช้ทดสอบให้ถูกต้อง
- หน้าต่าง iPad Landscape/Portrait, Mobile และ Desktop ไม่มีการเลื่อนแนวนอนของหน้า เมนู/ปุ่มไม่ทับกัน
- เปิด `/admin`, `/qr` และ Product Detail ตรงจาก URL แล้ว Refresh ไม่ได้ 404 สแกน PNG จากเว็บจริงสำเร็จ

## คำสั่งสำหรับผู้ดูแลโค้ด

```bash
npm ci
npm run build
node scripts/test-deployment.mjs
npm run admin:check
npm run catalog:check
npm run practice:check
```

ตรวจ Env ที่ถูกตั้งผ่านระบบ Environment ไว้แล้ว โดยไม่พิมพ์ Key ในคำสั่ง:

```bash
npm run deploy:check
# หลังฐานข้อมูลพร้อมและอนุญาตให้อ่านข้อมูล Public แล้วเท่านั้น:
npm run deploy:check-data
```

`deploy:check` ไม่ต่อ Network หรือรัน SQL; `deploy:check-data` เรียกเฉพาะ RPC อ่าน Published ด้วย Publishable key ไม่เรียก setup/import/admin RPC ไม่แก้ฐานข้อมูล ตรวจ 200 ID เดิม / 10×20 และรายงานจำนวนเท่านั้น มี `--initial` สำหรับชุดเริ่มต้น ถ้ามีการซ่อน/เพิ่มรุ่นภายหลัง ใช้ `node scripts/check-live-catalog.mjs` เพื่อรายงานโดยไม่บังคับจำนวนเริ่มต้น

`npm run build:vercel` หยุดถ้า Public Config ไม่ครบหรือยังเลือก static ทำหน้าที่ตรวจ Env และ Build เท่านั้น ไม่ได้พิสูจน์ว่า Auth/Storage/ข้อมูลใน Supabase จริงผ่านแล้ว ต้องตรวจรับจริงตามด้านบน

## Rollback

หาก Deployment ใหม่มีปัญหา: Vercel → **Deployments → Production Deployment ก่อนหน้าที่ตรวจแล้ว → … → Instant Rollback / Rollback** ตามเมนูที่บัญชีมี ไม่ต้อง Reset Git หรือ Merge master วิธีนี้คืนเฉพาะ Frontend ไม่ย้อนข้อมูลที่ Admin Publish ลง Supabase และไม่ใช่ Backup ฐานข้อมูล

ก่อนย้าย Schema หรือข้อมูลจริงให้ใช้แผนสำรองของ Supabase ที่ตกลงไว้แยก ไม่มี Migration/Import อัตโนมัติใน Build/Deploy งานรอบนี้

## หลักฐานทดสอบและข้อจำกัด

ดู [ผล Browser](tests/browser-results.json) และ [สรุปการส่งมอบ](tests/summary.json) ทดสอบ Chromium/WebKit บน viewport 1440×1000, 1194×834, 768×1024, 390×844 กับ Production Build ในเครื่องและตัวจำลองกฎ Routing ของ Vercel HTTP ของ Supabase เป็น Fixture ที่ชัดเจน ไม่มีฐานข้อมูลถูกเปลี่ยน ใช้ตัวอ่าน QR แยกถอดรหัส PNG ที่ Browser ดาวน์โหลดจริง

**ยังไม่ถือว่าทดสอบ Supabase/Vercel จริงหรือ iPad Safari เครื่องจริงแล้ว** จนเจ้าของตั้งค่าและเปิดเว็บจริง หลักฐานภาพชื่อ `fixture-qr` ไม่ใช่ QR ส่งอาจารย์

เอกสารอ้างอิง: [Vercel + Vite](https://vercel.com/docs/frameworks/frontend/vite), [Production Branch](https://vercel.com/docs/git#production-branch), [Environment Variables](https://vercel.com/docs/environment-variables), [Rewrites](https://vercel.com/docs/rewrites)
