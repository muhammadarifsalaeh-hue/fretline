import { cn } from '@/utils/cn';
import SmartImage from '@/components/ui/SmartImage';
import ImagePlaceholder from './ImagePlaceholder';

/**
 * รูปสินค้ากีตาร์ (ใช้ทุกที่ที่แสดงรูปรุ่นใดรุ่นหนึ่ง)
 *  - object-contain + padding: เห็นกีตาร์ครบทั้งตัว ไม่ถูกยืด/ตัด/บิดเบี้ยว ในกรอบสัดส่วนเดียวกันทุกใบ
 *  - ไม่มีรูป หรือรูปโหลดไม่ได้ → แสดง ImagePlaceholder (ไม่เอารูปรุ่นอื่นมาแทน)
 *  props: guitar, src (ไม่ใส่ = ใช้รูปหลักของ guitar), alt, size ('md' | 'sm'), className, imgClassName
 */
export default function GuitarImage({ guitar, src, alt, size = 'md', priority = false, sizes, srcSet, className = '', imgClassName = '' }) {
  const url = src === undefined ? guitar?.image : src;
  const compact = size === 'sm';
  const fallback = <ImagePlaceholder guitar={guitar} compact={compact} />;
  const photo = guitar?.gallery?.find((entry) => entry.src === url);

  return (
    <SmartImage
      key={url ?? 'placeholder'}
      src={url}
      srcSet={srcSet ?? photo?.srcSet}
      sizes={sizes ?? (compact ? '96px' : '100vw')}
      alt={alt ?? photo?.alt ?? (guitar ? `${guitar.brand} ${guitar.name}` : '')}
      width={photo?.width}
      height={photo?.height}
      fit="contain"
      priority={priority}
      fallback={fallback}
      className={cn(!className.includes('absolute') && 'relative', 'bg-gradient-to-b from-[#2b2b2b] to-[#171717]', className)}
      imgClassName={cn(compact ? 'p-[6%]' : 'p-[7%]', imgClassName)}
    />
  );
}
