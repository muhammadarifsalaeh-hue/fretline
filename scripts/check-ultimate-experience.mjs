import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createServer } from 'vite';
import postcss from 'postcss';

const baseline = JSON.parse(fs.readFileSync('docs/ultimate-experience-2026-10-30/safety-baseline.json', 'utf8'));
const hash = (value) => crypto.createHash('sha256').update(value).digest('hex');
for (const [path, expected] of Object.entries(baseline.protectedFiles)) {
  assert.equal(hash(fs.readFileSync(path)), expected, `Protected data, original artwork or system file changed: ${path}`);
}
assert.equal(execFileSync('git', ['rev-parse', 'master'], { encoding: 'utf8' }).trim(), baseline.masterCommit);
assert.match(execFileSync('git', ['branch', '--show-current'], { encoding: 'utf8' }).trim(), /^feature\//);
const routes = [...fs.readFileSync('src/App.jsx', 'utf8').matchAll(/<Route path="([^"]+)"/g)].map((match) => match[1]);
assert.deepEqual(routes, baseline.routes);
for (const path of ['src/components/home/Brands.jsx', 'src/hooks/useBrandMarquee.js', 'src/styles/home-brands.css']) {
  assert.equal(fs.readFileSync(path, 'utf8'), execFileSync('git', ['show', `${baseline.baseCommit}:${path}`], { encoding: 'utf8' }), `Original Home brand rail not restored: ${path}`);
}
// Exact reversal of the only permitted copy changes in the learning page.
const practice = fs.readFileSync('src/pages/PracticePage.jsx', 'utf8')
  .replace("docTitle: 'ฝึกคอร์ดกีตาร์ 3D | Fretline'", "docTitle: 'Guitar Practice Studio — ฝึกคอร์ด 3D | Fretline'")
  .replace("eyebrow: 'ฝึกคอร์ดทีละขั้น', intro: 'ฝึกทีละคอร์ด", "eyebrow: 'THE ART OF YOUR NEXT CHORD', intro: 'ฝึกทีละคอร์ด")
  .replace("stage: 'พื้นที่ฝึกกีตาร์', stageTitle: 'มองให้ชัด", "stage: 'YOUR PRACTICE SPACE', stageTitle: 'มองให้ชัด");
assert.equal(practice, execFileSync('git', ['show', `${baseline.baseCommit}:src/pages/PracticePage.jsx`], { encoding: 'utf8' }), 'Practice behavior must remain exactly unchanged');
assert.equal(hash(fs.readFileSync('src/assets/home-practice/practice-black-gold-les-paul.jpg')), baseline.originalPracticeImageSHA256);
for (const file of fs.readdirSync('src/styles').filter((file) => file.startsWith('experience-'))) {
  postcss.parse(fs.readFileSync(`src/styles/${file}`, 'utf8')).walkRules((rule) => {
    if (rule.parent?.type === 'atrule' && /keyframes$/.test(rule.parent.name)) return;
    assert.ok(rule.selectors.every((selector) => selector.startsWith('.fretline-experience')), `Public style leaks into Admin: ${file}: ${rule.selector}`);
  });
}
assert.ok(fs.readFileSync('src/components/layout/VisitorExperience.jsx','utf8').includes("pathname.replace(/\\/$/, '') !== '/admin'"));
const server = await createServer({ logLevel: 'error', server: { middlewareMode: true, hmr: false }, appType: 'custom' });
try {
  const { GUITARS, SAVED_GUITARS_BY_ID } = await server.ssrLoadModule('/src/data/guitars.js');
  const { BRANDS } = await server.ssrLoadModule('/src/data/brands.js');
  const { PRACTICE_CHORDS } = await server.ssrLoadModule('/src/features/practice/data/chords.js');
  const data = { guitars: GUITARS, saved: SAVED_GUITARS_BY_ID, brands: BRANDS, chords: PRACTICE_CHORDS };
  assert.equal(hash(JSON.stringify(data, null, 2)), baseline.effectiveDataSHA256);
  assert.equal(GUITARS.length, 200); assert.equal(new Set(GUITARS.map((g) => g.id)).size, 200);
  assert.equal(BRANDS.length, 10);
  const counts = Object.fromEntries(BRANDS.map((b) => [b.name, GUITARS.filter((g) => g.brand === b.name).length]));
  assert.ok(Object.values(counts).every((n) => n === 20));
  assert.equal(PRACTICE_CHORDS.length, 42);
  console.log(JSON.stringify({ passed: true, protectedFiles: Object.keys(baseline.protectedFiles).length, models: GUITARS.length, uniqueIds: 200, brands: BRANDS.length, modelsPerBrand: counts, categories: Object.fromEntries(['electric','acoustic','classical','bass'].map((type) => [type, GUITARS.filter((g) => g.category === type).length])), chords: PRACTICE_CHORDS.length, allOriginalDataAndImageRelationsIdentical: true, learningPageBehaviorIdentical: true, adminSourceIdentical: true, existingRoutes: routes.length, originalPracticePhotoIdentical: true, publicStylesScoped: true, databaseWrites: false, hostedSupabaseVerified: false }, null, 2));
} finally { await server.close(); }
