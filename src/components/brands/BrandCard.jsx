import { useState } from 'react';
import { t } from '@/i18n';
import { CATEGORIES } from '@/data/categories';
import { HOME_BRAND_ASSETS } from '@/data/homeBrandAssets';
import { brandCatalogUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import { ArrowRightIcon, GuitarIcon } from '@/components/ui/Icons';
import BrandMark from './BrandMark';

/** Editorial imagery identifies the brand, never a catalog model or official finish. */
export default function BrandCard({ brand }) {
  const artwork = HOME_BRAND_ASSETS[brand.id];
  const [photoFailed, setPhotoFailed] = useState(false);
  const [logoFailed, setLogoFailed] = useState(false);
  const showPhoto = Boolean(artwork?.photo) && !photoFailed;
  const recoverLogo = (event) => {
    // Capture descendant image errors without changing the shared Home mark.
    if (event.target.hasAttribute?.('data-brand-logo')) setLogoFailed(true);
  };
  return (
    <AppLink href={brandCatalogUrl(brand.name)} data-brand-id={brand.id}
      data-photo-status={showPhoto ? 'available' : 'error'}
      data-logo-status={logoFailed ? 'error' : 'available'} onErrorCapture={recoverLogo}
      aria-label={t('p5.brands.cardAria', { brand: brand.name, n: brand.models })}
      className={`brand-directory-card brand-directory-card--${brand.id}`}>
      {showPhoto ? <img className="brand-directory-photo" data-brand-photo={brand.id}
        src={artwork.photo} alt="" aria-hidden="true" width="600" height="640" loading="lazy" decoding="async"
        onError={() => setPhotoFailed(true)} />
        : <div className="brand-directory-photo-fallback" data-brand-photo-fallback={brand.id} aria-hidden="true">
          <GuitarIcon size={76} />
          <span className="brand-directory-photo-fallback-message">{t('p5.brands.imageUnavailable')}</span>
        </div>}
      <span className="brand-directory-shade" aria-hidden="true" />
      {logoFailed
        ? <span className="brand-artwork-mark brand-card-mark" data-brand-mark={brand.id}>
          <span data-brand-fallback lang="en">{brand.name}</span>
        </span>
        : <BrandMark brand={brand} className="brand-card-mark" />}
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
