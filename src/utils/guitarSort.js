/** เรียงตามราคา: รุ่นที่ไม่มีราคา (price = null) อยู่ท้ายเสมอ ทั้งขึ้นและลง */
export const priceCmp = (dir) => (a, b) => (a.price == null) - (b.price == null) || dir * (a.price - b.price);
/** ระยะห่างของราคา (ใช้หารุ่นใกล้เคียง) — ไม่มีราคา = ไกลที่สุด */
export const priceGap = (a, b) => (a.price == null || b.price == null ? Number.MAX_SAFE_INTEGER : Math.abs(a.price - b.price));

export const WISHLIST_SORTS = [
  { id: 'saved', label: 'Recently saved' },
  { id: 'price-asc', label: 'Price: low to high' },
  { id: 'price-desc', label: 'Price: high to low' },
  { id: 'name', label: 'Name: A to Z' },
];

/** เรียงกีตาร์ใน Wishlist (items เรียงตามลำดับที่บันทึก เก่า→ใหม่) — คืน array ใหม่ ไม่แก้ของเดิม */
export function sortGuitars(items, sort) {
  const list = [...items];
  switch (sort) {
    case 'price-asc':
      return list.sort(priceCmp(1));
    case 'price-desc':
      return list.sort(priceCmp(-1));
    case 'name':
      return list.sort((a, b) => `${a.brand} ${a.name}`.localeCompare(`${b.brand} ${b.name}`));
    default:
      return list.reverse(); // ล่าสุดก่อน
  }
}
