import assert from 'node:assert/strict';
import { createServer } from 'vite';

const server = await createServer({ server: { middlewareMode: true, hmr: false }, appType: 'custom', logLevel: 'error' });
const results = [];
const check = (name, fn) => { fn(); results.push({ name, passed: true }); console.log(`PASS ${name}`); };
try {
  const { analyseRows, COMPARE_ROWS } = await server.ssrLoadModule('/src/components/compare/compareRows.js');
  const { rowInCategory } = await server.ssrLoadModule('/src/components/compare/compareCategories.js');
  const stamp = { url: 'https://manufacturer.example/fixture', verifiedOn: '2026-10-29' };
  const make = (id, specs = {}, extra = {}) => ({ id, name: id, brand: 'QA', category: 'electric', dataStatus: 'partial', source: stamp, price: null, specs, ...extra });
  const row = (items, key, options = {}) => analyseRows(items, options).find((item) => item.row.key === key);
  const required = ['brand', 'model', 'price', 'type', 'bodyShape', 'body', 'top', 'back', 'sides', 'neck', 'fretboard', 'strings', 'frets', 'scale', 'pickups', 'electronics', 'bridge'];

  check('every requested comparison field remains visible in Overview even when absent', () => {
    const items = [make('one'), make('two')];
    const keys = analyseRows(items, { includeSamples: false }).filter(({ row: item }) => rowInCategory(item, 'main')).map(({ row: item }) => item.key);
    for (const key of required) assert.ok(keys.includes(key), key);
    assert.equal(new Set(COMPARE_ROWS.map((item) => item.key)).size, COMPARE_ROWS.length);
  });
  check('null, undefined, empty and whitespace specifications show no data and are not equal/different', () => {
    const items = [make('one', { neck: null }), make('two'), make('three', { neck: '' }), make('four', { neck: ' \t\n' })];
    const value = row(items, 'neck', { includeSamples: false });
    assert.equal(value.empty, true); assert.equal(value.incomplete, true); assert.equal(value.same, false); assert.equal(value.diff, false);
    for (const item of items) { assert.equal(value.valueOf(item), null); assert.equal(value.displayOf(item), 'ไม่มีข้อมูล'); }
  });
  check('a known absence of electronics is preserved and never invented for unknowns', () => {
    const items = [make('one', { electronics: 'None' }), make('two', { electronics: null })];
    const value = row(items, 'electronics');
    assert.equal(value.displayOf(items[0]), 'None'); assert.equal(value.displayOf(items[1]), 'ไม่มีข้อมูล');
    assert.equal(value.same, false); assert.equal(value.diff, false); assert.equal(value.incomplete, true);
  });
  check('one known value plus unknowns is incomplete, not a proven difference', () => {
    const items = [make('one', { top: 'Solid spruce' }), make('two'), make('three')];
    const value = row(items, 'top');
    assert.equal(value.empty, false); assert.equal(value.same, false); assert.equal(value.diff, false); assert.equal(value.incomplete, true);
  });
  check('known equal values plus an unknown do not claim all models are the same', () => {
    const value = row([make('one', { top: 'Solid spruce' }), make('two', { top: 'solid spruce' }), make('three')], 'top');
    assert.equal(value.same, false); assert.equal(value.diff, false); assert.equal(value.incomplete, true);
  });
  check('two genuinely different known values are highlighted even when another model is unknown', () => {
    const value = row([make('one', { top: 'Solid spruce' }), make('two', { top: 'Solid cedar' }), make('three')], 'top');
    assert.equal(value.same, false); assert.equal(value.diff, true); assert.equal(value.incomplete, true);
  });
  check('case and whitespace alone do not create false technical differences', () => {
    const items = [make('one', { body: '  Solid   Mahogany ' }), make('two', { body: 'solid mahogany' })];
    const value = row(items, 'body');
    assert.equal(value.same, true); assert.equal(value.diff, false); assert.equal(value.incomplete, false);
    assert.equal(value.displayOf(items[0]), 'Solid   Mahogany');
    assert.equal(row([make('one', { body: 'Nato' }), make('two', { body: 'Mahogany' })], 'body').diff, true);
  });
  check('equivalent inch and millimetre scales compare equally without changing source display', () => {
    const items = [make('one', { scale: 25.5 }), make('two', { scaleMm: 647.7 })];
    const value = row(items, 'scale');
    assert.equal(value.valueOf(items[0]), 647.7); assert.equal(value.valueOf(items[1]), 647.7);
    assert.equal(value.same, true); assert.equal(value.diff, false);
    assert.equal(value.displayOf(items[0]), '25.5"'); assert.equal(value.displayOf(items[1]), '647.7 mm');
    assert.equal(row([items[0], make('three', { scaleMm: 648 })], 'scale').diff, true, 'Do not guess that explicitly distinct source millimetres are equal');
  });
  check('invalid scale values cannot render as zero or poison a valid alternate unit', () => {
    const items = [make('one', { scaleMm: 0, scale: 25.5 }), make('two', { scaleMm: NaN, scale: -1 }), make('three', { scaleMm: Infinity }), make('four', { scaleMm: '647.7' })];
    const value = row(items, 'scale');
    assert.equal(value.valueOf(items[0]), 647.7); assert.equal(value.displayOf(items[0]), '25.5"');
    for (const item of items.slice(1)) { assert.equal(value.valueOf(item), null); assert.equal(value.displayOf(item), 'ไม่มีข้อมูล'); }
  });
  check('zero frets is a valid sourced fretless count, while zero strings is unknown', () => {
    const items = [make('one', { frets: 0, strings: 0 }), make('two', { frets: 22, strings: 6 })];
    const frets = row(items, 'frets'); const strings = row(items, 'strings');
    assert.equal(frets.valueOf(items[0]), 0); assert.equal(frets.displayOf(items[0]), 0); assert.equal(frets.diff, true);
    assert.equal(strings.valueOf(items[0]), null); assert.equal(strings.displayOf(items[0]), 'ไม่มีข้อมูล'); assert.equal(strings.diff, false);
  });
  check('unverified or non-THB prices cannot win the cheapest comparison', () => {
    const base = { source: { ...stamp, fields: ['price'] }, priceSource: { ...stamp, currency: 'THB' } };
    const items = [make('one', {}, { ...base, price: 20000 }), make('two', {}, { ...base, price: 30000 }), make('three', {}, { ...base, price: 1000, priceSource: { ...stamp, currency: 'USD' } }), make('four')];
    const value = row(items, 'price', { includeSamples: false });
    assert.equal(value.best, 20000); assert.equal(value.diff, true); assert.equal(value.incomplete, true);
    assert.equal(value.displayOf(items[0]), '฿20,000');
    for (const item of items.slice(2)) { assert.equal(value.valueOf(item), null); assert.equal(value.displayOf(item), 'สอบถามราคา'); }
  });
  check('unknown, zero, negative, non-finite and incorrectly typed prices never display zero baht', () => {
    for (const price of [null, 0, -1, NaN, Infinity, '0', '20000']) {
      const item = make('one', {}, { price }); const value = row([item], 'price');
      assert.equal(value.valueOf(item), null); assert.equal(value.displayOf(item), 'สอบถามราคา');
    }
  });
  check('sample specification protection remains enabled for public comparisons', () => {
    const item = make('one', { neck: 'Unverified material' }, { dataStatus: 'sample', source: null, price: 1000 });
    const value = row([item], 'neck', { includeSamples: false });
    assert.equal(value.valueOf(item), null); assert.equal(value.displayOf(item), 'ยังไม่ยืนยัน');
    assert.equal(row([item], 'price', { includeSamples: false }).displayOf(item), 'สอบถามราคา');
    assert.equal(row([item], 'neck', { includeSamples: true }).displayOf(item), 'Unverified material');
  });
  check('unrequested optional rows remain hidden until sourced data exists', () => {
    assert.equal(row([make('one'), make('two')], 'case'), undefined);
    const value = row([make('one', { case: 'Hardshell case' }), make('two')], 'case');
    assert.ok(value); assert.equal(value.diff, false); assert.equal(value.incomplete, true);
  });
  check('a genuine verified zero-star rating remains a known rating', () => {
    const items = [make('one', {}, { rating: { verified: true, source: stamp, count: 1, score: 0 } }), make('two', {}, { rating: { verified: true, source: stamp, count: 2, score: 1 } })];
    const value = row(items, 'rating');
    assert.equal(value.valueOf(items[0]), 0); assert.equal(value.displayOf(items[0]), '★ 0.0 (1)');
    assert.equal(value.best, 1); assert.equal(value.diff, true);
  });
  console.log(`\n${results.length}/${results.length} comparison data checks passed`);
} finally { await server.close(); }
