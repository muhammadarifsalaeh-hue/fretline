import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createServer } from 'vite';
import { readCatalog, readArchive, readPhase7, readPolicy, findDuplicates, validateGuitar, ROOT } from './lib/catalog.mjs';
import { batchIds, assertPhase9DataBoundary } from './lib/phase9.mjs';

const server = await createServer({ server: { middlewareMode: true, hmr: false }, appType: 'custom', logLevel: 'error' });
let count = 0;
const check = (name, fn) => { fn(); count++; console.log(`PASS ${name}`); };
try {
  const { GUITARS, GUITARS_BY_ID, ARCHIVED_GUITARS, SAVED_GUITARS_BY_ID } = await server.ssrLoadModule('/src/data/guitars.js');
  const { BRANDS, getBrandById, getBrandGuitars } = await server.ssrLoadModule('/src/data/brands.js');
  const { normalizeGuitarIds } = await server.ssrLoadModule('/src/utils/selection.js');
  const { applyFilters, PRICE_MAX } = await server.ssrLoadModule('/src/hooks/useCatalogFilters.js');
  const { rankGuitars, readAnswers, SCORE_WEIGHTS } = await server.ssrLoadModule('/src/utils/quizScoring.js');
  const { matchesQuery } = await server.ssrLoadModule('/src/utils/search.js');
  const { analyseRows } = await server.ssrLoadModule('/src/components/compare/compareRows.js');
  const { th } = await server.ssrLoadModule('/src/i18n/th.js');
  const { en } = await server.ssrLoadModule('/src/i18n/en.js');
  const policy = readPolicy();
  const added = readPhase7();
  const archive = readArchive();
  const records = readCatalog();
  const before = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/qa-phase7/audit-before.json'), 'utf8'));
  const approved = ['Yamaha', 'Fender', 'Epiphone', 'Ibanez', 'Taylor', 'Córdoba', 'Gibson', 'Martin', 'PRS', 'Squier'];
  check('exactly 200 active guitars in the CLI and browser data', () => { assert.equal(GUITARS.length, 200); assert.equal(records.length, 200); assert.equal(policy.target, 200); });
  check('exactly the ten approved brands with 20 models each', () => {
    assert.deepEqual(new Set(BRANDS.map((brand) => brand.name)), new Set(approved));
    for (const brand of BRANDS) { assert.equal(brand.models, 20); assert.equal(getBrandGuitars(brand.name).length, 20); }
  });
  check('166 new IDs and 34 retained originals, not colors or duplicate inserts', () => {
    assert.equal(added.length, 166); assert.ok(added.every((guitar) => !before.some((old) => old.id === guitar.id)));
    assert.equal(GUITARS.filter((guitar) => before.some((old) => old.id === guitar.id)).length, 34);
    assert.deepEqual(findDuplicates([...records, ...archive]), []);
  });
  check('retained identities remain unchanged and only the documented Phase 9 batch may revise facts', () => {
    assertPhase9DataBoundary();
    const rechecked = batchIds();
    for (const old of before.filter((guitar) => !policy.archivedIds.includes(guitar.id))) {
      const guitar = GUITARS_BY_ID[old.id];
      const keys = rechecked.has(old.id) ? ['id', 'slug', 'brand', 'name', 'category'] : ['id', 'slug', 'brand', 'name', 'category', 'source', 'specs'];
      for (const key of keys) assert.deepEqual(guitar[key], old[key], `${old.id}/${key}`);
    }
  });
  check('both archive backups contain exact original published records and sources', () => {
    assert.deepEqual(archive.map((guitar) => guitar.id), ['gretsch-g2420-streamliner', 'yamaha-c40']);
    for (const guitar of archive) {
      const old = before.find((item) => item.id === guitar.id);
      assert.deepEqual(guitar.previousPublishedSnapshot, old);
      assert.deepEqual(guitar.source, old.source);
      assert.ok(guitar.legacySourceRecord.includes(guitar.id));
      assert.equal(guitar.archivedFromCommit, '4fa60f6a5ee885c839324a2a5dc6adc651ad117a');
    }
  });
  check('archive records are resolvable but excluded from catalog and brand totals', () => {
    assert.equal(ARCHIVED_GUITARS.length, 2);
    for (const id of policy.archivedIds) { assert.equal(GUITARS_BY_ID[id], undefined); assert.equal(SAVED_GUITARS_BY_ID[id].archived, true); }
    assert.equal(getBrandById('gretsch'), null);
    assert.ok(GUITARS.every((guitar) => !guitar.archived));
  });
  check('all 36 old saved IDs survive migration without a silent archive deletion', () => {
    const ids = before.map((guitar) => guitar.id);
    assert.deepEqual(normalizeGuitarIds(ids), ids);
    assert.deepEqual(normalizeGuitarIds(['yamaha-c40', 'constructor', 'yamaha-c40', 'gretsch-g2420-streamliner']), ['yamaha-c40', 'gretsch-g2420-streamliner']);
  });
  check('shared archived comparison links retain order, deduplicate and cap four', () => {
    const ids = ['yamaha-c40', 'gretsch-g2420-streamliner', added[0].id, added[1].id, added[2].id];
    const params = new URLSearchParams({ ids: [...ids, ids[0]].join(',') });
    assert.deepEqual(normalizeGuitarIds(params.get('ids').split(','), 4), ids.slice(0, 4));
    const rows = analyseRows(ids.slice(0, 4).map((id) => SAVED_GUITARS_BY_ID[id]), { includeSamples: false });
    assert.ok(rows.every((row) => !row.empty || row.best === null));
  });
  check('all 166 models have successful manufacturer retrieval and scoped factual evidence', () => {
    const hosts = ['www.fender.com', 'www.gibson.com', 'www.ibanez.com', 'cordobaguitars.com', 'www.martinguitar.com', 'www.taylorguitars.com', 'support.prsguitars.com'];
    const evidence = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/qa-phase7/field-evidence.json'), 'utf8'));
    assert.equal(evidence.length, 166);
    for (const guitar of added) {
      assert.deepEqual(validateGuitar(guitar), [], guitar.id);
      assert.ok(hosts.includes(new URL(guitar.source.url).hostname), guitar.id);
      assert.equal(guitar.source.evidence.httpStatus, 200);
      assert.match(guitar.source.evidence.sha256, /^[a-f0-9]{64}$/);
      const record = evidence.find((item) => item.id === guitar.id);
      assert.equal(record?.retrievedSha256, guitar.source.evidence.sha256);
      assert.equal(record?.sourceUrl, guitar.source.url);
    }
  });
  check('PRS 2025 facts are explicitly dated and scoped to actual catalog pages', () => {
    const prs = added.filter((guitar) => guitar.brand === 'PRS');
    assert.equal(prs.length, 19);
    assert.ok(prs.every((guitar) => guitar.source.documentYear === 2025 && guitar.source.documentPage >= 3 && guitar.source.documentPage <= 8 && guitar.source.editionNote.includes('2025')));
  });
  check('Ibanez string counts match every explicitly numbered tuning, including comma spacing', () => {
    const evidence = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/qa-phase7/field-evidence.json'), 'utf8'));
    for (const guitar of added.filter((record) => record.brand === 'Ibanez')) {
      const tuning = evidence.find((entry) => entry.id === guitar.id).specificationLabels['factory tuning'][0];
      const numbers = [...tuning.matchAll(/(?:^|,)\s*(\d+)/g)].map((match) => Number(match[1]));
      assert.deepEqual(numbers, Array.from({ length: numbers.length }, (_, index) => index + 1), guitar.id);
      assert.equal(guitar.specs.strings, numbers.length, guitar.id);
    }
    assert.equal(GUITARS_BY_ID['ibanez-rg652ahm'].specs.strings, 6);
    assert.equal(GUITARS_BY_ID['ibanez-rg9pb'].specs.strings, 9);
  });
  check('all public facts remain partial; no manufactured prices, ratings or weights', () => {
    for (const guitar of [...GUITARS, ...ARCHIVED_GUITARS]) {
      assert.equal(guitar.dataStatus, 'partial'); assert.equal(guitar.price, null); assert.equal(guitar.rating, null); assert.equal(guitar.specs.weightKg, null);
      for (const [key, value] of Object.entries(guitar.specs)) if (value != null) assert.ok(guitar.source.fields.includes(`specs.${key}`));
    }
  });
  check('two licensed model photos leave 198 honest placeholders after the Phase 9 review', () => {
    assert.equal(GUITARS.filter((guitar) => guitar.hasPhotos).length, 2);
    assert.equal(GUITARS.filter((guitar) => !guitar.hasPhotos).length, 198);
    assert.equal(GUITARS_BY_ID['yamaha-fg820-12'].gallery[0].attribution.license, 'CC-BY-SA-4.0');
    assert.equal(GUITARS_BY_ID['martin-d-28'].gallery[0].attribution.license, 'CC-BY-SA-4.0');
    assert.ok(added.filter((guitar) => guitar.id !== 'martin-d-28').every((guitar) => !GUITARS_BY_ID[guitar.id].hasPhotos));
  });
  check('search and brand/type filters see all 200 active records without the archive', () => {
    const filters = { q: '', types: [], brands: [], min: 0, max: PRICE_MAX };
    assert.equal(applyFilters(GUITARS, filters).length, 200);
    for (const brand of approved) assert.equal(applyFilters(GUITARS, { ...filters, brands: [brand] }).length, 20);
    assert.equal(applyFilters(GUITARS, { ...filters, q: 'C40' }).length, 0);
    assert.equal(applyFilters(GUITARS, { ...filters, q: 'G2420' }).length, 0);
    for (const guitar of added) assert.ok(matchesQuery(GUITARS_BY_ID[guitar.id], guitar.name), guitar.id);
  });
  check('old quiz weights and shareable answers survive; archive is never recommended', () => {
    assert.deepEqual(SCORE_WEIGHTS, { type: 30, level: 20, style: 20, budget: 20, priority: 10, rating: 5 });
    for (const type of ['electric', 'acoustic', 'classical', 'bass', 'any']) {
      const answers = { type, level: 'beginner', style: type === 'classical' ? 'classical' : 'rock', budget: 'mid', priority: 'value' };
      assert.deepEqual(readAnswers(new URLSearchParams(answers)), answers);
      for (const result of rankGuitars(answers, 200)) { assert.ok(GUITARS_BY_ID[result.guitar.id]); assert.ok(!result.guitar.archived); assert.equal(result.points.rating, 0); }
    }
    assert.ok(added.every((guitar) => !guitar.profile));
  });
  check('Thai and English archival labels have matching interpolation fields', () => {
    for (const key of Object.keys(th).filter((key) => key.startsWith('p7.'))) {
      assert.ok(en[key], key);
      assert.deepEqual([...th[key].matchAll(/\{(\w+)\}/g)].map((match) => match[1]), [...en[key].matchAll(/\{(\w+)\}/g)].map((match) => match[1]));
    }
  });
  console.log(`\n${count}/${count} checks passed`);
} finally { await server.close(); }
