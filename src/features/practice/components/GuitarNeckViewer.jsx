import { useEffect, useRef, useState } from 'react';
import { LANG } from '@/i18n';
import { GuitarIcon, ReturnIcon, PlusIcon } from '@/components/ui/Icons';
import { loadPracticeScene, retryFailedSceneModule } from '../loadScene';
import './viewer.css';

const TH = {
  title: 'สำรวจคอกีตาร์ 3D', hint: 'หมุนมุมมอง แล้วดูตำแหน่งคอร์ดบนคอ',
  loading: 'กำลังเตรียมคอกีตาร์ 3D…', failed: 'ยังเปิดมุมมอง 3D ไม่ได้',
  failureText: 'โหลดระบบกราฟิกไม่สำเร็จ หรืออุปกรณ์อาจไม่รองรับ WebGL 2 คุณยังดูผังคอร์ดและข้อมูลสายได้ด้านข้าง',
  retry: 'ลองโหลด 3D อีกครั้ง',
  left: 'หมุนไปทางซ้าย', right: 'หมุนไปทางขวา', zoomIn: 'ซูมเข้า', zoomOut: 'ซูมออก', reset: 'รีเซ็ตกล้อง',
  help: 'ลากเพื่อหมุน · จีบสองนิ้วเพื่อซูม · เลื่อนหน้าเว็บจากพื้นที่นอกภาพ',
  keyboard: 'คีย์บอร์ด: เลือกภาพแล้วกดลูกศรเพื่อหมุน + / − เพื่อซูม และ 0 เพื่อรีเซ็ต',
  model: 'แบบจำลองคอทั่วไป · 6 สาย · 12 เฟรต', caption: 'จุดทองคือผังหมายเลขนิ้ว ยังไม่ใช่โมเดลมือมนุษย์',
};
const EN = {
  title: 'Explore the neck in 3D', hint: 'Find your angle. See the chord positions.',
  loading: 'Preparing your 3D guitar neck…', failed: '3D view is unavailable',
  failureText: 'The graphics engine could not load, or WebGL 2 may be unavailable. The chord diagram and string information remain available.',
  retry: 'Try loading 3D again',
  left: 'Rotate left', right: 'Rotate right', zoomIn: 'Zoom in', zoomOut: 'Zoom out', reset: 'Reset camera',
  help: 'Drag to rotate · Pinch to zoom · Scroll the page outside the canvas',
  keyboard: 'Keyboard: focus the canvas, use arrows to rotate, + / − to zoom, and 0 to reset.',
  model: 'Generic study neck · 6 strings · 12 frets', caption: 'Gold markers show finger numbers, not an anatomical hand model.',
};
const copy = LANG === 'en' ? EN : TH;
// Keep UI metadata local so camera controls do not import the lazy 3D module.
const CAMERA_PRESETS = [
  { id: 'angle', th: 'มุมเริ่มต้น', en: 'Default angle' },
  { id: 'front', th: 'ด้านหน้า', en: 'Front' },
  { id: 'head', th: 'จากหัวกีตาร์', en: 'Headstock' },
  { id: 'side', th: 'ด้านข้าง', en: 'Side' },
  { id: 'back', th: 'หลังคอ', en: 'Back of neck' },
  { id: 'player', th: 'มุมผู้เล่น', en: 'Player view' },
];

export default function GuitarNeckViewer({ chord }) {
  const hostRef = useRef(null), sceneRef = useRef(null), chordRef = useRef(chord);
  const [status, setStatus] = useState('loading');
  const [attempt, setAttempt] = useState(0);
  const [view, setView] = useState('angle');
  const [moduleFailed, setModuleFailed] = useState(false);
  chordRef.current = chord;

  useEffect(() => {
    let cancelled = false;
    setStatus('loading'); setView('angle'); setModuleFailed(false);
    loadPracticeScene().then(({ createNeckScene }) => {
      if (cancelled) return;
      let failed = false;
      sceneRef.current = createNeckScene(hostRef.current, {
        chord: chordRef.current,
        canvasLabel: `${copy.title}. ${copy.keyboard}`,
        onError: () => { failed = true; if (!cancelled) setStatus('error'); },
        onInteraction: () => { if (!cancelled) setView('custom'); },
      });
      if (!failed) setStatus('ready');
    }, () => {
      if (!cancelled) { setModuleFailed(true); setStatus('error'); }
    }).catch(() => { if (!cancelled) setStatus('error'); });
    return () => { cancelled = true; sceneRef.current?.dispose(); sceneRef.current = null; };
  }, [attempt]);

  useEffect(() => { sceneRef.current?.setChord(chord); }, [chord]);
  const action = (callback) => { if (status !== 'ready') return; setView('custom'); callback(sceneRef.current); };
  const changeView = (name) => {
    if (status !== 'ready' || !sceneRef.current) return;
    sceneRef.current.preset(name); setView(name);
  };
  const retry = () => {
    if (moduleFailed) retryFailedSceneModule();
    setAttempt((value) => value + 1);
  };

  return (
    <section className="practice-viewer" data-practice-status={status} aria-labelledby="practice-viewer-title">
      <div className="practice-viewer-heading">
        <div><span className="practice-overline" lang="en">INTERACTIVE VIEW</span><h2 id="practice-viewer-title">{copy.title}</h2></div>
        <span className="practice-live-label"><i aria-hidden="true" />{status === 'ready' ? 'LIVE 3D' : '3D VIEW'}</span>
      </div>
      <div className="practice-viewer-presets" role="group" aria-label={LANG === 'en' ? 'Camera view' : 'มุมมองกล้อง'}>
        {CAMERA_PRESETS.map(({ id, th, en }) => <button type="button" key={id} data-camera-preset={id}
          disabled={status !== 'ready'} aria-pressed={view === id} onClick={() => changeView(id)}>{LANG === 'en' ? en : th}</button>)}
      </div>
      <div className="practice-canvas-stage">
        <div ref={hostRef} className="practice-canvas-host" aria-hidden={status === 'error' ? true : undefined} />
        <span className="practice-canvas-model-note">{copy.model}</span>
        {status === 'loading' && <div className="practice-scene-state" role="status" aria-live="polite">
          <GuitarIcon size={42} /><p>{copy.loading}</p><span className="practice-loading-track" aria-hidden="true" />
        </div>}
        {status === 'error' && <div className="practice-scene-state practice-scene-error" role="alert">
          <GuitarIcon size={38} /><h3>{copy.failed}</h3><p>{copy.failureText}</p>
          <button data-practice-retry type="button" onClick={retry}><ReturnIcon size={17} />{copy.retry}</button>
        </div>}
      </div>
      <div className="practice-camera-controls" role="group" aria-label={LANG === 'en' ? 'Camera controls' : 'ควบคุมกล้อง'}>
        <div>
          <button type="button" aria-label={copy.left} disabled={status !== 'ready'} onClick={() => action((api) => api.rotate(-.2))}><span aria-hidden="true">↶</span></button>
          <button type="button" aria-label={copy.right} disabled={status !== 'ready'} onClick={() => action((api) => api.rotate(.2))}><span aria-hidden="true">↷</span></button>
          <span className="practice-control-divider" aria-hidden="true" />
          <button type="button" aria-label={copy.zoomOut} disabled={status !== 'ready'} onClick={() => action((api) => api.zoom(1.18))}><span aria-hidden="true">−</span></button>
          <button type="button" aria-label={copy.zoomIn} disabled={status !== 'ready'} onClick={() => action((api) => api.zoom(.85))}><PlusIcon size={19} /></button>
        </div>
        <button className="practice-camera-reset" type="button" aria-label={copy.reset} disabled={status !== 'ready'} onClick={() => changeView('angle')}><ReturnIcon size={17} /><span>{copy.reset}</span></button>
      </div>
      <div className="practice-camera-description" id="practice-camera-help"><p>{copy.help}</p><p>{copy.keyboard}</p></div>
      <p className="practice-marker-caption">{copy.caption}</p>
    </section>
  );
}
