import { t } from '@/i18n';
import { CATEGORIES } from '@/data/categories';
import { HOME_BRAND_ASSETS } from '@/data/homeBrandAssets';
import { brandCatalogUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import { ArrowRightIcon } from '@/components/ui/Icons';
import BrandMark from './BrandMark';

/** Editorial imagery identifies the brand, never a catalog model or official finish. */
export default function BrandCard({ brand }) {
  const artwork = HOME_BRAND_ASSETS[brand.id];
  return (
    <AppLink href={brandCatalogUrl(brand.name)} data-brand-id={brand.id}
      aria-label={t('p5.brands.cardAria', { brand: brand.name, n: brand.models })}
      className={`brand-directory-card brand-directory-card--${brand.id}`}>
      {artwork?.photo && <img className="brand-directory-photo" data-brand-photo={brand.id}
        src={artwork.photo} alt="" aria-hidden="true" width="600" height="640" loading="lazy" decoding="async" />}
      <span className="brand-directory-shade" aria-hidden="true" />
      <BrandMark brand={brand} className="brand-card-mark" />
      <div className="brand-directory-caption">
        <p className="brand-card-count" data-brand-count>
          <span className="brand-count-full">{t('p5.brands.models', { n: brand.models })}</span>
          <span className="brand-count-compact">{t('p5.brands.modelsShort', { n: brand.models })}</span>
        </p>
        <p className="brand-card-types">{brand.categories.map((id) => CATEGORIES.find((c) => c.id === id)?.name ?? id).join(' · ')}</p>
      </div>
      <span className="brand-card-arrow" aria-hidden="true"><ArrowRightIcon size={15} /></span>
    </AppLink>
  );
}
