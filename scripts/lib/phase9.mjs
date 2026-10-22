import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { ROOT, readCatalog, readImageRights } from './catalog.mjs';

export const PHASE9_BASELINE = '0f00def4f524de10f3f59f711bd43f2d0a50bc8c';
export const batchEvidence = () => JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/qa-phase9/field-evidence.json'), 'utf8'));
export const batchIds = () => new Set(batchEvidence().map((record) => record.id));
export const baselineFile = (file) => execFileSync('git', ['show', `${PHASE9_BASELINE}:${file}`], { cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe'] });

/** Reconstruct effective baseline facts from Git, independently of the audit snapshot. */
export function baselineCatalog() {
  const raw = baselineFile('src/data/guitars.js').toString();
  const samples = [...raw.matchAll(/id: '([^']+)',\n\s+brand: '([^']+)',\n\s+name: '((?:[^'\\]|\\.)*)'/g)]
    .map((match) => ({ id: match[1], brand: match[2], name: match[3].replace(/\\'/g, "'"), status: 'sample' }));
  const json = (file) => JSON.parse(baselineFile(`src/data/catalog/${file}.json`).toString());
  const reviewed = json('reviewedGuitars');
  const archived = new Set(json('catalogPolicy').archivedIds);
  return [...samples, ...json('extraGuitars'), ...json('phase7Guitars')]
    .filter((record) => !archived.has(record.id))
    .map((record) => ({ ...record, ...reviewed[record.id], id: record.id }));
}

/** Keep historical regression guards while allowing this explicit 20-model review. */
export function assertPhase9DataBoundary() {
  const selected = batchIds();
  assert.equal(selected.size, 20);
  const current = readCatalog();
  const baseline = baselineCatalog();
  assert.deepEqual(current.map((g) => g.id), baseline.map((g) => g.id));
  for (const old of baseline) {
    const record = current.find((g) => g.id === old.id);
    for (const key of ['id', 'brand', 'name', 'category']) assert.deepEqual(record[key], old[key], `${old.id}/${key}`);
    if (!selected.has(old.id)) assert.deepEqual(record, old, `Out-of-batch change: ${old.id}`);
  }
  const oldRights = JSON.parse(baselineFile('src/data/catalog/imageRights.json').toString());
  const rights = readImageRights();
  for (const [id, photos] of Object.entries(oldRights)) assert.deepEqual(rights[id], photos, `Existing image changed: ${id}`);
  assert.deepEqual(Object.keys(rights).filter((id) => !Object.hasOwn(oldRights, id)), ['martin-d-28']);
  for (const id of selected) assert.ok(current.find((g) => g.id === id)?.source.batch === 'phase9-batch1', id);
}
