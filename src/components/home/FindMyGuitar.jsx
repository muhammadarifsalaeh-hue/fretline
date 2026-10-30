import { LANG, t } from '@/i18n';
import { HOME_DISCOVERY_ASSETS } from '@/data/homeDiscoveryAssets';
import HomeEditorialSection from './HomeEditorialSection';

/** Home is an introduction; the existing five-step Quiz owns all answers. */
export default function FindMyGuitar() {
  return <HomeEditorialSection
    id="find"
    eyebrow={LANG === 'en' ? 'FIND MY GUITAR' : 'ค้นหากีตาร์ที่ใช่'}
    title={LANG === 'en' ? 'The right guitar.' : 'กีตาร์ที่ใช่'}
    accent={LANG === 'en' ? 'Starts with you.' : 'เริ่มจากตัวคุณ'}
    description={LANG === 'en'
      ? 'Five short questions to find a guitar that fits your style.'
      : '5 คำถามสั้น ๆ เพื่อค้นหากีตาร์ที่เข้ากับสไตล์ของคุณ'}
    photo={HOME_DISCOVERY_ASSETS.quizBackdrop}
    href="/find-my-guitar"
    action={t('signature.find.cta')}
  />;
}
