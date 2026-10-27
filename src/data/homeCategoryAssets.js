// Category-only photography. Never substitute these photographs for a catalog model.
// License observations and derivative hashes: docs/home-editorial-refinement/photos/.
import { LANG } from '@/i18n';
import { HOME_DISCOVERY_ASSETS } from '@/data/homeDiscoveryAssets';
import electricSmall from '@/assets/home-categories/electric-150.webp';
import electricLarge from '@/assets/home-categories/electric-300.webp';
import acousticSmall from '@/assets/home-categories/acoustic-120.webp';
import acousticLarge from '@/assets/home-categories/acoustic-231.webp';

const photos = [
  {
    key: 'electric', src: electricLarge,
    srcSet: `${electricSmall} 150w, ${electricLarge} 300w`, width: 300, height: 800,
    altTh: 'กีตาร์ไฟฟ้าทั้งตัว', altEn: 'A complete electric guitar',
    sourceUrl: 'https://commons.wikimedia.org/wiki/File:Fender_Stratocaster_Relic_FCS_AvR.png',
    author: 'Auge=mit', license: 'CC BY-SA 4.0', licenseUrl: 'https://creativecommons.org/licenses/by-sa/4.0/',
    changes: 'Proportionally resized and converted to WebP. Original publisher transparency retained.',
  },
  {
    key: 'acoustic', src: acousticLarge,
    srcSet: `${acousticSmall} 120w, ${acousticLarge} 231w`, width: 231, height: 548,
    altTh: 'กีตาร์โปร่งสายเหล็กทั้งตัว', altEn: 'A complete steel-string acoustic guitar',
    sourceUrl: 'https://commons.wikimedia.org/wiki/File:Guitar-jeffyong.png',
    author: 'Fingerstylefreak11', license: 'CC BY-SA 3.0', licenseUrl: 'https://creativecommons.org/licenses/by-sa/3.0/',
    changes: 'Proportionally resized and converted to WebP. Original black background retained; source is 231 by 548 pixels and is not upscaled.',
  },
].map((photo) => ({ ...photo, alt: LANG === 'en' ? photo.altEn : photo.altTh,
  role: 'generic-category', kind: 'real-photograph', productEvidence: false }));

export const HOME_CATEGORY_ASSETS = {
  electric: photos[0], acoustic: photos[1],
  classical: HOME_DISCOVERY_ASSETS.classical,
  bass: HOME_DISCOVERY_ASSETS.bass,
};
export const HOME_CATEGORY_CREDITS = photos;
