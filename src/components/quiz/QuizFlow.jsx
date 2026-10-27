import { useEffect, useRef } from 'react';
import { t } from '@/i18n';
import { QUIZ_STEPS } from '@/data/quiz';
import { ArrowRightIcon, ChevronLeftIcon } from '@/components/ui/Icons';
import QuizIntro from './QuizIntro';
import QuizOption from './QuizOption';
import QuizProgress from './QuizProgress';
import { QuizPhotoTriptych, quizCopy } from './QuizVisuals';

/** Answers/current step stay in the original URL contract, including browser history. */
export default function QuizFlow({ answers, index, onNavigate, onFinish }) {
  const headingRef = useRef(null);
  const panelRef = useRef(null);
  const activeIndex = Math.max(0, index);
  const step = QUIZ_STEPS[activeIndex];
  useEffect(() => {
    if (index < 0) { window.scrollTo({ top: 0 }); return; }
    panelRef.current?.scrollIntoView({ block: 'start' });
    headingRef.current?.focus({ preventScroll: true });
  }, [index]);
  const selected = answers[step.id];
  const next = () => {
    if (!selected) return;
    activeIndex === QUIZ_STEPS.length - 1 ? onFinish(answers) : onNavigate(answers, activeIndex + 1);
  };
  return <QuizIntro>
    <section className="container-x quiz-shell" aria-label={quizCopy('แบบทดสอบค้นหากีตาร์', 'Find your guitar questionnaire')}>
      <div className="quiz-studio-panel" id="quiz-questionnaire" ref={panelRef}>
        <QuizProgress index={activeIndex} total={QUIZ_STEPS.length} />
        <div className="quiz-studio-layout">
          <QuizPhotoTriptych />
          <form onSubmit={(event) => { event.preventDefault(); next(); }} className="quiz-question-form">
            <div key={step.id} className="quiz-question animate-fade-in">
              <p className="quiz-question-count">{t('p4.quiz.step', { n: activeIndex + 1, total: QUIZ_STEPS.length })}</p>
              <h2 id={`quiz-${step.id}-title`} ref={headingRef} tabIndex={-1}>{step.title}</h2>
              <p id={`quiz-${step.id}-hint`} className="quiz-question-hint">{step.hint}</p>
              <div role="radiogroup" aria-labelledby={`quiz-${step.id}-title`} aria-describedby={`quiz-${step.id}-hint`} className={`quiz-options ${step.id === 'type' ? 'quiz-type-options' : ''}`}>
                {step.options.map((option, optionIndex) => <QuizOption key={option.value} name={step.id} option={option} checked={selected === option.value}
                  supplemental={optionIndex === 4} onSelect={(value) => onNavigate({ ...answers, [step.id]: value }, activeIndex, { replace: true })} />)}
              </div>
            </div>
            <div className="quiz-step-actions">
              <button type="button" onClick={() => onNavigate(answers, activeIndex - 1, { replace: true })} className="phase4-button quiz-previous" disabled={index < 0}><ChevronLeftIcon size={16} />{t('p4.previous')}</button>
              <button type="submit" disabled={!selected} className="phase4-button is-gold quiz-next">{t(activeIndex === QUIZ_STEPS.length - 1 ? 'p4.quiz.seeResults' : 'p4.next')}<ArrowRightIcon size={18} /></button>
            </div>
          </form>
        </div>
      </div>
    </section>
  </QuizIntro>;
}
