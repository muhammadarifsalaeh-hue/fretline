import { useShop } from '@/context/ShopContext';
import { useLocation } from 'react-router-dom';
import { t } from '@/i18n';
import useSearchNavigation from '@/hooks/useSearchNavigation';
import { scrollToTop } from '@/utils/dom';
import AppLink from '@/components/ui/AppLink';
import { CompareIcon, HeartIcon, HomeIcon, SearchIcon } from '@/components/ui/Icons';

/** แถบเมนูล่างสำหรับมือถือ/แท็บเล็ต: Home / Search / Compare / Wishlist */
export default function BottomBar() {
  const handleSearch = useSearchNavigation();
  const { compare, wishlist } = useShop();
  const { pathname } = useLocation();

  const items = [
    { label: t('nav.home'), icon: <HomeIcon size={20} />, href: '/', onClick: () => scrollToTop() },
    { label: t('nav.search'), icon: <SearchIcon size={20} />, onClick: handleSearch },
    { label: t('nav.compare'), icon: <CompareIcon size={20} />, href: '/compare', count: compare.length },
    { label: t('nav.wishlist'), icon: <HeartIcon size={20} />, href: '/wishlist', count: wishlist.length },
  ];

  return (
    <nav
      aria-label={t('nav.quick')}
      style={{ zIndex: 'var(--fl-layer-navigation, 50)' }}
      className="site-bottom-nav fixed inset-x-0 bottom-0 grid grid-cols-4 border-t border-line bg-ink/90 pb-[env(safe-area-inset-bottom)] backdrop-blur-xl lg:hidden"
    >
      {items.map((item) => {
        const Comp = item.href ? AppLink : 'button';
        return (
          <Comp
            key={item.label}
            href={item.href}
            type={item.href ? undefined : 'button'}
            aria-current={item.href && (item.href === '/' ? pathname === '/' : pathname.startsWith(item.href)) ? 'page' : undefined}
            onClick={item.onClick}
            className="quick-nav-item relative flex min-h-[60px] flex-col items-center justify-center gap-1 text-[13px] text-mute transition-colors active:text-gold motion-reduce:transition-none"
          >
            <span className="quick-nav-icon relative inline-flex h-5 w-5 shrink-0 items-center justify-center">
              {item.icon}
              {item.count > 0 && (
                <span className="absolute -right-2.5 -top-1.5 grid h-[18px] min-w-[18px] place-items-center rounded-full bg-gold px-1 text-[11px] font-medium leading-none text-ink">
                  {item.count}
                </span>
              )}
            </span>
            <span className="quick-nav-label leading-normal">{item.label}</span>
          </Comp>
        );
      })}
    </nav>
  );
}
