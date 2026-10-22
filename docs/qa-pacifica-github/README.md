# Pacifica Preview — GitHub readiness validation

นำโค้ดเดิมและงานทดลอง Pacifica ที่ค้างไว้ขึ้น master ตามคำสั่งผู้ใช้ โดยไม่รวมภาพต้นฉบับที่ยังไม่มีหลักฐานสิทธิ์ ไม่สร้าง Git repository ใหม่ ไม่ใช้ force push และรักษา commit chain เดิม

คู่มือใช้งานจริง: [เปิดใน Codespaces บน iPad](../PACIFICA_PREVIEW_CODESPACES.md)

## เพิ่มเพื่อให้เปิดจาก GitHub/Codespaces ได้

- โหมด pacifica-preview เริ่ม server ได้แม้ไม่มี JPEG ในโฟลเดอร์ส่วนตัว
- ช่องเลือก JPEG ทั้ง 4 บน Detail ใช้ blob URL ในหน่วยความจำเบราว์เซอร์ ไม่ส่ง POST/upload ไป server, GitHub หรือบันทึกภาพใน localStorage
- ภาพใช้ร่วมกับ Gallery, ตัวเลือกสี, Catalog, Compare และ Wishlist ภายใน SPA; refresh จะกลับ Placeholder จนเลือกไฟล์ใหม่
- ล้างภาพแล้ว revoke URLs และ reset file inputs; ไฟล์ที่ไม่ใช่ JPEG ที่เปิดได้หรือเกิน 8 MB ต่อภาพแสดงข้อความผิดพลาด
- ภาพและ screenshot ทั้งหมดที่ยังไม่มีสิทธิ์อยู่ใน .local-preview/ ซึ่ง Git ignore; ไม่ใส่ใน licensed image registry หรือ Production Build
- รักษาข้อมูล 200 รุ่น / 10 แบรนด์ / แบรนด์ละ 20 รุ่น ไม่มี Guitar ID ใหม่ตามสี ส่วนข้อมูลราคา ฿34,000 และสเปก PAC612VIIFM จากงานทดลองก่อนหน้าอ้าง Yamaha ประเทศไทยพร้อม source.fields และวันที่เดิม

## ผลทดสอบก่อน commit

- Build ปกติ: ผ่าน
- Build ด้วย mode pacifica-preview: ผ่าน และยังไม่รวมภาพส่วนตัว
- Catalog check: ผ่าน (200 / 10 / 20, ไม่มีรุ่นหรือ ID ซ้ำ)
- Images check: ผ่าน (licensed photo models 2, placeholders 198)
- Data/preview checks: 15 ผ่าน
- Browser Gallery: 117 ผ่าน (320–1440px, สี, thumbnail, overview, lightbox, keyboard, touch emulation, Wishlist, Compare, licensed-photo regression)
- Fresh Codespaces / browser file selection: 10 ผ่าน (เปิดได้เมื่อไม่มีไฟล์, สี, Catalog/Wishlist ข้ามหน้า, clear, invalid-image error, refresh, ไม่มี upload)
- Production exclusion: 14 ผ่าน (ไม่มีภาพ/endpoint/ตัวเลือกสี/ช่องเลือกไฟล์ทดลองใน Production)
- ไม่พบ Console/Runtime error ในชุดที่ผ่าน ยังไม่ทดสอบ Safari/iPad จริง

เก็บ logs และ validation-before-push.json ในโฟลเดอร์นี้ ผลจากภาพเดี่ยวและ Multi-color รอบก่อนยังคงไว้เป็นประวัติการทดสอบ ไม่ใช่สถานะการ Push ล่าสุด
