import { t } from '@/i18n';
import { useMemo } from 'react';
import { GUITARS } from '@/data/guitars';
import { priceGap } from '@/utils/guitarSort';
import GuitarCard from '@/components/guitar/GuitarCard';
import SectionHeading from '@/components/ui/SectionHeading';

/** แนะนำกีตาร์ใกล้เคียง: ประเภทเดียวกันก่อน แล้วเรียงตามความใกล้เคียงของราคา */
export default function SimilarGuitars({ guitar }) {
  const similar = useMemo(
    () =>
      GUITARS.filter((g) => g.id !== guitar.id)
        .sort((a, b) => {
          const sameA = a.category === guitar.category ? 0 : 1;
          const sameB = b.category === guitar.category ? 0 : 1;
          return sameA - sameB || priceGap(a, guitar) - priceGap(b, guitar);
        })
        .slice(0, 4),
    [guitar],
  );

  return (
    <section className="section-y border-t border-line bg-ink">
      <div className="container-x">
        <SectionHeading title={t('similar.title')} action={{ label: t('feat.viewAll'), href: '/guitars' }} />
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4 lg:gap-6">
          {similar.map((g) => (
            <GuitarCard key={g.id} guitar={g} />
          ))}
        </div>
      </div>
    </section>
  );
}
