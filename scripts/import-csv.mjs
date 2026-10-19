/**
 * นำเข้ากีตาร์จากไฟล์ CSV (export จาก Excel/Google Sheets) เข้า src/data/catalog/extraGuitars.json
 *   npm run catalog:import -- data-template/guitars-template.csv
 *   npm run catalog:import -- my.csv --dry-run     # ตรวจอย่างเดียว ไม่เขียนไฟล์
 * - status: sample | partial (ตรวจบางส่วน ช่องว่าง = ไม่ทราบ) | verified (ครบ + มีราคา) | example (ถูกข้าม)
 * - price_thb ว่าง = Price on request (ไม่เดาและไม่แปลงสกุลเงิน)
 * - แถวที่ status = example ถูกข้าม (แถวตัวอย่างในแม่แบบ)
 * - ถ้ามีแถวผิดรูปแบบหรือซ้ำกับรุ่นที่มีอยู่ จะไม่นำเข้าอะไรเลย (all-or-nothing) และบอกว่าแถวไหนผิดเพราะอะไร
 */
import fs from 'node:fs';
import { EXTRA_PATH, findDuplicates, readExtras, readSampleGuitars, slugify, validateGuitar } from './lib/catalog.mjs';

const file = process.argv.slice(2).find((a) => !a.startsWith('--'));
const dry = process.argv.includes('--dry-run');
if (!file) {
  console.error('Usage: npm run catalog:import -- <file.csv> [--dry-run]');
  process.exit(2);
}

/** CSV parser: รองรับเครื่องหมายคำพูด, ขึ้นบรรทัดใหม่ในช่อง, CRLF และ BOM */
export function parseCsv(text) {
  const rows = [];
  let row = [];
  let cell = '';
  let quoted = false;
  const src = text.replace(/^\uFEFF/, '');
  for (let i = 0; i < src.length; i++) {
    const c = src[i];
    if (quoted) {
      if (c === '"' && src[i + 1] === '"') { cell += '"'; i++; }
      else if (c === '"') quoted = false;
      else cell += c;
    } else if (c === '"') quoted = true;
    else if (c === ',') { row.push(cell); cell = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && src[i + 1] === '\n') i++;
      row.push(cell); cell = '';
      if (row.some((x) => x.trim() !== '')) rows.push(row);
      row = [];
    } else cell += c;
  }
  row.push(cell);
  if (row.some((x) => x.trim() !== '')) rows.push(row);
  return rows;
}

const num = (v) => (v === '' || v == null ? null : Number(String(v).replace(/,/g, '')));
const text = (v) => (v?.trim() ? v.trim() : null); // ช่องว่าง = ไม่ทราบ (null) ไม่เดาค่า
const list = (v) => (v ? v.split(';').map((x) => x.trim()).filter(Boolean) : []);

export function rowToGuitar(r) {
  const brand = r.brand?.trim();
  const name = r.model?.trim();
  return {
    id: slugify(`${brand} ${name}`),
    brand,
    name,
    category: r.category?.trim().toLowerCase(),
    price: num(r.price_thb), // ว่าง = null = Price on request
    oldPrice: num(r.old_price_thb) ?? undefined,
    badge: r.badge?.trim().toUpperCase() || undefined,
    featured: /^(true|yes|1)$/i.test(r.featured ?? ''),
    tags: list(r.tags),
    keywords: r.keywords?.trim() || undefined,
    description: r.description?.trim(),
    colors: list(r.colors).map((c) => {
      const [n, hex] = c.split('|').map((x) => x?.trim());
      return { name: n, hex: hex || null }; // ไม่มี hex = แสดงเป็นสีกลาง ไม่เดาโทนสี
    }),
    specs: {
      body: text(r.body),
      neck: text(r.neck),
      fretboard: text(r.fingerboard),
      pickups: text(r.pickups),
      bridge: text(r.bridge),
      controls: text(r.controls),
      scale: num(r.scale_in),
      frets: num(r.frets),
      strings: num(r.strings),
      weightKg: num(r.weight_kg),
    },
    profile: r.levels || r.styles ? { levels: list(r.levels), styles: list(r.styles) } : undefined,
    status: (r.status?.trim().toLowerCase() || 'sample'),
    source: r.source_url ? { url: r.source_url.trim(), note: r.source_note?.trim() || '', verifiedOn: r.verified_on?.trim() } : null,
  };
}

const [header, ...body] = parseCsv(fs.readFileSync(file, 'utf8'));
const records = body
  .map((cells, i) => ({ line: i + 2, obj: Object.fromEntries(header.map((h, j) => [h.trim(), cells[j] ?? ''])) }))
  .filter(({ obj }) => (obj.status ?? '').trim().toLowerCase() !== 'example');

const existing = readExtras();
const incoming = [];
let problems = 0;
for (const { line, obj } of records) {
  const g = rowToGuitar(obj);
  const errs = validateGuitar(g);
  if (errs.length) {
    problems += errs.length;
    console.log(`✗ line ${line} (${g.brand ?? '?'} ${g.name ?? '?'})`);
    errs.forEach((m) => console.log(`    - ${m}`));
  }
  incoming.push(g);
}
const dups = findDuplicates([...readSampleGuitars(), ...existing, ...incoming]);
dups.forEach((m) => { problems++; console.log(`✗ ${m}`); });

if (problems) {
  console.log(`\nImport cancelled: ${problems} problem(s). Nothing was written.\n`);
  process.exit(1);
}
console.log(`\n${incoming.length} record(s) OK${dry ? ' (dry run, nothing written)' : ''}.`);
if (!dry) {
  fs.writeFileSync(EXTRA_PATH, JSON.stringify([...existing, ...incoming], null, 2) + '\n');
  console.log(`Wrote ${existing.length + incoming.length} record(s) to src/data/catalog/extraGuitars.json\n`);
}
