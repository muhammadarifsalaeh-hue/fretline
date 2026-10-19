import { cn } from '@/utils/cn';
import GuitarArt from './GuitarArt';

/**
 * พื้นหลังแบบเส้นร่าง (blueprint) ใช้แทนรูปบรรยากาศที่ยังไม่มีรูปจริง
 *  type   : ประเภทกีตาร์ของเส้นร่าง (electric | acoustic | classical | bass)
 *  anchor : 'center' | 'right' (ตำแหน่งของเส้นร่าง)
 * ใส่ class ของตำแหน่ง/ขนาดที่ className เช่น "absolute inset-0 -z-20"
 */
export default function ArtBackdrop({ type = 'electric', anchor = 'center', rotate = -24, className = 'absolute inset-0' }) {
  return (
    <div
      aria-hidden="true"
      className={cn('overflow-hidden bg-gradient-to-br from-[#282828] via-[#181818] to-[#0f0f0f] text-gold/35', className)}
    >
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.035)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.035)_1px,transparent_1px)] bg-[size:44px_44px] [mask-image:radial-gradient(70%_70%_at_50%_45%,black,transparent)]" />
      <div className="absolute inset-0 bg-[radial-gradient(55%_50%_at_50%_42%,rgba(200,161,90,0.10),transparent_70%)]" />
      <div
        className="absolute top-1/2 grid h-[120%] -translate-x-1/2 -translate-y-1/2 place-items-center transition-transform duration-700 ease-premium group-hover:scale-[1.06]"
        style={{ left: anchor === 'right' ? '76%' : '50%' }}
      >
        <GuitarArt type={type} className="h-full w-auto" style={{ transform: `rotate(${rotate}deg)` }} />
      </div>
    </div>
  );
}
