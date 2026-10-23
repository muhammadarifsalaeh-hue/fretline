import { BRANDS } from '@/data/brands';
import { CATEGORIES } from '@/data/categories';
import { GUITARS } from '@/data/guitars';
import { MAX_COMPARE } from '@/context/ShopContext';
import { t } from '@/i18n';

/** Catalogue facts stay in normal flow and always come from the current data. */
export default function HeroStats() {
  const items = [
    { value: GUITARS.length, label: t('stat.models') },
    { value: BRANDS.length, label: t('stat.brands') },
    { value: CATEGORIES.filter((category) => category.count > 0).length, label: t('stat.types') },
    { value: MAX_COMPARE, label: t('stat.compare') },
  ];

  return (
    <div className="signature-stats">
      <div className="signature-stats-inner container-x">
        <dl className="signature-stats-list">
          {items.map((item) => (
            <div key={item.label}>
              <dt>{item.label}</dt>
              <dd>{item.value}</dd>
            </div>
          ))}
        </dl>
        <p className="signature-stats-note">{t('signature.stats.note')}</p>
      </div>
    </div>
  );
}
