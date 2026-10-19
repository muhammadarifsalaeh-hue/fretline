import { t } from '@/i18n';
import { QUIZ_STEPS } from '@/data/quiz';

export default function QuizProgress({ index, total }) {
  return (
    <div className="quiz-progress">
      <p className="mb-3 text-xs text-gold" role="status">{t('p4.quiz.step', { n: index + 1, total })}</p>
      <div role="progressbar" aria-label={t('p4.quiz.progress')} aria-valuemin={1} aria-valuemax={total} aria-valuenow={index + 1} aria-valuetext={t('p4.quiz.step', { n: index + 1, total })} className="flex gap-2">
        {QUIZ_STEPS.map((step, value) => <span key={step.id} className="h-0.5 flex-1 bg-line"><span className="block h-full bg-gold transition-[width] duration-300" style={{ width: value <= index ? '100%' : '0%' }} /></span>)}
      </div>
    </div>
  );
}
