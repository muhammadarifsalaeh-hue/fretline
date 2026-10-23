import { HOME_BRAND_ASSETS } from '@/data/homeBrandAssets';

/** Brand-level artwork only; a typographic name never claims to be an official mark. */
export default function BrandMark({ brand, className = '', loading = 'lazy' }) {
  const artwork = HOME_BRAND_ASSETS[brand.id];
  return (
    <span className={`brand-artwork-mark ${className}`.trim()} data-brand-mark={brand.id}>
      {artwork?.logo
        ? <img data-brand-logo data-brand-logo-kind="mark" src={artwork.logo} alt={brand.name}
          width="220" height="90" loading={loading} decoding="async" />
        : <span data-brand-fallback lang="en">{brand.name}</span>}
    </span>
  );
}
