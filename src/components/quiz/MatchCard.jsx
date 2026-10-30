import { t } from '@/i18n';
import { publicPrice } from '@/utils/dataTrust';
import { guitarUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import { CheckIcon } from '@/components/ui/Icons';
import GuitarImage from '@/components/guitar/GuitarImage';
import MatchButtons from './MatchButtons';

export default function MatchCard({ match, rank, featured = false }) {
  const { guitar, score, reasons, caveats } = match;
  return (
    <article className={`match-card ${featured ? 'match-card-featured' : ''}`} data-guitar-id={guitar.id}>
      <AppLink href={guitarUrl(guitar.slug)} data-product-image-slot="square" className="product-image-slot match-image" aria-label={t('cmp.viewAria', { name: `${guitar.brand} ${guitar.name}` })}>
        <GuitarImage guitar={guitar} sizes={featured ? '(min-width: 768px) 40vw, 90vw' : '(min-width: 768px) 40vw, 90vw'} priority={featured} className="absolute inset-0" />
        <span className="match-rank">#{rank} {featured && t('p4.quiz.topMatch')}</span>
      </AppLink>
      <div className="match-copy">
        <div className="flex flex-wrap items-center justify-between gap-3"><span className="discovery-kicker">{guitar.brand}</span><span className="match-score">{score}% <span>{t('p4.quiz.alignment')}</span></span></div>
        {featured ? <h2><AppLink href={guitarUrl(guitar.slug)}>{guitar.name}</AppLink></h2> : <h3><AppLink href={guitarUrl(guitar.slug)}>{guitar.name}</AppLink></h3>}
        <p className="mt-3 text-xs text-gold">{t(`status.${guitar.dataStatus ?? 'sample'}`)}</p>
        <p className="mt-2 font-mono text-lg text-bone">{publicPrice(guitar)}</p>
        <h4 className="mb-3 mt-6 text-xs font-medium text-gold">{t('p4.quiz.why')}</h4>
        <ul className="space-y-2.5">{reasons.map((reason) => <li key={reason} className="flex items-start gap-2 text-sm leading-6 text-bone/80"><CheckIcon size={15} className="mt-1 shrink-0 text-gold" />{reason}</li>)}</ul>
        <details className="match-caveats"><summary>{t('p4.quiz.dataCaveats')}</summary><ul>{caveats.map((caveat) => <li key={caveat}>{caveat}</li>)}</ul></details>
        <p className="mt-3 text-[11px] leading-6 text-mute">{t('p4.quiz.profileNote')}</p>
        <div className="mt-auto pt-5"><MatchButtons guitar={guitar} /></div>
      </div>
    </article>
  );
}
