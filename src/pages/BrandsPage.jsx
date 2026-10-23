import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { t } from '@/i18n';
import BrandCard from '@/components/brands/BrandCard';
import BrandCredits from '@/components/brands/BrandCredits';
import BrandsToolbar from '@/components/brands/BrandsToolbar';
import CatalogEmpty from '@/components/catalog/CatalogEmpty';
import DiscoveryHeading from '@/components/ui/DiscoveryHeading';
import { BRANDS } from '@/data/brands';
import { CATEGORIES } from '@/data/categories';
import { GUITARS } from '@/data/guitars';
import { HOME_BRAND_ASSETS } from '@/data/homeBrandAssets';
import { filterBrands, isBrandSort } from '@/utils/brandFilters';

const COUNTRIES = [...new Set(BRANDS.map((brand) => brand.country).filter(Boolean))].sort();
const TYPES = CATEGORIES.filter((category) => BRANDS.some((brand) => brand.categories.includes(category.id)));

export default function BrandsPage() {
  const [showAtmosphere, setShowAtmosphere] = useState(true);
  const [params, setParams] = useSearchParams();
  const q = params.get('q') ?? '';
  const type = TYPES.some((item) => item.id === params.get('type')) ? params.get('type') : '';
  const country = COUNTRIES.includes(params.get('country')) ? params.get('country') : '';
  const sort = isBrandSort(params.get('sort')) ? params.get('sort') : 'models';
  useEffect(() => { document.title = t('p5.brands.docTitle'); }, []);

  const update = (patch, replace = false) => {
    const next = { q, type, country, sort, ...patch };
    const search = new URLSearchParams();
    if (next.q.trim()) search.set('q', next.q);
    if (next.type) search.set('type', next.type);
    if (next.country) search.set('country', next.country);
    if (next.sort !== 'models') search.set('sort', next.sort);
    setParams(search, { replace });
  };
  const results = useMemo(() => filterBrands(BRANDS, { q, type, country, sort }), [q, type, country, sort]);
  const hasFilters = Boolean(q.trim() || type || country);
  const clear = () => update({ q: '', type: '', country: '' });

  return (
    <div className="phase5-page brands-page">
      <div className="brand-directory-atmosphere" aria-hidden="true">
        {showAtmosphere && <img src={HOME_BRAND_ASSETS.fender.photo} alt="" width="1200" height="700" decoding="async"
          onError={() => setShowAtmosphere(false)} />}
      </div>
      <DiscoveryHeading eyebrow="BRAND DIRECTORY" title={t('p5.brands.title')} description={t('p5.brands.intro')}
        breadcrumbs={[{ label: t('nav.brands') }]}
        aside={<p className="phase5-heading-meta">{t('p5.brands.summary', { brands: BRANDS.length, n: GUITARS.length })}</p>} />
      <section className="container-x phase5-body" aria-label={t('p5.brands.title')}>
        <BrandsToolbar query={q} onQuery={(value) => update({ q: value }, true)} sort={sort} onSort={(value) => update({ sort: value })}
          type={type} onType={(value) => update({ type: value })} country={country} onCountry={(value) => update({ country: value })}
          types={TYPES} countries={COUNTRIES} count={results.length} hasFilters={hasFilters} onClear={clear} />
        {sort === 'price' && BRANDS.every((brand) => brand.priceMin == null) && <p className="phase5-note">{t('p5.brands.noPrices')}</p>}
        {results.length ? <div className="brand-directory-grid">
          {results.map((brand) => <BrandCard key={brand.id} brand={brand} />)}
        </div> : <CatalogEmpty title={t('p5.brands.empty')} text={t('p5.brands.emptyText')} onClear={clear} />}
        <p className="phase5-note brands-catalog-note">{t('p5.brands.note')}</p>
        <BrandCredits />
      </section>
    </div>
  );
}
