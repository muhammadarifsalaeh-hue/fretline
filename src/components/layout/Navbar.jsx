import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { NAV_LINKS } from '@/data/navigation';
import { useShop } from '@/context/ShopContext';
import useScrolled from '@/hooks/useScrolled';
import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import { focusSearch } from '@/utils/dom';
import { CompareIcon, HeartIcon, MenuIcon, SearchIcon } from '@/components/ui/Icons';
import AppLink from '@/components/ui/AppLink';
import IconButton from './IconButton';
import Logo from './Logo';
import MegaMenu from './MegaMenu';
import MobileMenu from './MobileMenu';

/** โปร่งใสบน Hero → พื้นดำ blur เมื่อ scroll | เมนูของหน้าปัจจุบันมีเส้นใต้สีทอง */
export default function Navbar() {
  const scrolled = useScrolled(24);
  const { wishlist, compare } = useShop();
  const { pathname } = useLocation();
  const [mega, setMega] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const solid = scrolled || mega;
  const isActive = (link) => (link.exact ? pathname === link.href : pathname === link.href || pathname.startsWith(`${link.href}/`));

  return (
    <>
      <header
        onMouseLeave={() => setMega(false)}
        className={cn(
          'fixed inset-x-0 top-0 z-50 border-b transition-[background-color,border-color,backdrop-filter] duration-500 ease-premium',
          solid ? 'border-line bg-ink/80 backdrop-blur-xl' : 'border-transparent bg-transparent',
        )}
      >
        <div className="container-x flex h-16 items-center justify-between lg:h-20">
          <Logo />

          <nav aria-label={t('nav.main')} className="hidden items-center gap-9 lg:flex">
            {NAV_LINKS.map((link) => (
              <AppLink
                key={link.href}
                href={link.href}
                className="nav-link"
                aria-current={isActive(link) ? 'page' : undefined}
                onMouseEnter={() => setMega(Boolean(link.mega))}
                onFocus={() => setMega(Boolean(link.mega))}
              >
                {link.label}
              </AppLink>
            ))}
          </nav>

          <div className="flex items-center gap-1">
            <IconButton label={t('nav.search')} onClick={focusSearch} className="hidden lg:inline-flex">
              <SearchIcon />
            </IconButton>
            <IconButton label={t('nav.wishlistAria', { n: wishlist.length })} href="/wishlist" badge={wishlist.length}>
              <HeartIcon />
            </IconButton>
            <IconButton label={t('nav.compareAria', { n: compare.length })} href="/compare" badge={compare.length} className="hidden sm:inline-flex">
              <CompareIcon />
            </IconButton>
            <IconButton label={t('nav.openMenu')} onClick={() => setMobileOpen(true)} className="lg:hidden">
              <MenuIcon />
            </IconButton>
          </div>
        </div>

        <MegaMenu open={mega} onClose={() => setMega(false)} />
      </header>

      <MobileMenu open={mobileOpen} onClose={() => setMobileOpen(false)} />
    </>
  );
}
