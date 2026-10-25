import { useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import AppLink from '@/components/ui/AppLink';
import { ArrowRightIcon } from '@/components/ui/Icons';
import { LANG } from '@/i18n';
import ChordDiagram from '@/features/practice/components/ChordDiagram';
import GuitarNeckViewer from '@/features/practice/components/GuitarNeckViewer';
import { PRACTICE_CHORDS, CHORD_TYPES } from '@/features/practice/data/chords';
import '@/styles/practice.css';

const COPY = {
  th: {
    docTitle: 'Guitar Practice Studio — ฝึกคอร์ด 3D | Fretline', home: 'หน้าหลัก', practice: 'ฝึกกีตาร์',
    eyebrow: 'THE ART OF YOUR NEXT CHORD', intro: 'ฝึกทีละคอร์ด เข้าใจทุกตำแหน่ง',
    description: 'สำรวจคอกีตาร์ 3D พร้อมผังคอร์ด 42 แบบ เลือกมุมที่ถนัด แล้วค่อย ๆ วางนิ้วตามผัง',
    stage: 'YOUR PRACTICE SPACE', stageTitle: 'มองให้ชัด ฝึกให้มั่นใจ', stageText: 'หมุน ซูม และเปลี่ยนคอร์ดได้ตามจังหวะของคุณ',
    strings: 'สาย', frets: 'เฟรต', chords: 'คอร์ด', choose: 'ค้นหาคอร์ดถัดไป',
    chooseDescription: 'ค้นหาชื่อคอร์ด หรือเลือกประเภทเพื่อจัดชุดฝึกของคุณ', chooseLabel: 'เลือกคอร์ด',
    explore: 'คอร์ดเดียวกัน มองได้ทุกมุม', exploreDescription: 'ลากเพื่อหมุน · จีบนิ้วเพื่อซูม · มีปุ่มปรับมุมมองให้เลือก',
    selected: 'คอร์ดที่เลือก', positioning: 'ตำแหน่งวางนิ้ว', finger: 'นิ้ว', string: 'สาย', fret: 'เฟรต',
    fingerNames: ['นิ้วชี้', 'นิ้วกลาง', 'นิ้วนาง', 'นิ้วก้อย'], barre: 'ทาบสาย', stringsRange: 'สาย',
    open: 'สายเปิด', muted: 'ไม่เล่นสาย', none: 'ไม่มี', diagramView: 'มองตรงเข้าหาฟิงเกอร์บอร์ด สาย 6 (E ต่ำ) อยู่ซ้าย',
    diagramLegend: 'เลขบนจุดคือหมายเลขนิ้ว · แถบทองคือทาบสาย · ○ สายเปิด · × ไม่เล่นสาย',
    tuning: 'การตั้งสายมาตรฐาน', preview: 'ฝึกจากผังทีละขั้น',
    previewText: 'เริ่มจากสายที่ต้องกด ตรวจสายเปิดและสายที่ไม่เล่น แล้วดีดช้า ๆ ทีละสาย ผังคอร์ดและสถานะการตรวจท่ามือแสดงแยกกันสำหรับแต่ละคอร์ด',
    modelNote: 'แบบจำลองเพื่อศึกษาโครงสร้างคอกีตาร์ ไม่ได้แสดงกีตาร์รุ่นใดในแคตตาล็อก', catalog: 'สำรวจกีตาร์ในแคตตาล็อก',
    search: 'ค้นหาคอร์ด', searchPlaceholder: 'เช่น C, Am, dominant 7…', clearSearch: 'ล้างคำค้น', allTypes: 'ทุกประเภท', typeFilter: 'ประเภทคอร์ด',
    results: 'คอร์ดที่พบ', clearFilters: 'ล้างตัวกรอง', empty: 'ยังไม่พบคอร์ดที่ตรงกัน', emptyText: 'ลองใช้ชื่อสั้น ๆ เช่น C หรือ Am หรือเลือกประเภทอื่น',
    previous: 'คอร์ดก่อนหน้า', next: 'คอร์ดถัดไป', navigation: 'เปลี่ยนคอร์ดในผลการค้นหา', currentOutside: 'คอร์ดที่เลือกอยู่นอกผลการค้นหา',
    keyboard: 'คีย์บอร์ด: ใช้ลูกศรเลือกคอร์ด · Home / End ไปคอร์ดแรก / สุดท้าย',
    diagramStatus: 'ผังคอร์ด', handStatus: 'ท่ามือ 3D', voicing: 'รูปแบบการจับ', instructions: 'แนวทางฝึก',
    statusVerified: 'ตรวจแล้ว', statusReview: 'ต้องตรวจทาน', statusUnavailable: 'ยังไม่พร้อม',
    handUnavailable: 'ยังไม่มีท่ามือที่ผ่านการตรวจสำหรับคอร์ดนี้', selectedAnnouncement: 'คอร์ดที่เลือก: ',
  },
  en: {
    docTitle: 'Guitar Practice Studio — 3D Chords | Fretline', home: 'Home', practice: 'Practice',
    eyebrow: 'THE ART OF YOUR NEXT CHORD', intro: 'One chord at a time. Every position, understood.',
    description: 'Explore a 3D guitar neck and 42 chord diagrams. Find your angle, then work through each finger position.',
    stage: 'YOUR PRACTICE SPACE', stageTitle: 'See clearly. Practice with purpose.', stageText: 'Rotate, zoom and change chords at your own pace',
    strings: 'strings', frets: 'frets', chords: 'chords', choose: 'Find your next chord',
    chooseDescription: 'Search by chord name or choose a type to shape your practice.', chooseLabel: 'Choose chord',
    explore: 'One chord. Every perspective.', exploreDescription: 'Drag to rotate · Pinch to zoom · Camera buttons also available',
    selected: 'Selected chord', positioning: 'Finger positions', finger: 'Finger', string: 'String', fret: 'Fret',
    fingerNames: ['Index finger', 'Middle finger', 'Ring finger', 'Little finger'], barre: 'Barre', stringsRange: 'strings',
    open: 'Open strings', muted: 'Muted strings', none: 'None', diagramView: 'Front view of the fingerboard. String 6 (low E) is on the left.',
    diagramLegend: 'Dot numbers are fingers · Gold bars are barres · ○ open string · × do not play',
    tuning: 'Standard tuning', preview: 'Work through the diagram',
    previewText: 'Start with the fretted notes, check the open and muted strings, then pick slowly through each string. Diagram accuracy and 3D hand review are shown separately for every chord.',
    modelNote: 'A generic study model of a guitar neck; it does not represent a catalog model.', catalog: 'Explore the guitar catalog',
    search: 'Search chords', searchPlaceholder: 'Try C, Am, dominant 7…', clearSearch: 'Clear search', allTypes: 'All types', typeFilter: 'Chord type',
    results: 'chords found', clearFilters: 'Clear filters', empty: 'No matching chords', emptyText: 'Try a short name such as C or Am, or choose another chord type.',
    previous: 'Previous chord', next: 'Next chord', navigation: 'Browse chords in search results', currentOutside: 'Selected chord is outside these results',
    keyboard: 'Keyboard: arrows choose a chord · Home / End go to the first / last chord',
    diagramStatus: 'Chord diagram', handStatus: '3D hand pose', voicing: 'Voicing', instructions: 'Practice notes',
    statusVerified: 'Verified', statusReview: 'Needs review', statusUnavailable: 'Unavailable',
    handUnavailable: 'A reviewed hand pose is not available for this chord', selectedAnnouncement: 'Selected chord: ',
  },
};

const localized = (value) => typeof value === 'string' ? value : value?.[LANG] ?? value?.en ?? value?.th ?? '';
const normalizeSearch = (value) => value.toLocaleLowerCase().normalize('NFKC').replaceAll('♯', '#').replaceAll('♭', 'b').replace(/\s+/g, ' ').trim();
const statusValue = (value) => ['verified', 'needs-review', 'unavailable'].includes(value) ? value : 'unavailable';

export default function PracticePage() {
  const copy = COPY[LANG] ?? COPY.th;
  const [params, setParams] = useSearchParams();
  const [poseStatus, setPoseStatus] = useState(null);
  const optionRefs = useRef(new Map());
  const query = params.get('q') ?? '';
  const type = CHORD_TYPES.some((item) => item.id === params.get('type')) ? params.get('type') : '';
  const chord = PRACTICE_CHORDS.find((item) => item.id === params.get('chord')) ?? PRACTICE_CHORDS.find((item) => item.id === 'C') ?? PRACTICE_CHORDS[0];
  const results = useMemo(() => {
    const normalizedQuery = normalizeSearch(query);
    const terms = normalizedQuery.split(' ').filter(Boolean);
    const rootOnly = /^[a-g](?:#|b)?$/.test(normalizedQuery);
    return PRACTICE_CHORDS.filter((item) => {
      if (type && item.type !== type) return false;
      if (rootOnly) return normalizeSearch(item.root) === normalizedQuery;
      const chordType = CHORD_TYPES.find((entry) => entry.id === item.type);
      const searchable = normalizeSearch([item.id, item.name, item.fullName, item.root, item.quality, item.type, localized(item.voicing), chordType?.label?.th, chordType?.label?.en].filter(Boolean).join(' '));
      return terms.every((term) => searchable.includes(term));
    });
  }, [query, type]);
  const resultIndex = results.findIndex((item) => item.id === chord.id);
  const hasFilters = Boolean(query || type);
  const fingerings = chord.frets.flatMap((fret, index) => fret > 0 ? [{ string: 6 - index, fret, finger: chord.fingers[index], note: chord.notes?.[index] }] : [])
    .sort((a, b) => a.finger - b.finger || b.string - a.string);
  const barres = chord.barres ?? [];
  const instructions = chord.instructions?.[LANG] ?? chord.instructions?.en ?? [];
  const handPose = poseStatus?.chordId === chord.id ? poseStatus : chord.handPose;
  const handStatus = statusValue(handPose?.status);
  const diagramStatus = statusValue(chord.diagramStatus?.status);
  const statusLabel = (status) => status === 'verified' ? copy.statusVerified : status === 'needs-review' ? copy.statusReview : copy.statusUnavailable;
  const stringsFor = (value) => chord.frets.flatMap((fret, index) => fret === value ? [6 - index] : []).join(', ') || copy.none;

  useEffect(() => { document.title = copy.docTitle; }, [copy.docTitle]);

  // Selection and filters have one source of truth, so shared URLs and history agree.
  const update = (patch, replace = false) => {
    const next = { chord: chord.id, q: query, type, ...patch };
    const search = new URLSearchParams(params);
    search.set('chord', next.chord);
    if (next.q) search.set('q', next.q); else search.delete('q');
    if (next.type) search.set('type', next.type); else search.delete('type');
    setParams(search, { replace, preventScrollReset: true });
  };
  const choose = (id) => update({ chord: id });
  const navigate = (direction) => {
    if (results.length < 2) return;
    const index = resultIndex < 0 ? (direction > 0 ? 0 : results.length - 1) : (resultIndex + direction + results.length) % results.length;
    choose(results[index].id);
  };
  const onOptionKeyDown = (event, index) => {
    let nextIndex;
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') nextIndex = (index + 1) % results.length;
    else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') nextIndex = (index - 1 + results.length) % results.length;
    else if (event.key === 'Home') nextIndex = 0;
    else if (event.key === 'End') nextIndex = results.length - 1;
    else return;
    event.preventDefault();
    choose(results[nextIndex].id);
    optionRefs.current.get(results[nextIndex].id)?.focus({ preventScroll: true });
  };

  return (
    <div className="practice-page">
      <header className="practice-intro container-x">
        <nav className="practice-breadcrumb" aria-label={LANG === 'en' ? 'Breadcrumb' : 'เส้นทางนำทาง'}>
          <AppLink href="/">{copy.home}</AppLink><span aria-hidden="true">/</span><span aria-current="page">{copy.practice}</span>
        </nav>
        <div className="practice-intro-grid">
          <div>
            <p className="practice-eyebrow" lang="en">{copy.eyebrow}</p>
            <h1 lang="en">Guitar <span>Practice Studio.</span></h1>
            <p className="practice-intro-title">{copy.intro}</p>
            <p className="practice-intro-description">{copy.description}</p>
          </div>
          <div className="practice-intro-aside">
            <p className="practice-stage-label" lang="en">{copy.stage}</p>
            <h2>{copy.stageTitle}</h2><p>{copy.stageText}</p>
            <dl className="practice-facts">
              <div><dd>06</dd><dt>{copy.strings}</dt></div>
              <div><dd>12</dd><dt>{copy.frets}</dt></div>
              <div><dd>{String(PRACTICE_CHORDS.length).padStart(2, '0')}</dd><dt>{copy.chords}</dt></div>
            </dl>
          </div>
        </div>
      </header>

      <div className="practice-workspace container-x">
        <section className="practice-studio" aria-labelledby="practice-studio-title">
          <div className="practice-section-heading">
            <div><p className="practice-section-index" lang="en">01 / THE FRETBOARD</p><h2 id="practice-studio-title">{copy.explore}</h2></div>
            <p>{copy.exploreDescription}</p>
          </div>
          <div className="practice-studio-layout">
            <div className="practice-viewer-column">
              <GuitarNeckViewer chord={chord} onPoseStatus={setPoseStatus} />
              <div className="practice-chord-navigation" role="group" aria-label={copy.navigation}>
                <button type="button" data-practice-previous disabled={results.length < 2} onClick={() => navigate(-1)}><span aria-hidden="true">←</span>{copy.previous}</button>
                <span className="practice-navigation-count" aria-live="polite">{resultIndex >= 0 ? (resultIndex + 1) + ' / ' + results.length : copy.currentOutside}</span>
                <button type="button" data-practice-next disabled={results.length < 2} onClick={() => navigate(1)}>{copy.next}<span aria-hidden="true">→</span></button>
              </div>
            </div>
            <aside className="practice-chord-detail" aria-labelledby="practice-selected-title" data-practice-active-chord={chord.id}>
              <div className="practice-selected-heading"><p>{copy.selected}</p><h3 id="practice-selected-title" lang="en">{chord.name}</h3><span lang="en">{chord.fullName}</span></div>
              <p className="practice-sr-only" role="status" aria-live="polite" aria-atomic="true">{copy.selectedAnnouncement}{chord.fullName ?? chord.name}</p>
              <div className="practice-diagram-wrap"><ChordDiagram chord={chord} /></div>
              <p className="practice-diagram-caption">{copy.diagramView}</p>
              <div className="practice-status-list">
                <div data-diagram-status={diagramStatus}><span>{copy.diagramStatus}</span><strong>{statusLabel(diagramStatus)}</strong></div>
                <div data-hand-pose-status={handStatus}><span>{copy.handStatus}</span><strong>{statusLabel(handStatus)}</strong></div>
                <p className="practice-hand-status-reason">{localized(handPose?.reason) || copy.handUnavailable}</p>
              </div>
              <div className="practice-fingering">
                {chord.voicing && <p className="practice-voicing"><span>{copy.voicing}</span>{localized(chord.voicing)}</p>}
                <h4>{copy.positioning}</h4>
                <ul>{fingerings.map(({ string, fret, finger, note }) => <li key={string} data-finger-instruction={finger} data-string={string} data-fret={fret}>
                  <span className="practice-finger-number" aria-hidden="true">{finger}</span>
                  <span><strong>{copy.fingerNames[finger - 1] ?? copy.finger + ' ' + finger}</strong><span>{copy.string} {string} <span aria-hidden="true">·</span> {copy.fret} {fret}{note && <span lang="en"> · {note}</span>}</span></span>
                </li>)}</ul>
                {barres.length > 0 && <div className="practice-barre-instructions">{barres.map((barre, index) => <p key={index} data-barre-instruction={index}><strong>{copy.barre} · {copy.fingerNames[barre.finger - 1]}</strong><span>{copy.fret} {barre.fret} · {copy.stringsRange} {barre.fromString}–{barre.toString}</span></p>)}</div>}
                <dl className="practice-string-status"><div><dt>{copy.open}</dt><dd>{stringsFor(0)}</dd></div><div><dt>{copy.muted}</dt><dd>{stringsFor(null)}</dd></div></dl>
              </div>
              {instructions.length > 0 && <details className="practice-instructions"><summary>{copy.instructions}</summary><ol>{instructions.map((instruction, index) => <li key={index}>{instruction}</li>)}</ol></details>}
              <p className="practice-diagram-legend">{copy.diagramLegend}</p>
            </aside>
          </div>
        </section>

        <section className="practice-chord-library" aria-labelledby="practice-choose-title">
          <div className="practice-section-heading">
            <div><p className="practice-section-index" lang="en">02 / CHORD LIBRARY</p><h2 id="practice-choose-title">{copy.choose}</h2></div>
            <p>{copy.chooseDescription}</p>
          </div>
          <div className="practice-library-toolbar">
            <div className="practice-search-field">
              <label htmlFor="practice-chord-search">{copy.search}</label>
              <div><span aria-hidden="true" className="practice-search-icon">⌕</span><input id="practice-chord-search" type="search" value={query} autoComplete="off" placeholder={copy.searchPlaceholder} onChange={(event) => update({ q: event.target.value }, true)} />
                {query && <button type="button" className="practice-search-clear" aria-label={copy.clearSearch} onClick={() => update({ q: '' })}><span aria-hidden="true">×</span></button>}
              </div>
            </div>
            <div className="practice-result-summary"><p role="status" aria-live="polite" aria-atomic="true" data-practice-result-count={results.length}><strong>{results.length}</strong> {copy.results} <span> / {PRACTICE_CHORDS.length}</span></p>{hasFilters && <button type="button" onClick={() => update({ q: '', type: '' })}>{copy.clearFilters}</button>}</div>
          </div>
          <div className="practice-type-filters" role="group" aria-label={copy.typeFilter}>
            {[{ id: '', label: copy.allTypes }, ...CHORD_TYPES].map((item) => <button key={item.id} type="button" data-practice-type={item.id || 'all'} aria-pressed={type === item.id} onClick={() => update({ type: item.id })}>{localized(item.label)}</button>)}
          </div>
          <p className="practice-keyboard-hint" id="practice-chord-keyboard">{copy.keyboard}</p>
          {results.length > 0 ? <div className="practice-chord-options" role="group" aria-labelledby="practice-choose-title" aria-describedby="practice-chord-keyboard">
            {results.map((item, index) => <button key={item.id} type="button" className="practice-chord-option"
              ref={(element) => { if (element) optionRefs.current.set(item.id, element); else optionRefs.current.delete(item.id); }}
              aria-pressed={chord.id === item.id} aria-label={copy.chooseLabel + ' ' + (item.fullName ?? item.name)}
              data-practice-chord={item.id} onClick={() => choose(item.id)} onKeyDown={(event) => onOptionKeyDown(event, index)}>
              <span className="practice-chord-name" lang="en">{item.name}</span>
              <span className="practice-chord-quality" lang="en">{item.quality}</span>
              <ChordDiagram chord={item} compact />
              <span className="practice-chord-selection-line" aria-hidden="true" />
            </button>)}
          </div> : <div className="practice-chord-empty"><h3>{copy.empty}</h3><p>{copy.emptyText}</p><button type="button" onClick={() => update({ q: '', type: '' })}>{copy.clearFilters}<span aria-hidden="true">↗</span></button></div>}
        </section>

        <div className="practice-bottom-notes">
          <div className="practice-version-note"><h2>{copy.preview}</h2><p>{copy.previewText}</p></div>
          <div className="practice-tuning-note"><p>{copy.tuning}</p><span lang="en">E <span>·</span> A <span>·</span> D <span>·</span> G <span>·</span> B <span>·</span> E</span></div>
        </div>
        <div className="practice-model-note"><div><p>{copy.modelNote}</p><p className="practice-model-credit">
          {LANG === 'en' ? 'Hand and skin: ' : 'โมเดลมือและผิว: '}
          <a href="https://www.makehumancommunity.org/content/license.html" target="_blank" rel="noreferrer">MakeHuman · CC0</a>
          {' · '}{LANG === 'en' ? 'Sleeve adapted from ' : 'แขนเสื้อดัดแปลงจาก '}
          <a href="https://static.makehumancommunity.org/assets/assetpacks/shirts02.html" target="_blank" rel="noreferrer">Elvaerwyn · CC-BY</a>
        </p></div><AppLink href="/guitars">{copy.catalog}<ArrowRightIcon size={16} /></AppLink></div>
      </div>
    </div>
  );
}
