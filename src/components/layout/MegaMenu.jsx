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
      aria-hidden={!open}
      className={cn(
        'absolute inset-x-0 top-full hidden border-b border-line bg-ink/95 backdrop-blur-xl transition-[opacity,transform,visibility] duration-500 ease-premium lg:block',
        open ? 'visible translate-y-0 opacity-100' : 'invisible -translate-y-2 opacity-0',
      )}
    >
      <div className="container-x grid grid-cols-12 gap-10 py-10">
        <div className="col-span-3">
          <p className="mb-4 text-xs text-mute">{t('mega.byType')}</p>
          <ul className="space-y-1">
            {CATEGORIES.map((c) => (
              <li key={c.id}>
                <AppLink
                  href={categoryUrl(c.id)}
                  onClick={onClose}
                  tabIndex={open ? 0 : -1}
                  className="flex items-baseline justify-between py-2 font-sans text-2xl font-medium transition-colors hover:text-gold"
                >
                  {c.name}
                  <span className="font-mono text-xs text-mute">{c.count}</span>
                </AppLink>
              </li>
            ))}
          </ul>
        </div>

        <div className="col-span-6 grid grid-cols-2 gap-5">
          {featured.map((g) => (
            <AppLink key={g.id} href={guitarUrl(g.slug)} onClick={onClose} tabIndex={open ? 0 : -1} className="group block">
              <GuitarImage guitar={g} className="aspect-[4/3] rounded-2xl" imgClassName="group-hover:scale-105" />
              <p className="mt-3 text-xs text-mute">{g.brand}</p>
              <p className="font-serif text-xl leading-tight">{g.name}</p>
              <p className="mt-1 font-mono text-sm text-gold">{formatPrice(g.price)}</p>
            </AppLink>
          ))}
        </div>

        <div className="col-span-3">
          <p className="mb-4 text-xs text-mute">{t('mega.byBudget')}</p>
          <ul className="space-y-1">
            {BUDGET_LINKS.map((l) => (
              <li key={l.label}>
                <AppLink
                  href={l.href}
                  onClick={onClose}
                  tabIndex={open ? 0 : -1}
                  className="block py-2 text-sm text-bone/80 transition-colors hover:text-gold"
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
