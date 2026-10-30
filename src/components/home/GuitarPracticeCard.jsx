import { LANG, t } from '@/i18n';
import { PRACTICE_CHORDS } from '@/features/practice/data/chords';
import Button from '@/components/ui/Button';
import { ArrowRightIcon, GuitarIcon } from '@/components/ui/Icons';
import practiceGuitar from '@/assets/home-practice/practice-black-gold-les-paul.jpg';

function ViewIcon() {
  return <svg width="30" height="30" viewBox="0 0 30 30" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden="true">
    <path d="m15 2 11 6v14l-11 6-11-6V8Z" /><path d="m4 8 11 6 11-6M15 14v14" />
    <path d="m9 13 3 1.6v3L9 16.5v3l3 1.6M18 16l3-1.6v6L18 22Z" />
  </svg>;
}

function StepsIcon() {
  return <svg width="30" height="30" viewBox="0 0 30 30" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" aria-hidden="true">
    <path d="M3 20h5v7H3ZM12 13h5v14h-5ZM21 4h5v23h-5Z" />
  </svg>;
}

/** Home-only gateway. The learning data, viewer and existing tools stay untouched. */
export default function GuitarPracticeCard() {
  const english = LANG === 'en';
  const features = [
    { icon: GuitarIcon, title: english ? `${PRACTICE_CHORDS.length} chords` : `${PRACTICE_CHORDS.length} คอร์ด`, detail: english ? 'Build your foundations' : 'ครบทุกพื้นฐาน' },
    { icon: ViewIcon, title: english ? '3D view' : 'มุมมอง 3D', detail: english ? 'Rotate and zoom freely' : 'หมุน ซูม ได้อิสระ' },
    { icon: StepsIcon, title: english ? 'Step by step' : 'เรียนรู้ทีละขั้น', detail: english ? 'Keep progressing' : 'พัฒนาต่อเนื่อง' },
  ];
  return <article id="home-practice" className="home-editorial home-practice-card home-practice-black-gold" data-home-practice-card aria-labelledby="home-practice-title">
    <div className="home-editorial-photo" aria-hidden="true">
      <img src={practiceGuitar} width={1061} height={1280} alt="" loading="lazy" decoding="async" />
    </div>
    <div className="home-editorial-inner">
      <div className="home-editorial-copy">
        <p className="signature-section-eyebrow">{t('targeted.home.practice')}</p>
        <h2 id="home-practice-title">{english ? 'Guitar' : 'โหมด'}<br /><span>{english ? 'Practice Studio' : 'ฝึกกีตาร์'}</span></h2>
        <p className="home-editorial-description">{english
          ? <>Practice chords with engaging guitar lessons,<br />from the basics to advanced playing.</>
          : <>ฝึกจับคอร์ด เล่นกีตาร์ไปกับบทเรียนที่สนุก<br />ตั้งแต่พื้นฐาน จนถึงขั้นสูง</>}</p>
        <ul className="home-practice-features">
          {features.map(({ icon: Icon, title, detail }) => <li key={title}>
            <Icon size={30} /><strong>{title}</strong><span>{detail}</span>
          </li>)}
        </ul>
        <Button href="/practice" size="lg" className="home-editorial-cta">{english ? 'Start practicing' : 'เริ่มฝึกกีตาร์'}<ArrowRightIcon size={19} /></Button>
      </div>
    </div>
  </article>;
}
