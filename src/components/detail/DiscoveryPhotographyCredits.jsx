import { LANG } from '@/i18n';
import { DISCOVERY_PHOTOGRAPHY } from '@/data/discoveryPhotography';

const copy = (th, en) => LANG === 'en' ? en : th;
const labels = {
  quizHero: ['หน้าปกค้นหากีตาร์ที่ใช่', 'Find My Guitar cover'],
  compareHero: ['หน้าปกเปรียบเทียบกีตาร์', 'Compare Guitars cover'],
  electricPlayer: ['การเล่นกีตาร์ไฟฟ้า', 'Electric guitar playing'],
  acousticPlayer: ['การเล่นกีตาร์โปร่ง', 'Acoustic guitar playing'],
  chordHands: ['การจับคอร์ด', 'Fretting a chord'],
};

/** Editorial atmosphere has its own attribution; it is never model-match evidence. */
export default function DiscoveryPhotographyCredits() {
  return <section id="discovery-photography" className="mt-12 scroll-mt-28" aria-labelledby="discovery-photography-title">
    <h2 id="discovery-photography-title" className="font-serif text-3xl text-bone">{copy('ภาพถ่ายสำหรับแบบทดสอบและการเปรียบเทียบ', 'Quiz & Compare photography')}</h2>
    <p className="mt-3 max-w-3xl text-sm leading-7 text-mute">{copy(
      'ภาพเหล่านี้ใช้ประกอบบรรยากาศและการเล่นกีตาร์ ไม่ใช่ภาพยืนยันรุ่น สเปก หรือภาพของกีตาร์ที่แนะนำและเลือกเปรียบเทียบ การ์ดสินค้ายังคงใช้ภาพที่ผูกกับ รหัสกีตาร์ของแต่ละรุ่น',
      'These photographs illustrate atmosphere and playing. They do not establish a catalog model, specification, recommendation or selected comparison guitar. Product cards continue to use each guitar’s own registered images.',
    )}</p>
    <ul className="mt-6 grid gap-6 md:grid-cols-2">
      {Object.entries(DISCOVERY_PHOTOGRAPHY).map(([key, photo]) => <li key={key} className="min-w-0 overflow-hidden rounded-xl border border-line bg-surface">
        <img src={photo.src} srcSet={photo.srcSet} sizes="(min-width: 768px) 45vw, 90vw" width={photo.width} height={photo.height}
          alt={photo.alt} loading="lazy" decoding="async" className="aspect-[16/9] w-full object-cover" />
        <div className="p-5 text-sm leading-7 text-mute">
          <h3 className="mb-2 font-medium text-bone">{copy(...labels[key])}</h3>
          <p><a href={photo.sourceUrl} target="_blank" rel="noopener noreferrer" className="text-gold underline-offset-4 hover:underline">{photo.author}</a>
            {' · '}<a href={photo.licenseUrl} target="_blank" rel="noopener noreferrer" className="text-gold underline-offset-4 hover:underline">{photo.license}</a></p>
          <p className="mt-2 text-xs leading-6">{copy('ย่อและแปลงเป็น WebP หลายขนาดเพื่อการแสดงผล พื้นหลังมืดและไล่สีบนหน้าเว็บเป็น CSS Overlay', 'Resized into responsive WebP files. Darkening and page gradients are CSS overlays.')}</p>
        </div>
      </li>)}
    </ul>
  </section>;
}
