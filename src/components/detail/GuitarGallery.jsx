import { t } from '@/i18n';
import { useCallback, useRef, useState } from 'react';
import { cn } from '@/utils/cn';
import GuitarImage from '@/components/guitar/GuitarImage';
import ImagePlaceholder from '@/components/guitar/ImagePlaceholder';
import Badge from '@/components/ui/Badge';
import { ChevronLeftIcon, ChevronRightIcon, ExpandIcon } from '@/components/ui/Icons';
import ImageLightbox from './ImageLightbox';

/** Genuine model photos only. Desktop thumbnail rail; mobile swipe and lightbox. */
export default function GuitarGallery({ guitar }) {
  const images = guitar.gallery ?? [];
  const name = `${guitar.brand} ${guitar.name}`;
  const [index, setIndex] = useState(0);
  const [zoom, setZoom] = useState(null);
  const [lightbox, setLightbox] = useState(false);
  const closeLightbox = useCallback(() => setLightbox(false), []);
  const touchX = useRef(null);
  const count = images.length;
  const current = images[index];
  const go = (direction) => { if (count > 1) setIndex((value) => (value + direction + count) % count); };
  const onMove = (event) => {
    if (!count || !window.matchMedia('(hover: hover)').matches || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const rect = event.currentTarget.getBoundingClientRect();
    setZoom({ x: ((event.clientX - rect.left) / rect.width) * 100, y: ((event.clientY - rect.top) / rect.height) * 100 });
  };
  const onTouchEnd = (event) => {
    if (touchX.current === null) return;
    const distance = event.changedTouches[0].clientX - touchX.current;
    touchX.current = null;
    if (Math.abs(distance) > 50) go(distance < 0 ? 1 : -1);
  };

  return (
    <div className="guitar-gallery">
      <div className="gallery-layout">
        <div className="gallery-main group" onMouseMove={onMove} onMouseLeave={() => setZoom(null)}
          onTouchStart={(event) => { touchX.current = event.touches[0].clientX; }} onTouchEnd={onTouchEnd}>
          {current ? (
            <>
              <div className="absolute inset-0 transition-transform duration-200" style={{ transform: zoom ? 'scale(1.8)' : 'scale(1)', transformOrigin: zoom ? `${zoom.x}% ${zoom.y}%` : 'center' }}>
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
        <ul className="gallery-thumbnails" aria-label={t('gallery.thumbnails')}>
          {count ? images.map((image, value) => (
            <li key={image.src}>
              <button type="button" aria-label={t('gallery.show', { label: image.label })} aria-current={value === index ? 'true' : undefined}
                onClick={() => { setIndex(value); setZoom(null); }} className={cn('gallery-thumbnail', value === index && 'is-active')}>
                <GuitarImage guitar={guitar} src={image.src} alt="" size="sm" className="h-full w-full" />
              </button>
            </li>
          )) : <li><div className="gallery-thumbnail relative" aria-label={t('gallery.soon')}><ImagePlaceholder guitar={guitar} compact /></div></li>}
        </ul>
      </div>
      {!count && <p className="mt-3 text-xs leading-relaxed text-mute">{t('gallery.soon')}</p>}
      {current?.credit && <p className="mt-3 text-xs text-mute">{current.credit}</p>}
      {lightbox && <ImageLightbox images={images} index={index} onIndex={setIndex} onClose={closeLightbox} name={name} guitar={guitar} />}
    </div>
  );
}
