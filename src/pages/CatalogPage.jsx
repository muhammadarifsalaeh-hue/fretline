import { t } from '@/i18n';
import { useCallback, useEffect, useRef, useState } from 'react';
import ActiveFilters from '@/components/catalog/ActiveFilters';
import CatalogCard from '@/components/catalog/CatalogCard';
import CatalogEmpty from '@/components/catalog/CatalogEmpty';
import CatalogToolbar from '@/components/catalog/CatalogToolbar';
import CatalogPagination from '@/components/catalog/CatalogPagination';
import CategoryNavigation from '@/components/catalog/CategoryNavigation';
import FilterPanel from '@/components/catalog/FilterPanel';
import MobileFilterDrawer from '@/components/catalog/MobileFilterDrawer';
import AppLink from '@/components/ui/AppLink';
import { CloseIcon, SearchIcon } from '@/components/ui/Icons';
import useCatalogFilters, { HAS_CATALOG_PRICES } from '@/hooks/useCatalogFilters';

const PAGE_SIZE = 9;

export default function CatalogPage() {
  const c = useCatalogFilters();
  const { filters } = c;
  const [drawerOpen, setDrawerOpen] = useState(false);
  const closeDrawer = useCallback(() => setDrawerOpen(false), []);
  const resultsRef = useRef(null);
  const pageCount = Math.max(1, Math.ceil(c.results.length / PAGE_SIZE));
  const page = Math.min(filters.page, pageCount);
  const visible = c.results.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  useEffect(() => { document.title = t('catalog.docTitle'); }, []);
  useEffect(() => {
    if (!drawerOpen) return undefined;
    const desktop = window.matchMedia('(min-width: 1024px)');
    const onResize = () => { if (desktop.matches) closeDrawer(); };
    desktop.addEventListener('change', onResize);
    return () => desktop.removeEventListener('change', onResize);
  }, [drawerOpen, closeDrawer]);
  useEffect(() => {
    if (filters.page !== page) c.setPage(page, true);
  }, [filters.page, page, c.setPage]);
  const panelProps = {
    filters, typeCounts: c.typeCounts, brandCounts: c.brandCounts,
    onToggleType: c.toggleType, onToggleBrand: c.toggleBrand, onPrice: c.setPrice,
  };
  const changePage = (next) => {
    c.setPage(next);
    resultsRef.current?.focus({ preventScroll: true });
    resultsRef.current?.scrollIntoView({ block: 'start', behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  };
  const submitSearch = (event) => {
    event.preventDefault();
    resultsRef.current?.focus({ preventScroll: true });
    resultsRef.current?.scrollIntoView({ block: 'start', behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  };

  return (
    <div className="catalog-page discovery-page">
      <header className="catalog-heading container-x">
        <nav aria-label={t('common.breadcrumb')} className="discovery-breadcrumb">
          <AppLink href="/">{t('nav.home')}</AppLink><span aria-hidden="true">›</span><span>{t('nav.guitars')}</span>
        </nav>
        <p className="discovery-kicker">FRETLINE / GUITAR DISCOVERY</p>
        <h1 className="font-serif text-5xl md:text-6xl">Catalog</h1>
        <p className="mt-1 text-sm text-gold">{t('catalog.tagline')}</p>
        <form role="search" className="catalog-search" onSubmit={submitSearch}>
          <SearchIcon size={19} className="shrink-0 text-gold" />
          <label htmlFor="catalog-search" className="sr-only">{t('toolbar.searchLabel')}</label>
          <input id="catalog-search" type="search" autoComplete="off" enterKeyHint="search" spellCheck="false" aria-controls="catalog-results" value={filters.q}
            placeholder={t('toolbar.placeholder')} onChange={(e) => c.setQuery(e.target.value)} />
          {filters.q && <button type="button" aria-label={t('toolbar.clear')} onClick={() => c.setQuery('')}><CloseIcon size={17} /></button>}
          <button type="submit" aria-label={t('search.button')} className="catalog-search-submit rounded-md bg-gold"><SearchIcon size={17} /></button>
        </form>
        <CategoryNavigation types={filters.types} onSelect={(id) => id === 'all' ? c.setTypes([]) : c.toggleType(id)} />
      </header>

      <div className="catalog-body container-x">
        <aside aria-label={t('filters.title')} className="catalog-sidebar">
          <div className="sticky top-24 max-h-[calc(100svh-112px)] overflow-y-auto pr-3 [scrollbar-width:thin]">
            <div className="mb-4 flex items-center justify-between gap-2">
              <h2 className="text-sm font-medium">{t('filters.title')}</h2>
              {c.activeCount > 0 && <button type="button" onClick={c.clearFilters} className="min-h-11 text-xs text-gold">{t('filters.clearAll')}</button>}
            </div>
            <FilterPanel {...panelProps} />
          </div>
        </aside>
        <section id="catalog-results" ref={resultsRef} tabIndex={-1} aria-label={t('catalog.resultsAria')} className="catalog-results min-w-0 scroll-mt-24 rounded-lg">
          <CatalogToolbar sort={filters.sort} onSort={c.setSort} count={c.results.length} page={page} pageSize={PAGE_SIZE}
            drawerOpen={drawerOpen} activeCount={c.activeCount} onOpenFilters={() => setDrawerOpen(true)} />
          <ActiveFilters filters={filters} priceActive={c.priceActive} onRemoveType={c.toggleType}
            onRemoveBrand={c.toggleBrand} onResetPrice={c.resetPrice} onClearQuery={() => c.setQuery('')} onClearAll={c.clearFilters} />
          <p className="catalog-data-note">{t('catalog.dataNote')}</p>
          {c.results.length === 0 ? <CatalogEmpty onClear={c.clearFilters}
            title={c.priceActive && !HAS_CATALOG_PRICES ? t('p6.price.empty') : undefined}
            text={c.priceActive && !HAS_CATALOG_PRICES ? t('p6.price.noData') : undefined} /> : (
            <>
              <div className="catalog-grid">
                {visible.map((guitar, index) => <CatalogCard key={guitar.id} guitar={guitar} index={index} compact />)}
              </div>
              <CatalogPagination page={page} pageCount={pageCount} total={c.results.length} pageSize={PAGE_SIZE} onPage={changePage} />
            </>
          )}
        </section>
      </div>
      <MobileFilterDrawer open={drawerOpen} onClose={closeDrawer} resultCount={c.results.length}
        activeCount={c.activeCount} onClear={c.clearFilters} {...panelProps} />
    </div>
  );
}
