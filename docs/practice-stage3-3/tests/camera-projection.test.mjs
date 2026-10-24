import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { FRET_COUNT, getFretPosition } from '../../../src/features/practice/data/fretboard.js';
import { buildStudyGuitar } from '../../../src/features/practice/scene/studyGuitar.js';
import {
  CAMERA_DIRECTIONS, referenceCameraUp, boundsCorners, fitPerspectiveDistance, placeCamera,
} from '../../../src/features/practice/scene/cameraMath.js';

// CPU projection/control math, using the real app model and camera helpers.
// No DOM, WebGL renderer, hand, browser/touch or physical iPad validation.
const UNIT = 40;
const model = buildStudyGuitar({ textures: false });
model.group.scale.setScalar(1 / UNIT);
model.group.position.x = -getFretPosition(FRET_COUNT) / UNIT / 2;
model.group.updateMatrixWorld(true);
assert.equal(model.group.position.x, -4.05);

// Match the scene's label positions and sprite size without canvas textures.
// The final .2 world-unit pad also covers their camera-facing footprint.
const fretLabels = new THREE.Group();
for (const fret of [3, 5, 7, 9, 12]) {
  const mm = (getFretPosition(fret - 1) + getFretPosition(fret)) / 2;
  const sprite = new THREE.Sprite();
  sprite.scale.set(.23, .23, 1);
  sprite.position.set(model.group.position.x + mm / UNIT, 0, -(model.surfaces.widthAtX(mm) / 2 + 9) / UNIT);
  fretLabels.add(sprite);
}
fretLabels.updateMatrixWorld(true);
const meshBounds = new THREE.Box3().setFromObject(model.group);
const labelBounds = new THREE.Box3().setFromObject(fretLabels);
const bounds = meshBounds.clone().union(labelBounds).expandByScalar(.2);
const target = new THREE.Vector3(bounds.getCenter(new THREE.Vector3()).x, 0, 0);
const up = referenceCameraUp();
const viewports = [
  [1440, 900], [1024, 768], [768, 1024], [390, 844], [320, 740],
  [930, 520], [900, 540], [640, 480], [358, 420], [288, 400],
];
const checks = [], results = [];
const check = (name, run) => { run(); checks.push({ name, passed: true }); };
const near = (actual, expected, epsilon = 1e-10) => assert.ok(
  Math.abs(actual - expected) < epsilon, `${actual} differs from ${expected}`,
);
const pixel = (camera, point, width, height) => {
  const ndc = point.clone().project(camera);
  return { x: (ndc.x + 1) * width / 2, y: (1 - ndc.y) * height / 2, depth: ndc.z };
};
const worldPoint = (point) => model.group.localToWorld(point.clone());
const physicalStrings = model.strings.map((string, index) => {
  const { centerlineSamplesMm, radialSegments } = string.geometry.userData;
  const ringIndex = centerlineSamplesMm.findIndex(([x]) => Math.abs(x - model.metadata.referenceStringXmm) < 1e-7);
  assert.ok(ringIndex >= 0, string.name);
  const ring = Array.from({ length: radialSegments }, (_, column) => new THREE.Vector3()
    .fromBufferAttribute(string.geometry.attributes.position, ringIndex * radialSegments + column)
    .applyMatrix4(string.matrixWorld));
  const center = ring.reduce((sum, point) => sum.add(point), new THREE.Vector3()).divideScalar(radialSegments);
  assert.ok(center.distanceTo(worldPoint(model.anchors.strings[index].position)) < 1e-12);
  const radius = ring.reduce((sum, point) => sum + point.distanceTo(center), 0) / radialSegments;
  near(radius, string.userData.radiusMm / UNIT, 3e-7);
  return { number: string.userData.number, note: string.userData.note, radius, center, ring };
});

const geometrySignature = () => {
  // Hash real attributes, topology and world matrices; camera math cannot edit them.
  model.group.updateMatrixWorld(true);
  const hash = createHash('sha256');
  model.group.traverse((object) => {
    if (!object.geometry) return;
    hash.update(object.name);
    for (const [name, attribute] of Object.entries(object.geometry.attributes)) {
      hash.update(name);
      hash.update(Buffer.from(attribute.array.buffer, attribute.array.byteOffset, attribute.array.byteLength));
    }
    const indices = object.geometry.index?.array;
    if (indices) hash.update(Buffer.from(indices.buffer, indices.byteOffset, indices.byteLength));
    hash.update(Buffer.from(new Float64Array(object.matrixWorld.elements).buffer));
  });
  return hash.digest('hex');
};
const originalGeometrySignature = geometrySignature();

check('Fixed rolled up vector is finite, unit length and points toward the low-E edge', () => {
  assert.ok(up.toArray().every(Number.isFinite));
  near(up.length(), 1);
  assert.ok(up.z > .9);
});
check('Actual scaled tube rings keep E A D G B e numbering and decreasing physical radii', () => {
  assert.deepEqual(physicalStrings.map(({ number }) => number), [6, 5, 4, 3, 2, 1]);
  assert.deepEqual(physicalStrings.map(({ note }) => note), ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']);
  physicalStrings.forEach((string, index) => {
    if (!index) return;
    assert.ok(physicalStrings[index - 1].center.z > string.center.z);
    assert.ok(physicalStrings[index - 1].radius > string.radius);
  });
});
check('A camera up vector parallel to the view is rejected instead of producing a broken fit', () => {
  const camera = new THREE.PerspectiveCamera(38, 1, .1, 100);
  camera.up.set(0, 1, 0);
  assert.throws(() => fitPerspectiveDistance(camera, bounds, target, new THREE.Vector3(0, 1, 0)), RangeError);
});

for (const [width, height] of viewports) {
  const viewport = `${width}x${height}`;
  const camera = new THREE.PerspectiveCamera(38, width / height, .1, 100);
  // OrbitControls caches this basis in its constructor, as in createNeckScene.
  camera.up.copy(up);
  camera.position.copy(target).addScaledVector(new THREE.Vector3(...CAMERA_DIRECTIONS.angle).normalize(), 15);
  const controls = new OrbitControls(camera);
  controls.target.copy(target);
  controls.enableDamping = false;
  controls.enablePan = false;
  controls.minPolarAngle = .45;
  controls.maxPolarAngle = Math.PI - .45;

  const presetResults = [];
  for (const name of ['angle', 'front', 'head', 'back', 'side', 'player']) {
    const distance = placeCamera(camera, bounds, target, name);
    controls.update();
    const strings = physicalStrings.map(({ number, note, center, ring }) => {
      const projected = pixel(camera, center, width, height);
      const projectedRadius = Math.max(...ring.map((point) => {
        const vertex = pixel(camera, point, width, height);
        return Math.hypot(vertex.x - projected.x, vertex.y - projected.y);
      }));
      return { number, note, ...projected, projectedRadius };
    });
    let maxProjectedBounds = 0;
    check(`${viewport} ${name}: actual mesh and padded fret-label bounds fit without clipping`, () => {
      for (const corner of boundsCorners(bounds)) {
        const point = corner.project(camera);
        assert.ok(point.toArray().every(Number.isFinite));
        assert.ok(Math.abs(point.x) < 1 && Math.abs(point.y) < 1 && point.z > -1 && point.z < 1, point.toArray().join(','));
        maxProjectedBounds = Math.max(maxProjectedBounds, Math.abs(point.x), Math.abs(point.y));
      }
      assert.ok(maxProjectedBounds <= 1 / 1.12 + 1e-10);
      assert.ok(controls.getPolarAngle() >= .45 - 1e-12);
      assert.ok(controls.getPolarAngle() <= Math.PI - .45 + 1e-12);
      assert.ok(camera.up.distanceTo(up) < 1e-12);
    });
    check(`${viewport} ${name}: actual strings project E A D G B e from top to bottom with decreasing radii`, () => {
      for (let index = 0; index < strings.length; index++) {
        const string = strings[index];
        assert.ok(Number.isFinite(string.projectedRadius) && string.projectedRadius > 0);
        assert.ok(string.depth > -1 && string.depth < 1);
        if (!index) continue;
        assert.ok(strings[index - 1].y < string.y, JSON.stringify(strings));
        assert.ok(strings[index - 1].projectedRadius > string.projectedRadius, JSON.stringify(strings));
      }
    });
    presetResults.push({ name, distance, polarAngle: controls.getPolarAngle(), maxProjectedBounds, strings });
  }

  placeCamera(camera, bounds, target, 'angle');
  controls.update();
  const head = pixel(camera, worldPoint(model.anchors.headstock), width, height);
  const nut = pixel(camera, worldPoint(model.anchors.nut), width, height);
  const body = pixel(camera, worldPoint(model.anchors.bodyDirection), width, height);
  // The sculpted headstock center is tilted off-axis. Nut/body share y=z=0.
  const slopeDegrees = THREE.MathUtils.radToDeg(Math.atan2(body.y - nut.y, nut.x - body.x));
  check(`${viewport} default: headstock right/up, body left/down and 15 degree neck axis`, () => {
    assert.ok(head.x > body.x && head.y < body.y);
    assert.ok(nut.x > body.x && nut.y < body.y);
    near(slopeDegrees, 15, 1e-8);
  });

  const resetPosition = camera.position.clone();
  const resetQuaternion = camera.quaternion.clone();
  const resetStrings = physicalStrings.map(({ center }) => pixel(camera, center, width, height));
  check(`${viewport}: public OrbitControls rotate and Reset preserve the fixed up basis and actual geometry`, () => {
    controls.rotateLeft(-.15);
    controls.rotateUp(.1);
    controls.update();
    assert.ok(camera.position.distanceTo(resetPosition) > .01);
    assert.ok(camera.position.toArray().every(Number.isFinite));
    assert.ok(camera.matrixWorld.elements.every(Number.isFinite));
    assert.ok(camera.up.distanceTo(up) < 1e-12);
    assert.equal(geometrySignature(), originalGeometrySignature);

    placeCamera(camera, bounds, target, 'angle');
    controls.update();
    assert.ok(camera.position.distanceTo(resetPosition) < 1e-10);
    assert.ok(camera.quaternion.angleTo(resetQuaternion) < 1e-7);
    assert.ok(camera.up.distanceTo(up) < 1e-12);
    for (let index = 0; index < physicalStrings.length; index++) {
      const restored = pixel(camera, physicalStrings[index].center, width, height);
      near(restored.x, resetStrings[index].x, 1e-8);
      near(restored.y, resetStrings[index].y, 1e-8);
    }
    assert.equal(geometrySignature(), originalGeometrySignature);
  });
  check(`${viewport}: public vertical rotation obeys both polar limits and Reset restores the view`, () => {
    controls.rotateUp(10 * Math.PI);
    controls.update();
    near(controls.getPolarAngle(), .45);
    controls.rotateUp(-10 * Math.PI);
    controls.update();
    near(controls.getPolarAngle(), Math.PI - .45);
    placeCamera(camera, bounds, target, 'angle');
    controls.update();
    assert.ok(camera.position.distanceTo(resetPosition) < 1e-10);
    assert.equal(geometrySignature(), originalGeometrySignature);
  });
  // No DOM element was attached; this Three release's dispose() assumes a DOM.
  results.push({ width, height, slopeDegrees, head, nut, body, presets: presetResults });
}

const report = {
  passed: true,
  scope: 'CPU perspective and OrbitControls math using actual study-neck meshes; no hand, browser/WebGL, touch or physical iPad approval.',
  fixedUp: up.toArray(), worldScale: 1 / UNIT, nutX: model.group.position.x,
  meshBounds: { min: meshBounds.min.toArray(), max: meshBounds.max.toArray() },
  labelBounds: { min: labelBounds.min.toArray(), max: labelBounds.max.toArray() },
  paddedBounds: { min: bounds.min.toArray(), max: bounds.max.toArray() },
  geometrySignature: originalGeometrySignature,
  checks, results,
};
const reportPath = path.join(process.env.STAGE33_REPORT_DIR || '/tmp/fretline-stage33-assets', 'camera', 'camera-math-report.json');
fs.mkdirSync(path.dirname(reportPath), { recursive: true });
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ passed: true, checks: checks.length, viewports: viewports.length, presetsPerViewport: 6, geometrySignature: originalGeometrySignature, reportPath }));
