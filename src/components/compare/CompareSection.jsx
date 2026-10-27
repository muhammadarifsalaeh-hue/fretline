import { t } from '@/i18n';
import { HOME_DISCOVERY_ASSETS } from '@/data/homeDiscoveryAssets';
import HomeEditorialSection from '@/components/home/HomeEditorialSection';

/** The full Compare route retains the visitor's existing selection. */
export default function CompareSection() {
  return <HomeEditorialSection
    id="compare"
    eyebrow="04 / SIDE BY SIDE"
    title={t('signature.compare.titleLead')}
    accent={t('signature.compare.titleEnd')}
    description={t('signature.compare.body')}
    photo={HOME_DISCOVERY_ASSETS.compareBackdrop}
    href="/compare"
    action={t('cmpsec.start')}
  />;
}
