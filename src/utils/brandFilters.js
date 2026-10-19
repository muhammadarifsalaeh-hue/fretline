import { t } from '@/i18n';

export const BRAND_SORTS = [
  { id: 'models', label: t('p5.sort.models') },
  { id: 'name', label: t('p5.sort.name') },
  { id: 'price', label: t('p5.sort.price') },
];

const SORTERS = {
  models: (a, b) => b.models - a.models || a.name.localeCompare(b.name),
  name: (a, b) => a.name.localeCompare(b.name),
  price: (a, b) => (a.priceMin == null) - (b.priceMin == null) || a.priceMin - b.priceMin || a.name.localeCompare(b.name),
};

export const isBrandSort = (id) => Object.prototype.hasOwnProperty.call(SORTERS, id);

/** กรอง + เรียงแบรนด์: q = ชื่อแบรนด์/ประเทศ, type = มีกีตาร์ประเภทนี้, country = ประเทศ */
export function filterBrands(brands, { q = '', type = '', country = '', sort = 'models' } = {}) {
  const needle = q.trim().toLowerCase();
  return brands
    .filter((b) => !needle || `${b.name} ${b.country ?? ''}`.toLowerCase().includes(needle))
    .filter((b) => !type || b.categories.includes(type))
    .filter((b) => !country || b.country === country)
    .sort(SORTERS[isBrandSort(sort) ? sort : 'models']);
}
