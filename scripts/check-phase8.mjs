import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readCatalog, readArchive, readPolicy, findDuplicates, validateGuitar, ROOT } from './lib/catalog.mjs';
import { assertPhase9DataBoundary } from './lib/phase9.mjs';

// Preserve the Phase 8 presentation boundary, allowing only the scoped Phase 9 review.
// This audit reads files only; browser behavior is checked by browser-phase8.py.
const BASELINE = '79025fe4c80f1bbb43a072bbfa6f79871da2fdbd';
const APPROVED_BRANDS = ['Yamaha', 'Fender', 'Epiphone', 'Ibanez', 'Taylor', 'Córdoba', 'Gibson', 'Martin', 'PRS', 'Squier'];
const records = readCatalog();
const archive = readArchive();
const policy = readPolicy();
const git = (...args) => execFileSync('git', args, { cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe'] });
let passed = 0;
const check = (name, fn) => { fn(); passed++; console.log(`PASS ${name}`); };

check('Phase 7 remains an ancestor of the current history', () => {
  git('merge-base', '--is-ancestor', BASELINE, 'HEAD');
});
check('the approved catalog remains exactly 200 models and 10 brands', () => {
  assert.equal(policy.target, 200);
  assert.equal(records.length, 200);
  assert.deepEqual(new Set(policy.brands), new Set(APPROVED_BRANDS));
  assert.deepEqual(new Set(records.map((guitar) => guitar.brand)), new Set(APPROVED_BRANDS));
});
check('every approved brand has exactly 20 models', () => {
  assert.equal(policy.modelsPerBrand, 20);
  for (const brand of APPROVED_BRANDS) assert.equal(records.filter((guitar) => guitar.brand === brand).length, 20, brand);
});
check('active and archived records have no duplicate IDs or normalized models', () => {
  assert.deepEqual(findDuplicates([...records, ...archive]), []);
  assert.equal(new Set(records.map((guitar) => guitar.id)).size, 200);
});
check('all 200 records still pass the existing data schema', () => {
  for (const guitar of records) assert.deepEqual(validateGuitar(guitar), [], guitar.id);
});
check('unknown prices and reviews remain unknown; partial is not promoted', () => {
  for (const guitar of [...records, ...archive]) {
    assert.equal(guitar.status, 'partial', guitar.id);
    assert.equal(guitar.price, null, guitar.id);
    assert.equal(guitar.rating, null, guitar.id);
  }
});
check('the two approved archives retain their original snapshots and sources', () => {
  assert.deepEqual(policy.archivedIds, ['gretsch-g2420-streamliner', 'yamaha-c40']);
  assert.deepEqual(archive.map((guitar) => guitar.id), policy.archivedIds);
  for (const guitar of archive) {
    assert.ok(!records.some((active) => active.id === guitar.id));
    assert.equal(guitar.previousPublishedSnapshot.id, guitar.id);
    assert.deepEqual(guitar.source, guitar.previousPublishedSnapshot.source);
  }
});
check('data/assets retain their Phase 7 bytes except the documented Phase 9 review and rights registry', () => {
  assertPhase9DataBoundary();
  const reviewedFiles = new Set(['src/data/catalog/reviewedGuitars.json', 'src/data/catalog/imageRights.json']);
  const files = git('ls-tree', '-r', '--name-only', BASELINE, '--', 'src/data', 'src/assets/guitars').toString().trim().split('\n');
  for (const file of files) {
    if (reviewedFiles.has(file)) continue; // Record-level assertions above still protect the other 180 models.
    const before = git('show', `${BASELINE}:${file}`);
    const after = fs.readFileSync(path.join(ROOT, file));
    assert.equal(createHash('sha256').update(after).digest('hex'), createHash('sha256').update(before).digest('hex'), file);
  }
});
console.log(`\n${passed}/${passed} checks passed`);
