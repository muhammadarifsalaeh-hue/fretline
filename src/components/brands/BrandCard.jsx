import { CATEGORIES } from '@/data/categories';
import { cn } from '@/utils/cn';
import { formatPrice } from '@/utils/format';
import { brandUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import GuitarArt from '@/components/ui/GuitarArt';
import { ArrowUpRightIcon } from '@/components/ui/Icons';

const typeName = (id) => CATEGORIES.find((c) => c.id === id)?.name ?? id;

/**
 * การ์ดแบรนด์: โลโก้ (ถ้ามีไฟล์) หรือชื่อแบรนด์แบบตัวอักษร + เส้นร่างกีตาร์ประเภทหลักของแบรนด์
 * ข้อมูลทั้งหมดมาจาก data/brands.js (คำนวณจาก Catalog)
 */
export default function BrandCard({ brand, index = 0 }) {
  const meta = [brand.country, brand.founded && `est. ${brand.founded}`].filter(Boolean).join(', ');

  return (
    <AppLink
      href={brandUrl(brand.name)}
      aria-label={`${brand.name}, ${brand.models} ${brand.models === 1 ? 'model' : 'models'}`}
      style={{ animationDelay: `${(index % 9) * 60}ms` }}
      className="group flex h-full animate-fade-up flex-col overflow-hidden rounded-2xl bg-surface ring-1 ring-white/5 transition duration-500 ease-premium hover:-translate-y-1 hover:ring-white/15 hover:shadow-[0_30px_60px_-24px_rgba(0,0,0,0.7)]"
    >
      <div className="relative aspect-[16/10] overflow-hidden bg-gradient-to-br from-[#2a2a2a] via-[#181818] to-[#0f0f0f]">
        <div aria-hidden="true" className="absolute inset-0 bg-[radial-gradient(60%_60%_at_25%_20%,rgba(200,161,90,0.12),transparent_70%)]" />
        <div aria-hidden="true" className="absolute -right-6 top-1/2 h-[150%] -translate-y-1/2 text-gold/25 transition-transform duration-700 ease-premium group-hover:scale-105">
          <GuitarArt type={brand.mainCategory} className="h-full w-auto" style={{ transform: 'rotate(-24deg)' }} />
        </div>

        <span className="absolute right-4 top-4 grid h-11 w-11 place-items-center rounded-full border border-white/25 bg-ink/40 text-bone backdrop-blur-md transition duration-500 ease-premium group-hover:rotate-45 group-hover:border-gold group-hover:text-gold">
          <ArrowUpRightIcon size={18} />
        </span>

        <div className="absolute inset-x-6 bottom-6">
          {brand.logo ? (
            <img src={brand.logo} alt={brand.name} loading="lazy" className="max-h-12 max-w-[70%] object-contain object-left" />
          ) : (
            <span className="block font-serif text-4xl leading-none tracking-tight sm:text-5xl">{brand.name}</span>
          )}
        </div>
      </div>

      <div className="flex flex-1 flex-col p-5 sm:p-6">
        <div className="flex items-baseline justify-between gap-3">
          <p className="font-mono text-sm text-bone">
            {brand.models} {brand.models === 1 ? 'model' : 'models'}
          </p>
          {meta && <p className="text-xs text-mute">{meta}</p>}
        </div>

        <ul className="mt-4 flex flex-wrap gap-1.5">
          {brand.categories.map((c) => (
            <li key={c} className="rounded-full border border-line px-2.5 py-1 text-[11px] text-bone/70">
              {typeName(c)}
            </li>
          ))}
        </ul>

        <p className="mt-auto pt-5 font-mono text-sm text-gold">
          {brand.priceMin == null ? formatPrice(null) : brand.priceMin === brand.priceMax ? formatPrice(brand.priceMin) : `${formatPrice(brand.priceMin)} – ${formatPrice(brand.priceMax)}`}
        </p>
      </div>
    </AppLink>
  );
}
