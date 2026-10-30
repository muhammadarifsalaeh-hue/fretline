import { t } from '@/i18n';

// Translate known provenance display text without changing stored evidence.
const MODEL_NOTES = new Map([
  ["The author identifies the instrument as a Yamaha FG820 12-string. The model label and 12 tuning machines are visible. The author states that only six strings are fitted in this photograph.", "targeted.images.modelNoteYamaha"],
  ["Author identifies Martin D-28 in the file caption. The photograph was taken on 2018-12-11; instrument production year is unknown. It illustrates the D-28 model, not the current Golden Era specification edition. No specifications are inferred from this photograph.", "targeted.images.modelNoteMartin"],
]);
export const modelMatchDisplay = (note) => MODEL_NOTES.has(note) ? t(MODEL_NOTES.get(note)) : note;
