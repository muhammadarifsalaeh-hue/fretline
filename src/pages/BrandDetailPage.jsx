import { useEffect, useMemo } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { t } from '@/i18n';
import CatalogCard from '@/components/catalog/CatalogCard';
import CatalogEmpty from '@/components/catalog/CatalogEmpty';
import AppLink from '@/components/ui/AppLink';
import DiscoveryHeading from '@/components/ui/DiscoveryHeading';
import SortSelect from '@/components/ui/SortSelect';
import { ArrowRightIcon, ArrowUpRightIcon } from '@/components/ui/Icons';
import { BRANDS, getBrandById, getBrandGuitars } from '@/data/brands';
import { ARCHIVED_GUITARS } from '@/data/guitars';
import { slugify } from '@/utils/slug';
import { CATEGORIES } from '@/data/categories';
import { isSourceBacked } from '@/utils/dataTrust';
import { sortGuitars, WISHLIST_SORTS } from '@/utils/guitarSort';
import { brandCatalogUrl, brandUrl } from '@/utils/routes';

const SORTS = [{ id: 'catalog', label: t('p5.detail.models') }, ...WISHLIST_SORTS.filter((item) => item.id !== 'saved')];

function BrandContent({ brand }) {
  const [params, setParams] = useSearchParams();
  const guitars = useMemo(() => getBrandGuitars(brand.name), [brand.name]);
  const type = CATEGORIES.some((item) => item.id === params.get('type')) ? params.get('type') : '';
  const sort = SORTS.some((item) => item.id === params.get('sort')) ? params.get('sort') : 'catalog';
  const results = useMemo(() => {
    const filtered = guitars.filter((guitar) => !type || guitar.category === type);
    return sort === 'catalog' ? filtered : sortGuitars(filtered, sort, { verifiedOnly: true });
  }, [guitars, type, sort]);
  const sources = useMemo(() => [...new Map(guitars.filter(isSourceBacked).map((guitar) => [guitar.source.url, guitar.source])).values()], [guitars]);
  const others = BRANDS.filter((item) => item.id !== brand.id);
  useEffect(() => { document.title = t('p5.detail.docTitle', { brand: brand.name }); }, [brand.name]);
  const update = (patch) => {
    const next = { type, sort, ...patch };
    const search = new URLSearchParams();
    if (next.type) search.set('type', next.type);
    if (next.sort !== 'catalog') search.set('sort', next.sort);
    setParams(search);
  };

  return (
    <div className="phase5-page brand-detail-page">
      <DiscoveryHeading eyebrow={t('targeted.brand.kicker')} title={brand.name} serif
        description={t('p5.detail.intro', { n: guitars.length, brand: brand.name })}
        breadcrumbs={[{ label: t('nav.brands'), href: '/brands' }, { label: brand.name }]}
        aside={<AppLink href={brandCatalogUrl(brand.name)} className="phase4-button is-gold">{t('p5.detail.catalog')}<ArrowRightIcon size={16} /></AppLink>}>
        {brand.logo && <img className="brand-detail-logo" src={brand.logo} alt={brand.name} width="180" height="64" />}
      </DiscoveryHeading>
      <div className="container-x phase5-body">
        <dl className="brand-detail-stats">
          <div><dt>{t('p5.detail.models')}</dt><dd>{guitars.length}</dd></div>
          <div><dt>{t('p5.detail.types')}</dt><dd className="is-text">{brand.categories.map((id) => CATEGORIES.find((item) => item.id === id)?.name ?? id).join(' · ')}</dd></div>
          <div><dt>{t('p5.detail.sourceCount')}</dt><dd>{brand.sourceModels}<span> / {guitars.length}</span></dd></div>
        </dl>
        <p className="brand-detail-bio">{t('p5.detail.noBio')}</p>
        {sources.length > 0 && <details className="brand-sources">
          <summary>{t('p5.detail.source')} ({sources.length})</summary>
          <p>{t('p5.detail.sourceCaveat')}</p>
          <ul>{sources.map((source) => <li key={source.url}>
            <a href={source.url} target="_blank" rel="noopener noreferrer">{new URL(source.url).hostname}<ArrowUpRightIcon size={14} /></a>
            <span>{t('p5.detail.checked', { date: source.verifiedOn })}</span>
            {source.note && <p>{source.note}</p>}
          </li>)}</ul>
        </details>}
        <section aria-labelledby="brand-models-title" className="brand-models-section">
          <div className="brand-models-heading">
            <h2 id="brand-models-title">{t('p5.detail.heading', { brand: brand.name })}</h2>
            <SortSelect value={sort} onChange={(value) => update({ sort: value })} options={SORTS} />
          </div>
          <div className="brands-filter-row" role="group" aria-label={t('p5.type')}>
            <button className={`phase5-chip ${!type ? 'is-active' : ''}`} type="button" aria-pressed={!type} onClick={() => update({ type: '' })}>{t('p5.all')}</button>
            {brand.categories.map((id) => <button key={id} type="button" className={`phase5-chip ${type === id ? 'is-active' : ''}`}
              aria-pressed={type === id} onClick={() => update({ type: type === id ? '' : id })}>
              {CATEGORIES.find((item) => item.id === id)?.name ?? id}
            </button>)}
            {type && !brand.categories.includes(type) && <button className="phase5-chip is-active" type="button" aria-pressed="true" onClick={() => update({ type: '' })}>{CATEGORIES.find((item) => item.id === type)?.name}</button>}
          </div>
          <p className="phase5-note">{t('p5.detail.dataNote')}</p>
          <p className="brand-model-count" aria-live="polite">{t('p5.detail.count', { n: results.length, total: guitars.length })}</p>
          {results.length ? <div className="brand-model-grid">
            {results.map((guitar, index) => <CatalogCard key={guitar.id} guitar={guitar} index={index} compact verifiedOnly />)}
          </div> : <CatalogEmpty title={t('p5.detail.empty')} text={t('p5.detail.emptyText')} onClear={() => update({ type: '' })} />}
        </section>
        <section className="brand-more" aria-labelledby="more-brands-title">
          <h2 id="more-brands-title">{t('p5.detail.more')}</h2>
          <ul>{others.map((item) => <li key={item.id}><AppLink href={brandUrl(item.name)}>{item.name}<span>{item.models}</span><ArrowUpRightIcon size={14} /></AppLink></li>)}</ul>
        </section>
      </div>
    </div>
  );
}

function MissingBrand() {
  useEffect(() => { document.title = `${t('p5.detail.notFound')} — Fretline`; }, []);
  return <div className="phase5-page">
    <DiscoveryHeading eyebrow={t('targeted.brand.missing')} title={t('p5.detail.notFound')} breadcrumbs={[{ label: t('nav.brands'), href: '/brands' }, { label: '404' }]} />
    <section className="container-x phase5-body">
      <CatalogEmpty title={t('p5.detail.notFound')} text={t('p5.detail.notFoundText')}>
        <AppLink href="/brands" className="phase4-button is-gold mt-6">{t('p5.detail.back')}<ArrowRightIcon size={16} /></AppLink>
      </CatalogEmpty>
    </section>
  </div>;
}

function ArchivedBrand({ guitars }) {
  const name = guitars[0].brand;
  useEffect(() => { document.title = `${name} — ${t('p7.archive.label')} — Fretline`; }, [name]);
  return <div className="phase5-page">
    <DiscoveryHeading eyebrow={t('targeted.brand.archived')} title={name} serif description={t('p7.archive.brand')}
      breadcrumbs={[{ label: t('nav.brands'), href: '/brands' }, { label: name }]} />
    <section className="container-x phase5-body">
      <p className="archive-notice" role="note">{t('p7.archive.brandText')}</p>
      <ul className="mb-8 space-y-3">{guitars.map((guitar) => <li key={guitar.id}>
        <AppLink href={`/guitars/${guitar.slug}`} className="phase4-button">{guitar.brand} {guitar.name}<ArrowRightIcon size={16} /></AppLink>
      </li>)}</ul>
      <AppLink href="/brands" className="phase4-button is-gold">{t('p5.detail.back')}</AppLink>
    </section>
  </div>;
}

export default function BrandDetailPage() {
  const { id } = useParams();
  const brand = getBrandById(id);
  if (brand) return <BrandContent key={brand.id} brand={brand} />;
  const archived = ARCHIVED_GUITARS.filter((guitar) => slugify(guitar.brand) === id.toLowerCase());
  return archived.length ? <ArchivedBrand guitars={archived} /> : <MissingBrand />;
}
