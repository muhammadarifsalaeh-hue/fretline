/** Exhaustive answer-space and byte-preservation audit for this visual-only change. */
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { createServer } from 'vite';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const DIR = path.dirname(fileURLToPath(import.meta.url));
const BASE = 'f2168efb6f260194e5732647073b05c8b36fe73a';
const sha = (bytes) => createHash('sha256').update(bytes).digest('hex');
const git = (...args) => execFileSync('git', args, { cwd: ROOT });
const old = (name) => git('show', `${BASE}:${name}`);
const list = (...names) => git('ls-tree', '-r', '--name-only', BASE, ...names).toString().trim().split('\n').filter(Boolean);
const protectedGroups = {
  catalogAndQuizData: list('src/data'),
  practiceSourceAndModels: list('src/features/practice', 'src/pages/PracticePage.jsx', 'scripts/practice', 'scripts/vite/practiceSceneModule.mjs'),
  scoringAndState: ['src/utils/quizScoring.js', 'src/utils/selection.js', 'src/context/ShopContext.jsx'],
  homepageAndSharedNavigation: [...list('src/components/home'), 'src/pages/HomePage.jsx', 'src/components/layout/Navbar.jsx', 'src/components/layout/Footer.jsx'],
  existingDiscovery: ['src/pages/CatalogPage.jsx', 'src/pages/BrandsPage.jsx', 'src/pages/BrandDetailPage.jsx', 'src/pages/GuitarDetailPage.jsx', 'src/pages/WishlistPage.jsx'],
};
const allProtected = [...new Set(Object.values(protectedGroups).flat())];
const protectedHashes = Object.fromEntries(allProtected.map((name) => {
  const before = old(name), current = fs.readFileSync(path.join(ROOT, name));
  assert.equal(sha(current), sha(before), `Protected source changed: ${name}`);
  return [name, sha(before)];
}));
// Additional design-safety boundaries do not rewrite the already frozen score fixture.
const extraProtectedGroups = {
  existingStyles: list('src/styles', 'src/index.css'),
  sharedLayout: list('src/components/layout'),
};
const extraProtectedFiles = [...new Set(Object.values(extraProtectedGroups).flat())];
const extraProtectedHashes = Object.fromEntries(extraProtectedFiles.map((name) => {
  const before = old(name), current = fs.readFileSync(path.join(ROOT, name));
  assert.equal(sha(current), sha(before), `Protected existing style/layout changed: ${name}`);
  return [name, sha(before)];
}));
const completeProtectedFiles = [...new Set([...allProtected, ...extraProtectedFiles])];
const completeProtectedGroups = { ...protectedGroups, ...extraProtectedGroups };
const expectedSteps = {
  type: ['electric', 'acoustic', 'classical', 'bass', 'any'],
  level: ['beginner', 'intermediate', 'advanced'],
  style: ['rock', 'blues', 'pop', 'folk', 'classical'],
  budget: ['low', 'mid', 'high', 'premium', 'flex'],
  priority: ['light', 'versatile', 'premium', 'value'],
};
const representative = [
  { type: 'acoustic', level: 'beginner', style: 'folk', budget: 'mid', priority: 'value' },
  { type: 'electric', level: 'beginner', style: 'pop', budget: 'mid', priority: 'versatile' },
  { type: 'bass', level: 'intermediate', style: 'rock', budget: 'low', priority: 'light' },
  { type: 'classical', level: 'advanced', style: 'classical', budget: 'premium', priority: 'premium' },
  { type: 'any', level: 'beginner', style: 'blues', budget: 'flex', priority: 'value' },
  { type: 'acoustic', level: 'advanced', style: 'pop', budget: 'high', priority: 'light' },
];
const snapshotMatch = ({ guitar, score, rawScore, points, reasons, caveats, typeMatch }) => ({
  id: guitar.id, brand: guitar.brand, name: guitar.name, price: guitar.price, dataStatus: guitar.dataStatus,
  score, rawScore, points, reasons, caveats, typeMatch,
});
const server = await createServer({ root: ROOT, server: { middlewareMode: true, hmr: false }, appType: 'custom', logLevel: 'error' });
try {
  const { QUIZ_STEPS } = await server.ssrLoadModule('/src/data/quiz.js');
  const { rankGuitars, SCORE_WEIGHTS, MAX_SCORE } = await server.ssrLoadModule('/src/utils/quizScoring.js');
  const { GUITARS } = await server.ssrLoadModule('/src/data/guitars.js');
  assert.deepEqual(Object.fromEntries(QUIZ_STEPS.map((step) => [step.id, step.options.map((option) => option.value)])), expectedSteps);
  assert.equal(GUITARS.length, 200); assert.equal(new Set(GUITARS.map((g) => g.id)).size, 200);
  const counts = GUITARS.reduce((all, guitar) => ({ ...all, [guitar.brand]: (all[guitar.brand] ?? 0) + 1 }), {});
  assert.equal(Object.keys(counts).length, 10); for (const count of Object.values(counts)) assert.equal(count, 20);
  assert.deepEqual(SCORE_WEIGHTS, { type: 30, level: 20, style: 20, budget: 20, priority: 10, rating: 5 });
  assert.equal(MAX_SCORE, 105);
  let combinations = [{}];
  for (const [id, values] of Object.entries(expectedSteps)) combinations = combinations.flatMap((answers) => values.map((value) => ({ ...answers, [id]: value })));
  assert.equal(combinations.length, 1500);
  const snapshots = combinations.map((answers) => ({ answers, matches: rankGuitars(answers).map(snapshotMatch) }));
  const fixture = path.join(DIR, 'baseline-scores.json');
  if (process.argv.includes('--create-baseline')) {
    assert.ok(!fs.existsSync(fixture), 'Never overwrite baseline scores with current output');
    fs.writeFileSync(fixture, JSON.stringify({ baselineCommit: BASE, locale: 'th', protectedHashes, optionValues: expectedSteps, combinations: snapshots }, null, 0) + '\n');
    fs.writeFileSync(path.join(DIR, 'browser-fixtures.json'), JSON.stringify({ baselineCommit: BASE, locale: 'th', cases: representative.map((answers) => ({ answers, matches: rankGuitars(answers).map(snapshotMatch) })) }, null, 2) + '\n');
    console.log('Created frozen baseline only after every protected input matched baseline Git bytes.');
  }
  assert.ok(fs.existsSync(fixture), 'Create baseline from the protected original inputs first');
  const baseline = JSON.parse(fs.readFileSync(fixture, 'utf8'));
  assert.equal(baseline.baselineCommit, BASE); assert.deepEqual(baseline.optionValues, expectedSteps);
  assert.deepEqual(baseline.protectedHashes, protectedHashes);
  assert.deepEqual(snapshots, baseline.combinations, 'One or more of the 1500 complete answer sets changed recommendations');
  const report = {
    passed: true, baselineCommit: BASE, baselineScoresSHA256: sha(fs.readFileSync(fixture)),
    protectedFileCount: completeProtectedFiles.length, baselineScoreBoundFileCount: allProtected.length, protectedGroups: Object.fromEntries(Object.entries(completeProtectedGroups).map(([key, files]) => [key, { count: files.length, unchanged: true }])),
    protectedHashes: { ...protectedHashes, ...extraProtectedHashes }, extraStyleAndLayoutProtectionFromGit: true, activeModels: GUITARS.length, distinctBrands: Object.keys(counts).length, brandCounts: counts,
    stableIds: GUITARS.map((guitar) => guitar.id), originalStepCount: QUIZ_STEPS.length,
    originalOptionCounts: QUIZ_STEPS.map((step) => step.options.length), completeAnswerSetsCompared: snapshots.length,
    topRecommendationRecordsCompared: snapshots.reduce((n, snapshot) => n + snapshot.matches.length, 0),
    allScoresPointsReasonsCaveatsAndOrderUnchanged: true, physicalIPadSafariTested: false,
  };
  fs.writeFileSync(path.join(DIR, 'preservation.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(`PASS ${completeProtectedFiles.length} protected files; exact 200/10/20 catalog; all ${snapshots.length} answer combinations unchanged.`);
} finally { await server.close(); }
