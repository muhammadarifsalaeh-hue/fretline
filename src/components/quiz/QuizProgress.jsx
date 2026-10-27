import { t } from '@/i18n';
import { QUIZ_STEPS } from '@/data/quiz';
import { CheckIcon } from '@/components/ui/Icons';
import { QUIZ_CATEGORY_COPY } from './QuizVisuals';

export default function QuizProgress({ index, total }) {
  return <div className="quiz-progress">
    <p className="sr-only" role="status">{t('p4.quiz.step', { n: index + 1, total })}</p>
    <div role="progressbar" aria-label={t('p4.quiz.progress')} aria-valuemin={1} aria-valuemax={total} aria-valuenow={index + 1} aria-valuetext={t('p4.quiz.step', { n: index + 1, total })}>
      <ol className="quiz-numbered-steps" aria-hidden="true">
        {QUIZ_STEPS.map((step, value) => <li key={step.id} className={value === index ? 'is-current' : value < index ? 'is-complete' : ''}>
          <span className="quiz-step-disc">{value < index ? <CheckIcon size={15} /> : value + 1}</span>
          <span className="quiz-step-label">{QUIZ_CATEGORY_COPY[step.id].label()}</span>
        </li>)}
      </ol>
    </div>
  </div>;
}
