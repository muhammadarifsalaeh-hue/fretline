import assert from 'node:assert/strict';
import { PRACTICE_CHORDS } from '../../../src/features/practice/data/chords.js';
import { buildStudyGuitar } from '../../../src/features/practice/scene/studyGuitar.js';
import { createFrettedStringController } from '../../../src/features/practice/scene/frettedStrings.js';

// Audit the rendered tubes rather than labels or alleged contact metadata.
const model = buildStudyGuitar({ textures: false });
const controller = createFrettedStringController(model);
const original = model.strings.map((s) => Array.from(s.geometry.attributes.position.array));
let checks = 0;
for (const chord of PRACTICE_CHORDS) {
  controller.update(chord, true);
  model.strings.forEach((string, i) => {
    const number = 6 - i, radius = string.userData.radiusMm;
    const points = string.geometry.userData.centerlineSamplesMm;
    const contacts = new Set(chord.frets[i] > 0 ? [chord.frets[i]] : []);
    chord.barres.forEach((b) => { if (number <= b.fromString && number >= b.toString) contacts.add(b.fret); });
    for (const fret of contacts) {
      const x = model.surfaces.fretX(fret);
      const point = points.find((p) => Math.abs(p[0] - x) < 1e-7);
      assert.ok(point, `${chord.id} string ${number} must touch its actual fret wire`);
      const top = model.surfaces.boardTopY(point[2]);
      assert.ok(Math.abs(point[1] - radius - top - 1.025) < 1e-5);
    }
    if (!contacts.size) assert.deepEqual(Array.from(string.geometry.attributes.position.array), original[i]);
    for (const [x, y, z] of points.filter((p) => p[0] >= 0)) {
      assert.ok([x, y, z].every(Number.isFinite));
      assert.ok(y - radius - model.surfaces.boardTopY(z) > .95, `${chord.id}: string enters fingerboard`);
    }
    const anchor = model.anchors.strings[i].position;
    assert.ok(anchor.toArray().every(Number.isFinite));
    assert.ok(Math.abs(anchor.x - model.metadata.referenceStringXmm) < 1e-4);
  });
  controller.update(chord, false);
  model.strings.forEach((s, i) => assert.deepEqual(Array.from(s.geometry.attributes.position.array), original[i]));
  checks++;
}
console.log(`PASS ${checks} physical fretted-string paths, barre contacts, open-string preservation and exact restoration`);
