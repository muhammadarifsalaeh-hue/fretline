import { t } from '@/i18n';
import { trustedPrice, trustedWeight, verifiedRating } from '@/utils/dataTrust';
import { formatPrice } from '@/utils/format';
import { guitarUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import GuitarImage from '@/components/guitar/GuitarImage';

/** สรุปเร็ว ๆ: ถูกที่สุด / เบาที่สุด / คะแนนสูงสุด (แสดงเฉพาะเมื่อแต่ละรุ่นมีค่าต่างกัน) */
export default function CompareVerdicts({ guitars }) {
  const pick = (getter, mode) => {
    const values = guitars.map(getter).filter((v) => typeof v === 'number');
    if (values.length < 2 || new Set(values).size === 1) return null;
    const target = mode === 'min' ? Math.min(...values) : Math.max(...values);
    return guitars.find((g) => getter(g) === target);
  };

  const cheapest = pick(trustedPrice, 'min');
  const lightest = pick(trustedWeight, 'min');
  const topRated = pick((g) => verifiedRating(g)?.score ?? null, 'max');

  const items = [
    cheapest && { label: t('p4.compare.lowest'), guitar: cheapest, value: formatPrice(cheapest.price) },
    lightest && { label: t('p4.compare.lightest'), guitar: lightest, value: `${lightest.specs.weightKg} kg` },
    topRated && { label: t('p4.compare.topRated'), guitar: topRated, value: `★ ${topRated.rating.score.toFixed(1)}` },
  ].filter(Boolean);

  if (!items.length) return null;

  return (
    <ul className="mb-10 grid gap-3 sm:grid-cols-3">
      {items.map((item) => (
        <li key={item.label} className="min-w-0">
          <AppLink
            href={guitarUrl(item.guitar.slug)}
            className="group flex items-center gap-4 rounded-2xl border border-line bg-surface p-3 pr-5 transition duration-300 hover:border-gold/60"
          >
            <GuitarImage guitar={item.guitar} size="sm" alt="" className="h-16 w-16 shrink-0 rounded-xl" />
            <span className="min-w-0 flex-1">
              <span className="block text-xs text-mute">{item.label}</span>
              <span className="block truncate font-serif text-xl leading-tight transition-colors group-hover:text-gold">{item.guitar.name}</span>
            </span>
            <span className="font-mono text-sm text-gold">{item.value}</span>
          </AppLink>
        </li>
      ))}
    </ul>
  );
}
