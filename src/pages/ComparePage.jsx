import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { LANG, t } from '@/i18n';
import CompareTable from '@/components/compare/CompareTable';
import CompareVerdicts from '@/components/compare/CompareVerdicts';
import { analyseRows } from '@/components/compare/compareRows';
import GuitarPicker from '@/components/compare/GuitarPicker';
import AppLink from '@/components/ui/AppLink';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import ShareLink from '@/components/ui/ShareLink';
import { PlusIcon } from '@/components/ui/Icons';
import ComparisonIcon from '@/components/compare/ComparisonIcon';
import ComparisonSlots from '@/components/compare/ComparisonSlots';
import { COMPARE_CATEGORIES, rowInCategory } from '@/components/compare/compareCategories';
import { DISCOVERY_PHOTOGRAPHY } from '@/data/discoveryPhotography';
import '@/styles/premium-compare.css';
import Switch from '@/components/ui/Switch';
import { SAVED_GUITARS_BY_ID } from '@/data/guitars';
import { MAX_COMPARE, useShop } from '@/context/ShopContext';
import { normalizeGuitarIds } from '@/utils/selection';

export default function ComparePage() {
  const { compare, setCompareIds } = useShop();
  const [params, setParams] = useSearchParams();
  const [diffOnly, setDiffOnly] = useState(false);
  const [includeSamples, setIncludeSamples] = useState(false);
  const [pickerOpen, setPickerOpen] = useState(false);
  const addRef = useRef(null);
  const contentRef = useRef(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [category, setCategory] = useState('main');
  const categoryRefs = useRef([]);
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
  const removeGuitar = (id) => {
    const index = compare.indexOf(id);
    changeSelection(compare.filter((value) => value !== id));
    // A removed column also removes its focused button. Keep keyboard users in
    // the comparison, or return to Add Guitar when fewer than two remain.
    requestAnimationFrame(() => {
      const buttons = contentRef.current?.querySelectorAll('[data-compare-remove]');
      (buttons?.[Math.min(index, buttons.length - 1)] ?? addRef.current)?.focus({ preventScroll: true });
    });
  };
  const selected = useMemo(() => compare.map((id) => SAVED_GUITARS_BY_ID[id]).filter(Boolean), [compare]);
  const ready = selected.length >= 2;
  const rows = useMemo(() => analyseRows(selected, { includeSamples }), [selected, includeSamples]);
  const categoryRows = rows.filter(({ row }) => rowInCategory(row, category));
  const diffCount = categoryRows.filter((row) => row.diff).length;
  const photo = DISCOVERY_PHOTOGRAPHY.compareHero;
  const english = LANG === 'en';
  const benefits = [
    { icon: 'specs', title: english ? 'Compare the details' : 'สเปกในที่เดียว', text: english ? 'Source-backed specifications' : 'ข้อมูลจากแหล่งอ้างอิง' },
    { icon: 'tone', title: english ? 'See the differences' : 'เห็นความแตกต่าง', text: english ? 'Highlight what matters' : 'ชัดเจนในทุกรายละเอียด' },
    { icon: 'star', title: english ? `Up to ${MAX_COMPARE} guitars` : `เลือกได้สูงสุด ${MAX_COMPARE} รุ่น`, text: english ? 'Side by side' : 'เทียบกันแบบรุ่นต่อรุ่น' },
    { icon: 'share', title: english ? 'Share your shortlist' : 'แชร์การเปรียบเทียบ', text: english ? 'One link, your selection' : 'ส่งลิงก์ให้เพื่อนได้ทันที' },
  ];
  const changeCategoryByKey = (event, index) => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % COMPARE_CATEGORIES.length;
    else if (event.key === 'ArrowLeft') next = (index - 1 + COMPARE_CATEGORIES.length) % COMPARE_CATEGORIES.length;
    else if (event.key === 'Home') next = 0;
    else if (event.key === 'End') next = COMPARE_CATEGORIES.length - 1;
    else return;
    event.preventDefault(); setCategory(COMPARE_CATEGORIES[next].id); categoryRefs.current[next]?.focus();
  };
  const shareUrl = `${window.location.origin}/compare?ids=${compare.join(',')}`;

  return (
    <div className="comparison-page phase4-page premium-compare">
      <header className="pc-hero">
        {photo?.src && <div className="pc-hero__photograph"><img src={photo.src} srcSet={photo.srcSet} sizes="(min-width: 1024px) 70vw, 100vw" width={photo.width} height={photo.height} alt={photo.alt} loading="eager" fetchpriority="high" decoding="async" /></div>}
        <div className="pc-hero__shade" aria-hidden="true" />
        <div className="container-x pc-hero__inner">
          <nav aria-label={t('common.breadcrumb')} className="discovery-breadcrumb"><AppLink href="/">{t('nav.home')}</AppLink><span aria-hidden="true">›</span><span>{t('nav.compare')}</span></nav>
          <div className="pc-hero__copy">
            <p className="discovery-kicker">FRETLINE / เปรียบเทียบกีตาร์</p>
            <h1>{english ? <>Compare <em>Guitars</em></> : <>เปรียบเทียบ<em>กีตาร์</em></>}</h1>
            <h2>{english ? 'A clearer view of your next guitar.' : 'เลือกกีตาร์ 2–4 รุ่น แล้วสำรวจความแตกต่าง'}</h2>
            <p className="pc-hero__description">{english ? 'Compare specifications, materials and source-backed prices. Find the details that matter to your playing.' : 'เปรียบเทียบสเปก เสียง วัสดุ และราคาที่ตรวจสอบได้ เพื่อช่วยให้คุณเลือกกีตาร์ที่ใช่ได้ง่ายขึ้น'}</p>
            <ul className="pc-benefits">{benefits.map((benefit) => <li key={benefit.icon}><span className="pc-benefit-icon"><ComparisonIcon name={benefit.icon} /></span><span className="pc-benefit-title">{benefit.title}</span><span className="pc-benefit-copy">{benefit.text}</span></li>)}</ul>
          </div>
        </div>
      </header>
      <section ref={contentRef} className="container-x pc-workspace" aria-label={t('p4.compare.title')}>
        <div className="pc-actions compare-toolbar">
          <div className="pc-action-buttons">
            <button type="button" ref={addRef} onClick={() => setPickerOpen(true)} disabled={compare.length >= MAX_COMPARE} className="phase4-button is-gold"><PlusIcon size={20} />{t(compare.length >= MAX_COMPARE ? 'p4.compare.full' : 'p4.compare.add')}</button>
            <div className="pc-share"><ComparisonIcon name="share" size={18} /><ShareLink url={shareUrl} disabled={!selected.length} /></div>
            <button type="button" disabled={!selected.length} onClick={() => setConfirmOpen(true)} className="phase4-button"><ComparisonIcon name="trash" size={18} />{t('p4.compare.clear')}</button>
          </div>
          <span className="compare-count" role="status" aria-atomic="true">{t('p4.compare.count', { n: selected.length, max: MAX_COMPARE })}</span>
        </div>
        <ComparisonSlots selected={selected} onAdd={() => setPickerOpen(true)} onRemove={removeGuitar} />
        {selected.some((guitar) => guitar.archived) && <p className="archive-notice" role="note">{t('p7.archive.saved')}</p>}
        {ready && <>
          <div className="pc-categories" role="tablist" aria-label={english ? 'Comparison categories' : 'หมวดหมู่ข้อมูลเปรียบเทียบ'}>
            {COMPARE_CATEGORIES.map((entry, index) => <button key={entry.id} type="button" role="tab" id={`compare-tab-${entry.id}`} aria-selected={category === entry.id} aria-controls="compare-category-panel" tabIndex={category === entry.id ? 0 : -1} data-compare-category={entry.id} ref={(node) => { categoryRefs.current[index] = node; }} onClick={() => setCategory(entry.id)} onKeyDown={(event) => changeCategoryByKey(event, index)}><ComparisonIcon name={entry.icon} size={19} /><span>{english ? entry.en : entry.th}</span></button>)}
          </div>
          <div className="pc-table-tools">
            <p aria-live="polite">{t('p4.compare.differences', { n: diffCount, total: categoryRows.length })}</p>
            <div className="pc-switches"><Switch checked={diffOnly} onChange={setDiffOnly} label={t('cmp.diffOnly')} /><Switch checked={includeSamples} onChange={setIncludeSamples} label={t('p4.compare.showSamples')} /></div>
          </div>
          <div id="compare-category-panel" role="tabpanel" aria-labelledby={`compare-tab-${category}`}>
            <CompareTable guitars={selected} diffOnly={diffOnly} stickyNames includeSamples={includeSamples} editorial compact rowFilter={(row) => rowInCategory(row, category)} />
            {diffOnly && !diffCount && <p className="phase4-empty-note" role="status">{t('p4.compare.noDifferences')}</p>}
          </div>
          <p className="pc-scroll-hint">{t('p4.compare.scrollHint')}</p>
          <div className="pc-verdicts"><CompareVerdicts guitars={selected} /></div>
        </>}
      </section>
      <GuitarPicker open={pickerOpen} onClose={closePicker} onSelectionChange={changeSelection} />
      <ConfirmDialog open={confirmOpen} onClose={closeConfirm} title={t('p4.compare.clearTitle')} description={t('p4.compare.clearText')}
        onConfirm={() => { changeSelection([]); closeConfirm(); window.setTimeout(() => addRef.current?.focus(), 0); }} />
    </div>
  );
}
