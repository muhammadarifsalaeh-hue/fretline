import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { createServer } from 'vite';
import postcss from 'postcss';
import { uiLogicDigest } from './lib/targeted-ui-logic.mjs';

const baseline = JSON.parse(fs.readFileSync('docs/targeted-ui-2026-10-30/safety-baseline.json', 'utf8'));
const hash = (value) => crypto.createHash('sha256').update(value).digest('hex');
for (const [path, expected] of Object.entries(baseline.protectedFiles)) assert.equal(hash(fs.readFileSync(path)), expected, `Protected file changed: ${path}`);
for (const [path, expected] of Object.entries(baseline.displayOnlyLogic)) assert.equal(uiLogicDigest(fs.readFileSync(path, 'utf8')), expected, `Change exceeds display copy: ${path}`);
const routes = [...fs.readFileSync('src/App.jsx', 'utf8').matchAll(/<Route path="([^"]+)"/g)].map((match) => match[1]);
assert.deepEqual(routes, baseline.routes);
assert.equal(hash(fs.readFileSync('src/assets/home-practice/practice-black-gold-les-paul.jpg')), baseline.originalPracticeImageSHA256, 'The supplied original practice image must not be edited');
const css = postcss.parse(fs.readFileSync('src/styles/home-targeted-refinement.css', 'utf8'));
css.walkRules((rule) => {
  for (const selector of rule.selectors) {
    assert.ok(selector.startsWith('.signature-home.premium-home '), `Unscoped style: ${selector}`);
    assert.match(selector, /#categories|signature-category-pill|category-pill-art|home-practice-black-gold/, `Style exceeds requested Home sections: ${selector}`);
  }
});

const server = await createServer({ logLevel: 'error', server: { middlewareMode: true, hmr: false }, appType: 'custom' });
try {
  const { GUITARS, SAVED_GUITARS_BY_ID } = await server.ssrLoadModule('/src/data/guitars.js');
  const { BRANDS } = await server.ssrLoadModule('/src/data/brands.js');
  const { PRACTICE_CHORDS } = await server.ssrLoadModule('/src/features/practice/data/chords.js');
  const data = { guitars: GUITARS, saved: SAVED_GUITARS_BY_ID, brands: BRANDS, chords: PRACTICE_CHORDS };
  assert.equal(hash(JSON.stringify(data, null, 2)), baseline.effectiveDataSHA256, 'Product fields, sources, image relationships, brands or chord data changed');
  assert.equal(GUITARS.length, 200); assert.equal(new Set(GUITARS.map((g) => g.id)).size, 200);
  assert.equal(BRANDS.length, 10); assert.ok(BRANDS.every((brand) => brand.models === 20));
  assert.equal(PRACTICE_CHORDS.length, 42);
  const { th } = await server.ssrLoadModule('/src/i18n/th.js');
  const { en } = await server.ssrLoadModule('/src/i18n/en.js');
  for (const key of Object.keys(th).filter((key) => key.startsWith('targeted.') || key === 'nav.admin')) assert.ok(en[key], `English fallback lost: ${key}`);
  console.log(JSON.stringify({ passed: true, protectedFiles: Object.keys(baseline.protectedFiles).length, displayOnlyModulesChecked: Object.keys(baseline.displayOnlyLogic).length, models: 200, uniqueIds: 200, brands: 10, modelsPerBrand: 20, chords: 42, allProductFieldsIdentical: true, existingHeroSourceAndStylesUnchanged: true, suppliedPracticeImageIdentical: true, routesUnchanged: routes.length, sqlExecuted: false, deployed: false, hostedSupabaseVerified: false }, null, 2));
} finally { await server.close(); }
