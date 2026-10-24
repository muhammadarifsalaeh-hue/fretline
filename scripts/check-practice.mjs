import assert from 'node:assert/strict';
import { PRACTICE_CHORDS, PRACTICE_CHORD_BY_ID } from '../src/features/practice/data/chords.js';
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

check('Exactly five unique, stable chord choices in the agreed order', () => {
  assert.deepEqual(PRACTICE_CHORDS.map(({ id }) => id), ['C', 'G', 'D', 'Em', 'Am']);
  assert.equal(new Set(PRACTICE_CHORDS.map(({ id }) => id)).size, 5);
  assert.equal(Object.keys(PRACTICE_CHORD_BY_ID).length, 5);
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

const VOICINGS = { C: 'x32010', G: '320003', D: 'xx0232', Em: '022000', Am: 'x02210' };
const ROOTS = { C: 0, G: 7, D: 2, Em: 4, Am: 9 };
const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
for (const item of PRACTICE_CHORDS) {
  check(`${item.id}: real open voicing, correct notes and a complete major/minor triad`, () => {
    assert.equal(item.frets.length, 6);
    assert.equal(item.fingers.length, 6);
    assert.equal(item.notes.length, 6);
    assert.equal(item.frets.map((fret) => fret === null ? 'x' : fret).join(''), VOICINGS[item.id]);
    const actualPitchClasses = new Set();
    item.frets.forEach((fret, i) => {
      if (fret === null) {
        assert.equal(item.notes[i], null);
        assert.equal(item.fingers[i], null);
        return;
      }
      assert.ok(Number.isInteger(fret) && fret >= 0 && fret <= FRET_COUNT);
      const midi = STRINGS[i].midi + fret;
      assert.equal(item.notes[i], `${NOTE_NAMES[midi % 12]}${Math.floor(midi / 12) - 1}`);
      actualPitchClasses.add(midi % 12);
      if (fret === 0) assert.equal(item.fingers[i], null);
      else assert.ok(Number.isInteger(item.fingers[i]) && item.fingers[i] >= 1 && item.fingers[i] <= 4);
    });
    const intervals = item.quality === 'Major' ? [0, 4, 7] : [0, 3, 7];
    const expectedPitchClasses = new Set(intervals.map((interval) => (ROOTS[item.id] + interval) % 12));
    assert.deepEqual(actualPitchClasses, expectedPitchClasses);
    const activeFingers = item.fingers.filter((finger) => finger !== null);
    assert.equal(new Set(activeFingers).size, activeFingers.length, 'These open voicings must not accidentally assign one finger to separate strings.');
    assert.equal(item.handPose, null, 'Stage 1–2 must not pretend an anatomical pose is implemented.');
    assert.equal(PRACTICE_CHORD_BY_ID[item.id], item);
  });
}
check('Practice reference data cannot be accidentally mutated by viewer state', () => {
  assert.ok(Object.isFrozen(PRACTICE_CHORDS));
  assert.ok(Object.isFrozen(STRINGS));
  for (const item of PRACTICE_CHORDS) {
    assert.ok(Object.isFrozen(item) && Object.isFrozen(item.frets) && Object.isFrozen(item.fingers));
  }
  assert.throws(() => { PRACTICE_CHORDS[0].frets[1] = 99; }, TypeError);
});

console.log(`\nPractice data/geometry: ${passed} passed, ${failed} failed.`);
if (failed) process.exitCode = 1;
