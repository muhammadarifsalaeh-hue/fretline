import { t } from '@/i18n';
import { useEffect } from 'react';
import { cn } from '@/utils/cn';
import { CloseIcon } from '@/components/ui/Icons';
import FilterPanel from './FilterPanel';

/** Bottom sheet สำหรับ filter บนมือถือ/แท็บเล็ต */
export default function MobileFilterDrawer({ open, onClose, resultCount, activeCount, onClear, ...panelProps }) {
  useEffect(() => {
    if (!open) return undefined;
    document.body.style.overflow = 'hidden';
    const onKey = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', onKey);
    };
  }, [open, onClose]);

  return (
    <div
      aria-hidden={!open}
      className={cn('fixed inset-0 z-[65] transition-[visibility] lg:hidden', open ? 'visible' : 'invisible delay-500')}
    >
      <div
        onClick={onClose}
        className={cn('absolute inset-0 bg-black/70 transition-opacity duration-500', open ? 'opacity-100' : 'opacity-0')}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={t('filters.title')}
        className={cn(
          'absolute inset-x-0 bottom-0 flex max-h-[88svh] flex-col rounded-t-3xl border-t border-line bg-surface transition-transform duration-500 ease-premium',
          open ? 'translate-y-0' : 'translate-y-full',
        )}
      >
        <div className="flex items-center justify-between px-5 pb-2 pt-5">
          <h2 className="font-sans text-2xl font-medium">{t('filters.title')}</h2>
          <button
            type="button"
            aria-label={t('filters.close')}
            onClick={onClose}
            className="grid h-11 w-11 place-items-center rounded-full hover:bg-white/10"
          >
            <CloseIcon />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 pb-4">
          <FilterPanel {...panelProps} />
        </div>

        <div className="flex items-center gap-3 border-t border-line p-4 pb-[calc(1rem+env(safe-area-inset-bottom))]">
          <button
            type="button"
            onClick={onClear}
            disabled={activeCount === 0}
            className="h-12 rounded-full px-5 text-sm text-bone/80 transition hover:text-bone disabled:opacity-40"
          >
            {t('filters.clearAll')}
          </button>
          <button
            type="button"
            onClick={onClose}
            className="h-12 flex-1 rounded-full bg-gold text-sm font-medium text-ink transition hover:bg-gold-soft"
          >
            {t('catalog.showResults', { n: resultCount })}
          </button>
        </div>
      </div>
    </div>
  );
}
