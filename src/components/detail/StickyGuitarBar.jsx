import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import { formatPrice } from '@/utils/format';
import { CheckIcon, PlusIcon } from '@/components/ui/Icons';
import GuitarImage from '@/components/guitar/GuitarImage';

/** แถบสรุปที่เลื่อนลงมาใต้ Navbar เมื่อปุ่มหลักหลุดจอ */
export default function StickyGuitarBar({ guitar, visible, inCompare, full = false, onToggleCompare }) {
  return (
    <div
      aria-hidden={!visible}
      className={cn(
        'fixed inset-x-0 top-16 z-40 border-b border-line bg-ink/90 backdrop-blur-xl transition duration-500 ease-premium lg:top-20',
        visible ? 'translate-y-0 opacity-100' : 'pointer-events-none -translate-y-full opacity-0',
      )}
    >
      <div className="container-x flex items-center gap-4 py-3">
        <GuitarImage guitar={guitar} size="sm" alt="" className="h-12 w-12 shrink-0 rounded-lg" />
        <div className="min-w-0 flex-1">
          <p className="truncate text-xs text-mute">{guitar.brand}</p>
          <p className="truncate font-serif text-xl leading-tight">{guitar.name}</p>
        </div>
        <p className="hidden font-mono text-lg text-gold sm:block">{formatPrice(guitar.price)}</p>
        <button
          type="button"
          disabled={full}
          title={full ? t('p4.compare.fullNote') : undefined}
          tabIndex={visible ? 0 : -1}
          onClick={onToggleCompare}
          aria-pressed={inCompare}
          className={cn(
            'inline-flex min-h-11 shrink-0 items-center gap-2 rounded-full px-5 text-sm font-medium transition duration-300 disabled:cursor-not-allowed disabled:opacity-50',
            inCompare ? 'border border-gold bg-gold/10 text-gold' : 'bg-gold text-ink hover:bg-gold-soft',
          )}
        >
          {inCompare ? <CheckIcon size={16} /> : <PlusIcon size={16} />}
          {inCompare ? t('cmp.added') : t('detail.add')}
        </button>
      </div>
    </div>
  );
}
