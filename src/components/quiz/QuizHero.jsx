import { LANG, t } from '@/i18n';
import { DISCOVERY_PHOTOGRAPHY } from '@/data/discoveryPhotography';
import AppLink from '@/components/ui/AppLink';
import { quizCopy } from './QuizVisuals';

export default function QuizHero() {
  const photo = DISCOVERY_PHOTOGRAPHY.quizHero;
  return <header className="quiz-cinematic-hero">
    <div className="quiz-hero-photograph" aria-hidden="true">
      <img src={photo.src} srcSet={photo.srcSet} sizes="(min-width: 1300px) 1100px, 100vw" width={photo.width} height={photo.height} alt="" fetchpriority="high" decoding="async" />
    </div>
    <div className="container-x quiz-hero-inner">
      <nav aria-label={t('common.breadcrumb')} className="discovery-breadcrumb"><AppLink href="/">{t('nav.home')}</AppLink><span aria-hidden="true">›</span><span>{t('nav.find')}</span></nav>
      <div className="quiz-hero-copy">
        <p className="discovery-kicker">{LANG === 'en' ? 'FRETLINE / FIND MY GUITAR' : 'FRETLINE / ค้นหากีตาร์ที่ใช่'}</p>
        <h1 className="quiz-page-title"><span>{LANG === 'en' ? 'Find My' : 'ค้นหากีตาร์'}</span>{' '}<em>{LANG === 'en' ? 'Guitar Quiz' : 'ที่ใช่สำหรับคุณ'}</em></h1>
        <h2>{quizCopy('ค้นหากีตาร์ที่ใช่ สำหรับสไตล์ของคุณ', 'Find the guitar that feels like you.')}</h2>
        <p className="quiz-hero-description">{t('p4.quiz.intro')}</p>
      </div>
    </div>
  </header>;
}
