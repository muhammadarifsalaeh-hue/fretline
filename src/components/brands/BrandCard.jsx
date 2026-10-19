import { t } from '@/i18n';
import { CATEGORIES } from '@/data/categories';
import { brandUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import { ArrowUpRightIcon } from '@/components/ui/Icons';

/** Use ordinary brand names when no licensed logo file is available. */
export default function BrandCard({ brand, index = 0 }) {
  return (
    <AppLink href={brandUrl(brand.name)} data-brand-id={brand.id}
      aria-label={t('p5.brands.cardAria', { brand: brand.name, n: brand.models })}
      style={{ animationDelay: `${(index % 9) * 40}ms` }}
      className="brand-directory-card animate-fade-up group">
      <ArrowUpRightIcon size={17} className="brand-card-arrow" />
      <div className="brand-card-mark">
        {brand.logo
          ? <img src={brand.logo} alt={brand.name} loading="lazy" width="180" height="64" />
          : <span className="font-serif" lang="en">{brand.name}</span>}
      </div>
      <p className="brand-card-count">{t('p5.brands.models', { n: brand.models })}</p>
      <p className="brand-card-types">{brand.categories.map((id) => CATEGORIES.find((c) => c.id === id)?.name ?? id).join(' · ')}</p>
    </AppLink>
  );
}
