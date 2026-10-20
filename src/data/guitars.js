import EXTRA_GUITARS from './catalog/extraGuitars.json';
import REVIEWED_GUITARS from './catalog/reviewedGuitars.json';
import PHASE7_GUITARS from './catalog/phase7Guitars.json';
import CATALOG_POLICY from './catalog/catalogPolicy.json';
import { getGuitarImages } from './guitarImages';
import { trustedPrice } from '@/utils/dataTrust';

/**
 * Legacy demo records are retained for their stable IDs and editorial order.
 * Their prices, reviews, colors and specifications are NOT public catalog data.
 * Reviewed manufacturer records below replace them before any page receives data.
 */
const raw = [
  {
    id: 'fender-american-professional-ii-stratocaster',
    brand: 'Fender',
    name: 'American Professional II Stratocaster',
    category: 'electric',
    price: 69900,
    badge: 'NEW',
    featured: true,
    tags: ['SSS', 'Alder', '22 Frets'],
    keywords: 'left-handed stratocaster',
    specs: { body: 'Alder', neck: 'Maple', fretboard: 'Rosewood', pickups: '3 × V-Mod II single-coil', scale: 25.5, frets: 22, weightKg: 3.6, strings: 6 },
  },
  {
    id: 'gibson-les-paul-standard-60s',
    brand: 'Gibson',
    name: 'Les Paul Standard 60s',
    category: 'electric',
    price: 115000,
    badge: null,
    featured: true,
    tags: ['HH', 'Mahogany', '22 Frets'],
    keywords: 'les paul',
    specs: { body: 'Mahogany, maple cap', neck: 'Mahogany', fretboard: 'Rosewood', pickups: '2 × Burstbucker humbucker', scale: 24.75, frets: 22, weightKg: 4.1, strings: 6 },
  },
  {
    id: 'ibanez-rg550-genesis',
    brand: 'Ibanez',
    name: 'RG550 Genesis',
    category: 'electric',
    price: 38900,
    oldPrice: 42900,
    badge: 'SALE',
    featured: true,
    tags: ['HSH', 'Basswood', '24 Frets'],
    keywords: '',
    specs: { body: 'Basswood', neck: 'Maple', fretboard: 'Maple', pickups: 'Humbucker + single + humbucker', scale: 25.5, frets: 24, weightKg: 3.3, strings: 6 },
  },
  {
    id: 'yamaha-pacifica-612viifm',
    brand: 'Yamaha',
    name: 'Pacifica 612VIIFM',
    category: 'electric',
    price: 17900,
    badge: null,
    featured: true,
    tags: ['HSS', 'Alder', '22 Frets'],
    keywords: 'beginner under ฿20,000 left-handed',
    specs: { body: 'Alder, flame maple top', neck: 'Maple', fretboard: 'Rosewood', pickups: 'Humbucker + 2 single-coil', scale: 25.5, frets: 22, weightKg: 3.5, strings: 6 },
  },
  {
    id: 'prs-se-custom-24',
    brand: 'PRS',
    name: 'SE Custom 24',
    category: 'electric',
    price: 32900,
    badge: 'NEW',
    featured: false,
    tags: ['HH', 'Mahogany', '24 Frets'],
    keywords: '',
    specs: { body: 'Mahogany, maple top', neck: 'Maple', fretboard: 'Rosewood', pickups: '2 × PRS 85/15 humbucker', scale: 25, frets: 24, weightKg: 3.4, strings: 6 },
  },
  {
    id: 'epiphone-casino',
    brand: 'Epiphone',
    name: 'Casino Hollowbody',
    category: 'electric',
    price: 24900,
    badge: null,
    featured: false,
    tags: ['P-90', 'Maple', 'Hollow'],
    keywords: '',
    specs: { body: 'Laminated maple', neck: 'Mahogany', fretboard: 'Laurel', pickups: '2 × P-90 single-coil', scale: 24.75, frets: 22, weightKg: 3.5, strings: 6 },
  },
  {
    id: 'taylor-214ce',
    brand: 'Taylor',
    name: '214ce Grand Auditorium',
    category: 'acoustic',
    price: 48900,
    badge: 'LIMITED',
    featured: true,
    tags: ['Spruce top', 'Cutaway', 'ES2'],
    keywords: '',
    specs: { body: 'Layered rosewood, spruce top', neck: 'Sapele', fretboard: 'Ebony', pickups: 'Taylor ES2 pickup', scale: 25.5, frets: 20, weightKg: 1.9, strings: 6 },
  },
  {
    id: 'martin-d-18',
    brand: 'Martin',
    name: 'D-18 Dreadnought',
    category: 'acoustic',
    price: 118000,
    badge: null,
    featured: true,
    tags: ['Solid spruce', 'Mahogany', 'Dreadnought'],
    keywords: '',
    specs: { body: 'Solid mahogany, spruce top', neck: 'Select hardwood', fretboard: 'Ebony', pickups: 'None (acoustic)', scale: 25.4, frets: 20, weightKg: 2.0, strings: 6 },
  },
  {
    id: 'yamaha-fg800',
    brand: 'Yamaha',
    name: 'FG800 Dreadnought',
    category: 'acoustic',
    price: 8900,
    badge: null,
    featured: true,
    tags: ['Solid spruce', 'Nato', 'Beginner'],
    keywords: 'beginner under ฿20,000 left-handed',
    specs: { body: 'Nato, solid spruce top', neck: 'Nato', fretboard: 'Rosewood', pickups: 'None (acoustic)', scale: 25.6, frets: 20, weightKg: 2.0, strings: 6 },
  },
  {
    id: 'cordoba-c5',
    brand: 'Córdoba',
    name: 'C5 Classical',
    category: 'classical',
    price: 9900,
    badge: null,
    featured: true,
    tags: ['Nylon', 'Cedar top', 'Classical'],
    keywords: 'beginner under ฿20,000 nylon',
    specs: { body: 'Mahogany, cedar top', neck: 'Mahogany', fretboard: 'Rosewood', pickups: 'None (acoustic)', scale: 25.6, frets: 19, weightKg: 1.4, strings: 6 },
  },
  {
    id: 'fender-player-ii-jazz-bass',
    brand: 'Fender',
    name: 'Player II Jazz Bass',
    category: 'bass',
    price: 31900,
    badge: 'NEW',
    featured: true,
    tags: ['JJ', 'Alder', '34" Scale'],
    keywords: 'bass',
    specs: { body: 'Alder', neck: 'Maple', fretboard: 'Maple', pickups: '2 × split-coil single', scale: 34, frets: 20, weightKg: 4.2, strings: 4 },
  },
  {
    id: 'ibanez-sr300e',
    brand: 'Ibanez',
    name: 'SR300E Bass',
    category: 'bass',
    price: 15900,
    badge: null,
    featured: false,
    tags: ['PJ', 'Mahogany', '34" Scale'],
    keywords: 'bass beginner under ฿20,000',
    specs: { body: 'Mahogany', neck: 'Jatoba', fretboard: 'Purpleheart', pickups: 'Precision + Jazz', scale: 34, frets: 24, weightKg: 3.9, strings: 4 },
  },
  {
    id: 'squier-classic-vibe-60s-stratocaster',
    brand: 'Squier',
    name: 'Classic Vibe \'60s Stratocaster',
    category: 'electric',
    price: 18900,
    badge: null,
    featured: false,
    tags: ['SSS', 'Poplar', '21 Frets'],
    keywords: 'beginner under ฿20,000 left-handed stratocaster',
    specs: { body: 'Poplar', neck: 'Maple', fretboard: 'Laurel', pickups: '3 × Alnico single-coil', scale: 25.5, frets: 21, weightKg: 3.5, strings: 6 },
  },
  {
    id: 'gretsch-g2420-streamliner',
    brand: 'Gretsch',
    name: 'G2420 Streamliner Hollow Body',
    category: 'electric',
    price: 27900,
    badge: 'NEW',
    featured: false,
    tags: ['HH', 'Laminated maple', 'Hollow'],
    keywords: '',
    specs: { body: 'Laminated maple', neck: 'Nato', fretboard: 'Laurel', pickups: '2 × Broad\'Tron humbucker', scale: 25.5, frets: 22, weightKg: 3.3, strings: 6 },
  },
  {
    id: 'epiphone-les-paul-standard-50s',
    brand: 'Epiphone',
    name: 'Les Paul Standard 50s',
    category: 'electric',
    price: 22900,
    badge: null,
    featured: false,
    tags: ['HH', 'Mahogany', '22 Frets'],
    keywords: 'les paul',
    specs: { body: 'Mahogany, maple top', neck: 'Mahogany', fretboard: 'Laurel', pickups: '2 × ProBucker humbucker', scale: 24.75, frets: 22, weightKg: 4.0, strings: 6 },
  },
  {
    id: 'taylor-gs-mini',
    brand: 'Taylor',
    name: 'GS Mini Mahogany',
    category: 'acoustic',
    price: 28900,
    badge: null,
    featured: false,
    tags: ['Solid spruce', 'Travel size', 'Mahogany'],
    keywords: 'travel',
    specs: { body: 'Layered sapele, spruce top', neck: 'Sapele', fretboard: 'Ebony', pickups: 'None (acoustic)', scale: 23.5, frets: 20, weightKg: 1.5, strings: 6 },
  },
  {
    id: 'yamaha-c40',
    brand: 'Yamaha',
    name: 'C40 Classical',
    category: 'classical',
    price: 5900,
    badge: null,
    featured: false,
    tags: ['Nylon', 'Spruce top', 'Beginner'],
    keywords: 'beginner under ฿20,000 nylon',
    specs: { body: 'Meranti, spruce top', neck: 'Nato', fretboard: 'Rosewood', pickups: 'None (acoustic)', scale: 25.6, frets: 18, weightKg: 1.3, strings: 6 },
  },
  {
    id: 'fender-player-precision-bass',
    brand: 'Fender',
    name: 'Player II Precision Bass',
    category: 'bass',
    price: 33900,
    badge: null,
    featured: false,
    tags: ['P', 'Alder', '34" Scale'],
    keywords: 'bass',
    specs: { body: 'Alder', neck: 'Maple', fretboard: 'Maple', pickups: 'Split-coil Precision', scale: 34, frets: 20, weightKg: 4.3, strings: 4 },
  },
];

/**
 * รายการกีตาร์ = 18 รุ่นตัวอย่างด้านบน + รุ่นที่เพิ่มผ่าน src/data/catalog/extraGuitars.json
 * (เพิ่มข้อมูลเป็นร้อยรุ่นได้โดยไม่ต้องแก้โค้ด — ดู docs/ADDING_GUITARS.md)
 *
 * dataStatus: 'sample'   = ข้อมูลตัวอย่างที่ยังไม่ได้ตรวจกับแหล่งจริง
 *             'partial'  = ตรวจกับแหล่งทางการบางส่วน (ช่องที่ไม่ทราบเป็น null, ราคาอาจเป็น null = Price on request)
 *             'verified' = ตรวจครบกับแหล่งทางการ และมี source.url / source.verifiedOn
 */
const withImages = (g) => {
  const reviewed = REVIEWED_GUITARS[g.id];
  const record = reviewed ?? g;
  const sourceFields = new Set(record.source?.fields ?? []);
  const specs = Object.fromEntries(['body', 'neck', 'fretboard', 'pickups', 'bridge', 'controls', 'scale', 'scaleMm', 'frets', 'strings', 'weightKg']
    .map((key) => [key, sourceFields.has(`specs.${key}`) ? record.specs?.[key] ?? null : null]));
  const publicRecord = {
    ...g, ...reviewed, id: g.id,
    price: sourceFields.has('price') ? trustedPrice({ ...record, dataStatus: record.status ?? record.dataStatus }) : null,
    oldPrice: null, rating: null, badge: null,
    colors: sourceFields.has('colors') ? record.colors ?? [] : [],
    tags: sourceFields.has('tags') ? record.tags ?? [] : [],
    description: sourceFields.has('description') ? record.description ?? '' : '',
    keywords: [g.id, g.brand, g.name, record.name, sourceFields.has('keywords') ? record.keywords : ''].filter(Boolean).join(' '),
    specs, source: record.source ?? null,
    dataStatus: record.source?.fields?.length ? record.status ?? record.dataStatus ?? 'partial' : 'sample',
  };
  const gallery = getGuitarImages(g.id).gallery;
  // รูปหลัก: null = ยังไม่มีรูปจริงของรุ่นนี้ (UI จะแสดงภาพประกอบ ไม่ใช้รูปรุ่นอื่นแทน)
  return { ...publicRecord, slug: g.id, image: gallery[0]?.src ?? null, gallery, hasPhotos: gallery.length > 0 };
};

const sampleGuitars = raw.map(withImages);

const extraGuitars = EXTRA_GUITARS.map((e) =>
  withImages({
    id: e.id,
    brand: e.brand,
    name: e.name,
    category: e.category,
    price: e.price ?? null, // null = Price on request
    oldPrice: e.oldPrice,
    badge: e.badge ?? null,
    featured: Boolean(e.featured),
    tags: e.tags ?? [],
    keywords: e.keywords ?? '',
    description: e.description ?? '',
    colors: e.colors ?? [],
    rating: e.rating ?? null,
    profile: e.profile, // โปรไฟล์สำหรับ Quiz (ไม่บังคับ)
    specs: { body: null, neck: null, fretboard: null, pickups: null, bridge: null, controls: null, scale: null, frets: null, strings: null, weightKg: null, ...e.specs },
    source: e.source ?? null,
    dataStatus: e.status ?? 'sample',
  }),
);

const archivedIds = new Set(CATALOG_POLICY.archivedIds);
const originalGuitars = [...sampleGuitars, ...extraGuitars];
// Only this collection feeds catalog, brand totals, search and quiz recommendations.
export const GUITARS = [...originalGuitars, ...PHASE7_GUITARS.map(withImages)].filter((guitar) => !archivedIds.has(guitar.id));

export const GUITARS_BY_ID = Object.assign(Object.create(null), Object.fromEntries(GUITARS.map((g) => [g.id, g])));

// Old detail URLs and user-owned selections resolve archive records without
// adding them back to the main catalog or changing saved IDs silently.
// Full backups (including audit snapshots) stay outside the browser bundle.
export const ARCHIVED_GUITARS = originalGuitars.filter((guitar) => archivedIds.has(guitar.id)).map((guitar) => ({ ...guitar, featured: false, archived: true }));
export const SAVED_GUITARS_BY_ID = Object.assign(Object.create(null), GUITARS_BY_ID, Object.fromEntries(ARCHIVED_GUITARS.map((guitar) => [guitar.id, guitar])));
