import { useDeferredValue, useEffect, useId, useMemo, useRef, useState } from 'react';
import { t } from '@/i18n';
import { GUITARS } from '@/data/guitars';
import { MAX_COMPARE, useShop } from '@/context/ShopContext';
import useDialogFocus from '@/hooks/useDialogFocus';
import { cn } from '@/utils/cn';
import { publicPrice } from '@/utils/dataTrust';
import { matchesQuery } from '@/utils/search';
import { CheckIcon, CloseIcon, PlusIcon, SearchIcon } from '@/components/ui/Icons';
import GuitarImage from '@/components/guitar/GuitarImage';

export default function GuitarPicker({ open, onClose, onSelectionChange }) {
  const { compare, toggleCompare } = useShop();
  const [query, setQuery] = useState('');
  const dialogRef = useRef(null);
  const searchRef = useRef(null);
  const statusId = useId();
  useDialogFocus(dialogRef, open, onClose);
  useEffect(() => {
    if (open) { setQuery(''); searchRef.current?.focus({ preventScroll: true }); }
  }, [open]);
  const full = compare.length >= MAX_COMPARE;
  const deferredQuery = useDeferredValue(query);
  const list = useMemo(() => GUITARS.filter((guitar) => matchesQuery(guitar, deferredQuery)), [deferredQuery]);
  const toggle = (guitar) => {
    const selected = compare.includes(guitar.id);
    if (!selected && full) return;
    if (onSelectionChange) onSelectionChange(selected ? compare.filter((id) => id !== guitar.id) : [...compare, guitar.id]);
    else toggleCompare(guitar);
  };
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-[70] flex items-end bg-black/75 p-0 sm:items-center sm:justify-center sm:p-5" onClick={onClose}>
      <div ref={dialogRef} role="dialog" aria-modal="true" aria-label={t('p4.compare.add')} aria-describedby={statusId} onClick={(event) => event.stopPropagation()}
        className="guitar-picker-modal">
        <div className="flex items-center justify-between gap-4 p-5 pb-3">
          <h2 className="text-xl font-medium">{t('p4.compare.add')}</h2>
          <button type="button" onClick={onClose} aria-label={t('p4.close')} className="grid h-11 w-11 place-items-center rounded-full hover:bg-white/5"><CloseIcon /></button>
        </div>
        <div className="px-5 pb-4">
          <label className="relative block"><span className="sr-only">{t('p4.compare.search')}</span><SearchIcon className="pointer-events-none absolute left-3 top-3 text-mute" />
            <input ref={searchRef} type="search" inputMode="search" autoComplete="off" value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t('toolbar.placeholder')} className="h-11 w-full rounded-lg border border-line bg-ink pl-11 pr-3 text-sm" />
          </label>
          <p id={statusId} className="mt-2 text-xs text-gold" role="status" aria-atomic="true">{t(full ? 'p4.compare.fullNote' : 'p4.compare.count', { n: compare.length, max: MAX_COMPARE })}</p>
          <p className="mt-1 text-xs text-mute" role="status" aria-atomic="true">{t('p5.detail.count', { n: list.length, total: GUITARS.length })}</p>
        </div>
        <ul aria-label={t('catalog.resultsAria')} aria-busy={query !== deferredQuery} className="min-h-0 flex-1 overflow-y-auto px-3 pb-3">
          {!list.length && <li className="px-4 py-10 text-center text-sm text-mute">{t('p4.compare.noModels')}</li>}
          {list.map((guitar) => {
            const added = compare.includes(guitar.id);
            return <li key={guitar.id}><button type="button" disabled={full && !added} onClick={() => toggle(guitar)} aria-pressed={added}
              className="picker-model-row">
              <GuitarImage guitar={guitar} size="sm" alt="" className="h-16 w-16 shrink-0 rounded-lg" />
              <span className="min-w-0 flex-1"><span className="block text-[10px] text-mute">{guitar.brand}</span><span className="block font-serif text-xl">{guitar.name}</span>
                <span className="block text-xs text-gold">{publicPrice(guitar)}</span><span className="block text-[10px] text-mute">{t(`status.${guitar.dataStatus ?? 'sample'}`)}</span></span>
              <span className={cn('grid h-9 w-9 shrink-0 place-items-center rounded-full border', added ? 'border-gold text-gold' : 'border-line text-mute')}>{added ? <CheckIcon size={16} /> : <PlusIcon size={16} />}</span>
            </button></li>;
          })}
        </ul>
        <div className="flex items-center justify-between gap-3 border-t border-line p-4 pb-[calc(1rem+env(safe-area-inset-bottom))]"><span className="text-xs text-mute">{t('p4.compare.count', { n: compare.length, max: MAX_COMPARE })}</span><button type="button" onClick={onClose} className="phase4-button is-gold">{t('p4.done')}</button></div>
      </div>
    </div>
  );
}
