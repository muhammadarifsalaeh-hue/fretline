import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { QUIZ_STEPS } from '@/data/quiz';
import { useShop } from '@/context/ShopContext';
import { catalogUrlFor, labelOf, rankGuitars } from '@/utils/quizScoring';
import { formatPrice } from '@/utils/format';
import { guitarUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import Button from '@/components/ui/Button';
import { CheckIcon } from '@/components/ui/Icons';
import GuitarImage from '@/components/guitar/GuitarImage';
import MatchButtons from './MatchButtons';
import MatchCard from './MatchCard';

/** ผลลัพธ์ Quiz: อันดับ 1 แบบใหญ่ + อันดับ 2–3 + ทางไปต่อ (เปรียบเทียบ / Catalog / ทำใหม่) */
export default function QuizResults({ answers, onRetake }) {
  const navigate = useNavigate();
  const { setCompareIds } = useShop();
  const matches = useMemo(() => rankGuitars(answers, 3), [answers]);
  const [top, ...others] = matches;
  const g = top.guitar;
  const canCompare = matches.length >= 2;

  const compareTop = () => {
    setCompareIds(matches.map((m) => m.guitar.id));
    navigate('/compare');
  };

  return (
    <>
      <header className="relative isolate border-b border-line pb-12 pt-28 md:pb-16 md:pt-36">
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(50%_80%_at_80%_0%,#262626_0%,#0A0A0A_70%)]" />
        <div className="container-x">
          <p className="text-xs uppercase tracking-[0.28em] text-gold">Your results</p>
          <h1 className="mt-4 font-serif text-5xl leading-[0.98] tracking-tight md:text-7xl">Your top matches</h1>

          <ul className="mt-8 flex flex-wrap gap-2" aria-label="Your answers">
            {QUIZ_STEPS.map((s) => (
              <li key={s.id} className="rounded-full border border-line px-4 py-2 text-[13px] text-bone/80">
                {labelOf(s.id, answers[s.id])}
              </li>
            ))}
            <li>
              <button type="button" onClick={onRetake} className="min-h-[40px] px-3 text-[13px] text-gold transition-colors hover:text-gold-soft">
                Change answers
              </button>
            </li>
          </ul>
        </div>
      </header>

      <section className="container-x py-12 md:py-20">
        {/* อันดับ 1 */}
        <article className="grid animate-fade-up gap-8 overflow-hidden rounded-3xl border border-line bg-surface p-4 sm:p-6 lg:grid-cols-12 lg:gap-12 lg:p-8">
          <AppLink
            href={guitarUrl(g.slug)}
            aria-label={`View ${g.name}`}
            className="relative block aspect-[4/5] overflow-hidden rounded-2xl bg-gradient-to-b from-[#2b2b2b] to-[#171717] lg:col-span-5"
          >
            <GuitarImage
              guitar={g}
              sizes="(min-width: 1024px) 40vw, 92vw"
              priority
              className="absolute inset-0"
              imgClassName="hover:scale-[1.03]"
            />
            <span className="absolute left-4 top-4 rounded-full bg-gold px-4 py-1.5 text-xs font-medium uppercase tracking-[0.14em] text-ink">Best match</span>
          </AppLink>

          <div className="flex flex-col justify-center lg:col-span-7">
            <div className="flex items-end gap-4">
              <p className="font-mono text-6xl leading-none text-gold md:text-7xl">{top.score}%</p>
              <p className="pb-1.5 text-sm text-mute">match for you</p>
            </div>

            <p className="mt-8 text-xs uppercase tracking-[0.18em] text-mute">{g.brand}</p>
            <h2 className="mt-2 font-serif text-4xl leading-[1.04] tracking-tight md:text-5xl">
              <AppLink href={guitarUrl(g.slug)} className="transition-colors hover:text-gold">{g.name}</AppLink>
            </h2>
            <p className="mt-4 flex items-baseline gap-3">
              <span className="font-mono text-3xl text-gold">{formatPrice(g.price)}</span>
              {g.oldPrice && <span className="font-mono text-base text-mute line-through">{formatPrice(g.oldPrice)}</span>}
            </p>

            <p className="mt-8 text-sm text-mute">Why it fits you</p>
            <ul className="mt-3 space-y-3">
              {top.reasons.map((r) => (
                <li key={r} className="flex items-start gap-3 text-[15px] text-bone/85">
                  <span className="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full border border-gold/50 text-gold">
                    <CheckIcon size={12} />
                  </span>
                  {r}
                </li>
              ))}
            </ul>
            {top.caveats[0] && <p className="mt-4 text-sm text-mute">Worth knowing: {top.caveats[0].toLowerCase()}.</p>}

            <div className="mt-8 max-w-md">
              <MatchButtons guitar={g} />
            </div>
          </div>
        </article>

        {/* อันดับ 2–3 */}
        {others.length > 0 && (
          <>
            <h2 className="mb-6 mt-16 font-serif text-3xl md:mb-8 md:text-4xl">Also worth a look</h2>
            <div className="grid gap-5 sm:grid-cols-2 lg:gap-6">
              {others.map((m, i) => (
                <MatchCard key={m.guitar.id} match={m} rank={i + 2} index={i} />
              ))}
            </div>
          </>
        )}

        {/* ทางไปต่อ */}
        <div className="mt-16 flex flex-col items-start justify-between gap-6 rounded-3xl border border-line bg-surface p-6 sm:p-8 md:flex-row md:items-center">
          <div>
            <h2 className="font-serif text-3xl md:text-4xl">Still deciding?</h2>
            <p className="mt-2 max-w-md text-sm leading-relaxed text-mute">
              {canCompare
                ? `Compare your top ${matches.length} side by side, or browse every guitar that fits your type and budget.`
                : 'Browse every guitar that fits your type and budget, or change your answers to see more options.'}
            </p>
          </div>
          <div className="flex w-full flex-col gap-3 sm:flex-row md:w-auto">
            {canCompare && (
              <Button onClick={compareTop} size="lg">
                Compare top {matches.length}
              </Button>
            )}
            <Button href={catalogUrlFor(answers)} variant="ghost" size="lg">Browse matching guitars</Button>
          </div>
        </div>

        <p className="mt-6 text-xs text-mute">Matches are based on the answers above and our own ratings of each guitar. We only list guitars that genuinely fit, so you may see fewer than three. They are a starting point, not a verdict.</p>
      </section>
    </>
  );
}
