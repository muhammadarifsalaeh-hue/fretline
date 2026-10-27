import { BRANDS } from '@/data/brands';
import { GUITARS } from '@/data/guitars';
import { HOME_DISCOVERY_ASSETS } from '@/data/homeDiscoveryAssets';
import AppLink from '@/components/ui/AppLink';
import Button from '@/components/ui/Button';
import { ArrowRightIcon } from '@/components/ui/Icons';
import { LANG, t } from '@/i18n';
import SmartImage from '@/components/ui/SmartImage';
import SearchBar from '@/components/search/SearchBar';
import HeroStats from './HeroStats';

export default function Hero() {
  const photo = HOME_DISCOVERY_ASSETS.heroBackdrop;
  return (
    <>
      <section id="top" className="home-hero signature-hero relative isolate z-10 bg-ink">
        <div className="hero-visual signature-hero-visual">
          <SmartImage
            src={photo.src}
            srcSet={photo.srcSet}
            sizes="100vw"
            alt={photo.alt}
            width={photo.width}
            height={photo.height}
            priority
            className="absolute inset-0"
          />
          <div aria-hidden="true" className="signature-hero-shade" />
        </div>

        <div className="hero-content signature-hero-content container-x relative z-10">
          <div className="signature-hero-copy">
            <p className="signature-section-eyebrow">{t('signature.hero.eyebrow')}</p>
            <h1 className="signature-hero-title">
              <span>{t('hero.title1')}</span>
              <span>{t('hero.title2')}</span>
            </h1>
            <p className="signature-hero-description">
              {t('signature.hero.description', { models: GUITARS.length, brands: BRANDS.length })}
            </p>

            <div className="signature-hero-actions">
              <Button href="/guitars" className="signature-hero-primary">
                {t('hero.explore')} <ArrowRightIcon size={18} />
              </Button>
              <AppLink href="/find-my-guitar" className="signature-hero-quiz">
                {t('hero.quizLink')} <ArrowRightIcon size={16} />
              </AppLink>
            </div>

            <div className="signature-hero-search"><SearchBar /></div>
          </div>
        </div>
        <AppLink href="/image-credits#home-photography" className="hero-art-note signature-hero-caption">{LANG === 'en' ? 'Editorial photography · Credits' : 'ภาพประกอบบรรยากาศ · เครดิตภาพ'}</AppLink>
      </section>
      <HeroStats />
    </>
  );
}
