import { t } from '@/i18n';
import { formatPrice } from './format';

const hasSource = (source) => {
  try {
    return ['https:', 'http:'].includes(new URL(source?.url).protocol)
      && /^\d{4}-\d{2}-\d{2}$/.test(source?.verifiedOn ?? '') && Number.isFinite(Date.parse(source.verifiedOn));
  } catch { return false; }
};

export const isSourceBacked = (guitar) => ['partial', 'verified'].includes(guitar.dataStatus) && hasSource(guitar.source);
const supports = (guitar, field) => !Array.isArray(guitar.source?.fields) || guitar.source.fields.includes(field);
export const trustedPrice = (guitar) => isSourceBacked(guitar) && supports(guitar, 'price')
  && (!Array.isArray(guitar.source?.fields) || (guitar.priceSource?.currency === 'THB' && hasSource(guitar.priceSource)))
  && Number.isFinite(guitar.price) && guitar.price > 0 ? guitar.price : null;
export const trustedWeight = (guitar) => isSourceBacked(guitar) && supports(guitar, 'specs.weightKg') && Number.isFinite(guitar.specs?.weightKg) && guitar.specs.weightKg > 0 ? guitar.specs.weightKg : null;

/** Reviews need their own verification; a verified guitar is not a verified review. */
export function verifiedRating(guitar) {
  const rating = guitar.rating;
  return rating?.verified === true && hasSource(rating.source)
    && Number.isFinite(rating.score) && rating.score >= 0 && rating.score <= 5
    && Number.isInteger(rating.count) && rating.count > 0 ? rating : null;
}

export const publicPrice = (guitar) => guitar.price != null && trustedPrice(guitar) == null
  ? t('data.priceUnverified') : formatPrice(guitar.price);
