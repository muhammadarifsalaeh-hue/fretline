import { t } from '@/i18n';
import { GUITARS } from '@/data/guitars';
import { QUIZ_STEPS } from '@/data/quiz';
import { ArrowRightIcon } from '@/components/ui/Icons';
import AppLink from '@/components/ui/AppLink';
import GuitarArt from '@/components/ui/GuitarArt';

export default function QuizIntro({ onStart }) {
  return (
    <div className="quiz-page phase4-page"><section className="container-x quiz-shell phase4-heading">
      <nav aria-label={t('common.breadcrumb')} className="discovery-breadcrumb"><AppLink href="/">{t('nav.home')}</AppLink><span aria-hidden="true">›</span><span>{t('nav.find')}</span></nav>
      <p className="discovery-kicker">FRETLINE / FIND YOUR SOUND</p>
      <h1 className="quiz-page-title mt-3">Find My Guitar Quiz</h1>
      <div className="quiz-welcome">
        <div><p className="text-sm text-gold">{t('p4.quiz.welcomeEyebrow')}</p><h2 className="mt-4 text-3xl font-medium leading-relaxed md:text-4xl">{t('p4.quiz.welcomeTitle')}</h2>
          <p className="mt-5 text-sm leading-8 text-mute">{t('p4.quiz.intro')}</p>
          <button type="button" onClick={onStart} className="phase4-button is-gold mt-7">{t('p4.quiz.start')}<ArrowRightIcon size={17} /></button>
        </div>
        <div className="quiz-welcome-art" aria-hidden="true"><GuitarArt type="acoustic" className="h-full -rotate-12 text-gold/65" /></div>
      </div>
      <dl className="quiz-welcome-facts"><div><dt>{t('p4.quiz.questions')}</dt><dd>{QUIZ_STEPS.length}</dd></div><div><dt>{t('p4.quiz.models')}</dt><dd>{GUITARS.length}</dd></div><div><dt>{t('p4.quiz.criteria')}</dt><dd>{QUIZ_STEPS.length}</dd></div></dl>
      <p className="phase4-data-note mt-6">{t('p4.quiz.honesty')}</p>
    </section></div>
  );
}
