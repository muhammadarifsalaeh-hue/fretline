import { useEffect, useLayoutEffect, useRef, useState } from 'react';
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
  model: 'แบบจำลองคอทั่วไป · 6 สาย · 12 เฟรต', caption: 'จุดทองแสดงหมายเลขนิ้วบนสาย ใช้ร่วมกับผังคอร์ดด้านข้าง',
  handLoading: 'กำลังโหลดโมเดลมือ…', handError: 'โมเดลมือโหลดไม่สำเร็จ',
  handUnavailable: 'ท่ามือยังไม่พร้อม · ใช้ผังคอร์ดและจุดทอง', handReview: 'ท่ามือรอตรวจทาน · ซ่อนไว้สำหรับการฝึก', handVerified: 'ท่ามือผ่านการตรวจทาน',
  review: 'ตรวจต้นแบบมือ (ยังไม่ใช่ท่าฝึก)', hideReview: 'ปิดต้นแบบมือ กลับไปดูผัง', retryHand: 'ลองโหลดโมเดลมืออีกครั้ง',
  reviewWarning: 'ต้นแบบรอตรวจทาน — ห้ามใช้ฝึกตาม', reviewDetail: 'กำลังแสดงท่าทดลองเพื่อตรวจโมเดล ตำแหน่งนิ้วและการชนอาจยังผิด ใช้ผังคอร์ดสำหรับการฝึก',
};
const EN = {
  title: 'Explore the neck in 3D', hint: 'Find your angle. See the chord positions.',
  loading: 'Preparing your 3D guitar neck…', failed: '3D view is unavailable',
  failureText: 'The graphics engine could not load, or WebGL 2 may be unavailable. The chord diagram and string information remain available.',
  retry: 'Try loading 3D again',
  left: 'Rotate left', right: 'Rotate right', zoomIn: 'Zoom in', zoomOut: 'Zoom out', reset: 'Reset camera',
  help: 'Drag to rotate · Pinch to zoom · Scroll the page outside the canvas',
  keyboard: 'Keyboard: focus the canvas, use arrows to rotate, + / − to zoom, and 0 to reset.',
  model: 'Generic study neck · 6 strings · 12 frets', caption: 'Gold markers show finger numbers on the strings. Use them with the chord diagram.',
  handLoading: 'Loading the hand model…', handError: 'The hand model could not load',
  handUnavailable: 'Hand pose unavailable · use the diagram and gold markers', handReview: 'Hand pose needs review · hidden for practice', handVerified: 'Reviewed hand pose',
  review: 'Inspect prototype hand (not a practice pose)', hideReview: 'Hide the prototype hand', retryHand: 'Try loading the hand model again',
  reviewWarning: 'UNREVIEWED PROTOTYPE — DO NOT USE FOR PRACTICE', reviewDetail: 'This experimental pose is shown for inspection. Finger contact and collisions may be incorrect. Use the chord diagram for practice.',
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

export default function GuitarNeckViewer({ chord, onPoseStatus }) {
  const hostRef = useRef(null), sceneRef = useRef(null), chordRef = useRef(chord);
  const poseCallbackRef = useRef(onPoseStatus);
  const [status, setStatus] = useState('loading');
  const [attempt, setAttempt] = useState(0);
  const [view, setView] = useState('angle');
  const [moduleFailed, setModuleFailed] = useState(false);
  const [handState, setHandState] = useState(null);
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
        chord: chordRef.current,
        canvasLabel: `${copy.title}. ${copy.keyboard}`,
        onError: () => { failed = true; reportFailure(); },
        onInteraction: () => { if (!cancelled) setView('custom'); },
        onPoseStatus: reportHand,
      });
      if (!failed) setStatus('ready');
    }, () => {
      if (!cancelled) { setModuleFailed(true); reportFailure(); }
    }).catch(reportFailure);
    return () => { cancelled = true; sceneRef.current?.dispose(); sceneRef.current = null; };
  }, [attempt]);

  // Close the previous inspection and synchronize its rig before the next UI paint.
  useLayoutEffect(() => { sceneRef.current?.setChord(chord); }, [chord]);
  const action = (callback) => { if (status !== 'ready' || !sceneRef.current) return; setView('custom'); callback(sceneRef.current); };
  const changeView = (name) => {
    if (status !== 'ready' || !sceneRef.current) return;
    sceneRef.current.preset(name); setView(name);
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
  const reviewing = reviewMode && inspectionAllowed && handStatus === 'needs-review' && assetStatus === 'ready';
  const handMessage = assetStatus === 'loading' ? copy.handLoading : assetStatus === 'error' ? copy.handError
    : handStatus === 'verified' ? copy.handVerified : handStatus === 'needs-review' && inspectionAllowed ? copy.handReview : copy.handUnavailable;
  const handReason = currentHand?.reason?.[LANG] || currentHand?.reason?.en;
  const toggleReview = () => {
    if (status === 'ready' && assetStatus === 'ready' && handStatus === 'needs-review' && inspectionAllowed) sceneRef.current?.setHandReviewMode(!reviewMode);
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
        {reviewing && <div className="practice-hand-review-warning" role="status" data-hand-review-warning>
          <strong>{copy.reviewWarning}</strong><span>{copy.reviewDetail}</span>
        </div>}
        {status === 'loading' && <div className="practice-scene-state" role="status" aria-live="polite">
          <GuitarIcon size={42} /><p>{copy.loading}</p><span className="practice-loading-track" aria-hidden="true" />
        </div>}
        {status === 'error' && <div className="practice-scene-state practice-scene-error" role="alert">
          <GuitarIcon size={38} /><h3>{copy.failed}</h3><p>{copy.failureText}</p>
          <button data-practice-retry type="button" onClick={retry}><ReturnIcon size={17} />{copy.retry}</button>
        </div>}
      </div>
      {status === 'ready' && <div className="practice-hand-state" data-hand-asset-status={assetStatus} data-hand-pose-status={handStatus} data-hand-inspection-allowed={inspectionAllowed}>
        <div aria-live="polite" aria-atomic="true"><strong>{reviewing ? copy.reviewWarning : handMessage}</strong>{handReason && <p>{handReason}</p>}</div>
        {assetStatus === 'error' && <button type="button" data-practice-hand-retry onClick={() => sceneRef.current?.retryHand()}><ReturnIcon size={16} />{copy.retryHand}</button>}
        {assetStatus === 'ready' && handStatus === 'needs-review' && inspectionAllowed && <button type="button" data-practice-hand-review aria-pressed={reviewMode} onClick={toggleReview}>{reviewMode ? copy.hideReview : copy.review}</button>}
      </div>}
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
