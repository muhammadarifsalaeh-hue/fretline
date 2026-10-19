import { BRANDS } from '@/data/brands';
import { CATEGORIES } from '@/data/categories';
import { GUITARS } from '@/data/guitars';
import { MAX_COMPARE } from '@/context/ShopContext';
import { t } from '@/i18n';
import { CompareIcon, GridIcon, GuitarIcon, TagIcon } from '@/components/ui/Icons';

/**
 * สถิติของแคตตาล็อก — คำนวณจากข้อมูลจริงทั้งหมด (ไม่มีตัวเลขโฆษณา)
 * Mobile: กริด 2 คอลัมน์ใต้ปุ่ม | Desktop: แผงลอยทางขวาของ Hero
 */
export default function HeroStats({ style }) {
  const items = [
    { icon: <GuitarIcon size={22} />, value: GUITARS.length, label: t('stat.models') },
    { icon: <TagIcon size={22} />, value: BRANDS.length, label: t('stat.brands') },
    { icon: <GridIcon size={22} />, value: CATEGORIES.filter((c) => c.count > 0).length, label: t('stat.types') },
    { icon: <CompareIcon size={22} />, value: MAX_COMPARE, label: t('stat.compare') },
  ];

  return (
    <dl
      style={style}
      className="mt-10 grid animate-fade-up grid-cols-2 gap-px overflow-hidden rounded-2xl border border-white/10 bg-white/10 lg:absolute lg:right-10 lg:top-1/2 lg:mt-0 lg:w-[150px] lg:-translate-y-1/2 lg:animate-none lg:grid-cols-1 lg:bg-transparent lg:backdrop-blur-xl"
    >
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-3 bg-ink/80 px-4 py-4 lg:border-b lg:border-white/10 lg:bg-ink/60 lg:last:border-b-0">
          <span className="text-gold">{item.icon}</span>
          <div className="flex flex-col">
            <dt className="order-2 text-xs text-mute">{item.label}</dt>
            <dd className="order-1 font-mono text-lg leading-tight text-bone">{item.value}</dd>
          </div>
        </div>
      ))}
    </dl>
  );
}
