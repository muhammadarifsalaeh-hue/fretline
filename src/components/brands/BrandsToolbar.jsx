import { t } from '@/i18n';
import { BRAND_SORTS } from '@/utils/brandFilters';
import { cn } from '@/utils/cn';
import SortSelect from '@/components/ui/SortSelect';
import { CloseIcon, SearchIcon } from '@/components/ui/Icons';

function Chip({ active, onClick, children }) {
  return <button type="button" aria-pressed={active} onClick={onClick}
    className={cn('phase5-chip', active && 'is-active')}>{children}</button>;
}

/** All filters remain URL-driven, including the explicitly unverified legacy country filter. */
export default function BrandsToolbar({ query, onQuery, sort, onSort, type, onType, country, onCountry, types, countries, count, hasFilters, onClear }) {
  return (
    <div className="brands-toolbar">
      <div className="brands-search-row">
        <div role="search" className="catalog-search brands-search">
          <SearchIcon size={18} className="shrink-0 text-gold" />
          <label htmlFor="brands-search" className="sr-only">{t('p5.brands.search')}</label>
          <input id="brands-search" type="search" inputMode="search" autoComplete="off"
            value={query} onChange={(event) => onQuery(event.target.value)} placeholder={t('p5.brands.placeholder')} />
          {query && <button type="button" aria-label={t('p5.clearSearch')} onClick={() => onQuery('')}><CloseIcon size={17} /></button>}
        </div>
        <SortSelect value={sort} onChange={onSort} options={BRAND_SORTS} />
      </div>
      <div className="brands-filter-row" role="group" aria-label={t('p5.type')}>
        <Chip active={!type} onClick={() => onType('')}>{t('p5.all')}</Chip>
        {types.map((item) => <Chip key={item.id} active={type === item.id} onClick={() => onType(type === item.id ? '' : item.id)}>{item.name}</Chip>)}
      </div>
      {countries.length > 1 && (
        <details className="brands-extra-filters" open={country ? true : undefined}>
          <summary>{t('p5.brands.moreFilters')}{country ? ` · ${country}` : ''}</summary>
          <div role="group" aria-label={t('p5.brands.country')} className="mt-3 flex flex-wrap gap-2">
            <span className="w-full text-xs text-mute">{t('p5.brands.country')}</span>
            <Chip active={!country} onClick={() => onCountry('')}>{t('p5.all')}</Chip>
            {countries.map((item) => <Chip key={item} active={country === item} onClick={() => onCountry(country === item ? '' : item)}>{item}</Chip>)}
          </div>
          <p className="mt-3 text-xs leading-6 text-mute">{t('p5.brands.countryNote')}</p>
        </details>
      )}
      <div className="brands-result-bar">
        <p aria-live="polite" aria-atomic="true">{t('p5.brands.count', { n: count })}</p>
        {hasFilters && <button type="button" onClick={onClear}>{t('p5.clearFilters')}</button>}
      </div>
    </div>
  );
}
