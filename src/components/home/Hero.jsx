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
    <section id="top" className="home-hero relative isolate z-10 flex flex-col bg-ink">
      {/* แสง spotlight หลังกีตาร์ */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(60%_60%_at_72%_42%,#2c2c2c_0%,#0A0A0A_72%)]"
      />

      {/* รูปกีตาร์: Mobile อยู่บน, Desktop ชิดขวาและล้นขอบ */}
      <div className="hero-visual relative mt-16 h-[320px] w-full overflow-hidden lg:absolute lg:inset-y-0 lg:right-0 lg:mt-0 lg:h-auto lg:w-full">
        <div ref={parallaxRef} className="absolute -inset-[4%] will-change-transform">
          <div className="relative h-full w-full animate-hero-guitar">
            {HERO.image ? (
              <>
                <SmartImage
                  src={HERO.image}
                  srcSet="/images/hero/acoustic-studio-mobile.webp 900w, /images/hero/acoustic-studio.webp 1536w"
                  sizes="100vw"
                  alt={HERO.imageAlt}
                  priority
                  className="absolute inset-0"
                  imgClassName="opacity-95"
                />
                {HERO.showHotspots && HERO.hotspots.map((spot) => <HeroHotspot key={spot.id} {...spot} />)}
              </>
            ) : (
              <HeroArt />
            )}
          </div>
        </div>
        {/* ไล่สีให้รูปกลืนไปกับพื้นดำ */}
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 bg-gradient-to-t from-ink via-ink/20 to-transparent lg:bg-gradient-to-r lg:from-ink lg:via-ink/10 lg:to-transparent" />
        <div aria-hidden="true" className="pointer-events-none absolute inset-x-0 bottom-0 hidden h-1/4 bg-gradient-to-t from-ink to-transparent lg:block" />
      </div>

      {/* เนื้อหาฝั่งซ้าย */}
      <div className="hero-content container-x relative z-10 flex flex-1 items-center pb-10 pt-2 lg:pb-12 lg:pt-32">
        <div className="w-full max-w-[550px]">
          <p style={delay(100)} className="animate-fade-up text-base text-gold sm:text-lg">
            {t('hero.eyebrow')}
          </p>

          <h1
            style={delay(200)}
            className="mt-4 animate-fade-up font-sans text-[clamp(2.75rem,5.2vw,4.5rem)] font-medium leading-[1.05]"
          >
            <span className="block">{t('hero.title1')}</span>
            <span className="block text-gold">{t('hero.title2')}</span>
          </h1>

          <p style={delay(320)} className="mt-5 max-w-[430px] animate-fade-up text-[15px] leading-relaxed text-bone/70 md:text-base">
            {t('hero.sub')}
          </p>

          <div style={delay(440)} className="mt-6 animate-fade-up">
            <SearchBar />
          </div>

          <div style={delay(560)} className="mt-6 flex animate-fade-up flex-col gap-3 sm:flex-row sm:items-center sm:gap-6">
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

      <p className="hero-art-note pointer-events-none absolute bottom-3 right-5 z-10 text-[10px] text-bone/60">{t('hero.artNote')}</p>

    </section>
  );
}
