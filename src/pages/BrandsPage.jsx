import { useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import BrandCard from '@/components/brands/BrandCard';
import BrandsToolbar from '@/components/brands/BrandsToolbar';
import CatalogEmpty from '@/components/catalog/CatalogEmpty';
import AppLink from '@/components/ui/AppLink';
import { BRANDS } from '@/data/brands';
import { CATEGORIES } from '@/data/categories';
import { GUITARS } from '@/data/guitars';
import { filterBrands, isBrandSort } from '@/utils/brandFilters';

const COUNTRIES = [...new Set(BRANDS.map((b) => b.country).filter(Boolean))].sort();
// แสดงเฉพาะประเภทที่มีแบรนด์ผลิตจริง
const TYPES = CATEGORIES.filter((c) => BRANDS.some((b) => b.categories.includes(c.id)));

/**
 * /brands — ทุกแบรนด์ที่มีใน Catalog (ข้อมูลชุดเดียวกัน)
 * ตัวกรองเก็บใน URL: ?q=&type=&country=&sort=
 */
export default function BrandsPage() {
  const [params, setParams] = useSearchParams();
  const q = params.get('q') ?? '';
  const type = TYPES.some((t) => t.id === params.get('type')) ? params.get('type') : '';
  const country = COUNTRIES.includes(params.get('country')) ? params.get('country') : '';
  const sort = isBrandSort(params.get('sort')) ? params.get('sort') : 'models';

  useEffect(() => {
    document.title = 'Brands — Fretline';
  }, []);

  const update = (patch) => {
    const next = { q, type, country, sort, ...patch };
    const p = new URLSearchParams();
    if (next.q.trim()) p.set('q', next.q);
    if (next.type) p.set('type', next.type);
    if (next.country) p.set('country', next.country);
    if (next.sort !== 'models') p.set('sort', next.sort);
    setParams(p, { replace: true });
  };

  const results = useMemo(() => filterBrands(BRANDS, { q, type, country, sort }), [q, type, country, sort]);
  const hasFilters = Boolean(q.trim() || type || country);

  return (
    <>
      <header className="relative isolate border-b border-line pb-12 pt-28 md:pb-16 md:pt-36">
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(50%_80%_at_80%_0%,#262626_0%,#0A0A0A_70%)]" />
        <div className="container-x">
          <nav aria-label="Breadcrumb" className="mb-6 flex items-center gap-2 text-sm text-mute">
            <AppLink href="/" className="transition-colors hover:text-bone">Home</AppLink>
            <span aria-hidden="true">/</span>
            <span className="text-bone/80">Brands</span>
          </nav>
          <h1 className="font-serif text-5xl leading-[0.98] tracking-tight md:text-7xl">Brands</h1>
          <p className="mt-5 max-w-lg text-base leading-relaxed text-mute md:text-lg">
            {BRANDS.length} makers and {GUITARS.length} guitars in the catalog. Pick a brand to see its instruments.
          </p>
        </div>
      </header>

      <section className="container-x pb-24 pt-8 md:pt-10">
        <BrandsToolbar
          query={q}
          onQuery={(v) => update({ q: v })}
          sort={sort}
          onSort={(v) => update({ sort: v })}
          type={type}
          onType={(v) => update({ type: v })}
          country={country}
          onCountry={(v) => update({ country: v })}
          types={TYPES}
          countries={COUNTRIES}
          count={results.length}
          hasFilters={hasFilters}
          onClear={() => update({ q: '', type: '', country: '' })}
        />

        <div className="mt-8">
          {results.length === 0 ? (
            <CatalogEmpty
              title="No brands match"
              text="Try a different name or remove a filter."
              onClear={() => update({ q: '', type: '', country: '' })}
            />
          ) : (
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 lg:gap-6">
              {results.map((brand, i) => (
                <BrandCard key={brand.id} brand={brand} index={i} />
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
