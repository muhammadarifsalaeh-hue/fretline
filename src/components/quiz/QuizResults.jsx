import { useEffect, useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { t } from '@/i18n';
import { QUIZ_STEPS } from '@/data/quiz';
import { useShop } from '@/context/ShopContext';
import { catalogUrlFor, labelOf, rankGuitars } from '@/utils/quizScoring';
import AppLink from '@/components/ui/AppLink';
import ShareLink from '@/components/ui/ShareLink';
import MatchCard from './MatchCard';
import '@/styles/premium-quiz.css';

export default function QuizResults({ answers, onRetake, onEdit }) {
  const navigate = useNavigate();
  const { setCompareIds } = useShop();
  const headingRef = useRef(null);
  useEffect(() => { headingRef.current?.focus({ preventScroll: true }); }, []);
  const matches = useMemo(() => rankGuitars(answers), [answers]);
  const [top, ...others] = matches;
  const shareUrl = `${window.location.origin}/find-my-guitar?${new URLSearchParams(answers)}`;
  const compareTop = () => {
    const ids = matches.map((match) => match.guitar.id);
    setCompareIds(ids); navigate(`/compare?ids=${ids.join(',')}`);
  };
  return (
    <div className="quiz-results-page phase4-page premium-quiz">
      <header className="container-x phase4-heading">
        <nav aria-label={t('common.breadcrumb')} className="discovery-breadcrumb"><AppLink href="/">{t('nav.home')}</AppLink><span aria-hidden="true">›</span><AppLink href="/find-my-guitar">{t('nav.find')}</AppLink><span aria-hidden="true">›</span><span>{t('p4.quiz.results')}</span></nav>
        <p className="discovery-kicker">{t('targeted.quiz.resultKicker')}</p>
        <div className="phase4-title-row"><div><h1 ref={headingRef} tabIndex={-1}>{t('p4.quiz.results')}</h1><p>{t('p4.quiz.resultIntro')}</p></div><ShareLink url={shareUrl} /></div>
        <ul className="quiz-answer-chips" aria-label={t('p4.quiz.yourAnswers')}>{QUIZ_STEPS.map((step) => <li key={step.id}>{labelOf(step.id, answers[step.id])}</li>)}</ul>
        <div className="mb-6 flex flex-wrap gap-3"><button type="button" onClick={onEdit} className="phase4-button">{t('p4.quiz.edit')}</button><button type="button" onClick={onRetake} className="phase4-button">{t('p4.quiz.retake')}</button></div>
        <p className="phase4-data-note">{t('p4.quiz.honesty')}</p>
      </header>
      <section className="container-x pb-16" aria-label={t('p4.quiz.matches')}>
        {top ? <><MatchCard match={top} rank={1} featured />{others.length > 0 && <><h2 className="mb-5 mt-10 text-xl font-medium">{t('p4.quiz.also')}</h2><div className="grid gap-5 md:grid-cols-2">{others.map((match, index) => <MatchCard key={match.guitar.id} match={match} rank={index + 2} />)}</div></>}</>
          : <div className="quiz-results-empty"><h2 className="text-2xl font-medium">{t('p4.quiz.emptyTitle')}</h2><p className="mt-3 text-sm text-mute">{t('p4.quiz.emptyText')}</p><button type="button" onClick={onEdit} className="phase4-button is-gold mt-6">{t('p4.quiz.edit')}</button></div>}
        <div className="quiz-results-next"><div><h2 className="text-xl font-medium">{t('p4.quiz.nextTitle')}</h2><p className="mt-2 text-sm leading-7 text-mute">{t('p4.quiz.nextText')}</p></div><div className="flex flex-wrap gap-3">{matches.length >= 2 && <button type="button" onClick={compareTop} className="phase4-button is-gold">{t('p4.quiz.compareTop', { n: matches.length })}</button>}<AppLink href={catalogUrlFor(answers)} className="phase4-button">{t('p4.quiz.browse')}</AppLink></div></div>
        <details className="quiz-method"><summary>{t('p4.quiz.method')}</summary><p>{t('p4.quiz.methodText')}</p><p>{t('p4.quiz.methodUnknown')}</p></details>
      </section>
    </div>
  );
}
