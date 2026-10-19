import { t } from '@/i18n';
/**
 * รูปกีตาร์รายรุ่น — ระบบนี้ "ไม่มีรูปสุ่ม" ถ้ารุ่นไหนยังไม่มีรูปจริงจะแสดงภาพ "Photo coming soon"
 *
 * วิธีเพิ่มรูป (ไม่ต้องแก้โค้ด):
 *   วางไฟล์ที่  src/assets/guitars/<guitar-id>/NN-ชื่อมุม.webp
 *   เช่น       src/assets/guitars/fender-player-ii-jazz-bass/01-front.webp
 *                                                            /02-headstock.webp
 *   - <guitar-id> ต้องตรงกับ `id` ใน data/guitars.js (ดูรายการใน MISSING_IMAGES.md)
 *   - ไฟล์ที่เลขนำหน้าน้อยที่สุด (01-...) = รูปหลักที่ใช้ในการ์ดทุกหน้า
 *   - ชื่อมุมที่รู้จัก: front back side angle headstock body neck pickups bridge detail
 *   - ตรวจว่ารุ่นไหนยังขาด:  npm run images:check
 *
 * ทางเลือก: ใช้ URL ภายนอกผ่าน IMAGE_OVERRIDES ด้านล่าง (เฉพาะรูปที่ตรวจแล้วว่าตรงรุ่นและมีสิทธิ์ใช้)
 */

// Vite รวบรวมไฟล์ในโฟลเดอร์ให้อัตโนมัติ (ไฟล์ preview แบบรวมไฟล์เดียวจะแทนที่บรรทัดนี้เป็น {})
const discovered = import.meta.glob('/src/assets/guitars/*/*.{webp,jpg,jpeg,png,avif}', { eager: true, query: '?url', import: 'default' });

const ANGLE_LABELS = {
  front: t('angle.front'),
  back: t('angle.back'),
  side: t('angle.side'),
  angle: t('angle.angle'),
  headstock: t('angle.headstock'),
  body: t('angle.body'),
  neck: t('angle.neck'),
  pickups: t('angle.pickups'),
  bridge: t('angle.bridge'),
  detail: t('angle.detail'),
};

const labelFrom = (file) => {
  const base = file.replace(/\.[^.]+$/, '').replace(/^\d+[-_]?/, '').toLowerCase();
  if (!base) return t('angle.photo');
  return ANGLE_LABELS[base] ?? base.replace(/[-_]+/g, ' ').replace(/^./, (c) => c.toUpperCase());
};

const found = {};
for (const [path, url] of Object.entries(discovered)) {
  const m = path.match(/\/assets\/guitars\/([^/]+)\/([^/]+)$/);
  if (!m) continue;
  (found[m[1]] ??= []).push({ file: m[2], src: url });
}
Object.values(found).forEach((list) => list.sort((a, b) => a.file.localeCompare(b.file, undefined, { numeric: true })));

/**
 * รูปจาก URL ภายนอก (ไม่บังคับ) — ใส่ credit ทุกครั้งถ้าไลเซนส์ต้องการ
 *   'guitar-id': [{ src: 'https://...', label: 'Front view', credit: 'Photo: ชื่อผู้ถ่าย, CC BY 4.0' }]
 * ต้องเป็นรูปของรุ่นนั้นจริง ๆ เท่านั้น
 */
export const IMAGE_OVERRIDES = {};

/**
 * เครดิตของรูปในโฟลเดอร์ src/assets/guitars/<id>/ (ใส่เมื่อไลเซนส์ต้องการ เช่น CC BY / CC BY-SA)
 *   'guitar-id': 'Photo: ชื่อผู้ถ่าย, CC BY-SA 4.0, via Wikimedia Commons'
 * จะแสดงใต้รูปในหน้า Detail และใน Lightbox
 */
export const IMAGE_CREDITS = {};

/** คืน { primary, gallery, hasPhotos } ของกีตาร์ id นั้น — ไม่มีรูป = primary เป็น null และ gallery ว่าง */
export function getGuitarImages(id) {
  const fromFiles = (found[id] ?? []).map(({ file, src }) => ({ src, label: labelFrom(file), credit: IMAGE_CREDITS[id] }));
  const gallery = IMAGE_OVERRIDES[id]?.length ? IMAGE_OVERRIDES[id] : fromFiles;
  return { primary: gallery[0]?.src ?? null, gallery, hasPhotos: gallery.length > 0 };
}
