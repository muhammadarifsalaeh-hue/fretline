# ตรวจและเตรียมรัน Supabase setup จากไฟล์ — ยังไม่อนุมัติให้รัน

สถานะรอบนี้: **ยังไม่ได้รัน SQL ใดกับฐานข้อมูล ไม่ได้เปลี่ยนฐานข้อมูล และยังไม่ได้ยืนยันการเชื่อมต่อ Project จริง**

ตรวจจาก Branch `feature/fretline-admin-studio` ฐานโค้ด `4fbcd40` ไม่แก้ `supabase/setup.sql`, หน้าเว็บ, ข้อมูลสินค้า หรือ `master` เพิ่มเฉพาะเครื่องมือและคู่มือเตรียมงาน

## ผลตรวจไฟล์

| รายการ | ผล |
| --- | --- |
| ขนาด setup.sql | 587,474 bytes |
| ตรงกับ Migration + Seed | ตรง |
| สินค้า / ID ไม่ซ้ำ | 200 / 200 |
| แบรนด์ | 10 แบรนด์ แบรนด์ละ 20 |
| มีราคา / สอบถามราคา | 27 / 173 |
| ราคา 0 | ไม่มี |
| Gallery เดิม | 3 รุ่น คง Legacy Reference ไม่ย้ายหรือลบไฟล์ภาพ |
| Seed ข้อมูลสินค้าซ้ำ | ใช้ ON CONFLICT DO NOTHING ไม่เขียนทับ Draft/Published เดิม |

SHA-256 ของไฟล์ต้นฉบับที่ตรวจ:

```text
b824dfb085f5371d013b8168bf5b5fbd6e9b70e1672c65415980de8ba7bdda96
```

สิ่งที่จะเปลี่ยนเมื่อรันจริง: สร้าง/ปรับนิยามตาราง 8 ตาราง, Index, Functions, เปิด RLS, สร้างใหม่เฉพาะ Policies ชื่อ Fretline, ปรับ GRANT/REVOKE, สร้างหรือปรับ Bucket `guitar-images` เป็น Private พร้อมข้อจำกัดไฟล์ และนำเข้า 200 รุ่นเป็น Published ในฐานข้อมูล ตั้ง `catalog_state.ready=true`

ไม่สร้างบัญชี Auth หรือแอดมิน ไม่อัปโหลด/ลบภาพ ไม่เปลี่ยนแหล่งข้อมูลของ Frontend และไม่ Deploy เว็บไซต์

แม้ Seed ไม่เขียนทับสินค้าเดิม แต่การรัน Migration ซ้ำ **ยังเปลี่ยนนิยาม Functions, Policies, สิทธิ์ และการตั้งค่า Bucket** จึงต้องตรวจฐานเดิมก่อน ไม่ถือว่าการรันซ้ำไม่มีผลข้างเคียง

## จุดที่พบและวิธีเตรียมแก้

ต้นฉบับมี BEGIN/COMMIT แยกสองชุด: Migration และ Seed ส่วนแรกอาจ Commit ไปแล้วหากส่วนหลังล้มเหลว การเพิ่ม `psql --single-transaction` ครอบไฟล์เดิมอย่างเดียวไม่แก้ปัญหา เพราะไฟล์ยังมี COMMIT ภายใน

ตัวช่วยเตรียมไฟล์ใหม่แบบ Atomic โดยตรวจ checksum ต้นฉบับก่อน แล้วเอาออกเฉพาะขอบเขตธุรกรรม 4 บรรทัดที่ตรวจแล้ว ครอบด้วยธุรกรรมเดียว เพิ่ม Lock/Statement timeout และตรวจจำนวนก่อน Commit ไม่แก้ไฟล์ต้นฉบับ ไม่ใช้การลบคำว่า BEGIN/COMMIT แบบกว้าง ๆ ที่อาจกระทบ Function Body

ไฟล์ที่เตรียมเก็บใน `.local-preview/supabase/setup.atomic.sql` ซึ่งถูก Git Ignore และ Vite ปฏิเสธการให้บริการโฟลเดอร์นี้ ตัวช่วยจะสร้างใหม่ได้จากไฟล์ใน Git ไม่ต้องคัดลอก SQL ยาวบน iPad

SHA-256 ของ Payload ที่เตรียม:

```text
b4dccdfc0b4a19b7c00d0784deae243f28fd6304121f0b937b4279287515f359
```

โหมดรันจริงของตัวช่วยนี้มีไว้สำหรับ **Initial Setup ของ Project ว่าง** เท่านั้น หากพบตาราง Fretline หรือ Bucket เดิมจะหยุดเพื่อให้ตรวจใหม่ ไม่ล้างข้อมูล ไม่ Drop ตาราง และไม่เปิดทางข้าม Guard อัตโนมัติ หากเคยรัน SQL ไปบางส่วนแล้วต้องตรวจกรณีนั้นแยกก่อน

## วิธีเชื่อมต่อที่เตรียม: HTTPS Management API

ใช้ไฟล์ SQL ใน Repository ส่งจาก Python ฝั่ง Codespaces ผ่าน Management API หลังได้รับอนุมัติ ไม่ใช้ Database Password, connection string, psql หรือ Service Role key และไม่ต้องติดตั้ง Supabase CLI

คำสั่ง/API ตรวจสอบกับเอกสารและ OpenAPI ทางการแล้ว:

- `GET /v1/projects/{ref}` ตรวจว่าตรง Project ชื่อ Fretline
- `GET /v1/projects/{ref}/health?services=db` ต้องได้ `ACTIVE_HEALTHY`
- `POST /v1/projects/{ref}/database/query` ใช้เฉพาะหลังอนุมัติ รองรับ `query` และ `read_only`

Endpoint รัน Query ยังเป็น Beta/Experimental ตามเอกสาร Supabase จึงยังไม่ถือว่าทดสอบการรัน Payload นี้กับ Hosted Project ผ่านแล้ว หากระบบปฏิเสธหลาย Statements จะหยุด ไม่แยกส่งทีละส่วนเอง

`--check-connection` ใช้เฉพาะ GET สองรายการแรก ไม่มี SELECT 1 ไม่มีการอ่านตารางผ่าน SQL และไม่มี POST ไป Query Endpoint ผลตรวจการเชื่อมต่อไม่ได้รับรองสิทธิ์เขียนฐานข้อมูลหรือความว่างของ Schema

## สิ่งที่ต้องกดเองบน iPad ตอนนี้

1. เปิด Project Fretline ใน Supabase → **Project Settings → General → Project ID** คัดลอกเฉพาะ ID ไม่ใช้ connection string
2. เปิด [Supabase Access Tokens](https://supabase.com/dashboard/account/tokens) → **Generate new token** ตั้งชื่อเช่น `Fretline setup check` เลือก Scoped จำกัดเฉพาะ Project Fretline และให้ **Project Settings → Read** ก่อน ใช้อายุสั้นตามที่ Dashboard รองรับ ไม่เลือก Legacy/Full access
3. คัดลอก Token ไปใส่ใน **GitHub → รูปโปรไฟล์ → Settings → Codespaces → Codespaces secrets → New secret** โดยตรง ไม่ส่งผ่านแชท
4. เพิ่มสองค่า โดยเลือก **Repository access → fretline → Add secret** สำหรับแต่ละรายการ:

| Name | Value ที่กรอกในหน้า Secrets เท่านั้น |
| --- | --- |
| `FRETLINE_SUPABASE_PROJECT_REF` | Project ID ของ Fretline |
| `FRETLINE_SUPABASE_ACCESS_TOKEN` | Scoped Personal Access Token จากขั้นก่อน |

ไม่ตั้งชื่อขึ้นต้น `VITE_` ไม่ใส่ Token ใน Frontend, `.env.example`, Git หรือข้อความ Terminal ไม่มีการพิมพ์หรือส่ง Token/Password/connection string ในแชท

5. Stop แล้ว Start Codespaces ใหม่ เพื่อรับ Secret ที่เพิ่ม ให้ใช้ Branch `feature/fretline-admin-studio` ซึ่งอัปเดตไฟล์เครื่องมือล่าสุดแล้ว
6. เปิด Terminal ที่โฟลเดอร์โปรเจกต์ แล้วรันเฉพาะโหมดตรวจดังนี้:

```bash
python scripts/supabase-setup.py --check-connection
```

ผลลัพธ์แสดงเฉพาะชื่อ/ID โปรเจกต์ สถานะ และ checksum ไม่แสดง Token หรือข้อมูลเชื่อมต่อฐานข้อมูล ส่งผลลัพธ์นี้กลับมาตรวจได้ หากพบ Missing settings/401/403 ให้หยุดตรวจ Secret และสิทธิ์ ไม่ต้องเพิ่มสิทธิ์กว้างหรือปิด RLS

Secret ใน Codespaces ของเจ้าของไม่จำเป็นต้องปรากฏใน Workspace ของ Codex ซึ่งเป็นคนละสภาพแวดล้อม จึงต้องตรวจใน Codespaces ที่ตั้งค่านั้นจริง

## คำสั่งที่ตรวจแล้วว่าปลอดจากการรัน SQL

```bash
# ตรวจไฟล์อย่างเดียว ไม่ติดต่อบริการ
python scripts/supabase-setup.py

# เตรียมไฟล์ Atomic ในเครื่องเท่านั้น ไม่เชื่อมต่อฐานข้อมูล
python scripts/supabase-setup.py --prepare

# ตรวจชื่อ Project และ Health ผ่าน GET เท่านั้น ไม่ส่ง SQL
python scripts/supabase-setup.py --check-connection
```

ผลที่รันใน Workspace รอบนี้: ตรวจไฟล์และเตรียม Payload สำเร็จ โหมดตรวจการเชื่อมต่อหยุดทันทีเพราะไม่พบสองค่าข้างต้น **ไม่มี Request ถึง Project และไม่มี SQL ถูกส่ง**

## หลังตรวจการเชื่อมต่อแล้ว — ยังไม่ให้รันในรอบนี้

ก่อนขออนุมัติต้องระบุ Project ที่ตรวจได้, checksum ของ Payload, ผลกระทบ และยืนยันว่าจะตรวจ Schema เดิมก่อน หากมีข้อมูลเดิมต้องสำรองตามแผนของ Project และทบทวนการย้ายข้อมูลแยก ไม่ใช้โหมด Initial Setup นี้ทับ

หลังเจ้าของยืนยันเท่านั้น จึงให้ Token ของ Project นั้นมี **Database → Read-write** เพื่อทำ Setup ไม่ต้องให้ API Key Secrets, Billing, Auth Write หรือสิทธิ์ทุก Project เมื่อเสร็จงานให้ Revoke Token ชั่วคราวได้

ตัวช่วยมี `--apply` แยกจากโหมดตรวจ และต้องมีทั้ง `--approve-project` กับ `--approve-sha256` ตรงกับค่าจริงที่ตรวจแล้ว ขาดข้อใดจะหยุดก่อนติดต่อ API ยังไม่แสดงคำสั่ง Apply ที่ใส่ค่าจริง เพราะยังตรวจการเชื่อมต่อไม่ได้และยังไม่มีการอนุมัติ

ลำดับหลังอนุมัติ: ตรวจ Project/Health → ส่ง Read-only SQL ตรวจว่ามีตาราง/Bucket เดิมหรือไม่ → หากว่างจึงส่ง Payload ครั้งเดียว → ตรวจจำนวนหลังรัน ไม่ Retry งานเขียนอัตโนมัติ หาก HTTP Timeout อาจ Commit ไปแล้ว ต้องตรวจสถานะก่อน ไม่สรุปว่า Rollback สำเร็จจาก Timeout เพียงอย่างเดียว

## ผลตรวจและขอบเขต

- Offline Safeguard Tests ผ่าน 13/13 ใช้ HTTP จำลองและห้ามเรียก Network จริง ไม่มี SQL Engine หรือฐานข้อมูลถูกใช้ในการทดสอบนี้
- PostgreSQL parser `pglast v8.7` อ่านต้นฉบับได้ 60 Statements และ Payload ได้ 62 Statements เป็นการ Parse ใน Memory ไม่ใช่การ Execute หรือยืนยันสิทธิ์/Compatibility ของ Hosted Database
- ไม่รัน Database Tests ของงานรอบก่อน ไม่ Start Docker Database ไม่รัน Apply ไม่เปลี่ยนฐานข้อมูล ไม่ Merge `master`

แหล่งอ้างอิงทางการ:

- [Supabase Personal Access Tokens / scopes](https://supabase.com/docs/guides/platform/personal-access-tokens)
- [Management API: Query](https://supabase.com/docs/reference/api/v1-run-a-query)
- [Management API: Health](https://supabase.com/docs/reference/api/v1-get-services-health)
- [GitHub Codespaces Secrets](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces)
