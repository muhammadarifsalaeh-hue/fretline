import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import AppLink from '@/components/ui/AppLink';

export default function Logo({ className = '' }) {
  return (
    <AppLink
      href="/"
      onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      aria-label={t('nav.homeAria')}
      className={cn('inline-flex items-baseline font-serif text-[1.75rem] leading-none tracking-tight', className)}
    >
      Fretline<span className="ml-0.5 text-gold">.</span>
    </AppLink>
  );
}
