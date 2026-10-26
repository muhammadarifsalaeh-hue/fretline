import { t } from '@/i18n';
import { hasManufacturerRrp, hasListedRetailerPrice } from '@/utils/dataTrust';

export default function PriceSourceNote({ guitar, full = false, linkTabIndex }) {
  const rrp = hasManufacturerRrp(guitar);
  const retailer = hasListedRetailerPrice(guitar);
  if (!rrp && !retailer) return null;
  return <p className="price-source-note relative z-[1] mt-2 text-[11px] leading-5 text-mute">
    <a href={guitar.priceSource.url} target="_blank" rel="noopener noreferrer" tabIndex={linkTabIndex} className="text-gold hover:underline">
      {rrp ? t('pricing.yamahaThailandRrp') : `${guitar.priceSource.retailer} · ${t('pricing.retailerPrice')}`}
    </a>
    {full && <><span className="block">{t(rrp ? 'pricing.rrpDisclaimer' : 'pricing.retailerDisclaimer')}</span><span className="block">{t('pricing.checkedOn', { date: guitar.priceSource.verifiedOn })}</span>{guitar.priceSource.availability === 'discontinued' && <span className="block">{t('pricing.discontinued')}</span>}</>}
  </p>;
}
