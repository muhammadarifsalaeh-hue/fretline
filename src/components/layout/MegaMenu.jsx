import { CATEGORIES } from '@/data/categories';
import { GUITARS } from '@/data/guitars';
import { BUDGET_LINKS } from '@/data/navigation';
import { formatPrice } from '@/utils/format';
import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import { categoryUrl, guitarUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import GuitarImage from '@/components/guitar/GuitarImage';

/** Mega menu ของ "Guitars" — แสดงเฉพาะ Desktop */
export default function MegaMenu({ open, onClose }) {
  const featured = GUITARS.filter((g) => g.featured).slice(0, 2);

  return (
    <div
      id="guitar-navigation"
      aria-hidden={!open}
      inert={!open ? '' : undefined}
      className={cn(
        'site-mega-menu absolute inset-x-0 top-full hidden border-b border-line bg-ink/95 backdrop-blur-xl transition-[opacity,transform,visibility] duration-[240ms] ease-premium motion-reduce:transform-none motion-reduce:transition-none lg:block',
        open ? 'visible translate-y-0 opacity-100' : 'invisible -translate-y-2 opacity-0',
      )}
    >
      <div className="container-x grid grid-cols-12 gap-10 py-10">
        <div className="col-span-3">
          <p className="site-mega-heading mb-4 text-[13px] text-mute">{t('mega.byType')}</p>
          <ul className="space-y-1">
            {CATEGORIES.map((c) => (
              <li key={c.id}>
                <AppLink
                  href={categoryUrl(c.id)}
                  onClick={onClose}
                  tabIndex={open ? 0 : -1}
                  className="site-mega-category flex min-h-11 items-center justify-between gap-3 py-2 font-sans text-xl font-medium transition-colors hover:text-gold"
                >
                  {c.name}
                  <span className="shrink-0 text-[13px] tabular-nums text-mute">{c.count}</span>
                </AppLink>
              </li>
            ))}
          </ul>
        </div>

        <div className="col-span-6 grid grid-cols-2 gap-5">
          {featured.map((g) => (
            <AppLink key={g.id} href={guitarUrl(g.slug)} onClick={onClose} tabIndex={open ? 0 : -1} className="group block">
              <GuitarImage guitar={g} className="aspect-square rounded-xl" />
              <p className="mt-3 text-[13px] text-mute">{g.brand}</p>
              <p lang="en" className="font-serif text-xl leading-snug">{g.name}</p>
              <p className="mt-1 font-mono text-sm text-gold">{formatPrice(g.price)}</p>
            </AppLink>
          ))}
        </div>

        <div className="col-span-3">
          <p className="site-mega-heading mb-4 text-[13px] text-mute">{t('mega.byBudget')}</p>
          <ul className="space-y-1">
            {BUDGET_LINKS.map((l) => (
              <li key={l.label}>
                <AppLink
                  href={l.href}
                  onClick={onClose}
                  tabIndex={open ? 0 : -1}
                  className="site-mega-budget inline-flex min-h-11 items-center py-2 text-sm text-bone transition-colors hover:text-gold"
                >
                  {l.label}
                </AppLink>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
