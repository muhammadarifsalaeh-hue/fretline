import { LANG } from '@/i18n';
import { HOME_DISCOVERY_CREDITS } from '@/data/homeDiscoveryAssets';
import { HOME_CATEGORY_CREDITS } from '@/data/homeCategoryAssets';

const copy = (th, en) => LANG === 'en' ? en : th;

/** Home editorial/category photographs have no catalog-model substitution role. */
export default function HomePhotographyCredits() {
  return <section id="home-photography" className="mt-12 scroll-mt-28" aria-labelledby="home-photography-title">
    <h2 id="home-photography-title" className="font-serif text-3xl text-bone">{copy('ภาพถ่ายบนหน้าหลัก', 'Homepage photography')}</h2>
    <p className="mt-3 max-w-3xl text-sm leading-7 text-mute">{copy(
      'ภาพบรรยากาศและภาพหมวดกีตาร์ใช้แนะนำประเภทเครื่องดนตรี ไม่ใช่ภาพยืนยันรุ่นหรือสเปกของสินค้าที่แนะนำและเปรียบเทียบ การ์ดเปรียบเทียบยังใช้ภาพที่ผูกกับรหัสกีตาร์จริงเท่านั้น ภาพคลาสสิกและเบสบางภาพแยกพื้นหลังไว้โดยผู้เผยแพร่ต้นทางแล้ว',
      'Atmospheric and category photographs introduce instrument types. They do not establish the model or specifications of a recommendation or comparison. Comparison cards retain their registered model-specific images. Some classical and bass photographs were already isolated by their original publishers.',
    )}</p>
    <ul className="mt-6 grid gap-6 md:grid-cols-2">
      {[...HOME_DISCOVERY_CREDITS, ...HOME_CATEGORY_CREDITS].map((photo) => <li key={photo.sourceUrl} className="min-w-0 overflow-hidden rounded-xl border border-line bg-surface">
        <div className="flex h-52 items-center justify-center bg-[#080807] p-4">
          <img src={photo.src} srcSet={photo.srcSet} sizes="(min-width: 768px) 35vw, 85vw" width={photo.width} height={photo.height}
            alt={photo.alt} loading="lazy" decoding="async" className="h-full w-full object-contain" />
        </div>
        <div className="p-5 text-sm leading-7 text-mute">
          <h3 className="mb-2 font-medium text-bone">{photo.role === 'generic-category'
            ? copy('ภาพประกอบประเภทกีตาร์', 'Instrument category photograph')
            : copy('ภาพประกอบบรรยากาศ', 'Atmospheric photograph')}</h3>
          <p><a href={photo.sourceUrl} target="_blank" rel="noopener noreferrer" className="text-gold underline-offset-4 hover:underline">{photo.author}</a>
            {' · '}<a href={photo.licenseUrl} target="_blank" rel="noopener noreferrer" className="text-gold underline-offset-4 hover:underline">{photo.license}</a></p>
          <p className="mt-2 text-xs leading-6">{copy(
            'ย่อภาพตามสัดส่วนและแปลงเป็น WebP โดยเก็บความโปร่งใสของไฟล์ต้นทางไว้ ไม่มีการตัดส่วนสำคัญ สร้างภาพใหม่ หรือนำภาพไปแทนรุ่นอื่นบนการ์ดสินค้า พื้นหลังมืดและไล่สีบนหน้าหลักเป็น CSS Overlay การ์ดหมวดหมู่หมุนภาพขณะแสดงผลโดยคงสัดส่วนเดิม ไฟล์ดัดแปลงยังอยู่ภายใต้สัญญาอนุญาตที่ระบุของแต่ละภาพ',
            'Proportionally resized into WebP while preserving source transparency. No important content is cropped or generated, and these files never substitute another model on product cards. Page darkening and gradients are CSS overlays. Category cards rotate the displayed photographs while retaining their proportions. Derivatives retain each image’s stated license.',
          )}</p>
        </div>
      </li>)}
    </ul>
  </section>;
}
