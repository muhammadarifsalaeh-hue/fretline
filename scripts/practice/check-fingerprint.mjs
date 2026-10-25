import assert from 'node:assert/strict';
import * as THREE from 'three';
import { createGeometryFingerprint } from '../../src/features/practice/scene/geometryFingerprint.js';
import { buildStudyGuitar } from '../../src/features/practice/scene/studyGuitar.js';
import { createFrettedStringController } from '../../src/features/practice/scene/frettedStrings.js';
import { PRACTICE_CHORD_BY_ID } from '../../src/features/practice/data/chords.js';

const model = buildStudyGuitar({ textures: false });
model.group.updateMatrixWorld(true);
const fingerprint = createGeometryFingerprint(model.group);
let count = 0;
function check(name, action) { action(); count++; console.log('PASS '+name); }
check('Repeated static/camera-only diagnostics reuse actual buffer work', () => {
  const original = fingerprint(), scans = fingerprint.bufferScans();
  const camera = new THREE.PerspectiveCamera(); camera.position.set(4, 3, 2); camera.updateMatrixWorld(true);
  for (let i = 0; i < 100; i++) assert.equal(fingerprint(), original);
  assert.equal(fingerprint.bufferScans(), scans);
});
check('World transforms invalidate the result without rescanning static buffers', () => {
  const original = fingerprint(), scans = fingerprint.bufferScans();
  model.group.position.x += 2; model.group.updateMatrixWorld(true);
  assert.notEqual(fingerprint(), original); assert.equal(fingerprint.bufferScans(), scans);
});
const mesh = model.strings[0];
check('GPU position updates and buffer replacement invalidate the cached geometry', () => {
  let original = fingerprint();
  const attribute = mesh.geometry.attributes.position;
  attribute.setY(0, attribute.getY(0)+.1); attribute.needsUpdate = true;
  assert.notEqual(fingerprint(), original); original = fingerprint();
  const replacement = attribute.clone(); replacement.setZ(0, replacement.getZ(0)+.1);
  mesh.geometry.setAttribute('position', replacement);
  assert.notEqual(fingerprint(), original);
  assert.equal(fingerprint(), createGeometryFingerprint(model.group)());
});
check('Index changes affect actual topology fingerprints with unchanged positions', () => {
  const original = fingerprint(), index = mesh.geometry.index;
  const first = index.getX(0); index.setX(0, index.getX(1)); index.setX(1, first); index.needsUpdate = true;
  assert.notEqual(fingerprint(), original);
  assert.equal(fingerprint(), createGeometryFingerprint(model.group)());
});
check('Real pressed-string replacement and open restoration invalidate correctly', () => {
  const strings = createFrettedStringController(model), before = fingerprint();
  strings.update(PRACTICE_CHORD_BY_ID.Cmaj7, true);
  assert.notEqual(fingerprint(), before);
  assert.equal(fingerprint(), createGeometryFingerprint(model.group)());
  strings.update(PRACTICE_CHORD_BY_ID.Cmaj7, false);
  assert.equal(fingerprint(), createGeometryFingerprint(model.group)());
});
check('A single Uint16 triangle is supported without 32-bit alignment assumptions', () => {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0, 1, 0, 0, 0, 1, 0], 3));
  g.setIndex(new THREE.Uint16BufferAttribute([0, 1, 2], 1));
  assert.match(createGeometryFingerprint(new THREE.Mesh(g))(), /^[a-f0-9]{8}$/);
});
console.log(`${count}/${count} geometry fingerprint regressions passed.`);
