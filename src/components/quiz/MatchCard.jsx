import { formatPrice } from '@/utils/format';
import { guitarUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import { CheckIcon } from '@/components/ui/Icons';
import GuitarImage from '@/components/guitar/GuitarImage';
import MatchButtons from './MatchButtons';

/** การ์ดอันดับ 2–3: รูป + เปอร์เซ็นต์ความเหมาะสม + เหตุผลสั้น ๆ */
export default function MatchCard({ match, rank, index = 0 }) {
  const { guitar, score, reasons, caveats } = match;
  return (
    <article
      style={{ animationDelay: `${index * 120}ms` }}
      className="flex animate-fade-up flex-col overflow-hidden rounded-2xl bg-surface ring-1 ring-white/5 transition duration-500 ease-premium hover:-translate-y-1 hover:ring-white/15"
    >
      <AppLink href={guitarUrl(guitar.slug)} className="relative block aspect-[4/3] overflow-hidden bg-gradient-to-b from-[#2b2b2b] to-[#171717]" aria-label={`View ${guitar.name}`}>
        <GuitarImage
          guitar={guitar}
          sizes="(min-width: 640px) 45vw, 92vw"
          className="absolute inset-0"
          imgClassName="hover:scale-[1.04]"
        />
        <span className="absolute left-4 top-4 rounded-full bg-ink/80 px-3 py-1 font-mono text-xs text-bone backdrop-blur">#{rank}</span>
        <span className="absolute right-4 top-4 rounded-full bg-gold px-3 py-1 font-mono text-xs font-medium text-ink">{score}% match</span>
      </AppLink>

      <div className="flex flex-1 flex-col p-5 sm:p-6">
        <p className="text-xs uppercase tracking-[0.14em] text-mute">{guitar.brand}</p>
        <h3 className="mt-2 font-serif text-[1.75rem] leading-[1.08]">
          <AppLink href={guitarUrl(guitar.slug)} className="transition-colors hover:text-gold">{guitar.name}</AppLink>
        </h3>
        <p className="mt-2 font-mono text-xl text-gold">{formatPrice(guitar.price)}</p>

        <ul className="mt-5 space-y-2.5">
          {reasons.slice(0, 3).map((r) => (
            <li key={r} className="flex items-start gap-3 text-sm text-bone/80">
              <CheckIcon size={16} className="mt-0.5 shrink-0 text-gold" />
              {r}
            </li>
          ))}
        </ul>
        {caveats[0] && <p className="mt-3 text-xs text-mute">{caveats[0]}</p>}

        <div className="mt-auto pt-6">
          <MatchButtons guitar={guitar} />
        </div>
      </div>
    </article>
  );
}
