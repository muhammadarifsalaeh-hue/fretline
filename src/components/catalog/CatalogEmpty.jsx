import { t } from '@/i18n';
import Button from '@/components/ui/Button';
import { SearchIcon } from '@/components/ui/Icons';

/** สถานะไม่พบผลลัพธ์/ยังว่างอยู่ — บอกว่าควรทำอะไรต่อ (ปรับข้อความ/ไอคอน/ปุ่มได้ ค่าเริ่มต้นใช้กับ Catalog) */
export default function CatalogEmpty({
  onClear,
  icon,
  title = t('empty.title'),
  text = t('empty.text'),
  children,
}) {
  return (
    <div className="grid place-items-center rounded-3xl border border-dashed border-line px-6 py-20 text-center">
      <span className="grid h-16 w-16 place-items-center rounded-full border border-line text-gold">{icon ?? <SearchIcon size={26} />}</span>
      <h2 className="mt-6 font-serif text-3xl">{title}</h2>
      <p className="mt-3 max-w-sm text-sm leading-relaxed text-mute">{text}</p>
      {children ?? (onClear && (
        <Button onClick={onClear} className="mt-8">
          {t('filters.clearAllFilters')}
        </Button>
      ))}
    </div>
  );
}
