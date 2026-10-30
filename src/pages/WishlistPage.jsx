import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { t } from '@/i18n';
import CatalogEmpty from '@/components/catalog/CatalogEmpty';
import AppLink from '@/components/ui/AppLink';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import DiscoveryHeading from '@/components/ui/DiscoveryHeading';
import SortSelect from '@/components/ui/SortSelect';
import WishlistRow from '@/components/wishlist/WishlistRow';
import { ArrowRightIcon, HeartIcon } from '@/components/ui/Icons';
import { SAVED_GUITARS_BY_ID } from '@/data/guitars';
import { MAX_COMPARE, useShop } from '@/context/ShopContext';
import { WISHLIST_SORTS, sortGuitars } from '@/utils/guitarSort';

/** Wishlist IDs live only in ShopContext; every page uses that same persisted list. */
export default function WishlistPage() {
  const { wishlist, compare, toggleWishlist, clearWishlist, setCompareIds } = useShop();
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const sort = WISHLIST_SORTS.some((option) => option.id === params.get('sort')) ? params.get('sort') : 'saved';
  const [dialog, setDialog] = useState(null);
  const closeDialog = useCallback(() => setDialog(null), []);
  const listRef = useRef(null);
  const countRef = useRef(null);
  const items = useMemo(() => wishlist.map((id) => SAVED_GUITARS_BY_ID[id]).filter(Boolean), [wishlist]);
  const sorted = useMemo(() => sortGuitars(items, sort, { verifiedOnly: true }), [items, sort]);
  const candidateIds = sorted.slice(0, MAX_COMPARE).map((guitar) => guitar.id);
  useEffect(() => { document.title = t('p5.wish.docTitle'); }, []);

  const compareSaved = () => {
    setCompareIds(candidateIds);
    setDialog(null);
    navigate(`/compare?${new URLSearchParams({ ids: candidateIds.join(',') })}`);
  };
  const askCompare = () => {
    if (compare.length && compare.join(',') !== candidateIds.join(',')) setDialog('compare');
    else compareSaved();
  };
  const onRemove = (guitar, index) => {
    toggleWishlist(guitar);
    requestAnimationFrame(() => {
      const links = listRef.current?.querySelectorAll('[data-wishlist-detail]');
      (links?.[Math.min(index, links.length - 1)] ?? countRef.current)?.focus({ preventScroll: true });
    });
  };
  const onConfirm = () => {
    if (dialog === 'compare') { compareSaved(); return; }
    clearWishlist();
    setDialog(null);
    requestAnimationFrame(() => document.getElementById('wishlist-browse')?.focus({ preventScroll: true }));
  };
  const onSort = (value) => {
    const search = new URLSearchParams();
    if (value !== 'saved') search.set('sort', value);
    setParams(search);
  };

  return (
    <div className="phase5-page wishlist-page">
      <DiscoveryHeading eyebrow={t('targeted.wishlist.kicker')} title={t('p5.wish.title')} description={t('p5.wish.intro')}
        breadcrumbs={[{ label: t('nav.wishlist') }]}
        aside={<p className="phase5-heading-meta"><HeartIcon size={15} />{t('p5.wish.local')}</p>} />
      <section className="container-x phase5-body" aria-label={t('p5.wish.title')}>
        <p className="wishlist-count" aria-live="polite" aria-atomic="true" ref={countRef} tabIndex={-1}>{t('p5.wish.count', { n: items.length })}</p>
        {!items.length ? <CatalogEmpty icon={<HeartIcon size={28} />} title={t('p5.wish.empty')} text={t('p5.wish.emptyText')}>
          <div className="phase5-empty-actions">
            <AppLink id="wishlist-browse" href="/guitars" className="phase4-button is-gold">{t('p5.wish.browse')}<ArrowRightIcon size={16} /></AppLink>
            <AppLink href="/find-my-guitar" className="phase4-button">{t('p5.wish.quiz')}</AppLink>
          </div>
        </CatalogEmpty> : <>
          <div className="wishlist-toolbar">
            <SortSelect value={sort} onChange={onSort} options={WISHLIST_SORTS} />
            <div className="wishlist-tools">
              {items.length >= 2 && <button type="button" className="phase4-button is-gold" onClick={askCompare}>
                {t(items.length > MAX_COMPARE ? 'p5.wish.compareFirst' : 'p5.wish.compare', { n: Math.min(items.length, MAX_COMPARE) })}
              </button>}
              <button type="button" onClick={() => setDialog('clear')} className="phase4-button">{t('p5.wish.clear')}</button>
            </div>
          </div>
          <p className="phase5-note">{t('p5.wish.dataNote')}{sort.startsWith('price') && <> {t('p5.wish.priceSortNote')}</>}</p>
          {items.some((guitar) => guitar.archived) && <p className="archive-notice" role="note">{t('p7.archive.saved')}</p>}
          <ul className="wishlist-list" aria-label={t('p5.wish.list')} ref={listRef}>
            {sorted.map((guitar, index) => <WishlistRow key={guitar.id} guitar={guitar} onRemove={() => onRemove(guitar, index)} />)}
          </ul>
          <div className="wishlist-after-list">
            <p>{t('p5.wish.imageNote')}</p>
            {items.length >= 2 && <p>{t('p5.wish.compareHint')}</p>}
            {compare.length >= MAX_COMPARE && <p className="text-gold" role="status">{t('p5.wish.compareFull')}</p>}
            <AppLink href="/guitars" className="phase4-button">{t('p5.wish.browse')}<ArrowRightIcon size={16} /></AppLink>
          </div>
        </>}
      </section>
      <ConfirmDialog open={Boolean(dialog)} onClose={closeDialog} onConfirm={onConfirm}
        title={t(dialog === 'compare' ? 'p5.wish.compareTitle' : 'p5.wish.clearTitle')}
        description={t(dialog === 'compare' ? 'p5.wish.compareText' : 'p5.wish.clearText')}
        confirmLabel={t(dialog === 'compare' ? 'p5.wish.replace' : 'p4.confirmClear')} />
    </div>
  );
}
