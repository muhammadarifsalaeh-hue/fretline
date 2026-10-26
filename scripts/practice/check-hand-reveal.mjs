import assert from 'node:assert/strict';
import * as THREE from 'three';
import { createHandReveal } from '../../src/features/practice/scene/handReveal.js';

let passed = 0, failed = 0;
const check = (name, run) => {
  try { run(); passed++; console.log(`PASS ${name}`); }
  catch (error) { failed++; console.error(`FAIL ${name}: ${error.stack || error}`); }
};

function setup(options = {}) {
  const root = new THREE.Group();
  const opaque = new THREE.MeshStandardMaterial({ opacity: .8, transparent: false, depthWrite: true });
  const translucent = new THREE.MeshStandardMaterial({ opacity: .4, transparent: true, depthWrite: false, alphaTest: .2 });
  const geometry = new THREE.BoxGeometry();
  root.add(new THREE.Mesh(geometry, [opaque, translucent]), new THREE.Mesh(geometry, opaque));
  const bone = new THREE.Bone(); bone.quaternion.setFromAxisAngle(new THREE.Vector3(1, 0, 0), .2); root.add(bone);
  let time = 0, serial = 0, invalidations = 0, reduced = false;
  const queued = new Map(), updates = [];
  const reveal = createHandReveal(root, {
    requestFrame(callback) { const id = ++serial; queued.set(id, callback); return id; },
    cancelFrame(id) { queued.delete(id); }, now: () => time,
    reducedMotion: () => reduced, invalidate() { invalidations++; },
    onProgress(value) { updates.push(value); }, ...options,
  });
  const step = (at) => { time = at; const callbacks = [...queued.values()]; queued.clear(); callbacks.forEach((callback) => callback(time)); };
  return { root, opaque, translucent, bone, reveal, queued, updates, step, setReduced(value) { reduced = value; },
    get invalidations() { return invalidations; } };
}

check('Only appearance changes; actual bone/root pose remains exact throughout the reveal', () => {
  const t = setup(), before = t.bone.quaternion.toArray(), rootBefore = t.root.matrix.toArray();
  t.reveal.start(); assert.equal(t.opaque.opacity, 0); assert.equal(t.queued.size, 1);
  t.step(80);
  assert.ok(t.opaque.opacity > 0 && t.opaque.opacity < .8);
  assert.deepEqual(t.bone.quaternion.toArray(), before); assert.deepEqual(t.root.matrix.toArray(), rootBefore);
  assert.equal(t.root.visible, true); assert.equal(t.queued.size, 1);
});
check('Completion restores each original alpha/transparent state without changing depth settings', () => {
  const t = setup(); t.reveal.start(); t.step(80); t.step(160);
  assert.equal(t.opaque.opacity, .8); assert.equal(t.opaque.transparent, false); assert.equal(t.opaque.depthWrite, true);
  assert.equal(t.translucent.opacity, .4); assert.equal(t.translucent.transparent, true);
  assert.equal(t.translucent.depthWrite, false); assert.equal(t.translucent.alphaTest, .2);
  assert.equal(t.queued.size, 0); assert.equal(t.updates.at(-1).phase, 'idle');
});
check('No render or animation work remains after the bounded transition', () => {
  const t = setup(); t.reveal.start(); t.step(160);
  const count = t.invalidations; t.step(5000);
  assert.equal(t.invalidations, count); assert.equal(t.queued.size, 0);
});
check('Reduced motion reveals immediately and schedules zero frames', () => {
  const t = setup(); t.setReduced(true); t.reveal.start();
  assert.equal(t.opaque.opacity, .8); assert.equal(t.opaque.transparent, false);
  assert.equal(t.queued.size, 0); assert.equal(t.updates.at(-1).phase, 'idle');
});
check('Reduced-motion change before the next reveal is respected', () => {
  const t = setup(); t.reveal.start(); t.step(40); t.setReduced(true); t.reveal.start();
  assert.equal(t.queued.size, 0); assert.equal(t.opaque.opacity, .8);
});
check('Enabling reduced motion during a reveal finishes on its next frame and leaves none queued', () => {
  const t = setup(); t.reveal.start(); t.step(40);
  assert.ok(t.opaque.opacity > 0 && t.opaque.opacity < .8);
  t.setReduced(true); t.step(50);
  assert.equal(t.opaque.opacity, .8); assert.equal(t.opaque.transparent, false);
  assert.equal(t.queued.size, 0); assert.equal(t.updates.at(-1).phase, 'idle');
  const count = t.invalidations; t.step(1000); assert.equal(t.invalidations, count);
});
check('Rapid toggle cancellation removes every queued frame and restores original material state', () => {
  const t = setup();
  for (let i = 0; i < 20; i++) { t.reveal.start(); t.step(i + 1); t.reveal.cancel(); }
  assert.equal(t.queued.size, 0); assert.equal(t.opaque.opacity, .8); assert.equal(t.opaque.transparent, false);
  const count = t.invalidations; t.step(1000); assert.equal(t.invalidations, count);
});
check('Retry/reset releases the previous material snapshots before a replacement asset appears', () => {
  const t = setup(); t.reveal.start(); t.step(50); t.reveal.reset();
  t.root.clear(); const next = new THREE.MeshStandardMaterial({ opacity: .65 });
  t.root.add(new THREE.Mesh(new THREE.BoxGeometry(), next));
  t.opaque.opacity = .22; t.reveal.start(); t.step(210);
  assert.equal(next.opacity, .65); assert.equal(t.opaque.opacity, .22); assert.equal(t.queued.size, 0);
});
check('Dispose cancels the outstanding frame, restores materials and rejects later starts/cancels', () => {
  const t = setup(); t.reveal.start(); t.step(60); t.reveal.dispose();
  assert.equal(t.queued.size, 0); assert.equal(t.opaque.opacity, .8); assert.equal(t.opaque.transparent, false);
  const count = t.invalidations, updates = t.updates.length;
  t.reveal.start(); t.reveal.cancel(); t.reveal.reset(); t.reveal.dispose(); t.step(1000);
  assert.equal(t.invalidations, count); assert.equal(t.updates.length, updates);
});
check('A runtime without animation-frame support uses the immediate fallback', () => {
  const t = setup({ requestFrame: undefined, cancelFrame: undefined }); t.reveal.start();
  assert.equal(t.opaque.opacity, .8); assert.equal(t.opaque.transparent, false); assert.equal(t.queued.size, 0);
});

console.log(`\nHand reveal: ${passed} passed, ${failed} failed.`);
if (failed) process.exitCode = 1;
