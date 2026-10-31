import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { LANG } from '@/i18n';
import { GuitarIcon, ReturnIcon } from '@/components/ui/Icons';
import { loadPracticeScene, retryFailedSceneModule } from '../loadScene';
import PracticeControlBar from './PracticeControlBar';
import PracticeIcon from './PracticeIcons';
import './viewer.css';

const TH = {
  title: 'สำรวจคอกีตาร์ 3D', hint: 'หมุนมุมมอง แล้วดูตำแหน่งคอร์ดบนคอ',
  loading: 'กำลังเตรียมคอกีตาร์ 3D…', failed: 'ยังเปิดมุมมอง 3D ไม่ได้',
  failureText: 'ดูตำแหน่งนิ้วจากผังคอร์ดด้านล่างได้',
  retry: 'ลองโหลด 3D อีกครั้ง',
  left: 'หมุนไปทางซ้าย', right: 'หมุนไปทางขวา', zoomIn: 'ซูมเข้า', zoomOut: 'ซูมออก', reset: 'รีเซ็ตกล้อง',
  help: 'ลากเพื่อหมุน · จีบสองนิ้วเพื่อซูม · เลื่อนหน้าเว็บจากพื้นที่นอกภาพ',
  keyboard: 'คีย์บอร์ด: เลือกภาพแล้วกดลูกศรเพื่อหมุน + / − เพื่อซูม และ 0 เพื่อรีเซ็ต',
  model: 'แบบจำลองคอทั่วไป · 6 สาย · 12 เฟรต', caption: 'จุดทองแสดงหมายเลขนิ้วบนสาย ใช้ร่วมกับผังคอร์ดด้านข้าง',
  handLoading: 'กำลังโหลดมือ…', handError: 'โหลดมือไม่สำเร็จ',
  review: 'แสดงมือ', hideReview: 'ซ่อนมือ', retryHand: 'ลองใหม่',
};
const EN = {
  title: 'Explore the neck in 3D', hint: 'Find your angle. See the chord positions.',
  loading: 'Preparing your 3D guitar neck…', failed: '3D view is unavailable',
  failureText: 'Use the chord diagram below to keep practicing.',
  retry: 'Try loading 3D again',
  left: 'Rotate left', right: 'Rotate right', zoomIn: 'Zoom in', zoomOut: 'Zoom out', reset: 'Reset camera',
  help: 'Drag to rotate · Pinch to zoom · Scroll the page outside the canvas',
  keyboard: 'Keyboard: focus the canvas, use arrows to rotate, + / − to zoom, and 0 to reset.',
  model: 'Generic study neck · 6 strings · 12 frets', caption: 'Gold markers show finger numbers on the strings. Use them with the chord diagram.',
  handLoading: 'Loading the hand…', handError: 'The hand could not load',
  review: 'Show hand', hideReview: 'Hide hand', retryHand: 'Try again',
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
  { id: 'overview', th: 'คอทั้งหมด', en: 'Full neck' },
];

export default function GuitarNeckViewer({ chord, audio, onPoseStatus }) {
  const hostRef = useRef(null), sceneRef = useRef(null), chordRef = useRef(chord), menuRef = useRef(null);
  const poseCallbackRef = useRef(onPoseStatus);
  const [status, setStatus] = useState('loading');
  const [attempt, setAttempt] = useState(0);
  const [view, setView] = useState('angle');
  const [moduleFailed, setModuleFailed] = useState(false);
  const [handState, setHandState] = useState(null);
  const [showHand, setShowHand] = useState(true);
  const [markersVisible, setMarkersVisible] = useState(true);
  const markersRef = useRef(true); markersRef.current = markersVisible;
  chordRef.current = chord;
  poseCallbackRef.current = onPoseStatus;

  useEffect(() => {
    let cancelled = false;
    const reportHand = (next) => {
      if (cancelled || next.chordId !== chordRef.current.id) return;
      setHandState(next); poseCallbackRef.current?.(next);
    };
    const reportFailure = () => {
      if (cancelled) return;
      setStatus('error');
      reportHand({ chordId: chordRef.current.id, status: 'unavailable', assetStatus: 'error', reviewMode: false,
        reason: { th: TH.failureText, en: EN.failureText } });
    };
    setStatus('loading'); setView('angle'); setModuleFailed(false);
    reportHand({ chordId: chordRef.current.id, status: 'unavailable', assetStatus: 'loading', reviewMode: false,
      reason: { th: TH.handLoading, en: EN.handLoading } });
    loadPracticeScene().then(({ createNeckScene }) => {
      if (cancelled) return;
      let failed = false;
      sceneRef.current = createNeckScene(hostRef.current, {
        chord: chordRef.current, cameraSlopeDegrees: 3, cameraFocusZ: -1.0,
        canvasLabel: `${copy.title}. ${copy.keyboard}`,
        onError: () => { failed = true; reportFailure(); },
        onInteraction: () => { if (!cancelled) setView('custom'); },
        onPoseStatus: reportHand,
      });
      if (!failed) { sceneRef.current?.setFingerMarkersVisible(markersRef.current); setStatus('ready'); }
    }, () => {
      if (!cancelled) { setModuleFailed(true); reportFailure(); }
    }).catch(reportFailure);
    return () => { cancelled = true; sceneRef.current?.dispose(); sceneRef.current = null; };
  }, [attempt]);

  useEffect(() => {
    const close = event => {
      if (!menuRef.current?.open) return;
      if (event.type === 'keydown' && event.key === 'Escape') {
        menuRef.current.open = false; menuRef.current.querySelector('summary')?.focus();
      } else if (event.type === 'pointerdown' && !menuRef.current.contains(event.target)) menuRef.current.open = false;
    };
    document.addEventListener('pointerdown', close); document.addEventListener('keydown', close);
    return () => { document.removeEventListener('pointerdown', close); document.removeEventListener('keydown', close); };
  }, []);
  useLayoutEffect(() => { sceneRef.current?.setFingerMarkersVisible(markersVisible); }, [markersVisible, status]);

  // Close the previous inspection and synchronize its rig before the next UI paint.
  useLayoutEffect(() => { sceneRef.current?.setChord(chord); }, [chord]);
  const changeView = (name) => {
    if (status !== 'ready' || !sceneRef.current) return;
    sceneRef.current.preset(name); setView(name);
    if (menuRef.current?.open) { menuRef.current.open = false; menuRef.current.querySelector('summary')?.focus({ preventScroll: true }); }
  };
  const retry = () => {
    if (moduleFailed) retryFailedSceneModule();
    setAttempt((value) => value + 1);
  };
  const currentHand = handState?.chordId === chord.id ? handState : null;
  const reviewMode = currentHand?.reviewMode === true;
  const assetStatus = currentHand?.assetStatus ?? 'loading';
  const handStatus = currentHand?.status ?? 'unavailable';
  const inspectionAllowed = currentHand?.inspectionAllowed === true;
  // Restore the original rig's inspection path without approving any pose or
  // weakening its geometry/hash gates. The preference survives chord changes;
  // rejected candidates still stay hidden inside the engine.
  useLayoutEffect(() => {
    if (status === 'ready' && assetStatus === 'ready' && handStatus === 'needs-review' && inspectionAllowed && reviewMode !== showHand) {
      sceneRef.current?.setHandReviewMode(showHand);
    }
  }, [status, assetStatus, handStatus, inspectionAllowed, reviewMode, showHand, chord.id]);

  return (
    <section className="practice-viewer" data-practice-status={status} aria-labelledby="practice-viewer-title">
      <h2 id="practice-viewer-title" className="practice-sr-only">{copy.title}</h2>
      <div className="practice-model-toolbar">
        <p><span className="practice-desktop-hint">{LANG === 'en' ? 'Drag to rotate · Scroll to zoom' : 'ลากเพื่อหมุน · เลื่อนเพื่อซูม'}</span><span className="practice-touch-hint">{LANG === 'en' ? 'Drag to rotate · Pinch to zoom' : 'ลากเพื่อหมุน · จีบเพื่อซูม'}</span></p>
        <details className="practice-camera-views" ref={menuRef}><summary>{LANG === 'en' ? 'Views' : 'มุมมอง'}<PracticeIcon name="chevron" size={14} /></summary>
          <div className="practice-viewer-presets" role="group" aria-label={LANG === 'en' ? 'Camera view' : 'มุมมองกล้อง'}>
            {CAMERA_PRESETS.filter(item => item.id !== 'angle').map(({ id, th, en }) => <button type="button" key={id} data-camera-preset={id} disabled={status !== 'ready'} aria-pressed={view === id} onClick={() => changeView(id)}>{LANG === 'en' ? en : th}</button>)}
            {assetStatus === 'ready' && handStatus === 'needs-review' && inspectionAllowed && <button type="button" className="practice-menu-hand" data-practice-hand-review aria-pressed={reviewMode} onClick={() => setShowHand(value => !value)}><PracticeIcon name="eye" size={15} />{LANG === 'en' ? '3D hand' : 'มือ 3D'}</button>}
          </div>
        </details>
      </div>
      <div className="practice-canvas-stage">
        <div ref={hostRef} className="practice-canvas-host" aria-hidden={status === 'error' ? true : undefined} />
        {status === 'loading' && <div className="practice-scene-state" role="status" aria-live="polite"><GuitarIcon size={34} /><p>{copy.loading}</p><span className="practice-loading-track" aria-hidden="true" /></div>}
        {status === 'error' && <div className="practice-scene-state practice-scene-error" role="alert"><GuitarIcon size={34} /><h3>{copy.failed}</h3><p>{copy.failureText}</p><button data-practice-retry type="button" onClick={retry}><ReturnIcon size={17} />{copy.retry}</button></div>}
      </div>
      <div className="practice-hand-state" data-hand-asset-status={assetStatus} data-hand-pose-status={handStatus} data-hand-inspection-allowed={inspectionAllowed} data-hand-display-preference={showHand}>
        {status === 'ready' && assetStatus === 'error' && <><p className="practice-hand-load-error" role="alert">{copy.handError}</p><button type="button" data-practice-hand-retry onClick={() => sceneRef.current?.retryHand()}><ReturnIcon size={16} />{copy.retryHand}</button></>}
      </div>
      <PracticeControlBar audio={audio} ready={status === 'ready'} markersVisible={markersVisible} onMarkersChange={() => setMarkersVisible(value => !value)} onReset={() => changeView('angle')} />
      {audio.error && <p className="practice-audio-error" role="alert">{LANG === 'en' ? 'Sound is unavailable. Tap Listen to try again.' : 'ยังเล่นเสียงไม่ได้ แตะฟังเสียงเพื่อลองอีกครั้ง'}</p>}
      <p className="practice-sr-only" id="practice-camera-help">{copy.keyboard}</p>
    </section>
  );
}
