import { useEffect, useRef, useState } from 'react';
import { QUIZ_STEPS } from '@/data/quiz';
import { cn } from '@/utils/cn';
import { ArrowRightIcon } from '@/components/ui/Icons';
import QuizIntro from './QuizIntro';
import QuizOption from './QuizOption';
import QuizProgress from './QuizProgress';

/** ตัวควบคุมคำถามทีละข้อ: intro → step 1..N → onFinish(answers) */
export default function QuizFlow({ onFinish }) {
  const [index, setIndex] = useState(-1); // -1 = หน้าเริ่มต้น
  const [answers, setAnswers] = useState({});
  const headingRef = useRef(null);
  const timer = useRef(0);

  const total = QUIZ_STEPS.length;
  const step = QUIZ_STEPS[index];

  // เปลี่ยนข้อ: เลื่อนขึ้นบนและย้าย focus ไปที่หัวข้อคำถาม (สำหรับ screen reader / คีย์บอร์ด)
  useEffect(() => {
    if (index < 0) return;
    window.scrollTo({ top: 0 });
    headingRef.current?.focus({ preventScroll: true });
  }, [index]);

  useEffect(() => () => window.clearTimeout(timer.current), []);

  const next = (nextAnswers = answers) => {
    if (index >= total - 1) onFinish(nextAnswers);
    else setIndex(index + 1);
  };
  const back = () => setIndex(index - 1);

  const select = (value, advance) => {
    const updated = { ...answers, [step.id]: value };
    setAnswers(updated);
    if (advance) {
      window.clearTimeout(timer.current);
      timer.current = window.setTimeout(() => next(updated), 380);
    }
  };

  if (index < 0) return <QuizIntro onStart={() => setIndex(0)} />;

  const selected = answers[step.id];
  const odd = step.options.length % 2 === 1;

  return (
    <section className="relative isolate pb-24 pt-28 md:pt-36">
      <div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(50%_60%_at_85%_0%,#262626_0%,#0A0A0A_70%)]" />
      <div className="container-x max-w-4xl">
        <QuizProgress index={index} total={total} onBack={index === 0 ? () => setIndex(-1) : back} />

        {/* key = ข้อปัจจุบัน → เล่น animation ใหม่ทุกครั้งที่เปลี่ยนข้อ */}
        <div key={step.id} className="animate-fade-up">
          <h1
            ref={headingRef}
            tabIndex={-1}
            className="font-serif text-4xl leading-[1.02] tracking-tight focus:outline-none md:text-6xl"
          >
            {step.title}
          </h1>
          <p className="mt-4 max-w-lg text-base text-mute md:text-lg">{step.hint}</p>

          <div role="radiogroup" aria-label={step.title} className="mt-10 grid gap-3 sm:grid-cols-2 sm:gap-4">
            {step.options.map((option, i) => (
              <QuizOption
                key={option.value}
                name={step.id}
                option={option}
                checked={selected === option.value}
                onSelect={select}
                className={cn(odd && i === step.options.length - 1 && 'sm:col-span-2')}
              />
            ))}
          </div>

          <div className="mt-10 flex justify-end">
            <button
              type="button"
              onClick={() => next()}
              disabled={!selected}
              className="inline-flex h-14 w-full items-center justify-center gap-2 rounded-full bg-gold px-9 text-[15px] font-medium text-ink transition duration-300 ease-premium hover:bg-gold-soft active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-35 disabled:hover:bg-gold sm:w-auto"
            >
              {index >= total - 1 ? 'See my matches' : 'Next'} <ArrowRightIcon size={18} />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
