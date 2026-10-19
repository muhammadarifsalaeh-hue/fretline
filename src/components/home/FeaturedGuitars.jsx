import { t } from '@/i18n';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { GUITARS } from '@/data/guitars';
import GuitarCard from '@/components/guitar/GuitarCard';
import Reveal from '@/components/ui/Reveal';
import SectionHeading from '@/components/ui/SectionHeading';
import Tabs from '@/components/ui/Tabs';
import { ChevronLeftIcon, ChevronRightIcon } from '@/components/ui/Icons';
import { cn } from '@/utils/cn';

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
        'grid h-12 w-12 place-items-center rounded-full border border-white/20 text-bone transition duration-300 ease-premium',
        disabled ? 'cursor-not-allowed opacity-30' : 'hover:bg-bone hover:text-ink active:scale-95',
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

  // แท็บ All = เฉพาะรุ่นแนะนำ, แท็บอื่น = ทุกรุ่นในหมวดนั้น
  const items = useMemo(
    () => GUITARS.filter((g) => (tab === 'all' ? g.featured : g.category === tab)),
    [tab],
  );

  const update = useCallback(() => {
    const el = trackRef.current;
    if (!el) return;
    const max = el.scrollWidth - el.clientWidth;
    setScroll({
      thumb: Math.min(1, el.clientWidth / el.scrollWidth),
      ratio: max > 0 ? el.scrollLeft / max : 0,
      atStart: el.scrollLeft < 4,
      atEnd: max <= 0 || el.scrollLeft >= max - 4,
    });
  }, []);

  useEffect(() => {
    const el = trackRef.current;
    if (!el) return undefined;
    el.scrollTo({ left: 0 });
    update();
    el.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    return () => {
      el.removeEventListener('scroll', update);
      window.removeEventListener('resize', update);
    };
  }, [tab, update]);

  const scrollByPage = (dir) => {
    const el = trackRef.current;
    if (el) el.scrollBy({ left: dir * el.clientWidth * 0.8, behavior: 'smooth' });
  };

  return (
    <section id="featured" className="featured-section border-t border-line bg-ink py-8 md:py-10">
      <div className="container-x">
        <Reveal>
          <SectionHeading title={t('feat.title')} className="mb-5 md:mb-5" action={{ label: t('feat.viewAll'), href: '/guitars' }} />
        </Reveal>

        <Reveal delay={100} className="mb-4 flex flex-col gap-4 md:mb-5 md:flex-row md:items-end md:justify-between">
          <Tabs tabs={TABS} value={tab} onChange={setTab} />
          <div className="hidden gap-3 md:flex">
            <ArrowButton direction="prev" disabled={scroll.atStart} onClick={() => scrollByPage(-1)} />
            <ArrowButton direction="next" disabled={scroll.atEnd} onClick={() => scrollByPage(1)} />
          </div>
        </Reveal>

        <div
          ref={trackRef}
          className="-mx-5 flex snap-x snap-mandatory gap-4 overflow-x-auto px-5 pb-6 pt-3 [scrollbar-width:none] sm:-mx-8 sm:gap-5 sm:px-8 lg:mx-0 lg:gap-3 lg:px-0 [&::-webkit-scrollbar]:hidden"
        >
          {items.map((guitar) => (
            <div
              key={guitar.id}
              className="w-[82%] shrink-0 snap-start sm:w-[calc(50%-10px)] lg:w-[calc(16.666667%-10px)]"
            >
              <GuitarCard guitar={guitar} />
            </div>
          ))}
        </div>

        {/* progress bar บาง ๆ */}
        <div aria-hidden="true" className="relative h-px w-full bg-white/15">
          <div
            className="absolute top-0 h-px bg-gold transition-[left,width] duration-300"
            style={{ width: `${scroll.thumb * 100}%`, left: `${scroll.ratio * (1 - scroll.thumb) * 100}%` }}
          />
        </div>
      </div>
    </section>
  );
}
