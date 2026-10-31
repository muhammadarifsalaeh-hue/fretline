import { LANG } from '@/i18n';
import PracticeIcon from './PracticeIcons';
export default function PracticeControlBar({ audio, ready, markersVisible, onMarkersChange, onReset }) {
  const en = LANG === 'en';
  return <div className="practice-control-bar" role="group" aria-label={en ? 'Practice controls' : 'ควบคุมการฝึก'}>
    <button type="button" className="practice-audio-main" data-practice-play onClick={audio.toggle} aria-pressed={audio.playing} aria-label={en ? audio.playing ? 'Stop chord' : 'Listen to chord' : audio.playing ? 'หยุดเสียงคอร์ด' : 'ฟังเสียงคอร์ด'}>
      <PracticeIcon name={audio.playing ? 'stop' : 'play'} /><span>{en ? audio.playing ? 'Stop' : 'Listen' : audio.playing ? 'หยุดเสียง' : 'ฟังเสียง'}</span>
    </button>
    <div className="practice-speed-control" role="group" aria-label={en ? 'Strum speed' : 'ความเร็วการดีด'}>
      <button type="button" data-practice-slower onClick={() => audio.changeRate(-1)} disabled={!audio.canSlowDown} aria-label={en ? 'Slower strum' : 'ลดความเร็วการดีด'}><PracticeIcon name="minus" size={16} /></button>
      <output aria-live="polite" data-practice-speed aria-label={en ? 'Strum speed' : 'ความเร็วการดีด'}>{audio.rate}×</output>
      <button type="button" data-practice-faster onClick={() => audio.changeRate(1)} disabled={!audio.canSpeedUp} aria-label={en ? 'Faster strum' : 'เพิ่มความเร็วการดีด'}><PracticeIcon name="plus" size={16} /></button>
    </div>
    <span className="practice-bar-separator" aria-hidden="true" />
    <button type="button" data-practice-reset onClick={onReset} disabled={!ready} aria-label={en ? 'Reset camera' : 'รีเซ็ตมุมมอง'} title={en ? 'Reset camera' : 'รีเซ็ตมุมมอง'}><PracticeIcon name="reset" /></button>
    <button type="button" data-practice-markers onClick={onMarkersChange} disabled={!ready} aria-pressed={markersVisible} aria-label={en ? 'Show finger position markers' : 'แสดงจุดบอกตำแหน่งนิ้ว'} title={en ? 'Finger positions' : 'ตำแหน่งนิ้ว'}><PracticeIcon name="eye" /></button>
  </div>;
}
