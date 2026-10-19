import { t } from '@/i18n';
import { trustedPrice } from './dataTrust';

/** เรียงตามราคา: รุ่นที่ไม่มีราคา (price = null) อยู่ท้ายเสมอ ทั้งขึ้นและลง */
export const priceCmp = (dir) => (a, b) => (a.price == null) - (b.price == null) || dir * (a.price - b.price);
/** ระยะห่างของราคา (ใช้หารุ่นใกล้เคียง) — ไม่มีราคา = ไกลที่สุด */
export const priceGap = (a, b) => (a.price == null || b.price == null ? Number.MAX_SAFE_INTEGER : Math.abs(a.price - b.price));

export const WISHLIST_SORTS = [
  { id: 'saved', label: t('p5.sort.saved') },
  { id: 'price-asc', label: t('p5.sort.priceAsc') },
  { id: 'price-desc', label: t('p5.sort.priceDesc') },
  { id: 'name', label: t('p5.sort.name') },
];

/** เรียงกีตาร์ใน Wishlist (items เรียงตามลำดับที่บันทึก เก่า→ใหม่) — คืน array ใหม่ ไม่แก้ของเดิม */
export function sortGuitars(items, sort, { verifiedOnly = false } = {}) {
  const list = [...items];
  const priceSorter = (dir) => verifiedOnly
    ? (a, b) => (trustedPrice(a) == null) - (trustedPrice(b) == null) || dir * (trustedPrice(a) - trustedPrice(b))
    : priceCmp(dir);
  switch (sort) {
    case 'price-asc':
      return list.sort(priceSorter(1));
    case 'price-desc':
      return list.sort(priceSorter(-1));
    case 'name':
      return list.sort((a, b) => `${a.brand} ${a.name}`.localeCompare(`${b.brand} ${b.name}`));
    default:
      return list.reverse(); // ล่าสุดก่อน
  }
}
