import { t } from '@/i18n';
import IMAGE_RIGHTS from './catalog/imageRights.json';
import PROJECT_ARTWORK from './catalog/projectArtwork.json';
import { hasImageRights } from '@/utils/imageRights';
/**
 * รูปกีตาร์รายรุ่น — ระบบนี้ "ไม่มีรูปสุ่ม" ถ้ารุ่นไหนยังไม่มีรูปจริงจะแสดงภาพ "Photo coming soon"
 *
 * วิธีเพิ่มรูปที่ตรวจสอบรุ่นและสิทธิ์แล้ว:
 *   วางไฟล์ที่  src/assets/guitars/<guitar-id>/NN-ชื่อมุม.webp
 *   เช่น       src/assets/guitars/fender-player-ii-jazz-bass/01-front.webp
 *                                                            /02-headstock.webp
 *   - <guitar-id> ต้องตรงกับ `id` ใน data/guitars.js (ดูรายการใน MISSING_IMAGES.md)
 *   - ไฟล์ที่เลขนำหน้าน้อยที่สุด (01-...) = รูปหลักที่ใช้ในการ์ดทุกหน้า
 *   - ชื่อมุมที่รู้จัก: front back side angle headstock body neck pickups bridge detail
 *   - ลงทะเบียนแหล่งที่มา สิทธิ์ ผู้ถ่าย และหลักฐานตรงรุ่นใน data/catalog/imageRights.json
 *   - ภาพผู้ใช้ที่ขอให้นำมาใช้ในโครงงานลงทะเบียนแยกใน projectArtwork.json
 *     โดยเก็บที่มาไว้และไม่อ้างว่าเป็นภาพที่ตรวจสอบสิทธิ์หรือภาพผู้ผลิต
 *   - ตรวจว่ารุ่นไหนยังขาด:  npm run images:check
 *
 * ทางเลือก: ใช้ URL ภายนอกผ่าน IMAGE_OVERRIDES ด้านล่าง (เฉพาะรูปที่ตรวจแล้วว่าตรงรุ่นและมีสิทธิ์ใช้)
 */

// Vite รวบรวมไฟล์ในโฟลเดอร์ให้อัตโนมัติ (ไฟล์ preview แบบรวมไฟล์เดียวจะแทนที่บรรทัดนี้เป็น {})
const discovered = import.meta.glob('/src/assets/guitars/*/*.{webp,jpg,jpeg,png,avif}', { eager: true, query: '?url', import: 'default' });
const responsive = import.meta.glob('/src/assets/guitars/*/responsive/*.webp', { eager: true, query: '?url', import: 'default' });

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
 * รูปจาก URL ภายนอก (ไม่บังคับ) — ต้องมี attribution ตามโครงสร้าง imageRights.json
 * และผ่าน hasImageRights เช่นเดียวกับไฟล์ในโปรเจกต์
 */
export const IMAGE_OVERRIDES = {};

/**
 * สรุปเครดิตจากทะเบียนสิทธิ์ ใช้ข้อมูลเดียวกันใน Detail, Lightbox และ Image Credits
 */
export const IMAGE_CREDITS = Object.fromEntries(Object.entries(IMAGE_RIGHTS).map(([id, photos]) => [id, photos.map((photo) => `${photo.author} · ${photo.license}`).join(', ')]));

/** คืน { primary, gallery, hasPhotos } ของกีตาร์ id นั้น — ไม่มีรูป = primary เป็น null และ gallery ว่าง */
export function getGuitarImages(id) {
  const fromFiles = (found[id] ?? []).flatMap(({ file, src }) => {
    const artwork = PROJECT_ARTWORK[id];
    const illustration = artwork?.images.find((entry) => entry.file === file);
    if (illustration) return [{ ...illustration, src, provenance: artwork }];
    const rights = IMAGE_RIGHTS[id]?.find((entry) => entry.file === file);
    if (!hasImageRights(rights, id)) return [];
    const variants = (rights.variants ?? []).flatMap((entry) => {
      const url = responsive[`/src/assets/guitars/${id}/${entry.file}`];
      return url ? [`${url} ${entry.width}w`] : [];
    });
    return [{ src, label: rights.label ?? labelFrom(file), credit: IMAGE_CREDITS[id], attribution: rights,
      alt: rights.alt, width: rights.width, height: rights.height,
      srcSet: [...variants, `${src} ${rights.width}w`].join(', ') }];
  });
  const overrides = (IMAGE_OVERRIDES[id] ?? []).filter((photo) => hasImageRights(photo.attribution, id));
  const gallery = overrides.length ? overrides : fromFiles;
  return { primary: gallery[0]?.src ?? null, gallery, hasPhotos: gallery.length > 0 };
}
