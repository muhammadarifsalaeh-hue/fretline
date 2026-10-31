# FRETLINE — Practice Studio 3D / Premium Minimal

ปรับเฉพาะหน้า `/practice` บน branch `feature/practice-premium-minimal` จาก `fb65ad182043fbdf2c2b0f522a7d4ea9d4c1d41f` โดยไม่รวมเข้า master หรือ Deploy

## สิ่งที่เปลี่ยน

- Desktop: คลังคอร์ดแบบแถวกะทัดรัด / โมเดล 3D / ผังคอร์ดและตำแหน่งนิ้ว แบ่งเป็นสามคอลัมน์ พื้นที่ตรงกลางกว้างที่สุด
- Tablet: ปรับเป็นแถบเลือกคอร์ดด้านบน และหนึ่งหรือสองคอลัมน์ตามพื้นที่จริง
- Mobile: ชื่อหน้า → ค้นหาและประเภทคอร์ด → รายการคอร์ดแนวนอน → โมเดล → แถบควบคุม → รายละเอียด → คอร์ดยอดนิยม
- ใช้สีดำ #080808, ทอง #D9B675 และตัวอักษรขาวนวล ขอบบาง ลดข้อความและกรอบที่ไม่จำเป็น
- ค้นหา ตัวกรองพื้นฐาน/ประเภทคอร์ด แป้นลูกศร Home/End และลิงก์คอร์ดผ่าน URL ยังใช้ได้
- แถบควบคุมชุดเดียว: ฟัง/หยุดเสียง ลดความเร็ว ตัวเลขความเร็ว เพิ่มความเร็ว รีเซ็ตกล้อง และเปิด/ปิดจุดบอกนิ้ว
- เสียงสังเคราะห์ด้วย Web Audio จากโน้ตของสายที่เล่นในข้อมูลคอร์ดเดิม ไม่ใช่เสียงบันทึกกีตาร์จริง ความเร็ว 0.5×–1.5× เปลี่ยนจังหวะการดีด ไม่เปลี่ยนระดับเสียงหรือข้อมูลท่านิ้ว
- เมนูมุมกล้องมีหกมุม และคงตัวเลือกซ่อน/แสดงมือที่ผ่านประตูตรวจสอบเดิมไว้ หมุนด้วยการลาก ซูมด้วยสองนิ้ว/ล้อเมาส์ และใช้คีย์บอร์ดได้
- คอร์ดยอดนิยมใช้ผังคอร์ดจริงที่มีอยู่ เลื่อนแนวนอนและเลือกเพื่อเปลี่ยนคอร์ดหลักได้ ไม่มีภาพท่านิ้วที่สร้างขึ้นใหม่
- ปุ่มสัมผัสในแถบควบคุมมีพื้นที่อย่างน้อย 44 × 44 px แม้หน้าจอกว้าง 320 px รองรับ focus และ Reduced Motion
- แถบนำทางล่างยังมีทุกลิงก์ โดยอยู่ท้ายเอกสารเฉพาะหน้า Practice เพื่อไม่ให้บังมือและปุ่มฝึก หน้าอื่นใช้ตำแหน่งเดิม
- กรณีโมเดลหรือเสียงโหลดไม่ได้ แสดงข้อความสั้นพร้อมวิธีลองใหม่ ไม่ซ้อนทับปุ่ม และยังเปิดผังคอร์ดได้

## ข้อมูลและความถูกต้องที่รักษาไว้

กีตาร์ 200 รุ่น, 10 แบรนด์ แบรนด์ละ 20 รุ่น และคอร์ด 42 คอร์ดเท่าเดิม ราคา สเปก คำอธิบาย รูปภาพ ID และข้อมูลสถานะไม่มีการแก้ไข

- Effective product + chord data SHA256: `3db84c9266dcefd514add330090bc00b2d25d7b3f8f8b7a2d7b351e19841b657`
- โมเดลมือ/แขนเสื้อเดิม SHA256: `23fdb5745e9343b597eb816bcdfcb266c1942ebbbb495cdb3776214343d7f3bc`
- คลังท่านิ้วเดิม SHA256: `add2baeb95d5cf50f52ac82f568a95415958a38a91d72404ddc73874848f7b95`

คงเกณฑ์เดิมที่อนุญาตให้แสดงท่ามือ 13 คอร์ดซึ่งผ่านการตรวจ mesh/contact: C, Dm, E7, Cmaj7, Fmaj7, Em7, Am7, B7, C7, Dm7, Dsus2, G7, Gmaj7 ส่วนอีก 29 คอร์ดยังซ่อนมือและใช้ผังคอร์ดเดิม ไม่ได้เลื่อนสถานะการตรวจสอบคอร์ดใดให้ผ่านเพิ่มเติม

**เกณฑ์ mesh/contact ไม่ใช่การรับรองทางกายวิภาคหรือการสอน**: คลังเดิมยังมี `reviewed: false`, `anatomyPassed: false`, `multiViewReviewed: false` ทุกท่า ไม่มีท่าใดได้รับการรับรองการสอนอย่างอิสระในงานนี้

ไม่มีการแก้ Home, Catalog, Compare, Favorites, แบบทดสอบ, Admin, Supabase, SQL, RLS, seed, `.env.local`, รูปสินค้า หรือไบนารีโมเดล ตรวจความเหมือนของไฟล์ที่ป้องกันไว้และข้อมูลที่แอปโหลดจริงใน [data-safety.json](tests/data-safety.json)

## ภาพก่อน–หลังจาก Playwright

ภาพก่อนแก้จับจาก commit `fb65ad1` ก่อนลงมือเปลี่ยน UI ภาพหลังจับจาก production build ที่ใช้โมเดล GLB จริง เป็น Full Page ทั้งหมด

| ขนาดหน้าจอ | ก่อน | หลัง |
| --- | --- | --- |
| Desktop 1440 × 1000 | [ก่อน](screenshots/before-desktop.png) | [หลัง](screenshots/after-desktop.png) |
| iPad แนวนอน 1194 × 834 | [ก่อน](screenshots/before-ipad-landscape.png) | [หลัง](screenshots/after-ipad-landscape.png) |
| iPad แนวตั้ง 768 × 1024 | [ก่อน](screenshots/before-ipad-portrait.png) | [หลัง](screenshots/after-ipad-portrait.png) |
| Mobile 390 × 844 | [ก่อน](screenshots/before-mobile.png) | [หลัง](screenshots/after-mobile.png) |

เพิ่มเติม: [320 px](screenshots/after-small-mobile.png), [Tablet 1024 px](screenshots/after-tablet.png), [Desktop 1920 px](screenshots/after-wide-desktop.png)

## การทดสอบ

ผลสรุปที่ตรวจสอบย้อนกลับได้อยู่ใน [verification-summary.json](tests/verification-summary.json) และ log ใน `tests/`

- Production Build: `npm run build` ผ่าน มีคำเตือนเดิมเรื่อง Three.js chunk เกิน 500 kB โมเดล/Three.js ยังคงโหลดแบบแยกส่วนเมื่อเข้าหน้าฝึก ไม่เพิ่ม dependency
- คอร์ด/ผังคอร์ดเดิม: `npm run practice:check` 56/56
- Runtime มือเดิม: `node scripts/check-hand-runtime.mjs` 20/20
- ประตูแสดงมือและการเปลี่ยนคอร์ดเดิม: `node scripts/practice/check-hand-reveal.mjs` 10/10
- เสียงคอร์ด: `node scripts/check-practice-audio.mjs` 7/7 ครบโน้ตของ 42 คอร์ด การหยุดเสียง การยกเลิกการปลดล็อกเสียงค้าง และการปิด context เมื่อออกหน้า ใช้ fixture เฉพาะ unit test
- Browser เสียงใช้ AudioContext, oscillator และ analyser จริง ตรวจสัญญาณเสียง ระดับเสียง ความถี่และเวลาที่ส่งให้เครื่องเสียงจริง ปุ่มทั้งสองสัมพันธ์กัน หยุดเมื่อเปลี่ยนคอร์ด จบเสียงเอง และปิด context เมื่อเปลี่ยนหน้าแบบ SPA
- Browser คอร์ด: เลือกครบ 42 คอร์ดในทั้งสี่หน้าจอหลัก ตรวจ bone signature ตรง baseline, มือแสดง 13/ซ่อน 29, ผัง/สาย/เฟรต/โน้ตตรงต้นฉบับทุกคอร์ด
- Browser UX: ค้นหา แปดตัวกรอง คีย์บอร์ด รายการยอดนิยม จุดบอกนิ้ว เมนูกล้อง ลาก หมุน ซูมสองนิ้วจริงผ่าน touch input และรีเซ็ต
- Browser จำลองปัญหา: ปิดกั้นไฟล์ GLB แล้วลองโหลดใหม่, WebGL context loss และกู้คืน, อุปกรณ์ไม่มี Web Audio พร้อมผังคอร์ดและมือที่ยังใช้งานได้
- Browser regression เดิม 98/98: Catalog, ภาพและรายละเอียด Yamaha, Compare สี่รุ่น, Favorites, แบบทดสอบ และเส้นทางเว็บ/แอดมินในสี่ขนาดหน้าจอ ไม่มี Console Error, runtime error หรือคำขอภาพเสียในเส้นทางปกติ
- Browser ตรวจปลายงาน: เจ็ดขนาดหน้าจอ ปุ่มสัมผัส 44 px, ไม่มีหน้าล้น, focus, Reduced Motion, ภาพ Full Page และหยุด render เมื่อไม่มีการใช้งาน รวมทั้งตรวจเปลี่ยนท่ามือในโหมด motion ปกติ
- Admin data checks เดิม 9/9 รันด้วยข้อมูล fixture และบันทึกรายงานในโฟลเดอร์งานนี้ ไม่แก้ระบบ Admin หรือข้อมูลจริง
- `npm run catalog:check` และ `npm run images:check` ผ่าน: 200 รุ่น/10 แบรนด์/20 รุ่นต่อแบรนด์ ภาพที่ลงทะเบียนเดิม 20 รุ่น และ placeholder เดิม 180 รุ่น ไฟล์ภาพที่มีอยู่ไม่สูญหาย
- โครงการไม่มีสคริปต์ Lint/Typecheck แยกใน package.json

รอบแรกพบ retry ถูกแถบควบคุมบังในกรณีโหลดมือไม่สำเร็จ แก้ CSS และทดสอบลองโหลด GLB จริงอีกครั้งผ่านแล้ว การตรวจเสียงบนมือถือรอบถัดไปพบตัว selector ของสคริปต์เลือกเมนู Desktop ที่ถูกซ่อน แก้สคริปต์ให้กดลิงก์ Footer จริงและตรวจปิด AudioContext เมื่อเปลี่ยนหน้า โดยไม่เปลี่ยนโค้ดเสียงเพื่อให้การทดสอบผ่าน เก็บรายงานก่อนแก้และผลทดสอบซ้ำไว้เพื่อเทียบได้

ข้อจำกัด: ทดสอบ Chromium พร้อมขนาดหน้าจอและ touch input จำลอง ไม่ใช่ iPad Safari บนอุปกรณ์จริง ยังต้องให้เจ้าของทดลองการแตะฟังเสียง/จีบซูมบน iPad การล็อกอิน/บันทึก/Publish ของ Supabase จริงไม่ได้ทดสอบหรือเขียนข้อมูลในงานนี้ และไม่ได้อ้างว่า Hosting/ฐานข้อมูลออนไลน์พร้อมใช้งาน

## ไฟล์โค้ดที่เปลี่ยน

- `src/pages/PracticePage.jsx` — ส่วนประกอบหน้าและการเลือกคอร์ด
- `src/styles/practice-minimal.css` — สไตล์ที่จำกัดขอบเขตเฉพาะ Practice
- `src/features/practice/components/GuitarNeckViewer.jsx` — การจัดโมเดลและเมนูมุมกล้อง
- `src/features/practice/components/PracticeControlBar.jsx` — แถบควบคุมเดียว
- `src/features/practice/components/PracticeIcons.jsx` — ไอคอนในหน้า Practice
- `src/features/practice/scene/createNeckScene.js` — ตัวเลือกมุมกล้องและการซ่อนจุดบอกนิ้วเท่านั้น ไม่แก้กีตาร์/สาย/ตำแหน่งมือ/ประตูตรวจสอบ
- `src/features/practice/audio/chordAudio.js` — เสียงจากโน้ตคอร์ดเดิม
- `src/features/practice/hooks/useChordAudio.js` — ควบคุมเสียงร่วมกันและคืนทรัพยากร
- `scripts/check-practice-audio.mjs`, `scripts/check-practice-minimal.mjs` และโฟลเดอร์เอกสาร/หลักฐานนี้

## เปิดสาธิตบน iPad / Codespaces

เปิด VS Code: https://turbo-fortnight-96wwrvp9jwqjh9px4.github.dev

ถ้า Terminal เดิมกำลังรัน Vite ให้หยุดด้วย Ctrl+C ก่อน หรือกดปุ่มถังขยะของ Terminal แล้วเปิด Terminal ใหม่ จากนั้นวางคำสั่งชุดนี้ คำสั่งจะหยุดเมื่อพบงานที่ยังไม่บันทึก โดยละเว้นเฉพาะแคช `supabase/.temp/` ที่เคยทำให้เปิดเว็บไม่ได้ และไม่ลบหรือแก้แคช/ค่าการเชื่อมต่อใด ๆ

```bash
(
  set -e
  cd /workspaces/fretline
  fretline_pending="$(git status --porcelain -- . ':(exclude)supabase/.temp')"
  if [ -n "$fretline_pending" ]; then
    echo "ยังมีงานอื่นที่ไม่ได้บันทึก หยุดเพื่อรักษางานเดิม"
    printf '%s\n' "$fretline_pending"
    exit 1
  fi
  git fetch origin
  git switch feature/practice-premium-minimal
  git pull --ff-only origin feature/practice-premium-minimal
  git rev-parse --short=7 HEAD
  npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
)
```

ในแท็บ **Ports** เลือกพอร์ต **5173 → Open in Browser** แล้วเปิด `/practice?chord=C`

ลิงก์ Codespaces หลังดึง branch และเริ่มเซิร์ฟเวอร์แล้ว:
https://turbo-fortnight-96wwrvp9jwqjh9px4-5173.app.github.dev/practice?chord=C

อาจต้องล็อกอิน GitHub เพื่อเปิด Preview ตามสิทธิ์ Codespaces ของเจ้าของ การ Push branch ในงานนี้ไม่ได้สั่งเปลี่ยน branch ของ Codespaces เครื่องนั้นให้เอง และไม่ได้เผยแพร่เว็บสาธารณะ

## จุดย้อนกลับ

สำรองก่อนแก้ไว้ที่ tag `backup/practice-before-premium-minimal-fb65ad1` ซึ่งชี้ไป `fb65ad1` และ branch เดิม `feature/restore-black-sleeved-hand` ยังอยู่ครบ

หากต้องการเปิดเปรียบเทียบดีไซน์เดิมโดยไม่เขียนทับงาน ให้สร้าง worktree ใหม่จาก tag นี้แล้วเปิดอีกพอร์ตหนึ่ง:

```bash
git worktree add --detach ../fretline-practice-original backup/practice-before-premium-minimal-fb65ad1
cd ../fretline-practice-original
npm ci
npm run dev -- --host 0.0.0.0 --port 5174 --strictPort
```

ไม่ใช้ reset, clean หรือ force push และไม่มีการย้อนฐานข้อมูล ไม่มี Merge เข้า master หรือ Deploy ในการส่งมอบครั้งนี้
