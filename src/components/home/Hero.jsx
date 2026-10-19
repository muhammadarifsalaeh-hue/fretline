import { useRef } from 'react';
import { HERO } from '@/data/hero';
import useParallax from '@/hooks/useParallax';
import AppLink from '@/components/ui/AppLink';
import Button from '@/components/ui/Button';
import { ArrowRightIcon } from '@/components/ui/Icons';
import { t } from '@/i18n';
import SmartImage from '@/components/ui/SmartImage';
import SearchBar from '@/components/search/SearchBar';
import HeroArt from './HeroArt';
import HeroHotspot from './HeroHotspot';
import HeroStats from './HeroStats';

// หน่วงเวลาให้เนื้อหา Hero ขึ้นมาทีละชั้น (เป็น "ช่วงเวลาเด่น" เดียวของหน้า)
const delay = (ms) => ({ animationDelay: `${ms}ms` });

export default function Hero() {
  const parallaxRef = useRef(null);
  useParallax(parallaxRef, { mouse: 12, scroll: 0.06 });

  return (
    <section id="top" className="relative isolate z-10 flex min-h-[100svh] flex-col bg-ink">
      {/* แสง spotlight หลังกีตาร์ */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(60%_60%_at_72%_42%,#2c2c2c_0%,#0A0A0A_72%)]"
      />

      {/* รูปกีตาร์: Mobile อยู่บน, Desktop ชิดขวาและล้นขอบ */}
      <div className="relative mt-16 h-[46svh] w-full overflow-hidden lg:absolute lg:inset-y-0 lg:right-0 lg:mt-0 lg:h-auto lg:w-[64%]">
        <div ref={parallaxRef} className="absolute -inset-[4%] will-change-transform">
          <div className="relative h-full w-full animate-hero-guitar">
            {HERO.image ? (
              <>
                <SmartImage
                  src={HERO.image}
                  alt={HERO.imageAlt}
                  priority
                  className="absolute inset-0"
                  imgClassName="opacity-90"
                />
                {HERO.showHotspots && HERO.hotspots.map((spot) => <HeroHotspot key={spot.id} {...spot} />)}
              </>
            ) : (
              <HeroArt />
            )}
          </div>
        </div>
        {/* ไล่สีให้รูปกลืนไปกับพื้นดำ */}
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 bg-gradient-to-t from-ink via-ink/20 to-transparent lg:bg-gradient-to-r lg:from-ink lg:via-ink/30 lg:to-transparent" />
        <div aria-hidden="true" className="pointer-events-none absolute inset-x-0 bottom-0 hidden h-1/4 bg-gradient-to-t from-ink to-transparent lg:block" />
      </div>

      {/* เนื้อหาฝั่งซ้าย */}
      <div className="container-x relative z-10 flex flex-1 items-center pb-24 pt-6 lg:pb-16 lg:pt-28">
        <div className="w-full max-w-[620px]">
          <p style={delay(100)} className="animate-fade-up text-base text-gold sm:text-lg">
            {t('hero.eyebrow')}
          </p>

          <h1
            style={delay(200)}
            className="mt-4 animate-fade-up font-sans text-[clamp(2.75rem,7vw,5.5rem)] font-medium leading-[1.05]"
          >
            <span className="block">{t('hero.title1')}</span>
            <span className="block text-gold">{t('hero.title2')}</span>
          </h1>

          <p style={delay(320)} className="mt-6 max-w-lg animate-fade-up text-[15px] leading-relaxed text-bone/70 md:text-base">
            {t('hero.sub')}
          </p>

          <div style={delay(440)} className="mt-8 animate-fade-up">
            <SearchBar />
          </div>

          <div style={delay(560)} className="mt-9 flex animate-fade-up flex-col gap-3 sm:flex-row sm:items-center sm:gap-6">
            <Button href="/guitars" size="lg" className="w-full sm:w-auto">
              {t('hero.explore')} <ArrowRightIcon size={18} />
            </Button>
            <AppLink
              href="/find-my-guitar"
              className="group inline-flex min-h-[44px] items-center justify-center gap-2 text-sm text-gold transition-colors hover:text-gold-soft"
            >
              {t('hero.quizLink')}
              <ArrowRightIcon size={16} className="transition-transform duration-300 ease-premium group-hover:translate-x-1" />
            </AppLink>
          </div>

          {/* สถิติจริงจากข้อมูล: Mobile อยู่ใต้ปุ่ม, Desktop เป็นแผงลอยทางขวา */}
          <HeroStats style={delay(680)} />
        </div>
      </div>

      {/* Scroll cue */}
      <a
        href="#categories"
        aria-label={t('hero.scroll')}
        className="absolute bottom-6 left-1/2 z-10 hidden -translate-x-1/2 flex-col items-center gap-2 text-xs text-mute lg:flex"
      >
        {t('hero.scroll')}
        <span className="relative block h-10 w-px overflow-hidden bg-line">
          <span className="absolute inset-0 animate-scroll-line bg-gold" />
        </span>
      </a>
    </section>
  );
}
