import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { createServer } from 'vite';
import { ROOT, readCatalog, readImageRights, readArchive, findDuplicates, validateGuitar, photoStats } from './lib/catalog.mjs';
import { PHASE9_BASELINE, baselineCatalog, batchEvidence, assertPhase9DataBoundary } from './lib/phase9.mjs';
import { hasImageRights } from '../src/utils/imageRights.js';

const read = (file) => JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/qa-phase9', file), 'utf8'));
const records = readCatalog();
const original = baselineCatalog();
const evidence = batchEvidence();
const selected = new Set(evidence.map((guitar) => guitar.id));
const retrievals = read('source-retrievals.json');
const rights = readImageRights();
let passed = 0;
const check = (name, fn) => { fn(); passed++; console.log(`PASS ${name}`); };

check('the audit snapshot equals the effective Phase 8 Git baseline', () => {
  assert.equal(PHASE9_BASELINE.slice(0, 7), '0f00def');
  assert.deepEqual(read('audit-before.json'), original);
  assert.deepEqual(read('audit-after.json'), records);
});
check('the first batch is exactly two existing models per approved brand', () => {
  assert.equal(evidence.length, 20); assert.equal(selected.size, 20);
  assert.deepEqual(new Set(read('selection.json').map((g) => g.id)), selected);
  for (const brand of new Set(records.map((g) => g.brand))) assert.equal(evidence.filter((g) => g.brand === brand).length, 2, brand);
});
check('all 200 identities and the other 180 complete records are unchanged', assertPhase9DataBoundary);
check('exactly 200 models, ten brands, twenty per brand, with no duplicate IDs or models', () => {
  assert.equal(records.length, 200);
  const brands = new Set(records.map((g) => g.brand)); assert.equal(brands.size, 10);
  for (const brand of brands) assert.equal(records.filter((g) => g.brand === brand).length, 20, brand);
  assert.deepEqual(findDuplicates([...records, ...readArchive()]), []);
});
check('all records pass the unchanged catalog criteria', () => {
  for (const guitar of records) assert.deepEqual(validateGuitar(guitar), [], guitar.id);
});
check('each selected model has freshly retrieved successful manufacturer evidence, date and hash', () => {
  const hosts = new Set(['my.yamaha.com', 'eu.fender.com', 'www.fender.com', 'www.gibson.com', 'www.ibanez.com', 'www.taylorguitars.com', 'www.martinguitar.com', 'support.prsguitars.com', 'cordobaguitars.com']);
  for (const item of evidence) {
    const guitar = records.find((g) => g.id === item.id);
    const source = guitar.source;
    const receipt = retrievals.find((entry) => entry.sha256 === item.retrievedSha256 && entry.httpStatus === 200);
    assert.ok(receipt, item.id); assert.ok(hosts.has(new URL(source.url).hostname));
    assert.equal(source.url, item.sourceUrl); assert.equal(source.evidence.sha256, receipt.sha256);
    assert.equal(source.evidence.httpStatus, 200); assert.match(receipt.sha256, /^[a-f0-9]{64}$/);
    assert.equal(source.verifiedOn, receipt.accessedAt.slice(0, 10));
    assert.equal(source.verifiedOn, item.verifiedOn); assert.ok(source.manufacturerModel);
    assert.equal(source.manufacturerModel, item.manufacturerModel);
    for (const key of ['brand', 'name', 'category']) assert.equal(guitar[key], item[key]);
  }
});
check('checked facts and retained facts are distinguished; no unknown field is silently filled', () => {
  for (const item of evidence) {
    const guitar = records.find((g) => g.id === item.id);
    const old = original.find((g) => g.id === item.id);
    for (const [field, fact] of Object.entries(item.fields)) {
      const key = field.replace('specs.', '');
      assert.equal(guitar.specs[key], fact.value, `${item.id}/${field}`);
      if (fact.review === 'checked') {
        assert.ok(fact.observed.length > 5); assert.ok(guitar.source.recheckedFields.includes(field));
        assert.ok(guitar.source.fields.includes(field));
      } else if (fact.review === 'retained') {
        assert.equal(fact.value, old.specs[key]); assert.equal(fact.sourceUrl, old.source.url);
        assert.ok(guitar.source.retainedFields.includes(field));
      } else { assert.equal(fact.review, 'unknown'); assert.equal(fact.value, null); }
    }
    for (const [key, value] of Object.entries(guitar.specs)) if (value != null) assert.ok(item.fields[`specs.${key}`], `${item.id}/${key}`);
  }
});
check('no selected record is called fully verified without price, weight and complete evidence', () => {
  for (const guitar of records) {
    assert.equal(guitar.status, 'partial'); assert.equal(guitar.price, null); assert.equal(guitar.rating, null);
    assert.equal(guitar.specs.weightKg, null);
    assert.ok(validateGuitar({ ...guitar, status: 'verified' }).length > 0);
  }
});
check('known omissions and edition limitations are preserved instead of guessed', () => {
  const get = (id) => records.find((g) => g.id === id);
  assert.equal(get('yamaha-fg800').specs.strings, null);
  assert.equal(get('yamaha-fg830').specs.frets, null);
  assert.equal(get('taylor-gs-mini').specs.frets, null);
  assert.equal(get('taylor-214ce').specs.controls, null);
  assert.equal(get('martin-d-28').specs.strings, null);
  assert.match(get('gibson-j-45-standard').source.editionNote, /ไม่จำหน่าย/);
  assert.match(get('epiphone-les-paul-standard-50s').source.editionNote, /Laurel/);
  assert.match(get('fender-player-ii-telecaster').source.editionNote, /SKU/);
  for (const id of ['prs-se-custom-24', 'prs-se-mccarty-594-singlecut']) {
    assert.equal(get(id).source.documentYear, 2025);
    assert.match(get(id).source.manufacturerModel, /2025/);
    assert.match(get(id).source.url, /#page=[34]$/);
  }
  assert.ok(retrievals.some((r) => r.ids.includes('prs-se-custom-24') && r.httpStatus === 403));
});
check('newly filled specifications have explicit manufacturer evidence and correct unit semantics', () => {
  const get = (id) => records.find((g) => g.id === id);
  assert.equal(get('cordoba-c5').specs.bridge, 'Rosewood');
  assert.equal(get('cordoba-c5').specs.pickups, 'None (manufacturer N/A)');
  assert.equal(get('cordoba-c5').specs.frets, 19);
  assert.equal(get('gibson-j-45-standard').specs.strings, 6);
  assert.match(get('prs-se-mccarty-594-singlecut').specs.controls, /2 volume, 2 push\/pull/);
  assert.equal(get('ibanez-sr300e').specs.scaleMm, 864);
  assert.equal(get('gibson-les-paul-standard-60s').specs.scaleMm, 628.65);
  assert.equal(get('prs-se-custom-24').specs.neck, 'Maple; Wide Thin profile');
  assert.match(get('martin-d-28').specs.neck, /GE Modified Low Oval/);
});
check('one authorized new model photo leaves 198 placeholders; the existing photo is retained', () => {
  assert.deepEqual(photoStats(records.map((g) => g.id)), { withPhotos: 2, placeholders: 198 });
  assert.deepEqual(Object.keys(rights).sort(), ['martin-d-28', 'yamaha-fg820-12']);
  const photo = rights['martin-d-28'][0]; const license = read('image-license-evidence.json');
  assert.ok(hasImageRights(photo, 'martin-d-28'));
  assert.equal(photo.author, license.author); assert.equal(photo.licenseUrl, license.licenseUrl);
  assert.equal(photo.originalSha256, license.originalSha256);
  assert.match(photo.caption, /2018/); assert.match(photo.caption, /Golden Era/);
  assert.match(photo.modelMatchNote, /production year is unknown/);
  assert.equal(photo.variants.length, 2); assert.ok(photo.bytes < 150000);
  for (const file of [photo, ...photo.variants]) {
    const bytes = fs.readFileSync(path.join(ROOT, 'src/assets/guitars/martin-d-28', file.file));
    assert.equal(bytes.length, file.bytes); assert.equal(createHash('sha256').update(bytes).digest('hex'), file.sha256);
    assert.ok(Math.abs(file.width / file.height - 2376 / 3156) < 0.002);
  }
});

const server = await createServer({ server: { middlewareMode: true, hmr: false }, appType: 'custom', logLevel: 'error' });
try {
  const { GUITARS, GUITARS_BY_ID } = await server.ssrLoadModule('/src/data/guitars.js');
  const { matchesQuery } = await server.ssrLoadModule('/src/utils/search.js');
  const { rankGuitars, SCORE_WEIGHTS } = await server.ssrLoadModule('/src/utils/quizScoring.js');
  check('browser and CLI agree on all scoped facts and all 200 models remain searchable', () => {
    assert.equal(GUITARS.length, records.length);
    for (const guitar of records) {
      const published = GUITARS_BY_ID[guitar.id];
      assert.ok(published); assert.ok(matchesQuery(published, guitar.name), guitar.id);
      for (const [key, value] of Object.entries(guitar.specs)) assert.equal(published.specs[key], value, `${guitar.id}/${key}`);
      assert.equal(published.price, null); assert.equal(published.rating, null);
    }
  });
  check('the new licensed photo has one real gallery view and responsive sources', () => {
    const gallery = GUITARS_BY_ID['martin-d-28'].gallery;
    assert.equal(gallery.length, 1);
    for (const width of [480, 960, 1200]) assert.ok(gallery[0].srcSet.includes(`${width}w`));
    assert.equal(gallery[0].width, 1200); assert.equal(gallery[0].height, 1594);
    assert.equal(GUITARS_BY_ID['martin-d-18'].hasPhotos, false);
  });
  check('quiz weights and unknown-price/rating treatment survive the data review', () => {
    assert.deepEqual(SCORE_WEIGHTS, { type: 30, level: 20, style: 20, budget: 20, priority: 10, rating: 5 });
    for (const type of ['electric', 'acoustic', 'bass', 'classical', 'any']) {
      for (const match of rankGuitars({ type, level: 'beginner', style: 'rock', budget: 'mid', priority: 'light' }, 200)) {
        assert.ok(GUITARS_BY_ID[match.guitar.id]); assert.equal(match.points.rating, 0);
        assert.equal(match.points.priority, 0); assert.equal(match.points.budget, 6);
      }
    }
  });
} finally { await server.close(); }
console.log(`\n${passed}/${passed} checks passed`);
