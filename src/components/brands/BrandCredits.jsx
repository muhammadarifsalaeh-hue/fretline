import { t } from '@/i18n';
import { BRANDS } from '@/data/brands';
import { HOME_BRAND_ASSETS, HOME_BRAND_ORDER } from '@/data/homeBrandAssets';

const orderedBrands = [...BRANDS].sort((a, b) => HOME_BRAND_ORDER.indexOf(a.id) - HOME_BRAND_ORDER.indexOf(b.id));

/** Credits follow the editorial art wherever it is displayed, independently of product data. */
export default function BrandCredits() {
  return (
    <details id="brand-credits" className="brand-artwork-credits">
      <summary>{t('signature.brand.credits')}</summary>
      <div>
        <p>{t('signature.brand.photoNote')}</p>
        <p>{t('signature.brand.trademarkNote')}</p>
        <ul>
          {orderedBrands.map((brand) => {
            const artwork = HOME_BRAND_ASSETS[brand.id];
            return <li key={brand.id}>
              <strong>{brand.name}</strong>{' — '}
              {artwork?.photoSource && <>
                <a href={artwork.photoSource} target="_blank" rel="noopener noreferrer">{artwork.author}</a>{' · '}
                <a href={artwork.licenseUrl} target="_blank" rel="noopener noreferrer">{artwork.license}</a>{'. '}
              </>}
              {artwork?.logoSource
                ? <a href={artwork.logoSource} target="_blank" rel="noopener noreferrer">{t('signature.brand.logoCredit')}</a>
                : t(artwork?.logoKind === 'typographic' ? 'signature.brand.typeCredit' : 'signature.brand.pending')}
            </li>;
          })}
        </ul>
      </div>
    </details>
  );
}
