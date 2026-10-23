import { useEffect, useRef, useState } from 'react';
import { t } from '@/i18n';
import { BRANDS } from '@/data/brands';
import { HOME_BRAND_ORDER } from '@/data/homeBrandAssets';
import { brandCatalogUrl } from '@/utils/routes';
import { ArrowRightIcon, ChevronLeftIcon, ChevronRightIcon } from '@/components/ui/Icons';
import AppLink from '@/components/ui/AppLink';
import BrandMark from '@/components/brands/BrandMark';

const brands = HOME_BRAND_ORDER.map((id) => BRANDS.find((brand) => brand.id === id)).filter(Boolean);
const prefersReducedMotion = () => typeof window !== 'undefined'
  && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function BrandGroup({ decorative = false, onFocus }) {
  return (
    <div className="signature-marquee-group" data-marquee-primary={decorative ? undefined : ''}
      data-marquee-clone={decorative ? '' : undefined} aria-hidden={decorative ? true : undefined}>
      {brands.map((brand) => (
        <AppLink key={brand.id} href={brandCatalogUrl(brand.name)} data-brand-id={brand.id}
          className="signature-marquee-link" tabIndex={decorative ? -1 : undefined}
          aria-label={t('signature.brand.open', { brand: brand.name, n: brand.models })}
          onFocus={decorative ? undefined : onFocus}>
          {/* Small repeating marks load before they travel into the viewport. */}
          <BrandMark brand={brand} className="signature-marquee-mark" loading="eager" />
          <span className="signature-marquee-count">{t('unit.models', { n: brand.models })}</span>
        </AppLink>
      ))}
    </div>
  );
}

/** Restore the Phase B two-copy marquee; keep current Hero and catalog data. */
export default function Brands() {
  const viewport = useRef(null);
  const [paused, setPaused] = useState(false);
  const [manual, setManual] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(prefersReducedMotion);

  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const update = () => setReducedMotion(media.matches);
    media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, []);

  const revealFocusedBrand = (event) => {
    // A static unique row keeps every keyboard-focused link visible.
    if (!event.currentTarget.matches(':focus-visible')) return;
    const link = event.currentTarget;
    setManual(true);
    setPaused(true);
    requestAnimationFrame(() => link.scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: 'auto' }));
  };

  const browse = (direction) => {
    setManual(true);
    setPaused(true);
    requestAnimationFrame(() => {
      const row = viewport.current;
      if (!row) return;
      const max = row.scrollWidth - row.clientWidth;
      const destination = direction < 0 && row.scrollLeft <= 1 ? max
        : direction > 0 && row.scrollLeft >= max - 1 ? 0
          : row.scrollLeft + direction * row.clientWidth * .75;
      row.scrollTo({ left: destination, behavior: reducedMotion ? 'auto' : 'smooth' });
    });
  };

  const toggleMotion = () => {
    if (paused || manual) {
      if (viewport.current) viewport.current.scrollLeft = 0;
      setManual(false);
      setPaused(false);
    } else setPaused(true);
  };
  const stopped = paused || manual || reducedMotion;

  return (
    <section id="brands" className="signature-brand-marquee" aria-labelledby="home-brands-title"
      data-manual={manual ? 'true' : 'false'} data-paused={paused ? 'true' : 'false'}>
      <div className="container-x">
        <div className="signature-marquee-heading">
          <div><p className="signature-section-eyebrow">EXPLORE BY BRAND</p>
            <h2 id="home-brands-title">{t('brand.homeTitle')}</h2></div>
          <AppLink href="/brands" className="signature-marquee-view-all">{t('brand.viewAll')}<ArrowRightIcon size={16} /></AppLink>
        </div>
        <div className="signature-marquee-rail">
          <button type="button" className="signature-marquee-arrow" data-marquee-prev
            aria-label={t('signature.brand.previous')} aria-controls="home-brand-track" onClick={() => browse(-1)}><ChevronLeftIcon size={18} /></button>
          <div ref={viewport} className="signature-marquee-viewport" data-marquee-viewport>
            <div id="home-brand-track" className="signature-marquee-track animate-marquee">
              <BrandGroup onFocus={revealFocusedBrand} />
              <BrandGroup decorative />
            </div>
          </div>
          <button type="button" className="signature-marquee-arrow" data-marquee-next
            aria-label={t('signature.brand.next')} aria-controls="home-brand-track" onClick={() => browse(1)}><ChevronRightIcon size={18} /></button>
        </div>
        <div className="signature-marquee-footer">
          <button type="button" data-marquee-pause aria-pressed={stopped} disabled={reducedMotion}
            aria-controls="home-brand-track" onClick={toggleMotion}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
              {stopped ? <path d="m8 5 11 7-11 7Z" /> : <path d="M8 5v14M16 5v14" />}
            </svg>
            {t(reducedMotion ? 'signature.brand.reducedMotion' : stopped ? 'signature.brand.resume' : 'signature.brand.pause')}
          </button>
          <AppLink href="/brands#brand-credits">{t('signature.brand.credits')}</AppLink>
        </div>
      </div>
    </section>
  );
}
