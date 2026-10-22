# เปิด Fretline และ Gallery PAC612VIIFM ใน Codespaces บน iPad

ใช้ Repository เดิม `muhammadarifsalaeh-hue/fretline`, branch `master` ไม่ต้องลง patch หรือสร้างโปรเจกต์ใหม่ ภาพต้นฉบับที่ยังไม่ได้ยืนยันสิทธิ์ไม่ถูกนำขึ้น GitHub

## คำสั่งเปิดเว็บ

เปิด Codespace เดิมจาก https://github.com/codespaces แล้วเปิด Terminal ที่ root ของ Fretline:

```bash
git pull --ff-only origin master
npm install
npm run dev:pacifica-preview -- --host 0.0.0.0 --port 5173 --strictPort
```

หาก git pull แจ้งว่ามีงานแก้ค้าง ให้สำรองและตรวจ diff ก่อน ห้าม reset หรือ force ทับงาน หาก Vite ตัวเก่าใช้ port 5173 อยู่ ให้กด Ctrl+C ที่ Terminal ตัวเก่าก่อนรันคำสั่ง dev ใหม่

เลือกแท็บ **Ports → 5173 → Private → Open in Browser** แล้วเข้า path:

```text
/guitars/yamaha-pacifica-612viifm
```

localhost ของเครื่องพัฒนาไม่ใช่ลิงก์เข้าเว็บจาก iPad โดยตรง ต้องเปิด URL ของ port ที่ Codespaces forward ให้ คง Terminal ที่รัน Vite ไว้ระหว่างดูเว็บ

## ดูภาพทั้ง 4 จาก iPad โดยไม่อัปโหลดเข้า GitHub

เมื่อไม่มีไฟล์ภาพส่วนตัวอยู่ใน Codespace หน้า Pacifica จะแสดงช่อง **เลือกภาพจากอุปกรณ์เพื่อดู Gallery**:

1. เลือก JPEG สีดำในช่อง Black
2. เลือก JPEG สีแดงในช่อง Red
3. เลือก JPEG สีฟ้าอมเขียวในช่อง Blue / Teal
4. เลือก JPEG ภาพรวมสามสีในช่องภาพรวม 3 สี
5. กด **แสดงภาพทั้ง 4**

เลือกไฟล์ให้ตรงรุ่นและช่องสี: โค้ดไม่ยืนยันความตรงรุ่นหรือสิทธิ์แทนผู้ใช้ ภาพใช้ผ่าน `blob:` URL ในหน่วยความจำเบราว์เซอร์ ไม่มี POST/upload, backend หรือการบันทึก bytes ภาพใน localStorage/GitHub เมื่อเปลี่ยนหน้าภายในเว็บไซต์ ภาพยังใช้กับ Catalog, Compare และ Wishlist ได้ เมื่อ refresh/ปิดแท็บให้เลือกภาพใหม่ ใช้ปุ่มล้างเพื่อลบภาพจาก Preview และคืน Placeholder

ไฟล์ต้องเป็น JPEG ที่เปิดอ่านได้ ไม่เกิน 8 MB ต่อภาพ รุ่นนี้ยังมีเพียง Guitar ID `yamaha-pacifica-612viifm` ภาพสามสีไม่ใช่กีตาร์สามรุ่นแยกกัน

หากมี JPEG ทั้งสี่ใน `.local-preview/yamaha-pacifica-612viifm/` อยู่แล้ว โหมด Preview ใช้ภาพเดิมจากโฟลเดอร์ที่ Git ignore ไม่แสดงช่องเลือกไฟล์เพิ่ม ดูชื่อไฟล์ใน [รายงาน Multi-color](qa-pacifica-multicolor/README.md)

## สิทธิ์ภาพและสถานะข้อมูล

- ป้าย AI ไม่แสดงบนการ์ดหรือบริเวณภาพหลัก เก็บการแก้ไขและข้อจำกัดไว้ใน metadata / ส่วนแหล่งข้อมูล
- ยังไม่มีหลักฐานสิทธิ์ภาพต้นฉบับ ไม่ยืนยันสีหรือฮาร์ดแวร์จากภาพตกแต่ง ชื่อ Black/Red/Blue / Teal ใช้แยกภาพ ไม่ใช่ชื่อสีทางการ
- ไม่เพิ่มภาพเหล่านี้ใน licensed image registry และไม่ใส่ใน Production Build ทั้ง dev ปกติและ Production ยังแสดง Placeholder สำหรับ PAC612VIIFM
- ห้าม git add -f ภาพใน `.local-preview/` หรือเผยแพร่ port เป็น Public จนจัดการสิทธิ์ครบถ้วน
- Catalog 200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 รุ่น ไม่มี ID ใหม่ตามสี
- ข้อมูล PAC612VIIFM ยังคง partial ราคา ฿34,000 คือราคาขายปลีกแนะนำจาก Yamaha ประเทศไทย ไม่รับประกันราคาขายร้านค้า แหล่งอ้างอิงและวันที่อยู่ใน Detail

## ตรวจโค้ด

```bash
npm run build
npm run catalog:check
npm run images:check
node scripts/check-pacifica-preview.mjs
```

ชุดตรวจจะระบุ SKIP การตรวจ bytes รูปส่วนตัวเมื่อไม่ได้วางไฟล์เหล่านั้นใน Codespace แยกจากผลข้อมูล/Build/สิทธิ์ที่ตรวจได้จาก repository

Browser QA ใช้ Chromium บน Linux; ยังไม่ได้ทดสอบ Safari/iPad จริง ดูผลใน `docs/qa-pacifica-github/`
