import { t } from '@/i18n';
import { useCallback, useRef, useState } from 'react';
import { cn } from '@/utils/cn';
import GuitarImage from '@/components/guitar/GuitarImage';
import ImagePlaceholder from '@/components/guitar/ImagePlaceholder';
import Badge from '@/components/ui/Badge';
import { ChevronLeftIcon, ChevronRightIcon, ExpandIcon } from '@/components/ui/Icons';
import ImageLightbox from './ImageLightbox';
import ImageAttribution from './ImageAttribution';
import { getDevelopmentImagePreview } from '@/utils/developmentImagePreview';

/** Shared gallery for registered photos, project artwork and local previews. */
export default function GuitarGallery({ guitar, activeIndex, onIndexChange }) {
  const developmentPreview = getDevelopmentImagePreview(guitar);
  const images = developmentPreview?.images ?? guitar.gallery ?? [];
  const name = `${guitar.brand} ${guitar.name}`;
  const [localIndex, setLocalIndex] = useState(0);
  const index = activeIndex ?? localIndex;
  const [lightbox, setLightbox] = useState(false);
  const setIndex = useCallback((value) => {
    if (onIndexChange) onIndexChange(value);
    else setLocalIndex(value);
  }, [onIndexChange]);
  const closeLightbox = useCallback(() => setLightbox(false), []);
  const touchX = useRef(null);
  const count = images.length;
  const current = images[index];
  const go = (direction) => { if (count > 1) setIndex((index + direction + count) % count); };
  const onTouchEnd = (event) => {
    if (touchX.current === null) return;
    const distance = event.changedTouches[0].clientX - touchX.current;
    touchX.current = null;
    if (Math.abs(distance) > 50) go(distance < 0 ? 1 : -1);
  };

  return (
    <div className="guitar-gallery">
      <div className={cn('gallery-layout', !count && 'is-placeholder')}>
        <div data-product-image-slot="square" className="product-image-slot gallery-main group"
          onTouchStart={(event) => { touchX.current = event.touches[0].clientX; }} onTouchEnd={onTouchEnd}>
          {current ? (
            <>
              <div className="absolute inset-0">
                <GuitarImage key={current.src} guitar={guitar} src={current.src} alt={`${name}, ${current.label}`}
                  sizes="(min-width: 1024px) 40vw, (min-width: 768px) 45vw, 90vw" priority className="absolute inset-0" />
              </div>
              <button type="button" aria-label={t('gallery.open')} onClick={() => setLightbox(true)} className="absolute inset-0 z-[1] cursor-zoom-in" />
              <p className="pointer-events-none absolute bottom-4 left-4 z-[2] font-mono text-xs text-bone/80" role="status">{index + 1} / {count}</p>
              <span aria-hidden="true" className="pointer-events-none absolute bottom-4 right-4 z-[2] flex items-center gap-2 rounded-lg bg-ink/80 px-3 py-2 text-xs"><ExpandIcon size={14} />{t('gallery.zoom')}</span>
              {count > 1 && [-1, 1].map((direction) => (
                <button key={direction} type="button" onClick={() => go(direction)} aria-label={t(direction < 0 ? 'gallery.prev' : 'gallery.next')}
                  className={cn('absolute top-1/2 z-[2] grid h-11 w-11 -translate-y-1/2 place-items-center rounded-full bg-ink/80 text-bone opacity-0 transition-opacity group-hover:opacity-100 focus-visible:opacity-100 [@media(hover:none)]:opacity-100', direction < 0 ? 'left-2' : 'right-2')}>
                  {direction < 0 ? <ChevronLeftIcon /> : <ChevronRightIcon />}
                </button>
              ))}
            </>
          ) : <ImagePlaceholder guitar={guitar} />}
          {guitar.badge && <div className="pointer-events-none absolute left-4 top-4 z-[2]"><Badge type={guitar.badge} /></div>}
        </div>
        {count > 0 && <ul className="gallery-thumbnails" aria-label={t('gallery.thumbnails')}>
          {images.map((image, value) => (
            <li key={image.src}>
              <button type="button" aria-label={t('gallery.show', { label: image.label })} aria-current={value === index ? 'true' : undefined}
                onClick={() => setIndex(value)} className={cn('gallery-thumbnail', value === index && 'is-active')}>
                <GuitarImage guitar={guitar} src={image.src} alt="" size="sm" className="h-full w-full" />
              </button>
            </li>
          ))}
        </ul>}
      </div>
      {(developmentPreview || current?.kind === 'illustration') && current && <p className="mt-3 text-center text-xs tracking-wide text-gold" aria-live="polite" data-preview-selection={developmentPreview ? true : undefined} data-gallery-selection>{current.label}</p>}
      <ImageAttribution image={current} />
      {lightbox && <ImageLightbox images={images} index={index} onIndex={setIndex} onClose={closeLightbox} name={name} guitar={guitar} />}
    </div>
  );
}
