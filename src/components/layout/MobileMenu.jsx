import { useEffect, useRef } from 'react';
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
  useEffect(() => {
    if (!open) return undefined;
    const previousFocus = document.activeElement;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const dialog = dialogRef.current;
    const focusable = () => [...dialog.querySelectorAll('a[href], button:not([disabled])')]
      .filter((el) => el.tabIndex >= 0);
    focusable()[0]?.focus();
    const onKey = (e) => {
      if (e.key === 'Escape') onClose();
      if (e.key !== 'Tab') return;
      const elements = focusable();
      const first = elements[0];
      const last = elements[elements.length - 1];
      if (e.shiftKey && (document.activeElement === first || !dialog.contains(document.activeElement))) {
        e.preventDefault(); last?.focus();
      } else if (!e.shiftKey && (document.activeElement === last || !dialog.contains(document.activeElement))) {
        e.preventDefault(); first?.focus();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', onKey);
      previousFocus?.focus({ preventScroll: true });
    };
  }, [open, onClose]);

  return (
    <div
      ref={dialogRef}
      id="mobile-navigation"
      role="dialog"
      aria-modal="true"
      aria-label={t('nav.menu')}
      aria-hidden={!open}
      className={cn(
        'fixed inset-0 z-[60] flex flex-col bg-ink transition-[opacity,visibility] duration-500 ease-premium lg:hidden',
        open ? 'visible opacity-100' : 'invisible opacity-0',
      )}
    >
      <div className="container-x flex h-16 items-center justify-between">
        <Logo />
        <IconButton label={t('nav.closeMenu')} onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </div>

      <nav className="container-x flex flex-1 flex-col justify-center gap-1">
        {NAV_LINKS.map((link, i) => (
          <AppLink
            key={link.label}
            href={link.href}
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
