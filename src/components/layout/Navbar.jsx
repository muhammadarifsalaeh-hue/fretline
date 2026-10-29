import { useCallback, useEffect, useRef, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { NAV_LINKS } from '@/data/navigation';
import { useShop } from '@/context/ShopContext';
import { useAdminAccess } from '@/context/AdminAccessContext';
import useScrolled from '@/hooks/useScrolled';
import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import useSearchNavigation from '@/hooks/useSearchNavigation';
import { ChevronDownIcon, CompareIcon, HeartIcon, MenuIcon, SearchIcon } from '@/components/ui/Icons';
import AppLink from '@/components/ui/AppLink';
import IconButton from './IconButton';
import Logo from './Logo';
import MegaMenu from './MegaMenu';
import MobileMenu from './MobileMenu';

/** โปร่งใสบน Hero → พื้นดำ blur เมื่อ scroll | เมนูของหน้าปัจจุบันมีเส้นใต้สีทอง */
export default function Navbar() {
  const handleSearch = useSearchNavigation();
  const scrolled = useScrolled(24);
  const { wishlist, compare } = useShop();
  const isAdmin = useAdminAccess();
  const links = isAdmin ? [...NAV_LINKS, { label: 'Admin Studio', href: '/admin' }] : NAV_LINKS;
  const { pathname } = useLocation();
  const [mega, setMega] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const headerRef = useRef(null);
  const megaToggleRef = useRef(null);
  const closeMobile = useCallback(() => setMobileOpen(false), []);
  const solid = scrolled || mega || pathname !== '/';
  const isActive = (link) => (link.exact ? pathname === link.href : pathname === link.href || pathname.startsWith(`${link.href}/`));

  useEffect(() => { setMega(false); setMobileOpen(false); }, [pathname]);
  useEffect(() => {
    const desktop = window.matchMedia('(min-width: 1024px)');
    const closeOnBreakpoint = () => {
      if (desktop.matches) setMobileOpen(false);
      else setMega(false);
    };
    desktop.addEventListener('change', closeOnBreakpoint);
    return () => desktop.removeEventListener('change', closeOnBreakpoint);
  }, []);
  useEffect(() => {
    if (!mega) return undefined;
    const closeOutside = (event) => {
      if (!headerRef.current?.contains(event.target)) setMega(false);
    };
    document.addEventListener('pointerdown', closeOutside);
    return () => document.removeEventListener('pointerdown', closeOutside);
  }, [mega]);

  const openMegaWithKeyboard = (event) => {
    if (event.key !== 'ArrowDown') return;
    event.preventDefault();
    setMega(true);
    window.requestAnimationFrame(() => document.querySelector('#guitar-navigation a')?.focus());
  };

  return (
    <>
      <header
        ref={headerRef}
        onPointerLeave={(event) => { if (event.pointerType === 'mouse') setMega(false); }}
        onBlur={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) setMega(false); }}
        onKeyDown={(event) => {
          if (event.key === 'Escape' && mega) {
            event.preventDefault();
            setMega(false);
            megaToggleRef.current?.focus();
          }
        }}
        style={{ zIndex: 'var(--fl-layer-navigation, 50)' }}
        className={cn(
          'site-header fixed inset-x-0 top-0 border-b transition-[background-color,border-color,backdrop-filter] duration-300 ease-premium motion-reduce:transition-none',
          isAdmin && 'site-header--admin',
          solid ? 'border-line bg-ink/80 backdrop-blur-xl' : 'border-transparent bg-transparent',
        )}
      >
        <div className="site-header-inner container-x flex h-16 items-center justify-between lg:h-20" style={{ height: 'var(--fl-header-height, 64px)' }}>
          <Logo />

          <nav aria-label={t('nav.main')} className="site-nav hidden items-center gap-5 lg:flex">
            {links.map((link) => (
              <div key={link.href} className="site-nav-item flex items-center gap-0.5">
                <AppLink href={link.href} className="nav-link nav-link-content inline-flex min-h-11 items-center"
                  aria-current={isActive(link) ? 'page' : undefined}
                  onPointerEnter={(event) => { if (event.pointerType === 'mouse') setMega(Boolean(link.mega)); }}
                  onFocus={() => setMega(Boolean(link.mega))}
                  onKeyDown={link.mega ? openMegaWithKeyboard : undefined}>
                  {link.label}
                </AppLink>
                {link.mega && <button ref={megaToggleRef} type="button"
                  aria-label={`${t('nav.menu')}: ${link.label}`} aria-expanded={mega} aria-controls="guitar-navigation"
                  onClick={() => setMega((value) => !value)} onKeyDown={openMegaWithKeyboard}
                  className="nav-disclosure inline-flex h-11 w-11 items-center justify-center rounded-lg text-mute transition-colors hover:text-gold">
                  <ChevronDownIcon size={16} className={cn('transition-transform duration-200 motion-reduce:transition-none', mega && 'rotate-180')} />
                </button>}
              </div>
            ))}
          </nav>

          <div className="site-header-actions flex items-center gap-1">
            <IconButton label={t('nav.search')} onClick={handleSearch} className="hidden lg:inline-flex">
              <SearchIcon size={20} />
            </IconButton>
            <IconButton label={t('nav.wishlistAria', { n: wishlist.length })} href="/wishlist" badge={wishlist.length}>
              <HeartIcon size={20} />
            </IconButton>
            <IconButton label={t('nav.compareAria', { n: compare.length })} href="/compare" badge={compare.length} className="hidden sm:inline-flex">
              <CompareIcon size={20} />
            </IconButton>
            <IconButton aria-expanded={mobileOpen} aria-controls="mobile-navigation" label={t('nav.openMenu')} onClick={() => setMobileOpen(true)} className="lg:hidden">
              <MenuIcon size={20} />
            </IconButton>
          </div>
        </div>

        <MegaMenu open={mega} onClose={() => setMega(false)} />
      </header>

      <MobileMenu open={mobileOpen} onClose={closeMobile} isAdmin={isAdmin} />
    </>
  );
}
