/**
 * One learner voicing for each of the 42 supported chords in E A D G B E tuning.
 * Arrays: string 6 / low E → string 1 / high e. null = muted; 0 = open.
 * Fingers: null = no finger, 1–4 = index–little. Barre endpoints are inclusive
 * physical string numbers, descending 6→1. Data never certify an anatomical pose.
 */
const deepFreeze = (value) => {
  if (value && typeof value === 'object') {
    Object.values(value).forEach(deepFreeze);
    Object.freeze(value);
  }
  return value;
};

export const CHORD_TYPES = deepFreeze([
  { id: 'major', label: { th: 'เมเจอร์', en: 'Major' } },
  { id: 'minor', label: { th: 'ไมเนอร์', en: 'Minor' } },
  { id: 'dominant7', label: { th: 'โดมินันต์ 7', en: 'Dominant 7th' } },
  { id: 'major7', label: { th: 'เมเจอร์ 7', en: 'Major 7th' } },
  { id: 'minor7', label: { th: 'ไมเนอร์ 7', en: 'Minor 7th' } },
  { id: 'suspended', label: { th: 'ซัสเพนเด็ด', en: 'Suspended' } },
]);

const TUNING_MIDI = [40, 45, 50, 55, 59, 64];
const PITCH_CLASS = { C: 0, 'C#': 1, D: 2, Eb: 3, 'D#': 3, E: 4, F: 5, 'F#': 6, G: 7, Ab: 8, 'G#': 8, A: 9, Bb: 10, 'A#': 10, B: 11 };
const FINGER_NAMES = {
  en: { 1: 'index finger', 2: 'middle finger', 3: 'ring finger', 4: 'little finger' },
  th: { 1: 'นิ้วชี้', 2: 'นิ้วกลาง', 3: 'นิ้วนาง', 4: 'นิ้วก้อย' },
};
const TYPE_NAMES = Object.fromEntries(CHORD_TYPES.map(({ id, label }) => [id, label.en]));
const barre = (fret, fromString, toString, finger = 1) => ({ finger, fret, fromString, toString });

function buildInstructions(frets, fingers, barres, omittedTones) {
  const th = [];
  const en = [];
  const muted = frets.flatMap((fret, i) => fret === null ? [6 - i] : []);
  const open = frets.flatMap((fret, i) => fret === 0 ? [6 - i] : []);
  for (const item of barres) {
    th.push(`ใช้${FINGER_NAMES.th[item.finger]}ทาบเฟรต ${item.fret} ตั้งแต่สาย ${item.fromString} ถึงสาย ${item.toString}`);
    en.push(`Barre fret ${item.fret}, strings ${item.fromString} to ${item.toString}, with your ${FINGER_NAMES.en[item.finger]}.`);
  }
  frets.forEach((fret, i) => {
    if (!fret) return;
    const string = 6 - i;
    if (barres.some((item) => item.finger === fingers[i] && item.fret === fret && string <= item.fromString && string >= item.toString)) return;
    th.push(`ใช้${FINGER_NAMES.th[fingers[i]]}กดสาย ${string} ที่เฟรต ${fret}`);
    en.push(`Place your ${FINGER_NAMES.en[fingers[i]]} on string ${string}, fret ${fret}.`);
  });
  if (open.length) {
    th.push(`ปล่อยสาย ${open.join(', ')} ให้เป็นสายเปิด`);
    en.push(`Leave strings ${open.join(', ')} open.`);
  }
  if (muted.length) {
    th.push(`ไม่เล่นสาย ${muted.join(', ')}`);
    en.push(`Do not play strings ${muted.join(', ')}.`);
  }
  if (omittedTones.length) {
    th.push(`รูปจับมาตรฐานนี้ละโน้ตคู่ห้า ${omittedTones.join(', ')} แต่ยังมีรากโน้ต คู่สาม และคู่เจ็ดครบ`);
    en.push(`This conventional voicing omits the fifth (${omittedTones.join(', ')}), keeping the root, third and seventh.`);
  }
  th.push('ดีดทีละสายช้า ๆ ให้เสียงชัด หากเจ็บให้หยุดและคลายมือ');
  en.push('Pick each sounding string slowly. Relax your hand and stop if it hurts.');
  return { th, en };
}

function chord(id, type, frets, fingers, tones, barres = [], suspendedInterval = null, omittedTones = []) {
  const root = id[0];
  const quality = suspendedInterval ? `Suspended ${suspendedInterval === 2 ? '2nd' : '4th'}` : TYPE_NAMES[type];
  const notes = frets.map((fret, index) => {
    if (fret === null) return null;
    const midi = TUNING_MIDI[index] + fret;
    const pitch = tones.find((tone) => PITCH_CLASS[tone] === midi % 12);
    if (!pitch) throw new Error(`${id}: fret ${fret} on string ${6 - index} is outside the chord.`);
    return `${pitch}${Math.floor(midi / 12) - 1}`;
  });
  const positiveFrets = frets.filter((fret) => fret > 0);
  return deepFreeze({
    id, name: id, fullName: `${root} ${quality}`, quality, type, root,
    frets, fingers, notes,
    baseFret: frets.includes(0) ? 1 : Math.min(...positiveFrets),
    barres,
    voicing: frets.map((fret) => fret === null ? 'x' : fret).join(''),
    omittedTones,
    openStrings: frets.flatMap((fret, i) => fret === 0 ? [6 - i] : []),
    mutedStrings: frets.flatMap((fret, i) => fret === null ? [6 - i] : []),
    instructions: buildInstructions(frets, fingers, barres, omittedTones),
    diagramStatus: {
      status: 'verified',
      reviewedAt: '2026-10-25',
      evidence: 'docs/practice-trainer/tests/reports/chord-status-42.json',
      reason: {
        th: 'ตรวจโน้ตและการใช้นิ้วตามแหล่งเรียนรู้แล้ว พร้อมตรวจผังเต็มและผังย่อจริงครบ 42 คอร์ดใน Chromium และ WebKit แยกจากการรับรองท่ามือ',
        en: 'Notes and fingering match the learning references; full and compact diagrams were independently checked for all 42 chords in Chromium and WebKit. This does not approve the hand pose.',
      },
    },
    handPose: {
      status: 'unavailable',
      reason: {
        th: 'ยังไม่มีท่ามือทางกายวิภาคที่ผ่านการตรวจสอบอิสระสำหรับรูปจับนี้',
        en: 'An independently validated anatomical hand pose is unavailable for this voicing.',
      },
    },
  });
}

export const PRACTICE_CHORDS = deepFreeze([
  chord('C', 'major', [null, 3, 2, 0, 1, 0], [null, 3, 2, null, 1, null], ['C', 'E', 'G']),
  chord('D', 'major', [null, null, 0, 2, 3, 2], [null, null, null, 1, 3, 2], ['D', 'F#', 'A']),
  chord('E', 'major', [0, 2, 2, 1, 0, 0], [null, 2, 3, 1, null, null], ['E', 'G#', 'B']),
  chord('F', 'major', [1, 3, 3, 2, 1, 1], [1, 3, 4, 2, 1, 1], ['F', 'A', 'C'], [barre(1, 6, 1)]),
  chord('G', 'major', [3, 2, 0, 0, 0, 3], [2, 1, null, null, null, 3], ['G', 'B', 'D']),
  chord('A', 'major', [null, 0, 2, 2, 2, 0], [null, null, 2, 3, 4, null], ['A', 'C#', 'E']),
  chord('B', 'major', [null, 2, 4, 4, 4, 2], [null, 1, 2, 3, 4, 1], ['B', 'D#', 'F#'], [barre(2, 5, 1)]),

  chord('Cm', 'minor', [null, 3, 5, 5, 4, 3], [null, 1, 3, 4, 2, 1], ['C', 'Eb', 'G'], [barre(3, 5, 1)]),
  chord('Dm', 'minor', [null, null, 0, 2, 3, 1], [null, null, null, 2, 3, 1], ['D', 'F', 'A']),
  chord('Em', 'minor', [0, 2, 2, 0, 0, 0], [null, 2, 3, null, null, null], ['E', 'G', 'B']),
  chord('Fm', 'minor', [1, 3, 3, 1, 1, 1], [1, 3, 4, 1, 1, 1], ['F', 'Ab', 'C'], [barre(1, 6, 1)]),
  chord('Gm', 'minor', [3, 5, 5, 3, 3, 3], [1, 3, 4, 1, 1, 1], ['G', 'Bb', 'D'], [barre(3, 6, 1)]),
  chord('Am', 'minor', [null, 0, 2, 2, 1, 0], [null, null, 2, 3, 1, null], ['A', 'C', 'E']),
  chord('Bm', 'minor', [null, 2, 4, 4, 3, 2], [null, 1, 3, 4, 2, 1], ['B', 'D', 'F#'], [barre(2, 5, 1)]),

  // Conventional open C7 deliberately omits G, its optional fifth.
  chord('C7', 'dominant7', [null, 3, 2, 3, 1, 0], [null, 3, 2, 4, 1, null], ['C', 'E', 'G', 'Bb'], [], null, ['G']),
  chord('D7', 'dominant7', [null, null, 0, 2, 1, 2], [null, null, null, 2, 1, 3], ['D', 'F#', 'A', 'C']),
  chord('E7', 'dominant7', [0, 2, 0, 1, 0, 0], [null, 2, null, 1, null, null], ['E', 'G#', 'B', 'D']),
  chord('F7', 'dominant7', [1, 3, 1, 2, 1, 1], [1, 3, 1, 2, 1, 1], ['F', 'A', 'C', 'Eb'], [barre(1, 6, 1)]),
  chord('G7', 'dominant7', [3, 2, 0, 0, 0, 1], [3, 2, null, null, null, 1], ['G', 'B', 'D', 'F']),
  chord('A7', 'dominant7', [null, 0, 2, 0, 2, 0], [null, null, 2, null, 3, null], ['A', 'C#', 'E', 'G']),
  chord('B7', 'dominant7', [null, 2, 1, 2, 0, 2], [null, 2, 1, 3, null, 4], ['B', 'D#', 'F#', 'A']),

  chord('Cmaj7', 'major7', [null, 3, 2, 0, 0, 0], [null, 3, 2, null, null, null], ['C', 'E', 'G', 'B']),
  chord('Dmaj7', 'major7', [null, null, 0, 2, 2, 2], [null, null, null, 1, 1, 1], ['D', 'F#', 'A', 'C#'], [barre(2, 3, 1)]),
  chord('Emaj7', 'major7', [0, 2, 1, 1, 0, 0], [null, 3, 1, 2, null, null], ['E', 'G#', 'B', 'D#']),
  chord('Fmaj7', 'major7', [null, null, 3, 2, 1, 0], [null, null, 3, 2, 1, null], ['F', 'A', 'C', 'E']),
  chord('Gmaj7', 'major7', [3, 2, 0, 0, 0, 2], [3, 2, null, null, null, 1], ['G', 'B', 'D', 'F#']),
  chord('Amaj7', 'major7', [null, 0, 2, 1, 2, 0], [null, null, 2, 1, 3, null], ['A', 'C#', 'E', 'G#']),
  chord('Bmaj7', 'major7', [null, 2, 4, 3, 4, 2], [null, 1, 3, 2, 4, 1], ['B', 'D#', 'F#', 'A#'], [barre(2, 5, 1)]),

  chord('Cm7', 'minor7', [null, 3, 5, 3, 4, 3], [null, 1, 3, 1, 2, 1], ['C', 'Eb', 'G', 'Bb'], [barre(3, 5, 1)]),
  chord('Dm7', 'minor7', [null, null, 0, 2, 1, 1], [null, null, null, 2, 1, 1], ['D', 'F', 'A', 'C'], [barre(1, 2, 1)]),
  chord('Em7', 'minor7', [0, 2, 0, 0, 0, 0], [null, 2, null, null, null, null], ['E', 'G', 'B', 'D']),
  chord('Fm7', 'minor7', [1, 3, 1, 1, 1, 1], [1, 3, 1, 1, 1, 1], ['F', 'Ab', 'C', 'Eb'], [barre(1, 6, 1)]),
  chord('Gm7', 'minor7', [3, 5, 3, 3, 3, 3], [1, 3, 1, 1, 1, 1], ['G', 'Bb', 'D', 'F'], [barre(3, 6, 1)]),
  chord('Am7', 'minor7', [null, 0, 2, 0, 1, 0], [null, null, 2, null, 1, null], ['A', 'C', 'E', 'G']),
  chord('Bm7', 'minor7', [null, 2, 4, 2, 3, 2], [null, 1, 3, 1, 2, 1], ['B', 'D', 'F#', 'A'], [barre(2, 5, 1)]),

  chord('Csus2', 'suspended', [null, 3, 5, 5, 3, 3], [null, 1, 3, 4, 1, 1], ['C', 'D', 'G'], [barre(3, 5, 1)], 2),
  chord('Dsus2', 'suspended', [null, null, 0, 2, 3, 0], [null, null, null, 1, 3, null], ['D', 'E', 'A'], [], 2),
  chord('Asus2', 'suspended', [null, 0, 2, 2, 0, 0], [null, null, 2, 3, null, null], ['A', 'B', 'E'], [], 2),
  chord('Csus4', 'suspended', [null, 3, 3, 0, 1, 1], [null, 3, 4, null, 1, 1], ['C', 'F', 'G'], [barre(1, 2, 1)], 4),
  chord('Dsus4', 'suspended', [null, null, 0, 2, 3, 3], [null, null, null, 1, 3, 4], ['D', 'G', 'A'], [], 4),
  chord('Esus4', 'suspended', [0, 2, 2, 2, 0, 0], [null, 2, 3, 4, null, null], ['E', 'A', 'B'], [], 4),
  chord('Asus4', 'suspended', [null, 0, 2, 2, 3, 0], [null, null, 2, 3, 4, null], ['A', 'D', 'E'], [], 4),
]);

export const PRACTICE_CHORD_BY_ID = deepFreeze(Object.fromEntries(PRACTICE_CHORDS.map((item) => [item.id, item])));
export const BY_ID = PRACTICE_CHORD_BY_ID;

export const DATA_NOTES = deepFreeze([
  'ผังคอร์ดอ่านจากสาย 6 (เสียงต่ำ) ทางซ้าย ไปยังสาย 1 (เสียงสูง) ทางขวา',
  '× คือสายที่ไม่เล่น · ○ คือสายเปิด · ตัวเลข 1–4 คือหมายเลขนิ้ว',
  'เส้นโค้งเชื่อมจุดหมายถึงการทาบด้วยนิ้วเดียว สายที่กดเฟรตสูงกว่ายังวางอยู่เหนือการทาบได้',
  'ตำแหน่งจุดบนคอเป็นผังช่วยเรียนรู้ ยังไม่ใช่โมเดลมือหรือท่าจับทางกายวิภาค',
  'คอกีตาร์นี้เป็นแบบจำลองทั่วไป ไม่ใช่สเปกของรุ่นใดในแคตตาล็อก',
]);

/** Contents fetched/read on this date; a source read does not certify our diagrams. */
export const CHORD_REFERENCES = deepFreeze([
  { id: 'fender-major-minor', title: 'Fender — Minor vs. Major Chords', url: 'https://www.fender.com/articles/chords/minor-vs-major-chords', retrievedAt: '2026-10-24', status: 'read', reviewedFacts: 'Major 1–3–5 and minor 1–♭3–5 formulas.' },
  { id: 'fender-b7', title: 'Fender — B7 guitar chord', url: 'https://www.fender.com/articles/chords/learn-how-to-play-b7-guitar-chord', retrievedAt: '2026-10-24', status: 'read', reviewedFacts: 'B–D#–F#–A; x21202 and its four-finger placement.' },
  { id: 'fender-dm7', title: 'Fender — Dm7 guitar chord', url: 'https://www.fender.com/articles/chords/how-to-play-a-dm7-chord-on-guitar', retrievedAt: '2026-10-24', status: 'read', reviewedFacts: 'D–F–A–C; xx0211 with an index mini-barre.' },
  { id: 'fender-fmaj7', title: 'Fender — Fmaj7 guitar chord', url: 'https://www.fender.com/articles/chords/learn-how-to-play-fmaj7-guitar-chord', retrievedAt: '2026-10-24', status: 'read', reviewedFacts: 'F–A–C–E; xx3210 and ring/middle/index placements.' },
  { id: 'fender-f7', title: 'Fender — F7 guitar chord', url: 'https://www.fender.com/articles/chords/learn-how-to-play-the-f7-chord', retrievedAt: '2026-10-24', status: 'read', reviewedFacts: 'F–A–C–Eb; 131211, index barre1, ring A3, middle G2.' },
  { id: 'fender-em7', title: 'Fender — Em7 guitar chord', url: 'https://www.fender.com/articles/chords/learn-how-to-play-em7-guitar-chord', retrievedAt: '2026-10-24', status: 'read', reviewedFacts: 'E–G–B–D; 020000, middle finger on A2.' },
  { id: 'fender-sus', title: 'Fender — Suspended chords', url: 'https://www.fender.com/articles/chords/the-sus-piciously-easy-way-to-liven-up-basic-chords', retrievedAt: '2026-10-24', status: 'read', reviewedFacts: 'Suspended second/fourth replace the third; Csus2 C–D–G and Csus4 C–F–G.' },
  { id: 'guitar-chord-major7', title: 'Guitar-chord.org — Major seventh chords', url: 'https://www.guitar-chord.org/maj7.html', retrievedAt: '2026-10-24', status: 'read', reviewedFacts: '1–3–5–7 formula and movable shapes; chosen notes checked independently.' },
  { id: 'guitar-chord-dominant7', title: 'Guitar-chord.org — Seventh chords', url: 'https://www.guitar-chord.org/7.html', retrievedAt: '2026-10-24', status: 'read', reviewedFacts: '1–3–5–♭7 formula and natural-root note sets.' },
  { id: 'guitar-chord-c7', title: 'Guitar-chord.org — C7 chord', url: 'https://www.guitar-chord.org/c7.html', retrievedAt: '2026-10-24', status: 'read', reviewedFacts: 'Conventional x32310 voicing intentionally omits the fifth G.' },
  { id: 'guitar-chord-minor7', title: 'Guitar-chord.org — Minor seventh chords', url: 'https://www.guitar-chord.org/m7.html', retrievedAt: '2026-10-24', status: 'read', reviewedFacts: '1–♭3–5–♭7 formula and movable barre forms.' },
  { id: 'guitar-chord-sus2', title: 'Guitar-chord.org — Suspended second chords', url: 'https://www.guitar-chord.org/sus2-chords.html', retrievedAt: '2026-10-24', status: 'read', reviewedFacts: '1–2–5 formula; Dsus2 xx0230 and Asus2 x02200. Csus2 uses our independently checked movable shape.' },
  { id: 'guitar-chord-sus4', title: 'Guitar-chord.org — Suspended fourth chords', url: 'https://www.guitar-chord.org/sus4-chords.html', retrievedAt: '2026-10-24', status: 'read', reviewedFacts: '1–4–5 formula; Dsus4 xx0233, Esus4 022200, Asus4 x02230. Csus4 adds high F to x3301x.' },
]);
