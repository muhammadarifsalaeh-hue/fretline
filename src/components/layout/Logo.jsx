import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import AppLink from '@/components/ui/AppLink';
import { scrollToTop } from '@/utils/dom';

export default function Logo({ className = '', onClick }) {
  return (
    <AppLink
      href="/"
      onClick={(event) => { onClick?.(event); scrollToTop(); }}
      aria-label={t('nav.homeAria')}
      className={cn('site-logo inline-flex min-h-11 shrink-0 items-center font-serif text-[2rem] leading-none tracking-tight', className)}
    >
      <span lang="en">Fretline</span><span aria-hidden="true" className="ml-0.5 text-gold">.</span>
    </AppLink>
  );
}
