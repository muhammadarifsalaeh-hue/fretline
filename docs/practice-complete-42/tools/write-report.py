"""Generate delivery tables from completed evidence, never from solver success."""
import csv, hashlib, io, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/practice-complete-42'
def read(name):
    return json.loads((OUT / name).read_text())

geometry = read('tests/geometry/summary.json')
visual = read('tests/visual-review.json')
browser = read('tests/browser-practice.json')
public = read('tests/public-smoke.json')
safety = read('tests/data-safety.json')
imported = read('tests/import-reviewed.json')
inventory = read('tests/candidate-inventory.json')
captures = read('tests/captures-final.json')
assert geometry['testSuitePassed'] and browser['passed'] and safety['passed']
assert all(c['passed'] for c in public['checks'])
runtime_sha = hashlib.sha256((ROOT / 'src/features/practice/assets/hand-poses.json').read_bytes()).hexdigest()
assert geometry['librarySnapshotSha256'] == imported['runtimeLibrarySHA256'] == runtime_sha
vrows = {r['id']: r for r in visual['rows']}
research = {r['id']: r for r in inventory}
allowed = set(safety['displayableHands'])
assert len(allowed) == visual['technicalVisualPassed'] == geometry['geometricPassed']

def problems(row):
    reasons = []
    if row['skinAndClothSelfCrossingPairs']:
        reasons.append('เมชมือ/แขนเสื้อชนกัน')
    if row['guitar'].get('crossingPairs'):
        reasons.append('เมชมือชนคอ/เฟรต/สาย')
    if row['woodSamplesInsideOver002Mm']:
        reasons.append('ผิวมือทะลุเนื้อไม้')
    if any(not c['passed'] for c in row.get('contacts', [])):
        reasons.append('ตำแหน่งสัมผัสสายยังไม่ผ่าน')
    if any(s.get('openStringPassed') is False for s in row.get('strings', [])):
        reasons.append('นิ้วกีดขวางสายเปิด')
    if any(not c['passed'] for c in row.get('barreCoverage', [])):
        reasons.append('ช่วงนิ้วทาบยังไม่ผ่าน')
    return ' / '.join(reasons) or 'ยังไม่ผ่านเกณฑ์เมชและการสัมผัสสายครบทุกข้อ'

table = ['| คอร์ด | ผังคอร์ด/ข้อมูลเดิม | เมชจริงในระบบ | ตรวจภาพจริง 4 มุม | ต้องแก้เพิ่ม |',
         '| --- | --- | --- | --- | --- |']
csv_rows = []
for row in geometry['rows']:
    key = row['id']; vr = vrows[key]
    assert vr['actualFourViewRendersInspected'] and len(vr['views']) == 4
    for view in vr['views']:
        assert hashlib.sha256((ROOT / view['file']).read_bytes()).hexdigest() == view['imageSHA256']
    good = key in allowed
    reason = '—' if good else problems(research[key]['row'])
    table.append(f'| {key} | ผ่าน | {"ผ่าน" if good else "ไม่ผ่าน"} | {"ผ่านเชิงเทคนิค" if good else "ตรวจแล้ว ไม่ผ่าน"} | {reason} |')
    csv_rows.append(dict(chord=key, canonicalDataUnchanged=True, runtimeGeometryPassed=good,
                         actualFourViewsInspected=True, technicalVisualPassed=good,
                         independentInstructorCertified=False, needsFurtherCorrection=not good,
                         candidateAudit=research[key]['audit'], reason=reason))
(OUT / 'chord-results.json').write_text(json.dumps(csv_rows, ensure_ascii=False, indent=2) + '\n')
stream = io.StringIO(); writer = csv.DictWriter(stream, fieldnames=list(csv_rows[0]), lineterminator='\n'); writer.writeheader(); writer.writerows(csv_rows)
(OUT / 'chord-results.csv').write_text(stream.getvalue(), encoding='utf-8-sig')
missing = ', '.join(r['chord'] for r in csv_rows if r['needsFurtherCorrection'])
new = imported['newDisplayHands']; total = len(allowed)
text = f'''# ผลพัฒนาท่ามือ 3D FRETLINE

**ยังไม่ครบ 42 ท่ามือที่ถูกต้อง**: เปิดแสดงท่ามือที่ผ่านการตรวจเมชจริงและภาพเรนเดอร์เชิงเทคนิคได้ {total}/42 คอร์ด เพิ่ม {new} จากฐานเดิม 13 คอร์ด อีก {42-total} คอร์ดคือ **{missing}** ยังคงใช้ผังคอร์ดเดิมแทนมือที่ไม่ผ่าน ไม่ลบคอร์ดและไม่เปลี่ยนข้อมูลเสียง/สาย/เฟรต/นิ้ว

ตรวจภาพ GLB จริงครบ 42 คอร์ด × 4 มุม = 168 ภาพ รวมท่าที่ถูกปฏิเสธเพื่อวินิจฉัย ไม่ใช้ภาพนิ่งแทนโมเดลบนหน้าเว็บ จำนวนผู้สอนอิสระที่รับรองท่ามือในงานนี้ = **0**; การผ่านตัวเลข การตรวจภาพเชิงเทคนิค และการรับรองโดยผู้สอนเป็นคนละสถานะ ไม่มีการเปลี่ยน `reviewed`, `anatomyPassed` หรือสถานะ `verified` ให้เป็นจริงเพื่อให้ผ่านงาน

## สิ่งที่เปลี่ยน

- ปรับตำแหน่งกระดูกและนิ้วโป้งของโมเดลมือเสื้อดำต้นฉบับ โดยคง GLB เดิมทุกไบต์
- เพิ่มจุดกดสายต่อท่ามือภายในเฟรตเดิม เพื่อให้วางนิ้วเหลื่อมกันได้ตามรูปทรงมือ โดยไม่เปลี่ยนเลขสาย เฟรต นิ้ว หรือระดับเสียง
- นิ้วที่กดเฟรตสูงกว่าเป็นผู้กดสายที่เกิดเสียง ส่วนนิ้วทาบมีการตรวจช่วงที่พาดอยู่ใต้สายเหล่านั้นแยกต่างหาก
- แผนจุดกดสายที่ไม่ครบ ผิดสาย ผิดเฟรต หรือเกินช่วงเฟรตถูกปฏิเสธ ท่ามือที่ไม่ผ่านยังคงซ่อน
- ระบบเดิมในการเปลี่ยนคอร์ด หมุน ซูม รีเซ็ต เสียงและความเร็ว การแสดงจุดนิ้ว และ Reduced Motion ยังคงอยู่ ไม่แก้ Layout/CSS ของ Practice Studio

ท่ามือเดิม 13 คอร์ดคงกระดูกนิ้วกดสายและ Root เหมือนเดิมทุกค่า ยกเว้นการซ่อมเฉพาะนิ้วโป้งของ B7, Gmaj7 และ Dsus2 ซึ่งเดิมลอยห่างจากหลังคอ ขณะนี้ตรวจการรองรับจากผิวโมเดลจริงแล้ว

## ผลตรวจ 42 คอร์ด

คำว่า “ผังคอร์ด/ข้อมูลเดิมผ่าน” หมายถึงการตรวจความสอดคล้องของข้อมูลเดิมด้วยสคริปต์ ไม่ใช่การรับรองใหม่โดยครูกีตาร์ ช่องภาพตรวจจากโมเดลจริง; ภาพที่ไม่ผ่านไม่ปรากฏเป็นท่ามือบนหน้าเว็บ

{chr(10).join(table)}

ตารางแบบเครื่องอ่าน: [CSV](chord-results.csv) · [JSON](chord-results.json)

## เกณฑ์ตรวจและหลักฐาน

- ตรวจ FK/LBS จาก Rig และน้ำหนัก Vertex เดิม เทียบผิวมือ/แขนเสื้อกับ Triangle ของคอ เฟรต และสายที่ Export จากโค้ดแสดงผลจริง ไม่ใช้เพียง Marker หรือชื่อคอร์ดเป็นหลักฐาน
- มือกับกีตาร์และมือกับตัวเองต้องไม่มี Triangle crossing; Dense wood sampling ต้องไม่ทะลุเกิน 0.02 mm; การสัมผัสสายของผิวนิ้วที่กำหนดต้องอยู่ในช่วง 0–0.12 mm; สายเปิดต้องมีระยะว่างอย่างน้อย 0.2 mm
- นิ้วโป้งต้องมีพยานผิวหลังคอจริงไม่เกิน 0.8 mm; มุม PIP ≤115° / DIP ≤90° เป็นเพียงเกณฑ์เรขาคณิต ไม่ใช่การรับรองชีวกลศาสตร์
- ตรวจทิศผิวนิ้วที่กดจากด้านเหนือสายจริงครบ {total} ท่า เกณฑ์ตรวจ Triangle เดิมไม่ได้ถูกผ่อนปรน
- Runtime pose SHA-256: `{runtime_sha}`
- [เมชครบ 42](tests/geometry/summary.json) · [ภาพที่ตรวจด้วยตา](tests/visual-review.json) · [แรงกดเหนือสาย](tests/pressure-direction/summary.json) · [รายการต้นแบบและผลที่ไม่ผ่าน](tests/candidate-inventory.json)

ภาพทุกคอร์ด: [ภาพด้านหน้า](screenshots/final/sheet-front-1.jpg) · [ชุดที่ 2](screenshots/final/sheet-front-2.jpg) · [ชุดที่ 3](screenshots/final/sheet-front-3.jpg) และไฟล์ `screenshots/final/{{chord}}-{{front,side,back,player}}.png` ภาพวินิจฉัยในโฟลเดอร์นี้รวมต้นแบบที่ถูกปฏิเสธด้วย

## ผลทดสอบ

- Production Build ผ่าน; Vite เตือน Three.js chunk >500 kB ซึ่งแยกโหลดเฉพาะหน้า Practice อยู่แล้ว ไม่มี Dependency ใหม่
- [Practice Browser](tests/browser-practice.json): {len(browser['checks'])} ชุดทดสอบ ผ่านทั้งหมด ตรวจท่ามือจริงและ Diagram ทั้ง 42 คอร์ดบน Desktop, iPad แนวนอน/ตั้ง และ Mobile รวมปุ่ม คีย์บอร์ด หมุน ซูม สองนิ้ว เสียงจริง ความเร็ว การเปลี่ยนคอร์ด การโหลดโมเดลล้มเหลวและกู้คืน WebGL
- [ระบบผู้เข้าชม](tests/public-smoke.json): {len(public['checks'])} ชุด ผ่าน Catalog/Search/Yamaha/Detail/Compare/Favorites/Brands/แบบทดสอบ 5 ข้อ/ทางเข้า Admin แบบไม่ล็อกอิน
- Console และ Runtime Error ในเส้นทางใช้งานปกติ = 0; การทดสอบจำลองข้อผิดพลาดแยก Context ต่างหาก
- Audio unit 7, Pressure unit 8, ตัวเลือกข้อมูลผิด 21, JS/Python geometry parity 42, Practice data 56 และ Hand runtime 21: ดู [บันทึกคำสั่ง](tests/verification.json)
- ทดสอบด้วย Chromium และ Touch simulation เท่านั้น **ยังไม่ได้ทดสอบบน iPad Safari เครื่องจริง** และไม่ใช้ตัวเลขจาก Software renderer อ้าง Performance ของเครื่องจริง
- ทดสอบหน้า Admin แบบผู้เยี่ยมชมและตรวจ Source เดิม ไม่ได้ล็อกอิน อัปโหลด Publish หรือเขียนฐานข้อมูล Supabase ในงานนี้

## ข้อมูลและขอบเขตที่รักษาไว้

ตรวจเทียบฐาน `1f2836b875dc02f667c002093534f592cd1a0141`: กีตาร์ 200 ID / 10 แบรนด์ / แบรนด์ละ 20 รุ่น / 42 คอร์ดครบ ข้อมูล ชื่อ ราคา สเปก รูปภาพและความสัมพันธ์เหมือนเดิมทุกค่า ไม่แก้ Home, Admin, Authentication, Compare, Find My Guitar, Database, SQL หรือ .env

ภาพสินค้าเดิมไม่ได้ครบ 200 ภาพ: มีภาพที่ลงทะเบียน 20 รุ่น และ Placeholder เดิม 180 รุ่น ไม่มีการสร้างหรือแทนภาพสินค้าในงานนี้ ดู [หลักฐานข้อมูล](tests/data-safety.json)

ไฟล์ Source ที่แก้มีเพียง `hand-poses.json`, `pressureContacts.js`, `frettedStrings.js`, `handPoseEngine.js`, `createNeckScene.js` ใน `src/features/practice/` และ `scripts/check-hand-runtime.mjs`; ที่เหลือในโฟลเดอร์นี้เป็นเครื่องมือทดสอบ หลักฐาน และรายงาน

## เปิดสาธิตบน Codespaces / iPad

Branch: `feature/practice-complete-42-poses` ไม่มี Merge master และไม่มี Deploy

เปิด Terminal ที่ `/workspaces/fretline` หยุด Vite ตัวเก่าด้วย Ctrl+C ก่อน จากนั้นใช้คำสั่งแบบรักษางานค้างนี้ (ข้ามเฉพาะ Supabase CLI temporary cache; ไม่ลบหรือ Stash งาน)

```bash
(
  set -e
  cd /workspaces/fretline
  pending="$(git status --porcelain -- . ':(exclude)supabase/.temp')"
  if [ -n "$pending" ]; then
    echo "มีงานค้าง กรุณาบันทึกงานก่อนเปลี่ยน Branch"
    git status --short
    exit 1
  fi
  git fetch origin
  git switch feature/practice-complete-42-poses
  git pull --ff-only origin feature/practice-complete-42-poses
  git rev-parse --short HEAD
  npm ci
  npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
)
```

ใน Codespaces เลือกแท็บ **Ports → 5173 → Open in Browser** แล้วเปิด `/practice?chord=C` เลือกคอร์ดหรือแตะรายการยอดนิยม ปัดหมุนและใช้สองนิ้วซูม เปิดเสียงด้วยการแตะปุ่มครั้งแรกบน Safari

ลิงก์เดิมของ Codespace (จะเป็นรุ่นใหม่นี้เมื่อ Pull และเริ่ม Vite จาก Branch ข้างบนแล้ว): https://turbo-fortnight-96wwrvp9jwqjh9px4-5173.app.github.dev/practice?chord=C

## รันตรวจซ้ำ / ย้อนกลับ

`npm ci` แล้ว `npm run build`, `npm run practice:check`, `node scripts/check-hand-runtime.mjs` สำหรับการตรวจเมชติดตั้ง NumPy/SciPy และใช้ `OPENBLAS_NUM_THREADS=1 python docs/practice-complete-42/tools/audit-all.py` เครื่องมือ Browser ใช้ Python Playwright กับ Chromium (`/usr/bin/chromium`) และ Production preview ที่พอร์ต 4198

สำรองต้นแบบและผลวิจัยไว้ใน [Archive](evidence/authoring-evidence.tar.xz) พร้อม [SHA-256 manifest](evidence/manifest.json) แตกจาก Root repo เพื่อคืน `.local-preview/practice-complete-42/`; [Review library](evidence/review-library.json) ใช้ตรวจภาพจริงซ้ำกับ `tools/inspector.html` ไม่ถูกนำเข้า Production build

จุดย้อนกลับ: tag `backup/practice-before-all42-1f2836b` เพื่อดูเวอร์ชันเดิมอย่างปลอดภัยโดยไม่ Reset หรือทับงานปัจจุบัน ใช้ Worktree แยก: `git worktree add ../fretline-before-all42 backup/practice-before-all42-1f2836b` ส่วน Branch งานนี้ยังอยู่ครบ Master คง SHA `9f7b35d7a0daea8a579976a5534ffb67d90f06a9`
'''
(OUT / 'README.md').write_text(text)
print(json.dumps({'hands': total, 'new': new, 'needsCorrection': missing, 'rows': len(csv_rows), 'all42Complete': total == 42}))
