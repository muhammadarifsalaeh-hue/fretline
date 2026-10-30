import { t } from '@/i18n';
import { MAX_COMPARE, useShop } from '@/context/ShopContext';
import { publicPrice } from '@/utils/dataTrust';
import { guitarUrl, brandUrl } from '@/utils/routes';
import GuitarImage from '@/components/guitar/GuitarImage';
import PriceSourceNote from '@/components/guitar/PriceSourceNote';
import AppLink from '@/components/ui/AppLink';
import { ArrowUpRightIcon, CheckIcon, HeartIcon, PlusIcon } from '@/components/ui/Icons';

export default function WishlistRow({ guitar, onRemove }) {
  const { compare, toggleCompare } = useShop();
  const selected = compare.includes(guitar.id);
  const full = !selected && compare.length >= MAX_COMPARE;
  return (
    <li className="wishlist-row" data-guitar-id={guitar.id}>
      <AppLink href={guitarUrl(guitar.slug)} tabIndex={-1} aria-hidden="true" data-product-image-slot="square" className="product-image-slot wishlist-image">
        <GuitarImage guitar={guitar} size="sm" className="absolute inset-0" sizes="100px" />
      </AppLink>
      <div className="wishlist-copy">
        <AppLink href={brandUrl(guitar.brand)} className="wishlist-brand">{guitar.brand}</AppLink>
        <h2><AppLink href={guitarUrl(guitar.slug)} data-wishlist-detail>{guitar.name}</AppLink></h2>
        {guitar.archived && <p className="archive-label">{t('p7.archive.label')}</p>}
        <p className="wishlist-meta">{t(`category.${guitar.category}`)}<span aria-hidden="true">·</span><span>{t(`status.${guitar.dataStatus ?? 'sample'}`)}</span></p>
        <p className="wishlist-price">{publicPrice(guitar)}</p>
        <PriceSourceNote guitar={guitar} />
      </div>
      <div className="wishlist-row-actions">
        <button type="button" onClick={onRemove} className="wishlist-heart" aria-label={t('wl.removeAria', { name: guitar.name })}>
          <HeartIcon size={19} fill="currentColor" />
        </button>
        <AppLink href={guitarUrl(guitar.slug)} className="wishlist-detail-link" aria-label={t('cmp.viewAria', { name: guitar.name })}>
          <span>{t('card.view')}</span><ArrowUpRightIcon size={17} />
        </AppLink>
        <button type="button" aria-pressed={selected} disabled={full} title={full ? t('p5.wish.compareFull') : undefined}
          aria-label={selected ? t('cmp.removeAria', { name: guitar.name }) : t('cmp.addAria', { name: guitar.name })}
          className={`wishlist-compare ${selected ? 'is-active' : ''}`} onClick={() => toggleCompare(guitar)}>
          {selected ? <CheckIcon size={16} /> : <PlusIcon size={16} />}<span>{selected ? t('cmp.added') : t('cmp.btn')}</span>
        </button>
      </div>
    </li>
  );
}
