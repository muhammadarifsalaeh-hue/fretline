/** Independent field-by-field check against retained manufacturer/retailer evidence. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
import { ROOT, readCatalog, readReviewed, validateGuitar } from './lib/catalog.mjs';
import { ADDITIONAL_SPECIFICATIONS } from '../src/data/additionalSpecifications.js';

const folder = path.join(ROOT, 'docs/yamaha-import');
const read = (file) => JSON.parse(fs.readFileSync(path.join(folder, file), 'utf8'));
const sha = (bytes) => createHash('sha256').update(bytes).digest('hex');
const records = readReviewed();
const manifest = read('preview-manifest.json');
const table = read('sources-a/official-table.json');
const lineup = read('sources-a/official-lineup.json');
const ids = manifest.models.map((model) => model.guitarId);
const rows = [];
const check = (name, fn) => { fn(); rows.push({ name, passed: true }); console.log(`PASS ${name}`); };
const textFields = {
  bodyShape: 'Body Shape', top: 'Top Material', back: 'Back Material', sides: 'Side Material',
  neck: 'Neck Material', fretboard: 'Fingerboard Material', bridge: 'Bridge Material',
  bodyDepth: 'Body Depth', nut: 'Nut Material', saddle: 'Saddle Material', bridgePins: 'Bridge Pins',
  tuners: 'Tuners', bodyBinding: 'Body Binding', soundholeInlay: 'Soundhole Inlay', pickguard: 'Pickguard',
  bodyFinish: 'Body Finish', neckFinish: 'Neck Finish', electronics: 'Electronics', controls: 'Controls',
  connections: 'Connections', factoryStrings: 'Strings', accessories: 'Accessories', case: 'Case',
};
const numericFields = {
  scaleMm: 'Scale Length', bodyLengthMm: 'Body Length', totalLengthMm: 'Total Length', bodyWidthMm: 'Body Width',
  nutWidthMm: 'Nut Width', stringSpacingMm: 'String Spacing *', fingerboardRadiusMm: 'Fingerboard Radius',
};
const expectedPrices = {
  'yamaha-fsx830c': 24000, 'yamaha-fsx800c': 15500, 'yamaha-fs800': 12400,
  'yamaha-fgx820c': 20500, 'yamaha-fg800m': 12400, 'yamaha-fg820l': 18200,
  'yamaha-fs830': 17500, 'yamaha-fg820': 15400, 'yamaha-fgx800c': 15500,
  'yamaha-fg840': 19200, 'yamaha-fg850': 19700, 'yamaha-fg800j': null,
  'yamaha-fg820-12': 16500, 'yamaha-fs850': 19700, 'yamaha-fg830': 17500,
  'yamaha-fsx820c': 20500, 'yamaha-fs820': 15400, 'yamaha-fg800': 12400,
};

check('exactly 18 accessible archives/models and 20 source images; no invented nineteenth file', () => {
  assert.equal(manifest.intendedArchiveCount, 19); assert.equal(manifest.archives.length, 18);
  assert.equal(ids.length, 18); assert.equal(new Set(ids).size, 18);
  assert.deepEqual(new Set(ids), new Set(Object.keys(expectedPrices)));
  assert.equal(manifest.models.reduce((n, model) => n + model.images.length, 0), 20);
  assert.ok(!ids.includes('yamaha-fgx830c')); assert.ok(!ids.includes('yamaha-pacifica-612viifm'));
});
check('catalog remains 200 unique stable IDs, 10 brands, 20 per brand', () => {
  const all = readCatalog(); assert.equal(all.length, 200); assert.equal(new Set(all.map((g) => g.id)).size, 200);
  const brands = new Map(); for (const g of all) brands.set(g.brand, (brands.get(g.brand) ?? 0) + 1);
  assert.equal(brands.size, 10); for (const count of brands.values()) assert.equal(count, 20);
});
check('every imported record meets the original catalog validator and retains honest partial status', () => {
  for (const id of ids) {
    const g = records[id]; assert.deepEqual(validateGuitar({ ...g, id }), [], id);
    assert.equal(g.status, 'partial'); assert.equal(g.intake.batch, 'yamaha-2026-10-26');
    assert.equal(g.intake.imageRights, 'unconfirmed'); assert.equal(g.specs.weightKg, null);
    assert.equal(g.specs.frets, null); assert.equal(g.rating ?? null, null);
    for (const [key, value] of Object.entries(g.specs)) if (value != null) assert.ok(g.source.fields.includes(`specs.${key}`), `${id}.${key}`);
  }
});
check('all 18 exact model columns match all 30 retained Yamaha specification fields', () => {
  for (const id of ids) {
    const g = records[id], official = table[g.source.manufacturerModel]; assert.ok(official, id);
    for (const [key, column] of Object.entries(textFields)) assert.equal(g.specs[key], official[column], `${id}.${key}`);
    for (const [key, column] of Object.entries(numericFields)) assert.equal(g.specs[key], Number(official[column].match(/[\d.]+/)[0]), `${id}.${key}`);
    assert.equal(g.specs.scale, Number((g.specs.scaleMm / 25.4).toFixed(2)));
    assert.ok(g.specs.body.includes(g.specs.top) && g.specs.body.includes(g.specs.back) && g.specs.body.includes(g.specs.sides));
    assert.equal(g.specs.bracing, 'Scalloped Bracing');
    assert.ok(lineup[g.source.manufacturerModel].some((text) => text.includes('Scalloped Bracing')));
  }
});
check('model distinctions stay correct: FG/FS scales, 12 strings, left-handed model and Matt finish', () => {
  assert.equal(records['yamaha-fg800'].specs.scaleMm, 650);
  assert.equal(records['yamaha-fg800j'].specs.scaleMm, 634);
  assert.equal(records['yamaha-fs800'].specs.scaleMm, 634);
  assert.equal(records['yamaha-fg820-12'].specs.strings, 12);
  assert.equal(records['yamaha-fg820-12'].specs.nutWidthMm, 46);
  assert.equal(records['yamaha-fg820-12'].specs.electronics, 'None');
  assert.equal(records['yamaha-fg800m'].specs.bodyFinish, 'Matt');
  assert.ok(lineup.FG820L.some((text) => /Lefty/i.test(text)));
  assert.ok(records['yamaha-fg820l'].keywords.includes('left-handed'));
  assert.ok(!records['yamaha-fgx820c-02']);
});
check('17 observed retailer prices are THB, date/source backed; FG800J stays unconfirmed', () => {
  for (const [id, expected] of Object.entries(expectedPrices)) {
    const g = records[id]; assert.equal(g.price, expected, id);
    if (expected == null) { assert.ok(!g.source.fields.includes('price')); assert.equal(g.priceSource ?? null, null); continue; }
    assert.ok(g.source.fields.includes('price')); assert.equal(g.priceSource.currency, 'THB');
    assert.equal(g.priceSource.kind, 'retailer-listed'); assert.equal(g.priceSource.retailer, 'Music Arms');
    assert.equal(g.priceSource.verifiedOn, '2026-10-26'); assert.ok(g.priceSource.url.startsWith('https://www.musicarms.net/'));
  }
});
check('additional source URLs are unique without losing their supported-field lists', () => {
  for (const id of ids) {
    const sources = records[id].source.additionalSources ?? [];
    assert.equal(new Set(sources.map((s) => s.url)).size, sources.length, id);
    assert.ok(sources.some((s) => s.url.endsWith('/lineup.html') && s.fields.includes('specs.bracing')), id);
  }
});
check('retained original HTTP evidence hashes match the bodies used for price/specification review', () => {
  for (const evidence of [...read('sources-a/fetch.json'), ...read('sources-a/fetch-additional.json')]) {
    const bytes = gunzipSync(fs.readFileSync(path.join(folder, 'sources-a', `${evidence.key}.html.gz`)));
    assert.equal(sha(bytes), evidence.sha256); assert.equal(bytes.length, evidence.bytes);
  }
  for (const evidence of read('sources-b/raw-evidence.json')) {
    const bytes = gunzipSync(fs.readFileSync(path.join(folder, 'sources-b', evidence.rawFile)));
    assert.equal(sha(bytes), evidence.rawSha256); assert.equal(bytes.length, evidence.rawBytes);
    assert.equal(evidence.priceTHB, expectedPrices[evidence.id]);
    assert.ok(bytes.toString('utf8').includes(evidence.model));
    assert.equal(records[evidence.id].priceSource.evidence.sha256, evidence.rawSha256);
    assert.ok(evidence.modelPriceHeader.includes(evidence.priceTHB.toLocaleString('en-US')));
  }
});
check('every original non-image attachment remains available byte-for-byte as unverified provenance', () => {
  for (const archive of manifest.archives) for (const file of archive.files) {
    if (/\.(png|jpe?g|webp|avif)$/i.test(file.path)) continue;
    assert.equal(sha(fs.readFileSync(path.join(folder, 'original-metadata', file.path))), file.sha256);
  }
});
check('new verified specification keys have shared Detail/Compare definitions and both translations', () => {
  const core = new Set(['body', 'neck', 'fretboard', 'pickups', 'bridge', 'controls', 'scale', 'scaleMm', 'strings', 'frets', 'weightKg']);
  for (const id of ids) for (const key of Object.keys(records[id].specs)) if (!core.has(key)) {
    const field = ADDITIONAL_SPECIFICATIONS.find((entry) => entry.key === key); assert.ok(field, key);
    for (const language of ['th', 'en']) assert.ok(fs.readFileSync(path.join(ROOT, `src/i18n/${language}.js`), 'utf8').includes(`"${field.label}"`), `${language}.${key}`);
  }
});
check('production build contains no newly supplied image bytes or development preview asset routes', () => {
  const files = fs.readdirSync(path.join(ROOT, 'dist/assets')).map((name) => fs.readFileSync(path.join(ROOT, 'dist/assets', name)));
  const hashes = new Set(files.map(sha));
  for (const model of manifest.models) for (const image of model.images) assert.ok(!hashes.has(image.sha256));
  for (const bytes of files) assert.ok(!bytes.includes(Buffer.from('/__fretline_yamaha_import_preview__/')));
  assert.ok(!fs.existsSync(path.join(ROOT, 'dist/docs')));
});

fs.writeFileSync(path.join(folder, 'tests/data-check.json'), JSON.stringify({ passed: true, checks: rows, count: rows.length, importedIds: ids, observedPricesTHB: expectedPrices, sourceSha256: sha(fs.readFileSync(path.join(ROOT, 'src/data/catalog/reviewedGuitars.json'))) }, null, 2) + '\n');
console.log(`${rows.length} Yamaha import evidence/isolation checks passed.`);
