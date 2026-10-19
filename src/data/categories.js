import { t } from '@/i18n';
import { GUITARS } from './guitars';
import { IMAGES } from './images';

const countOf = (id) => GUITARS.filter((g) => g.category === id).length; // จำนวนรุ่นจริงจากข้อมูลกีตาร์

export const CATEGORIES = [
  { id: 'electric', name: t('category.electric'), count: countOf('electric'), image: IMAGES.categories.electric },
  { id: 'acoustic', name: t('category.acoustic'), count: countOf('acoustic'), image: IMAGES.categories.acoustic },
  { id: 'classical', name: t('category.classical'), count: countOf('classical'), image: IMAGES.categories.classical },
  { id: 'bass', name: t('category.bass'), count: countOf('bass'), image: IMAGES.categories.bass },
];
