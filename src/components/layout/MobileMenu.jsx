import { useRef } from 'react';
import { useLocation } from 'react-router-dom';
import useDialogFocus from '@/hooks/useDialogFocus';
import { NAV_LINKS } from '@/data/navigation';
import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import { CloseIcon } from '@/components/ui/Icons';
import AppLink from '@/components/ui/AppLink';
import IconButton from './IconButton';
import Logo from './Logo';

/** เมนูเต็มจอสำหรับ Mobile/Tablet พร้อม focus management */
export default function MobileMenu({ open, onClose, isAdmin = false }) {
  const dialogRef = useRef(null);
  const { pathname } = useLocation();
  useDialogFocus(dialogRef, open, onClose);

  return (
    <div
      ref={dialogRef}
      id="mobile-navigation"
      role="dialog"
      aria-modal="true"
      aria-label={t('nav.menu')}
      aria-hidden={!open}
      inert={!open ? '' : undefined}
      style={{ zIndex: 'var(--fl-layer-drawer, 60)' }}
      className={cn(
        'mobile-navigation fixed inset-0 flex flex-col bg-ink transition-[opacity,visibility] duration-[240ms] ease-premium motion-reduce:transition-none lg:hidden',
        open ? 'visible opacity-100' : 'invisible opacity-0',
      )}
    >
      <div className="mobile-navigation-header container-x flex h-16 shrink-0 items-center justify-between" style={{ height: 'var(--fl-header-height, 64px)' }}>
        <Logo onClick={onClose} />
        <IconButton label={t('nav.closeMenu')} onClick={onClose}>
          <CloseIcon size={20} />
        </IconButton>
      </div>

      <nav aria-label={t('nav.main')} className="container-x flex min-h-0 flex-1 flex-col justify-center gap-1 overflow-y-auto">
        {(isAdmin ? [...NAV_LINKS, { label: 'Admin Studio', href: '/admin' }] : NAV_LINKS).map((link) => (
          <AppLink
            key={link.label}
            href={link.href}
            aria-current={(link.exact ? pathname === link.href : pathname === link.href || pathname.startsWith(`${link.href}/`)) ? 'page' : undefined}
            onClick={onClose}
            tabIndex={open ? 0 : -1}
            className={cn(
              'mobile-navigation-link flex min-h-14 items-center py-2 font-sans text-[2rem] font-medium leading-normal transition-[color,opacity,transform] duration-[240ms] ease-premium hover:text-gold motion-reduce:transform-none motion-reduce:transition-none',
              open ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0',
            )}
          >
            {link.label}
          </AppLink>
        ))}
      </nav>

      <p className="mobile-navigation-footer container-x shrink-0 pb-8 pt-5 text-sm leading-7 text-mute">{t('footer.dataNote')}</p>
    </div>
  );
}
