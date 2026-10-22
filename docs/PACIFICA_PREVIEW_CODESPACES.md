# Pacifica 612VIIFM — เปิดใน Codespaces บน iPad

ภาพที่ผู้ใช้จัดหาครบ 4 ภาพรวมอยู่ในโปรเจกต์แล้ว ไม่ต้องเลือกไฟล์จาก iPad ซ้ำ ใช้คำสั่ง Vite ปกติได้ทั้ง Development และ Production Build

## เปิดเว็บ

เปิด Codespace เดิมจาก https://github.com/codespaces แล้วเปิด Terminal ที่โฟลเดอร์ Fretline หากมี Vite เดิมทำงานอยู่ กด Ctrl+C ก่อน

```bash
git pull --ff-only origin master
npm install
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

หาก Git แจ้งว่าไฟล์ที่แก้ไว้ขัดกับการอัปเดต ให้สำรองการแก้ไขก่อน แล้วค่อย pull อีกครั้ง:

```bash
git stash push -u -m "backup-before-pacifica-gallery"
git pull --ff-only origin master
```

การแก้ไขเดิมอยู่ใน `git stash list` ห้ามใช้ reset หรือ force push เพื่อแก้ปัญหานี้

เลือก **Ports → 5173 → Visibility: Private → Open in Browser** จากนั้นเปิด:

```text
/guitars/yamaha-pacifica-612viifm
```

ข้อความ `/guitars/...` เป็นเส้นทางใน Safari ไม่ใช่คำสั่ง Terminal

## ภาพและรายละเอียด

- Catalog แสดงภาพสีดำเป็นค่าเริ่มต้นและมีการ์ดเพียงใบเดียว
- Detail มีภาพดำ แดง ฟ้าอมเขียว และภาพรวม 3 สี พร้อม Thumbnail, ปุ่มเลือกสี และ Lightbox
- ราคา 34,000 บาทเป็นราคาขายปลีกแนะนำโดย Yamaha ประเทศไทย ใช้รายละเอียดและสเปกชุดเดียวกับ Catalog, Compare และ Wishlist
- ไฟล์ JPEG เดิมไม่ถูกครอป สร้างใหม่ หรือเปลี่ยนสี
- ผู้ใช้ขอให้นำไฟล์ภาพไปใช้ในโครงงานแทนเงื่อนไข Preview-only เดิม ข้อมูลที่มาและประวัติ AI editing เก็บใน `src/data/catalog/projectArtwork.json` ไม่แสดงเป็นป้ายบนการ์ดหรือภาพหลัก และไม่เปลี่ยนสถานะ license/model/color verification ให้เป็นจริง
- ฐานข้อมูลยังมี 200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 รุ่น

## การตรวจครั้งนี้

ดูผลทดสอบและภาพหน้าจอชุดปัจจุบันใน `docs/qa-pacifica-project/` รายงาน private-preview เดิมเก็บไว้เป็นประวัติและไม่ใช่สถานะการแสดงภาพปัจจุบัน
