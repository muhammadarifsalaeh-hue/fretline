import { useEffect, useState } from 'react';
import AppLink from '@/components/ui/AppLink';
import { ArrowRightIcon } from '@/components/ui/Icons';
import { LANG } from '@/i18n';
import ChordDiagram from '@/features/practice/components/ChordDiagram';
import GuitarNeckViewer from '@/features/practice/components/GuitarNeckViewer';
import { PRACTICE_CHORDS } from '@/features/practice/data/chords';
import '@/styles/practice.css';

const COPY = {
  th: {
    docTitle: 'Guitar Practice Studio — ฝึกคอร์ด 3D | Fretline', home: 'หน้าหลัก', practice: 'ฝึกกีตาร์',
    eyebrow: 'THE ART OF YOUR FIRST CHORD', intro: 'เริ่มจากคอร์ดแรก เข้าใจทุกตำแหน่ง',
    description: 'สำรวจคอกีตาร์ 3D เลือกคอร์ดพื้นฐาน แล้วมองตำแหน่งวางนิ้วจากมุมที่ถนัด',
    stage: 'CAMERA PREVIEW', stageTitle: 'สำรวจคอกีตาร์', stageText: 'หมุน ซูม และปรับมุมมองได้จริง',
    strings: 'สาย', frets: 'เฟรต', chords: 'คอร์ดพื้นฐาน', choose: 'เลือกคอร์ด',
    chooseDescription: 'เลือกเพื่อเปลี่ยนผังและตำแหน่งบนคอกีตาร์', chooseLabel: 'เลือกคอร์ด',
    explore: 'มองใกล้ขึ้น เข้าใจมากขึ้น', exploreDescription: 'ลากเพื่อหมุน · จีบนิ้วเพื่อซูม · ใช้ปุ่มปรับมุมมองได้เช่นกัน',
    selected: 'คอร์ดที่เลือก', positioning: 'ตำแหน่งวางนิ้ว', finger: 'นิ้ว', string: 'สาย', fret: 'เฟรต',
    fingerNames: ['นิ้วชี้', 'นิ้วกลาง', 'นิ้วนาง', 'นิ้วก้อย'],
    open: 'สายเปิด', muted: 'ไม่เล่นสาย', none: 'ไม่มี', diagramView: 'ผังมองตรงเข้าหาฟิงเกอร์บอร์ด สาย 6 (E ต่ำ) อยู่ซ้าย',
    diagramLegend: 'เลขบนจุดคือหมายเลขนิ้ว · ○ สายเปิด · × ไม่เล่นสาย',
    tuning: 'การตั้งสายมาตรฐาน', preview: 'เกี่ยวกับเวอร์ชันนี้',
    previewText: 'เวอร์ชันนี้แสดงคอกีตาร์ 3D พร้อมมุมกล้อง 6 แบบ จุดทองแสดงตำแหน่งนิ้ว ยังไม่มีโมเดลมือมนุษย์ เสียงคอร์ด หรือบทเรียนทีละขั้น',
    modelNote: 'แบบจำลองเพื่อศึกษาโครงสร้างคอกีตาร์ ไม่ได้แสดงกีตาร์รุ่นใดในแคตตาล็อก',
    catalog: 'สำรวจกีตาร์ในแคตตาล็อก',
  },
  en: {
    docTitle: 'Guitar Practice Studio — 3D Chords | Fretline', home: 'Home', practice: 'Practice',
    eyebrow: 'THE ART OF YOUR FIRST CHORD', intro: 'Your first chord. Every position, understood.',
    description: 'Explore a real 3D guitar neck, choose a basic chord and see each position from your own angle.',
    stage: 'CAMERA PREVIEW', stageTitle: 'Explore the fretboard', stageText: 'Rotate, zoom and change your perspective',
    strings: 'strings', frets: 'frets', chords: 'basic chords', choose: 'Choose a chord',
    chooseDescription: 'Change the diagram and positions on the guitar neck', chooseLabel: 'Choose chord',
    explore: 'A closer look. A clearer understanding.', exploreDescription: 'Drag to rotate · Pinch to zoom · Camera buttons also available',
    selected: 'Selected chord', positioning: 'Finger positions', finger: 'Finger', string: 'String', fret: 'Fret',
    fingerNames: ['Index finger', 'Middle finger', 'Ring finger', 'Little finger'],
    open: 'Open strings', muted: 'Muted strings', none: 'None', diagramView: 'Front view of the fingerboard. String 6 (low E) is on the left.',
    diagramLegend: 'Dot numbers are fingers · ○ open string · × do not play',
    tuning: 'Standard tuning', preview: 'About this version',
    previewText: 'This version offers a 3D guitar neck and six camera views. Gold markers show finger positions. An anatomical hand model, chord audio and step-by-step lessons are not included yet.',
    modelNote: 'A generic study model of a guitar neck; it does not represent a catalog model.',
    catalog: 'Explore the guitar catalog',
  },
};

export default function PracticePage() {
  const copy = COPY[LANG] ?? COPY.th;
  const [chordId, setChordId] = useState(PRACTICE_CHORDS[0].id);
  const chord = PRACTICE_CHORDS.find((item) => item.id === chordId) ?? PRACTICE_CHORDS[0];
  const fingerings = chord.frets.flatMap((fret, index) => fret > 0 ? [{ string: 6 - index, fret, finger: chord.fingers[index] }] : []);
  const stringsFor = (value) => chord.frets.flatMap((fret, index) => fret === value ? [6 - index] : []).join(', ') || copy.none;

  useEffect(() => { document.title = copy.docTitle; }, [copy.docTitle]);

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
            <div className="practice-viewer-column"><GuitarNeckViewer chord={chord} /></div>
            <aside className="practice-chord-detail" aria-labelledby="practice-selected-title" data-practice-active-chord={chord.id}>
              <div className="practice-selected-heading"><p>{copy.selected}</p><h3 id="practice-selected-title" lang="en" aria-live="polite" aria-atomic="true">{chord.fullName ?? `${chord.name} ${chord.quality}`}</h3></div>
              <div className="practice-diagram-wrap"><ChordDiagram chord={chord} /></div>
              <p className="practice-diagram-caption">{copy.diagramView}</p>
              <div className="practice-fingering">
                <h4>{copy.positioning}</h4>
                <ul>{fingerings.map(({ string, fret, finger }) => <li key={string}>
                  <span className="practice-finger-number" aria-hidden="true">{finger}</span>
                  <span><strong>{copy.fingerNames[finger - 1] ?? `${copy.finger} ${finger}`}</strong><span>{copy.string} {string} <span aria-hidden="true">·</span> {copy.fret} {fret}</span></span>
                </li>)}</ul>
                <dl className="practice-string-status"><div><dt>{copy.open}</dt><dd>{stringsFor(0)}</dd></div><div><dt>{copy.muted}</dt><dd>{stringsFor(null)}</dd></div></dl>
              </div>
              <p className="practice-diagram-legend">{copy.diagramLegend}</p>
            </aside>
          </div>
        </section>

        <section className="practice-chord-library" aria-labelledby="practice-choose-title">
          <div className="practice-section-heading">
            <div><p className="practice-section-index" lang="en">02 / CHORD LIBRARY</p><h2 id="practice-choose-title">{copy.choose}</h2></div>
            <p>{copy.chooseDescription}</p>
          </div>
          <div className="practice-chord-options" role="group" aria-labelledby="practice-choose-title">
            {PRACTICE_CHORDS.map((item) => <button key={item.id} type="button" className="practice-chord-option"
              aria-pressed={chord.id === item.id} aria-label={`${copy.chooseLabel} ${item.fullName ?? `${item.name} ${item.quality}`}`}
              data-practice-chord={item.id} onClick={() => setChordId(item.id)}>
              <span className="practice-chord-name" lang="en">{item.name}</span>
              <span className="practice-chord-quality" lang="en">{item.quality}</span>
              <ChordDiagram chord={item} compact />
              <span className="practice-chord-selection-line" aria-hidden="true" />
            </button>)}
          </div>
        </section>

        <div className="practice-bottom-notes">
          <div className="practice-version-note"><h2>{copy.preview}</h2><p>{copy.previewText}</p></div>
          <div className="practice-tuning-note"><p>{copy.tuning}</p><span lang="en">E <span>·</span> A <span>·</span> D <span>·</span> G <span>·</span> B <span>·</span> E</span></div>
        </div>
        <div className="practice-model-note"><p>{copy.modelNote}</p><AppLink href="/guitars">{copy.catalog}<ArrowRightIcon size={16} /></AppLink></div>
      </div>
    </div>
  );
}
