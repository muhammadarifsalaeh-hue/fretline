/**
 * Common open voicings in standard E A D G B E tuning.
 * Every six-value array runs from string 6 / low E to string 1 / high E.
 * frets: null = mute, 0 = open, positive integer = fret.
 * fingers: null = no fretting finger, 1 = index ... 4 = little finger.
 * Alternative valid fingerings exist; these are one consistent beginner set.
 */
const chord = (data) => Object.freeze({
  ...data,
  frets: Object.freeze(data.frets),
  fingers: Object.freeze(data.fingers),
  notes: Object.freeze(data.notes),
  // An anatomical pose is a separate, unimplemented Stage 3 asset/rig mapping.
  handPose: null,
});

export const PRACTICE_CHORDS = Object.freeze([
  chord({
    id: 'C', name: 'C', fullName: 'C Major', quality: 'Major',
    frets: [null, 3, 2, 0, 1, 0],
    fingers: [null, 3, 2, null, 1, null],
    notes: [null, 'C3', 'E3', 'G3', 'C4', 'E4'],
  }),
  chord({
    id: 'G', name: 'G', fullName: 'G Major', quality: 'Major',
    frets: [3, 2, 0, 0, 0, 3],
    fingers: [2, 1, null, null, null, 3],
    notes: ['G2', 'B2', 'D3', 'G3', 'B3', 'G4'],
  }),
  chord({
    id: 'D', name: 'D', fullName: 'D Major', quality: 'Major',
    frets: [null, null, 0, 2, 3, 2],
    fingers: [null, null, null, 1, 3, 2],
    notes: [null, null, 'D3', 'A3', 'D4', 'F#4'],
  }),
  chord({
    id: 'Em', name: 'Em', fullName: 'E Minor', quality: 'Minor',
    frets: [0, 2, 2, 0, 0, 0],
    fingers: [null, 2, 3, null, null, null],
    notes: ['E2', 'B2', 'E3', 'G3', 'B3', 'E4'],
  }),
  chord({
    id: 'Am', name: 'Am', fullName: 'A Minor', quality: 'Minor',
    frets: [null, 0, 2, 2, 1, 0],
    fingers: [null, null, 2, 3, 1, null],
    notes: [null, 'A2', 'E3', 'A3', 'C4', 'E4'],
  }),
]);

export const PRACTICE_CHORD_BY_ID = Object.freeze(
  Object.fromEntries(PRACTICE_CHORDS.map((item) => [item.id, item])),
);

export const DATA_NOTES = Object.freeze([
  'ผังคอร์ดอ่านจากสาย 6 (เสียงต่ำ) ทางซ้าย ไปยังสาย 1 (เสียงสูง) ทางขวา',
  '× คือสายที่ไม่เล่น · ○ คือสายเปิด · ตัวเลข 1–4 คือหมายเลขนิ้ว',
  'ตำแหน่งจุดบนคอเป็นผังช่วยเรียนรู้ ยังไม่ใช่โมเดลมือหรือท่าจับทางกายวิภาค',
  'คอกีตาร์นี้เป็นแบบจำลองทั่วไป ไม่ใช่สเปกของรุ่นใดในแคตตาล็อก',
]);

// General learning references only. No claim of a live page-level verification
// or copied licensed diagram: the UI draws its own diagram from the arrays above.
export const CHORD_REFERENCES = Object.freeze([
  Object.freeze({
    title: 'JustinGuitar — beginner chord learning reference',
    url: 'https://www.justinguitar.com/',
    status: 'General reference; no live verification claimed',
  }),
]);
