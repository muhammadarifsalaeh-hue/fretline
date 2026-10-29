import { isSourceBacked, verifiedRating, hasManufacturerRrp, trustedPrice } from '@/utils/dataTrust';
import { ADDITIONAL_SPECIFICATIONS } from '@/data/additionalSpecifications';
import { LANG, t } from '@/i18n';
import { formatScale, scaleInMillimetres, formatKg, formatPrice } from '@/utils/format';

// Compare's missing-data label is local; product/detail wording remains unchanged.
const NOT_SPECIFIED = LANG === 'en' ? 'No data' : 'ไม่มีข้อมูล';

/**
 * นิยามแถวของตารางเปรียบเทียบ — เพิ่ม/ลบ/เรียงแถวที่นี่ที่เดียว (แถวกลุ่มเดียวกันต้องอยู่ติดกัน)
 *  group       : หัวข้อกลุ่ม
 *  raw         : ค่าที่ใช้เทียบ (null = ไม่ทราบ) ถ้าเท่ากันทุกตัว = แถว "เหมือนกัน"
 *  display     : ข้อความที่แสดง (ไม่ใส่ = ใช้ raw, null แสดง "ไม่มีข้อมูล")
 *  best        : 'min' | 'max' = ค่าที่ดีที่สุดจะมีจุดสีทอง (ต้องมีค่าที่ทราบอย่างน้อย 2 รุ่น)
 *  note        : ข้อความเล็กใต้ค่า เช่น ส่วนต่างจากรุ่นที่ถูกที่สุด
 *  hideIfEmpty : ซ่อนทั้งแถวถ้าไม่มีข้อมูลเลย (เช่น ยังไม่มีรีวิว)
 */
const known = (list) => list.filter((value) => typeof value === 'number' && Number.isFinite(value));
const requiredOptionalKeys = new Set(['bodyShape', 'top', 'back', 'sides', 'electronics']);
const numericKeys = new Set(['price', 'rating', 'scale', 'frets', 'strings', 'weight']);
const positiveNumber = (value) => typeof value === 'number' && Number.isFinite(value) && value > 0 ? value : null;
const cleanScale = (specs) => ({ scaleMm: positiveNumber(specs?.scaleMm), scale: positiveNumber(specs?.scale) });
const normalizeValue = (value, row) => {
  if (value == null) return null;
  if ((numericKeys.has(row.key) || row.numeric) && typeof value !== 'number') return null;
  if (typeof value === 'string') return value.trim() || null;
  if (typeof value !== 'number' || !Number.isFinite(value)) return null;
  if (row.key === 'frets') return Number.isInteger(value) && value >= 0 ? value : null;
  if (row.key === 'strings') return Number.isInteger(value) && value > 0 ? value : null;
  if (row.key === 'rating') return value >= 0 ? value : null;
  return value > 0 ? value : null;
};
const comparisonValue = (value) => typeof value === 'string'
  ? value.normalize('NFKC').replace(/\s+/gu, ' ').toLocaleLowerCase('en') : value;
const optionalRows = (group) => ADDITIONAL_SPECIFICATIONS.filter((field) => field.group === group).map((field) => ({
  key: field.key, group: t(`group.${group}`), label: t(field.label), raw: (g) => g.specs?.[field.key] ?? null,
  numeric: field.type === 'number',
  display: (_g, value) => `${value}${field.unit ?? ''}`, hideIfEmpty: !requiredOptionalKeys.has(field.key),
}));

export const COMPARE_ROWS = [
  { key: 'brand', group: t('group.overview'), label: t('p4.compare.brand'), raw: (g) => g.brand, identity: true },
  { key: 'model', group: t('group.overview'), label: t('cmp.model'), raw: (g) => g.name, identity: true },
  { key: 'type', group: t('group.overview'), label: t('filter.type'), raw: (g) => g.category, display: (g) => t(`category.${g.category}`), identity: true },
  {
    key: 'price',
    group: t('group.overview'),
    label: t('row.price'),
    raw: (g) => g.price ?? null,
    display: (g, value) => `${formatPrice(value)}${value != null && hasManufacturerRrp(g) ? ` · ${t('pricing.rrpShort')}` : ''}`,
    best: 'min',
    note: (g, all) => {
      if (g.price == null) return null;
      const prices = known(all.map((x) => x.price));
      if (prices.length < 2) return null;
      const min = Math.min(...prices);
      return g.price > min ? `+${formatPrice(g.price - min)}` : t('note.lowestPrice');
    },
  },
  {
    key: 'rating',
    group: t('group.overview'),
    label: t('row.rating'),
    raw: (g) => verifiedRating(g)?.score ?? null,
    display: (g) => (verifiedRating(g) ? `★ ${verifiedRating(g).score.toFixed(1)} (${verifiedRating(g).count})` : t('rating.none')),
    best: 'max',
    hideIfEmpty: true,
  },
  { key: 'body', group: t('group.construction'), label: t('row.body'), raw: (g) => g.specs?.body ?? null },
  { key: 'neck', group: t('group.construction'), label: t('row.neck'), raw: (g) => g.specs?.neck ?? null },
  { key: 'fretboard', group: t('group.construction'), label: t('row.fingerboard'), raw: (g) => g.specs?.fretboard ?? null },
  { key: 'scale', group: t('group.construction'), label: t('row.scale'), raw: (g) => scaleInMillimetres(cleanScale(g.specs)), display: (g) => formatScale(cleanScale(g.specs)) },
  { key: 'frets', group: t('group.construction'), label: t('row.frets'), raw: (g) => g.specs?.frets ?? null },
  { key: 'strings', group: t('group.construction'), label: t('row.strings'), raw: (g) => g.specs?.strings ?? null },
  ...optionalRows('construction'),
  { key: 'pickups', group: t('group.electronics'), label: t('row.pickups'), raw: (g) => g.specs?.pickups ?? null },
  { key: 'bridge', group: t('group.electronics'), label: t('row.bridge'), raw: (g) => g.specs?.bridge ?? null },
  { key: 'controls', group: t('group.electronics'), label: t('row.controls'), raw: (g) => g.specs?.controls ?? null },
  ...optionalRows('electronics'),
  {
    key: 'weight',
    group: t('group.details'),
    label: t('row.weight'),
    raw: (g) => g.specs?.weightKg ?? null,
    display: (_g, value) => formatKg(value),
    best: 'min',
    note: (g, all) => {
      if (g.specs.weightKg == null) return null;
      const weights = known(all.map((x) => x.specs.weightKg));
      if (weights.length < 2) return null;
      const diff = g.specs.weightKg - Math.min(...weights);
      return diff > 0.001 ? `+${diff.toFixed(1)} kg` : t('note.lightest');
    },
  },
  ...optionalRows('details'),
];

export { NOT_SPECIFIED };

/**
 * วิเคราะห์แต่ละแถว
 *  diff  = ค่าต่างกัน (ไฮไลต์) | same = เหมือนกันทุกรุ่น | empty = ไม่ทราบทุกรุ่น (ไม่ใช่ "เหมือนกัน")
 *  best  = ค่าที่ดีที่สุด (ถ้ามี)
 */
export function analyseRows(guitars, { includeSamples = true, includeIdentity = true } = {}) {
  return COMPARE_ROWS.filter((row) => includeIdentity || !row.identity).map((row) => {
    const allowed = (g) => row.identity || row.key === 'rating' || includeSamples || isSourceBacked(g);
    const valueOf = (g) => !allowed(g) ? null : normalizeValue(row.key === 'price' && !includeSamples ? trustedPrice(g) : row.raw(g), row);
    const displayOf = (g) => {
      const value = valueOf(g);
      // A missing/untrusted price is a request for a quote, never a spec placeholder.
      if (row.key === 'price') return row.display(g, value);
      if (!allowed(g)) return t('data.unverified');
      return value == null ? NOT_SPECIFIED : row.display ? row.display(g, value) : value;
    };
    const values = guitars.map(valueOf);
    const confirmed = values.filter((value) => value != null).map(comparisonValue);
    const empty = confirmed.length === 0;
    const incomplete = confirmed.length < values.length;
    const same = !empty && !incomplete && confirmed.every((value) => value === confirmed[0]);
    // Missing evidence is not a proven physical difference between instruments.
    const diff = new Set(confirmed).size >= 2;
    const nums = known(values);
    let best = null;
    if (row.best && diff && nums.length >= 2) best = row.best === 'min' ? Math.min(...nums) : Math.max(...nums);
    return { row, same, empty, incomplete, diff, best, valueOf, displayOf, allowed };
  }).filter((r) => !(r.row.hideIfEmpty && r.empty));
}

/** จัดแถวเป็นกลุ่มตามลำดับที่ปรากฏ */
export function groupRows(analysed) {
  return analysed.reduce((acc, item) => {
    const last = acc[acc.length - 1];
    if (last && last.title === item.row.group) last.rows.push(item);
    else acc.push({ title: item.row.group, rows: [item] });
    return acc;
  }, []);
}
