import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { LANG } from '@/i18n';
import ChordDiagram from '@/features/practice/components/ChordDiagram';
import GuitarNeckViewer from '@/features/practice/components/GuitarNeckViewer';
import PracticeIcon from '@/features/practice/components/PracticeIcons';
import { useChordAudio } from '@/features/practice/hooks/useChordAudio';
import { PRACTICE_CHORDS, CHORD_TYPES, PRACTICE_CHORD_BY_ID } from '@/features/practice/data/chords';
import '@/styles/practice.css';
import '@/styles/practice-minimal.css';

const EN = LANG === 'en';
const localized = value => typeof value === 'string' ? value : value?.[LANG] ?? value?.th ?? value?.en ?? '';
const normalize = value => value.toLocaleLowerCase().normalize('NFKC').replaceAll('♯', '#').replaceAll('♭', 'b').replace(/\s+/g, ' ').trim();
const BASIC_IDS = new Set(['C', 'D', 'E', 'F', 'G', 'A', 'Dm', 'Em', 'Am']);
const POPULAR = ['C', 'G', 'D', 'Am', 'Em', 'F', 'Dm', 'E7'].map(id => PRACTICE_CHORD_BY_ID[id]);
const FILTERS = [
  { id: '', label: EN ? 'All' : 'ทั้งหมด' }, { id: 'basic', label: EN ? 'Basics' : 'พื้นฐาน' },
  { id: 'major', label: 'Major' }, { id: 'minor', label: 'Minor' }, { id: 'dominant7', label: '7' },
  { id: 'major7', label: 'Maj7' }, { id: 'minor7', label: 'm7' }, { id: 'suspended', label: 'Sus' },
];
const COPY = EN ? {
  title: 'Guitar practice', subtitle: 'Choose a chord. Find your angle. Make it yours.', choose: 'Choose chord', search: 'Search chords', placeholder: 'Search C, Am…',
  types: 'Chord type', clear: 'Clear search', results: 'chords', clearFilters: 'Clear filters', empty: 'No matching chords', emptyText: 'Try another name or chord type.',
  previous: 'Previous chord', next: 'Next chord', outside: 'Outside these results', selected: 'Selected chord', positions: 'Finger positions', string: 'String', fret: 'Fret',
  fingers: ['Index', 'Middle', 'Ring', 'Little'], barre: 'Barre', open: 'Open strings', muted: 'Muted strings', none: 'None', notes: 'Practice notes',
  listen: 'Listen to chord', stop: 'Stop chord', popular: 'Popular chords', left: 'Previous popular chords', right: 'Next popular chords',
  keyboard: 'Arrow keys select a chord. Home and End go to the first and last chord.', announcement: 'Selected chord: ', credits: 'Model credits',
} : {
  title: 'ฝึกกีตาร์', subtitle: 'เลือกคอร์ด แล้วค่อย ๆ ฝึกในมุมที่ถนัด', choose: 'เลือกคอร์ด', search: 'ค้นหาคอร์ด', placeholder: 'ค้นหา เช่น C, Am…',
  types: 'ประเภทคอร์ด', clear: 'ล้างคำค้น', results: 'คอร์ด', clearFilters: 'ล้างตัวกรอง', empty: 'ยังไม่พบคอร์ด', emptyText: 'ลองค้นหาชื่อหรือเลือกประเภทอื่น',
  previous: 'คอร์ดก่อนหน้า', next: 'คอร์ดถัดไป', outside: 'อยู่นอกผลค้นหา', selected: 'คอร์ดที่เลือก', positions: 'ตำแหน่งนิ้ว', string: 'สาย', fret: 'เฟรต',
  fingers: ['นิ้วชี้', 'นิ้วกลาง', 'นิ้วนาง', 'นิ้วก้อย'], barre: 'ทาบสาย', open: 'สายเปิด', muted: 'ไม่เล่นสาย', none: 'ไม่มี', notes: 'แนวทางฝึก',
  listen: 'ฟังเสียงคอร์ด', stop: 'หยุดเสียงคอร์ด', popular: 'คอร์ดยอดนิยม', left: 'เลื่อนคอร์ดยอดนิยมไปทางซ้าย', right: 'เลื่อนคอร์ดยอดนิยมไปทางขวา',
  keyboard: 'ใช้ลูกศรเลือกคอร์ด · Home / End ไปคอร์ดแรก / สุดท้าย', announcement: 'คอร์ดที่เลือก: ', credits: 'สิทธิ์และเครดิตโมเดล',
};
const ChordOption = memo(function ChordOption({ item, selected, index, focusable, onChoose, onKeyDown, optionRefs }) {
  return <button type="button" className="practice-chord-option" data-practice-chord={item.id} aria-pressed={selected}
    aria-label={COPY.choose + ' ' + item.fullName} tabIndex={focusable ? 0 : -1}
    ref={node => { if (node) optionRefs.current.set(item.id, node); else optionRefs.current.delete(item.id); }}
    onClick={() => onChoose(item.id)} onKeyDown={event => onKeyDown(event, index)}>
    <ChordDiagram chord={item} compact />
    <span className="practice-chord-option-text"><strong lang="en">{item.name}</strong><span lang="en">{item.fullName}</span></span>
    <span className="practice-option-indicator" aria-hidden="true" />
  </button>;
});

export default function PracticePage() {
  const [params, setParams] = useSearchParams();
  const [poseStatus, setPoseStatus] = useState(null);
  const [popularEdges, setPopularEdges] = useState({ start: true, end: false });
  const optionRefs = useRef(new Map()), libraryRef = useRef(null), popularRef = useRef(null);
  const query = params.get('q') ?? '';
  const type = FILTERS.some(item => item.id === params.get('type')) ? params.get('type') : '';
  const chord = PRACTICE_CHORD_BY_ID[params.get('chord')] ?? PRACTICE_CHORD_BY_ID.C;
  const audio = useChordAudio(chord);
  const results = useMemo(() => {
    const terms = normalize(query).split(' ').filter(Boolean), rootOnly = /^[a-g](?:#|b)?$/.test(normalize(query));
    return PRACTICE_CHORDS.filter(item => {
      if (type === 'basic' && !BASIC_IDS.has(item.id)) return false;
      if (type && type !== 'basic' && item.type !== type) return false;
      if (rootOnly) return normalize(item.root) === normalize(query);
      const quality = CHORD_TYPES.find(entry => entry.id === item.type);
      const text = normalize([item.id, item.name, item.fullName, item.quality, item.type, quality?.label.th, quality?.label.en].join(' '));
      return terms.every(term => text.includes(term));
    });
  }, [query, type]);
  const resultIndex = results.findIndex(item => item.id === chord.id);
  const update = useCallback(patch => {
    const next = { chord: chord.id, q: query, type, ...patch }, search = new URLSearchParams(params);
    search.set('chord', next.chord);
    for (const name of ['q', 'type']) { if (next[name]) search.set(name, next[name]); else search.delete(name); }
    setParams(search, { replace: Boolean(patch.replace), preventScrollReset: true });
  }, [params, setParams, chord.id, query, type]);
  const choose = useCallback(id => update({ chord: id }), [update]);
  const choosePopular = id => update({ chord: id, q: '', type: '' });
  const navigate = direction => {
    if (results.length < 2) return;
    choose(results[resultIndex < 0 ? direction > 0 ? 0 : results.length - 1 : (resultIndex + direction + results.length) % results.length].id);
  };
  const onOptionKeyDown = useCallback((event, index) => {
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    let next;
    if (['ArrowRight', 'ArrowDown'].includes(event.key)) next = (index + 1) % results.length;
    else if (['ArrowLeft', 'ArrowUp'].includes(event.key)) next = (index - 1 + results.length) % results.length;
    else if (event.key === 'Home') next = 0;
    else if (event.key === 'End') next = results.length - 1;
    else return;
    event.preventDefault(); choose(results[next].id); optionRefs.current.get(results[next].id)?.focus({ preventScroll: true });
  }, [results, choose]);
  useEffect(() => { document.title = EN ? 'Guitar Practice 3D | Fretline' : 'ฝึกกีตาร์ 3D | Fretline'; }, []);
  useEffect(() => {
    // Scroll only the library itself; choosing a chord must not jump the page.
    const list = libraryRef.current, node = optionRefs.current.get(chord.id);
    if (!list || !node) return;
    const box = list.getBoundingClientRect(), selected = node.getBoundingClientRect();
    if (getComputedStyle(list).flexDirection === 'row') {
      if (selected.left < box.left || selected.right > box.right) list.scrollLeft += selected.left - box.left - (box.width - selected.width) / 2;
    } else if (selected.top < box.top || selected.bottom > box.bottom) list.scrollTop += selected.top - box.top - (box.height - selected.height) / 2;
  }, [chord.id, results]);
  useEffect(() => {
    const list = popularRef.current;
    if (!list) return;
    let frame = 0;
    const measure = () => {
      frame = 0;
      const start = list.scrollLeft <= 2, end = list.scrollLeft + list.clientWidth >= list.scrollWidth - 2;
      setPopularEdges(previous => previous.start === start && previous.end === end ? previous : { start, end });
    };
    const schedule = () => { if (!frame) frame = requestAnimationFrame(measure); };
    const observer = new ResizeObserver(schedule); observer.observe(list);
    list.addEventListener('scroll', schedule, { passive: true }); measure();
    return () => { observer.disconnect(); list.removeEventListener('scroll', schedule); cancelAnimationFrame(frame); };
  }, []);
  const slidePopular = direction => {
    const list = popularRef.current;
    if (list) list.scrollBy({ left: direction * Math.max(160, list.clientWidth * .7), behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  };
  const fingerings = chord.frets.flatMap((fret, index) => fret > 0 ? [{ string: 6 - index, fret, finger: chord.fingers[index], note: chord.notes[index] }] : [])
    .sort((a, b) => a.finger - b.finger || b.string - a.string);
  const stringsFor = value => chord.frets.flatMap((fret, index) => fret === value ? [6 - index] : []).join(', ') || COPY.none;
  const instructions = chord.instructions?.[LANG] ?? chord.instructions.en;
  const handStatus = poseStatus?.chordId === chord.id ? poseStatus.status : chord.handPose.status;

  return <div className="practice-page practice-minimal" data-practice-edition="premium-minimal" data-audio-status={audio.state.status}
    data-audio-rate={audio.rate} data-audio-tones={audio.state.tones ? JSON.stringify(audio.state.tones) : undefined}>
    <div className="practice-shell container-x">
      <div className="practice-main-grid">
        <header className="practice-intro">
          <p className="practice-minimal-eyebrow">PRACTICE 3D</p>
          <h1>{COPY.title} <span>3D</span></h1>
          <p className="practice-intro-description">{COPY.subtitle}</p>
        </header>

        <section className="practice-chord-library" aria-labelledby="practice-choose-title">
          <div className="practice-library-heading"><h2 id="practice-choose-title">{COPY.choose}</h2><span>{PRACTICE_CHORDS.length} {COPY.results}</span></div>
          <div className="practice-library-toolbar">
            <div className="practice-search-field"><label htmlFor="practice-chord-search" className="practice-sr-only">{COPY.search}</label>
              <PracticeIcon name="search" size={16} /><input id="practice-chord-search" type="search" value={query} autoComplete="off" placeholder={COPY.placeholder} onChange={event => update({ q: event.target.value, replace: true })} />
              {query && <button type="button" aria-label={COPY.clear} onClick={() => update({ q: '' })}>×</button>}
            </div>
            <label className="practice-mobile-type"><span className="practice-sr-only">{COPY.types}</span><select aria-label={COPY.types} value={type} onChange={event => update({ type: event.target.value })}>{FILTERS.map(item => <option key={item.id} value={item.id}>{item.label}</option>)}</select><PracticeIcon name="chevron" size={14} /></label>
          </div>
          <div className="practice-type-filters" role="group" aria-label={COPY.types}>{FILTERS.map(item => <button type="button" key={item.id} data-practice-type={item.id || 'all'} aria-pressed={type === item.id} onClick={() => update({ type: item.id })}>{item.label}</button>)}</div>
          <p className="practice-sr-only" id="practice-chord-keyboard">{COPY.keyboard}</p>
          <div ref={libraryRef} className="practice-chord-options" role="group" aria-labelledby="practice-choose-title" aria-describedby="practice-chord-keyboard">
            {results.map((item, index) => <ChordOption key={item.id} item={item} selected={item.id === chord.id} index={index} focusable={resultIndex < 0 ? index === 0 : index === resultIndex}
              onChoose={choose} onKeyDown={onOptionKeyDown} optionRefs={optionRefs} />)}
            {!results.length && <div className="practice-chord-empty"><h3>{COPY.empty}</h3><p>{COPY.emptyText}</p><button type="button" onClick={() => update({ q: '', type: '' })}>{COPY.clearFilters}</button></div>}
          </div>
          <div className="practice-chord-navigation" role="group" aria-label={COPY.choose}>
            <button type="button" data-practice-previous onClick={() => navigate(-1)} disabled={results.length < 2} aria-label={COPY.previous}><PracticeIcon name="left" size={16} /></button>
            <span className="practice-navigation-count" data-practice-result-count={results.length} aria-live="polite">{resultIndex >= 0 ? `${resultIndex + 1} / ${results.length}` : results.length ? COPY.outside : `0 / ${PRACTICE_CHORDS.length}`}</span>
            <button type="button" data-practice-next onClick={() => navigate(1)} disabled={results.length < 2} aria-label={COPY.next}><PracticeIcon name="right" size={16} /></button>
          </div>
        </section>

        <section className="practice-viewer-column" aria-label={EN ? '3D guitar experience' : 'พื้นที่ฝึกกีตาร์ 3D'}>
          <GuitarNeckViewer chord={chord} audio={audio} onPoseStatus={setPoseStatus} />
        </section>

        <aside className="practice-chord-detail" aria-labelledby="practice-selected-title" data-practice-active-chord={chord.id} data-diagram-status={chord.diagramStatus.status} data-hand-pose-status={handStatus}>
          <p className="practice-detail-eyebrow">{COPY.selected}</p>
          <div className="practice-selected-heading"><h2 id="practice-selected-title" lang="en">{chord.fullName}</h2><span lang="en">{chord.name}</span></div>
          <p className="practice-sr-only" role="status" aria-live="polite" aria-atomic="true">{COPY.announcement}{chord.fullName}</p>
          <div className="practice-diagram-wrap"><ChordDiagram chord={chord} /></div>
          <div className="practice-fingering"><h3>{COPY.positions}</h3><ul>{fingerings.map(({ string, fret, finger, note }) => <li key={string} data-finger-instruction={finger} data-string={string} data-fret={fret}>
            <span className="practice-finger-number" aria-hidden="true">{finger}</span><span><strong>{COPY.fingers[finger - 1]}</strong><span>{COPY.string} {string} · {COPY.fret} {fret}<span lang="en"> · {note}</span></span></span>
          </li>)}</ul>{chord.barres.length > 0 && <div className="practice-barre-instructions">{chord.barres.map((barre, index) => <p key={index} data-barre-instruction={index}><strong>{COPY.barre} · {COPY.fingers[barre.finger - 1]}</strong><span>{COPY.fret} {barre.fret} · {COPY.string} {barre.fromString}–{barre.toString}</span></p>)}</div>}</div>
          <dl className="practice-string-status"><div><dt><span aria-hidden="true">○</span> {COPY.open}</dt><dd>{stringsFor(0)}</dd></div><div><dt><span aria-hidden="true">×</span> {COPY.muted}</dt><dd>{stringsFor(null)}</dd></div></dl>
          <details className="practice-instructions"><summary>{COPY.notes}</summary><ol>{instructions.map((text, index) => <li key={index}>{text}</li>)}</ol></details>
          <button type="button" className="practice-detail-listen" data-practice-detail-play onClick={audio.toggle} aria-pressed={audio.playing}><PracticeIcon name={audio.playing ? 'stop' : 'sound'} size={17} />{audio.playing ? COPY.stop : COPY.listen}</button>
        </aside>
      </div>

      <section className="practice-popular" aria-labelledby="practice-popular-title">
        <div className="practice-popular-heading"><h2 id="practice-popular-title">{COPY.popular}</h2><div><button type="button" onClick={() => slidePopular(-1)} disabled={popularEdges.start} aria-label={COPY.left}><PracticeIcon name="left" /></button><button type="button" onClick={() => slidePopular(1)} disabled={popularEdges.end} aria-label={COPY.right}><PracticeIcon name="right" /></button></div></div>
        <div className="practice-popular-track" ref={popularRef}>{POPULAR.map(item => <button key={item.id} type="button" className="practice-popular-chord" data-popular-chord={item.id} onClick={() => choosePopular(item.id)} aria-pressed={chord.id === item.id} aria-label={COPY.choose + ' ' + item.fullName}>
          <ChordDiagram chord={item} compact /><span><strong lang="en">{item.name}</strong><span>{localized(CHORD_TYPES.find(type => type.id === item.type).label)}</span></span>
        </button>)}</div>
      </section>
      <details className="practice-model-credits"><summary>{COPY.credits}</summary><p>{EN ? 'Hand and skin: ' : 'โมเดลมือและผิว: '}<a href="https://www.makehumancommunity.org/content/license.html" target="_blank" rel="noreferrer">MakeHuman · CC0</a>{' · '}{EN ? 'Sleeve adapted from ' : 'แขนเสื้อดัดแปลงจาก '}<a href="https://static.makehumancommunity.org/assets/assetpacks/shirts02.html" target="_blank" rel="noreferrer">Elvaerwyn · CC-BY</a></p></details>
    </div>
  </div>;
}
