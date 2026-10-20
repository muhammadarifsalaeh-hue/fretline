import { t } from '@/i18n';
import { MAX_COMPARE, useShop } from '@/context/ShopContext';
import { cn } from '@/utils/cn';
import { formatPrice } from '@/utils/format';
import { guitarUrl } from '@/utils/routes';
import Badge from '@/components/ui/Badge';
import { ArrowUpRightIcon, CheckIcon, HeartIcon, PlusIcon } from '@/components/ui/Icons';
import GuitarImage from './GuitarImage';
import AppLink from '@/components/ui/AppLink';

/** ปุ่มกลมมุมขวาบนของการ์ด (Wishlist / Compare) */
function CardAction({ label, active, disabled = false, onClick, children }) {
  return (
    <button
      type="button"
      aria-label={label}
      aria-pressed={active}
      disabled={disabled}
      onClick={onClick}
      className={cn(
        'grid h-11 w-11 place-items-center rounded-full backdrop-blur-md transition duration-300 ease-premium hover:scale-105 active:scale-95',
        active ? 'bg-gold text-ink' : 'bg-ink/70 text-bone hover:bg-ink',
      )}
    >
      {children}
    </button>
  );
}

export default function GuitarCard({ guitar }) {
  const { compare, wishlist, toggleCompare, toggleWishlist } = useShop();
  const inCompare = compare.includes(guitar.id);
  const inWishlist = wishlist.includes(guitar.id);
  const compareFull = !inCompare && compare.length >= MAX_COMPARE;

  return (
    <article data-guitar-id={guitar.id} className="guitar-card group relative flex h-full flex-col overflow-hidden rounded-lg border border-white/[0.07] bg-surface text-bone ring-1 ring-white/5 transition duration-500 ease-premium hover:-translate-y-1 hover:border-gold/40 hover:shadow-[0_30px_60px_-20px_rgba(0,0,0,0.6)]">
      {/* พื้นที่รูป 4:5 */}
      <div className="relative aspect-[4/5] overflow-hidden bg-gradient-to-b from-[#191919] to-[#101010]">
        <GuitarImage
          guitar={guitar}
          sizes="(min-width: 1024px) 25vw, (min-width: 640px) 50vw, 82vw"
          className="absolute inset-0"
          imgClassName="group-hover:scale-[1.05]"
        />
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 bg-gradient-to-t from-surface/50 via-transparent to-transparent" />

        {guitar.badge && (
          <div className="absolute left-4 top-4 z-10">
            <Badge type={guitar.badge} />
          </div>
        )}

        {/* ปุ่ม hover (บนมือถือแสดงถาวร) */}
        <div
          className={cn(
            'absolute right-3 top-3 z-10 flex flex-col gap-2 transition duration-300 ease-premium',
            'group-focus-within:translate-y-0 group-focus-within:opacity-100 group-hover:translate-y-0 group-hover:opacity-100',
            '[@media(hover:none)]:translate-y-0 [@media(hover:none)]:opacity-100',
            inCompare || inWishlist ? 'translate-y-0 opacity-100' : '-translate-y-1 opacity-0',
          )}
        >
          <CardAction
            label={inWishlist ? t('wl.removeAria', { name: guitar.name }) : t('wl.saveAria', { name: guitar.name })}
            active={inWishlist}
            onClick={() => toggleWishlist(guitar)}
          >
            <HeartIcon size={18} fill={inWishlist ? 'currentColor' : 'none'} />
          </CardAction>
          <CardAction
            label={compareFull ? t('p4.compare.fullNote') : inCompare ? t('cmp.removeAria', { name: guitar.name }) : t('cmp.addAria', { name: guitar.name })}
            active={inCompare}
            disabled={compareFull}
            onClick={() => toggleCompare(guitar)}
          >
            {inCompare ? <CheckIcon size={18} /> : <PlusIcon size={18} />}
          </CardAction>
        </div>

        {/* ลิงก์เลื่อนขึ้นจากด้านล่างรูปตอน hover */}
        <AppLink
          href={guitarUrl(guitar.slug)}
          className="absolute inset-x-4 bottom-4 z-10 flex h-11 translate-y-3 items-center justify-center gap-2 rounded-full bg-bone text-sm font-medium text-ink opacity-0 transition duration-300 ease-premium focus-visible:translate-y-0 focus-visible:opacity-100 group-hover:translate-y-0 group-hover:opacity-100 [@media(hover:none)]:hidden"
        >
          {t('card.view')} <ArrowUpRightIcon size={16} />
        </AppLink>
      </div>

      <div className="card-copy flex flex-1 flex-col gap-3 p-5">
        <p className="text-[11px] text-gold">{t(`status.${guitar.dataStatus ?? 'sample'}`)}</p>
        <p className="text-xs uppercase tracking-[0.14em] text-mute">{guitar.brand}</p>
        <h3 className="font-serif text-2xl leading-[1.15]">
          <AppLink href={guitarUrl(guitar.slug)} className="after:absolute after:inset-x-0 after:top-0 after:bottom-0 after:content-[''] after:z-0 hover:text-gold transition-colors">
            <span className="sr-only">{guitar.brand} </span>
            {guitar.name}
          </AppLink>
        </h3>

        <ul className="flex flex-wrap gap-1.5">
          {guitar.tags.map((tag) => (
            <li key={tag} className="rounded-full border border-line px-2.5 py-1 font-mono text-[11px] text-bone/70">
              {tag}
            </li>
          ))}
        </ul>

        <p className="mt-auto flex items-baseline gap-3 pt-3">
          <span className="font-mono text-xl text-gold">{formatPrice(guitar.price)}</span>
          {guitar.oldPrice && <span className="font-mono text-sm text-mute line-through">{formatPrice(guitar.oldPrice)}</span>}
        </p>
      </div>
    </article>
  );
}
