import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import ProductImage from './ProductImage';
import { getDevelopmentPreviewImage } from '@/utils/developmentImagePreview';

export { hasDevelopmentImagePreview } from '@/utils/developmentImagePreview';

/** Original user illustration. Provenance is metadata, never an image overlay. */
export default function DevelopmentImagePreview({ guitar, src, alt, compact = false, priority = false, className = '' }) {
  const image = getDevelopmentPreviewImage(guitar, src);
  if (!image) return null;
  return <div className={cn('development-image-preview h-full min-h-0 w-full overflow-hidden bg-black', className)}
    data-development-image-preview={guitar.id} data-preview-image={image.id}>
    <ProductImage key={image.src} src={image.src} alt={alt === '' ? '' : t('imagePreview.galleryAlt', { name: `${guitar.brand} ${guitar.name}`, color: image.label })}
      guitar={guitar} compact={compact} width={image.width} height={image.height} priority={priority} className="h-full w-full" />
  </div>;
}
