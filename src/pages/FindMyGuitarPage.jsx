import { useEffect, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { t } from '@/i18n';
import { QUIZ_STEPS } from '@/data/quiz';
import QuizFlow from '@/components/quiz/QuizFlow';
import QuizResults from '@/components/quiz/QuizResults';
import { readAnswers, readPartialAnswers } from '@/utils/quizScoring';

export default function FindMyGuitarPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const key = params.toString();
  const answers = useMemo(() => readPartialAnswers(new URLSearchParams(key)), [key]);
  const complete = useMemo(() => readAnswers(new URLSearchParams(key)), [key]);
  const step = params.get('step');
  const editing = step !== null;
  const index = /^\d+$/.test(step ?? '') && Number(step) >= 1 && Number(step) <= QUIZ_STEPS.length ? Number(step) - 1 : -1;
  const showResults = complete && !editing;
  useEffect(() => { document.title = t(showResults ? 'p4.quiz.resultDocTitle' : 'p4.quiz.docTitle'); }, [showResults]);

  const onNavigate = (nextAnswers, nextIndex, { replace = false } = {}) => {
    const next = new URLSearchParams(nextAnswers);
    next.set('step', nextIndex < 0 ? 'welcome' : String(nextIndex + 1));
    navigate(`/find-my-guitar?${next}`, { replace });
  };
  return showResults
    ? <QuizResults answers={complete} onEdit={() => onNavigate(complete, 0)} onRetake={() => navigate('/find-my-guitar')} />
    : <QuizFlow answers={answers} index={index} onNavigate={onNavigate} onFinish={(next) => navigate(`/find-my-guitar?${new URLSearchParams(next)}`)} />;
}
