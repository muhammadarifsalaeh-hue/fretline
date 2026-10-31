import assert from 'node:assert/strict';
import { createHash, webcrypto } from 'node:crypto';
import { existsSync, readFileSync } from 'node:fs';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { assessHandPose, createHandPoseEngine, disposeHandObject } from '../src/features/practice/scene/handPoseEngine.js';

let passed = 0, failed = 0;
async function check(name, run) {
  try { await run(); passed++; console.log(`PASS ${name}`); }
  catch (error) { failed++; console.error(`FAIL ${name}: ${error.stack || error.message}`); }
}
const clone = (value) => structuredClone(value);
const bytes = new Uint8Array([71, 76, 84, 70, 1, 2, 3, 4]).buffer;
const sha = createHash('sha256').update(new Uint8Array(bytes)).digest('hex');
const boneNames = ['wrist.L', 'finger2-1.L'];
const rigSignature = [...boneNames].sort().join('|');
const bilingual = { th: 'ท่าทดลองรอตรวจทาน', en: 'Experimental pose awaiting review.' };
function fixture() {
  const metadata = { schemaVersion: 1, assetSha256: sha, rigSignature, expectedBoneNames: boneNames, millimetresPerAssetUnit: 1000, anatomicalPoseStatus: 'unavailable' };
  const record = { status: 'needs-review', reviewed: false, reason: bilingual, root: { positionMm: [55, 12, -4], quaternion: [0, 0, 0, 1] }, bones: Object.fromEntries(boneNames.map((name) => [name, { quaternion: [0, 0, 0, 1] }])), audit: { collisionPassed: true, contactPassed: true, anatomyPassed: false, multiViewReviewed: false } };
  const library = { schemaVersion: 1, assetSha256: sha, rigSignature, poses: { C: record, D: clone(record) } };
  library.poses.D.bones['finger2-1.L'].quaternion = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), .4).toArray();
  return { metadata, library, assetSha256: sha, boneNames, chordId: 'C' };
}

await check('A matched but unreviewed candidate remains needs-review', () => {
  const result = assessHandPose(fixture());
  assert.equal(result.status, 'needs-review'); assert.equal(result.candidate, true);
  assert.equal(result.inspectionAllowed, true);
  assert.deepEqual(result.reason, bilingual);
});
await check('Inspection requires explicit successful contact and collision gates, without granting teaching approval', () => {
  for (const name of ['collisionPassed', 'contactPassed']) {
    for (const value of [undefined, false, 'true', 1, null]) {
      const data = fixture(); data.library.poses.C.audit[name] = value;
      const result = assessHandPose(data);
      assert.equal(result.candidate, true, 'Complete transforms remain available to hidden diagnostics');
      assert.equal(result.status, 'needs-review'); assert.equal(result.inspectionAllowed, false, `${name}=${value}`);
      assert.ok(result.reason.th); assert.ok(result.reason.en);
    }
  }
  const data = fixture(); delete data.library.poses.C.audit;
  assert.equal(assessHandPose(data).inspectionAllowed, false);
  assert.equal(assessHandPose(fixture()).status, 'needs-review');
});
await check('Actual 42-record library permits inspection only for independently mesh-audited endpoints', () => {
  const libraryFile = new URL('../src/features/practice/assets/hand-poses.json', import.meta.url);
  const libraryBytes = readFileSync(libraryFile), library = JSON.parse(libraryBytes);
  const metadata = JSON.parse(readFileSync(new URL('../src/features/practice/assets/makehuman-left-arm.metadata.json', import.meta.url)));
  const actualHash = createHash('sha256').update(readFileSync(new URL('../src/features/practice/assets/makehuman-left-arm-sleeved.glb', import.meta.url))).digest('hex');
  const libraryHash = createHash('sha256').update(libraryBytes).digest('hex');
  const reports = ['../docs/practice-complete-42/tests/geometry/summary.json', '../docs/practice-fingering-polish/tests/geometry/summary.json', '../docs/practice-final-delivery/geometry/summary.json', '../docs/practice-hand-batch-3/geometry/summary.json']
    .map((path) => new URL(path, import.meta.url)).filter(existsSync).map((path) => JSON.parse(readFileSync(path)));
  const audit = reports.find((report) => report.librarySnapshotSha256 === libraryHash);
  assert.ok(audit, 'A completed actual mesh report must bind the current library before inspection tests can pass');
  assert.equal(audit.assetSha256, actualHash); assert.equal(audit.count, 42);
  assert.equal(new Set(audit.rows.map(({ id }) => id)).size, 42);
  const expected = audit.rows.filter(({ geometricPassed }) => geometricPassed).map(({ id }) => id).sort();
  const actual = Object.keys(library.poses).filter((chordId) => {
    const result = assessHandPose({ library, metadata, assetSha256: actualHash, boneNames: metadata.expectedBoneNames, chordId });
    assert.equal(result.candidate, true, `${chordId}: keep the complete real rig for hidden diagnostic fingerprints`);
    assert.notEqual(result.status, 'verified', `${chordId}: geometry alone cannot approve a teaching hand`);
    return result.inspectionAllowed;
  }).sort();
  assert.equal(Object.keys(library.poses).length, 42); assert.deepEqual(actual, expected);
  console.log(`  Actual inspected eligibility: ${actual.length}/42; rejected endpoints remain hidden.`);
});
await check('A status label alone cannot promote a pose to verified', () => {
  for (const patch of [{}, { reviewed: true }, { audit: { collisionPassed: true } }]) {
    const data = fixture(); Object.assign(data.library.poses.C, { status: 'verified' }, patch);
    assert.equal(assessHandPose(data).status, 'needs-review');
  }
});
await check('Verification requires each per-chord physical audit and explicit review', () => {
  const data = fixture(); const flags = ['collisionPassed', 'contactPassed', 'anatomyPassed', 'multiViewReviewed'];
  Object.assign(data.library.poses.C, { status: 'verified', reviewed: true, audit: Object.fromEntries(flags.map((name) => [name, true])) });
  // The source model's unposed status does not override a reviewed chord pose.
  data.metadata.anatomicalPoseStatus = 'unavailable';
  assert.equal(assessHandPose(data).status, 'verified');
  for (const name of flags) {
    for (const value of [undefined, false, 'true']) {
      const candidate = clone(data); candidate.library.poses.C.audit[name] = value;
      assert.equal(assessHandPose(candidate).status, 'needs-review', `${name}=${value}`);
    }
  }
  data.library.poses.C.reviewed = 'true';
  assert.notEqual(assessHandPose(data).status, 'verified');
});
await check('Missing or explicitly unavailable poses never offer a renderable candidate', () => {
  for (const status of ['missing', 'unavailable']) {
    const data = fixture(); if (status === 'missing') delete data.library.poses.C; else data.library.poses.C.status = status;
    const result = assessHandPose(data); assert.equal(result.status, 'unavailable'); assert.equal(result.candidate, false);
    assert.ok(result.reason.th); assert.ok(result.reason.en);
  }
});
await check('Hash, rig, schema and physical-unit mismatches hide the candidate', () => {
  const edits = [
    (data) => { data.assetSha256 = ''; },
    (data) => { data.library.assetSha256 = 'different'; },
    (data) => { data.metadata.assetSha256 = 'different'; },
    (data) => { data.library.rigSignature = 'unrelated'; },
    (data) => { data.metadata.rigSignature = 'unrelated'; },
    (data) => { data.library.schemaVersion = 2; },
    (data) => { data.metadata.schemaVersion = 2; },
    (data) => { data.metadata.millimetresPerAssetUnit = 1; },
  ];
  for (const edit of edits) {
    const data = fixture(); edit(data); const result = assessHandPose(data);
    assert.equal(result.status, 'unavailable'); assert.equal(result.candidate, false);
  }
});
await check('Incomplete, non-finite or non-unit transforms hide the candidate', () => {
  const edits = [
    (record) => { delete record.root; },
    (record) => { record.root.positionMm = [0, NaN, 0]; },
    (record) => { record.root.positionMm = [0, 0]; },
    (record) => { record.root.quaternion = [0, 0, 0, 0]; },
    (record) => { record.root.quaternion = [0, 0, 0, 1.05]; },
    (record) => { record.bones['wrist.L'].quaternion = [Infinity, 0, 0, 1]; },
    (record) => { delete record.bones['finger2-1.L']; },
  ];
  for (const edit of edits) {
    const data = fixture(); edit(data.library.poses.C); const result = assessHandPose(data);
    assert.equal(result.status, 'unavailable'); assert.equal(result.candidate, false);
  }
});
await check('An empty, duplicate or malformed loaded rig cannot satisfy the gate', () => {
  for (const names of [[], ['wrist.L', 'wrist.L'], ['wrist.L', null]]) {
    const data = fixture(); data.boneNames = names;
    const result = assessHandPose(data); assert.equal(result.status, 'unavailable'); assert.equal(result.candidate, false);
  }
});

await check('Per-string pressure offsets are complete, finite and restricted to canonical frets', () => {
  const good = { '5:3': 12, '4:2': 8, '2:1': 4 };
  const data = fixture(); data.library.poses.C.pressOffsetsMm = good;
  assert.equal(assessHandPose(data).inspectionAllowed, true);
  for (const value of [null, [], {}, { ...good, '6:1': 4 }, { ...good, '3:1': 4 }, { ...good, '5:3': 0 }, { ...good, '4:2': Infinity }, { ...good, '2:1': true }, { ...good, '2:1': 30 }]) {
    const candidate = fixture(); candidate.library.poses.C.pressOffsetsMm = value;
    const result = assessHandPose(candidate);
    assert.equal(result.candidate, false); assert.equal(result.inspectionAllowed, false); assert.equal(result.status, 'unavailable');
  }
});

function modelFixture({ duplicate = false } = {}) {
  const root = new THREE.Group(), counts = { geometry: 0, material: 0, texture: 0, skeleton: 0, image: 0 };
  const geometry = new THREE.BufferGeometry(); geometry.addEventListener('dispose', () => counts.geometry++);
  const image = { close() { counts.image++; } };
  const texture = new THREE.Texture(image); texture.addEventListener('dispose', () => counts.texture++);
  const material = new THREE.MeshStandardMaterial({ map: texture }); material.addEventListener('dispose', () => counts.material++);
  const bones = boneNames.map((name) => { const bone = new THREE.Bone(); bone.name = name.replaceAll('.', ''); bone.userData.name = name; return bone; });
  bones[0].add(bones[1]); root.add(bones[0]);
  if (duplicate) { const bone = new THREE.Bone(); bone.userData.name = boneNames[0]; root.add(bone); }
  const skeleton = new THREE.Skeleton(bones); skeleton.computeBoneTexture();
  skeleton.boneTexture.addEventListener('dispose', () => counts.skeleton++);
  for (let i = 0; i < 2; i++) {
    const mesh = new THREE.SkinnedMesh(geometry, material); mesh.bind(skeleton); root.add(mesh);
  }
  return { scene: root, counts, bones };
}
await check('Disposal releases shared skin, texture, geometry and image resources once', () => {
  const model = modelFixture(), parent = new THREE.Group(); parent.add(model.scene);
  disposeHandObject(model.scene); disposeHandObject(model.scene);
  assert.deepEqual(model.counts, { geometry: 1, material: 1, texture: 1, skeleton: 1, image: 1 });
  assert.equal(parent.children.length, 0); assert.equal(model.scene.children.length, 0);
});

const deferred = () => { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; };
const tick = () => new Promise((resolve) => setImmediate(resolve));
async function until(predicate, description) {
  const deadline = Date.now() + 2000;
  while (!predicate()) { if (Date.now() > deadline) throw new Error(`Timed out: ${description}`); await tick(); }
}
function responseFor(url, data) {
  return { ok: true, arrayBuffer: async () => bytes.slice(0), json: async () => clone(url.endsWith('metadata.json') ? data.metadata : data.library) };
}
async function withEngine(run, overrides = {}) {
  const oldFetch = globalThis.fetch, oldCrypto = Object.getOwnPropertyDescriptor(globalThis, 'crypto'), oldParse = GLTFLoader.prototype.parseAsync;
  const data = fixture(), scene = new THREE.Scene(), canvas = { dataset: {} }, updates = [], requests = [], models = [];
  let parses = 0, engine;
  try {
    Object.defineProperty(globalThis, 'crypto', { configurable: true, value: webcrypto });
    globalThis.fetch = (url, options) => { requests.push({ url, signal: options.signal }); return overrides.fetch ? overrides.fetch(url, options, data, requests.length) : Promise.resolve(responseFor(url, data)); };
    GLTFLoader.prototype.parseAsync = (...args) => { parses++; if (overrides.parse) return overrides.parse(...args); const model = modelFixture(overrides.modelOptions); models.push(model); return Promise.resolve(model); };
    engine = createHandPoseEngine({ scene, canvas, chord: { id: 'C' }, nutX: -4, unit: 40, invalidate() {}, onPoseStatus(value) { updates.push(value); } });
    await run({ engine, canvas, scene, updates, requests, models, data, get parses() { return parses; } });
  } finally {
    engine?.dispose(); globalThis.fetch = oldFetch; GLTFLoader.prototype.parseAsync = oldParse;
    if (oldCrypto) Object.defineProperty(globalThis, 'crypto', oldCrypto); else delete globalThis.crypto;
  }
}
await check('Loaded candidates stay hidden until inspection; bone transforms produce distinct signatures', async () => {
  await withEngine(async ({ engine, canvas, updates, models }) => {
    await until(() => canvas.dataset.handAssetStatus === 'ready', 'hand ready');
    assert.equal(canvas.dataset.handStatus, 'needs-review'); assert.equal(canvas.dataset.handVisible, 'false');
    const first = canvas.dataset.handPoseSignature;
    assert.match(first, /^[a-f0-9]{8}$/); assert.equal(updates.at(-1).reviewMode, false);
    engine.setHandReviewMode(true); assert.equal(canvas.dataset.handVisible, 'true');
    engine.setChord({ id: 'D' });
    assert.notEqual(canvas.dataset.handPoseSignature, first);
    assert.equal(canvas.dataset.handVisible, 'false'); assert.equal(updates.at(-1).reviewMode, false);
    assert.ok(Math.abs(models[0].bones[1].quaternion.x) > .1);
    engine.setHandReviewMode(true); engine.setChord({ id: 'missing' });
    assert.equal(canvas.dataset.handStatus, 'unavailable'); assert.equal(canvas.dataset.handVisible, 'false');
  });
});
await check('Programmatic inspection cannot reveal a failed pose, and accepted hidden rig fingerprints remain distinct', async () => {
  for (const name of ['collisionPassed', 'contactPassed']) {
    for (const value of [undefined, false, 'true']) {
      await withEngine(async ({ engine, canvas, updates, models }) => {
        await until(() => canvas.dataset.handAssetStatus === 'ready', 'geometry-rejected hand ready');
        const cSignature = canvas.dataset.handPoseSignature;
        assert.equal(canvas.dataset.handInspectionAllowed, 'false');
        engine.setHandReviewMode(true);
        assert.equal(canvas.dataset.handVisible, 'false'); assert.equal(canvas.dataset.handReviewMode, 'false');
        assert.equal(updates.at(-1).inspectionAllowed, false); assert.equal(updates.at(-1).reviewMode, false);
        engine.setChord({ id: 'D' });
        assert.notEqual(canvas.dataset.handPoseSignature, cSignature);
        assert.ok(Math.abs(models[0].bones[1].quaternion.x) > .1);
        assert.equal(canvas.dataset.handInspectionAllowed, 'true'); assert.equal(canvas.dataset.handVisible, 'false');
        engine.setHandReviewMode(true); assert.equal(canvas.dataset.handVisible, 'true');
        engine.setChord({ id: 'C' }); engine.setHandReviewMode(true);
        assert.equal(canvas.dataset.handVisible, 'false'); assert.equal(canvas.dataset.handReviewMode, 'false');
      }, { fetch: async (url, options, data) => {
        data.library.poses.C.audit[name] = value;
        return responseFor(url, data);
      } });
    }
  }
});
await check('An HTTP asset failure aborts sibling requests and reports diagram fallback', async () => {
  await withEngine(async (context) => {
    await until(() => context.canvas.dataset.handAssetStatus === 'error', 'hand error');
    assert.equal(context.canvas.dataset.handVisible, 'false'); assert.equal(context.canvas.dataset.handStatus, 'unavailable');
    assert.ok(context.updates.at(-1).reason.th); assert.ok(context.updates.at(-1).reason.en);
    assert.equal(context.parses, 0); assert.ok(context.requests.every(({ signal }) => signal.aborted));
  }, { fetch: async () => ({ ok: false }) });
});
await check('A malformed parsed rig is disposed and exposes a retryable fallback', async () => {
  await withEngine(async ({ canvas, models }) => {
    await until(() => canvas.dataset.handAssetStatus === 'error', 'rig error');
    assert.equal(canvas.dataset.handVisible, 'false');
    assert.deepEqual(models[0].counts, { geometry: 1, material: 1, texture: 1, skeleton: 1, image: 1 });
  }, { modelOptions: { duplicate: true } });
});
await check('Leaving during network load aborts requests and prevents later publication', async () => {
  const pending = [];
  await withEngine(async (context) => {
    assert.equal(pending.length, 3); context.engine.dispose(); const before = context.updates.length;
    assert.ok(context.requests.every(({ signal }) => signal.aborted)); assert.equal(context.scene.children.length, 0);
    context.engine.setChord({ id: 'D' }); context.engine.setHandReviewMode(true); context.engine.retryHand();
    for (const item of pending) item.resolve(responseFor(item.url, context.data));
    await tick(); await tick();
    assert.equal(context.updates.length, before); assert.equal(context.parses, 0); assert.equal(context.requests.length, 3);
  }, { fetch(url) { const item = deferred(); pending.push({ ...item, url }); return item.promise; } });
});
await check('A parse completed after disposal releases the late skin and publishes nothing', async () => {
  const parsed = deferred(), model = modelFixture(); let started = false;
  await withEngine(async ({ engine, updates, scene }) => {
    await until(() => started, 'parse started'); engine.dispose(); const before = updates.length;
    parsed.resolve(model); await tick(); await tick();
    assert.equal(updates.length, before); assert.equal(scene.children.length, 0);
    assert.deepEqual(model.counts, { geometry: 1, material: 1, texture: 1, skeleton: 1, image: 1 });
  }, { parse() { started = true; return parsed.promise; } });
});
await check('Retry ignores an earlier load even when its fetch ignores cancellation', async () => {
  const pending = [];
  await withEngine(async (context) => {
    context.engine.retryHand(); assert.equal(pending.length, 6);
    assert.ok(context.requests.slice(0, 3).every(({ signal }) => signal.aborted));
    for (const item of pending.slice(3)) item.resolve(responseFor(item.url, context.data));
    await until(() => context.canvas.dataset.handAssetStatus === 'ready', 'retry ready');
    const readyUpdates = context.updates.length;
    for (const item of pending.slice(0, 3)) item.resolve(responseFor(item.url, context.data));
    await tick(); await tick();
    assert.equal(context.parses, 1); assert.equal(context.updates.length, readyUpdates);
    assert.equal(context.canvas.dataset.handVisible, 'false');
  }, { fetch(url) { const item = deferred(); pending.push({ ...item, url }); return item.promise; } });
});
await check('Parse errors remain recoverable through the hand-only retry', async () => {
  let calls = 0; const model = modelFixture();
  await withEngine(async (context) => {
    await until(() => context.canvas.dataset.handAssetStatus === 'error', 'parse failure');
    assert.equal(context.canvas.dataset.handVisible, 'false');
    context.engine.retryHand();
    await until(() => context.canvas.dataset.handAssetStatus === 'ready', 'parse recovery');
    assert.equal(context.canvas.dataset.handStatus, 'needs-review'); assert.equal(context.canvas.dataset.handVisible, 'false');
    assert.equal(context.parses, 2);
  }, { parse() { return ++calls === 1 ? Promise.reject(new Error('bad glTF')) : Promise.resolve(model); } });
});
await check('Retry hides and disposes the inspected hand before loading its replacement', async () => {
  await withEngine(async (context) => {
    await until(() => context.canvas.dataset.handAssetStatus === 'ready', 'first hand');
    context.engine.setHandReviewMode(true); assert.equal(context.canvas.dataset.handVisible, 'true');
    const first = context.models[0]; context.engine.retryHand();
    assert.equal(context.canvas.dataset.handVisible, 'false'); assert.equal(context.canvas.dataset.handReviewMode, 'false');
    assert.equal(context.canvas.dataset.handAssetStatus, 'loading');
    assert.deepEqual(first.counts, { geometry: 1, material: 1, texture: 1, skeleton: 1, image: 1 });
    await until(() => context.canvas.dataset.handAssetStatus === 'ready', 'replacement hand');
    assert.equal(context.models.length, 2); assert.equal(context.canvas.dataset.handVisible, 'false');
  });
});
await check('A parse superseded by retry is disposed without replacing the current hand', async () => {
  const first = deferred(), second = deferred(), oldModel = modelFixture(), newModel = modelFixture(); let calls = 0;
  await withEngine(async (context) => {
    await until(() => calls === 1, 'first parse started'); context.engine.retryHand();
    await until(() => calls === 2, 'second parse started'); second.resolve(newModel);
    await until(() => context.canvas.dataset.handAssetStatus === 'ready', 'second parse ready');
    const readyUpdates = context.updates.length; first.resolve(oldModel); await tick(); await tick();
    assert.equal(context.updates.length, readyUpdates); assert.equal(context.canvas.dataset.handAssetStatus, 'ready');
    assert.deepEqual(oldModel.counts, { geometry: 1, material: 1, texture: 1, skeleton: 1, image: 1 });
    assert.deepEqual(newModel.counts, { geometry: 0, material: 0, texture: 0, skeleton: 0, image: 0 });
  }, { parse() { return ++calls === 1 ? first.promise : second.promise; } });
});

console.log(`\nHand runtime: ${passed} passed, ${failed} failed.`);
if (failed) process.exitCode = 1;
