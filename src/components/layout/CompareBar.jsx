import { useLocation } from 'react-router-dom';
import { GUITARS_BY_ID } from '@/data/guitars';
import { MAX_COMPARE, useShop } from '@/context/ShopContext';
import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import { CloseIcon, PlusIcon } from '@/components/ui/Icons';
import AppLink from '@/components/ui/AppLink';
import GuitarImage from '@/components/guitar/GuitarImage';

/** แถบเปรียบเทียบลอยด้านล่าง — โผล่เมื่อเลือกกีตาร์อย่างน้อย 1 ตัว */
export default function CompareBar() {
  const { compare, removeCompare } = useShop();
  const { pathname } = useLocation();
  if (pathname === '/compare' || pathname === '/find-my-guitar') return null;
  const items = compare.map((id) => GUITARS_BY_ID[id]).filter(Boolean);
  const visible = items.length > 0;
  const ready = items.length >= 2;
  const slots = Array.from({ length: MAX_COMPARE }, (_, i) => items[i] ?? null);

  return (
    <div
      aria-hidden={!visible}
      className={cn(
        'fixed inset-x-0 bottom-[calc(68px+env(safe-area-inset-bottom))] z-40 px-3 transition duration-500 ease-premium lg:bottom-6',
        visible ? 'translate-y-0 opacity-100' : 'pointer-events-none translate-y-[140%] opacity-0',
      )}
    >
      <div className="mx-auto flex max-w-3xl items-center gap-3 rounded-3xl border border-white/10 bg-ink/85 p-2.5 pl-4 shadow-[0_20px_60px_-10px_rgba(0,0,0,0.8)] backdrop-blur-xl">
        <p className="hidden text-sm text-mute sm:block">{t('cmpbar.title')}</p>

        <ul className="flex flex-1 items-center gap-2">
          {slots.map((g, i) =>
            g ? (
              <li key={g.id} className="group relative h-12 w-12 overflow-hidden rounded-xl ring-1 ring-white/15">
                <GuitarImage guitar={g} size="sm" className="h-full w-full" />
                <button
                  type="button"
                  onClick={() => removeCompare(g.id)}
                  tabIndex={visible ? 0 : -1}
                  aria-label={t('cmp.removeAria', { name: g.name })}
                  className="absolute inset-0 grid place-items-center bg-ink/70 opacity-0 transition-opacity focus-visible:opacity-100 group-hover:opacity-100 [@media(hover:none)]:opacity-100 [@media(hover:none)]:bg-ink/40"
                >
                  <CloseIcon size={16} />
                </button>
              </li>
            ) : (
              <li key={`empty-${i}`} className="grid h-12 w-12 place-items-center rounded-xl border border-dashed border-white/20 text-mute">
                <PlusIcon size={16} />
              </li>
            ),
          )}
        </ul>

        <AppLink
          href="/compare"
          tabIndex={visible ? 0 : -1}
          aria-disabled={!ready}
          className={cn(
            'inline-flex h-12 items-center rounded-full bg-gold px-6 text-sm font-medium text-ink transition duration-300 hover:bg-gold-soft',
            !ready && 'pointer-events-none opacity-40',
          )}
        >
          {t('cmpbar.button', { n: items.length })}
        </AppLink>
      </div>
    </div>
  );
}
