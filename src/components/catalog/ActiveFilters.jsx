import { t } from '@/i18n';
import { CATEGORIES } from '@/data/categories';
import { formatPrice } from '@/utils/format';
import { CloseIcon } from '@/components/ui/Icons';

function Chip({ label, onRemove }) {
  return (
    <li>
      <button
        type="button"
        onClick={onRemove}
        aria-label={t('filters.removeAria', { label })}
        className="group inline-flex min-h-[36px] items-center gap-2 rounded-full border border-line bg-surface pl-4 pr-3 text-[13px] text-bone transition hover:border-gold"
      >
        {label}
        <CloseIcon size={14} className="text-mute transition-colors group-hover:text-gold" />
      </button>
    </li>
  );
}

/** Chip ของ filter ที่เปิดอยู่ + ปุ่มล้างทั้งหมด */
export default function ActiveFilters({ filters, priceActive, onRemoveType, onRemoveBrand, onResetPrice, onClearQuery, onClearAll }) {
  const typeName = (id) => CATEGORIES.find((c) => c.id === id)?.name ?? id;
  const hasAny = filters.types.length || filters.brands.length || priceActive || filters.q.trim();
  if (!hasAny) return null;

  return (
    <ul className="mb-6 flex flex-wrap items-center gap-2" aria-label={t('filters.activeAria')}>
      {filters.q.trim() && <Chip label={`“${filters.q.trim()}”`} onRemove={onClearQuery} />}
      {filters.types.map((id) => (
        <Chip key={id} label={typeName(id)} onRemove={() => onRemoveType(id)} />
      ))}
      {filters.brands.map((b) => (
        <Chip key={b} label={b} onRemove={() => onRemoveBrand(b)} />
      ))}
      {priceActive && <Chip label={`${formatPrice(filters.min)} – ${formatPrice(filters.max)}`} onRemove={onResetPrice} />}
      <li>
        <button type="button" onClick={onClearAll} className="min-h-[36px] px-2 text-[13px] text-gold transition-colors hover:text-gold-soft">
          {t('filters.clearAll')}
        </button>
      </li>
    </ul>
  );
}
