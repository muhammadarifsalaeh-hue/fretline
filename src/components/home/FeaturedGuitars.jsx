import { t } from '@/i18n';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { GUITARS } from '@/data/guitars';
import GuitarCard from '@/components/guitar/GuitarCard';
import Reveal from '@/components/ui/Reveal';
import SectionHeading from '@/components/ui/SectionHeading';
import Tabs from '@/components/ui/Tabs';
import { ChevronLeftIcon, ChevronRightIcon } from '@/components/ui/Icons';
import { cn } from '@/utils/cn';
import { preferredScrollBehavior } from '@/utils/dom';

// Presentation order belongs to the homepage; catalogue records stay untouched.
const COLLECTION_IMAGE_IDS = ['yamaha-pacifica-612viifm', 'martin-d-28', 'yamaha-fg820-12'];
const COLLECTION = [
  ...COLLECTION_IMAGE_IDS.map((id) => GUITARS.find((guitar) => guitar.id === id)).filter(Boolean),
  ...GUITARS.filter((guitar) => guitar.featured && !COLLECTION_IMAGE_IDS.includes(guitar.id)),
];

const TABS = [
  { id: 'all', label: t('common.all') },
  { id: 'electric', label: t('category.electric') },
  { id: 'acoustic', label: t('category.acoustic') },
  { id: 'bass', label: t('category.bass') },
];

function ArrowButton({ direction, disabled, onClick }) {
  const Icon = direction === 'prev' ? ChevronLeftIcon : ChevronRightIcon;
  return (
    <button
      type="button"
      aria-label={direction === 'prev' ? t('feat.prev') : t('feat.next')}
      disabled={disabled}
      onClick={onClick}
      className={cn(
        'signature-collection-arrow grid h-12 w-12 place-items-center',
        disabled && 'cursor-not-allowed opacity-30',
      )}
    >
      <Icon />
    </button>
  );
}

export default function FeaturedGuitars() {
  const [tab, setTab] = useState('all');
  const trackRef = useRef(null);
  const [scroll, setScroll] = useState({ thumb: 1, ratio: 0, atStart: true, atEnd: true });

  // Keep every original featured model and every model in the category tabs.
  const items = useMemo(
    () => tab === 'all' ? COLLECTION : GUITARS.filter((guitar) => guitar.category === tab),
    [tab],
  );

  const update = useCallback(() => {
    const el = trackRef.current;
    if (!el) return;
    const max = el.scrollWidth - el.clientWidth;
    setScroll({
      thumb: el.scrollWidth > 0 ? Math.min(1, el.clientWidth / el.scrollWidth) : 1,
      ratio: max > 0 ? Math.max(0, Math.min(1, el.scrollLeft / max)) : 0,
      atStart: el.scrollLeft < 4,
      atEnd: max <= 0 || el.scrollLeft >= max - 4,
    });
  }, []);

  useEffect(() => {
    const el = trackRef.current;
    if (!el) return undefined;
    el.scrollTo({ left: 0, behavior: 'auto' });
    update();
    el.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    const observer = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(update) : null;
    observer?.observe(el);
    return () => {
      el.removeEventListener('scroll', update);
      window.removeEventListener('resize', update);
      observer?.disconnect();
    };
  }, [tab, update]);

  const scrollByPage = (dir) => {
    const el = trackRef.current;
    if (el) el.scrollBy({ left: dir * el.clientWidth * 0.8, behavior: preferredScrollBehavior() });
  };

  return (
    <section id="featured" className="featured-section signature-collection bg-ink">
      <div className="container-x">
        <Reveal className="signature-collection-heading">
          <p className="signature-section-eyebrow">{t('signature.collection.eyebrow')}</p>
          <SectionHeading title={t('signature.collection.title')} className="signature-collection-title" action={{ label: t('feat.viewAll'), href: '/guitars' }} />
        </Reveal>

        <div className="signature-collection-controls">
          <Tabs tabs={TABS} value={tab} onChange={setTab} label={t('feat.title')} idPrefix="featured-tab" panelId="featured-models" />
          <div className="signature-collection-arrows">
            <ArrowButton direction="prev" disabled={scroll.atStart} onClick={() => scrollByPage(-1)} />
            <ArrowButton direction="next" disabled={scroll.atEnd} onClick={() => scrollByPage(1)} />
          </div>
        </div>

        <div
          id="featured-models"
          role="tabpanel"
          aria-labelledby={`featured-tab-${tab}`}
          tabIndex={0}
          ref={trackRef}
          className="signature-collection-track"
        >
          {items.map((guitar) => (
            <div
              key={guitar.id}
              className="signature-collection-item"
            >
              <GuitarCard guitar={guitar} />
            </div>
          ))}
        </div>

        {/* progress bar บาง ๆ */}
        <div aria-hidden="true" className="signature-collection-progress relative h-px w-full bg-white/15">
          <div
            className="absolute top-0 h-px bg-gold transition-[left,width] duration-300"
            style={{ width: `${scroll.thumb * 100}%`, left: `${scroll.ratio * (1 - scroll.thumb) * 100}%` }}
          />
        </div>
      </div>
    </section>
  );
}
