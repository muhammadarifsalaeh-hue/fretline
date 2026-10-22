import { useLocation } from 'react-router-dom';
import { SAVED_GUITARS_BY_ID } from '@/data/guitars';
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
  const items = compare.map((id) => SAVED_GUITARS_BY_ID[id]).filter(Boolean);
  const visible = items.length > 0;
  const ready = items.length >= 2;
  const slots = Array.from({ length: MAX_COMPARE }, (_, i) => items[i] ?? null);

  return (
    <div
      aria-hidden={!visible}
      inert={!visible ? '' : undefined}
      style={{ zIndex: 'var(--fl-layer-tray, 40)' }}
      className={cn(
        'compare-tray-positioner fixed inset-x-0 bottom-[calc(68px+env(safe-area-inset-bottom))] px-3 transition-[opacity,transform] duration-[240ms] ease-premium motion-reduce:transition-none lg:bottom-6',
        visible ? 'translate-y-0 opacity-100' : 'pointer-events-none translate-y-[140%] opacity-0',
      )}
    >
      <div className="compare-tray mx-auto flex max-w-3xl items-center gap-3 rounded-xl border border-line bg-ink/95 p-2.5 pl-4 shadow-[0_12px_32px_rgba(0,0,0,0.28)] backdrop-blur-xl">
        <p className="hidden text-sm text-mute sm:block">{t('cmpbar.title')}</p>

        <ul aria-label={t('cmpbar.title')} className="flex min-w-0 flex-1 items-center gap-2 overflow-x-auto">
          {slots.map((g, i) =>
            g ? (
              <li key={g.id} className="group relative h-12 w-12 shrink-0 overflow-hidden rounded-lg ring-1 ring-line">
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
              <li key={`empty-${i}`} className="grid h-12 w-12 shrink-0 place-items-center rounded-lg border border-dashed border-line text-mute">
                <PlusIcon size={16} />
              </li>
            ),
          )}
        </ul>

        <AppLink
          href="/compare"
          tabIndex={visible && ready ? 0 : -1}
          aria-disabled={!ready}
          onClick={(event) => { if (!ready) event.preventDefault(); }}
          className={cn(
            'site-tray-action inline-flex h-12 shrink-0 items-center justify-center rounded-lg bg-gold px-5 text-sm font-medium leading-normal text-ink transition-colors duration-200 hover:bg-gold-soft motion-reduce:transition-none',
            !ready && 'pointer-events-none opacity-40',
          )}
        >
          {t('cmpbar.button', { n: items.length })}
        </AppLink>
      </div>
    </div>
  );
}
