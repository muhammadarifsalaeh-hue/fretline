/** Independent standard-tuning and fingering checks; no mesh or hand-pose claims. */
const TUNING = [40, 45, 50, 55, 59, 64];
const ROOTS = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
const NATURAL_NOTES = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
const INTERVALS = {
  major: [0, 4, 7], minor: [0, 3, 7], dominant7: [0, 4, 7, 10],
  major7: [0, 4, 7, 11], minor7: [0, 3, 7, 10],
};
const SUFFIXES = { major: '', minor: 'm', dominant7: '7', major7: 'maj7', minor7: 'm7' };
const isText = (value) => typeof value === 'string' && value.trim().length > 0;
const integerIn = (value, min, max) => Number.isInteger(value) && value >= min && value <= max;
const sameSet = (a, b) => a.size === b.size && [...a].every((value) => b.has(value));
const sameArray = (a, b) => Array.isArray(a) && a.length === b.length && a.every((value, i) => value === b[i]);

export function noteToMidi(note) {
  if (typeof note !== 'string') return null;
  const match = /^([A-G])([#b]?)(-?\d+)$/.exec(note);
  if (!match) return null;
  const accidental = match[2] === '#' ? 1 : match[2] === 'b' ? -1 : 0;
  return (Number(match[3]) + 1) * 12 + NATURAL_NOTES[match[1]] + accidental;
}

export function validatePracticeChord(item) {
  const errors = [];
  const require = (condition, message) => { if (!condition) errors.push(message); };
  if (!item || typeof item !== 'object') return { valid: false, errors: ['Chord must be an object.'] };
  for (const key of ['id', 'name', 'fullName', 'quality', 'type', 'root', 'voicing']) require(isText(item[key]), `${key} must contain text.`);
  require(Object.hasOwn(ROOTS, item.root), 'root must be a supported natural root.');
  let intervals = INTERVALS[item.type];
  if (item.type === 'suspended') {
    intervals = item.id === `${item.root}sus2` ? [0, 2, 7] : item.id === `${item.root}sus4` ? [0, 5, 7] : null;
    require(Boolean(intervals), 'A suspended chord ID must specify sus2 or sus4.');
  } else {
    require(Boolean(intervals), 'type must be supported.');
    require(item.id === `${item.root}${SUFFIXES[item.type]}`, 'ID must agree with its root and type.');
  }
  for (const key of ['frets', 'fingers', 'notes']) require(Array.isArray(item[key]) && item[key].length === 6, `${key} must have six low-to-high entries.`);
  if (!['frets', 'fingers', 'notes'].every((key) => Array.isArray(item[key]) && item[key].length === 6)) return { valid: false, errors };

  const pitches = new Set();
  const frettedByFinger = new Map();
  item.frets.forEach((fret, i) => {
    const finger = item.fingers[i];
    if (fret === null) {
      require(item.notes[i] === null && finger === null, `Muted string ${6 - i} must have no note or finger.`);
      return;
    }
    require(integerIn(fret, 0, 12), `String ${6 - i} fret must be an integer from 0 to 12.`);
    require(noteToMidi(item.notes[i]) === TUNING[i] + fret, `String ${6 - i} note disagrees with standard tuning and fret.`);
    pitches.add((TUNING[i] + fret) % 12);
    if (fret === 0) require(finger === null, `Open string ${6 - i} must have no finger.`);
    else {
      require(integerIn(finger, 1, 4), `Fretted string ${6 - i} needs finger 1–4.`);
      if (!frettedByFinger.has(finger)) frettedByFinger.set(finger, []);
      frettedByFinger.get(finger).push({ string: 6 - i, fret });
    }
  });

  const omissions = item.omittedTones;
  require(Array.isArray(omissions), 'omittedTones must be an explicit array.');
  const conventionalC7 = item.id === 'C7' && item.voicing === 'x32310' && sameArray(omissions, ['G']);
  require(conventionalC7 || sameArray(omissions, []), 'Only the documented conventional C7 voicing may omit its fifth G.');
  if (intervals && Object.hasOwn(ROOTS, item.root)) {
    const expected = new Set(intervals.map((interval) => (ROOTS[item.root] + interval) % 12));
    if (conventionalC7) expected.delete(7);
    require(sameSet(pitches, expected), 'Sounding notes must contain every required chord tone and no extra tones.');
  }

  const barres = Array.isArray(item.barres) ? item.barres.filter((barre) => barre && typeof barre === 'object') : [];
  require(Array.isArray(item.barres), 'barres must be an explicit array.');
  require(!Array.isArray(item.barres) || barres.length === item.barres.length, 'Every barre must be an object.');
  require(new Set(barres.map((barre) => barre.finger)).size === barres.length, 'One finger cannot make separate barres.');
  for (const barre of barres) {
    const validRange = integerIn(barre.finger, 1, 4) && integerIn(barre.fret, 1, 12)
      && integerIn(barre.fromString, 1, 6) && integerIn(barre.toString, 1, 6) && barre.fromString > barre.toString;
    require(validRange, 'A barre needs finger/fret and descending physical string endpoints.');
    if (!validRange) continue;
    for (const string of [barre.fromString, barre.toString]) {
      require(item.frets[6 - string] === barre.fret && item.fingers[6 - string] === barre.finger, 'Both barre endpoints must be sounding notes played by that finger at that fret.');
    }
    for (let string = barre.fromString; string >= barre.toString; string--) {
      const fret = item.frets[6 - string];
      const finger = item.fingers[6 - string];
      require(fret !== null && fret >= barre.fret, `Barre blocks a muted, open or lower-fretted string ${string}.`);
      require(fret === barre.fret ? finger === barre.finger : finger !== barre.finger, `String ${string} finger must agree with the barre or fret above it with another finger.`);
    }
  }
  for (const [finger, placements] of frettedByFinger) {
    require(new Set(placements.map(({ fret }) => fret)).size === 1, `Finger ${finger} cannot fret at different fret numbers.`);
    if (placements.length > 1) {
      require(barres.some((barre) => barre.finger === finger && placements.every(({ string, fret }) => fret === barre.fret && string <= barre.fromString && string >= barre.toString)), `Repeated finger ${finger} needs one coherent barre.`);
    }
  }

  const positive = item.frets.filter((fret) => fret > 0);
  const expectedBase = item.frets.includes(0) ? 1 : Math.min(...positive);
  require(integerIn(item.baseFret, 1, 12) && item.baseFret === expectedBase, 'baseFret must start the visible voicing; open shapes start at 1.');
  require(positive.length > 0 && Math.max(...positive) - Math.min(...positive) <= 4, 'The learner voicing must fit within a five-fret span.');
  require(item.voicing === item.frets.map((fret) => fret === null ? 'x' : fret).join(''), 'voicing must encode the frets.');
  require(sameArray(item.openStrings, item.frets.flatMap((fret, i) => fret === 0 ? [6 - i] : [])), 'openStrings must match the frets.');
  require(sameArray(item.mutedStrings, item.frets.flatMap((fret, i) => fret === null ? [6 - i] : [])), 'mutedStrings must match the frets.');
  for (const language of ['th', 'en']) {
    require(Array.isArray(item.instructions?.[language]) && item.instructions[language].length >= 2 && item.instructions[language].every(isText), `${language} instructions must contain useful text steps.`);
    require(isText(item.diagramStatus?.reason?.[language]), `${language} diagram status needs a reason.`);
    require(isText(item.handPose?.reason?.[language]), `${language} hand status needs a reason.`);
  }
  require(['needs-review', 'verified'].includes(item.diagramStatus?.status), 'diagramStatus must declare review status.');
  require(item.handPose?.status === 'unavailable', 'The data must not claim an implemented anatomical hand pose.');
  return { valid: errors.length === 0, errors };
}
