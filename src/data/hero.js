import { t } from '@/i18n';
import { IMAGES } from './images';

/**
 * ค่าของ Hero
 * - image: null = ใช้ภาพเส้นร่างใน HeroArt | ใส่รูปจริงใน data/images.js เพื่อใช้รูปถ่ายแทน
 * - hotspots: x,y = ตำแหน่ง % บนรูปถ่าย | art = พิกัดบนเส้นร่าง | ตั้ง showHotspots เป็น false เพื่อปิด
 *   (ข้อความเป็นคำอธิบายส่วนประกอบทั่วไป ไม่ใช่สเปกของรุ่นใด)
 * - ตัวเลขสถิติคำนวณจากข้อมูลจริงใน components/home/HeroStats.jsx
 */
export const HERO = {
  image: IMAGES.hero,
  imageAlt: t('hero.imageAlt'),
  showHotspots: false,
  hotspots: [
    { id: 'neck', x: 34, y: 36, art: [95, 96], title: t('hotspot.neck'), detail: t('hotspot.neckDetail') },
    { id: 'pickups', x: 56, y: 52, art: [95, 201], title: t('hotspot.pickups'), detail: t('hotspot.pickupsDetail') },
    { id: 'bridge', x: 68, y: 63, art: [95, 231], title: t('hotspot.bridge'), detail: t('hotspot.bridgeDetail') },
  ],
};
