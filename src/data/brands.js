import { GUITARS } from './guitars';
import { IMAGES } from './images';
import { slugify } from '@/utils/slug';
import { isSourceBacked, trustedPrice } from '@/utils/dataTrust';

/**
 * รายการแบรนด์ "คำนวณจากข้อมูลกีตาร์ชุดเดียวกับ Catalog" — เพิ่มกีตาร์ใหม่แล้วแบรนด์/จำนวนรุ่น/ช่วงราคาอัปเดตเอง
 *
 * BRAND_INFO is legacy, unsourced metadata. Brand pages do not use it as a biography.
 *
 * โลโก้: วางไฟล์ที่ src/assets/brands/<brand-id>.svg (หรือ .webp/.png) เช่น fender.svg, cordoba.svg
 * ต้องบันทึกสิทธิ์การใช้ไฟล์ก่อนเพิ่มโลโก้ ตอนนี้ยังไม่มีไฟล์โลโก้ที่ได้รับอนุญาต
 * แบรนด์ที่ไม่มีโลโก้จะแสดงเป็นชื่อแบรนด์แบบตัวอักษร
 */
const discovered = import.meta.glob('/src/assets/brands/*.{svg,webp,png}', { eager: true, query: '?url', import: 'default' });
const LOGOS = Object.fromEntries(
  Object.entries(discovered).map(([path, url]) => [path.split('/').pop().replace(/\.[^.]+$/, '').toLowerCase(), url]),
);

// Legacy metadata has no recorded sources. Keep it for the existing country
// filter, explicitly marked unverified; never use it as a verified biography.
const BRAND_INFO = {
  fender: { country: 'USA', founded: 1946 },
  gibson: { country: 'USA', founded: 1902 },
  ibanez: { country: 'Japan', founded: 1957 },
  yamaha: { country: 'Japan', founded: 1887 },
  taylor: { country: 'USA', founded: 1974 },
  martin: { country: 'USA', founded: 1833 },
  prs: { country: 'USA', founded: 1985 },
  epiphone: { country: 'USA', founded: 1873 },
  gretsch: { country: 'USA', founded: 1883 },
  cordoba: { country: 'USA' },
  squier: { country: 'USA' },
};

const mostCommon = (list) => {
  const counts = list.reduce((acc, x) => ({ ...acc, [x]: (acc[x] || 0) + 1 }), {});
  return Object.keys(counts).sort((a, b) => counts[b] - counts[a])[0];
};

/** Counts describe this catalog only. Sample prices never define a range. */
export function buildBrands(guitars, info = BRAND_INFO, logos = LOGOS) {
  const grouped = guitars.reduce((acc, g) => {
    (acc[g.brand] ??= []).push(g);
    return acc;
  }, Object.create(null));
  return Object.entries(grouped)
  .map(([name, items]) => {
    const id = slugify(name);
    const prices = items.map(trustedPrice).filter((p) => p != null);
    return {
      id,
      name,
      ...info[id],
      metadataStatus: 'unverified',
      logo: logos[id] ?? null,
      models: items.length,
      categories: [...new Set(items.map((g) => g.category))],
      mainCategory: mostCommon(items.map((g) => g.category)),
      sourceModels: items.filter(isSourceBacked).length,
      pricedModels: prices.length,
      priceMin: prices.length ? Math.min(...prices) : null, // null = ทุกรุ่นของแบรนด์นี้ยังไม่มีราคา
      priceMax: prices.length ? Math.max(...prices) : null,
    };
  })
  .sort((a, b) => b.models - a.models || a.name.localeCompare(b.name));
}

export const BRANDS = buildBrands(GUITARS);

export const BRANDS_BY_ID = Object.fromEntries(BRANDS.map((b) => [b.id, b]));
export const getBrandById = (id = '') => {
  const key = id.toLowerCase();
  return Object.prototype.hasOwnProperty.call(BRANDS_BY_ID, key) ? BRANDS_BY_ID[key] : null;
};

/** กีตาร์ของแบรนด์นั้น (แนะนำก่อน แล้วเรียงราคาต่ำ→สูง) */
export const getBrandGuitars = (brandName) =>
  GUITARS.filter((g) => g.brand === brandName).sort((a, b) => Number(b.featured) - Number(a.featured) || (trustedPrice(a) == null) - (trustedPrice(b) == null) || trustedPrice(a) - trustedPrice(b));

// แบรนด์เด่น 3 ใบใต้ marquee ในหน้าแรก (image: ใส่รูปจริงที่ data/images.js)
export const FEATURED_BRANDS = [
  { id: 'fender', image: IMAGES.brands.fender },
  { id: 'yamaha', image: IMAGES.brands.yamaha },
  { id: 'taylor', image: IMAGES.brands.taylor },
];
