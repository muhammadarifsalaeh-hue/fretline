import { useMemo } from 'react';
import { GUITARS, GUITARS_BY_ID } from '@/data/guitars';
import { useShop } from '@/context/ShopContext';
import { priceGap } from '@/utils/guitarSort';
import { formatPrice } from '@/utils/format';
import Button from '@/components/ui/Button';
import { CompareIcon, PlusIcon } from '@/components/ui/Icons';
import GuitarImage from '@/components/guitar/GuitarImage';

// คู่เปรียบเทียบยอดนิยมให้กดลองได้ทันที
const PRESETS = [
  { label: 'Stratocaster vs Les Paul', ids: ['fender-american-professional-ii-stratocaster', 'gibson-les-paul-standard-60s'] },
  { label: 'Taylor 214ce vs Martin D-18', ids: ['taylor-214ce', 'martin-d-18'] },
  { label: 'Jazz Bass vs Precision Bass', ids: ['fender-player-ii-jazz-bass', 'fender-player-precision-bass'] },
];

/** ยังเลือกไม่ครบ 2 รุ่น: บอกว่าต้องทำอะไรต่อ + ทางลัด */
export default function CompareEmpty({ selected, onAdd }) {
  const { setCompareIds, toggleCompare } = useShop();
  const first = selected[0];

  // ถ้าเลือกไว้ 1 รุ่น: แนะนำรุ่นใกล้เคียง
  const suggestions = useMemo(() => {
    if (!first) return [];
    return GUITARS.filter((g) => g.id !== first.id)
      .sort((a, b) => (a.category === first.category ? 0 : 1) - (b.category === first.category ? 0 : 1) || priceGap(a, first) - priceGap(b, first))
      .slice(0, 3);
  }, [first]);

  return (
    <div className="rounded-3xl border border-dashed border-line px-6 py-14 text-center md:py-20">
      <span className="mx-auto grid h-16 w-16 place-items-center rounded-full border border-line text-gold">
        <CompareIcon size={26} />
      </span>
      <h2 className="mt-6 font-serif text-3xl md:text-4xl">
        {first ? 'Add one more guitar to compare' : 'Choose two to four guitars'}
      </h2>
      <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-mute">
        {first
          ? `${first.brand} ${first.name} is ready. Pick at least one more to see the differences side by side.`
          : 'Pick guitars from the catalog or add them here, and every spec is lined up so the differences stand out.'}
      </p>

      <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
        <Button onClick={onAdd}>
          <PlusIcon size={16} /> Add a guitar
        </Button>
        <Button href="/guitars" variant="ghost">Browse the catalog</Button>
      </div>

      {first ? (
        <ul className="mx-auto mt-12 max-w-xl space-y-2 text-left">
          <li className="mb-3 text-center text-xs text-mute">Similar guitars</li>
          {suggestions.map((g) => (
            <li key={g.id}>
              <button
                type="button"
                onClick={() => toggleCompare(g)}
                className="flex w-full items-center gap-4 rounded-2xl border border-line bg-surface px-3 py-3 text-left transition hover:border-gold/60"
              >
                <GuitarImage guitar={g} size="sm" alt="" className="h-14 w-14 shrink-0 rounded-xl" />
                <span className="min-w-0 flex-1">
                  <span className="block text-xs text-mute">{g.brand}</span>
                  <span className="block truncate font-serif text-lg leading-tight">{g.name}</span>
                </span>
                <span className="font-mono text-sm text-gold">{formatPrice(g.price)}</span>
                <PlusIcon size={18} className="text-bone/70" />
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <div className="mt-12">
          <p className="mb-4 text-xs text-mute">Or try a popular comparison</p>
          <ul className="flex flex-wrap justify-center gap-2">
            {PRESETS.map((p) => (
              <li key={p.label}>
                <button
                  type="button"
                  onClick={() => setCompareIds(p.ids.filter((id) => GUITARS_BY_ID[id]))}
                  className="min-h-[44px] rounded-full border border-white/15 px-5 text-sm text-bone/80 transition hover:border-gold hover:text-gold"
                >
                  {p.label}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
