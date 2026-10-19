import { t } from '@/i18n';
import { MAX_COMPARE, useShop } from '@/context/ShopContext';
import { cn } from '@/utils/cn';
import { guitarUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import { ArrowUpRightIcon, CheckIcon, HeartIcon, PlusIcon } from '@/components/ui/Icons';

export default function MatchButtons({ guitar }) {
  const { compare, wishlist, toggleCompare, toggleWishlist } = useShop();
  const inCompare = compare.includes(guitar.id);
  const saved = wishlist.includes(guitar.id);
  return (
    <div className="match-actions">
      <AppLink href={guitarUrl(guitar.slug)} className="phase4-button is-gold">{t('card.view')}<ArrowUpRightIcon size={15} /></AppLink>
      <button type="button" disabled={!inCompare && compare.length >= MAX_COMPARE} aria-pressed={inCompare}
        aria-label={t(inCompare ? 'cmp.removeAria' : 'cmp.addAria', { name: guitar.name })} onClick={() => toggleCompare(guitar)} className={cn('phase4-button', inCompare && 'is-active')}>
        {inCompare ? <CheckIcon size={15} /> : <PlusIcon size={15} />}{t(inCompare ? 'cmp.added' : 'cmp.btn')}
      </button>
      <button type="button" aria-pressed={saved} aria-label={t(saved ? 'wl.removeAria' : 'wl.saveAria', { name: guitar.name })} onClick={() => toggleWishlist(guitar)} className={cn('phase4-button', saved && 'is-active')}><HeartIcon size={16} fill={saved ? 'currentColor' : 'none'} /></button>
    </div>
  );
}
