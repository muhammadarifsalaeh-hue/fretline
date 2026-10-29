import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { mergeCatalogRecords, normalizeSpecEvidence, parseCSV, validateIntake, verifyArchiveRepresentations } from '../../../scripts/import-catalog-prices-20261029.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const HERE = path.dirname(fileURLToPath(import.meta.url));
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));
const copy = (v) => structuredClone(v);
const tests = [];
const run = (name, fn) => {
  try { fn(); tests.push({ name, passed: true }); console.log('PASS', name); }
  catch (error) { tests.push({ name, passed: false, error: error.stack }); console.error('FAIL', name, error.stack); }
};
function fixture() {
  const id = 'fender-test-model';
  const record = { id, brand: 'Fender', name: 'Test Model', category: 'electric', price: null, status: 'partial',
    description: 'Existing sourced description', image: 'keep.webp', gallery: [{ src: 'keep.webp' }],
    rating: null, oldPrice: null, colors: [{ name: 'Existing finish' }],
    specs: { body: 'Alder / Ash', fretboard: 'Maple / Rosewood', frets: 22, strings: null },
    source: { url: 'https://www.fender.com/products/test-model', verifiedOn: '2026-10-20', method: 'http', manufacturerModel: 'Test Model',
      fields: ['brand', 'name', 'category', 'description', 'specs.body', 'specs.fretboard', 'specs.frets'],
      evidence: { sha256: 'keep-manufacturer-evidence' }, priceNote: 'Old price note',
      additionalSources: [{ url: 'https://www.fender.com/old', fields: ['specs.body'], verifiedOn: '2026-10-20' }] } };
  const incoming = [{ id, brand: 'Fender', model: 'Test Model', category: 'electric', price_thb: 30600,
    description_th: 'Unverified editorial substitute', comparison_specs: { body_wood: 'Alder', strings: 6 }, colors: [], image_files: [],
    price_reference: { amount_thb: 30600, currency: 'THB', source_url: 'https://www.musicarms.net/category/list/' } }];
  return { incoming, baseline: [copy(record)], reviewed: { [id]: record }, phase7: [], priceEvidence: [], specEvidence: [] };
}
const id = 'fender-test-model';
const price = (extra = {}) => ({ id, model: 'Test Model', accepted: true, acceptedAmountTHB: 30600,
  candidateAmountTHB: 30600, currency: 'THB', checkedOn: '2026-10-29', httpStatus: 200,
  sourceURL: 'https://www.musicarms.net/test-model/', sourceKind: 'retailer-listed', sourceLabel: 'Music Arms',
  quote: 'Test Model; Product Offer price 30600 THB', ...extra });
const spec = (key, value, extra = {}) => ({ id, canonicalKey: key, value, accepted: true, checkedOn: '2026-10-29',
  sourceURL: 'https://www.musicarms.net/test-model/', sourceKind: 'retailer-specifications',
  quote: `${key}: ${value}`, evidence: { httpStatus: 200 }, ...extra });

run('Pure merge leaves its complete input objects unchanged', () => {
  const f = fixture(); f.priceEvidence = [price()]; const original = copy(f);
  mergeCatalogRecords(f); assert.deepEqual(f, original);
});
run('New THB price gets precise retailer/date/evidence without manufacturer promotion', () => {
  const f = fixture(); f.priceEvidence = [price()]; const r = mergeCatalogRecords(f); const g = r.reviewed[id];
  assert.equal(g.price, 30600); assert.equal(g.priceSource.currency, 'THB'); assert.equal(g.priceSource.verifiedOn, '2026-10-29');
  assert.equal(g.priceSource.kind, 'retailer-listed'); assert.equal(g.priceSource.availability, 'unknown');
  assert.equal(g.priceSource.url, price().sourceURL); assert.equal(g.status, 'partial'); assert.equal(g.oldPrice, null);
  for (const key of ['url', 'verifiedOn', 'method', 'manufacturerModel', 'evidence']) assert.deepEqual(g.source[key], f.reviewed[id].source[key]);
  assert.ok(g.source.fields.includes('price')); assert.ok(g.source.additionalSources.some((s) => s.kind === 'retailer-listed' && s.fields.includes('price')));
});
run('Retailer evidence does not alter identities, category, descriptions, photos, colors or reviews', () => {
  const f = fixture(); f.priceEvidence = [price()]; const g = mergeCatalogRecords(f).reviewed[id];
  for (const key of ['id', 'brand', 'name', 'category', 'description', 'image', 'gallery', 'colors', 'rating']) assert.deepEqual(g[key], f.reviewed[id][key]);
});
run('Incoming null, blank and zero prices cannot erase an existing source-backed price', () => {
  for (const value of [null, '', ' ', 0]) {
    const f = fixture(); f.reviewed[id].price = f.baseline[0].price = 16500;
    const oldSource = { currency: 'THB', url: 'https://www.musicarms.net/old-price/', verifiedOn: '2026-10-26', kind: 'retailer-listed' };
    f.reviewed[id].priceSource = copy(oldSource); f.reviewed[id].source.fields.push('price');
    f.incoming[0].price_thb = f.incoming[0].price_reference.amount_thb = value; f.priceEvidence = [price({ acceptedAmountTHB: value })];
    const g = mergeCatalogRecords(f).reviewed[id]; assert.equal(g.price, 16500); assert.deepEqual(g.priceSource, oldSource);
    assert.equal(g.source.priceNote, 'Old price note');
  }
});
run('An existing primary price/source wins even over a newer different valid quote', () => {
  const f = fixture(); f.reviewed[id].price = f.baseline[0].price = 16500; f.priceEvidence = [price()];
  const r = mergeCatalogRecords(f); assert.equal(r.reviewed[id].price, 16500); assert.equal(r.report.newPrices, 0); assert.equal(r.report.priceConflicts.length, 1);
});
run('Zero, negative and nonnumeric new prices remain unknown, never become THB0', () => {
  for (const value of [0, -5, '30600', null, ' ']) {
    const f = fixture(); f.incoming[0].price_thb = f.incoming[0].price_reference.amount_thb = value;
    f.priceEvidence = [price({ acceptedAmountTHB: value })]; assert.equal(mergeCatalogRecords(f).reviewed[id].price, null);
  }
});
run('Unaccepted, non-THB, missing quote and HTTP403 price evidence are refused', () => {
  for (const patch of [{ accepted: false }, { currency: 'USD' }, { quote: '' }, { httpStatus: 403 }]) {
    const f = fixture(); f.priceEvidence = [price(patch)]; assert.equal(mergeCatalogRecords(f).report.newPrices, 0);
  }
});
run('Wrong model, mismatch amount and mismatched observed Offer are refused', () => {
  for (const patch of [{ model: 'Another Model' }, { acceptedAmountTHB: 31500 }, { productPriceObserved: { price: 31500, priceCurrency: 'THB' } }]) {
    const f = fixture(); f.priceEvidence = [price(patch)]; assert.equal(mergeCatalogRecords(f).report.newPrices, 0);
  }
});
run('Search URLs and retailer category pages cannot be precise primary price evidence', () => {
  for (const sourceURL of ['https://www.google.com/search?q=model', 'https://www.musicarms.net/category/guitars/', 'http://www.musicarms.net/test-model/']) {
    const f = fixture(); f.priceEvidence = [price({ sourceURL })]; assert.equal(mergeCatalogRecords(f).report.newPrices, 0);
  }
});
run('Invalid source dates are refused; verifiedOn aliases remain stored correctly', () => {
  const f = fixture(); f.priceEvidence = [price({ checkedOn: '2026-02-31' })]; assert.equal(mergeCatalogRecords(f).report.newPrices, 0);
  f.priceEvidence = [price({ checkedOn: undefined, verifiedOn: '2026-10-29' })];
  assert.equal(mergeCatalogRecords(f).reviewed[id].priceSource.verifiedOn, '2026-10-29');
});
run('Unknown evidence IDs never create a product', () => {
  const f = fixture(); f.priceEvidence = [price({ id: 'unknown-model' })]; const r = mergeCatalogRecords(f);
  assert.deepEqual(Object.keys(r.reviewed), [id]); assert.equal(r.report.newPrices, 0);
});
run('Incoming duplicate, missing and replaced IDs abort rather than silently changing inventory', () => {
  const f = fixture(); assert.throws(() => mergeCatalogRecords({ ...f, incoming: [f.incoming[0], f.incoming[0]] }), /duplicate ID/);
  assert.throws(() => mergeCatalogRecords({ ...f, incoming: [] }), /ID sets/);
  assert.throws(() => mergeCatalogRecords({ ...f, incoming: [{ ...f.incoming[0], id: 'another-id' }] }), /ID sets/);
});
run('A matching ID cannot rename a brand or model', () => {
  const f = fixture(); f.incoming[0].model = 'Not the existing model'; assert.throws(() => mergeCatalogRecords(f), /Identity mismatch/);
});
run('Only accepted missing specifications fill; raw editorial strings are never technical evidence', () => {
  const f = fixture(); const r = mergeCatalogRecords(f);
  assert.equal(r.reviewed[id].specs.strings, null); assert.equal(r.report.newSpecificationFields, 0);
  f.specEvidence = [spec('bodyShape', 'Stratocaster')]; const g = mergeCatalogRecords(f).reviewed[id];
  assert.equal(g.specs.bodyShape, 'Stratocaster'); assert.ok(g.source.fields.includes('specs.bodyShape'));
});
run('Narrower SKU woods and fretboard values never replace broader existing options', () => {
  const f = fixture(); f.specEvidence = [spec('body', 'Alder'), spec('fretboard', 'Maple')];
  const g = mergeCatalogRecords(f).reviewed[id]; assert.equal(g.specs.body, 'Alder / Ash'); assert.equal(g.specs.fretboard, 'Maple / Rosewood');
});
run('Null, blank and invalid numeric specifications cannot erase or fabricate existing values', () => {
  const f = fixture(); f.specEvidence = [spec('body', null), spec('fretboard', ' '), spec('scaleMm', 0), spec('strings', 0)];
  const r = mergeCatalogRecords(f); assert.equal(r.report.newSpecificationFields, 0); assert.equal(r.reviewed[id].specs.body, 'Alder / Ash');
});
run('A sourced fretless zero is a valid fact; numeric zero remains invalid for price/scale/strings', () => {
  const f = fixture(); f.reviewed[id].specs.frets = f.baseline[0].specs.frets = null;
  f.specEvidence = [spec('frets', 0, { quote: 'Fretless; Number of frets: 0' }), spec('scaleMm', 0), spec('strings', 0)];
  const r = mergeCatalogRecords(f); assert.equal(r.reviewed[id].specs.frets, 0); assert.equal(r.report.newSpecificationFields, 1);
});
run('Existing fretless zero is retained when another source proposes frets', () => {
  const f = fixture(); f.reviewed[id].specs.frets = f.baseline[0].specs.frets = 0; f.specEvidence = [spec('frets', 22)];
  assert.equal(mergeCatalogRecords(f).reviewed[id].specs.frets, 0);
});
run('Unaccepted, unsupported and HTTP403 specifications are refused', () => {
  const f = fixture(); f.specEvidence = [spec('strings', 6, { accepted: false }), spec('unsupportedField', 'anything'), spec('scaleMm', 648, { evidence: { httpStatus: 403 } })];
  assert.equal(mergeCatalogRecords(f).report.newSpecificationFields, 0);
});
run('Retailer specification evidence stays explicitly retailer-sourced, without verified status', () => {
  const f = fixture(); f.specEvidence = [spec('bodyShape', 'Stratocaster'), spec('pickupConfiguration', 'SSS')];
  const g = mergeCatalogRecords(f).reviewed[id]; const extra = g.source.additionalSources.filter((s) => s.batch);
  assert.equal(extra.length, 1); assert.equal(extra[0].kind, 'retailer-specifications'); assert.equal(extra[0].fields.length, 2);
  assert.equal(g.status, 'partial'); assert.deepEqual(g.source.additionalSources[0], f.reviewed[id].source.additionalSources[0]);
});
run('Evidence adapters honor explicit rejected fields and canonical keys', () => {
  const entries = normalizeSpecEvidence([{ acceptedSpecs: [spec('top', 'Solid Spruce')] }, { id, fields: { strings: { accepted: false, value: null }, bodyShape: { accepted: true, value: 'Stratocaster' } } }]);
  assert.equal(entries.length, 3); assert.equal(entries.find((r) => r.canonicalKey === 'strings').accepted, false);
});
run('Reviewed datastore wins over a duplicate phase7 backing row', () => {
  const f = fixture(); f.phase7 = [{ ...copy(f.reviewed[id]), price: 99999 }]; f.priceEvidence = [price()];
  const r = mergeCatalogRecords(f); assert.equal(r.reviewed[id].price, 30600); assert.equal(r.phase7[0].price, 99999);
});
run('Phase7-only records update in place without reordering or introducing a reviewed override', () => {
  const f = fixture(); f.phase7 = [f.reviewed[id]]; f.reviewed = {}; f.priceEvidence = [price()];
  const r = mergeCatalogRecords(f); assert.deepEqual(Object.keys(r.reviewed), []); assert.equal(r.phase7[0].id, id); assert.equal(r.phase7[0].price, 30600);
});
run('Applying an already-merged result is idempotent, including sources and field arrays', () => {
  const f = fixture(); f.priceEvidence = [price(), price()]; f.specEvidence = [spec('bodyShape', 'Stratocaster')];
  const once = mergeCatalogRecords(f); const twice = mergeCatalogRecords({ ...f, reviewed: once.reviewed, phase7: once.phase7 });
  assert.deepEqual(twice.reviewed, once.reviewed); assert.equal(twice.report.changedModels, 0); assert.equal(twice.report.newPrices, 0);
});
run('CSV reader handles BOM, quoted commas, escaped quotes and CRLF', () => {
  assert.deepEqual(parseCSV('\uFEFFid,model\r\none,"Name, with ""quotes"""\r\n'), [{ id: 'one', model: 'Name, with "quotes"' }]);
  assert.throws(() => parseCSV('id,id\na,b\n'), /Duplicate CSV header/); assert.throws(() => parseCSV('id,model\na,"broken'), /Unclosed CSV quote/);
});

const incoming = read('docs/catalog-update-2026-10-29/intake/ALL_200_WITH_PRICES.json');
const baseline = read('docs/catalog-update-2026-10-29/baseline-effective.json');
const historical = (p) => JSON.parse(execFileSync('git', ['show', `edc293f:${p}`], { cwd: ROOT, encoding: 'utf8' }));
const actual = { incoming, baseline, reviewed: historical('src/data/catalog/reviewedGuitars.json'), phase7: historical('src/data/catalog/phase7Guitars.json'),
  priceEvidence: read('docs/catalog-update-2026-10-29/verification/fender-sources.json'),
  specEvidence: [read('docs/catalog-update-2026-10-29/verification/yamaha-sources.json'), read('docs/catalog-update-2026-10-29/verification/fender-specs.json')] };
run('Actual archive covers exactly original200 IDs,10 brands×20, and all JSON/CSV representations agree', () => {
  assert.equal(validateIntake(incoming, baseline).models, 200);
  assert.deepEqual(verifyArchiveRepresentations(path.join(ROOT, 'docs/catalog-update-2026-10-29/intake'), incoming), { perBrandJSONFiles: 10, priceCSVFiles: 10, aggregateMatches: true });
});
const plan = mergeCatalogRecords(actual);
run('Actual import plan is exactly nine verified new prices plus nine missing fields on ten models', () => {
  assert.equal(plan.report.newPrices, 9); assert.equal(plan.report.newSpecificationFields, 9); assert.equal(plan.report.changedModels, 10);
  assert.equal(plan.report.pricedModelsBefore, 18); assert.equal(plan.report.pricedModelsAfter, 27);
});
run('Actual null prices keep all18 old prices, FG820-12 quote and broader manufacturer fields', () => {
  const winner = (id) => plan.reviewed[id] ?? plan.phase7.find((r) => r.id === id);
  for (const g of baseline.filter((r) => r.price != null)) assert.equal(winner(g.id).price, g.price);
  assert.equal(winner('yamaha-fg820-12').price, 16500);
  assert.deepEqual(winner('yamaha-fg800j').specs, actual.reviewed['yamaha-fg800j'].specs);
  const old = actual.phase7.find((r) => r.id === 'fender-player-ii-stratocaster'); const now = winner(old.id);
  assert.equal(now.specs.body, old.specs.body); assert.equal(now.specs.fretboard, old.specs.fretboard);
  assert.equal(now.specs.fingerboardRadiusMm, 241); assert.equal(now.specs.strings, old.specs.strings);
});
run('Actual Thunderbird category and full200 inventory/order/status stay unchanged', () => {
  assert.deepEqual(plan.phase7.map((r) => r.id), actual.phase7.map((r) => r.id));
  assert.deepEqual(Object.keys(plan.reviewed), Object.keys(actual.reviewed));
  const winner = (id) => plan.reviewed[id] ?? plan.phase7.find((r) => r.id === id);
  assert.equal(winner('epiphone-thunderbird-64-with-rosewood-fretboard').category, 'bass');
  for (const g of baseline) {
    const row = winner(g.id); const old = actual.reviewed[g.id] ?? actual.phase7.find((r) => r.id === g.id);
    for (const k of ['brand', 'name', 'category', 'description', 'colors', 'rating', 'status']) assert.deepEqual(row[k], old[k]);
    for (const k of ['url', 'verifiedOn', 'method', 'manufacturerModel', 'evidence']) assert.deepEqual(row.source[k], old.source[k]);
  }
});
run('Actual complete import is idempotent with zero repeated data changes', () => {
  const r = mergeCatalogRecords({ ...actual, reviewed: plan.reviewed, phase7: plan.phase7 });
  assert.deepEqual(r.reviewed, plan.reviewed); assert.deepEqual(r.phase7, plan.phase7); assert.equal(r.report.changedModels, 0); assert.equal(r.report.changes.length, 0);
});
const report = { passed: tests.every((t) => t.passed), passedChecks: tests.filter((t) => t.passed).length, totalChecks: tests.length, tests };
fs.writeFileSync(path.join(HERE, 'importer-results.json'), JSON.stringify(report, null, 2) + '\n');
console.log(`${report.passedChecks}/${report.totalChecks} importer checks passed`);
if (!report.passed) process.exitCode = 1;
