import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import { formatPrice } from '@/utils/format';
import { CheckIcon, PlusIcon } from '@/components/ui/Icons';
import GuitarImage from '@/components/guitar/GuitarImage';
import PriceSourceNote from '@/components/guitar/PriceSourceNote';

/** แถบสรุปที่เลื่อนลงมาใต้ Navbar เมื่อปุ่มหลักหลุดจอ */
export default function StickyGuitarBar({ guitar, visible, inCompare, full = false, onToggleCompare }) {
  return (
    <div
      aria-hidden={!visible}
      inert={!visible ? '' : undefined}
      style={{ top: 'var(--fl-header-height, 64px)', zIndex: 'var(--fl-layer-tray, 40)' }}
      className={cn(
        'site-detail-sticky fixed inset-x-0 border-b border-line bg-ink/95 backdrop-blur-xl transition-[opacity,transform] duration-[240ms] ease-premium motion-reduce:transition-none',
        visible ? 'translate-y-0 opacity-100' : 'pointer-events-none -translate-y-full opacity-0',
      )}
    >
      <div className="container-x flex items-center gap-4 py-3">
        <GuitarImage guitar={guitar} size="sm" alt="" className="h-12 w-12 shrink-0 rounded-lg" />
        <div className="min-w-0 flex-1">
          <p className="truncate text-[13px] text-mute">{guitar.brand}</p>
          <p lang="en" className="truncate font-serif text-xl leading-snug">{guitar.name}</p>
        </div>
        <div className="hidden sm:block"><p className="font-mono text-lg text-gold">{formatPrice(guitar.price)}</p><PriceSourceNote guitar={guitar} linkTabIndex={visible ? undefined : -1} /></div>
        <button
          type="button"
          disabled={full}
          title={full ? t('p4.compare.fullNote') : undefined}
          tabIndex={visible ? 0 : -1}
          onClick={onToggleCompare}
          aria-pressed={inCompare}
          className={cn(
            'site-sticky-action inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-lg px-4 text-sm font-medium leading-normal transition-colors duration-200 disabled:cursor-not-allowed disabled:opacity-50 motion-reduce:transition-none',
            inCompare ? 'border border-gold bg-gold/10 text-gold' : 'bg-gold text-ink hover:bg-gold-soft',
          )}
        >
          {inCompare ? <CheckIcon size={18} /> : <PlusIcon size={18} />}
          {inCompare ? t('cmp.added') : t('detail.add')}
        </button>
      </div>
    </div>
  );
}
