import { LANG } from '@/i18n';
import AppLink from '@/components/ui/AppLink';
import { DISCOVERY_PHOTOGRAPHY } from '@/data/discoveryPhotography';

export const quizCopy = (th, en) => LANG === 'en' ? en : th;

/** Lightweight editorial symbols. They are never product illustrations. */
export function QuizGlyph({ kind = 'type', size = 25 }) {
  const paths = {
    type: <><path d="m13 11 6-6m-2-2 4 4M11 10c-2-3-6-2-7 1-1 1-1 3 0 4-2 3 0 6 3 6 2 0 4-2 3-4 3-1 4-5 1-7Z" /><circle cx="8" cy="15" r="1.5" /></>,
    level: <><path d="M4 20v-4h4v4m2 0V10h4v10m2 0V4h4v16" /></>,
    style: <><path d="M9 17V5l11-2v12M9 8l11-2" /><ellipse cx="6" cy="18" rx="3" ry="2" /><ellipse cx="17" cy="16" rx="3" ry="2" /></>,
    budget: <><rect x="3" y="6" width="18" height="15" rx="2" /><path d="M3 10h18M6 6V3h12v3m-2 8h5v4h-5z" /></>,
    priority: <path d="m12 3 2.8 5.6 6.2.9-4.5 4.4 1.1 6.1-5.6-2.9L6.4 20l1.1-6.1L3 9.5l6.2-.9z" />,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.35" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[kind] ?? paths.type}</svg>;
}

export const QUIZ_CATEGORY_COPY = {
  type: { label: () => quizCopy('ประเภทกีตาร์', 'Instrument'), hint: () => quizCopy('ไฟฟ้า โปร่ง คลาสสิก หรือเบส', 'Electric, acoustic, classical or bass') },
  level: { label: () => quizCopy('ประสบการณ์', 'Experience'), hint: () => quizCopy('เริ่มต้น หรือเล่นมานานแล้ว?', 'Where are you in your playing journey?') },
  style: { label: () => quizCopy('แนวเพลง', 'Your music'), hint: () => quizCopy('ร็อก บลูส์ ป็อป และอีกมากมาย', 'Rock, blues, pop and more') },
  budget: { label: () => quizCopy('งบประมาณ', 'Your budget'), hint: () => quizCopy('เลือกช่วงราคาที่สบายใจ', 'A range that feels right for you') },
  priority: { label: () => quizCopy('สิ่งที่ให้ความสำคัญ', 'What matters'), hint: () => quizCopy('ความสบาย เสียง หรือความคุ้มค่า', 'Comfort, versatility or value') },
};

/** Real licensed editorial images, not photographs of recommended catalog models. */
export function QuizPhotoTriptych() {
  const photos = [
    ['electricPlayer', quizCopy('กีตาร์ไฟฟ้า', 'Electric expression')],
    ['acousticPlayer', quizCopy('เสียงอะคูสติก', 'Acoustic character')],
    ['chordHands', quizCopy('สัมผัสที่เป็นคุณ', 'Your own way to play')],
  ];
  return <div className="quiz-editorial-triptych" aria-label={quizCopy('ภาพบรรยากาศการเล่นกีตาร์', 'Editorial guitar playing photographs')}>
    {photos.map(([key, caption]) => {
      const photo = DISCOVERY_PHOTOGRAPHY[key];
      return <figure key={key} className={`quiz-editorial-photo is-${key}`}>
        <img src={photo.src} srcSet={photo.srcSet} sizes="(min-width: 1100px) 170px, (min-width: 700px) 20vw, 30vw" width={photo.width} height={photo.height} alt={photo.alt} loading="lazy" decoding="async" />
        <figcaption>{caption}</figcaption>
      </figure>;
    })}
  </div>;
}

export function QuizEditorialCredit() {
  return <AppLink className="quiz-editorial-credit" href="/image-credits#discovery-photography">{quizCopy('เครดิตภาพประกอบ', 'Editorial photo credits')}<span aria-hidden="true"> ↗</span></AppLink>;
}
