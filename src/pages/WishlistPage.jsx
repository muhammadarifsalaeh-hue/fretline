import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CatalogCard from '@/components/catalog/CatalogCard';
import CatalogEmpty from '@/components/catalog/CatalogEmpty';
import AppLink from '@/components/ui/AppLink';
import Button from '@/components/ui/Button';
import { ChevronDownIcon, HeartIcon } from '@/components/ui/Icons';
import { GUITARS_BY_ID } from '@/data/guitars';
import { MAX_COMPARE, useShop } from '@/context/ShopContext';
import { formatPrice } from '@/utils/format';
import { WISHLIST_SORTS, sortGuitars } from '@/utils/guitarSort';

/**
 * /wishlist — ใช้ระบบ Wishlist เดิมใน ShopContext (รายการที่กดหัวใจไว้ที่ใดก็ได้) ไม่มีที่เก็บซ้ำ
 */
export default function WishlistPage() {
  const { wishlist, toggleWishlist, clearWishlist, setCompareIds } = useShop();
  const navigate = useNavigate();
  const [sort, setSort] = useState('saved');
  const [confirmClear, setConfirmClear] = useState(false);
  const timer = useRef(0);

  useEffect(() => {
    document.title = 'Wishlist — Fretline';
    return () => window.clearTimeout(timer.current);
  }, []);

  // รหัสที่ไม่มีในข้อมูลแล้ว (เช่น รุ่นถูกลบ) จะถูกข้าม
  const items = useMemo(() => wishlist.map((id) => GUITARS_BY_ID[id]).filter(Boolean), [wishlist]);
  const sorted = useMemo(() => sortGuitars(items, sort), [items, sort]);
  const priced = items.filter((g) => g.price != null);
  const total = priced.reduce((sum, g) => sum + g.price, 0);
  const onRequest = items.length - priced.length;

  const askClear = () => {
    if (confirmClear) {
      window.clearTimeout(timer.current);
      setConfirmClear(false);
      clearWishlist();
      return;
    }
    setConfirmClear(true);
    timer.current = window.setTimeout(() => setConfirmClear(false), 4000);
  };

  const compareSaved = () => {
    setCompareIds(sorted.slice(0, MAX_COMPARE).map((g) => g.id));
    navigate('/compare');
  };

  return (
    <>
      <header className="relative isolate border-b border-line pb-12 pt-28 md:pb-16 md:pt-36">
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(50%_80%_at_80%_0%,#262626_0%,#0A0A0A_70%)]" />
        <div className="container-x">
          <nav aria-label="Breadcrumb" className="mb-6 flex items-center gap-2 text-sm text-mute">
            <AppLink href="/" className="transition-colors hover:text-bone">Home</AppLink>
            <span aria-hidden="true">/</span>
            <span className="text-bone/80">Wishlist</span>
          </nav>
          <h1 className="font-serif text-5xl leading-[0.98] tracking-tight md:text-7xl">Wishlist</h1>
          <p className="mt-5 max-w-lg text-base leading-relaxed text-mute md:text-lg" aria-live="polite">
            {items.length === 0
              ? 'Guitars you save will appear here.'
              : `${items.length} saved ${items.length === 1 ? 'guitar' : 'guitars'}${priced.length ? `, ${formatPrice(total)} in total${onRequest ? ` for the ${priced.length} with a listed price` : ''}` : ', price on request'}.`}
          </p>
        </div>
      </header>

      <section className="container-x pb-24 pt-8 md:pt-10">
        {items.length === 0 ? (
          <CatalogEmpty
            icon={<HeartIcon size={26} />}
            title="Your wishlist is empty"
            text="Tap the heart on any guitar to save it here, then compare your favourites side by side."
          >
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Button href="/guitars">Browse guitars</Button>
              <Button href="/find-my-guitar" variant="ghost">Find my guitar</Button>
            </div>
          </CatalogEmpty>
        ) : (
          <>
            <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <label className="relative w-full md:w-auto">
                <span className="sr-only">Sort by</span>
                <select
                  value={sort}
                  onChange={(e) => setSort(e.target.value)}
                  className="h-12 w-full appearance-none rounded-full border border-line bg-surface pl-5 pr-11 text-sm text-bone transition focus:border-gold focus:outline-none md:w-auto"
                >
                  {WISHLIST_SORTS.map((o) => (
                    <option key={o.id} value={o.id} className="bg-surface">{o.label}</option>
                  ))}
                </select>
                <ChevronDownIcon size={18} className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-mute" />
              </label>

              <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
                {items.length >= 2 && (
                  <Button onClick={compareSaved} variant="ghost" className="h-11">
                    {items.length > MAX_COMPARE ? `Compare first ${MAX_COMPARE}` : `Compare ${items.length}`}
                  </Button>
                )}
                <button
                  type="button"
                  onClick={askClear}
                  className={`min-h-[44px] px-2 text-sm transition-colors ${confirmClear ? 'text-gold' : 'text-bone/80 hover:text-gold'}`}
                >
                  {confirmClear ? 'Tap again to remove all' : 'Clear all'}
                </button>
              </div>
            </div>

            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 lg:gap-6">
              {sorted.map((guitar, i) => (
                <CatalogCard key={guitar.id} guitar={guitar} index={i} onRemove={toggleWishlist} />
              ))}
            </div>

            <div className="mt-14 text-center">
              <AppLink href="/guitars" className="text-sm text-gold transition-colors hover:text-gold-soft">
                Keep browsing the catalog
              </AppLink>
            </div>
          </>
        )}
      </section>
    </>
  );
}
