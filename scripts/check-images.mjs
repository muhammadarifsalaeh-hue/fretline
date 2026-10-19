/**
 * ตรวจว่ากีตาร์รุ่นไหนยังไม่มีรูปจริง
 *   npm run images:check           แสดงรายงานในเทอร์มินัล
 *   npm run images:check -- --write   เขียนรายการลง MISSING_IMAGES.md ด้วย
 * รูปต้องวางที่  src/assets/guitars/<guitar-id>/01-front.webp (ดูรายละเอียดใน src/data/guitarImages.js)
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const imagesDir = path.join(root, 'src/assets/guitars');
const exts = /\.(webp|jpe?g|png|avif)$/i;

// รุ่นตัวอย่างใน guitars.js + รุ่นที่นำเข้าใน src/data/catalog/extraGuitars.json
const source = fs.readFileSync(path.join(root, 'src/data/guitars.js'), 'utf8');
const sampleGuitars = [...source.matchAll(/id: '([^']+)',\n\s+brand: '([^']+)',\n\s+name: '((?:[^'\\]|\\.)*)'/g)].map((m) => ({
  id: m[1],
  model: `${m[2]} ${m[3].replace(/\\'/g, "'")}`,
}));
const extraGuitars = JSON.parse(fs.readFileSync(path.join(root, 'src/data/catalog/extraGuitars.json'), 'utf8')).map((g) => ({
  id: g.id,
  model: `${g.brand} ${g.name}`,
}));
const guitars = [...sampleGuitars, ...extraGuitars];

const folders = fs.existsSync(imagesDir)
  ? fs.readdirSync(imagesDir, { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name)
  : [];
const filesOf = (id) => (folders.includes(id) ? fs.readdirSync(path.join(imagesDir, id)).filter((f) => exts.test(f)) : []);

const rows = guitars.map((g) => ({ ...g, files: filesOf(g.id) }));
const missing = rows.filter((r) => r.files.length === 0);
const done = rows.filter((r) => r.files.length > 0);
const unknown = folders.filter((f) => !guitars.some((g) => g.id === f));

console.log(`\nGuitar photos: ${done.length}/${rows.length} models have images\n`);
done.forEach((r) => console.log(`  ✓ ${r.model.padEnd(48)} ${r.files.length} file(s)${r.files.length < 2 ? '  (add more angles for the gallery)' : ''}`));
missing.forEach((r) => console.log(`  ✗ ${r.model.padEnd(48)} src/assets/guitars/${r.id}/`));
if (unknown.length) console.log(`\n  ! Folders that match no guitar id (typo?): ${unknown.join(', ')}`);
console.log('');

if (process.argv.includes('--write')) {
  const lines = [
    '# Missing guitar photos',
    '',
    `${missing.length} of ${rows.length} models still need real photos. Until then the site shows a "Photo coming soon" illustration instead of a photo of a different guitar.`,
    '',
    '## How to add photos',
    '',
    '1. Get photos of **exactly that model** (the manufacturer press kit/product page, a licensed stock photo, or your own photo). Check the licence and keep the credit.',
    '2. Export as **WebP**, about 1600 px on the long side. Best look: guitar cut out on a transparent background, shown whole (the site never crops or stretches it), roughly 4:5 portrait.',
    '3. Put the files in the model folder, numbered in display order:',
    '   - `01-front.webp` is the main photo used on every card',
    '   - more angles are optional: `02-angle.webp`, `03-headstock.webp`, `04-back.webp`, `05-pickups.webp` ...',
    '4. Run `npm run images:check` to confirm. No code changes needed.',
    '',
    '## Models without photos',
    '',
    '| Model | Folder (`src/assets/guitars/…`) | Needed files |',
    '|---|---|---|',
    ...missing.map((r) => `| ${r.model} | \`${r.id}/\` | \`01-front.webp\` (+ 2–4 more angles) |`),
    '',
    ...(done.length ? ['## Models with photos', '', ...done.map((r) => `- ${r.model} (${r.files.length} file(s))`), ''] : []),
  ];
  fs.writeFileSync(path.join(root, 'MISSING_IMAGES.md'), lines.join('\n'));
  console.log('Wrote MISSING_IMAGES.md\n');
}
