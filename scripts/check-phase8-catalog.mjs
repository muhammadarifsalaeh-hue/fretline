import assert from 'node:assert/strict';
import { createServer } from 'vite';

const server = await createServer({ server: { middlewareMode: true, hmr: false }, appType: 'custom', logLevel: 'error' });
let passed = 0;
const check = (name, test) => { test(); passed++; console.log(`PASS ${name}`); };
try {
  const { GUITARS, ARCHIVED_GUITARS } = await server.ssrLoadModule('/src/data/guitars.js');
  const { applyFilters, readCatalogFilters, PRICE_MIN, PRICE_MAX, ALL_BRANDS } = await server.ssrLoadModule('/src/hooks/useCatalogFilters.js');
  const { matchesQuery, searchCatalog, normalizeSearchText } = await server.ssrLoadModule('/src/utils/search.js');
  const filters = readCatalogFilters(new URLSearchParams());

  check('Accentless Córdoba search finds all twenty actual models', () => {
    const matches = GUITARS.filter((guitar) => matchesQuery(guitar, 'cordoba'));
    assert.equal(matches.length, 20);
    assert.ok(matches.every((guitar) => guitar.brand === 'Córdoba'));
    assert.ok(searchCatalog('cordoba').some((group) => group.items.some((item) => item.key === 'b-cordoba')));
  });
  check('Common model punctuation variants find the real D-18', () => {
    for (const query of ['Martin D18', 'Martin D–18', 'Martin D−18', 'MARTIN D-18']) {
      assert.ok(GUITARS.filter((guitar) => matchesQuery(guitar, query)).some((guitar) => guitar.name.startsWith('D-18')), query);
    }
  });
  check('Latin accent folding preserves Thai vowels and tone marks', () => {
    assert.equal(normalizeSearchText('ผู้เริ่มต้น กีตาร์'), 'ผู้เริ่มต้น กีตาร์');
    assert.equal(normalizeSearchText('Córdoba'), 'cordoba');
    assert.ok(GUITARS.some((guitar) => matchesQuery(guitar, 'ผู้เริ่มต้น')));
  });
  check('Thai bass alias matches the category without a Basswood false positive', () => {
    const matches = GUITARS.filter((guitar) => matchesQuery(guitar, 'เบส'));
    assert.ok(matches.length > 0);
    assert.ok(matches.every((guitar) => guitar.category === 'bass'));
  });
  check('Every published model remains searchable by its exact manufacturer name', () => {
    for (const guitar of GUITARS) assert.ok(matchesQuery(guitar, `${guitar.brand} ${guitar.name}`), guitar.id);
  });
  check('Duplicate URL facets are trimmed and deduplicated', () => {
    const parsed = readCatalogFilters(new URLSearchParams('type=acoustic,acoustic,%20electric,,&brand=Yamaha,Yamaha,%20Fender'));
    assert.deepEqual(parsed.types, ['acoustic', 'electric']);
    assert.deepEqual(parsed.brands, ['Yamaha', 'Fender']);
  });
  check('Malformed URL numbers and sort values use safe defaults', () => {
    const parsed = readCatalogFilters(new URLSearchParams('page=NaN&min=nope&max=Infinity&sort=constructor'));
    assert.equal(parsed.page, 1);
    assert.equal(parsed.min, PRICE_MIN);
    assert.equal(parsed.max, PRICE_MAX);
    assert.equal(parsed.sort, 'featured');
    assert.equal(readCatalogFilters(new URLSearchParams('page=-6')).page, 1);
    assert.equal(readCatalogFilters(new URLSearchParams('page=2.8')).page, 2);
  });
  check('Brand, type and model query intersect rather than overriding each other', () => {
    const parsed = readCatalogFilters(new URLSearchParams('brand=Yamaha&type=acoustic&q=FG820'));
    const expected = GUITARS.filter((guitar) => guitar.brand === 'Yamaha' && guitar.category === 'acoustic' && guitar.name.includes('FG820'));
    assert.deepEqual(applyFilters(GUITARS, parsed).map((guitar) => guitar.id), expected.map((guitar) => guitar.id));
    assert.ok(expected.length > 0);
    assert.equal(applyFilters(GUITARS, { ...parsed, types: ['bass'] }).length, 0);
  });
  check('Unknown prices remain excluded when an actual price URL filter is active', () => {
    assert.equal(applyFilters(GUITARS, { ...filters, max: 20000 }).length, 0);
  });
  check('Quota and archived-model rules are unchanged', () => {
    assert.equal(GUITARS.length, 200);
    assert.equal(ALL_BRANDS.length, 10);
    assert.equal(new Set(GUITARS.map((guitar) => guitar.id)).size, 200);
    for (const brand of ALL_BRANDS) assert.equal(applyFilters(GUITARS, { ...filters, brands: [brand] }).length, 20);
    for (const archive of ARCHIVED_GUITARS) assert.ok(!GUITARS.some((guitar) => guitar.id === archive.id));
  });
  console.log(`\n${passed}/${passed} checks passed`);
} finally {
  await server.close();
}
