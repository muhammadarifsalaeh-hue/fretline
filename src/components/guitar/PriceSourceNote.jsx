import { t } from '@/i18n';
import { hasManufacturerRrp } from '@/utils/dataTrust';

export default function PriceSourceNote({ guitar, full = false, linkTabIndex }) {
  if (!hasManufacturerRrp(guitar)) return null;
  return <p className="price-source-note relative z-[1] mt-2 text-[11px] leading-5 text-mute">
    <a href={guitar.priceSource.url} target="_blank" rel="noopener noreferrer" tabIndex={linkTabIndex} className="text-gold hover:underline">
      {t('pricing.yamahaThailandRrp')}
    </a>
    {full && <><span className="block">{t('pricing.rrpDisclaimer')}</span><span className="block">{t('pricing.checkedOn', { date: guitar.priceSource.verifiedOn })}</span></>}
  </p>;
}
