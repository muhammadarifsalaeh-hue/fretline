# Fretline Admin Studio — Phase 0–1 และจุดรอตั้งค่า Supabase

## สถานะที่ยืนยันได้

- งาน Catalog ก่อนหน้า Commit `a620d5e31948cd9ea063ad188a314d8c4e092d16` ถูก Push แล้วจริง: SHA บน `origin/feature/catalog-prices-2026-10-29` ตรงกับเครื่องนี้
- เริ่มงานด้วย Working Tree สะอาด ไม่มีงานผู้ใช้ที่ต้อง Stash หรือ Commit เพิ่ม
- สร้าง `feature/fretline-admin-studio` ต่อจาก Commit นี้ ไม่เปลี่ยนหรือ Merge `master`
- Catalog ครบ **200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 รุ่น** โดยใช้ ID เดิม
- มีราคาอ้างอิงได้ **27 รุ่น** (Yamaha 18 / Fender 9) อีก **173 รุ่น** เป็น “สอบถามราคา”
- งานก่อนหน้าเพิ่มสเปกที่ตรวจแหล่งอ้างอิงแล้ว 9 ช่อง ไม่มีรุ่นที่ครบทุกช่องสเปกที่ร้องขอ จึงไม่ระบุว่าสเปกครบแล้ว
- มีรูปสินค้าจริงตามระบบเดิม 3 รุ่น อีก 197 รุ่นคงสถานะไม่มีรูป ไม่แทนภาพคนละรุ่น
- การตรวจข้อมูล ราคา สเปก และการเก็บข้อมูลเดิมผ่านก่อนเริ่มแก้ไฟล์ Admin

รายงานข้อมูลเดิม: [Catalog update](../catalog-update-2026-10-29/README.md)

## สิ่งที่เตรียมแล้ว

React 18 + Vite 5 ใช้ React Router 6 ผ่าน `BrowserRouter` และ Route ใน `src/App.jsx` ข้อมูลปัจจุบันเป็น JSON ที่รวมผ่าน `src/data/guitars.js` ยังไม่มี Backend หรือ Supabase client

เพิ่ม Route `/admin` แบบ Lazy Load ใช้ธีมและ Design Tokens ดำ–ทองเดิม พร้อมหน้ารอตั้งค่าที่แสดงสถานะตามจริง รองรับจอแคบและสัมผัส ไม่เพิ่มเมนูหรือเปลี่ยนหน้า Home / Explore by Brand ไม่มีฟอร์มล็อกอินหรือปุ่มบันทึกที่แสร้งว่าทำงานได้

**นี่เป็นทางเข้าเบื้องต้น ยังไม่ใช่ Admin Studio ที่จัดการสินค้าได้**

## หยุดก่อน Phase 2 ตามคำสั่งผู้ใช้

ไม่พบ Supabase Project URL, Publishable key, ตัวแปร Supabase หรือไฟล์ตั้งค่าเชื่อมต่อใน Workspace นี้ และไม่มีบริการ Supabase ที่เชื่อมต่อให้เรียกใช้ได้

จึงยังไม่ได้สร้าง/เชื่อมต่อ Database, Auth, Storage, RLS, Migration หรือ Import สินค้าใดเข้า Supabase ยังไม่ได้สร้างบัญชีแอดมิน และยังไม่ได้แก้แหล่งข้อมูลของเว็บจริง

เมื่อถึงขั้นที่ผู้ใช้ต้องสร้างบัญชีหรือกรอกค่าเชื่อมต่อ ผู้ใช้สั่งให้หยุดและแจ้งขั้นตอน จึงยังไม่เริ่ม Phase 3–10 หรือรายงานว่าระบบบันทึกและ Publish ใช้งานได้

## สิ่งที่ต้องทำบน iPad Safari ตอนนี้

หากมี Supabase Project สำหรับ Fretline อยู่แล้ว ใช้ Project นั้นได้ ไม่จำเป็นต้องสร้างใหม่

1. เปิด [Supabase Dashboard](https://supabase.com/dashboard) แล้วสมัครหรือล็อกอินด้วยบัญชีของคุณ
2. กด **New project** แล้วเลือกหรือสร้าง Organization หากระบบถาม
3. ตั้งชื่อ `Fretline` เลือก Region ที่เหมาะสม และกำหนด Database password ที่เดายาก เก็บรหัสผ่านไว้กับตัว ไม่ต้องส่งให้ Codex
4. ตรวจแผนและค่าใช้จ่ายที่แสดง แล้วกด **Create new project** รอจน Project พร้อม
5. ที่หน้า Project กด **Connect** แล้วมองหาค่า **Project URL** และ **Publishable key** ในตัวอย่างเชื่อมต่อแอป หากไม่แสดง ให้เปิด **Project Settings → Data API** เพื่อดู Project URL และ **Project Settings → API Keys → Publishable key** เพื่อดูคีย์ ชื่อเมนูอาจต่างเล็กน้อยตาม Dashboard รุ่นที่ใช้
6. ส่งกลับมาเฉพาะ **Project URL** เช่น `https://<project-ref>.supabase.co` และ **Publishable key** ที่ขึ้นต้น `sb_publishable_...` ค่านี้ออกแบบให้ใช้ใน Frontend ได้ แต่ยังต้องมี RLS ก่อนให้ผู้ใช้แก้ข้อมูล

ถ้าเมนูด้านซ้ายถูกซ่อนบน iPad ให้กดเมนูมุมซ้ายบน หรือใช้เมนู Safari → Request Desktop Website

**ห้ามส่ง** Database password, Connection string ที่มีรหัสผ่าน, JWT secret, Access token, `service_role`, Secret key หรือคีย์ที่ขึ้นต้น `sb_secret_...` และห้ามใส่ข้อมูลเหล่านี้ในตัวแปร Vite ที่ขึ้นต้น `VITE_`

รอบนี้ยังไม่ต้องรัน SQL เปิด Bucket เป็น Public สร้างผู้ใช้ หรือปิด RLS เอง การตั้งค่าสิทธิ์และบัญชีแอดมินครั้งแรกจะทำหลังเตรียม Migration และทดสอบข้อจำกัดสิทธิ์แล้ว

เอกสารทางการที่ตรวจสอบได้:

- [Supabase API keys](https://supabase.com/docs/guides/api/api-keys)
- [Supabase + React](https://supabase.com/docs/guides/getting-started/quickstarts/reactjs)

## สิ่งที่จะทำต่อหลังได้รับค่าเชื่อมต่อ

ส่วนนี้เป็นแผนงาน ยังไม่ได้ติดตั้งหรือทดสอบกับฐานข้อมูลจริง

1. เตรียม SQL Migration สำหรับ Brands, Guitars, Specifications, Images, Prices, Admin Users และ Audit Logs ใช้ ID เดิม พร้อมค่าที่ไม่ทราบเป็น `null`
2. แยกข้อมูลแก้ไข Draft ออกจากสำเนาที่ Published เพื่อให้การบันทึก Draft ของรุ่นเดิมไม่เปลี่ยนข้อมูลสาธารณะก่อน Publish และซ่อนสินค้าโดยไม่ลบข้อมูล
3. เปิด RLS ทุกตาราง ให้สาธารณะอ่านได้เฉพาะ Published จำกัดการแก้ไขและ Storage สำหรับแอดมิน ตรวจสิทธิ์ที่ฐานข้อมูล ไม่ใช้การซ่อนปุ่มหรือ Frontend Guard เป็นระบบความปลอดภัย
4. บัญชีแอดมินสร้าง/เชิญผ่านเจ้าของ Project และกำหนดสิทธิ์จากช่องทางที่มีสิทธิ์เท่านั้น ผู้ใช้ทั่วไปต้องเพิ่มตัวเองเป็นแอดมินไม่ได้
5. นำเข้า 200 ID แบบรันซ้ำได้และไม่เขียนค่าที่มีอยู่ด้วย `null` เก็บข้อมูลต้นทางและรูปเดิมไว้ รวมภาพที่ยังใช้ URL/Asset เดิม
6. ทดสอบการปฏิเสธผู้ไม่มีสิทธิ์ Draft/Published การอัปโหลด ราคา ประวัติ และข้อมูล Compare จริง ก่อนเปลี่ยน Catalog / Search / Brand / Detail / Compare / Quiz มาอ่านข้อมูลใหม่
7. เตรียม Feature Flag และขั้นตอน Rollback กลับไปใช้ Catalog เดิมก่อนเปิด Backend บนเว็บจริง โดยไม่ทำให้สินค้าที่ซ่อนกลับมาปรากฏเพราะ Offline Fallback

## เข้า Preview และ Rollback ในรอบนี้

ให้เปิดจาก Preview เดิมของ Codespaces แล้วเติม `/admin` หลังโดเมน เช่น `<Preview origin>/admin` ไม่มี URL Codespaces เต็มที่ตรวจสอบได้จาก Workspace นี้ จึงไม่สร้าง URL ขึ้นเอง

หาก Codespaces ยังอยู่ Branch เก่า ให้เปิด Terminal ใหม่และตรวจ `git status --short --branch` ก่อน หากมีไฟล์แก้ค้างอยู่ให้หยุดตรวจ ไม่ Reset หรือ Force Switch จากนั้นจึงใช้:

```bash
git fetch origin
git switch feature/fretline-admin-studio
git pull --ff-only
```

ถ้า Vite เดิมทำงานบน Port 5173 อยู่แล้ว ไม่ต้องเปิดเซิร์ฟเวอร์ซ้ำ Refresh หน้าเดิมได้ หากยังไม่มีเซิร์ฟเวอร์ ให้รันจาก `/workspaces/fretline`:

```bash
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

เปิดแท็บ **Ports** แล้วเลือก **Open in Browser** ของ Port 5173 อย่าเปลี่ยน Port เพื่อแก้ปัญหา “already in use” โดยยังไม่ตรวจเซิร์ฟเวอร์เดิม

รอบนี้ยังไม่มี Database Migration หรือ Deploy จริง หากต้องย้อนเฉพาะงาน Admin ให้ Deploy Commit ก่อนหน้า `a620d5e` หรือกลับ Branch `feature/catalog-prices-2026-10-29` หลังตรวจ Working Tree สะอาด ไม่ใช้ Reset/Force Push และไม่กระทบงานนำเข้าราคาเดิม

## ขอบเขตการทดสอบ

ตรวจ Build, Catalog, ราคาและสเปกเดิม และหน้า `/admin` เบื้องต้นได้เท่านั้น การล็อกอิน สิทธิ์ Upload การบันทึก Draft/Publish และการย้ายข้อมูลยังทดสอบกับ Supabase ไม่ได้จนกว่าจะเชื่อมต่อจริง จะไม่รายงานว่าผ่านล่วงหน้า

ผลที่รันจริงในรอบนี้:

| การตรวจ | ผล |
| --- | --- |
| `npm run build` | ผ่าน มีคำเตือนขนาด Chunk 3D เดิม |
| `npm run catalog:check` | ผ่าน 200 รุ่น / 10 × 20 |
| `npm run images:check` | ผ่าน รูปและสิทธิ์เดิมไม่เปลี่ยน |
| `npm run practice:check` | ผ่าน 56/56 รวมคอร์ดเดิม 42 คอร์ด |
| ราคา public | ผ่าน 5/5 |
| ข้อมูล Compare | ผ่าน 15/15 |
| ตรวจการรักษาข้อมูลนำเข้าเดิมก่อนแก้ Admin | ผ่าน 9/9 |
| Browser หน้า Setup และกลับ Catalog/Search | ผ่าน 8/8 Chromium + WebKit บน 4 ขนาดจอ |

Browser ไม่มี Console/Runtime/HTTP Error ในรอบทดสอบนี้ ยังไม่ได้ทดสอบบน iPad เครื่องจริง การตรวจ Git ยืนยันว่าไฟล์เดิมใน `src` / `public` ที่เปลี่ยนมีเพียง `src/App.jsx` เพิ่ม Import และ Route อย่างละบรรทัด ส่วนอีก 280 ไฟล์เดิมไม่เปลี่ยน และเพิ่มไฟล์หน้า Admin กับ CSS แยกต่างหาก

- [ผล Browser Tests](tests/browser-results.json)
- [ภาพ iPad แนวนอน](tests/admin-setup-ipad-landscape.png)
- [ภาพ iPad แนวตั้ง](tests/admin-setup-ipad-portrait.png)

หน้า Login/Dashboard/จัดการสินค้า/ภาพ/ราคา/สเปก, SQL Migration, RLS, Import ไป Supabase และระบบ Publish **ยังไม่เสร็จและยังไม่ได้ทดสอบ** ไม่มีบัญชีแอดมินหรือรหัสผ่านเริ่มต้นให้ล็อกอินในรอบนี้
