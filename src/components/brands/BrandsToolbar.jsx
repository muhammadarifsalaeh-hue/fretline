import { BRAND_SORTS } from '@/utils/brandFilters';
import { cn } from '@/utils/cn';
import { ChevronDownIcon, CloseIcon, SearchIcon } from '@/components/ui/Icons';

function Chip({ active, onClick, children }) {
  return (
    <button
      type="button"
      aria-pressed={active}
      onClick={onClick}
      className={cn(
        'min-h-[40px] shrink-0 rounded-full border px-4 text-[13px] transition duration-300',
        active ? 'border-gold bg-gold/10 text-gold' : 'border-white/12 text-bone/75 hover:border-gold hover:text-gold',
      )}
    >
      {children}
    </button>
  );
}

function ChipRow({ label, children }) {
  return (
    <div className="flex items-center gap-3">
      <p className="w-16 shrink-0 text-xs text-mute">{label}</p>
      <div className="-mr-5 flex gap-2 overflow-x-auto pb-1 pr-5 [scrollbar-width:none] sm:mr-0 sm:flex-wrap sm:overflow-visible sm:pr-0 [&::-webkit-scrollbar]:hidden">{children}</div>
    </div>
  );
}

/** ค้นหา + เรียงลำดับ + ตัวกรอง (ประเภทกีตาร์ / ประเทศ) ของหน้า Brands */
export default function BrandsToolbar({ query, onQuery, sort, onSort, type, onType, country, onCountry, types, countries, count, hasFilters, onClear }) {
  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-3">
        <div role="search" className="relative w-full md:min-w-0 md:flex-1 md:max-w-xl">
          <SearchIcon className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-mute" />
          <label htmlFor="brands-search" className="sr-only">Search brands</label>
          <input
            id="brands-search"
            type="text"
            inputMode="search"
            autoComplete="off"
            value={query}
            onChange={(e) => onQuery(e.target.value)}
            placeholder="Search brands…"
            className="h-12 w-full rounded-full border border-line bg-surface pl-12 pr-12 text-[15px] text-bone placeholder:text-mute transition duration-300 focus:border-gold focus:outline-none focus:shadow-[0_0_0_4px_rgba(200,161,90,0.14)]"
          />
          {query && (
            <button
              type="button"
              aria-label="Clear search"
              onClick={() => onQuery('')}
              className="absolute right-2 top-1/2 grid h-9 w-9 -translate-y-1/2 place-items-center rounded-full text-mute transition hover:bg-white/10 hover:text-bone"
            >
              <CloseIcon size={16} />
            </button>
          )}
        </div>

        <p className="ml-auto hidden font-mono text-sm text-mute md:block" aria-live="polite">
          {count} {count === 1 ? 'brand' : 'brands'}
        </p>

        <label className="relative w-full md:w-auto">
          <span className="sr-only">Sort by</span>
          <select
            value={sort}
            onChange={(e) => onSort(e.target.value)}
            className="h-12 w-full appearance-none rounded-full border border-line bg-surface pl-5 pr-11 text-sm text-bone transition focus:border-gold focus:outline-none md:w-auto"
          >
            {BRAND_SORTS.map((o) => (
              <option key={o.id} value={o.id} className="bg-surface">{o.label}</option>
            ))}
          </select>
          <ChevronDownIcon size={18} className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-mute" />
        </label>
      </div>

      <ChipRow label="Type">
        <Chip active={!type} onClick={() => onType('')}>All</Chip>
        {types.map((t) => (
          <Chip key={t.id} active={type === t.id} onClick={() => onType(type === t.id ? '' : t.id)}>
            {t.name}
          </Chip>
        ))}
      </ChipRow>

      {countries.length > 1 && (
        <ChipRow label="Based in">
          <Chip active={!country} onClick={() => onCountry('')}>All</Chip>
          {countries.map((c) => (
            <Chip key={c} active={country === c} onClick={() => onCountry(country === c ? '' : c)}>
              {c}
            </Chip>
          ))}
        </ChipRow>
      )}

      <div className="flex items-center justify-between md:hidden">
        <p className="font-mono text-sm text-mute" aria-live="polite">
          {count} {count === 1 ? 'brand' : 'brands'}
        </p>
        {hasFilters && (
          <button type="button" onClick={onClear} className="min-h-[40px] text-sm text-gold transition-colors hover:text-gold-soft">
            Clear filters
          </button>
        )}
      </div>
      {hasFilters && (
        <button type="button" onClick={onClear} className="hidden min-h-[40px] text-sm text-gold transition-colors hover:text-gold-soft md:block">
          Clear filters
        </button>
      )}
    </div>
  );
}
