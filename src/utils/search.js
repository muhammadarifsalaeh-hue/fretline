import { GUITARS } from '@/data/guitars';
import { BRANDS } from '@/data/brands';
import { CATEGORIES } from '@/data/categories';
import { t } from '@/i18n';
import { formatPrice } from './format';
import { brandUrl, categoryUrl, guitarUrl } from './routes';

export function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// คำค้นภาษาไทยที่ใช้บ่อย → คำที่อยู่ในข้อมูล (ข้อมูลรุ่น/แท็กเป็นภาษาอังกฤษ)
const ALIASES = {
  ผู้เริ่มต้น: 'beginner',
  มือใหม่: 'beginner',
  มือซ้าย: 'left-handed',
  กีตาร์โปร่ง: 'acoustic',
  อะคูสติก: 'acoustic',
  กีตาร์ไฟฟ้า: 'electric',
  ไฟฟ้า: 'electric',
  กีตาร์เบส: 'bass',
  เบส: 'bass',
  คลาสสิก: 'classical',
  กีตาร์คลาสสิก: 'classical',
  สายไนลอน: 'nylon',
};

// Fold Latin accents without stripping Thai vowels or tone marks. This also
// makes manufacturer punctuation variants (D–18 / D-18) searchable consistently.
export const normalizeSearchText = (value) => String(value ?? '')
  .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  .toLowerCase().replace(/[\u2010-\u2015\u2212]/g, '-');

const searchFields = new WeakMap();
function fieldsFor(guitar) {
  let fields = searchFields.get(guitar);
  if (!fields) {
    const haystack = normalizeSearchText([guitar.brand, guitar.name, guitar.category, guitar.keywords, ...(guitar.tags ?? [])].join(' '));
    fields = {
      haystack,
      words: new Set(haystack.split(/[^a-z0-9฿-]+/).filter(Boolean)),
      model: normalizeSearchText(`${guitar.brand} ${guitar.name}`).replace(/[^a-z0-9]/g, ''),
    };
    searchFields.set(guitar, fields);
  }
  return fields;
}

/** กีตาร์ตรงกับคำค้นไหม — ทุกคำที่พิมพ์ต้องเจอใน แบรนด์/ชื่อ/ประเภท/แท็ก/คีย์เวิร์ด */
export function matchesQuery(guitar, query) {
  const q = normalizeSearchText(query).trim();
  if (!q) return true;
  const { haystack, words, model } = fieldsFor(guitar);
  return q.split(/\s+/).every((word) => {
    // คำไทยที่แปลงเป็นศัพท์ (เช่น เบส → bass) ต้องตรงทั้งคำ ไม่ใช่จับกลางคำ (กัน "Basswood" โผล่เมื่อค้นหาเบส)
    const alias = ALIASES[word];
    if (alias) return words.has(alias);
    // คำที่พิมพ์เอง: จับบางส่วนได้ (เช่น fg8 → FG800)
    if (haystack.includes(word)) return true;
    // Model punctuation is optional, while arbitrary metadata still uses the
    // literal query. Do not turn a punctuation-only query into a match-all.
    const compact = word.replace(/[^a-z0-9]/g, '');
    return compact.length > 0 && /^[a-z0-9-]+$/.test(word) && model.includes(compact);
  });
}

/**
 * ผลลัพธ์ autocomplete แบบแบ่งกลุ่ม: [{ title, items: [{ key, label, meta, image, href }] }]
 * ตอนมี backend ให้เปลี่ยนเป็นเรียก API แทน แต่คง shape ผลลัพธ์ไว้
 */
export function searchCatalog(query) {
  const q = normalizeSearchText(query).trim();
  if (!q) return [];
  const qa = ALIASES[q] ?? q; // เช่น พิมพ์ "เบส" → ค้นหา bass ด้วย
  const has = (text) => normalizeSearchText(text).includes(q) || normalizeSearchText(text).includes(qa);

  const guitars = GUITARS.filter((g) => matchesQuery(g, query))
    .slice(0, 4)
    .map((g) => ({
      key: `g-${g.id}`,
      label: `${g.brand} ${g.name}`,
      meta: formatPrice(g.price),
      guitar: g,
      href: guitarUrl(g.slug),
    }));

  const brands = BRANDS.filter((b) => has(b.name))
    .slice(0, 3)
    .map((b) => ({ key: `b-${b.id}`, label: b.name, meta: t('unit.models', { n: b.models }), href: brandUrl(b.name) }));

  const categories = CATEGORIES.filter((c) => has(c.name) || has(c.id))
    .slice(0, 3)
    .map((c) => ({ key: `c-${c.id}`, label: t('search.categoryLabel', { name: c.name }), meta: t('unit.models', { n: c.count }), href: categoryUrl(c.id) }));

  return [
    { title: t('search.groupGuitars'), items: guitars },
    { title: t('search.groupBrands'), items: brands },
    { title: t('search.groupCategories'), items: categories },
  ].filter((group) => group.items.length > 0);
}
