import assert from 'node:assert/strict';
import { createServer } from 'vite';

const server = await createServer({ server: { middlewareMode: true, hmr: false }, appType: 'custom', logLevel: 'error' });
let count = 0;
const check = (name, fn) => { fn(); count += 1; console.log(`PASS ${name}`); };
try {
  const { GUITARS } = await server.ssrLoadModule('/src/data/guitars.js');
  const { buildBrands, BRANDS, getBrandById, getBrandGuitars } = await server.ssrLoadModule('/src/data/brands.js');
  const { filterBrands } = await server.ssrLoadModule('/src/utils/brandFilters.js');
  const { sortGuitars } = await server.ssrLoadModule('/src/utils/guitarSort.js');
  const { normalizeGuitarIds } = await server.ssrLoadModule('/src/utils/selection.js');
  const { publicPrice } = await server.ssrLoadModule('/src/utils/dataTrust.js');
  const { en } = await server.ssrLoadModule('/src/i18n/en.js');
  const { th } = await server.ssrLoadModule('/src/i18n/th.js');
  // Fixtures are test-only and are never added to the shipped guitar catalog.
  const source = { url: 'https://example.com/qa-source', verifiedOn: '2026-10-19' };
  const sample = { id: 'sample', brand: 'Test maker', name: 'A', category: 'electric', price: 1, dataStatus: 'sample' };
  const cheap = { ...sample, id: 'cheap', name: 'B', price: 20000, dataStatus: 'partial', source };
  const expensive = { ...cheap, id: 'expensive', name: 'C', price: 50000, category: 'acoustic' };
  const unknown = { ...cheap, id: 'unknown', name: 'D', price: null };
  const items = [sample, cheap, expensive, unknown];
  check('brand names and model counts exactly partition the existing catalog', () => {
    assert.equal(BRANDS.length, new Set(GUITARS.map((g) => g.brand)).size);
    assert.equal(BRANDS.reduce((sum, b) => sum + b.models, 0), GUITARS.length);
    for (const brand of BRANDS) assert.equal(brand.models, GUITARS.filter((g) => g.brand === brand.name).length);
  });
  check('brand category membership comes only from its real catalog entries', () => {
    for (const brand of BRANDS) assert.deepEqual(new Set(brand.categories), new Set(getBrandGuitars(brand.name).map((g) => g.category)));
  });
  check('unknown, inherited-object and uppercase brand routes are safe', () => {
    for (const id of ['missing', '__proto__', 'constructor', 'toString']) assert.equal(getBrandById(id), null);
    assert.equal(getBrandById('YAMAHA')?.name, 'Yamaha');
  });
  check('empty brand catalog yields an empty index', () => assert.deepEqual(buildBrands([], {}, {}), []));
  check('brand summary excludes sample prices and counts source-backed models', () => {
    const [brand] = buildBrands(items, {}, {});
    assert.equal(brand.models, 4); assert.equal(brand.sourceModels, 3); assert.equal(brand.pricedModels, 2);
    assert.equal(brand.priceMin, 20000); assert.equal(brand.priceMax, 50000); assert.equal(brand.metadataStatus, 'unverified');
  });
  check('sample-only brand has no asserted price range', () => {
    const [brand] = buildBrands([sample], {}, {});
    assert.equal(brand.priceMin, null); assert.equal(brand.priceMax, null); assert.equal(brand.sourceModels, 0);
  });
  check('current catalog has no source-backed price range or licensed logo file', () => {
    assert.ok(BRANDS.every((brand) => brand.priceMin === null && brand.priceMax === null && !brand.logo));
  });
  check('brand search is trimmed and case-insensitive', () => {
    assert.deepEqual(filterBrands(BRANDS, { q: ' YaMaHa ' }).map((b) => b.id), ['yamaha']);
    assert.deepEqual(filterBrands(BRANDS, { q: 'no-such-brand' }), []);
  });
  check('type and explicitly unverified legacy country filters intersect', () => {
    const result = filterBrands(BRANDS, { type: 'electric', country: 'USA' });
    assert.ok(result.length > 0); assert.ok(result.every((b) => b.categories.includes('electric') && b.country === 'USA'));
  });
  check('brand sorting is deterministic without mutating the input', () => {
    const before = BRANDS.map((b) => b.id);
    const names = filterBrands(BRANDS, { sort: 'name' }).map((b) => b.name);
    assert.deepEqual(names, [...names].sort((a, b) => a.localeCompare(b)));
    assert.deepEqual(filterBrands(BRANDS, { sort: 'price' }).map((b) => b.name), names);
    assert.deepEqual(BRANDS.map((b) => b.id), before);
  });
  check('verified-only price sorts put sample and missing prices last in both directions', () => {
    assert.deepEqual(sortGuitars(items, 'price-asc', { verifiedOnly: true }).map((g) => g.id), ['cheap', 'expensive', 'sample', 'unknown']);
    assert.deepEqual(sortGuitars(items, 'price-desc', { verifiedOnly: true }).map((g) => g.id), ['expensive', 'cheap', 'sample', 'unknown']);
  });
  check('recently saved order is reversed on a copy', () => {
    assert.deepEqual(sortGuitars(items, 'saved').map((g) => g.id), ['unknown', 'expensive', 'cheap', 'sample']);
    assert.deepEqual(items.map((g) => g.id), ['sample', 'cheap', 'expensive', 'unknown']);
  });
  check('wishlist migration removes duplicate, stale and invalid IDs', () => {
    assert.deepEqual(normalizeGuitarIds([GUITARS[0].id, GUITARS[0].id, null, 'deleted', GUITARS[1].id]), [GUITARS[0].id, GUITARS[1].id]);
  });
  check('public wishlist prices cannot expose legacy sample amounts', () => {
    assert.ok(!publicPrice(sample).includes('1')); assert.ok(publicPrice(cheap).includes('20,000'));
  });
  check('Thai and English Phase 5 text keys and interpolation fields match', () => {
    const keys = Object.keys(th).filter((key) => key.startsWith('p5.'));
    assert.ok(keys.length > 60);
    for (const key of keys) {
      assert.ok(en[key], key);
      assert.deepEqual([...th[key].matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort(), [...en[key].matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort(), key);
    }
  });
  console.log(`\n${count}/${count} checks passed`);
} finally { await server.close(); }
