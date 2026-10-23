import { t } from '@/i18n';
import { BRANDS } from '@/data/brands';
import { HOME_BRAND_ASSETS, HOME_BRAND_ORDER } from '@/data/homeBrandAssets';
import { brandUrl } from '@/utils/routes';
import { ArrowRightIcon } from '@/components/ui/Icons';
import AppLink from '@/components/ui/AppLink';

// Presentation order only; counts and destinations always use the live catalog.
const rank = (id) => {
  const index = HOME_BRAND_ORDER.indexOf(id);
  return index < 0 ? HOME_BRAND_ORDER.length : index;
};
const orderedBrands = [...BRANDS].sort((a, b) => rank(a.id) - rank(b.id));

function BrandCard({ brand }) {
  const artwork = HOME_BRAND_ASSETS[brand.id] ?? {};
  return (
    <AppLink href={brandUrl(brand.name)}
      className={`signature-brand-card signature-brand-card--${brand.id}`}
      data-brand-id={brand.id}
      aria-label={t('signature.brand.open', { brand: brand.name, n: brand.models })}>
      {artwork.photo && <img className="signature-brand-photo" src={artwork.photo} alt="" aria-hidden="true"
        width="600" height="640" loading="lazy" decoding="async" />}
      <span className="signature-brand-shade" aria-hidden="true" />
      <span className="signature-brand-mark">
        {artwork.logoKind === 'photographic' ? (
          <span className="signature-brand-photo-mark" data-brand-logo-frame>
            <img data-brand-logo data-brand-logo-kind="photographic" src={artwork.logo} alt={brand.name}
              width="1920" height="1280" loading="lazy" decoding="async" />
          </span>
        ) : artwork.logo ? <img data-brand-logo src={artwork.logo} alt={brand.name} width="220" height="90" loading="lazy" decoding="async" />
          : <span data-brand-fallback>{brand.name}</span>}
      </span>
      <span className="signature-brand-count" data-brand-count>
        <span aria-hidden="true" />{t('signature.brand.count', { n: brand.models })}
      </span>
      <span className="signature-brand-arrow" aria-hidden="true"><ArrowRightIcon size={15} /></span>
    </AppLink>
  );
}

function BrandCredits() {
  return (
    <details className="signature-brand-credits">
      <summary>{t('signature.brand.credits')}</summary>
      <div>
        <p>{t('signature.brand.photoNote')}</p>
        <p>{t('signature.brand.trademarkNote')}</p>
        <ul>
          {orderedBrands.map((brand) => {
            const asset = HOME_BRAND_ASSETS[brand.id];
            return <li key={brand.id}>
              <strong>{brand.name}</strong>{' — '}
              {asset?.photoSource && <><a href={asset.photoSource} target="_blank" rel="noreferrer">{asset.author}</a>{' · '}<a href={asset.licenseUrl} target="_blank" rel="noreferrer">{asset.license}</a>{'. '}</>}
              {asset?.logoSource ? <a href={asset.logoSource} target="_blank" rel="noreferrer">{t(asset.logoKind === 'photographic' ? 'signature.brand.photoMarkCredit' : 'signature.brand.logoCredit')}</a> : t('signature.brand.pending')}
            </li>;
          })}
        </ul>
      </div>
    </details>
  );
}

export default function Brands() {
  return (
    <section id="brands" className="signature-brands" aria-labelledby="signature-brands-heading">
      <div className="signature-brand-header-art" aria-hidden="true">
        <img src={HOME_BRAND_ASSETS.fender.photo} width="1200" height="700" alt="" loading="lazy" decoding="async" />
      </div>
      <div className="signature-brand-inner">
        <div className="signature-brand-heading">
          <p className="signature-section-eyebrow">02 / EXPLORE BY BRAND</p>
          <h2 id="signature-brands-heading"><span>{t('signature.brand.titleLead')}</span><span>{t('signature.brand.titleEnd')}</span></h2>
          <div className="signature-brand-heading-bottom">
            <p>{t('signature.brand.description')}</p>
            <AppLink href="/brands" className="signature-brand-view-all">{t('brand.viewAll')}<span aria-hidden="true"><ArrowRightIcon size={16} /></span></AppLink>
          </div>
        </div>
        <div className="signature-brand-grid" data-brand-grid>
          {orderedBrands.map((brand) => <BrandCard key={brand.id} brand={brand} />)}
        </div>
        <BrandCredits />
      </div>
    </section>
  );
}
