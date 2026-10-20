import { t } from '@/i18n';
import { SORT_OPTIONS } from '@/hooks/useCatalogFilters';
import { ChevronDownIcon, GridIcon } from '@/components/ui/Icons';

export default function CatalogToolbar({ sort, onSort, count, page, pageSize, drawerOpen, activeCount, onOpenFilters }) {
  return (
    <div className="catalog-toolbar">
      <div className="catalog-result-count min-w-0" role="status" aria-atomic="true">
        <p className="text-sm text-bone">{t('unit.guitars', { n: count })}</p>
        {count > 0 && <p className="mt-0.5 text-[11px] text-mute">{t('catalog.pageRange', { from: (page - 1) * pageSize + 1, to: Math.min(page * pageSize, count), total: count })}</p>}
      </div>
      <div className="catalog-toolbar-controls flex min-w-0 items-center gap-2 sm:gap-3">
        <button type="button" onClick={onOpenFilters} aria-controls="catalog-filter-dialog"
          aria-expanded={drawerOpen} aria-haspopup="dialog"
          className="catalog-filter-trigger lg:hidden">
          {t('filters.title')}{activeCount > 0 && <span className="ml-2 text-gold">({activeCount})</span>}
        </button>
        <label className="relative flex min-w-0 items-center gap-2">
          <span className="hidden text-xs text-mute sm:inline">{t('toolbar.sortBy')}</span>
          <select aria-label={t('toolbar.sortBy')} value={sort} onChange={(e) => onSort(e.target.value)}
            className="h-11 min-w-0 max-w-[180px] appearance-none rounded-lg border border-line bg-surface pl-3 pr-9 text-xs focus:border-gold">
            {SORT_OPTIONS.map((option) => <option key={option.id} value={option.id}>{option.label}</option>)}
          </select>
          <ChevronDownIcon size={15} className="pointer-events-none absolute right-3 text-mute" />
        </label>
        <GridIcon size={17} className="hidden text-gold sm:block" />
      </div>
    </div>
  );
}
