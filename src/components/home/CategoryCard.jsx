import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import { categoryUrl } from '@/utils/routes';
import { ArrowUpRightIcon } from '@/components/ui/Icons';
import AppLink from '@/components/ui/AppLink';
import GuitarArt from '@/components/ui/GuitarArt';
import SmartImage from '@/components/ui/SmartImage';

export default function CategoryCard({ category, className = '' }) {
  return (
    <AppLink href={categoryUrl(category.id)} className={cn('signature-category-card', className)}>
      <div className="signature-category-art" aria-hidden="true">
        {category.image ? (
          <SmartImage src={category.image} alt="" fit="contain" className="h-full w-full" />
        ) : <GuitarArt type={category.id} className="h-full w-full" />}
      </div>
      <div className="signature-category-copy">
        <h3>{category.name}</h3>
        <p>{t('unit.models', { n: category.count })}</p>
      </div>
      <ArrowUpRightIcon size={16} className="signature-category-arrow" />
    </AppLink>
  );
}
