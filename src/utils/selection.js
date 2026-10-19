import { GUITARS_BY_ID } from '@/data/guitars';

/** Stored/shared selections must be known, unique ids in their original order. */
export function normalizeGuitarIds(value, limit = Infinity) {
  if (!Array.isArray(value)) return [];
  return [...new Set(value.filter((id) => typeof id === 'string' && GUITARS_BY_ID[id]))].slice(0, limit);
}
