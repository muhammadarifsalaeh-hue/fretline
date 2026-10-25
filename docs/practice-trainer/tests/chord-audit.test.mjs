/** Independent music/playability audit; no application mutation or hand approval. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { PRACTICE_CHORDS, PRACTICE_CHORD_BY_ID } from '../../../src/features/practice/data/chords.js';

const fixture = JSON.parse(fs.readFileSync(new URL('./reference-voicings.json', import.meta.url)));
const expected = fixture.groups.flatMap(group => Object.entries(group.voicings).map(([id, frets]) => ({
  id, type: group.type, frets: [...frets].map(fret => fret === 'x' ? null : Number(fret)),
  intervals: id === 'C7' ? [0, 4, 10] : group.intervals ?? (id.endsWith('sus2') ? [0, 2, 7] : [0, 5, 7]),
})));
const sorted = values => [...new Set(values)].sort((a, b) => a - b);
const pitchValue = name => {
  const match = /^([A-G])([#b]?)(-?\d+)$/.exec(name ?? '');
  assert.ok(match, `Invalid absolute note ${name}`);
  return (Number(match[3]) + 1) * 12 + ({ C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 }[match[1]]) +
    (match[2] === '#' ? 1 : match[2] === 'b' ? -1 : 0);
};
const checks = [];
const check = (name, fn) => {
  try { const details = fn(); checks.push({ name, passed: true, ...(details ? { details } : {}) }); console.log(`PASS ${name}`); }
  catch (error) { checks.push({ name, passed: false, error: error.stack }); console.error(`FAIL ${name}: ${error.message}`); }
};

check('Exactly 42 stable unique choices in the requested family/root order', () => {
  assert.equal(expected.length, 42);
  assert.deepEqual(PRACTICE_CHORDS.map(chord => chord.id), expected.map(chord => chord.id));
  assert.equal(new Set(PRACTICE_CHORDS.map(chord => chord.id)).size, 42);
  assert.deepEqual(Object.keys(PRACTICE_CHORD_BY_ID), expected.map(chord => chord.id));
});

for (const reference of expected) {
  const chord = PRACTICE_CHORD_BY_ID[reference.id];
  check(`${reference.id}: independent reference shape and named quality`, () => {
    assert.ok(chord, `Missing ${reference.id}`);
    assert.deepEqual(chord.frets, reference.frets);
    assert.equal(chord.type, reference.type, 'Filtering metadata must match the independently named chord quality');
    assert.equal(chord.root, reference.id[0]);
    for (const key of ['frets', 'fingers', 'notes']) assert.equal(chord[key].length, 6, `${key} must describe six strings`);
    const absolute = [];
    chord.frets.forEach((fret, index) => {
      if (fret === null) {
        assert.equal(chord.fingers[index], null, `Muted string ${6-index} cannot be fingered`);
        assert.equal(chord.notes[index], null, `Muted string ${6-index} cannot sound`);
        return;
      }
      assert.ok(Number.isInteger(fret) && fret >= 0 && fret <= 12, `Invalid fret ${fret}`);
      const midi = fixture.tuningMidi[index] + fret;
      assert.equal(pitchValue(chord.notes[index]), midi, `String ${6-index} note must follow standard tuning + fret`);
      absolute.push(midi);
      if (fret === 0) assert.equal(chord.fingers[index], null, `Open string ${6-index} must remain free`);
      else assert.ok(Number.isInteger(chord.fingers[index]) && chord.fingers[index] >= 1 && chord.fingers[index] <= 4,
        `String ${6-index} needs a real left-hand finger`);
    });
    const root = fixture.roots[reference.id[0]];
    assert.deepEqual(sorted(absolute.map(midi => (midi - root + 12) % 12)), reference.intervals,
      'All required chord tones must sound without foreign tones; only documented C7 may omit the fifth');
    assert.deepEqual(chord.omittedTones ?? [], reference.id === 'C7' ? ['G'] : [], 'Only C7 has an agreed, explicit fifth omission');
    assert.equal(Math.min(...absolute) % 12, root, 'Study voicing should have the root in the bass');
    assert.deepEqual(chord.openStrings, reference.frets.flatMap((fret, index) => fret === 0 ? [6-index] : []));
    assert.deepEqual(chord.mutedStrings, reference.frets.flatMap((fret, index) => fret === null ? [6-index] : []));
    return { frets: chord.frets, soundingMidi: absolute, intervals: reference.intervals };
  });
  check(`${reference.id}: playable finger reuse, barre endpoints and clearance`, () => {
    assert.ok(chord, `Missing ${reference.id}`);
    const barres = chord.barres ?? [];
    assert.ok(Array.isArray(barres));
    const usedFingers = new Set();
    for (const barre of barres) {
      assert.ok(Number.isInteger(barre.fret) && barre.fret > 0 && barre.fret <= 12);
      assert.ok(Number.isInteger(barre.finger) && barre.finger >= 1 && barre.finger <= 4);
      assert.ok(Number.isInteger(barre.fromString) && Number.isInteger(barre.toString));
      assert.ok(barre.fromString <= 6 && barre.toString >= 1 && barre.fromString > barre.toString,
        'A barre must span at least two physical strings from low to high');
      assert.ok(!usedFingers.has(barre.finger), 'One finger cannot make disconnected barres');
      usedFingers.add(barre.finger);
      for (let string = barre.fromString; string >= barre.toString; string--) {
        const index = 6 - string;
        assert.ok(chord.frets[index] !== null && chord.frets[index] >= barre.fret,
          `Barre finger ${barre.finger} would block sounding string ${string}`);
        if (chord.frets[index] === barre.fret) assert.equal(chord.fingers[index], barre.finger,
          `Barre must supply string ${string} at its own fret`);
        else assert.notEqual(chord.fingers[index], barre.finger, 'A barre finger cannot also reach a higher fret');
      }
      for (const string of [barre.fromString, barre.toString]) {
        assert.equal(chord.frets[6-string], barre.fret, 'Barre endpoints must be actual same-fret contacts');
        assert.equal(chord.fingers[6-string], barre.finger);
      }
    }
    for (const finger of [1, 2, 3, 4]) {
      const contacts = chord.fingers.flatMap((value, index) => value === finger ? [{ string: 6-index, fret: chord.frets[index] }] : []);
      assert.ok(contacts.every(contact => contact.fret > 0), 'Fingers must not be assigned to muted/open strings');
      assert.ok(new Set(contacts.map(contact => contact.fret)).size <= 1, 'A physical finger cannot fret distinct fret numbers');
      if (contacts.length > 1) assert.ok(barres.some(barre => barre.finger === finger &&
        contacts.every(contact => barre.fret === contact.fret && contact.string <= barre.fromString && contact.string >= barre.toString)),
      `Finger ${finger} repeats on strings ${contacts.map(contact => contact.string)} without one covering barre`);
    }
    const positive = chord.frets.filter(fret => fret > 0);
    assert.ok(Math.max(...positive) - Math.min(...positive) <= 3, 'Unexplained four-plus fret stretch in study voicing');
    return { fingers: chord.fingers, barres, anatomicalHandStatus: 'Not assessed by this musical audit' };
  });
}

check('Frozen reference records and nested barre metadata cannot be changed by viewer state', () => {
  assert.ok(Object.isFrozen(PRACTICE_CHORDS) && Object.isFrozen(PRACTICE_CHORD_BY_ID));
  for (const chord of PRACTICE_CHORDS) {
    assert.ok(Object.isFrozen(chord));
    for (const key of ['frets', 'fingers', 'notes', 'barres']) assert.ok(Object.isFrozen(chord[key]), `${chord.id}.${key} not frozen`);
    for (const barre of chord.barres) assert.ok(Object.isFrozen(barre));
  }
});

const report = { date: new Date().toISOString(), scope: fixture.scope, source: fileURLToPath(new URL('../../../src/features/practice/data/chords.js', import.meta.url)),
  passed: checks.every(check => check.passed), checks, limitations: [
    'Mathematical notes and structural fingering/barre checks do not approve a rig, mesh, animation or anatomical hand pose.',
    'The independent fixture selects conventional voicings with an explicit C7 fifth omission; other musically valid alternatives exist.',
    'Reference page review, where performed, is reported separately; this test does not claim browser access to external references.',
  ] };
if (process.env.FRETLINE_QA_OUTPUT_DIR) {
  fs.mkdirSync(process.env.FRETLINE_QA_OUTPUT_DIR, { recursive: true });
  fs.writeFileSync(`${process.env.FRETLINE_QA_OUTPUT_DIR}/chord-audit.json`, `${JSON.stringify(report, null, 2)}\n`);
}
console.log(`\nIndependent chord audit: ${checks.filter(check => check.passed).length} passed, ${checks.filter(check => !check.passed).length} failed.`);
process.exitCode = report.passed ? 0 : 1;
