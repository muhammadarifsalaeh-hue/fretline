import assert from 'node:assert/strict';
import { PRACTICE_CHORDS, PRACTICE_CHORD_BY_ID, BY_ID, CHORD_TYPES, CHORD_REFERENCES } from '../src/features/practice/data/chords.js';
import { noteToMidi, validatePracticeChord } from '../src/features/practice/data/chordValidation.js';
import {
  SCALE_LENGTH, FRET_COUNT, STRING_COUNT, STRING_SPACING, STRINGS,
  getFretPosition, getFingerPosition, getStringZ,
} from '../src/features/practice/data/fretboard.js';

let passed = 0;
let failed = 0;
function check(name, run) {
  try { run(); passed++; console.log(`PASS ${name}`); }
  catch (error) { failed++; console.error(`FAIL ${name}: ${error.message}`); }
}
const near = (actual, expected, tolerance = 1e-8) => assert.ok(
  Math.abs(actual - expected) < tolerance, `${actual} must be within ${tolerance} of ${expected}`,
);

const EXPECTED_IDS = [
  'C', 'D', 'E', 'F', 'G', 'A', 'B',
  'Cm', 'Dm', 'Em', 'Fm', 'Gm', 'Am', 'Bm',
  'C7', 'D7', 'E7', 'F7', 'G7', 'A7', 'B7',
  'Cmaj7', 'Dmaj7', 'Emaj7', 'Fmaj7', 'Gmaj7', 'Amaj7', 'Bmaj7',
  'Cm7', 'Dm7', 'Em7', 'Fm7', 'Gm7', 'Am7', 'Bm7',
  'Csus2', 'Dsus2', 'Asus2', 'Csus4', 'Dsus4', 'Esus4', 'Asus4',
];
check('Exactly 42 unique stable IDs, in six groups of seven', () => {
  assert.deepEqual(PRACTICE_CHORDS.map(({ id }) => id), EXPECTED_IDS);
  assert.equal(new Set(PRACTICE_CHORDS.map(({ id }) => id)).size, 42);
  assert.equal(Object.keys(PRACTICE_CHORD_BY_ID).length, 42);
  assert.equal(BY_ID, PRACTICE_CHORD_BY_ID);
  assert.deepEqual(CHORD_TYPES.map(({ id }) => id), ['major', 'minor', 'dominant7', 'major7', 'minor7', 'suspended']);
  for (const type of CHORD_TYPES) {
    assert.equal(PRACTICE_CHORDS.filter((chord) => chord.type === type.id).length, 7);
    assert.ok(type.label.th.length > 0 && type.label.en.length > 0);
  }
});
check('Original five chord IDs retain their open voicings and fingerings', () => {
  const originals = {
    C: ['x32010', [null, 3, 2, null, 1, null]],
    G: ['320003', [2, 1, null, null, null, 3]],
    D: ['xx0232', [null, null, null, 1, 3, 2]],
    Em: ['022000', [null, 2, 3, null, null, null]],
    Am: ['x02210', [null, null, 2, 3, 1, null]],
  };
  for (const [id, [voicing, fingers]] of Object.entries(originals)) {
    assert.equal(BY_ID[id].voicing, voicing);
    assert.deepEqual(BY_ID[id].fingers, fingers);
  }
});
check('The neck contains six standard-tuned strings and twelve study frets', () => {
  assert.equal(STRING_COUNT, 6);
  assert.equal(FRET_COUNT, 12);
  assert.deepEqual(STRINGS.map(({ number }) => number), [6, 5, 4, 3, 2, 1]);
  assert.deepEqual(STRINGS.map(({ note }) => note), ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']);
  assert.deepEqual(STRINGS.map(({ midi }) => midi), [40, 45, 50, 55, 59, 64]);
});
check('Nut is zero; octave wire divides the speaking length exactly in half', () => {
  assert.equal(getFretPosition(0), 0);
  near(getFretPosition(12), 324);
  near(getFretPosition(12, 650), 325);
  near(getFretPosition(24), 486);
});
check('Successive wires get closer by the equal-tempered semitone ratio', () => {
  const positions = Array.from({ length: FRET_COUNT + 1 }, (_, i) => getFretPosition(i));
  const gaps = positions.slice(1).map((value, i) => value - positions[i]);
  assert.ok(gaps.every((value) => value > 0));
  for (let i = 1; i < gaps.length; i++) {
    assert.ok(gaps[i] < gaps[i - 1]);
    near(gaps[i] / gaps[i - 1], 0.9438743126816935);
  }
  assert.ok(positions.at(-1) < SCALE_LENGTH);
});
check('Finger targets stay inside their fret interval; open strings have no offset', () => {
  assert.equal(getFingerPosition(0), 0);
  for (let fret = 1; fret <= FRET_COUNT; fret++) {
    assert.ok(getFingerPosition(fret) > getFretPosition(fret - 1));
    assert.ok(getFingerPosition(fret) < getFretPosition(fret));
  }
});
check('String coordinates are evenly spaced, symmetric and low-E positive', () => {
  const z = STRINGS.map((_, index) => getStringZ(index));
  assert.ok(z[0] > 0 && z.at(-1) < 0);
  for (let i = 0; i < z.length; i++) near(z[i], -z[z.length - 1 - i]);
  for (let i = 1; i < z.length; i++) near(z[i - 1] - z[i], STRING_SPACING);
});
check('Invalid fret, scale and string indices fail explicitly', () => {
  for (const value of [-1, 1.5, NaN, Infinity, '1']) assert.throws(() => getFretPosition(value), RangeError);
  for (const value of [0, -1, NaN, Infinity]) assert.throws(() => getFretPosition(1, value), RangeError);
  for (const value of [-1, 6, 1.5, NaN, '0']) assert.throws(() => getStringZ(value), RangeError);
});

for (const item of PRACTICE_CHORDS) {
  check(`${item.id}: schema, tuning, chord tones, finger and barre coherence`, () => {
    const result = validatePracticeChord(item);
    assert.equal(result.valid, true, result.errors.join(' '));
    assert.equal(PRACTICE_CHORD_BY_ID[item.id], item);
  });
}
check('Fifths are omitted only for the documented conventional open C7', () => {
  assert.deepEqual(PRACTICE_CHORDS.filter(({ omittedTones }) => omittedTones.length).map(({ id }) => id), ['C7']);
  assert.deepEqual(BY_ID.C7.omittedTones, ['G']);
  assert.equal(BY_ID.C7.voicing, 'x32310');
  assert.deepEqual(BY_ID.C7.notes, [null, 'C3', 'E3', 'Bb3', 'C4', 'E4']);
});
check('A barre correctly permits higher notes on covered strings', () => {
  assert.equal(validatePracticeChord(BY_ID.F).valid, true);
  assert.equal(validatePracticeChord(BY_ID.Csus2).valid, true);
  assert.deepEqual(BY_ID.Csus2.barres, [{ finger: 1, fret: 3, fromString: 5, toString: 1 }]);
});
check('Validator rejects wrong notes, omitted essential tones, finger reuse and blocked strings', () => {
  const invalid = [];
  const copy = (chord) => structuredClone(chord);
  let item = copy(BY_ID.C); item.notes[1] = 'B2'; invalid.push(item);
  item = copy(BY_ID.C); item.frets[3] = 1; item.notes[3] = 'G#3'; item.fingers[3] = 4; invalid.push(item);
  item = copy(BY_ID.C7); item.omittedTones = []; invalid.push(item);
  item = copy(BY_ID.Em7); item.frets[2] = 2; item.notes[2] = 'E3'; item.fingers[2] = 3; invalid.push(item);
  item = copy(BY_ID.C); item.fingers[2] = 3; invalid.push(item);
  item = copy(BY_ID.F); item.frets[2] = 0; item.notes[2] = 'D3'; item.fingers[2] = null; invalid.push(item);
  item = copy(BY_ID.Csus2); item.barres[0].fromString = 6; invalid.push(item);
  item = copy(BY_ID.C); item.frets[1] = 13; invalid.push(item);
  item = copy(BY_ID.C); item.instructions.en = []; invalid.push(item);
  item = copy(BY_ID.C); item.handPose.status = 'verified'; invalid.push(item);
  for (const bad of invalid) assert.equal(validatePracticeChord(bad).valid, false, `Invalid ${bad.id} was accepted.`);
});
check('Enharmonic note parsing preserves actual octave and rejects non-note labels', () => {
  assert.equal(noteToMidi('Bb3'), 58);
  assert.equal(noteToMidi('A#3'), 58);
  assert.equal(noteToMidi('F#4'), 66);
  assert.equal(noteToMidi('Cb4'), 59);
  assert.equal(noteToMidi('B#3'), 60);
  for (const value of [null, undefined, 123, 'H3', 'C', 'C##4', ' C4']) assert.equal(noteToMidi(value), null);
});
check('Learning references record actual read dates and specific reviewed facts', () => {
  assert.ok(CHORD_REFERENCES.length >= 6);
  assert.equal(new Set(CHORD_REFERENCES.map(({ id }) => id)).size, CHORD_REFERENCES.length);
  for (const source of CHORD_REFERENCES) {
    assert.equal(new URL(source.url).protocol, 'https:');
    assert.equal(source.retrievedAt, '2026-10-24');
    assert.equal(source.status, 'read');
    assert.ok(source.reviewedFacts.length > 20);
  }
});
check('Practice reference data cannot be accidentally mutated by viewer state', () => {
  const assertDeepFrozen = (value) => {
    if (!value || typeof value !== 'object') return;
    assert.ok(Object.isFrozen(value));
    Object.values(value).forEach(assertDeepFrozen);
  };
  for (const data of [PRACTICE_CHORDS, BY_ID, CHORD_TYPES, CHORD_REFERENCES]) assertDeepFrozen(data);
  assert.ok(Object.isFrozen(STRINGS));
  assert.throws(() => { PRACTICE_CHORDS[0].frets[1] = 99; }, TypeError);
});

console.log(`\nPractice data/geometry: ${passed} passed, ${failed} failed.`);
if (failed) process.exitCode = 1;
