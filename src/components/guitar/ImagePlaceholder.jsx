import { t } from '@/i18n';
import { cn } from '@/utils/cn';

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
        'image-placeholder absolute inset-0 grid place-items-center overflow-hidden bg-black text-gold/55',
        compact && 'is-compact',
        className,
      )}
    >
      {!compact && (
        <span aria-hidden="true" className="product-image-empty-label">{t('placeholder.soon')}</span>
      )}
    </div>
  );
}
