// Optional per-pose pressure positions. Musical frets/fingers remain canonical.
import { getFretPosition } from '../data/fretboard.js';
export const pressureKey = (string, fret) => `${string}:${fret}`;
export function pressureContacts(chord) {
  const contacts = new Map();
  // A higher fretting finger owns the sounding contact. A barre spans below
  // it but need not press that same string again at the lower fret.
  chord.frets.forEach((fret, i) => {
    if (fret > 0) contacts.set(pressureKey(6 - i, fret), { string: 6 - i, fret, finger: chord.fingers[i] });
  });
  return [...contacts.values()];
}
export function pressureOffsetBounds(fret) {
  const gap = getFretPosition(fret) - getFretPosition(fret - 1);
  return { min: 1.5, max: Math.min(24, gap - 5) };
}
export function validatePressureOffsets(chord, offsets) {
  if (offsets === undefined) return true; // exact legacy pressure positions
  if (!chord || !offsets || Array.isArray(offsets) || typeof offsets !== 'object') return false;
  const contacts = pressureContacts(chord), keys = contacts.map(({ string, fret }) => pressureKey(string, fret));
  if (Object.keys(offsets).length !== keys.length || Object.keys(offsets).some(key => !keys.includes(key))) return false;
  return contacts.every(({ string, fret }) => {
    const value = offsets[pressureKey(string, fret)], bounds = pressureOffsetBounds(fret);
    return Number.isFinite(value) && value >= bounds.min && value <= bounds.max;
  });
}
export function pressureX(string, fret, offsets) {
  const wire = getFretPosition(fret), gap = wire - getFretPosition(fret - 1);
  return wire - (offsets?.[pressureKey(string, fret)] ?? Math.min(4, gap * .25));
}
