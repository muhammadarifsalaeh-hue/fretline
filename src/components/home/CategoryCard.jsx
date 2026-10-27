import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import { categoryUrl } from '@/utils/routes';
import { ArrowUpRightIcon } from '@/components/ui/Icons';
import AppLink from '@/components/ui/AppLink';
import SmartImage from '@/components/ui/SmartImage';
import { HOME_DISCOVERY_ASSETS } from '@/data/homeDiscoveryAssets';

export default function CategoryCard({ category, className = '' }) {
  const photo = HOME_DISCOVERY_ASSETS[category.id];
  return (
    <AppLink href={categoryUrl(category.id)} className={cn('signature-category-card', className)}>
      <div className="signature-category-art" aria-hidden="true">
        <SmartImage src={photo.src} srcSet={photo.srcSet} sizes="(min-width: 1024px) 160px, 130px"
          width={photo.width} height={photo.height} alt="" fit="contain" className="h-full w-full" />
      </div>
      <div className="signature-category-copy">
        <h3>{category.name}</h3>
        <p>{t('unit.models', { n: category.count })}</p>
      </div>
      <ArrowUpRightIcon size={16} className="signature-category-arrow" />
    </AppLink>
  );
}
