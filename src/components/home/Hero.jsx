import { HOME_DISCOVERY_ASSETS } from '@/data/homeDiscoveryAssets';
import { DISCOVERY_PHOTOGRAPHY } from '@/data/discoveryPhotography';
import AppLink from '@/components/ui/AppLink';
import Button from '@/components/ui/Button';
import { ArrowRightIcon } from '@/components/ui/Icons';
import { t } from '@/i18n';
import SearchBar from '@/components/search/SearchBar';
import useHeroSlideshow from '@/hooks/useHeroSlideshow';
import HeroStats from './HeroStats';
import '@/styles/home-hero-slideshow.css';

const slides = [
  { ...HOME_DISCOVERY_ASSETS.quizBackdrop, scene: 'electric' },
  { ...HOME_DISCOVERY_ASSETS.heroBackdrop, scene: 'room' },
  { ...DISCOVERY_PHOTOGRAPHY.compareHero, scene: 'collection' },
];

export default function Hero() {
  const { sectionRef, active, dragging, handlers } = useHeroSlideshow(slides.length);
  return (
    <>
      <section ref={sectionRef} id="top" className="home-hero signature-hero relative isolate z-10 bg-ink"
        data-hero-slide-index={active} data-hero-dragging={dragging ? 'true' : undefined} {...handlers}>
        <div className="hero-visual signature-hero-visual" aria-hidden="true">
          {slides.map((photo, index) => <div key={photo.scene}
            className={`signature-hero-slide${index === active ? ' is-active' : ''}`} data-scene={photo.scene}>
            <img src={photo.src} srcSet={photo.srcSet} sizes={photo.scene === 'electric' ? '(min-width:640px) 72vw, 100vw' : '100vw'}
              alt="" width={photo.width} height={photo.height} loading={index === 0 ? 'eager' : 'lazy'}
              fetchpriority={index === 0 ? 'high' : undefined} decoding="async" draggable="false" />
          </div>)}
          <div aria-hidden="true" className="signature-hero-shade" />
        </div>

        <div className="hero-content signature-hero-content container-x relative z-10">
          <div className="signature-hero-copy">
            <p className="signature-section-eyebrow">{t('signature.hero.eyebrow')}</p>
            <h1 className="signature-hero-title">
              <span>{t('hero.title1')}</span>
              <span>{t('hero.title2')}</span>
            </h1>
            <div className="signature-hero-actions">
              <Button href="/guitars" className="signature-hero-primary">
                {t('hero.explore')} <ArrowRightIcon size={18} />
              </Button>
              <AppLink href="/find-my-guitar" className="signature-hero-quiz">
                {t('hero.quizLink')} <ArrowRightIcon size={16} />
              </AppLink>
            </div>

            <div className="signature-hero-search"><SearchBar showSuggestions={false} /></div>
          </div>
        </div>
      </section>
      <HeroStats />
    </>
  );
}
