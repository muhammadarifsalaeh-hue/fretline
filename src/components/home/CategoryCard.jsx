import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import { categoryUrl } from '@/utils/routes';
import { ArrowRightIcon } from '@/components/ui/Icons';
import AppLink from '@/components/ui/AppLink';
import { HOME_CATEGORY_ASSETS } from '@/data/homeCategoryAssets';

// Instrument-only bounds after rotation, including a small safety margin.
// These are display coordinates, not guitar specifications or catalog data.
const ART_FRAMES = {
  electric: { angle: 61, bounds: [-634.01, 131.61, 64.95, 596.98] },
  acoustic: { angle: 61, bounds: [-439.67, 80.48, 57.85, 429.84] },
  classical: { angle: 32, bounds: [-293.85, 195.16, 325.93, 665.44] },
  bass: { angle: 61, bounds: [-794.45, 56.19, 52.38, 716.3] },
};

export default function CategoryCard({ category, className = '' }) {
  const photo = HOME_CATEGORY_ASSETS[category.id];
  // Fit the complete existing instrument photograph into the reserved artwork
  // area. Rotation is presentation only; no product image or metadata changes.
  const { angle, bounds: [left, top, right, bottom] } = ART_FRAMES[category.id];
  const scale = Math.min(154 / (right - left), 108 / (bottom - top));
  return (
    <AppLink href={categoryUrl(category.id)} className={cn('signature-category-card signature-category-pill', `signature-category-card--${category.id}`, className)}>
      <svg className="category-pill-art" viewBox="0 0 160 112" aria-hidden="true" focusable="false">
        <image href={photo.src} width={photo.width} height={photo.height}
          transform={`translate(80 56) scale(${scale}) translate(${-(left + right) / 2} ${-(top + bottom) / 2}) rotate(${angle})`} preserveAspectRatio="xMidYMid meet" />
      </svg>
      <div className="signature-category-copy">
        <h3>{category.name}</h3>
        <p>{t('unit.models', { n: category.count })}</p>
      </div>
      <ArrowRightIcon size={16} className="signature-category-arrow" />
    </AppLink>
  );
}
