import { t } from '@/i18n';
import { SORT_OPTIONS } from '@/hooks/useCatalogFilters';
import { ChevronDownIcon, CloseIcon, SearchIcon } from '@/components/ui/Icons';

/** แถบเครื่องมือ: ค้นหา + ปุ่ม Filters (มือถือ) + เรียงลำดับ + จำนวนผลลัพธ์ */
export default function CatalogToolbar({ query, onQuery, sort, onSort, count, activeCount, onOpenFilters }) {
  return (
    <div className="border-b border-line bg-ink/85 backdrop-blur-xl md:sticky md:top-16 md:z-30 lg:top-20">
      <div className="container-x flex flex-wrap items-center gap-3 py-3">
        <div role="search" className="relative w-full md:min-w-0 md:flex-1 md:max-w-xl">
          <SearchIcon className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-mute" />
          <label htmlFor="catalog-search" className="sr-only">{t('toolbar.searchLabel')}</label>
          <input
            id="catalog-search"
            type="text"
            inputMode="search"
            autoComplete="off"
            value={query}
            onChange={(e) => onQuery(e.target.value)}
            placeholder={t('toolbar.placeholder')}
            className="h-12 w-full rounded-full border border-line bg-surface pl-12 pr-12 text-[15px] text-bone placeholder:text-mute transition duration-300 focus:border-gold focus:outline-none focus:shadow-[0_0_0_4px_rgba(200,161,90,0.14)]"
          />
          {query && (
            <button
              type="button"
              aria-label={t('toolbar.clear')}
              onClick={() => onQuery('')}
              className="absolute right-2 top-1/2 grid h-9 w-9 -translate-y-1/2 place-items-center rounded-full text-mute transition hover:bg-white/10 hover:text-bone"
            >
              <CloseIcon size={16} />
            </button>
          )}
        </div>

        <p className="ml-auto hidden font-mono text-sm text-mute lg:block" aria-live="polite">
          {t('unit.guitars', { n: count })}
        </p>

        <button
          type="button"
          onClick={onOpenFilters}
          className="relative inline-flex h-12 flex-1 items-center justify-center gap-2 rounded-full border border-white/20 px-6 text-sm text-bone transition hover:border-gold md:flex-none lg:hidden"
        >
          {t('filters.title')}
          {activeCount > 0 && (
            <span className="grid h-5 min-w-5 place-items-center rounded-full bg-gold px-1 font-mono text-[11px] font-medium text-ink">
              {activeCount}
            </span>
          )}
        </button>

        <label className="relative flex-1 md:flex-none">
          <span className="sr-only">{t('toolbar.sortBy')}</span>
          <select
            value={sort}
            onChange={(e) => onSort(e.target.value)}
            className="h-12 w-full appearance-none rounded-full border border-line bg-surface pl-5 pr-11 text-sm text-bone transition focus:border-gold focus:outline-none md:w-auto"
          >
            {SORT_OPTIONS.map((o) => (
              <option key={o.id} value={o.id} className="bg-surface">
                {o.label}
              </option>
            ))}
          </select>
          <ChevronDownIcon size={18} className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-mute" />
        </label>
      </div>
    </div>
  );
}
