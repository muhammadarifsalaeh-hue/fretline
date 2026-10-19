/** ฟังก์ชันร่วมของสคริปต์ตรวจ/นำเข้าข้อมูลกีตาร์ */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
export const EXTRA_PATH = path.join(ROOT, 'src/data/catalog/extraGuitars.json');
export const CATEGORIES = ['electric', 'acoustic', 'classical', 'bass'];
// sample = ตัวอย่างยังไม่ตรวจ | partial = ตรวจกับแหล่งทางการบางส่วน (ช่องที่ไม่ทราบเป็น null) | verified = ตรวจครบ + มีราคา
export const STATUSES = ['sample', 'partial', 'verified'];
export const TARGET_DEFAULT = 200;

export const slugify = (t) =>
  String(t).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
// ใช้เทียบรายการซ้ำ: "Fender" + "Player II Jazz Bass" เท่ากับ "fender player ii jazz bass" ไม่สนช่องว่าง/เครื่องหมาย
export const dupKey = (brand, name) => slugify(`${brand} ${name}`).replace(/-/g, '');

/** รุ่นตัวอย่าง 18 รุ่นเดิมใน src/data/guitars.js (อ่านด้วย regex ไม่ต้อง import) */
export function readSampleGuitars() {
  const src = fs.readFileSync(path.join(ROOT, 'src/data/guitars.js'), 'utf8');
  return [...src.matchAll(/id: '([^']+)',\n\s+brand: '([^']+)',\n\s+name: '((?:[^'\\]|\\.)*)'/g)].map((m) => ({
    id: m[1],
    brand: m[2],
    name: m[3].replace(/\\'/g, "'"),
    status: 'sample',
  }));
}

export const readExtras = () => JSON.parse(fs.readFileSync(EXTRA_PATH, 'utf8'));

const nonEmpty = (v) => typeof v === 'string' && v.trim().length > 0;
const positive = (v) => typeof v === 'number' && Number.isFinite(v) && v > 0;

/** ตรวจ 1 รายการ คืน array ของข้อความ error (ว่าง = ผ่าน) */
export function validateGuitar(g) {
  const e = [];
  const partial = g.status === 'partial';
  const optionalText = (k) => g.specs?.[k] == null || nonEmpty(g.specs[k]);
  const optionalNum = (k) => g.specs?.[k] == null || positive(g.specs[k]);

  if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(g.id ?? '')) e.push('id ต้องเป็นตัวพิมพ์เล็ก/ตัวเลข/ขีดกลาง');
  if (!nonEmpty(g.brand)) e.push('ไม่มี brand');
  if (!nonEmpty(g.name)) e.push('ไม่มีชื่อรุ่น (name)');
  if (!CATEGORIES.includes(g.category)) e.push(`category ต้องเป็น ${CATEGORIES.join('/')}`);
  if (!STATUSES.includes(g.status)) e.push(`status ต้องเป็น ${STATUSES.join('/')}`);

  // ราคา: ไม่ทราบ (null) ได้เฉพาะ sample/partial — verified ต้องมีราคาจากแหล่งที่ตรวจสอบได้
  if (g.price == null) {
    if (g.status === 'verified') e.push('verified ต้องมีราคา (ถ้ายืนยันราคาไม่ได้ ให้ใช้ status = partial)');
  } else if (!Number.isInteger(g.price) || g.price <= 0) e.push('price (บาท) ต้องเป็นจำนวนเต็มมากกว่า 0 หรือเว้นว่าง (Price on request)');
  if (g.oldPrice != null && !(Number.isInteger(g.oldPrice) && g.price != null && g.oldPrice > g.price)) e.push('oldPrice ต้องมากกว่า price');
  if (!nonEmpty(g.description)) e.push('ไม่มี description');

  const s = g.specs ?? {};
  if (partial) {
    // partial: ช่องที่ไม่ทราบเว้นว่างได้ แต่ถ้าใส่ต้องถูกรูปแบบ และต้องมี body อย่างน้อย
    if (!nonEmpty(s.body)) e.push('specs.body ว่าง (partial ต้องมี body อย่างน้อย)');
    for (const k of ['neck', 'fretboard', 'pickups', 'bridge', 'controls']) if (!optionalText(k)) e.push(`specs.${k} ต้องเป็นข้อความหรือเว้นว่าง`);
    for (const k of ['scale', 'frets', 'strings', 'weightKg']) if (!optionalNum(k)) e.push(`specs.${k} ต้องเป็นตัวเลขมากกว่า 0 หรือเว้นว่าง`);
  } else {
    for (const k of ['body', 'neck', 'fretboard', 'pickups', 'bridge', 'controls']) if (!nonEmpty(s[k])) e.push(`specs.${k} ว่าง`);
    for (const k of ['scale', 'frets', 'strings', 'weightKg']) if (!positive(s[k])) e.push(`specs.${k} ต้องเป็นตัวเลขมากกว่า 0`);
  }

  if (!Array.isArray(g.colors)) e.push('colors ต้องเป็น array');
  else {
    if (!partial && g.colors.length === 0) e.push('ต้องมี colors อย่างน้อย 1 สี');
    g.colors.forEach((c, i) => !nonEmpty(c.name) && e.push(`colors[${i}] ต้องมี name (hex ไม่บังคับ)`));
  }

  if (g.status === 'verified' || partial) {
    if (!/^https:\/\//.test(g.source?.url ?? '')) e.push(`${g.status} ต้องมี source.url (https://…) ที่เป็นแหล่งทางการ`);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(g.source?.verifiedOn ?? '')) e.push(`${g.status} ต้องมี source.verifiedOn รูปแบบ YYYY-MM-DD`);
  }
  return e;
}

/** หารายการซ้ำ (id ซ้ำ หรือ brand+ชื่อรุ่นซ้ำ) ในรายการรวม คืน array ของข้อความ */
export function findDuplicates(all) {
  const out = [];
  const ids = new Map();
  const keys = new Map();
  for (const g of all) {
    if (ids.has(g.id)) out.push(`id ซ้ำ: ${g.id}`);
    ids.set(g.id, true);
    const k = dupKey(g.brand, g.name);
    if (keys.has(k)) out.push(`รุ่นซ้ำ: "${g.brand} ${g.name}" ซ้ำกับ "${keys.get(k)}"`);
    else keys.set(k, `${g.brand} ${g.name}`);
  }
  return out;
}

export function photoStats(ids) {
  const dir = path.join(ROOT, 'src/assets/guitars');
  const has = (id) => fs.existsSync(path.join(dir, id)) && fs.readdirSync(path.join(dir, id)).some((f) => /\.(webp|jpe?g|png|avif)$/i.test(f));
  const withPhotos = ids.filter(has);
  return { withPhotos: withPhotos.length, placeholders: ids.length - withPhotos.length };
}
