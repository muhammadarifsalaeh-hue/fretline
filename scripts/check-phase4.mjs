import assert from 'node:assert/strict';
import { createServer } from 'vite';

const server = await createServer({ server: { middlewareMode: true, hmr: false }, appType: 'custom', logLevel: 'error' });
let count = 0;
const check = (name, fn) => { fn(); count += 1; console.log(`PASS ${name}`); };
try {
  const scoring = await server.ssrLoadModule('/src/utils/quizScoring.js');
  const { analyseRows } = await server.ssrLoadModule('/src/components/compare/compareRows.js');
  const trust = await server.ssrLoadModule('/src/utils/dataTrust.js');
  const { normalizeGuitarIds } = await server.ssrLoadModule('/src/utils/selection.js');
  const { GUITARS } = await server.ssrLoadModule('/src/data/guitars.js');
  const answers = { type: 'electric', level: 'beginner', style: 'rock', budget: 'mid', priority: 'versatile' };
  // Test fixtures exist only in this script, never in the shipped catalog.
  const source = { url: 'https://example.com/test-source', verifiedOn: '2026-10-19' };
  const guitar = { id: 'qa-fixture', name: 'QA fixture', category: 'electric', dataStatus: 'verified', source,
    price: 20000, specs: { weightKg: 3 }, profile: { levels: ['beginner'], styles: ['rock'], versatile: true } };
  check('original weights and maximum are preserved', () => {
    assert.deepEqual(scoring.SCORE_WEIGHTS, { type: 30, level: 20, style: 20, budget: 20, priority: 10, rating: 5 });
    assert.equal(scoring.MAX_SCORE, 105);
  });
  check('full main criteria without review bonus: 100 / 105 = 95%', () => {
    const score = scoring.scoreGuitar(guitar, answers);
    assert.equal(score.rawScore, 100); assert.equal(score.score, 95); assert.equal(score.points.rating, 0);
  });
  check('unverified review cannot affect score or recommendation order', () => {
    const a = scoring.scoreGuitar({ ...guitar, rating: { score: 5, count: 500 } }, answers);
    assert.equal(a.rawScore, 100); assert.equal(a.points.rating, 0);
    const one = { ...guitar, id: 'first', rating: { score: 4, count: 2 } };
    const two = { ...guitar, id: 'second', rating: { score: 5, count: 999 } };
    assert.deepEqual(scoring.rankGuitars(answers, 3, 40, [one, two]).map((match) => match.guitar.id), ['first', 'second']);
  });
  check('verified review bonus keeps five-point cap and 99% maximum', () => {
    const score = scoring.scoreGuitar({ ...guitar, rating: { verified: true, source, score: 5, count: 8 } }, answers);
    assert.equal(score.points.rating, 5); assert.equal(score.rawScore, 105); assert.equal(score.score, 99);
  });
  check('invalid or missing review provenance cannot qualify', () => {
    for (const rating of [{ verified: true, score: 5, count: 1 }, { verified: true, source, score: 6, count: 1 }, { verified: true, source: { ...source, url: 'javascript:bad' }, score: 5, count: 1 }]) assert.equal(trust.verifiedRating({ ...guitar, rating }), null);
  });
  check('sample price uses existing unknown-budget six-point rule', () => {
    const score = scoring.scoreGuitar({ ...guitar, dataStatus: 'sample', source: null }, answers);
    assert.equal(score.points.budget, 6); assert.equal(score.rawScore, 86); assert.equal(score.score, 82);
    assert.ok(!score.reasons.some((reason) => reason.includes('20,000')));
  });
  check('unknown price and weight award no invented priority points', () => {
    const score = scoring.scoreGuitar({ ...guitar, price: null, specs: { weightKg: null } }, { ...answers, priority: 'light' });
    assert.equal(score.points.budget, 6); assert.equal(score.points.priority, 0); assert.equal(score.caveats.length, 3);
  });
  check('sample weight is never a verified lightweight recommendation', () => {
    assert.equal(scoring.scoreGuitar({ ...guitar, dataStatus: 'sample' }, { ...answers, priority: 'light' }).points.priority, 0);
  });
  check('budget boundaries, flexibility and 20% over-budget tolerance', () => {
    for (const price of [10000, 30000]) assert.equal(scoring.scoreGuitar({ ...guitar, price }, answers).points.budget, 20);
    assert.equal(scoring.scoreGuitar({ ...guitar, price: 36000 }, answers).points.budget, 10);
    assert.equal(scoring.scoreGuitar({ ...guitar, price: 36001 }, answers).points.budget, 0);
    assert.equal(scoring.scoreGuitar(guitar, { ...answers, budget: 'flex' }).points.budget, 14);
  });
  check('adjacent experience level retains eight-point rule', () => {
    assert.equal(scoring.scoreGuitar({ ...guitar, profile: { levels: ['intermediate'], styles: ['rock'] } }, answers).points.level, 8);
  });
  check('type mismatch retains 0.35 penalty and cannot be forced into results', () => {
    const wrong = { ...guitar, category: 'bass' };
    assert.equal(scoring.scoreGuitar(wrong, answers).rawScore, 70 * 0.35);
    assert.deepEqual(scoring.rankGuitars(answers, 3, 40, [wrong]), []);
    assert.deepEqual(scoring.rankGuitars(answers, 3, 101, [guitar]), []);
  });
  check('empty catalog yields empty results and results respect limit', () => {
    assert.deepEqual(scoring.rankGuitars(answers, 3, 40, []), []);
    assert.equal(scoring.rankGuitars(answers, 2, 40, [guitar, guitar, guitar]).length, 2);
  });
  check('shared quiz answers round-trip; invalid and incomplete links rejected', () => {
    assert.deepEqual(scoring.readAnswers(new URLSearchParams(answers)), answers);
    assert.equal(scoring.readAnswers(new URLSearchParams({ ...answers, type: 'invalid' })), null);
    assert.equal(scoring.readAnswers(new URLSearchParams('type=electric')), null);
    assert.deepEqual(scoring.readPartialAnswers(new URLSearchParams('type=electric&level=bad')), { type: 'electric' });
  });
  check('catalog URL uses existing type and budget boundaries', () => {
    assert.equal(scoring.catalogUrlFor(answers), '/guitars?type=electric&min=10000&max=30000');
    assert.equal(scoring.catalogUrlFor({ ...answers, type: 'any', budget: 'flex' }), '/guitars');
  });
  check('stored/shared ids deduplicate, reject unknowns and cap four', () => {
    const ids = GUITARS.slice(0, 6).map((g) => g.id);
    assert.deepEqual(normalizeGuitarIds([ids[0], ids[0], null, 'bad', ...ids.slice(1)], 4), ids.slice(0, 4));
    for (const invalid of [null, {}, 'text', 42]) assert.deepEqual(normalizeGuitarIds(invalid), []);
  });
  check('all-null specs are empty, not equal or different', () => {
    const items = [guitar, { ...guitar, id: 'other' }].map((g) => ({ ...g, specs: {} }));
    const row = analyseRows(items).find(({ row }) => row.key === 'neck');
    assert.equal(row.empty, true); assert.equal(row.same, false); assert.equal(row.diff, false);
  });
  check('sample specs stay hidden unless explicitly enabled', () => {
    const items = [{ ...guitar, dataStatus: 'sample' }, { ...guitar, id: 'other', specs: { weightKg: 4 } }];
    const hidden = analyseRows(items, { includeSamples: false }).find(({ row }) => row.key === 'weight');
    assert.equal(hidden.valueOf(items[0]), null); assert.equal(hidden.best, null);
    const visible = analyseRows(items, { includeSamples: true }).find(({ row }) => row.key === 'weight');
    assert.equal(visible.diff, true); assert.equal(visible.best, 3);
  });
  check('sample reviews are absent from comparison; sourced reviews can appear', () => {
    assert.ok(!analyseRows(GUITARS.slice(0, 4)).some(({ row }) => row.key === 'rating'));
    const item = { ...guitar, rating: { verified: true, source, score: 4.5, count: 3 } };
    assert.ok(analyseRows([item]).some(({ row }) => row.key === 'rating'));
  });
  check('all real catalog recommendations have finite scores and no review bonus', () => {
    const matches = GUITARS.map((g) => scoring.scoreGuitar(g, answers));
    assert.ok(matches.every((m) => Number.isFinite(m.score) && m.score >= 0 && m.score <= 99 && m.points.rating === 0));
  });
  console.log(`\n${count}/${count} checks passed`);
} finally { await server.close(); }
