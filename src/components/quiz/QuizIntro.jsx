import { QUIZ_STEPS } from '@/data/quiz';
import QuizHero from './QuizHero';
import { QuizGlyph, QUIZ_CATEGORY_COPY, quizCopy } from './QuizVisuals';
import '@/styles/premium-quiz.css';

/** The welcome and every live question share the reference's cinematic composition. */
export default function QuizIntro({ children }) {
  return <div className="quiz-page phase4-page premium-quiz">
    <QuizHero />
    <section id="quiz-how-it-works" className="container-x quiz-five-factors" aria-label={quizCopy('ปัจจัยที่ใช้ค้นหากีตาร์', 'Five factors that guide your discovery')}>
      {QUIZ_STEPS.map((step) => <div key={step.id}>
        <span className="quiz-factor-icon"><QuizGlyph kind={step.id} size={27} /></span>
        <h2>{QUIZ_CATEGORY_COPY[step.id].label()}</h2>
        <p>{QUIZ_CATEGORY_COPY[step.id].hint()}</p>
      </div>)}
    </section>
    {children}
  </div>;
}
