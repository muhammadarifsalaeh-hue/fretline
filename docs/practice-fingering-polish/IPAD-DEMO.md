# สาธิต Fretline Guitar Practice Studio บน iPad

งานนี้ใช้ Codespaces และ Preview ได้ ไม่ต้อง Deploy หรือตั้งค่า Supabase เพิ่ม

1. เปิด [VS Code ของ Codespaces เดิม](https://turbo-fortnight-96wwrvp9jwqjh9px4.github.dev) ใน Safari และลงชื่อเข้า GitHub
2. เปิด **Terminal → New Terminal** หากมี Vite รันอยู่ใน Terminal เดิม ให้กด **Ctrl+C** เพื่อหยุดก่อน หากไม่มีปุ่ม Ctrl บนคีย์บอร์ด iPad ให้แตะรูปถังขยะในแถบ Terminal เพื่อหยุด Terminal นั้น แล้วเปิด New Terminal (ไม่ลบไฟล์โปรเจกต์)
3. วางคำสั่งนี้ใน Terminal คำสั่งจะหยุดเมื่อพบงานที่ยังไม่บันทึก ไม่ Reset, Stash หรือลบงาน

```bash
(
  set -e
  cd /workspaces/fretline
  if [ -n "$(git status --porcelain)" ]; then
    echo 'พบงานที่ยังไม่ได้บันทึก: หยุดไว้เพื่อรักษางานเดิม'
    git status --short
    exit 1
  fi
  git fetch origin
  git switch feature/restore-black-sleeved-hand
  git pull --ff-only origin feature/restore-black-sleeved-hand
  git rev-parse --short HEAD
  npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
)
```

4. รอข้อความ **Local / Network** ของ Vite แล้วเปิดแท็บ **Ports** เลือก **5173 → Open in Browser**
5. เปิดหน้า `/practice?chord=C` เพื่อเริ่มสาธิต เลือกคอร์ดจากรายการด้านล่าง
6. ลากหนึ่งนิ้วเพื่อหมุน จีบสองนิ้วเพื่อซูม หรือใช้ปุ่มหมุน/ซูมและเมนู **มุมมอง** ด้านบน
7. ปุ่ม **ซ่อนมือ / แสดงมือ** จะปรากฏเฉพาะท่าที่ผ่านเกณฑ์สัมผัสสายและการชนของโมเดล ท่าที่ไม่ผ่านจะใช้ผังคอร์ดและตำแหน่งนิ้วเดิม ไม่มีมือที่ถูกปฏิเสธแสดงเป็นตัวอย่าง

[ลิงก์ Practice ของ Codespaces เดิม](https://turbo-fortnight-96wwrvp9jwqjh9px4-5173.app.github.dev/practice?chord=C)

ลิงก์นี้ต้องมี Codespace เดิมเปิดอยู่และ Vite รันที่ 5173 การ Push ใน workspace ทดสอบไม่ได้เปลี่ยน branch หรือรีสตาร์ต Vite ใน Codespace ของเจ้าของบัญชีโดยอัตโนมัติ

หากแจ้ง **Port 5173 is already in use** ให้เปิด Terminal ที่รัน Vite เดิมแล้วกด Ctrl+C ก่อนเริ่มใหม่ ไม่ควรเปลี่ยนเป็นพอร์ตอื่นโดยไม่เปลี่ยน URL ให้ตรงกัน

หากเปิด Preview แล้วพบหน้าเข้าสู่ระบบ ให้เข้าสู่ GitHub บัญชีเดียวกับ Codespace ก่อน ส่วนการตั้ง Port Visibility เป็น Public เป็นตัวเลือกของเจ้าของบัญชี ไม่จำเป็นสำหรับการสาธิตใน Safari ที่เข้าสู่ระบบแล้ว

หากขึ้นข้อความพบงานที่ยังไม่ได้บันทึก ให้เก็บงานนั้นก่อน ไม่ใช้ `reset --hard`, `clean` หรือ Force Push

## ขอบเขตการรับรอง

ผังคอร์ดเดิมครบ 42 แบบ การผ่านเรขาคณิตหมายถึงผ่านการตรวจเมชจริงและสัมผัสสาย ไม่ใช่การรับรองท่าจับจากผู้สอนกีตาร์ ดูผลรายคอร์ดใน `CHORD-STATUS-42.md` ก่อนนำไปอ้างว่าสอนท่ามือได้ครบ 42 คอร์ด

การทดสอบหน้าจอใช้ Chromium บน Desktop, iPad แนวนอน/แนวตั้ง และ Mobile จำลอง ยังต้องลอง Safari บน iPad เครื่องจริง
