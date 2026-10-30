import ProductImage from './ProductImage';
import DevelopmentImagePreview from './DevelopmentImagePreview';
import { getDevelopmentPreviewImage } from '@/utils/developmentImagePreview';
import useDevelopmentImagePreview from '@/hooks/useDevelopmentImagePreview';

/**
 * รูปสินค้ากีตาร์ (ใช้ทุกที่ที่แสดงรูปรุ่นใดรุ่นหนึ่ง)
 *  - square, black, contained: no crop, fixed zoom or extra image padding
 *  - ไม่มีรูป หรือรูปโหลดไม่ได้ → แสดง ImagePlaceholder (ไม่เอารูปรุ่นอื่นมาแทน)
 *  props: guitar, src (ไม่ใส่ = ใช้รูปหลักของ guitar), alt, size ('md' | 'sm'), className, imgClassName
 */
export default function GuitarImage({ guitar, src, alt, size = 'md', priority = false, sizes, srcSet, className = '', imgClassName = '' }) {
  useDevelopmentImagePreview(guitar);
  const url = src === undefined ? guitar?.image : src;
  const compact = size === 'sm';
  const photo = guitar?.gallery?.find((entry) => entry.src === url);

  if (getDevelopmentPreviewImage(guitar, src)) return <DevelopmentImagePreview guitar={guitar} src={src} alt={alt} compact={compact} priority={priority} className={className} />;

  return (
    <ProductImage
      key={url ?? 'placeholder'}
      src={url}
      srcSet={srcSet ?? photo?.srcSet}
      sizes={sizes ?? (compact ? '96px' : '100vw')}
      alt={alt ?? photo?.alt ?? (guitar ? `${guitar.brand} ${guitar.name}` : '')}
      width={photo?.width}
      height={photo?.height}
      priority={priority}
      guitar={guitar}
      compact={compact}
      className={className}
      imgClassName={imgClassName}
    />
  );
}
