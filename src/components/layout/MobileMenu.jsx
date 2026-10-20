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

/** เมนูเต็มจอสำหรับ Mobile/Tablet — ลิงก์เข้ามาแบบ stagger */
export default function MobileMenu({ open, onClose }) {
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
      className={cn(
        'mobile-navigation fixed inset-0 z-[60] flex flex-col bg-ink transition-[opacity,visibility] duration-500 ease-premium lg:hidden',
        open ? 'visible opacity-100' : 'invisible opacity-0',
      )}
    >
      <div className="container-x flex h-16 items-center justify-between">
        <Logo />
        <IconButton label={t('nav.closeMenu')} onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </div>

      <nav aria-label={t('nav.main')} className="container-x flex min-h-0 flex-1 flex-col justify-center gap-1 overflow-y-auto">
        {NAV_LINKS.map((link, i) => (
          <AppLink
            key={link.label}
            href={link.href}
            aria-current={(link.exact ? pathname === link.href : pathname === link.href || pathname.startsWith(`${link.href}/`)) ? 'page' : undefined}
            onClick={onClose}
            tabIndex={open ? 0 : -1}
            style={{ transitionDelay: open ? `${120 + i * 70}ms` : '0ms' }}
            className={cn(
              'py-2 font-sans text-4xl font-medium transition duration-700 ease-premium hover:text-gold',
              open ? 'translate-y-0 opacity-100' : 'translate-y-6 opacity-0',
            )}
          >
            {link.label}
          </AppLink>
        ))}
      </nav>

      <p className="container-x pb-10 text-sm text-mute">{t('footer.dataNote')}</p>
    </div>
  );
}
