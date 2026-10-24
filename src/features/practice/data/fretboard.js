/**
 * Generic six-string study neck. Dimensions are millimetres, not specifications
 * for a guitar in the Fretline catalog. X runs from the nut toward the body;
 * Y points out of the fingerboard; the low E string has positive Z.
 */
export const SCALE_LENGTH = 648;
export const FRET_COUNT = 12;
export const STRING_COUNT = 6;
export const STRING_SPACING = 8;

export const STRINGS = Object.freeze([
  { number: 6, note: 'E2', midi: 40 },
  { number: 5, note: 'A2', midi: 45 },
  { number: 4, note: 'D3', midi: 50 },
  { number: 3, note: 'G3', midi: 55 },
  { number: 2, note: 'B3', midi: 59 },
  { number: 1, note: 'E4', midi: 64 },
].map(Object.freeze));

/** Equal temperament: fret 12 is exactly half the speaking string length. */
export function getFretPosition(fret, scaleLength = SCALE_LENGTH) {
  if (!Number.isInteger(fret) || fret < 0) {
    throw new RangeError('Fret must be a non-negative integer.');
  }
  if (!Number.isFinite(scaleLength) || scaleLength <= 0) {
    throw new RangeError('Scale length must be a positive finite number.');
  }
  return scaleLength * (1 - 2 ** (-fret / 12));
}

/** A clear schematic target between wires, not a physical finger/hand pose. */
export function getFingerPosition(fret, scaleLength = SCALE_LENGTH) {
  const wire = getFretPosition(fret, scaleLength);
  return fret === 0 ? wire : (getFretPosition(fret - 1, scaleLength) + wire) / 2;
}

/** Index 0 is string 6 (low E); index 5 is string 1 (high E). */
export function getStringZ(index) {
  if (!Number.isInteger(index) || index < 0 || index >= STRING_COUNT) {
    throw new RangeError('String index must be an integer from 0 to 5.');
  }
  return ((STRING_COUNT - 1) / 2 - index) * STRING_SPACING;
}
