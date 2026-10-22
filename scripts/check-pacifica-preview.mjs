import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import os from 'node:os';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { createServer, resolveConfig } from 'vite';
import { ROOT, readCatalog, readReviewed, readArchive, readImageRights, findDuplicates, validateGuitar, photoStats } from './lib/catalog.mjs';
import { developmentImagePreview } from './vite/developmentImagePreview.mjs';

const ID = 'yamaha-pacifica-612viifm';
const baselineRef = '1229c669425f79505f9a9064cc5f28978984a793';
const fromGit = (file) => JSON.parse(execFileSync('git', ['show', `${baselineRef}:${file}`], { cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe'] }));
const records = readCatalog();
const reviewed = readReviewed();
const guitar = records.find((g) => g.id === ID);
const before = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/qa-pacifica-preview/audit-before.json'), 'utf8'));
const evidence = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/qa-pacifica-preview/manufacturer-evidence.json'), 'utf8'));
let checks = 0;
const check = (name, fn) => { fn(); checks++; console.log(`PASS ${name}`); };

check('200 models, ten brands, twenty per brand; no duplicate or changed identity', () => {
  assert.equal(records.length, 200);
  assert.equal(new Set(records.map((g) => g.brand)).size, 10);
  for (const brand of new Set(records.map((g) => g.brand))) assert.equal(records.filter((g) => g.brand === brand).length, 20);
  assert.deepEqual(findDuplicates([...records, ...readArchive()]), []);
  assert.deepEqual(records.map(({ id, brand, name, category }) => ({ id, brand, name, category })), before.map(({ id, brand, name, category }) => ({ id, brand, name, category })));
});
check('only the authorized reviewed model changed; all other 199 records and archives are intact', () => {
  const oldReviewed = fromGit('src/data/catalog/reviewedGuitars.json');
  assert.deepEqual(Object.keys(reviewed), Object.keys(oldReviewed));
  for (const [id, record] of Object.entries(reviewed)) if (id !== ID) assert.deepEqual(record, oldReviewed[id], id);
  assert.deepEqual(records.filter((g) => g.id !== ID), before.filter((g) => g.id !== ID));
  for (const file of ['extraGuitars.json', 'phase7Guitars.json', 'catalogPolicy.json', 'archivedGuitars.json', 'imageRights.json']) {
    assert.deepEqual(JSON.parse(fs.readFileSync(path.join(ROOT, 'src/data/catalog', file), 'utf8')), fromGit(`src/data/catalog/${file}`), file);
  }
});
check('all records satisfy catalog validation without claiming full verification', () => {
  for (const g of records) assert.deepEqual(validateGuitar(g), [], g.id);
  assert.equal(guitar.status, 'partial');
  assert.equal(guitar.rating, null); assert.deepEqual(guitar.colors, []);
  assert.equal(guitar.specs.bodyShape, null); assert.equal(guitar.specs.weightKg, null);
  assert.ok(validateGuitar({ ...guitar, status: 'verified' }).length > 0);
});
check('fresh manufacturer receipts and the exact PAC612VIIFM table column support the changes', () => {
  assert.equal(evidence.specificationTable.columnName, 'PAC612VIIFM');
  assert.equal(evidence.specificationTable.zeroBasedModelIndex, 4);
  for (const source of [guitar.source, guitar.priceSource, ...guitar.source.additionalSources]) {
    const receipt = evidence.retrievals.find((r) => r.url === source.url);
    assert.equal(receipt.httpStatus, 200); assert.equal(source.evidence.sha256, receipt.sha256);
    assert.equal(source.verifiedOn, receipt.accessedAt.slice(0, 10));
  }
  const rows = evidence.specificationTable.rows;
  assert.equal(guitar.specs.neckFinish, rows['Neck Finish']);
  assert.equal(guitar.specs.neckFinish, 'Gloss Polyurethane');
  assert.equal(guitar.specs.neckPickup, rows['Neck Pickup']);
  assert.equal(guitar.specs.middlePickup, rows['Middle Pickup']);
  assert.equal(guitar.specs.scaleMm, 648); assert.equal(guitar.specs.fingerboardRadiusMm, 350);
  assert.equal(guitar.specs.pickupConfiguration, 'HSS');
  assert.doesNotMatch(JSON.stringify(guitar.specs), /SP90|Satin|Fired Red/);
  for (const [key, value] of Object.entries(guitar.specs)) if (value != null) assert.ok(guitar.source.fields.includes(`specs.${key}`), key);
  assert.equal(guitar.price, 34000); assert.equal(guitar.priceSource.kind, 'manufacturer-recommended-retail');
  assert.ok(evidence.lineupBlock.includes('34,000.00'));
  assert.equal(records.filter((g) => g.price != null).length, 1);
});
check('AI illustration is excluded from licensed photos and the ignore rule protects local files', () => {
  assert.deepEqual(photoStats(records.map((g) => g.id)), { withPhotos: 2, placeholders: 198 });
  assert.equal(readImageRights()[ID], undefined);
  assert.equal(execFileSync('git', ['check-ignore', '.local-preview/yamaha-pacifica-612viifm-preview.png'], { cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe'] }).toString().trim(), '.local-preview/yamaha-pacifica-612viifm-preview.png');
});

const virtualId = '\0virtual:fretline-development-image-preview';
check('normal development module contains no illustration', () => {
  assert.equal(developmentImagePreview({ enabled: false, root: ROOT }).load(virtualId), 'export default null;');
});
check('a fresh Codespace starts the preview without private image files', () => {
  const empty = fs.mkdtempSync(path.join(os.tmpdir(), 'fretline-empty-images-'));
  try {
    const p = developmentImagePreview({ enabled: true, root: empty });
    const data = JSON.parse(p.load(virtualId).replace('export default ', '').slice(0, -1));
    assert.equal(data.guitarId, ID); assert.equal(data.images.length, 0); assert.equal(data.colors.length, 3);
    assert.equal(data.originalImageRightsVerified, false);
  } finally { fs.rmdirSync(empty); }
});
const plugin = developmentImagePreview({ enabled: true, root: ROOT });
const metadata = JSON.parse(plugin.load(virtualId).replace('export default ', '').slice(0, -1));
const hasPrivateOriginals = metadata.images.length === 4;
if (!hasPrivateOriginals) console.log('SKIP original image byte/dimension checks: private JPEGs are intentionally absent from Git.');
check('opt-in gallery keeps one model, three descriptive colors and original hashes when files are supplied', () => {
  const intake = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/qa-pacifica-multicolor/image-intake.json'), 'utf8'));
  assert.equal(metadata.guitarId, ID); assert.equal(metadata.colors.length, 3);
  assert.deepEqual(metadata.images.map((image) => image.id), hasPrivateOriginals ? ['black', 'red', 'blue-teal', 'all-colors'] : []);
  assert.equal(metadata.aiEdited, true); assert.equal(metadata.productPhotoVerified, false); assert.equal(metadata.originalImageRightsVerified, false);
  assert.equal(metadata.modelMatchVerified, false); assert.equal(metadata.officialColorNamesVerified, false);
  for (const item of hasPrivateOriginals ? intake.images : []) {
    const bytes = fs.readFileSync(path.join(ROOT, '.local-preview', ID, item.file));
    const image = metadata.images.find((entry) => entry.id === item.id);
    const digest = createHash('sha256').update(bytes).digest('hex');
    assert.equal(digest, item.sha256); assert.equal(image.sha256, digest);
    assert.equal(image.width, item.width); assert.equal(image.height, item.height);
    assert.equal(item.permissionVerified, false); assert.equal(item.modelMatchVerified, false);
  }
  if (hasPrivateOriginals) assert.equal(metadata.images[3].colorId, null);
});
check('multi-color update does not change any catalog record, rights registry or identity', () => {
  const hashes = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/qa-pacifica-multicolor/data-before-sha256.json'), 'utf8'));
  for (const [file, sha256] of Object.entries(hashes)) {
    assert.equal(createHash('sha256').update(fs.readFileSync(path.join(ROOT, file))).digest('hex'), sha256, file);
  }
});
check('preview middleware limits all four routes to the fixed model with no-store/noindex headers', () => {
  let handler;
  plugin.configureServer({ middlewares: { use(fn) { handler = fn; } } });
  const request = (url, method = 'GET') => {
    const response = { statusCode: 200, headers: {}, setHeader(k, v) { this.headers[k] = v; }, end(body) { this.body = body; } };
    handler({ url, method }, response, () => { response.next = true; });
    return response;
  };
  assert.equal(request('/unrelated').next, true);
  if (!hasPrivateOriginals) {
    assert.equal(request('/__fretline_development_preview__/missing.jpg').statusCode, 404);
    return;
  }
  const src = metadata.images[0].src;
  const good = request(src);
  assert.equal(good.statusCode, 200); assert.ok(Buffer.isBuffer(good.body));
  assert.equal(good.headers['Cache-Control'], 'no-store'); assert.match(good.headers['X-Robots-Tag'], /noindex/);
  assert.equal(request(src, 'HEAD').body, undefined);
  assert.equal(request(src, 'POST').statusCode, 405);
  assert.equal(request(src.replace(ID, 'yamaha-fg800')).statusCode, 404);
  assert.equal(request('/unrelated').next, true);
  for (const image of metadata.images) assert.equal(request(image.src).headers['Content-Type'], 'image/jpeg');
  assert.equal(request(src.replace('/black/', '/not-a-color/')).statusCode, 404);
});
for (const mode of ['production', 'pacifica-preview']) {
  const config = await resolveConfig({ mode, logLevel: 'silent' }, 'build');
  check(`build mode ${mode} always resolves an empty preview module`, () => {
    const p = config.plugins.find((entry) => entry.name === plugin.name);
    assert.equal(p.load(virtualId), 'export default null;');
  });
}

// Attach HMR to a non-listening server so data checks never need a TCP socket.
const internalHttp = http.createServer();
const vite = await createServer({ server: { middlewareMode: true, hmr: { server: internalHttp } }, appType: 'custom', logLevel: 'error' });
try {
  const { GUITARS, GUITARS_BY_ID } = await vite.ssrLoadModule('/src/data/guitars.js');
  const { trustedPrice, hasManufacturerRrp } = await vite.ssrLoadModule('/src/utils/dataTrust.js');
  const { analyseRows } = await vite.ssrLoadModule('/src/components/compare/compareRows.js');
  const { rankGuitars } = await vite.ssrLoadModule('/src/utils/quizScoring.js');
  check('all pages receive the same trusted price and source-gated specifications', () => {
    const pac = GUITARS_BY_ID[ID];
    assert.equal(GUITARS.length, 200); assert.equal(pac.price, 34000); assert.equal(trustedPrice(pac), 34000); assert.equal(hasManufacturerRrp(pac), true);
    assert.equal(trustedPrice({ ...pac, source: { ...pac.source, fields: pac.source.fields.filter((f) => f !== 'price') } }), null);
    assert.equal(trustedPrice({ ...pac, priceSource: null }), null);
    assert.equal(trustedPrice({ ...pac, priceSource: { ...pac.priceSource, currency: 'USD' } }), null);
    assert.equal(trustedPrice({ ...pac, dataStatus: 'sample' }), null);
    assert.equal(pac.specs.neckFinish, 'Gloss Polyurethane'); assert.equal(pac.specs.bodyShape, null);
    assert.equal(pac.hasPhotos, false); assert.equal(pac.gallery.length, 0); assert.equal(pac.image, null);
    for (const g of GUITARS.filter((g) => g.id !== ID)) assert.equal(g.price, null);
  });
  check('Compare receives optional sourced rows and the manufacturer RRP qualifier', () => {
    const rows = analyseRows([GUITARS_BY_ID[ID], GUITARS_BY_ID['yamaha-fg800']]);
    assert.equal(rows.find(({ row }) => row.key === 'neckFinish').valueOf(GUITARS_BY_ID[ID]), 'Gloss Polyurethane');
    assert.match(rows.find(({ row }) => row.key === 'price').displayOf(GUITARS_BY_ID[ID]), /34,000/);
    assert.equal(analyseRows([GUITARS_BY_ID['yamaha-fg800'], GUITARS_BY_ID['cordoba-c5']]).some(({ row }) => row.key === 'neckFinish'), false);
  });
  check('quiz ranking still uses real catalog IDs with finite scores', () => {
    const result = rankGuitars({ type: 'electric', level: 'intermediate', style: 'rock', budget: 'high', priority: 'versatile' }, 10, 0, GUITARS);
    assert.equal(result.length, 10);
    for (const item of result) { assert.ok(GUITARS_BY_ID[item.guitar.id]); assert.ok(Number.isFinite(item.score)); }
  });
} finally { await vite.close(); internalHttp.close(); }
console.log(`${checks} Pacifica data / preview checks passed.`);
