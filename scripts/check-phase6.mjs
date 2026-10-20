import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { createServer } from 'vite';
import { readCatalog, readPolicy, readImageRights, validateGuitar, findDuplicates, ROOT } from './lib/catalog.mjs';
import { hasImageRights } from '../src/utils/imageRights.js';

let count = 0;
const check = (name, fn) => { fn(); count++; console.log(`PASS ${name}`); };
const server = await createServer({ server: { middlewareMode: true, hmr: false }, appType: 'custom', logLevel: 'error' });
try {
  const { GUITARS, GUITARS_BY_ID, SAVED_GUITARS_BY_ID, ARCHIVED_GUITARS } = await server.ssrLoadModule('/src/data/guitars.js');
  const { BRANDS } = await server.ssrLoadModule('/src/data/brands.js');
  const trust = await server.ssrLoadModule('/src/utils/dataTrust.js');
  const { PRICE_MAX, HAS_CATALOG_PRICES, applyFilters } = await server.ssrLoadModule('/src/hooks/useCatalogFilters.js');
  const { analyseRows } = await server.ssrLoadModule('/src/components/compare/compareRows.js');
  const { scaleInMillimetres } = await server.ssrLoadModule('/src/utils/format.js');
  const scoring = await server.ssrLoadModule('/src/utils/quizScoring.js');
  const { normalizeGuitarIds } = await server.ssrLoadModule('/src/utils/selection.js');
  const before = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/qa-phase6/audit-before.json'), 'utf8'));
  const records = readCatalog();
  const policy = readPolicy();
  check('all original IDs remain resolvable; retained catalog order survives approved archival', () => {
    assert.equal(GUITARS.length, policy.target);
    for (const g of before) assert.deepEqual([SAVED_GUITARS_BY_ID[g.id]?.brand, SAVED_GUITARS_BY_ID[g.id]?.category, SAVED_GUITARS_BY_ID[g.id]?.slug], [g.brand, g.category, g.id]);
    const retained = before.filter((g) => !policy.archivedIds.includes(g.id));
    assert.deepEqual(GUITARS.slice(0, retained.length).map((g) => g.id), retained.map((g) => g.id));
  });
  check('no duplicate IDs or normalized brand/model pairs', () => assert.deepEqual(findDuplicates(records), []));
  check('every effective record passes catalog validation', () => { for (const record of records) assert.deepEqual(validateGuitar(record), [], record.id); });
  check('all records remain partial; none silently becomes verified', () => assert.ok(GUITARS.every((g) => g.dataStatus === 'partial')));
  check('all public prices, old prices, reviews, weights and promotional badges are unknown', () => {
    for (const g of GUITARS) { assert.equal(g.price, null); assert.equal(g.oldPrice, null); assert.equal(g.rating, null); assert.equal(g.badge, null); assert.equal(g.specs.weightKg, null); }
  });
  check('every published factual spec has an explicit source field and real check date', () => {
    for (const g of GUITARS) {
      assert.ok(trust.isSourceBacked(g), g.id);
      assert.equal(new Date(g.source.verifiedOn).toISOString().slice(0, 10), g.source.verifiedOn);
      for (const [key, value] of Object.entries(g.specs)) if (value != null) assert.ok(g.source.fields.includes(`specs.${key}`), `${g.id}/${key}`);
    }
  });
  check('limited search-index evidence remains visibly marked with edition caveats', () => {
    const limited = [...GUITARS, ...ARCHIVED_GUITARS].filter((g) => g.source.method === 'search-index');
    assert.deepEqual(limited.map((g) => g.id), ['gretsch-g2420-streamliner', 'yamaha-c40']);
    assert.ok(limited.every((g) => g.source.editionNote.includes('403') && g.dataStatus === 'partial'));
  });
  check('incorrect SR300E demo materials and pickups are replaced by the actual referenced variant', () => {
    const g = GUITARS_BY_ID['ibanez-sr300e'];
    assert.equal(g.specs.body, 'Okoume'); assert.equal(g.specs.fretboard, 'Jatoba'); assert.match(g.specs.pickups, /PowerSpan/);
    assert.ok(!g.tags.includes('PJ'));
  });
  check('GS Mini Mahogany and current 214ce wood variants are not conflated', () => {
    assert.match(GUITARS_BY_ID['taylor-gs-mini'].specs.body, /mahogany top/i);
    assert.ok(!/spruce/i.test(GUITARS_BY_ID['taylor-gs-mini'].specs.body));
    assert.match(GUITARS_BY_ID['taylor-214ce'].specs.body, /walnut/i);
  });
  check('every Yamaha table column stays mapped to its correct model', () => {
    assert.match(GUITARS_BY_ID['yamaha-fg830'].specs.body, /Rosewood/);
    assert.match(GUITARS_BY_ID['yamaha-fg820'].specs.body, /Mahogany/);
    assert.equal(GUITARS_BY_ID['yamaha-fg820-12'].specs.strings, 12);
    assert.equal(GUITARS_BY_ID['yamaha-fgx830c'].specs.pickups, 'SYSTEM66');
    assert.equal(GUITARS_BY_ID['yamaha-fg800j'].specs.scaleMm, 634);
  });
  check('equal millimetre scales are equal despite rounded inch labels', () => {
    assert.equal(scaleInMillimetres(GUITARS_BY_ID['cordoba-c5'].specs), scaleInMillimetres(GUITARS_BY_ID['yamaha-fg830'].specs));
    assert.equal(analyseRows([GUITARS_BY_ID['cordoba-c5'], GUITARS_BY_ID['yamaha-fg830']]).find(({ row }) => row.key === 'scale').same, true);
  });
  check('catalog has a finite price bound when every amount is unknown', () => { assert.equal(HAS_CATALOG_PRICES, false); assert.ok(Number.isFinite(PRICE_MAX) && PRICE_MAX > 0); });
  check('default filters retain unknown-price models; a budget does not assert them affordable', () => {
    const filters = { q: '', brands: [], types: [], min: 0, max: PRICE_MAX };
    assert.equal(applyFilters(GUITARS, filters).length, GUITARS.length);
    assert.equal(applyFilters(GUITARS, { ...filters, max: 20000 }).length, 0);
    assert.equal(applyFilters(GUITARS, { ...filters, q: 'RG550' })[0]?.id, 'ibanez-rg550-genesis');
  });
  check('quick searches retain only source-backed beginner, nylon and left-handed labels', () => {
    const filters = { q: 'มือซ้าย', brands: [], types: [], min: 0, max: PRICE_MAX };
    assert.deepEqual(applyFilters(GUITARS, filters).map((g) => g.id), ['yamaha-fg820l']);
    assert.ok(applyFilters(GUITARS, { ...filters, q: 'ผู้เริ่มต้น' }).length >= 2);
    assert.ok(applyFilters(GUITARS, { ...filters, q: 'สายไนลอน' }).some((g) => g.id === 'cordoba-c5'));
    assert.ok(!GUITARS_BY_ID['fender-american-professional-ii-stratocaster'].keywords.includes('left-handed'));
  });
  check('every brand count still partitions the same catalog', () => {
    assert.equal(BRANDS.length, policy.brands.length); assert.equal(BRANDS.reduce((sum, b) => sum + b.models, 0), GUITARS.length);
    assert.equal(BRANDS.reduce((sum, b) => sum + b.sourceModels, 0), GUITARS.length);
  });
  check('wishlist and comparison IDs survive migration; inherited property names do not qualify', () => {
    const ids = before.map((g) => g.id);
    assert.deepEqual(normalizeGuitarIds(ids), ids);
    assert.deepEqual(normalizeGuitarIds(['constructor', '__proto__', ids[0], ids[0]]), [ids[0]]);
  });
  check('quiz retains the original weights and cannot use unknown prices, weights or reviews', () => {
    assert.deepEqual(scoring.SCORE_WEIGHTS, { type: 30, level: 20, style: 20, budget: 20, priority: 10, rating: 5 });
    for (const guitar of GUITARS) {
      const match = scoring.scoreGuitar(guitar, { type: 'any', level: 'beginner', style: 'rock', budget: 'mid', priority: 'light' });
      assert.equal(match.points.budget, 6); assert.equal(match.points.priority, 0); assert.equal(match.points.rating, 0);
    }
  });
  check('general specification sources cannot validate a THB price', () => {
    const g = GUITARS_BY_ID['yamaha-fg830'];
    assert.equal(trust.trustedPrice({ ...g, price: 20000 }), null);
    assert.equal(trust.trustedPrice({ ...g, price: 20000, source: { ...g.source, fields: [...g.source.fields, 'price'] } }), null);
  });
  const rights = readImageRights();
  check('one matching licensed photo is published; derivatives are not gallery angles', () => {
    assert.equal(GUITARS.filter((g) => g.hasPhotos).length, 1);
    const photo = GUITARS_BY_ID['yamaha-fg820-12'].gallery[0];
    assert.equal(GUITARS_BY_ID['yamaha-fg820-12'].gallery.length, 1);
    assert.ok(photo.srcSet.includes('480w') && photo.srcSet.includes('960w') && photo.srcSet.includes('1200w'));
    assert.equal(photo.attribution.author, 'Peternick2468'); assert.equal(photo.attribution.license, 'CC-BY-SA-4.0');
  });
  check('every delivered image file has intact attribution, dimensions and SHA-256', () => {
    for (const [id, photos] of Object.entries(rights)) for (const photo of photos) {
      assert.ok(hasImageRights(photo, id));
      for (const file of [photo, ...photo.variants]) {
        const contents = fs.readFileSync(path.join(ROOT, 'src/assets/guitars', id, file.file));
        assert.equal(createHash('sha256').update(contents).digest('hex'), file.sha256);
        assert.ok(file.width > 0 && file.height > 0);
      }
    }
  });
  check('missing rights, mismatched models, fake license URLs and impossible dates are rejected', () => {
    const photo = rights['yamaha-fg820-12'][0];
    for (const invalid of [{ ...photo, author: '' }, { ...photo, licenseUrl: 'https://example.com/license' }, { ...photo, checkedOn: '2026-99-99' }, { ...photo, modelMatchNote: '' }]) assert.equal(hasImageRights(invalid, photo.guitarId), false);
    assert.equal(hasImageRights(photo, 'yamaha-fg820'), false);
  });
  console.log(`\n${count}/${count} checks passed`);
} finally { await server.close(); }
