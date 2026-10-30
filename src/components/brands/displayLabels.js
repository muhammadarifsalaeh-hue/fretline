import { t } from '@/i18n';

const COUNTRY_KEYS = Object.freeze({ USA: 'targeted.country.USA', Japan: 'targeted.country.Japan' });
// Translate the label, retaining the original country value in filters/URLs.
export const countryLabel = (value) => Object.hasOwn(COUNTRY_KEYS, value) ? t(COUNTRY_KEYS[value]) : value;
