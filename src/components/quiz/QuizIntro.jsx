import { GUITARS } from '@/data/guitars';
import { IMAGES } from '@/data/images';
import { QUIZ_STEPS } from '@/data/quiz';
import Button from '@/components/ui/Button';
import { ArrowRightIcon } from '@/components/ui/Icons';
import ArtBackdrop from '@/components/ui/ArtBackdrop';
import SmartImage from '@/components/ui/SmartImage';

const delay = (ms) => ({ animationDelay: `${ms}ms` });

/** หน้าเริ่มต้นของ Quiz */
export default function QuizIntro({ onStart }) {
  const facts = [
    { value: String(QUIZ_STEPS.length), label: 'Questions' },
    { value: '~1 min', label: 'To finish' },
    { value: String(GUITARS.length), label: 'Guitars matched' },
  ];

  return (
    <section className="relative isolate flex min-h-[100svh] items-center overflow-hidden">
      {IMAGES.findMyGuitar ? (
        <SmartImage src={IMAGES.findMyGuitar} alt="" priority className="absolute inset-0 -z-20" imgClassName="opacity-50" />
      ) : (
        <ArtBackdrop type="electric" anchor="right" className="absolute inset-0 -z-20" />
      )}
      <div aria-hidden="true" className="absolute inset-0 -z-10 bg-gradient-to-r from-ink via-ink/85 to-ink/30" />
      <div aria-hidden="true" className="absolute inset-x-0 bottom-0 -z-10 h-1/3 bg-gradient-to-t from-ink to-transparent" />

      <div className="container-x pb-20 pt-32">
        <div className="max-w-xl">
          <p style={delay(100)} className="animate-fade-up text-xs uppercase tracking-[0.28em] text-gold">
            Find my guitar
          </p>
          <h1 style={delay(200)} className="mt-5 animate-fade-up font-serif text-[clamp(2.75rem,7vw,5.5rem)] leading-[0.96] tracking-[-0.02em]">
            Not sure where to start?
            <span className="block italic text-bone/90">We will narrow it down.</span>
          </h1>
          <p style={delay(320)} className="mt-6 max-w-md animate-fade-up text-base leading-relaxed text-bone/75 md:text-lg">
            Answer a few quick questions about how you play and what you want to spend. We will rank the guitars in our catalog that fit you best, and tell you why.
          </p>

          <div style={delay(440)} className="mt-9 animate-fade-up">
            <Button onClick={onStart} size="lg" className="w-full sm:w-auto">
              Start the quiz <ArrowRightIcon size={18} />
            </Button>
          </div>

          <dl style={delay(560)} className="mt-12 flex animate-fade-up gap-8 border-t border-line pt-6 sm:gap-12">
            {facts.map((f) => (
              <div key={f.label}>
                <dt className="sr-only">{f.label}</dt>
                <dd className="font-mono text-2xl">{f.value}</dd>
                <p className="mt-1 text-xs text-mute">{f.label}</p>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  );
}
