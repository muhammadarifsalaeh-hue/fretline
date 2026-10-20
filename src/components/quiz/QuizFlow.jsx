import { useEffect, useRef } from 'react';
import { t } from '@/i18n';
import { QUIZ_STEPS } from '@/data/quiz';
import { ArrowRightIcon, ChevronLeftIcon } from '@/components/ui/Icons';
import AppLink from '@/components/ui/AppLink';
import QuizIntro from './QuizIntro';
import QuizOption from './QuizOption';
import QuizProgress from './QuizProgress';

/** Answers and current step live in the URL, including browser Back/Forward snapshots. */
export default function QuizFlow({ answers, index, onNavigate, onFinish }) {
  const headingRef = useRef(null);
  const step = QUIZ_STEPS[index];
  useEffect(() => {
    if (index < 0) return;
    window.scrollTo({ top: 0 }); headingRef.current?.focus({ preventScroll: true });
  }, [index]);
  if (index < 0) return <QuizIntro onStart={() => onNavigate(answers, 0)} />;
  const selected = answers[step.id];
  const next = () => { if (selected) index === QUIZ_STEPS.length - 1 ? onFinish(answers) : onNavigate(answers, index + 1); };

  return (
    <div className="quiz-page phase4-page">
      <section className="container-x quiz-shell phase4-heading">
        <nav aria-label={t('common.breadcrumb')} className="discovery-breadcrumb"><AppLink href="/">{t('nav.home')}</AppLink><span aria-hidden="true">›</span><span>{t('nav.find')}</span></nav>
        <h1 className="quiz-page-title">Find My Guitar Quiz</h1>
        <p className="mt-2 text-sm text-mute">{t('p4.quiz.intro')}</p>
        <QuizProgress index={index} total={QUIZ_STEPS.length} />
        <form onSubmit={(event) => { event.preventDefault(); next(); }}>
          <div key={step.id} className="quiz-question animate-fade-in">
            <h2 id={`quiz-${step.id}-title`} ref={headingRef} tabIndex={-1} className="text-xl font-medium focus:outline-none md:text-2xl">{step.title}</h2>
            <p id={`quiz-${step.id}-hint`} className="mt-2 text-sm leading-7 text-mute">{step.hint}</p>
            <div role="radiogroup" aria-labelledby={`quiz-${step.id}-title`} aria-describedby={`quiz-${step.id}-hint`} className={`quiz-options ${step.id === 'type' ? 'quiz-type-options' : ''}`}>
              {step.options.map((option) => <QuizOption key={option.value} name={step.id} option={option} checked={selected === option.value}
                onSelect={(value) => onNavigate({ ...answers, [step.id]: value }, index, { replace: true })} />)}
            </div>
          </div>
          <div className="quiz-step-actions">
            <button type="button" onClick={() => onNavigate(answers, index - 1, { replace: true })} className="phase4-button"><ChevronLeftIcon size={16} />{t('p4.previous')}</button>
            <button type="submit" disabled={!selected} className="phase4-button is-gold">{t(index === QUIZ_STEPS.length - 1 ? 'p4.quiz.seeResults' : 'p4.next')}<ArrowRightIcon size={16} /></button>
          </div>
        </form>
      </section>
    </div>
  );
}
