import { useEffect, useRef, useState } from 'react';
import { GUITARS } from '@/data/guitars';
import { MAX_COMPARE, useShop } from '@/context/ShopContext';
import { cn } from '@/utils/cn';
import { formatPrice } from '@/utils/format';
import { matchesQuery } from '@/utils/search';
import { CheckIcon, CloseIcon, PlusIcon, SearchIcon } from '@/components/ui/Icons';
import GuitarImage from '@/components/guitar/GuitarImage';

/** หน้าต่างเลือกกีตาร์เพิ่มเข้าเปรียบเทียบ (มือถือ = bottom sheet, Desktop = modal กลางจอ) */
export default function GuitarPicker({ open, onClose }) {
  const { compare, toggleCompare } = useShop();
  const [query, setQuery] = useState('');
  const inputRef = useRef(null);
  const full = compare.length >= MAX_COMPARE;
  const list = GUITARS.filter((g) => matchesQuery(g, query));

  useEffect(() => {
    if (!open) return undefined;
    setQuery('');
    document.body.style.overflow = 'hidden';
    const focusTimer = window.setTimeout(() => inputRef.current?.focus(), 350);
    const onKey = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = '';
      window.clearTimeout(focusTimer);
      window.removeEventListener('keydown', onKey);
    };
  }, [open, onClose]);

  return (
    <div aria-hidden={!open} className={cn('fixed inset-0 z-[70] flex items-end transition-[visibility] md:items-center md:justify-center', open ? 'visible' : 'invisible delay-500')}>
      <div onClick={onClose} className={cn('absolute inset-0 bg-black/70 transition-opacity duration-500', open ? 'opacity-100' : 'opacity-0')} />
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Add guitars to compare"
        className={cn(
          'relative flex max-h-[85svh] w-full flex-col rounded-t-3xl border border-line bg-surface transition duration-500 ease-premium md:max-w-[640px] md:rounded-3xl',
          open ? 'translate-y-0 opacity-100' : 'translate-y-full md:translate-y-6 md:opacity-0',
        )}
      >
        <div className="flex items-center justify-between px-5 pb-3 pt-5 md:px-7">
          <h2 className="font-serif text-3xl">Add guitars</h2>
          <button type="button" onClick={onClose} aria-label="Close" className="grid h-11 w-11 place-items-center rounded-full hover:bg-white/10">
            <CloseIcon />
          </button>
        </div>

        <div className="px-5 pb-3 md:px-7">
          <div className="relative">
            <SearchIcon className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-mute" />
            <label htmlFor="picker-search" className="sr-only">Search guitars</label>
            <input
              ref={inputRef}
              id="picker-search"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by model or brand…"
              className="h-12 w-full rounded-full border border-line bg-ink pl-12 pr-5 text-[15px] placeholder:text-mute focus:border-gold focus:outline-none"
            />
          </div>
        </div>

        <ul className="flex-1 overflow-y-auto px-3 pb-2 md:px-5">
          {list.length === 0 && <li className="px-4 py-10 text-center text-sm text-mute">No guitars match “{query.trim()}”.</li>}
          {list.map((g) => {
            const added = compare.includes(g.id);
            const disabled = full && !added;
            return (
              <li key={g.id}>
                <button
                  type="button"
                  disabled={disabled}
                  onClick={() => toggleCompare(g)}
                  aria-pressed={added}
                  className={cn(
                    'flex w-full items-center gap-4 rounded-2xl px-3 py-3 text-left transition-colors',
                    disabled ? 'cursor-not-allowed opacity-40' : 'hover:bg-white/5',
                  )}
                >
                  <GuitarImage guitar={g} size="sm" alt="" className="h-16 w-16 shrink-0 rounded-xl" />
                  <span className="min-w-0 flex-1">
                    <span className="block text-xs text-mute">{g.brand}</span>
                    <span className="block truncate font-serif text-xl leading-tight">{g.name}</span>
                    <span className="block font-mono text-sm text-gold">{formatPrice(g.price)}</span>
                  </span>
                  <span
                    className={cn(
                      'inline-flex h-10 shrink-0 items-center gap-1.5 rounded-full border px-4 text-sm',
                      added ? 'border-gold bg-gold/10 text-gold' : 'border-white/20 text-bone',
                    )}
                  >
                    {added ? <CheckIcon size={16} /> : <PlusIcon size={16} />}
                    {added ? 'Added' : 'Add'}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>

        <div className="flex items-center justify-between gap-4 border-t border-line p-4 pb-[calc(1rem+env(safe-area-inset-bottom))] md:px-7">
          <p className="font-mono text-sm text-mute">
            {compare.length} of {MAX_COMPARE} selected
          </p>
          <button type="button" onClick={onClose} className="h-12 rounded-full bg-gold px-8 text-sm font-medium text-ink transition hover:bg-gold-soft">
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
