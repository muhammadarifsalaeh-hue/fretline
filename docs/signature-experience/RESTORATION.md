# คืนดีไซน์เดิมตามคำขอเจ้าของ

เจ้าของไม่ต้องการดีไซน์ Signature ที่เผยแพร่ทดสอบ จึงคืนไฟล์ใน `src/` ทั้งหมดให้ตรงกับต้นฉบับก่อนเริ่มดีไซน์ใหม่: `302ce43def126e4785460c4b0297eae973dbccfb`

- Branch งานคืนดีไซน์: `feature/restore-original-experience`
- คืนเฉพาะ 27 ไฟล์ Presentation ที่เปลี่ยนในรอบ Signature รวมการนำ CSS และ Wrapper ใหม่ออก
- ไม่ Reset/Revert ทั้งโปรเจกต์ ไม่แก้ฐานข้อมูล ไม่เปลี่ยนรูป ราคา สเปก รหัสสินค้า Admin/Auth หรือระบบคอร์ด/3D
- ตรวจ Protected files 179 ไฟล์และทุก Field ของข้อมูลตรงกัน: 200 รุ่น / 10 แบรนด์ / 42 คอร์ด
- Build ผ่าน; Browser routes 104/104, Interactions 22/22 ผ่านบน Chromium/WebKit ไม่มี Console/Runtime errors ที่ตรวจพบ
- โค้ดหน้าเว็บตรงกับต้นฉบับทั้ง `src/` ไม่ใช่เพียงซ่อนสไตล์ใหม่ด้วย CSS
- คืนดีไซน์บน Site เดิม `appgprj_6ae3ecbd81208191882ee17887744126` โดยคงสิทธิ์ดูเฉพาะเจ้าของ ไม่เปลี่ยนหรือ Merge เข้า GitHub master
- Supabase จริงยังไม่ได้เชื่อมในเว็บทดสอบ ไม่รัน SQL หรือเปลี่ยนฐานข้อมูล

## งานใหม่ยังเก็บไว้ครบ

Signature ยังอยู่ที่ `feature/fretline-signature-experience` Commit `b4c0bba`, Tag `backup/fretline-signature-before-restore-20261030-b4c0bba` และ Site version ก่อนหน้า ไม่ลบประวัติหรือ Force Push

หลักฐานการคืนดีไซน์อยู่ใน [restoration/](restoration/) บันทึกการเผยแพร่พร้อม URL/Version อยู่ใน `.local-preview/signature-experience/site-publication.json` เฉพาะ Workspace โดยไม่มี Credential
