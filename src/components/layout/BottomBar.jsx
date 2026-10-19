import { useShop } from '@/context/ShopContext';
import { t } from '@/i18n';
import useSearchNavigation from '@/hooks/useSearchNavigation';
import AppLink from '@/components/ui/AppLink';
import { CompareIcon, HeartIcon, HomeIcon, SearchIcon } from '@/components/ui/Icons';

/** แถบเมนูล่างสำหรับมือถือ/แท็บเล็ต: Home / Search / Compare / Wishlist */
export default function BottomBar() {
  const handleSearch = useSearchNavigation();
  const { compare, wishlist } = useShop();

  const items = [
    { label: t('nav.home'), icon: <HomeIcon />, href: '/', onClick: () => window.scrollTo({ top: 0, behavior: 'smooth' }) },
    { label: t('nav.search'), icon: <SearchIcon />, onClick: handleSearch },
    { label: t('nav.compare'), icon: <CompareIcon />, href: '/compare', count: compare.length },
    { label: t('nav.wishlist'), icon: <HeartIcon />, href: '/wishlist', count: wishlist.length },
  ];

  return (
    <nav
      aria-label={t('nav.quick')}
      className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-4 border-t border-line bg-ink/90 pb-[env(safe-area-inset-bottom)] backdrop-blur-xl lg:hidden"
    >
      {items.map((item) => {
        const Comp = item.href ? AppLink : 'button';
        return (
          <Comp
            key={item.label}
            href={item.href}
            onClick={item.onClick}
            className="relative flex min-h-[60px] flex-col items-center justify-center gap-1 text-[11px] text-bone/70 transition-colors active:text-gold"
          >
            <span className="relative">
              {item.icon}
              {item.count > 0 && (
                <span className="absolute -right-2.5 -top-1.5 grid h-4 min-w-4 place-items-center rounded-full bg-gold px-1 font-mono text-[10px] font-medium text-ink">
                  {item.count}
                </span>
              )}
            </span>
            {item.label}
          </Comp>
        );
      })}
    </nav>
  );
}
