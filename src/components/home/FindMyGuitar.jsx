import { useEffect, useId, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LANG, t } from '@/i18n';
import { GUITARS } from '@/data/guitars';
import { QUIZ_STEPS } from '@/data/quiz';
import { HOME_DISCOVERY_ASSETS } from '@/data/homeDiscoveryAssets';
import AppLink from '@/components/ui/AppLink';
import { ArrowRightIcon, CheckIcon, ChevronLeftIcon } from '@/components/ui/Icons';
import '@/styles/home-quiz-premium.css';

const copy = (th, en) => LANG === 'en' ? en : th;
const catalogStats = [
  [GUITARS.length, () => copy('รุ่นกีตาร์', 'guitar models')],
  [new Set(GUITARS.map((guitar) => guitar.brand)).size, () => copy('แบรนด์', 'brands')],
  [new Set(GUITARS.map((guitar) => guitar.category)).size, () => copy('ประเภทกีตาร์', 'guitar families')],
];

/** The original five-question data feeds the original results/scoring route. */
export default function FindMyGuitar() {
  const navigate = useNavigate();
  const [answers, setAnswers] = useState({});
  const [index, setIndex] = useState(0);
  const panelRef = useRef(null);
  const headingRef = useRef(null);
  const focusAfterStep = useRef(false);
  const inputPrefix = useId();
  const step = QUIZ_STEPS[index];
  const photo = HOME_DISCOVERY_ASSETS.quizBackdrop;
  const selected = answers[step.id];

  const revealPanel = () => {
    panelRef.current?.scrollIntoView({ block: 'start', behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    headingRef.current?.focus({ preventScroll: true });
  };
  useEffect(() => {
    // Loading Home must never pull the visitor down from the main Hero.
    if (!focusAfterStep.current) return;
    focusAfterStep.current = false;
    panelRef.current?.scrollIntoView({ block: 'start' });
    headingRef.current?.focus({ preventScroll: true });
  }, [index]);
  const changeStep = (nextIndex) => { focusAfterStep.current = true; setIndex(nextIndex); };
  const next = () => {
    if (!selected) return;
    // Never copy or approximate the recommendation engine in the Homepage.
    if (index === QUIZ_STEPS.length - 1) navigate(`/find-my-guitar?${new URLSearchParams(answers)}`);
    else changeStep(index + 1);
  };

  return <section id="find" className="home-find-section premium-home-find" aria-labelledby="home-find-title">
    <div className="home-find-photograph" aria-hidden="true">
      <img src={photo.src} srcSet={photo.srcSet} sizes="(min-width: 1024px) 65vw, 100vw" width={photo.width} height={photo.height} alt="" loading="lazy" decoding="async" />
    </div>
    <div className="container-x home-find-layout">
      <div className="home-experience-copy home-find-editorial">
        <p className="home-experience-eyebrow"><span aria-hidden="true" />03 / FIND MY GUITAR</p>
        <h2 id="home-find-title">{copy('กีตาร์ที่ใช่', 'The right guitar.')}<br /><em>{copy('เริ่มจากตัวคุณ', 'Starts with you.')}</em></h2>
        <p className="home-experience-description">{copy('5 คำถามเกี่ยวกับวิธีเล่นและสิ่งที่คุณชอบ เพื่อค้นหากีตาร์ที่เข้ากับสไตล์ของคุณ', 'Five questions about your playing and what matters to you. Find a guitar that fits your own way to play.')}</p>
        <button type="button" onClick={revealPanel} className="home-find-start" data-home-quiz-start>{t('signature.find.cta')}<ArrowRightIcon size={20} /></button>
        <dl className="home-find-statistics">{catalogStats.map(([value, label], itemIndex) => <div key={itemIndex}><dt>{label()}</dt><dd>{value}</dd></div>)}</dl>
        <AppLink href="/image-credits#home-photography" className="home-find-photography-credit">{copy('เครดิตภาพประกอบ', 'Editorial photo credits')}</AppLink>
      </div>
      <div ref={panelRef} className="home-find-panel" data-home-quiz-panel>
        <div className="home-find-caption"><span>FIND MY GUITAR</span><span aria-hidden="true">{String(index + 1).padStart(2, '0')} / {String(QUIZ_STEPS.length).padStart(2, '0')}</span></div>
        <div role="progressbar" aria-label={t('p4.quiz.progress')} aria-valuemin={1} aria-valuemax={QUIZ_STEPS.length} aria-valuenow={index + 1} aria-valuetext={t('p4.quiz.step', { n: index + 1, total: QUIZ_STEPS.length })} className="home-find-track">
          {QUIZ_STEPS.map((entry, entryIndex) => <span key={entry.id} className={entryIndex <= index ? 'is-reached' : ''} aria-hidden="true" />)}
        </div>
        <p className="sr-only" role="status">{t('p4.quiz.step', { n: index + 1, total: QUIZ_STEPS.length })}</p>
        <form className="home-find-form" onSubmit={(event) => { event.preventDefault(); next(); }}>
          <div className="home-find-live-question" key={step.id}>
            <h3 id={`${inputPrefix}-${step.id}-title`} ref={headingRef} tabIndex={-1}>{step.title}</h3>
            <p id={`${inputPrefix}-${step.id}-hint`} className="home-find-question-hint">{step.hint}</p>
            <div className="home-find-choices" role="radiogroup" aria-labelledby={`${inputPrefix}-${step.id}-title`} aria-describedby={`${inputPrefix}-${step.id}-hint`}>
              {step.options.map((option) => {
                const instrument = step.id === 'type' ? HOME_DISCOVERY_ASSETS[option.value] : null;
                const chosen = selected === option.value;
                const optionId = `${inputPrefix}-${step.id}-${option.value}`;
                return <label key={option.value} className={`home-find-choice ${instrument ? 'has-photograph' : ''} ${chosen ? 'is-selected' : ''} ${option.value === 'any' ? 'is-any' : ''}`} data-home-quiz-option={option.value}>
                  <input type="radio" name={`home-quiz-${step.id}`} value={option.value} checked={chosen} aria-labelledby={`${optionId}-label`} aria-describedby={`${optionId}-description`} onChange={() => setAnswers((current) => ({ ...current, [step.id]: option.value }))} className="sr-only" />
                  <span className="home-find-option-focus" aria-hidden="true" />
                  {instrument && <span className="home-find-instrument" aria-hidden="true"><img src={instrument.src} srcSet={instrument.srcSet} sizes="88px" width={instrument.width} height={instrument.height} alt="" loading="lazy" decoding="async" /></span>}
                  <span className="home-find-option-copy"><span id={`${optionId}-label`} className="home-find-option-title">{option.label}</span><span id={`${optionId}-description`} className="home-find-option-description">{option.desc}</span></span>
                  <span className="home-find-option-indicator" aria-hidden="true">{chosen ? <CheckIcon size={17} /> : <ArrowRightIcon size={17} />}</span>
                </label>;
              })}
            </div>
          </div>
          <div className="home-find-actions">
            <button type="button" className="home-find-previous" onClick={() => changeStep(index - 1)} disabled={index === 0}><ChevronLeftIcon size={17} />{t('p4.previous')}</button>
            <button type="submit" className="home-find-next" disabled={!selected}>{t(index === QUIZ_STEPS.length - 1 ? 'p4.quiz.seeResults' : 'p4.next')}<ArrowRightIcon size={18} /></button>
          </div>
        </form>
        <p className="home-find-data-note">{copy('คำแนะนำเบื้องต้นจากคำตอบของคุณ ข้อมูลที่ยังไม่ยืนยันจะแจ้งในผลลัพธ์', 'A starting point based on your answers. Unconfirmed catalog information remains identified in the results.')}</p>
      </div>
    </div>
  </section>;
}
