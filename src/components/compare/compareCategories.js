/** Presentation-only row filters. The catalog and comparison calculations are unchanged. */
const main = new Set(['brand', 'model', 'type', 'price', 'bodyShape', 'body', 'top', 'back', 'sides', 'neck', 'fretboard', 'pickups', 'pickupConfiguration', 'electronics', 'bridge', 'frets', 'scale', 'strings', 'weight']);
const sound = new Set(['pickups', 'controls', 'electronics', 'pickupConfiguration', 'bridgePickup', 'middlePickup', 'neckPickup', 'pickupSelector', 'connections']);
const materials = new Set(['body', 'neck', 'fretboard', 'series', 'bodyShape', 'top', 'back', 'sides', 'bodyFinish', 'neckFinish', 'bracing', 'bodyBinding', 'soundholeInlay', 'pickguard']);
const hardware = new Set(['bridge', 'tuners', 'nut', 'saddle', 'bridgePins', 'factoryStrings', 'accessories', 'case']);
const dimensions = new Set(['scale', 'frets', 'strings', 'weight', 'fingerboardRadiusMm', 'nutWidthMm', 'stringSpacingMm', 'bodyLengthMm', 'totalLengthMm', 'bodyWidthMm', 'bodyDepth']);
export const COMPARE_CATEGORIES = [
  { id: 'main', icon: 'specs', th: 'สเปกหลัก', en: 'Overview', keys: main },
  { id: 'sound', icon: 'tone', th: 'เสียง', en: 'Sound', keys: sound },
  { id: 'materials', icon: 'materials', th: 'วัสดุ', en: 'Materials', keys: materials },
  { id: 'hardware', icon: 'hardware', th: 'ฮาร์ดแวร์', en: 'Hardware', keys: hardware },
  { id: 'dimensions', icon: 'dimensions', th: 'ขนาดและน้ำหนัก', en: 'Dimensions', keys: dimensions },
  { id: 'all', icon: 'all', th: 'ทุกสเปก', en: 'All specifications', keys: null },
];
export const rowInCategory = (row, category) => {
  const group = COMPARE_CATEGORIES.find((entry) => entry.id === category);
  return !group?.keys || group.keys.has(row.key);
};
