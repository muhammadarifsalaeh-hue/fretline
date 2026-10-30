import { LANG, t } from '@/i18n';
import { HOME_DISCOVERY_ASSETS } from '@/data/homeDiscoveryAssets';
import HomeEditorialSection from '@/components/home/HomeEditorialSection';

/** The full Compare route retains the visitor's existing selection. */
export default function CompareSection() {
  return <HomeEditorialSection
    id="compare"
    eyebrow={LANG === 'en' ? 'SIDE BY SIDE' : 'เปรียบเทียบกีตาร์'}
    title={t('signature.compare.titleLead')}
    accent={t('signature.compare.titleEnd')}
    description={LANG === 'en'
      ? 'Put 2–4 guitars side by side. See what matters to your playing.'
      : <>เลือก 2–4 รุ่น แล้ววางรายละเอียดข้างกัน<br />ดูว่าอะไรสำคัญกับการเล่นของคุณ</>}
    photo={HOME_DISCOVERY_ASSETS.compareBackdrop}
    href="/compare"
    action={t('cmpsec.start')}
  />;
}
