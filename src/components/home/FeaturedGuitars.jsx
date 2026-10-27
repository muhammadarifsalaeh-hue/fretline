import { LANG, t } from '@/i18n';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { GUITARS } from '@/data/guitars';
import GuitarCard from '@/components/guitar/GuitarCard';
import AppLink from '@/components/ui/AppLink';
import Tabs from '@/components/ui/Tabs';
import { ArrowRightIcon, ChevronLeftIcon, ChevronRightIcon } from '@/components/ui/Icons';
import { cn } from '@/utils/cn';
import { preferredScrollBehavior } from '@/utils/dom';
import { sortGuitars } from '@/utils/guitarSort';

// Presentation order belongs to the homepage; catalogue records stay untouched.
const COLLECTION_IMAGE_IDS = ['yamaha-pacifica-612viifm', 'martin-d-28', 'yamaha-fg820-12'];
const COLLECTION = [
  ...COLLECTION_IMAGE_IDS.map((id) => GUITARS.find((guitar) => guitar.id === id)).filter(Boolean),
  ...GUITARS.filter((guitar) => guitar.featured && !COLLECTION_IMAGE_IDS.includes(guitar.id)),
];

const TABS = [
  { id: 'popular', label: LANG === 'en' ? 'Featured' : 'ยอดนิยม' },
  { id: 'new', label: LANG === 'en' ? 'Recently added' : 'รุ่นใหม่' },
  { id: 'price-desc', label: LANG === 'en' ? 'Price: high–low' : 'ราคาสูง–ต่ำ' },
  { id: 'price-asc', label: LANG === 'en' ? 'Price: low–high' : 'ราคาต่ำ–สูง' },
];

// "New" means recently added to this catalog, never an inferred release date.
const RECENTLY_ADDED = GUITARS.filter((guitar) => guitar.intake?.batch)
  .sort((a, b) => b.intake.batch.localeCompare(a.intake.batch));

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
  const [tab, setTab] = useState('popular');
  const trackRef = useRef(null);
  const [scroll, setScroll] = useState({ thumb: 1, ratio: 0, atStart: true, atEnd: true });

  const items = useMemo(
    () => tab === 'popular' ? COLLECTION : tab === 'new' ? RECENTLY_ADDED : sortGuitars(GUITARS, tab, { verifiedOnly: true }),
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
    <section id="featured" className="featured-section signature-collection bg-ink" aria-labelledby="home-featured-title">
      <div className="container-x">
        <div className="signature-collection-controls">
          <h2 id="home-featured-title">{LANG === 'en' ? 'Guitars to discover' : 'แนะนำกีตาร์ยอดนิยม'}</h2>
          <Tabs tabs={TABS} value={tab} onChange={setTab} label={t('feat.title')} idPrefix="featured-tab" panelId="featured-models" />
          <AppLink href="/guitars" className="home-featured-view-all">{t('feat.viewAll')}<ArrowRightIcon size={16} /></AppLink>
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
          {items.length === 0 && <p className="home-featured-empty">{LANG === 'en' ? 'No recently added models are confirmed yet.' : 'ยังไม่มีข้อมูลรุ่นที่เพิ่มใหม่ที่ยืนยันแล้ว'}</p>}
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
