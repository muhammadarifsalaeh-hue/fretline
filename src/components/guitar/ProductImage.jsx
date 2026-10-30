import { cn } from '@/utils/cn';
import SmartImage from '@/components/ui/SmartImage';
import ImagePlaceholder from './ImagePlaceholder';
import '@/styles/product-images.css';

/** One presentation contract for product photos, uploads and empty frames. */
export default function ProductImage({ guitar, src, alt = '', width, height, sizes = '100vw', srcSet, priority = false, compact = false, className = '', imgClassName = '' }) {
  const cap = (value) => Number.isFinite(value) && value > 0 ? `min(100%, ${value}px)` : '100%';
  return <SmartImage key={src ?? 'empty'} src={src} alt={alt} width={width} height={height}
    sizes={sizes} srcSet={srcSet} priority={priority} fit="contain"
    containerStyle={{ background: '#000000' }}
    className={cn('guitar-image-frame', !className.includes('absolute') && 'relative', className)}
    imgClassName={imgClassName}
    imageStyle={{ position: 'absolute', inset: 0, margin: 'auto', width: '100%', height: '100%',
      maxWidth: cap(width), maxHeight: cap(height), padding: 0, transform: 'none', objectFit: 'contain', objectPosition: 'center' }}
    fallback={<ImagePlaceholder guitar={guitar} compact={compact} />} />;
}
