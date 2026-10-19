import { GUITARS } from './guitars';
import { IMAGES } from './images';
import { slugify } from '@/utils/slug';

/**
 * รายการแบรนด์ "คำนวณจากข้อมูลกีตาร์ชุดเดียวกับ Catalog" — เพิ่มกีตาร์ใหม่แล้วแบรนด์/จำนวนรุ่น/ช่วงราคาอัปเดตเอง
 *
 * ข้อมูลเสริมของแต่ละแบรนด์ (ประเทศที่ตั้ง, ปีก่อตั้ง) แก้ที่ BRAND_INFO ด้านล่าง ไม่ใส่ = ไม่แสดง
 *
 * โลโก้: วางไฟล์ที่ src/assets/brands/<brand-id>.svg (หรือ .webp/.png) เช่น fender.svg, cordoba.svg
 * แนะนำเป็นโลโก้สีขาวพื้นโปร่งใส ตอนนี้ยังไม่มีไฟล์โลโก้ (เป็นเครื่องหมายการค้า ต้องใช้ไฟล์จากแบรนด์เอง)
 * แบรนด์ที่ไม่มีโลโก้จะแสดงเป็นชื่อแบรนด์แบบตัวอักษร
 */
const discovered = import.meta.glob('/src/assets/brands/*.{svg,webp,png}', { eager: true, query: '?url', import: 'default' });
const LOGOS = Object.fromEntries(
  Object.entries(discovered).map(([path, url]) => [path.split('/').pop().replace(/\.[^.]+$/, '').toLowerCase(), url]),
);

// country = ประเทศที่แบรนด์ตั้งอยู่, founded = ปีก่อตั้ง (ใส่เฉพาะที่ยืนยันได้)
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

const grouped = GUITARS.reduce((acc, g) => {
  (acc[g.brand] ??= []).push(g);
  return acc;
}, {});

export const BRANDS = Object.entries(grouped)
  .map(([name, items]) => {
    const id = slugify(name);
    const prices = items.map((g) => g.price).filter((p) => p != null);
    return {
      id,
      name,
      ...BRAND_INFO[id],
      logo: LOGOS[id] ?? null,
      models: items.length,
      categories: [...new Set(items.map((g) => g.category))],
      mainCategory: mostCommon(items.map((g) => g.category)),
      priceMin: prices.length ? Math.min(...prices) : null, // null = ทุกรุ่นของแบรนด์นี้ยังไม่มีราคา
      priceMax: prices.length ? Math.max(...prices) : null,
    };
  })
  .sort((a, b) => b.models - a.models || a.name.localeCompare(b.name));

export const BRANDS_BY_ID = Object.fromEntries(BRANDS.map((b) => [b.id, b]));

/** กีตาร์ของแบรนด์นั้น (แนะนำก่อน แล้วเรียงราคาต่ำ→สูง) */
export const getBrandGuitars = (brandName) =>
  GUITARS.filter((g) => g.brand === brandName).sort((a, b) => Number(b.featured) - Number(a.featured) || (a.price == null) - (b.price == null) || a.price - b.price);

// แบรนด์เด่น 3 ใบใต้ marquee ในหน้าแรก (image: ใส่รูปจริงที่ data/images.js)
export const FEATURED_BRANDS = [
  { id: 'fender', image: IMAGES.brands.fender },
  { id: 'yamaha', image: IMAGES.brands.yamaha },
  { id: 'taylor', image: IMAGES.brands.taylor },
];
