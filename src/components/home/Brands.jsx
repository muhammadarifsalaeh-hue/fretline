import { t } from '@/i18n';
import { BRANDS } from '@/data/brands';
import { HOME_BRAND_ORDER } from '@/data/homeBrandAssets';
import { brandCatalogUrl } from '@/utils/routes';
import { ArrowRightIcon } from '@/components/ui/Icons';
import AppLink from '@/components/ui/AppLink';
import BrandMark from '@/components/brands/BrandMark';
import useBrandMarquee from '@/hooks/useBrandMarquee';

const brands = HOME_BRAND_ORDER.map((id) => BRANDS.find((brand) => brand.id === id)).filter(Boolean);

function BrandGroup({ decorative = false }) {
  return <div className="signature-marquee-group" data-marquee-primary={decorative ? undefined : ''}
    data-marquee-clone={decorative ? '' : undefined} aria-hidden={decorative ? true : undefined}>
    {brands.map((brand) => <AppLink key={brand.id} href={brandCatalogUrl(brand.name)} data-brand-id={brand.id}
      className="signature-marquee-link" tabIndex={decorative ? -1 : undefined} draggable="false"
      aria-label={t('signature.brand.open', { brand: brand.name, n: brand.models })}>
      <BrandMark brand={brand} className="signature-marquee-mark" loading="eager" />
      <span className="signature-marquee-count">{t('unit.models', { n: brand.models })}</span>
    </AppLink>)}
  </div>;
}

/** One continuous rail: native touch swipe, mouse drag and automatic movement. */
export default function Brands() {
  const viewport = useBrandMarquee();
  return <section id="brands" className="signature-brand-marquee" aria-labelledby="home-brands-title">
    <div className="container-x">
      <div className="signature-marquee-heading">
        <div><p className="signature-section-eyebrow">EXPLORE BY BRAND</p>
          <h2 id="home-brands-title">{t('brand.homeTitle')}</h2></div>
        <AppLink href="/brands" className="signature-marquee-view-all">{t('brand.viewAll')}<ArrowRightIcon size={16} /></AppLink>
      </div>
      <div className="signature-marquee-rail">
        <div ref={viewport} className="signature-marquee-viewport" data-marquee-viewport>
          <div id="home-brand-track" className="signature-marquee-track">
            <BrandGroup decorative />
            <BrandGroup />
            <BrandGroup decorative />
          </div>
        </div>
      </div>
      <div className="signature-marquee-footer"><AppLink href="/brands#brand-credits">{t('signature.brand.credits')}</AppLink></div>
    </div>
  </section>;
}
