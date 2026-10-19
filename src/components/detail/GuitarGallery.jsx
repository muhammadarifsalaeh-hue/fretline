import { t } from '@/i18n';
import { useRef, useState } from 'react';
import { cn } from '@/utils/cn';
import GuitarImage from '@/components/guitar/GuitarImage';
import ImagePlaceholder from '@/components/guitar/ImagePlaceholder';
import Badge from '@/components/ui/Badge';
import { ChevronLeftIcon, ChevronRightIcon, ExpandIcon } from '@/components/ui/Icons';
import ImageLightbox from './ImageLightbox';

/**
 * Gallery: รูปหลักขนาดใหญ่ + thumbnails (แสดงเฉพาะรูปจริงของรุ่นนี้)
 *  - Desktop: เลื่อนเมาส์เพื่อซูมดูรายละเอียด | คลิกเพื่อเปิดเต็มจอ
 *  - Mobile: ปัดซ้าย/ขวาเพื่อเปลี่ยนรูป | แตะเพื่อเปิดเต็มจอ
 *  - ยังไม่มีรูปจริง: แสดง "Photo coming soon" (ไม่เอารูปรุ่นอื่นมาแทน)
 */
export default function GuitarGallery({ guitar }) {
  const images = guitar.gallery;
  const name = `${guitar.brand} ${guitar.name}`;
  const [index, setIndex] = useState(0);
  const [zoom, setZoom] = useState(null);
  const [lightbox, setLightbox] = useState(false);
  const touchX = useRef(null);
  const count = images.length;
  const go = (d) => setIndex((i) => (i + d + count) % count);

  const frame = 'relative aspect-[4/5] overflow-hidden rounded-3xl bg-gradient-to-b from-[#2b2b2b] to-[#171717] ring-1 ring-white/5';
  const badge = guitar.badge && (
    <div className="pointer-events-none absolute left-5 top-5 z-[2]">
      <Badge type={guitar.badge} />
    </div>
  );

  // ยังไม่มีรูปจริงของรุ่นนี้
  if (count === 0) {
    return (
      <div>
        <div className={frame}>
          <ImagePlaceholder guitar={guitar} />
          {badge}
        </div>
        <p className="mt-4 text-sm text-mute">{t('gallery.soon')}</p>
      </div>
    );
  }

  const onMove = (e) => {
    if (!window.matchMedia('(hover: hover)').matches) return;
    const r = e.currentTarget.getBoundingClientRect();
    setZoom({ x: ((e.clientX - r.left) / r.width) * 100, y: ((e.clientY - r.top) / r.height) * 100 });
  };
  const onTouchEnd = (e) => {
    if (touchX.current == null) return;
    const dx = e.changedTouches[0].clientX - touchX.current;
    touchX.current = null;
    if (Math.abs(dx) > 50) go(dx < 0 ? 1 : -1);
  };

  return (
    <div>
      <div
        className={cn('group', frame)}
        onMouseMove={onMove}
        onMouseLeave={() => setZoom(null)}
        onTouchStart={(e) => (touchX.current = e.touches[0].clientX)}
        onTouchEnd={onTouchEnd}
      >
        {images.map((img, i) => (
          <div
            key={img.src}
            aria-hidden={i !== index}
            className="absolute inset-0"
            style={{
              opacity: i === index ? 1 : 0,
              transition: 'opacity 500ms cubic-bezier(0.22,1,0.36,1), transform 200ms ease-out',
              transform: i === index && zoom ? 'scale(1.9)' : 'scale(1)',
              transformOrigin: zoom ? `${zoom.x}% ${zoom.y}%` : '50% 50%',
            }}
          >
            <GuitarImage
              guitar={guitar}
              src={img.src}
              alt={`${name}, ${img.label}`}
              sizes="(min-width: 1024px) 58vw, 100vw"
              priority={i === 0}
              className="!bg-none absolute inset-0"
            />
          </div>
        ))}

        <button type="button" onClick={() => setLightbox(true)} aria-label={t('gallery.open')} className="absolute inset-0 z-[1] cursor-zoom-in" />
        {badge}

        <p className="pointer-events-none absolute bottom-5 left-5 z-[2] font-mono text-xs text-bone/80">
          {index + 1} / {count}
        </p>
        <span
          aria-hidden="true"
          className={cn(
            'pointer-events-none absolute bottom-4 right-4 z-[2] inline-flex items-center gap-2 rounded-full bg-ink/70 px-3 py-2 text-xs backdrop-blur transition-opacity duration-300',
            zoom && 'opacity-0',
          )}
        >
          <ExpandIcon size={14} /> {t('gallery.zoom')}
        </span>

        {count > 1 && (
          <>
            <button
              type="button"
              onClick={() => go(-1)}
              aria-label={t('gallery.prev')}
              className="absolute left-3 top-1/2 z-[2] grid h-11 w-11 -translate-y-1/2 place-items-center rounded-full bg-ink/70 opacity-0 backdrop-blur transition duration-300 hover:bg-ink focus-visible:opacity-100 group-hover:opacity-100 [@media(hover:none)]:opacity-100"
            >
              <ChevronLeftIcon />
            </button>
            <button
              type="button"
              onClick={() => go(1)}
              aria-label={t('gallery.next')}
              className="absolute right-3 top-1/2 z-[2] grid h-11 w-11 -translate-y-1/2 place-items-center rounded-full bg-ink/70 opacity-0 backdrop-blur transition duration-300 hover:bg-ink focus-visible:opacity-100 group-hover:opacity-100 [@media(hover:none)]:opacity-100"
            >
              <ChevronRightIcon />
            </button>
          </>
        )}
      </div>

      {count > 1 && (
        <ul className="mt-4 grid grid-cols-4 gap-3">
          {images.map((img, i) => (
            <li key={img.src}>
              <button
                type="button"
                onClick={() => setIndex(i)}
                aria-label={t('gallery.show', { label: img.label })}
                aria-current={i === index}
                className={cn(
                  'block aspect-square w-full overflow-hidden rounded-xl ring-2 transition duration-300',
                  i === index ? 'ring-gold' : 'opacity-60 ring-transparent hover:opacity-100',
                )}
              >
                <GuitarImage guitar={guitar} src={img.src} alt="" size="sm" className="h-full w-full" />
              </button>
            </li>
          ))}
        </ul>
      )}

      {images[index].credit && <p className="mt-3 text-xs text-mute">{images[index].credit}</p>}

      {lightbox && <ImageLightbox images={images} index={index} onIndex={setIndex} onClose={() => setLightbox(false)} name={name} guitar={guitar} />}
    </div>
  );
}
