import { HERO } from '@/data/hero';
import GuitarArt from '@/components/ui/GuitarArt';
import HeroHotspot from './HeroHotspot';

const ANGLE = -24; // องศาที่เอียงเส้นร่าง
const VIEW = { w: 190, h: 250 }; // ต้องตรงกับ viewBox ใน GuitarArt

/** แปลงพิกัดบนเส้นร่าง (หน่วย viewBox) เป็น % ของกรอบ หลังหมุนแล้ว เพื่อวาง hotspot ให้ตรงตำแหน่งจริง */
function rotatedPercent([x, y]) {
  const t = (ANGLE * Math.PI) / 180;
  const dx = x - VIEW.w / 2;
  const dy = y - VIEW.h / 2;
  return {
    x: ((VIEW.w / 2 + dx * Math.cos(t) - dy * Math.sin(t)) / VIEW.w) * 100,
    y: ((VIEW.h / 2 + dx * Math.sin(t) + dy * Math.cos(t)) / VIEW.h) * 100,
  };
}

/**
 * ภาพประกอบเส้นร่างกีตาร์ไฟฟ้าใน Hero (ใช้เมื่อ HERO.image เป็น null)
 * hotspot เป็นคำอธิบายส่วนประกอบทั่วไป ไม่ใช่สเปกของรุ่นใดรุ่นหนึ่ง
 */
export default function HeroArt() {
  return (
    <div className="absolute inset-0 grid place-items-center">
      <div className="relative h-[92%] max-h-[820px]" style={{ aspectRatio: `${VIEW.w} / ${VIEW.h}` }}>
        <GuitarArt
          type="electric"
          className="h-full w-full text-gold/70 drop-shadow-[0_0_28px_rgba(200,161,90,0.22)]"
          style={{ transform: `rotate(${ANGLE}deg)` }}
        />
        {HERO.showHotspots &&
          HERO.hotspots.map((spot) => {
            const pos = rotatedPercent(spot.art);
            return <HeroHotspot key={spot.id} x={pos.x} y={pos.y} title={spot.title} detail={spot.detail} />;
          })}
      </div>
    </div>
  );
}
