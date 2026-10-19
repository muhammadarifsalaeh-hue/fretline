import { t } from '@/i18n';
import { useEffect, useState } from 'react';
import ActiveFilters from '@/components/catalog/ActiveFilters';
import CatalogCard from '@/components/catalog/CatalogCard';
import CatalogEmpty from '@/components/catalog/CatalogEmpty';
import CatalogToolbar from '@/components/catalog/CatalogToolbar';
import FilterPanel from '@/components/catalog/FilterPanel';
import MobileFilterDrawer from '@/components/catalog/MobileFilterDrawer';
import AppLink from '@/components/ui/AppLink';
import { CATEGORIES } from '@/data/categories';
import { GUITARS } from '@/data/guitars';
import useCatalogFilters from '@/hooks/useCatalogFilters';

const PAGE_SIZE = 9;
const BRAND_TOTAL = new Set(GUITARS.map((g) => g.brand)).size;

export default function CatalogPage() {
  const c = useCatalogFilters();
  const { filters } = c;
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [limit, setLimit] = useState(PAGE_SIZE);

  // เปลี่ยน filter/sort/search → กลับไปแสดงหน้าแรกของผลลัพธ์
  const filterKey = JSON.stringify([filters.q, filters.types, filters.brands, filters.min, filters.max, filters.sort]);
  useEffect(() => setLimit(PAGE_SIZE), [filterKey]);

  useEffect(() => {
    document.title = t('catalog.docTitle');
  }, []);

  const visible = c.results.slice(0, limit);
  const heading =
    filters.types.length === 1
      ? t('catalog.typeGuitars', { name: CATEGORIES.find((x) => x.id === filters.types[0])?.name ?? '' })
      : t('catalog.allGuitars');

  const panelProps = {
    filters,
    typeCounts: c.typeCounts,
    brandCounts: c.brandCounts,
    onToggleType: c.toggleType,
    onToggleBrand: c.toggleBrand,
    onPrice: c.setPrice,
  };

  return (
    <>
      {/* Header */}
      <header className="relative isolate border-b border-line pb-12 pt-28 md:pb-16 md:pt-36">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(50%_80%_at_80%_0%,#262626_0%,#0A0A0A_70%)]"
        />
        <div className="container-x">
          <nav aria-label={t('common.breadcrumb')} className="mb-6 flex items-center gap-2 text-sm text-mute">
            <AppLink href="/" className="transition-colors hover:text-bone">{t('nav.home')}</AppLink>
            <span aria-hidden="true">/</span>
            <span className="text-bone/80">{t('nav.guitars')}</span>
          </nav>
          <h1 className="font-sans text-4xl font-medium leading-[1.1] tracking-tight md:text-6xl">{heading}</h1>
          <p className="mt-5 max-w-lg text-base leading-relaxed text-mute md:text-lg">
            {t('catalog.intro', { n: GUITARS.length, b: BRAND_TOTAL })}
          </p>
        </div>
      </header>

      <CatalogToolbar
        query={filters.q}
        onQuery={c.setQuery}
        sort={filters.sort}
        onSort={c.setSort}
        count={c.results.length}
        activeCount={c.activeCount}
        onOpenFilters={() => setDrawerOpen(true)}
      />

      <div className="container-x pb-24 pt-8 lg:grid lg:grid-cols-[272px_minmax(0,1fr)] lg:gap-12 lg:pt-10">
        {/* Sidebar (Desktop) */}
        <aside className="hidden lg:block">
          <div className="sticky top-[168px] max-h-[calc(100svh-190px)] overflow-y-auto pr-2 [scrollbar-width:thin]">
            <div className="mb-5 flex items-center justify-between">
              <h2 className="font-sans text-2xl font-medium">{t('filters.title')}</h2>
              {c.activeCount > 0 && (
                <button type="button" onClick={c.clearFilters} className="text-sm text-gold transition-colors hover:text-gold-soft">
                  {t('filters.clearAll')}
                </button>
              )}
            </div>
            <FilterPanel {...panelProps} />
          </div>
        </aside>

        {/* Results */}
        <section aria-label={t('catalog.resultsAria')} className="min-w-0">
          <p className="mb-5 font-mono text-sm text-mute lg:hidden" aria-live="polite">
            {t('unit.guitars', { n: c.results.length })}
          </p>

          <ActiveFilters
            filters={filters}
            priceActive={c.priceActive}
            onRemoveType={c.toggleType}
            onRemoveBrand={c.toggleBrand}
            onResetPrice={c.resetPrice}
            onClearQuery={() => c.setQuery('')}
            onClearAll={c.clearFilters}
          />

          {c.results.length === 0 ? (
            <CatalogEmpty onClear={c.clearFilters} />
          ) : (
            <>
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3 xl:gap-6">
                {visible.map((guitar, i) => (
                  <CatalogCard key={guitar.id} guitar={guitar} index={i} />
                ))}
              </div>

              <div className="mt-14 flex flex-col items-center gap-4">
                <p className="font-mono text-sm text-mute">
                  {t('catalog.showing', { a: visible.length, b: c.results.length })}
                </p>
                <div aria-hidden="true" className="h-px w-48 bg-line">
                  <div
                    className="h-px bg-gold transition-[width] duration-500 ease-premium"
                    style={{ width: `${(visible.length / c.results.length) * 100}%` }}
                  />
                </div>
                {visible.length < c.results.length && (
                  <button
                    type="button"
                    onClick={() => setLimit(limit + PAGE_SIZE)}
                    className="mt-2 inline-flex h-12 items-center rounded-full border border-white/20 px-8 text-sm text-bone transition duration-300 hover:border-gold hover:text-gold active:scale-[0.98]"
                  >
                    {t('catalog.loadMore')}
                  </button>
                )}
              </div>
            </>
          )}
        </section>
      </div>

      <MobileFilterDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        resultCount={c.results.length}
        activeCount={c.activeCount}
        onClear={c.clearFilters}
        {...panelProps}
      />
    </>
  );
}
