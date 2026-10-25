#!/usr/bin/env node
// Export actual runtime study-guitar triangles for independent contact audits.
import fs from 'node:fs';
import * as THREE from 'three';
import { buildStudyGuitar } from '../../src/features/practice/scene/studyGuitar.js';
import { createFrettedStringController } from '../../src/features/practice/scene/frettedStrings.js';
import { PRACTICE_CHORD_BY_ID } from '../../src/features/practice/data/chords.js';

const chordId = process.argv[2] || 'C';
const output = process.argv[3] || `/tmp/fretline-trainer-pose/guitar-${chordId}-triangles.json`;
const chord = PRACTICE_CHORD_BY_ID[chordId];
if (!chord) throw new Error(`Unknown chord: ${chordId}`);
const model = buildStudyGuitar({ textures: false });
createFrettedStringController(model).update(chord, true);
model.group.updateMatrixWorld(true);
const positions = [], indices = [], dominantBones = [];
let offset = 0;
model.group.traverse((object) => {
  if (!object.isMesh) return;
  const vertices = object.geometry.attributes.position;
  for (let i = 0; i < vertices.count; i++) {
    positions.push(new THREE.Vector3().fromBufferAttribute(vertices, i).applyMatrix4(object.matrixWorld).toArray());
    dominantBones.push(object.name);
  }
  const index = object.geometry.index;
  for (let i = 0; i < (index ? index.count : vertices.count); i++) indices.push(offset + (index ? index.getX(i) : i));
  offset += vertices.count;
});
const strings = model.strings.map((string, index) => ({
  number: 6 - index,
  radiusMm: string.userData.radiusMm,
  controlPointsMm: string.userData.activeControlPointsMm,
  centerlineSamplesMm: string.geometry.userData.centerlineSamplesMm,
}));
fs.writeFileSync(output, `${JSON.stringify({ chordId, units: 'millimetres', positions, indices, dominantBones, strings })}\n`);
console.log(JSON.stringify({ output, vertices: positions.length, triangles: indices.length / 3 }));
