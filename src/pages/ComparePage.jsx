import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import CompareEmpty from '@/components/compare/CompareEmpty';
import CompareTable from '@/components/compare/CompareTable';
import CompareVerdicts from '@/components/compare/CompareVerdicts';
import { analyseRows } from '@/components/compare/compareRows';
import GuitarPicker from '@/components/compare/GuitarPicker';
import AppLink from '@/components/ui/AppLink';
import { PlusIcon } from '@/components/ui/Icons';
import Switch from '@/components/ui/Switch';
import { GUITARS_BY_ID } from '@/data/guitars';
import { MAX_COMPARE, useShop } from '@/context/ShopContext';

export default function ComparePage() {
  const { compare, removeCompare, clearCompare, setCompareIds, notify } = useShop();
  const [params, setParams] = useSearchParams();
  const [diffOnly, setDiffOnly] = useState(false);
  const [pickerOpen, setPickerOpen] = useState(false);

  useEffect(() => {
    document.title = 'Compare guitars — Fretline';
  }, []);

  // เปิดลิงก์แชร์ /compare?ids=a,b,c → โหลดรายการเข้า compare แล้วเอา param ออกจาก URL
  useEffect(() => {
    const ids = params.get('ids');
    if (ids === null) return;
    const valid = ids.split(',').filter((id) => GUITARS_BY_ID[id]);
    if (valid.length) setCompareIds(valid);
    setParams({}, { replace: true });
  }, [params, setParams, setCompareIds]);

  const selected = useMemo(() => compare.map((id) => GUITARS_BY_ID[id]).filter(Boolean), [compare]);
  const ready = selected.length >= 2;
  const diffCount = useMemo(() => (ready ? analyseRows(selected).filter((r) => r.diff).length : 0), [ready, selected]);
  const totalRows = useMemo(() => (ready ? analyseRows(selected).length : 0), [ready, selected]);

  const share = async () => {
    const url = `${window.location.origin}/compare?ids=${selected.map((g) => g.id).join(',')}`;
    try {
      await navigator.clipboard.writeText(url);
      notify('Comparison link copied');
    } catch {
      notify('Could not copy the link');
    }
  };

  return (
    <>
      <header className="relative isolate border-b border-line pb-12 pt-28 md:pb-16 md:pt-36">
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(50%_80%_at_80%_0%,#262626_0%,#0A0A0A_70%)]" />
        <div className="container-x">
          <nav aria-label="Breadcrumb" className="mb-6 flex items-center gap-2 text-sm text-mute">
            <AppLink href="/" className="transition-colors hover:text-bone">Home</AppLink>
            <span aria-hidden="true">/</span>
            <span className="text-bone/80">Compare</span>
          </nav>
          <h1 className="font-serif text-5xl leading-[0.98] tracking-tight md:text-7xl">Compare guitars</h1>
          <p className="mt-5 max-w-lg text-base leading-relaxed text-mute md:text-lg">
            Put two to four guitars side by side. Rows that differ are highlighted, and the best value in each row is marked.
          </p>
        </div>
      </header>

      <section className="container-x pb-24 pt-8 md:pt-10">
        {!ready ? (
          <CompareEmpty selected={selected} onAdd={() => setPickerOpen(true)} />
        ) : (
          <>
            {/* แถบเครื่องมือ */}
            <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <p className="text-sm text-mute" aria-live="polite">
                <span className="font-mono text-bone">{selected.length}</span> guitars selected.{' '}
                <span className="font-mono text-bone">{diffCount}</span> of {totalRows} specs differ.
              </p>
              <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
                <Switch checked={diffOnly} onChange={setDiffOnly} label="Show differences only" />
                <button
                  type="button"
                  onClick={() => setPickerOpen(true)}
                  disabled={selected.length >= MAX_COMPARE}
                  className="inline-flex h-11 items-center gap-2 rounded-full border border-white/20 px-5 text-sm transition hover:border-gold hover:text-gold disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:border-white/20 disabled:hover:text-bone"
                >
                  <PlusIcon size={16} />
                  {selected.length >= MAX_COMPARE ? 'Maximum 4' : 'Add guitar'}
                </button>
                <button type="button" onClick={share} className="min-h-[44px] px-2 text-sm text-bone/80 transition-colors hover:text-gold">
                  Copy link
                </button>
                <button type="button" onClick={clearCompare} className="min-h-[44px] px-2 text-sm text-bone/80 transition-colors hover:text-gold">
                  Clear all
                </button>
              </div>
            </div>

            <CompareVerdicts guitars={selected} />

            <CompareTable guitars={selected} diffOnly={diffOnly} onRemove={removeCompare} grouped stickyNames />

            <p className="mt-8 text-xs text-mute">
              <span className="mr-2 inline-block h-1.5 w-1.5 -translate-y-px rounded-full bg-gold align-middle" />
              marks the best value in a row. Highlighted rows differ between the guitars you picked. Ratings are sample data.
            </p>
          </>
        )}
      </section>

      <GuitarPicker open={pickerOpen} onClose={() => setPickerOpen(false)} />
    </>
  );
}
