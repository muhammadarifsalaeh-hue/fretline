import useDialogFocus from '@/hooks/useDialogFocus';
import { t } from '@/i18n';
import { useEffect, useRef } from 'react';
import { cn } from '@/utils/cn';
import { ChevronLeftIcon, ChevronRightIcon, CloseIcon } from '@/components/ui/Icons';
import GuitarImage from '@/components/guitar/GuitarImage';
import ImageAttribution from './ImageAttribution';

/** ดูรูปเต็มจอ: ปุ่มลูกศร / คีย์บอร์ด ← → / Esc ปิด */
export default function ImageLightbox({ images, index, onIndex, onClose, name, guitar }) {
  const dialogRef = useRef(null);
  useDialogFocus(dialogRef, true, onClose);
  const count = images.length;
  const next = () => onIndex((index + 1) % count);
  const prev = () => onIndex((index - 1 + count) % count);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'ArrowRight') onIndex((index + 1) % count);
      if (e.key === 'ArrowLeft') onIndex((index - 1 + count) % count);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [index, count, onClose, onIndex]);

  const current = images[index];

  return (
    <div ref={dialogRef} role="dialog" aria-modal="true" aria-label={t('gallery.dialogAria', { name })} className="fixed inset-0 z-[80] flex animate-fade-in flex-col bg-ink/95 backdrop-blur-md">
      <div className="flex items-center justify-between px-5 py-4 md:px-8">
        <p className="font-mono text-sm text-mute">
          {index + 1} / {count}
          <span className="ml-3 hidden text-bone/70 sm:inline">{current.label}</span>
        </p>
        <button
          type="button"
          onClick={onClose}
          aria-label={t('gallery.close')}
          className="grid h-11 w-11 place-items-center rounded-full bg-white/10 text-bone transition hover:bg-white/20"
        >
          <CloseIcon />
        </button>
      </div>

      <div className="relative min-h-0 flex-1 px-4 md:px-20">
        <GuitarImage
          key={current.src}
          guitar={guitar}
          src={current.src}
          alt={`${name}, ${current.label}`}
          sizes="100vw"
          priority
          className="h-full w-full !bg-none !bg-transparent"
          imgClassName="!p-0"
        />
        {count > 1 && (
          <>
            <button type="button" onClick={prev} aria-label={t('gallery.prev')} className="absolute left-3 top-1/2 grid h-12 w-12 -translate-y-1/2 place-items-center rounded-full bg-white/10 transition hover:bg-white/20 md:left-6">
              <ChevronLeftIcon />
            </button>
            <button type="button" onClick={next} aria-label={t('gallery.next')} className="absolute right-3 top-1/2 grid h-12 w-12 -translate-y-1/2 place-items-center rounded-full bg-white/10 transition hover:bg-white/20 md:right-6">
              <ChevronRightIcon />
            </button>
          </>
        )}
      </div>

      <div className="max-h-[30svh] overflow-y-auto px-5 pb-3 text-center"><ImageAttribution image={current} /></div>

      <ul className="flex shrink-0 gap-3 overflow-x-auto px-4 py-5 sm:justify-center">
        {images.map((img, i) => (
          <li key={img.src} className="shrink-0">
            <button
              type="button"
              onClick={() => onIndex(i)}
              aria-label={t('gallery.show', { label: img.label })}
              aria-current={i === index}
              className={cn('block h-16 w-16 overflow-hidden rounded-xl ring-2 transition duration-300 md:h-20 md:w-20', i === index ? 'ring-gold' : 'opacity-60 ring-transparent hover:opacity-100')}
            >
              <GuitarImage guitar={guitar} src={img.src} alt="" size="sm" className="h-full w-full" />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
