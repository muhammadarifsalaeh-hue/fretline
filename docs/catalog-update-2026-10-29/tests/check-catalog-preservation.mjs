import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { createServer } from 'vite';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const AUDIT = path.join(ROOT, 'docs/catalog-update-2026-10-29');
const BASELINE = 'edc293f';
const baseline = JSON.parse(fs.readFileSync(path.join(AUDIT, 'baseline-effective.json'), 'utf8'));
const oldByID = new Map(baseline.map((g) => [g.id, g]));
const expectedPrices = {
  'fender-player-ii-telecaster': 30600,
  'fender-player-ii-telecaster-hh': 31500,
  'fender-player-ii-stratocaster': 30600,
  'fender-player-ii-mustang': 30600,
  'fender-player-ii-stratocaster-hss': 31500,
  'fender-player-ii-jaguar': 31500,
  'fender-player-ii-modified-stratocaster-hss': 39600,
  'fender-player-ii-modified-stratocaster-hss-floyd-rose': 43200,
  'fender-player-ii-modified-telecaster': 37800,
};
const expectedSpecs = {
  'yamaha-fgx830c': { bodyShape: 'Dreadnought Cutaway Style', top: 'Solid Spruce', back: 'Rosewood', sides: 'Rosewood', electronics: 'SYSTEM66' },
  'fender-player-ii-stratocaster': { bodyShape: 'Stratocaster', pickupConfiguration: 'SSS', nutWidthMm: 42, fingerboardRadiusMm: 241 },
};
const allowedSourceChanges = new Set([
  'src/data/catalog/reviewedGuitars.json', 'src/data/catalog/phase7Guitars.json',
  'src/components/compare/CompareTable.jsx', 'src/components/compare/ComparisonSlots.jsx',
  'src/components/compare/compareCategories.js', 'src/components/compare/compareRows.js',
  'src/components/detail/SpecTable.jsx', 'src/i18n/th.js', 'src/utils/dataTrust.js',
]);
const results = [];
const writeJSON = (name, value) => fs.writeFileSync(path.join(AUDIT, name), JSON.stringify(value, null, 2) + '\n');
const check = (name, fn) => {
  try { const evidence = fn(); results.push({ name, passed: true, ...(evidence ? { evidence } : {}) }); console.log(`PASS ${name}`); }
  catch (error) { results.push({ name, passed: false, error: error.stack }); console.log(`FAIL ${name}\n${error.stack}`); }
};
const positive = (v) => typeof v === 'number' && Number.isFinite(v) && v > 0;
const nonempty = (v) => v != null && (typeof v !== 'string' || v.trim() !== '');
const textKnown = (v) => typeof v === 'string' && v.trim() !== '' && !/^(?:unknown|unconfirmed|not specified|not verified|ไม่มีข้อมูล|ไม่ระบุ|ยังไม่ยืนยัน|[-—])$/iu.test(v.trim());
const requestedFields = ['bodyShape', 'body', 'top', 'back', 'sides', 'neck', 'fretboard', 'strings', 'frets', 'scale', 'pickups', 'electronics', 'bridge'];
const known = (g, field) => field === 'scale'
  ? positive(g.specs?.scaleMm) || positive(g.specs?.scale)
  : field === 'strings' ? Number.isInteger(g.specs?.strings) && g.specs.strings > 0
    : field === 'frets' ? Number.isInteger(g.specs?.frets) && g.specs.frets >= 0
      : textKnown(g.specs?.[field]);
const requiredForType = (g) => ['acoustic', 'classical'].includes(g.category)
  ? requestedFields : requestedFields.filter((field) => !['top', 'back', 'sides'].includes(field));
const metrics = (guitars) => {
  const rows = guitars.map((g) => ({
    id: g.id, brand: g.brand, name: g.name, category: g.category,
    hasVerifiedPrice: positive(g.price),
    missingStrictFields: requestedFields.filter((field) => !known(g, field)),
    requiredTypeAwareFields: requiredForType(g),
    missingTypeAwareFields: requiredForType(g).filter((field) => !known(g, field)),
  }));
  const brands = [...new Set(guitars.map((g) => g.brand))].sort();
  const perBrand = Object.fromEntries(brands.map((brand) => {
    const entries = rows.filter((g) => g.brand === brand);
    return [brand, { models: entries.length, withVerifiedPrice: entries.filter((g) => g.hasVerifiedPrice).length,
      strictCompleteSpecifications: entries.filter((g) => !g.missingStrictFields.length).length,
      typeAwareCompleteSpecifications: entries.filter((g) => !g.missingTypeAwareFields.length).length,
      priceAndTypeAwareCompleteSpecifications: entries.filter((g) => g.hasVerifiedPrice && !g.missingTypeAwareFields.length).length }];
  }));
  return {
    models: guitars.length, brands: brands.length,
    withVerifiedPrice: rows.filter((g) => g.hasVerifiedPrice).length,
    withoutVerifiedPrice: rows.filter((g) => !g.hasVerifiedPrice).length,
    withAnySpecification: guitars.filter((g) => Object.values(g.specs ?? {}).some(nonempty)).length,
    strictCompleteSpecifications: rows.filter((g) => !g.missingStrictFields.length).length,
    typeAwareCompleteSpecifications: rows.filter((g) => !g.missingTypeAwareFields.length).length,
    priceAndStrictCompleteSpecifications: rows.filter((g) => g.hasVerifiedPrice && !g.missingStrictFields.length).length,
    priceAndTypeAwareCompleteSpecifications: rows.filter((g) => g.hasVerifiedPrice && !g.missingTypeAwareFields.length).length,
    sourceStatusCounts: Object.fromEntries([...new Set(guitars.map((g) => g.dataStatus))].map((status) => [status, guitars.filter((g) => g.dataStatus === status).length])),
    fieldCoverage: Object.fromEntries(requestedFields.map((field) => [field, { known: guitars.filter((g) => known(g, field)).length, missing: guitars.filter((g) => !known(g, field)).length }])),
    perBrand, modelsByMissingFields: rows,
  };
};

const server = await createServer({ server: { middlewareMode: true, hmr: false }, appType: 'custom', logLevel: 'error' });
try {
  const { GUITARS } = await server.ssrLoadModule('/src/data/guitars.js');
  const { trustedPrice } = await server.ssrLoadModule('/src/utils/dataTrust.js');
  const finalByID = new Map(GUITARS.map((g) => [g.id, g]));
  writeJSON('final-effective.json', GUITARS);

  check('The exact 200 original IDs and their editorial order remain unchanged', () => {
    assert.equal(GUITARS.length, 200); assert.equal(finalByID.size, 200);
    assert.deepEqual(GUITARS.map((g) => g.id), baseline.map((g) => g.id));
  });
  check('All ten original brands retain exactly twenty models', () => {
    const counts = Object.fromEntries([...new Set(GUITARS.map((g) => g.brand))].map((brand) => [brand, GUITARS.filter((g) => g.brand === brand).length]));
    assert.equal(Object.keys(counts).length, 10);
    assert.ok(Object.values(counts).every((count) => count === 20)); return counts;
  });
  check('Names, categories, descriptions, colors, photos, tags, stable slugs and review/status fields are preserved', () => {
    const keys = ['id', 'brand', 'name', 'category', 'description', 'colors', 'gallery', 'image', 'hasPhotos', 'tags', 'keywords', 'slug', 'rating', 'status', 'dataStatus', 'badge', 'featured', 'oldPrice'];
    for (const old of baseline) for (const key of keys) assert.deepEqual(finalByID.get(old.id)[key], old[key], `${old.id}.${key}`);
    assert.equal(finalByID.get('epiphone-thunderbird-64-with-rosewood-fretboard').category, 'bass');
  });
  check('Every pre-existing nonempty specification remains exactly unchanged', () => {
    let count = 0;
    for (const old of baseline) for (const [key, value] of Object.entries(old.specs)) if (nonempty(value)) {
      assert.deepEqual(finalByID.get(old.id).specs[key], value, `${old.id}.specs.${key}`); count++;
    }
    return { preservedSpecificationValues: count };
  });
  check('Every original eighteen known prices and their primary source objects remain unchanged', () => {
    const oldPriced = baseline.filter((g) => positive(g.price)); assert.equal(oldPriced.length, 18);
    for (const old of oldPriced) { const current = finalByID.get(old.id); assert.equal(current.price, old.price, old.id); assert.deepEqual(current.priceSource, old.priceSource, `${old.id}.priceSource`); }
    assert.equal(finalByID.get('yamaha-pacifica-612viifm').price, 34000);
    assert.equal(finalByID.get('yamaha-fg820-12').price, 16500);
    assert.equal(finalByID.get('yamaha-fg800j').specs.back, 'Nato/Mahogany');
    assert.equal(finalByID.get('yamaha-fg800j').specs.sides, 'Nato/Mahogany');
  });
  check('Exactly the nine independently verified Fender prices are newly exposed', () => {
    const changes = GUITARS.filter((g) => g.price !== oldByID.get(g.id).price);
    assert.deepEqual(changes.map((g) => g.id).sort(), Object.keys(expectedPrices).sort());
    const evidence = JSON.parse(fs.readFileSync(path.join(AUDIT, 'verification/fender-sources.json'), 'utf8'));
    const accepted = new Map(evidence.results.filter((g) => g.accepted).map((g) => [g.id, g]));
    for (const [id, value] of Object.entries(expectedPrices)) {
      const g = finalByID.get(id); const proof = accepted.get(id);
      assert.equal(g.price, value, id); assert.equal(proof.acceptedAmountTHB, value, id);
      assert.equal(trustedPrice(g), value, id);
      assert.equal(g.priceSource.url, proof.sourceURL); assert.equal(g.priceSource.currency, 'THB');
      assert.equal(g.priceSource.verifiedOn, '2026-10-29'); assert.equal(g.priceSource.kind, 'retailer-listed');
      assert.equal(g.priceSource.retailer, 'Music Arms'); assert.equal(g.priceSource.availability, 'unknown');
      assert.equal(new URL(g.priceSource.url).hostname, 'www.musicarms.net');
      assert.ok(!new URL(g.priceSource.url).pathname.startsWith('/category/'));
    }
    assert.equal(GUITARS.filter((g) => positive(g.price)).length, 27);
    assert.ok(GUITARS.every((g) => g.price === null || trustedPrice(g) === g.price));
  });
  check('Exactly nine verified missing fields are added and every other specification including null remains unchanged', () => {
    const actual = [];
    for (const g of GUITARS) {
      const old = oldByID.get(g.id);
      for (const key of new Set([...Object.keys(old.specs), ...Object.keys(g.specs)])) {
        if (Object.hasOwn(expectedSpecs[g.id] ?? {}, key)) {
          assert.ok(!nonempty(old.specs[key]), `${g.id}.${key} must have been missing`);
          assert.deepEqual(g.specs[key], expectedSpecs[g.id][key], `${g.id}.${key}`);
          actual.push(`${g.id}.${key}`);
        } else assert.deepEqual(g.specs[key], old.specs[key], `${g.id}.${key}`);
      }
    }
    assert.equal(actual.length, 9);
    assert.equal(finalByID.get('fender-player-ii-stratocaster').specs.strings, null);
    return { additions: actual };
  });
  check('New field evidence is recorded without rewriting original manufacturer URLs, dates or verification statuses', () => {
    for (const g of GUITARS) {
      const old = oldByID.get(g.id);
      for (const key of ['url', 'verifiedOn', 'method', 'manufacturerModel', 'editionNote', 'reviewNote', 'evidence', 'batch', 'recheckedFields', 'retainedFields']) {
        assert.deepEqual(g.source?.[key], old.source?.[key], `${g.id}.source.${key}`);
      }
      for (const key of Object.keys(expectedSpecs[g.id] ?? {})) {
        assert.ok(g.source.fields.includes(`specs.${key}`));
        const proof = g.source.additionalSources.find((s) => s.batch === 'catalog-prices-2026-10-29' && s.fields.includes(`specs.${key}`));
        assert.ok(proof, `${g.id}.${key} source`); assert.equal(proof.verifiedOn, '2026-10-29');
        assert.ok(proof.quotes.length > 0); assert.equal(new URL(proof.url).protocol, 'https:');
      }
    }
  });
  check('All tracked Home, navigation, brand, Quiz, Practice, image/model assets and other protected source files are byte-identical', () => {
    const names = execFileSync('git', ['ls-tree', '-r', '-z', '--name-only', BASELINE, '--', 'src', 'public', 'scripts', 'package.json', 'package-lock.json', 'vite.config.js'], { cwd: ROOT }).toString().split('\0').filter(Boolean);
    const protectedFiles = []; const unexpectedChanges = [];
    for (const name of names) {
      if (allowedSourceChanges.has(name)) continue;
      const before = execFileSync('git', ['show', `${BASELINE}:${name}`], { cwd: ROOT, maxBuffer: 256 * 1024 * 1024 });
      const actualPath = path.join(ROOT, name);
      const expectedHash = createHash('sha256').update(before).digest('hex');
      const actualHash = fs.existsSync(actualPath) ? createHash('sha256').update(fs.readFileSync(actualPath)).digest('hex') : null;
      protectedFiles.push({ path: name, sha256: expectedHash, matches: expectedHash === actualHash });
      if (expectedHash !== actualHash) unexpectedChanges.push(name);
    }
    writeJSON('preservation.json', { baselineCommit: BASELINE, protectedTrackedFilesCompared: protectedFiles.length, unexpectedChanges, allowedModifiedSourceFiles: [...allowedSourceChanges], protectedFiles });
    assert.deepEqual(unexpectedChanges, []); return { protectedTrackedFilesCompared: protectedFiles.length };
  });

  const before = metrics(baseline); const after = metrics(GUITARS);
  const completeness = {
    baselineCommit: BASELINE,
    definition: {
      strictRequestedFields: requestedFields,
      typeAwareRule: 'Acoustic/classical require separately confirmed top/back/sides woods; electric/bass require the confirmed body material instead. All categories still require body shape, neck, fretboard, string count, fret count, scale, pickups, electronics and bridge. No absent value is inferred to be None or not applicable.',
      scaleRule: 'A positive confirmed scaleMm or scale in inches satisfies the single scale requirement.',
      knownAbsenceRule: 'An explicit source-backed None for electronics/pickups is a known fact; null or an empty string is unknown.',
      verificationStatusRule: 'dataStatus is reported separately and is not used as a substitute for field completeness.',
    },
    before, after,
  };
  writeJSON('completeness.json', completeness);
  const csv = ['id,brand,model,category,verified_price,missing_type_aware_fields,missing_strict_fields', ...after.modelsByMissingFields.map((g) => [g.id, g.brand, g.name, g.category, g.hasVerifiedPrice, g.missingTypeAwareFields.join(';'), g.missingStrictFields.join(';')].map((v) => `"${String(v).replaceAll('"', '""')}"`).join(','))].join('\n') + '\n';
  fs.writeFileSync(path.join(AUDIT, 'completeness-by-model.csv'), csv);
  const report = { baselineCommit: BASELINE, passed: results.every((r) => r.passed), passedChecks: results.filter((r) => r.passed).length, totalChecks: results.length, checks: results };
  writeJSON('tests/catalog-preservation-results.json', report);
  console.log(JSON.stringify({ ...report, checks: undefined, metrics: { models: after.models, priced: after.withVerifiedPrice, priceOnRequest: after.withoutVerifiedPrice, strictSpecsComplete: after.strictCompleteSpecifications, typeAwareSpecsComplete: after.typeAwareCompleteSpecifications, fields: after.fieldCoverage } }, null, 2));
  if (!report.passed) process.exitCode = 1;
} finally { await server.close(); }
