import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { t } from '@/i18n';
import CompareEmpty from '@/components/compare/CompareEmpty';
import CompareTable from '@/components/compare/CompareTable';
import CompareVerdicts from '@/components/compare/CompareVerdicts';
import { analyseRows } from '@/components/compare/compareRows';
import GuitarPicker from '@/components/compare/GuitarPicker';
import AppLink from '@/components/ui/AppLink';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import ShareLink from '@/components/ui/ShareLink';
import { PlusIcon } from '@/components/ui/Icons';
import Switch from '@/components/ui/Switch';
import { GUITARS_BY_ID } from '@/data/guitars';
import { MAX_COMPARE, useShop } from '@/context/ShopContext';
import { normalizeGuitarIds } from '@/utils/selection';

export default function ComparePage() {
  const { compare, setCompareIds } = useShop();
  const [params, setParams] = useSearchParams();
  const [diffOnly, setDiffOnly] = useState(false);
  const [includeSamples, setIncludeSamples] = useState(false);
  const [pickerOpen, setPickerOpen] = useState(false);
  const addRef = useRef(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const closePicker = useCallback(() => setPickerOpen(false), []);
  const closeConfirm = useCallback(() => setConfirmOpen(false), []);

  useEffect(() => { document.title = t('p4.compare.docTitle'); }, []);
  const lastReadUrl = useRef(null);
  const selectionKey = compare.join(',');
  useEffect(() => {
    const signature = params.toString();
    const incoming = lastReadUrl.current !== signature;
    const shared = params.has('ids') ? normalizeGuitarIds(params.get('ids').split(','), MAX_COMPARE) : null;
    // Read browser history first. Changes from the global tray then update the current URL.
    if (incoming && shared && shared.join(',') !== selectionKey) {
      setCompareIds(shared);
      return;
    }
    // Mark as read only after context has caught up. Strict Mode may replay this effect.
    lastReadUrl.current = signature;
    const canonical = new URLSearchParams({ ids: selectionKey });
    if (signature !== canonical.toString()) setParams(canonical, { replace: true });
  }, [params, selectionKey, setCompareIds, setParams]);

  const changeSelection = (ids) => {
    const valid = normalizeGuitarIds(ids, MAX_COMPARE);
    setCompareIds(valid);
    setParams({ ids: valid.join(',') });
  };
  const selected = useMemo(() => compare.map((id) => GUITARS_BY_ID[id]).filter(Boolean), [compare]);
  const ready = selected.length >= 2;
  const rows = useMemo(() => analyseRows(selected, { includeSamples }), [selected, includeSamples]);
  const diffCount = rows.filter((row) => row.diff).length;
  const shareUrl = `${window.location.origin}/compare?ids=${compare.join(',')}`;

  return (
    <div className="comparison-page phase4-page">
      <header className="container-x phase4-heading">
        <nav aria-label={t('common.breadcrumb')} className="discovery-breadcrumb"><AppLink href="/">{t('nav.home')}</AppLink><span aria-hidden="true">›</span><span>{t('nav.compare')}</span></nav>
        <p className="discovery-kicker">FRETLINE / SIDE BY SIDE</p>
        <div className="phase4-title-row"><div><h1>{t('p4.compare.title')}</h1><p>{t('p4.compare.intro')}</p></div>
          <span className="compare-count" role="status">{t('p4.compare.count', { n: selected.length, max: MAX_COMPARE })}</span>
        </div>
      </header>
      <section className="container-x pb-16">
        <div className="compare-toolbar">
          <div className="flex flex-wrap items-center gap-3">
            <button type="button" ref={addRef} onClick={() => setPickerOpen(true)} disabled={compare.length >= MAX_COMPARE} className="phase4-button is-gold"><PlusIcon size={16} />{t(compare.length >= MAX_COMPARE ? 'p4.compare.full' : 'p4.compare.add')}</button>
            <ShareLink url={shareUrl} disabled={!selected.length} />
            <button type="button" disabled={!selected.length} onClick={() => setConfirmOpen(true)} className="phase4-button">{t('p4.compare.clear')}</button>
          </div>
          {ready && <div className="flex flex-wrap gap-5"><Switch checked={diffOnly} onChange={setDiffOnly} label={t('cmp.diffOnly')} /><Switch checked={includeSamples} onChange={setIncludeSamples} label={t('p4.compare.showSamples')} /></div>}
        </div>
        <p className="phase4-data-note">{t(includeSamples ? 'p4.compare.sampleNote' : 'p4.compare.verifiedNote')}</p>
        {!ready ? <CompareEmpty selected={selected} onAdd={() => setPickerOpen(true)} onSelect={changeSelection} onRemove={(id) => changeSelection(compare.filter((value) => value !== id))} /> : <>
          <p className="mb-4 text-xs text-mute" aria-live="polite">{t('p4.compare.differences', { n: diffCount, total: rows.length })}</p>
          <CompareVerdicts guitars={selected} />
          <CompareTable guitars={selected} diffOnly={diffOnly} onRemove={(id) => changeSelection(compare.filter((value) => value !== id))} grouped stickyNames includeSamples={includeSamples} editorial />
          {diffOnly && !diffCount && <p className="phase4-empty-note" role="status">{t('p4.compare.noDifferences')}</p>}
          <p className="mt-5 text-xs leading-6 text-mute">{t('p4.compare.scrollHint')}</p>
        </>}
      </section>
      <GuitarPicker open={pickerOpen} onClose={closePicker} onSelectionChange={changeSelection} />
      <ConfirmDialog open={confirmOpen} onClose={closeConfirm} title={t('p4.compare.clearTitle')} description={t('p4.compare.clearText')}
        onConfirm={() => { changeSelection([]); closeConfirm(); window.setTimeout(() => addRef.current?.focus(), 0); }} />
    </div>
  );
}
