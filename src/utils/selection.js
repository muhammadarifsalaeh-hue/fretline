import { SAVED_GUITARS_BY_ID } from '@/data/guitars';

/** Preserve known active/archive IDs in saved/shared lists; reject unknown IDs. */
export function normalizeGuitarIds(value, limit = Infinity) {
  if (!Array.isArray(value)) return [];
  return [...new Set(value.filter((id) => typeof id === 'string' && SAVED_GUITARS_BY_ID[id]))].slice(0, limit);
}
