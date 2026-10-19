import { t } from '@/i18n';
import { useShop } from '@/context/ShopContext';
import { cn } from '@/utils/cn';
import { formatPrice } from '@/utils/format';
import { guitarUrl } from '@/utils/routes';
import GuitarImage from '@/components/guitar/GuitarImage';
import AppLink from '@/components/ui/AppLink';
import Badge from '@/components/ui/Badge';
import { ArrowUpRightIcon, CheckIcon, CloseIcon, HeartIcon, PlusIcon } from '@/components/ui/Icons';

const CATEGORY_LABEL = { electric: t('category.electric'), acoustic: t('category.acoustic'), classical: t('category.classical'), bass: t('category.bass') };

/**
 * การ์ดกีตาร์สำหรับหน้า Catalog: รูปใหญ่ + ข้อมูลครบ + ปุ่ม View details / Compare แสดงตลอด
 * (รูปใช้ srcSet เพื่อให้คมชัดตามขนาดหน้าจอ)
 */
export default function CatalogCard({ guitar, index = 0, onRemove, compact = false }) {
  const { compare, wishlist, toggleCompare, toggleWishlist } = useShop();
  const inCompare = compare.includes(guitar.id);
  const inWishlist = wishlist.includes(guitar.id);
  const href = guitarUrl(guitar.slug);

  return (
    <article
      data-guitar-id={guitar.id}
      style={{ animationDelay: `${(index % 9) * 60}ms` }}
      className={cn('group flex h-full animate-fade-up flex-col overflow-hidden rounded-2xl bg-surface ring-1 ring-white/5 transition duration-500 ease-premium hover:-translate-y-1 hover:ring-white/15 hover:shadow-[0_30px_60px_-24px_rgba(0,0,0,0.7)]', compact && 'catalog-product-card')}
    >
      <div className="catalog-card-image relative aspect-[4/5] overflow-hidden bg-gradient-to-b from-[#2b2b2b] to-[#171717]">
        <AppLink href={href} tabIndex={-1} aria-hidden="true" className="absolute inset-0 block">
          <GuitarImage
            guitar={guitar}
            sizes={compact ? '(min-width: 1024px) 25vw, (min-width: 380px) 46vw, 90vw' : '(min-width: 1280px) 30vw, (min-width: 640px) 45vw, 92vw'}
            className="absolute inset-0"
            imgClassName="group-hover:scale-[1.05]"
          />
        </AppLink>
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 bg-gradient-to-t from-surface/40 via-transparent to-transparent" />

        {guitar.badge && (
          <div className="absolute left-4 top-4">
            <Badge type={guitar.badge} />
          </div>
        )}

        {onRemove ? (
          <button
            type="button"
            onClick={() => onRemove(guitar)}
            aria-label={t('wl.removeAria', { name: guitar.name })}
            className="absolute right-3 top-3 inline-flex h-11 items-center gap-2 rounded-full bg-ink/75 pl-4 pr-3 text-xs text-bone backdrop-blur-md transition duration-300 hover:bg-ink hover:text-gold active:scale-95"
          >
            {t('wl.remove')} <CloseIcon size={14} />
          </button>
        ) : (
          <button
            type="button"
            aria-pressed={inWishlist}
            aria-label={inWishlist ? t('wl.removeAria', { name: guitar.name }) : t('wl.saveAria', { name: guitar.name })}
            onClick={() => toggleWishlist(guitar)}
            className={cn(
              'absolute right-3 top-3 grid h-11 w-11 place-items-center rounded-full backdrop-blur-md transition duration-300 ease-premium hover:scale-105 active:scale-95',
              inWishlist ? 'bg-gold text-ink' : 'bg-ink/70 text-bone hover:bg-ink',
            )}
          >
            <HeartIcon size={18} fill={inWishlist ? 'currentColor' : 'none'} />
          </button>
        )}
      </div>

      <div className="catalog-card-copy flex flex-1 flex-col p-5 sm:p-6">
        <div className="flex items-center justify-between gap-3 text-xs">
          <p className="uppercase tracking-[0.14em] text-mute">{guitar.brand}</p>
          <p className="text-mute">{CATEGORY_LABEL[guitar.category]}</p>
        </div>

        <h3 className="mt-2 font-serif text-[1.75rem] leading-[1.08]">
          <AppLink href={href} className="transition-colors hover:text-gold">
            {guitar.name}
          </AppLink>
        </h3>

        <p className="mt-2 text-[11px] text-gold">{t(`status.${guitar.dataStatus ?? 'sample'}`)}</p>
        <ul className="catalog-card-tags mt-4 flex flex-wrap gap-1.5">
          {guitar.tags.map((tag) => (
            <li key={tag} className="rounded-full border border-line px-2.5 py-1 font-mono text-[11px] text-bone/70">
              {tag}
            </li>
          ))}
        </ul>

        <p className="catalog-card-price mt-auto flex flex-wrap items-baseline gap-3 pt-5">
          <span className="font-mono text-xl text-gold">{formatPrice(guitar.price)}</span>
          {guitar.oldPrice && <span className="font-mono text-sm text-mute line-through">{formatPrice(guitar.oldPrice)}</span>}
        </p>

        <div className="catalog-card-actions mt-4 flex gap-2">
          <AppLink
            href={href}
            className="inline-flex h-12 flex-1 items-center justify-center gap-2 rounded-full bg-bone text-sm font-medium text-ink transition duration-300 hover:bg-white active:scale-[0.98]"
          >
            {t('card.view')} <ArrowUpRightIcon size={16} />
          </AppLink>
          <button
            type="button"
            aria-pressed={inCompare}
            aria-label={inCompare ? t('cmp.removeAria', { name: guitar.name }) : t('cmp.addAria', { name: guitar.name })}
            onClick={() => toggleCompare(guitar)}
            className={cn(
              'inline-flex h-12 items-center gap-2 rounded-full border px-5 text-sm transition duration-300 active:scale-[0.98]',
              inCompare ? 'border-gold bg-gold/10 text-gold' : 'border-white/20 text-bone hover:border-gold hover:text-gold',
            )}
          >
            {inCompare ? <CheckIcon size={16} /> : <PlusIcon size={16} />}
            {inCompare ? t('cmp.added') : t('cmp.btn')}
          </button>
        </div>
      </div>
    </article>
  );
}
