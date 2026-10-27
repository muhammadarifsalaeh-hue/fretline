import { BRANDS } from '@/data/brands';
import { CATEGORIES } from '@/data/categories';
import { GUITARS } from '@/data/guitars';
import { MAX_COMPARE } from '@/context/ShopContext';
import { t } from '@/i18n';
import { CompareIcon, GridIcon, GuitarIcon, TagIcon } from '@/components/ui/Icons';

/** Catalogue facts stay in normal flow and always come from the current data. */
export default function HeroStats() {
  const items = [
    { value: GUITARS.length, label: t('stat.models'), Icon: GuitarIcon },
    { value: BRANDS.length, label: t('stat.brands'), Icon: TagIcon },
    { value: CATEGORIES.filter((category) => category.count > 0).length, label: t('stat.types'), Icon: GridIcon },
    { value: MAX_COMPARE, label: t('stat.compare'), Icon: CompareIcon },
  ];

  return (
    <div className="signature-stats">
      <div className="signature-stats-inner container-x">
        <dl className="signature-stats-list">
          {items.map(({ value, label, Icon }) => (
            <div key={label}>
              <dt><Icon size={28} className="signature-stat-icon" />{label}</dt>
              <dd>{value}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  );
}
