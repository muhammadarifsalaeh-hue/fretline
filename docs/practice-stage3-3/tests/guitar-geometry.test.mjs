import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import * as THREE from 'three';
import {
  buildStudyGuitar, STRING_DIAMETERS_MM, STRING_NOTES, fretX,
  boardTopY, widthAtX, neckBackY, stringZ, openStringCenterY,
} from '../../../src/features/practice/scene/studyGuitar.js';

// Run: node docs/practice-stage3-3/tests/guitar-geometry.test.mjs
// CPU geometry only; this never constructs WebGL, a DOM, textures, or a hand.
const model = buildStudyGuitar({ textures: false });
const checks = [];
const near = (actual, expected, epsilon = 1e-5) => assert.ok(
  Math.abs(actual - expected) < epsilon, `${actual} differs from ${expected}`,
);
const check = (name, run) => { run(); checks.push({ name, passed: true }); };

check('Six actual open-string meshes retain standard numbering, notes, and decreasing gauges', () => {
  assert.deepEqual(model.strings.map((string) => string.userData.number), [6, 5, 4, 3, 2, 1]);
  assert.deepEqual(STRING_NOTES, ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']);
  assert.deepEqual(model.strings.map((string) => string.userData.note), STRING_NOTES);
  assert.deepEqual(STRING_DIAMETERS_MM, [1.32, .91, .66, .46, .33, .25]);
  model.strings.forEach((string, index) => {
    assert.equal(string.isMesh, true);
    assert.equal(string.userData.open, true);
    near(string.userData.radiusMm, STRING_DIAMETERS_MM[index] / 2);
    if (index) assert.ok(string.userData.radiusMm < model.strings[index - 1].userData.radiusMm);
  });
});

check('Every actual board-side tube ring follows the unpressed nut-to-end string path', () => {
  for (const string of model.strings) {
    const { centerlineSamplesMm, radialSegments } = string.geometry.userData;
    const positions = string.geometry.attributes.position;
    assert.equal(positions.count, centerlineSamplesMm.length * radialSegments);
    assert.ok(centerlineSamplesMm.filter(([x]) => x >= 0).length > 40);
    for (let ring = 0; ring < centerlineSamplesMm.length; ring++) {
      if (centerlineSamplesMm[ring][0] < 0) continue;
      const vertices = Array.from({ length: radialSegments }, (_, column) => new THREE.Vector3()
        .fromBufferAttribute(positions, ring * radialSegments + column));
      const center = vertices.reduce((sum, vertex) => sum.add(vertex), new THREE.Vector3()).divideScalar(radialSegments);
      near(center.x, centerlineSamplesMm[ring][0], 3e-5);
      near(center.y, openStringCenterY(center.x, string.userData.number));
      near(center.z, stringZ(string.userData.number, center.x));
      vertices.forEach((vertex) => near(vertex.distanceTo(center), string.userData.radiusMm, 3e-5));
    }
  }
  assert.equal(model.metadata.openStringModel, true);
  assert.equal(model.metadata.anatomicalHandIncluded, false);
});

check('Projection anchors and radii come from actual tube rings on the open string paths', () => {
  assert.equal(model.anchors.strings.length, 6);
  model.strings.forEach((string, index) => {
    const anchor = model.anchors.strings[index];
    const { centerlineSamplesMm, radialSegments } = string.geometry.userData;
    const ring = centerlineSamplesMm.findIndex(([x]) => Math.abs(x - model.metadata.referenceStringXmm) < 1e-7);
    assert.ok(ring >= 0, string.name);
    const center = new THREE.Vector3();
    const vertices = Array.from({ length: radialSegments }, (_, column) => new THREE.Vector3()
      .fromBufferAttribute(string.geometry.attributes.position, ring * radialSegments + column));
    vertices.forEach((vertex) => center.add(vertex));
    center.divideScalar(radialSegments);
    assert.ok(center.distanceTo(anchor.position) < 1e-10);
    near(anchor.position.x, model.metadata.referenceStringXmm);
    near(anchor.position.y, openStringCenterY(anchor.position.x, anchor.number));
    near(anchor.position.z, stringZ(anchor.number, anchor.position.x));
    vertices.forEach((vertex) => near(vertex.distanceTo(center), anchor.radiusMm));
    assert.equal(anchor.number, string.userData.number);
    assert.equal(anchor.note, string.userData.note);
  });
});

check('Twelve actual fret crowns follow equal temperament, with fret 12 at half scale', () => {
  near(fretX(12), 324);
  let previousGap;
  for (let fret = 1; fret <= 12; fret++) {
    const mesh = model.group.getObjectByName(`fret-${fret}`);
    assert.ok(mesh?.isMesh);
    const box = new THREE.Box3().setFromObject(mesh);
    near((box.min.x + box.max.x) / 2, fretX(fret));
    const gap = fretX(fret) - fretX(fret - 1);
    if (previousGap !== undefined) near(gap / previousGap, 2 ** (-1 / 12));
    previousGap = gap;
  }
});

check('Fingerboard taper and curved D-back retain their declared physical dimensions', () => {
  near(widthAtX(0), 43);
  near(widthAtX(324), 54);
  for (const x of [0, 36, 71, 103, 200, 324]) {
    near(neckBackY(x, 0), -21);
    for (const fraction of [-1, -.6, 0, .6, 1]) {
      const z = widthAtX(x) / 2 * fraction;
      near(neckBackY(x, z), boardTopY(z) - 5 - 16 * Math.sqrt(Math.max(0, 1 - fraction * fraction)));
    }
  }
});

let minimumFretClearance = Infinity;
check('All six open strings clear all twelve fret crowns across their full 2.2 mm width', () => {
  for (let number = 1; number <= 6; number++) {
    for (let fret = 1; fret <= 12; fret++) {
      for (let sample = 0; sample <= 200; sample++) {
        const dx = -1.1 + 2.2 * sample / 200;
        const x = fretX(fret) + dx, z = stringZ(number, x);
        const crown = boardTopY(z) + .5 + .5 * Math.sqrt(Math.max(0, 1 - (dx / 1.1) ** 2));
        const clearance = openStringCenterY(x, number) - STRING_DIAMETERS_MM[6 - number] / 2 - crown;
        minimumFretClearance = Math.min(minimumFretClearance, clearance);
        assert.ok(clearance > .05, `string ${number}, fret ${fret}, sample ${sample}: ${clearance} mm`);
      }
    }
  }
});

check('Actual nut groove vertices meet each corresponding string bottom', () => {
  const positions = model.group.getObjectByName('grooved-nut').geometry.attributes.position;
  for (let number = 1; number <= 6; number++) {
    const z = stringZ(number, 0), tops = [];
    for (let index = 0; index < positions.count; index++) {
      if (Math.abs(positions.getX(index)) < 1e-5 && Math.abs(positions.getZ(index) - z) < 1e-5 && positions.getY(index) > 0) {
        tops.push(positions.getY(index));
      }
    }
    assert.ok(tops.length);
    near(Math.min(...tops), openStringCenterY(0, number) - STRING_DIAMETERS_MM[6 - number] / 2);
  }
});

check('The 14 degree headstock has six separate complete tuning machines in a 3+3 arrangement', () => {
  near(model.headstock.rotation.z, 14 * Math.PI / 180);
  const tuners = model.headstock.children.filter((object) => /^tuner-/.test(object.name));
  assert.equal(tuners.length, 6);
  for (const tuner of tuners) {
    for (const part of ['tuner-housing', 'tuner-post', 'tuner-button', 'tuner-shaft', 'tuner-washer']) {
      assert.ok(tuner.getObjectByName(part)?.isMesh, `${tuner.name}: ${part}`);
    }
  }
  assert.equal(tuners.filter((tuner) => tuner.position.z > 0).length, 3);
  assert.equal(tuners.filter((tuner) => tuner.position.z < 0).length, 3);
});

check('The visible headstock veneer faces outward with a FrontSide material', () => {
  const veneer = model.headstock.getObjectByName('headstock-veneer');
  assert.equal(veneer.material.side, THREE.FrontSide);
  const normals = veneer.geometry.attributes.normal;
  for (let index = 0; index < normals.count; index++) assert.ok(normals.getY(index) > .999);
});

check('Board top, D-back and fret crown surface normals face outward', () => {
  for (const [name, surface, sign] of [
    ['curved-fingerboard', 'board', 1], ['d-section-neck-back', 'back', -1], ['fret-2', 'crown', 1],
  ]) {
    const { position, normal } = model.group.getObjectByName(name).geometry.attributes;
    const samples = [];
    for (let index = 0; index < position.count; index++) {
      const x = position.getX(index), y = position.getY(index), z = position.getZ(index);
      if (surface === 'board' && x > 20 && x < 300 && Math.abs(z) < 15 && Math.abs(y - boardTopY(z)) < 1e-4) samples.push(normal.getY(index));
      if (surface === 'back' && x > 20 && x < 300 && Math.abs(z) < 1 && y < -20.5) samples.push(normal.getY(index));
      if (surface === 'crown' && Math.abs(z) < 15 && Math.abs(y - boardTopY(z) - 1) < 1e-4) samples.push(normal.getY(index));
    }
    assert.ok(samples.length, name);
    assert.ok(samples.reduce((sum, value) => sum + value, 0) / samples.length * sign > .98, name);
  }
});

const solids = [];
check('Neck, board, nut, fret and headstock solids are watertight after UV-seam welding', () => {
  for (const name of ['d-section-neck-back', 'curved-fingerboard', 'grooved-nut', 'fret-1', 'headstock-solid']) {
    const geometry = model.group.getObjectByName(name).geometry, positions = geometry.attributes.position;
    const indices = geometry.index?.array ?? Array.from({ length: positions.count }, (_, index) => index);
    const welded = new Map(), vertexIds = [];
    for (let index = 0; index < positions.count; index++) {
      const key = [positions.getX(index), positions.getY(index), positions.getZ(index)].map((value) => Math.round(value * 1e4)).join(',');
      if (!welded.has(key)) welded.set(key, welded.size);
      vertexIds.push(welded.get(key));
    }
    const edges = new Map();
    for (let triangle = 0; triangle < indices.length; triangle += 3) {
      for (let edge = 0; edge < 3; edge++) {
        const a = vertexIds[indices[triangle + edge]], b = vertexIds[indices[triangle + (edge + 1) % 3]];
        if (a === b) continue;
        const key = [Math.min(a, b), Math.max(a, b)].join(',');
        edges.set(key, (edges.get(key) ?? 0) + 1);
      }
    }
    assert.ok([...edges.values()].every((count) => count === 2), name);
    solids.push({ name, weldedVertices: welded.size, edges: edges.size });
  }
});

let triangles = 0, vertices = 0, meshes = 0;
check('Geometry has finite attributes, valid indices and at most 20,000 triangles / 75 meshes', () => {
  model.group.traverse((object) => {
    if (!object.isMesh) return;
    meshes++;
    const geometry = object.geometry, positions = geometry.attributes.position;
    vertices += positions.count;
    triangles += (geometry.index?.count ?? positions.count) / 3;
    assert.ok(positions.count > 0, object.name);
    for (const [name, attribute] of Object.entries(geometry.attributes)) {
      assert.ok([...attribute.array].every(Number.isFinite), `${object.name}: ${name}`);
      assert.equal(attribute.count, positions.count, `${object.name}: ${name}`);
    }
    if (geometry.index) assert.ok([...geometry.index.array].every((index) => Number.isInteger(index) && index >= 0 && index < positions.count), object.name);
    assert.ok(Number.isInteger((geometry.index?.count ?? positions.count) / 3), object.name);
  });
  assert.ok(triangles > 0 && triangles <= 20000);
  assert.ok(meshes > 0 && meshes <= 75);
});

const report = {
  passed: true,
  scope: 'CPU audit of a generic open-string study neck; no hand, browser/WebGL, touch or physical iPad approval.',
  checks, triangles, vertices, meshes, minimumOpenFretClearanceMm: minimumFretClearance,
  solids, boundsMm: model.metadata.boundsMm,
};
const reportPath = path.join(process.env.STAGE33_REPORT_DIR || '/tmp/fretline-stage33-assets', 'guitar', 'geometry-audit.json');
fs.mkdirSync(path.dirname(reportPath), { recursive: true });
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ passed: true, checks: checks.length, triangles, vertices, meshes, minimumOpenFretClearanceMm: minimumFretClearance, reportPath }));
