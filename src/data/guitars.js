import { DETAILS, RATINGS } from './guitarDetails';
import EXTRA_GUITARS from './catalog/extraGuitars.json';
import { getGuitarImages } from './guitarImages';

/**
 * ข้อมูลกีตาร์ตัวอย่าง (ราคาเป็นบาท, เป็นข้อมูลสมมติเพื่อการสาธิต)
 * ภายหลังเปลี่ยนเป็นข้อมูลจาก API / Database ได้ โดยคง shape เดิมไว้
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
  const gallery = g.gallery ?? getGuitarImages(g.id).gallery;
  // รูปหลัก: null = ยังไม่มีรูปจริงของรุ่นนี้ (UI จะแสดงภาพประกอบ ไม่ใช้รูปรุ่นอื่นแทน)
  return { ...g, slug: g.id, image: gallery[0]?.src ?? null, gallery, hasPhotos: gallery.length > 0 };
};

const sampleGuitars = raw.map((g) => {
  const d = DETAILS[g.id] ?? {};
  return withImages({
    ...g,
    gallery: d.gallery,
    description: d.description ?? '',
    colors: d.colors ?? [],
    rating: RATINGS[g.id] ?? null,
    specs: { ...g.specs, bridge: d.bridge ?? '-', controls: d.controls ?? '-' },
    source: null,
    dataStatus: 'sample',
  });
});

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

export const GUITARS = [...sampleGuitars, ...extraGuitars];

export const GUITARS_BY_ID = Object.fromEntries(GUITARS.map((g) => [g.id, g]));
