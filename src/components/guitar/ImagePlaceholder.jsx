import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import GuitarArt from '@/components/ui/GuitarArt';

/**
 * ภาพประกอบชั่วคราวเมื่อยังไม่มีรูปจริงของรุ่นนั้น (หรือรูปโหลดไม่ได้) — ระบุชัดว่าไม่ใช่ภาพสินค้า
 * ตั้งใจไม่ใช้รูปกีตาร์รุ่นอื่นแทน เพื่อไม่ให้แสดงสินค้าผิดรุ่น
 * compact = สำหรับรูปเล็ก (thumbnail) แสดงเฉพาะเส้นร่าง ไม่มีข้อความ
 */
export default function ImagePlaceholder({ guitar, compact = false, className = '' }) {
  return (
    <div
      role="img"
      aria-label={guitar ? t('placeholder.aria', { name: `${guitar.brand} ${guitar.name}` }) : t('placeholder.ariaNoName')}
      className={cn(
        'image-placeholder absolute inset-0 flex flex-col items-center justify-center overflow-hidden bg-gradient-to-b from-[#262626] to-[#141414] text-gold/55',
        className,
      )}
    >
      <div aria-hidden="true" className="pointer-events-none absolute inset-0 bg-[radial-gradient(60%_50%_at_50%_38%,rgba(200,161,90,0.10),transparent_70%)]" />
      <GuitarArt
        type={guitar?.category}
        className={cn('relative -rotate-[18deg]', compact ? 'h-[72%] w-auto' : 'h-[58%] w-auto')}
      />
      {!compact && (
        <div className="placeholder-message relative mt-5 px-6 text-center">
          <p className="text-[11px] uppercase tracking-[0.2em] text-mute">{t('placeholder.soon')}</p>
          <p className="mt-1 text-[10px] text-mute/70">{t('placeholder.illustration')}</p>
        </div>
      )}
    </div>
  );
}
