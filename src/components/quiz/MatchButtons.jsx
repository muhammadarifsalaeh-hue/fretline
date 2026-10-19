import { useShop } from '@/context/ShopContext';
import { cn } from '@/utils/cn';
import { guitarUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import { ArrowUpRightIcon, CheckIcon, PlusIcon } from '@/components/ui/Icons';

/** ปุ่ม View details + Compare ที่ใช้ซ้ำในผลลัพธ์ทุกใบ */
export default function MatchButtons({ guitar }) {
  const { compare, toggleCompare } = useShop();
  const inCompare = compare.includes(guitar.id);
  return (
    <div className="flex gap-2">
      <AppLink
        href={guitarUrl(guitar.slug)}
        className="inline-flex h-12 flex-1 items-center justify-center gap-2 rounded-full bg-bone text-sm font-medium text-ink transition duration-300 hover:bg-white active:scale-[0.98]"
      >
        View details <ArrowUpRightIcon size={16} />
      </AppLink>
      <button
        type="button"
        aria-pressed={inCompare}
        aria-label={inCompare ? `Remove ${guitar.name} from compare` : `Add ${guitar.name} to compare`}
        onClick={() => toggleCompare(guitar)}
        className={cn(
          'inline-flex h-12 items-center gap-2 rounded-full border px-5 text-sm transition duration-300 active:scale-[0.98]',
          inCompare ? 'border-gold bg-gold/10 text-gold' : 'border-white/20 text-bone hover:border-gold hover:text-gold',
        )}
      >
        {inCompare ? <CheckIcon size={16} /> : <PlusIcon size={16} />}
        {inCompare ? 'Added' : 'Compare'}
      </button>
    </div>
  );
}
