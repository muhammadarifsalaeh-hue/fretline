// Export the actual runtime guitar triangles in model-space millimetres.
// This deliberately calls the same tube/neck builders as the Practice route.
import { writeFileSync } from 'node:fs';
import { Vector3 } from 'three';
import { buildStudyGuitar } from '../../../src/features/practice/scene/studyGuitar.js';
import { createFrettedStringController } from '../../../src/features/practice/scene/frettedStrings.js';
import { PRACTICE_CHORD_BY_ID } from '../../../src/features/practice/data/chords.js';

const chordId = process.argv[2] || 'C';
const chord = PRACTICE_CHORD_BY_ID[chordId];
if (!chord) throw new Error(`Unknown chord: ${chordId}`);
const model = buildStudyGuitar({ textures: false });
createFrettedStringController(model).update(chord, true);
model.group.updateMatrixWorld(true);
const positions = [], indices = [], dominantBones = [], parts = [];
model.group.traverse((node) => {
  if (!node.isMesh) return;
  const geometry = node.geometry, attribute = geometry.attributes.position;
  const offset = positions.length, triangleStart = indices.length / 3;
  for (let i = 0; i < attribute.count; i++) {
    positions.push(new Vector3().fromBufferAttribute(attribute, i).applyMatrix4(node.matrixWorld).toArray());
    dominantBones.push(node.name);
  }
  const source = geometry.index ? Array.from(geometry.index.array) : Array.from({ length: attribute.count }, (_, i) => i);
  indices.push(...source.map((i) => i + offset));
  parts.push({ name: node.name, triangleStart, triangleCount: source.length / 3 });
});
const output = process.argv[3] || `/tmp/fretline-trainer-pose/${chordId}-actual-guitar.json`;
writeFileSync(output, JSON.stringify({ units: 'millimetres', chordId, positions, indices, dominantBones, parts }));
console.log(JSON.stringify({ output, vertices: positions.length, triangles: indices.length / 3 }));
