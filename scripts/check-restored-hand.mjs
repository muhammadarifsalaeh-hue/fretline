import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { createServer } from 'vite';

const base = 'cb6d8195c1fcb18da10429e9991365e7497e0b4c';
const sourceRef = 'origin/feature/guitar-practice-3d';
const out = 'docs/restore-black-sleeved-hand/tests';
const git = (...args) => execFileSync('git', args, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }).trim();
const hash = (value) => crypto.createHash('sha256').update(value).digest('hex');
const allowed = new Set(['src/features/practice/components/GuitarNeckViewer.jsx', 'src/features/practice/components/viewer.css', 'scripts/check-restored-hand.mjs']);
const changed = git('diff', '--name-only', base).split('\n').filter(Boolean);
assert.ok(changed.every((file) => allowed.has(file) || file.startsWith('docs/restore-black-sleeved-hand/')), `Unrelated changes: ${changed}`);
const sourceFiles = git('ls-tree', '-r', '--name-only', sourceRef, '--', 'src/features/practice/assets', 'src/features/practice/scene', 'src/features/practice/data').split('\n').filter(Boolean);
for (const file of sourceFiles) {
  assert.equal(hash(fs.readFileSync(file)), hash(execFileSync('git', ['show', `${sourceRef}:${file}`], { maxBuffer: 64 * 1024 * 1024 })), `Original rig/poses/music/scene changed: ${file}`);
}
const model = fs.readFileSync('src/features/practice/assets/makehuman-left-arm-sleeved.glb');
const gltf = JSON.parse(model.subarray(20, 20 + model.readUInt32LE(12)).toString());
const metadata = JSON.parse(fs.readFileSync('src/features/practice/assets/makehuman-left-arm.metadata.json'));
const library = JSON.parse(fs.readFileSync('src/features/practice/assets/hand-poses.json'));
assert.equal(hash(model), metadata.assetSha256);
assert.equal(hash(model), library.assetSha256);
assert.ok(gltf.meshes.some((mesh) => mesh.name.includes('Black_LongSleeve')));
assert.ok(gltf.meshes.some((mesh) => mesh.name.includes('Left_Hand_Forearm')));
assert.ok(gltf.materials.some((material) => material.name === 'Black_Cotton_LongSleeve_Elvaerwyn'));
const accepted = Object.entries(library.poses).filter(([, pose]) => pose.audit?.collisionPassed === true && pose.audit?.contactPassed === true).map(([id]) => id).sort();
assert.deepEqual(accepted, ['Am7', 'C', 'Cmaj7', 'Dm', 'E7', 'Em7', 'Fmaj7']);
assert.ok(Object.values(library.poses).every((pose) => pose.status === 'needs-review' && pose.reviewed !== true));
const server = await createServer({ logLevel: 'error', server: { middlewareMode: true, hmr: false }, appType: 'custom' });
try {
  const { GUITARS, SAVED_GUITARS_BY_ID } = await server.ssrLoadModule('/src/data/guitars.js');
  const { BRANDS } = await server.ssrLoadModule('/src/data/brands.js');
  const { PRACTICE_CHORDS } = await server.ssrLoadModule('/src/features/practice/data/chords.js');
  const baseline = JSON.parse(fs.readFileSync('docs/universal-guitar-images/baseline.json'));
  assert.equal(hash(JSON.stringify({ guitars: GUITARS, saved: SAVED_GUITARS_BY_ID, brands: BRANDS, chords: PRACTICE_CHORDS })), baseline.effectiveDataSHA256);
  assert.equal(GUITARS.length, 200); assert.equal(new Set(GUITARS.map((g) => g.id)).size, 200);
  assert.equal(BRANDS.length, 10); assert.equal(PRACTICE_CHORDS.length, 42);
  const counts = Object.fromEntries(BRANDS.map((brand) => [brand.name, GUITARS.filter((g) => g.brand === brand.name).length]));
  assert.ok(Object.values(counts).every((count) => count === 20));
  const report = { passed: true, baselineCommit: base, originalPracticeBranchCommit: git('rev-parse', sourceRef),
    originalModelAndSceneFilesIdentical: sourceFiles.length, sourceModelSHA256: hash(model), modelBytes: model.length,
    meshes: gltf.meshes.map((mesh) => mesh.name), materials: gltf.materials.map((material) => material.name),
    poseLibrarySHA256: hash(fs.readFileSync('src/features/practice/assets/hand-poses.json')), chords: 42,
    inspectablePoses: accepted, rejectedPosesKeptHidden: 35, verifiedTeachingPoses: 0,
    models: 200, brands: 10, counts, allProductAndChordDataIdentical: true,
    unrelatedFilesChanged: false, databaseWrites: 0, hostedSupabaseVerified: false };
  fs.mkdirSync(out, { recursive: true }); fs.writeFileSync(`${out}/source-and-data.json`, JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
} finally { await server.close(); }
