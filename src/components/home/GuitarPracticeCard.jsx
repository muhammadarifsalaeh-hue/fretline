import { LANG } from '@/i18n';
import { DISCOVERY_PHOTOGRAPHY } from '@/data/discoveryPhotography';
import Button from '@/components/ui/Button';
import { ArrowRightIcon } from '@/components/ui/Icons';

/** One new gateway. The existing Find and Compare cards retain their components. */
export default function GuitarPracticeCard() {
  const photo = DISCOVERY_PHOTOGRAPHY.electricPlayer;
  const english = LANG === 'en';
  return <article id="home-practice" className="home-editorial home-practice-card" data-home-practice-card aria-labelledby="home-practice-title">
    <div className="home-editorial-photo" aria-hidden="true">
      <img src={photo.src} srcSet={photo.srcSet} sizes="(min-width:1024px) 55vw, 100vw"
        width={photo.width} height={photo.height} alt="" loading="lazy" decoding="async" />
    </div>
    <div className="home-editorial-inner">
      <div className="home-editorial-copy">
        <h2 id="home-practice-title">{english ? 'Guitar Practice Studio' : 'โหมดฝึกกีตาร์'}</h2>
        <p className="home-editorial-description">{english
          ? 'Practice chords and learn finger positions, from the basics to advanced playing.'
          : 'ฝึกจับคอร์ดและเรียนรู้ตำแหน่งนิ้ว ตั้งแต่พื้นฐานจนถึงขั้นสูง'}</p>
        <Button href="/practice" size="lg" className="home-editorial-cta">{english ? 'Start practicing' : 'เริ่มฝึกกีตาร์'}<ArrowRightIcon size={19} /></Button>
      </div>
    </div>
  </article>;
}
