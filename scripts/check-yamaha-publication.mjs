import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createServer } from 'vite';

const folder = 'docs/yamaha-live-release-2026-10-30';
const read = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const hash = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
const git = (...args) => execFileSync('git', args, { encoding: 'utf8' }).trim();
const before = read(`${folder}/baseline.json`);
const oldGuard = read('docs/ultimate-experience-2026-10-30/safety-baseline.json');
const manifest = read('docs/yamaha-import/preview-manifest.json');
const artwork = read('src/data/catalog/projectArtwork.json');
const intendedChanges = new Set(['src/data/catalog/projectArtwork.json', 'src/data/guitarImages.js']);
for (const [file, expected] of Object.entries(oldGuard.protectedFiles)) {
  if (!intendedChanges.has(file)) assert.equal(hash(fs.readFileSync(file)), expected, `Protected file changed: ${file}`);
}
for (const [id, record] of Object.entries(before.previousProjectArtwork)) assert.deepEqual(artwork[id], record, `Existing artwork registration changed: ${id}`);
const images = [];
for (const model of manifest.models) {
  const current = artwork[model.guitarId];
  assert.equal(current.usage, 'user-requested-project-use');
  assert.equal(current.archiveSha256, model.archiveSha256);
  assert.equal(current.licenseVerified, false);
  assert.equal(current.modelMatchVerified, false);
  for (const image of model.images) {
    const source = `docs/yamaha-import/preview-assets/${model.guitarId}/${image.file}`;
    const target = `src/assets/guitars/${model.guitarId}/${image.file}`;
    intendedChanges.add(target);
    assert.equal(hash(fs.readFileSync(source)), image.sha256, source);
    assert.equal(hash(fs.readFileSync(target)), image.sha256, target);
    assert.deepEqual(current.images.find((candidate) => candidate.file === image.file), { ...image, credit: 'ภาพประกอบจากไฟล์ที่เจ้าของเว็บไซต์จัดเตรียม' });
    images.push({ id: model.guitarId, source, target, sha256: image.sha256, bytes: image.bytes });
  }
}
assert.equal(images.length, 20);
assert.equal(new Set(images.map((image) => image.id)).size, 18);
for (const file of git('diff', '--name-only', before.baseCommit, '--', 'src', 'public', 'supabase', 'vite.config.js', 'package.json', 'package-lock.json').split('\n').filter(Boolean)) assert.ok(intendedChanges.has(file), `Unexpected application change: ${file}`);
assert.deepEqual([...fs.readFileSync('src/App.jsx', 'utf8').matchAll(/<Route path="([^"]+)"/g)].map((match) => match[1]), oldGuard.routes);

const omitImages = (g) => Object.fromEntries(Object.entries(g).filter(([key]) => !['image', 'gallery', 'hasPhotos'].includes(key)));
async function inspect(mode) {
  const server = await createServer({ mode, logLevel: 'error', server: { middlewareMode: true, hmr: false }, appType: 'custom' });
  try {
    const { GUITARS, SAVED_GUITARS_BY_ID } = await server.ssrLoadModule('/src/data/guitars.js');
    const { BRANDS } = await server.ssrLoadModule('/src/data/brands.js');
    const { PRACTICE_CHORDS } = await server.ssrLoadModule('/src/features/practice/data/chords.js');
    assert.equal(GUITARS.length, 200);
    assert.equal(new Set(GUITARS.map((g) => g.id)).size, 200);
    assert.equal(BRANDS.length, 10);
    const counts = Object.fromEntries(BRANDS.map((brand) => [brand.name, GUITARS.filter((g) => g.brand === brand.name).length]));
    assert.ok(Object.values(counts).every((count) => count === 20));
    assert.equal(PRACTICE_CHORDS.length, 42);
    const stable = { guitars: GUITARS.map(omitImages), saved: Object.fromEntries(Object.entries(SAVED_GUITARS_BY_ID).map(([id, g]) => [id, omitImages(g)])), brands: BRANDS, chords: PRACTICE_CHORDS };
    assert.equal(hash(JSON.stringify(stable)), before.nonImageDataSha256, 'Product facts, prices, IDs, saved records, brands or chord data changed');
    const importedIds = new Set(manifest.models.map((model) => model.guitarId));
    for (const g of GUITARS) {
      if (!importedIds.has(g.id)) assert.equal(hash(JSON.stringify({ image: g.image, gallery: g.gallery, hasPhotos: g.hasPhotos })), before.originalGallerySha256[g.id], `Unrelated model gallery changed: ${g.id}`);
      else {
        const original = manifest.models.find((model) => model.guitarId === g.id);
        for (const image of original.images) assert.equal(g.gallery.filter((candidate) => candidate.file === image.file && candidate.sha256 === image.sha256).length, 1, `Original image missing or duplicated: ${g.id}/${image.file}`);
        assert.equal(g.gallery.length, original.images.length + (g.id === 'yamaha-fg820-12' ? 1 : 0));
      }
    }
    const yamaha = GUITARS.filter((g) => g.brand === 'Yamaha');
    assert.equal(yamaha.length, 20);
    assert.equal(yamaha.filter((g) => g.hasPhotos).length, 19);
    assert.equal(yamaha.find((g) => g.id === 'yamaha-fgx830c').hasPhotos, false);
    const licensed = GUITARS.find((g) => g.id === 'yamaha-fg820-12').gallery[0];
    assert.equal(licensed.file ?? licensed.attribution?.file, '01-front.webp');
    return { mode, guitars: GUITARS.length, uniqueIds: 200, brands: BRANDS.length, counts, chords: PRACTICE_CHORDS.length, yamahaModels: yamaha.length, yamahaWithImages: 19, allOriginalProductDataUnchanged: true, unrelatedGalleriesUnchanged: true, duplicateImages: false, yamaha: yamaha.map((g) => ({ id: g.id, name: g.name, description: g.description, specs: g.specs, priceTHB: g.price, gallery: g.gallery.map((image) => ({ src: image.src, sha256: image.sha256 ?? image.attribution?.sha256 ?? null, width: image.width, height: image.height })), galleryCount: g.gallery.length })) };
  } finally { await server.close(); }
}
const modes = [await inspect('production'), await inspect('yamaha-preview')];
const report = { passed: true, checkedAt: new Date().toISOString(), originalImageCount: 20, imageModels: 18, originalBytesUnchanged: true, protectedFilesChecked: Object.keys(oldGuard.protectedFiles).length - [...intendedChanges].filter((file) => file in oldGuard.protectedFiles).length, applicationChanges: [...intendedChanges], modes, images, missing: ['yamaha-fgx830c'], databaseWrites: false, liveAdminTransactionsVerified: false };
if (process.argv.includes('--report')) fs.writeFileSync(`${folder}/tests/data-and-images.json`, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ passed: true, originalImages: 20, imageModels: 18, yamahaModels: 20, yamahaWithImages: 19, catalog: 200, brands: 10, chords: 42, allNonImageDataUnchanged: true, duplicates: 0, missingOriginals: report.missing }, null, 2));
