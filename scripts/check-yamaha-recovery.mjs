import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { createServer } from 'vite';

// Read-only audit: never imports into Supabase, edits product data or publishes images.
const root = process.cwd();
const importedAt = 'f2168efb6f260194e5732647073b05c8b36fe73a';
const latestAtStart = 'a3e770d7d07f6a10dac9788cd6765c6bf6f028dc';
const git = (...args) => execFileSync('git', args, { encoding: 'utf8' }).trim();
const read = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const hash = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
const manifest = read('docs/yamaha-import/preview-manifest.json');
const reviewed = read('src/data/catalog/reviewedGuitars.json');
const imported = JSON.parse(git('show', `${importedAt}:src/data/catalog/reviewedGuitars.json`));
const folder = 'docs/yamaha-recovery-2026-10-30';
const originalPaths = ['docs/yamaha-import/original-metadata', 'docs/yamaha-import/preview-assets', 'docs/yamaha-import/preview-manifest.json'];
const imageByHash = new Map(manifest.models.flatMap((model) => model.images.map((image) => [image.sha256, { model, image }])));
const files = [];
for (const archive of manifest.archives) {
  for (const original of archive.files) {
    const picture = imageByHash.get(original.sha256);
    const retainedPath = picture
      ? `docs/yamaha-import/preview-assets/${picture.model.guitarId}/${picture.image.file}`
      : `docs/yamaha-import/original-metadata/${original.path}`;
    const bytes = fs.readFileSync(retainedPath);
    assert.equal(hash(bytes), original.sha256, retainedPath);
    assert.equal(bytes.length, original.bytes, retainedPath);
    const extractedPath = path.join('.yamaha-intake', original.path);
    const extractedAlsoVerified = fs.existsSync(extractedPath);
    if (extractedAlsoVerified) assert.equal(hash(fs.readFileSync(extractedPath)), original.sha256, extractedPath);
    files.push({ archive: archive.archive, originalPath: original.path, retainedPath, kind: picture ? 'image' : 'metadata', bytes: bytes.length, sha256: original.sha256, extractedAlsoVerified });
  }
}
assert.equal(manifest.archives.length, 18);
assert.equal(manifest.models.length, 18);
assert.equal(files.filter((file) => file.kind === 'image').length, 20);
assert.equal(files.filter((file) => file.kind === 'metadata').length, 50);
assert.equal(git('diff', '--name-only', importedAt, 'HEAD', '--', ...originalPaths), '');
for (const model of manifest.models) {
  assert.deepEqual(reviewed[model.guitarId], imported[model.guitarId], `Imported data changed: ${model.guitarId}`);
  assert.equal(reviewed[model.guitarId].intake.archiveSha256, model.archiveSha256);
}

async function catalog(mode) {
  const server = await createServer({ mode, logLevel: 'error', server: { middlewareMode: true, hmr: false }, appType: 'custom' });
  try {
    const { GUITARS } = await server.ssrLoadModule('/src/data/guitars.js');
    const { BRANDS } = await server.ssrLoadModule('/src/data/brands.js');
    assert.equal(GUITARS.length, 200);
    assert.equal(new Set(GUITARS.map((g) => g.id)).size, 200);
    assert.equal(BRANDS.length, 10);
    const brandCounts = Object.fromEntries(BRANDS.map((brand) => [brand.name, GUITARS.filter((g) => g.brand === brand.name).length]));
    assert.ok(Object.values(brandCounts).every((count) => count === 20));
    return {
      mode, guitars: GUITARS.length, brands: BRANDS.length, brandCounts,
      yamaha: GUITARS.filter((g) => g.brand === 'Yamaha').map((g) => ({ id: g.id, name: g.name, category: g.category, description: g.description, priceTHB: g.price, priceSource: g.priceSource ?? null, specs: g.specs, dataStatus: g.dataStatus, gallery: g.gallery.map((image) => ({ src: image.src, width: image.width, height: image.height, sha256: image.sha256 ?? null, kind: image.kind ?? 'photo' })) })),
    };
  } finally { await server.close(); }
}
const production = await catalog('production');
const preview = await catalog('yamaha-preview');
assert.equal(production.yamaha.length, 20);
assert.equal(preview.yamaha.length, 20);
assert.equal(production.yamaha.filter((g) => g.gallery.length).length, 2);
assert.equal(preview.yamaha.filter((g) => g.gallery.length).length, 19);
for (const model of manifest.models) {
  const normal = production.yamaha.find((g) => g.id === model.guitarId);
  const review = preview.yamaha.find((g) => g.id === model.guitarId);
  assert.ok(normal.description && Object.values(normal.specs).some((value) => value != null));
  assert.deepEqual(normal.specs, reviewed[model.guitarId].specs);
  assert.equal(normal.description, reviewed[model.guitarId].description);
  assert.equal(normal.priceTHB, reviewed[model.guitarId].price);
  const images = review.gallery.filter((image) => image.src.startsWith('/__fretline_yamaha_import_preview__/'));
  assert.equal(images.length, model.images.length);
  assert.deepEqual(new Set(images.map((image) => image.sha256)), new Set(model.images.map((image) => image.sha256)));
}
assert.ok(!production.yamaha.some((g) => g.gallery.some((image) => image.src.startsWith('/__fretline_yamaha_import_preview__/'))));
const missingId = 'yamaha-fgx830c';
assert.ok(production.yamaha.some((g) => g.id === missingId && g.description && !g.gallery.length));
assert.ok(!manifest.models.some((model) => model.guitarId === missingId));

const branches = git('for-each-ref', '--format=%(refname)', 'refs/heads', 'refs/remotes/origin').split('\n').filter((ref) => !ref.endsWith('/HEAD')).map((ref) => {
  const commit = git('rev-parse', ref);
  const importedFiles = git('ls-tree', '-r', '--name-only', ref, '--', ...originalPaths).split('\n').filter(Boolean);
  return { ref, commit, importedFiles: importedFiles.length, originalsMatchImport: !git('diff', '--name-only', importedAt, ref, '--', ...originalPaths) };
});
const historicFiles = git('log', '--all', '--format=', '--name-only', '--', '*yamaha*', '*Yamaha*', '*FGX830*', '*fgx830*').split('\n').filter(Boolean);
const fgx830cOriginalFilesInAccessibleHistory = [...new Set(historicFiles.filter((file) => /fgx830/i.test(file)))];
assert.deepEqual(fgx830cOriginalFilesInAccessibleHistory, []);
assert.equal(git('rev-parse', 'master'), '9f7b35d7a0daea8a579976a5534ffb67d90f06a9');
assert.equal(git('diff', '--name-only', latestAtStart, 'HEAD', '--', 'src', 'public', 'supabase', 'vite.config.js', 'package.json'), '');

const report = {
  passed: true, auditedAt: new Date().toISOString(), latestApplicationCommit: latestAtStart, importCommit: importedAt, branch: git('branch', '--show-current'),
  counts: { receivedArchiveSets: 18, requestedArchiveSets: 19, originalFilesVerified: files.length, metadataFiles: 50, imageFiles: 20, importedModelRecordsUnchanged: 18, originalImagesLinkedInOptInPreview: 20, modelsWithUploadedImagesLinkedInOptInPreview: 18, allYamahaModels: 20, normalModelsWithImages: 2, previewModelsWithImages: 19, missingOriginalSets: 1 },
  findings: { originalsIdenticalToImport: true, importedRecordsIdenticalToImport: true, latestRedesignDeletedOriginals: false, applicationSourceChangedForThisAudit: false, databaseRead: false, databaseWrite: false, liveSupabaseVerified: false, imagePublicationRulesChanged: false, pushed: false, merged: false, deployed: false },
  missing: [{ id: missingId, name: 'FGX830C', missingOriginals: ['User-supplied FGX830C archive', 'Original product image(s)', 'Supplied model JSON and/or description file'], existingCatalogRecordPresent: true, existingSourceBackedDescriptionAndSpecsPresent: true, confirmedTHBPrice: null, exactMissingFilenamesKnown: false }],
  branches, fgx830cOriginalFilesInAccessibleHistory, files,
  models: production.yamaha.map((g) => {
    const supplied = manifest.models.find((model) => model.guitarId === g.id);
    const before = preview.yamaha.find((model) => model.id === g.id);
    return { ...g, importedArchive: supplied?.archive ?? null, importedImages: supplied?.images.length ?? 0, productionGalleryCount: g.gallery.length, previewGalleryCount: before.gallery.length, previewGallery: before.gallery, detailsRoute: `/guitars/${g.id}`, specificationRoute: `/guitars/${g.id}#specs` };
  }),
};
if (process.argv.includes('--report')) {
  fs.mkdirSync(folder, { recursive: true });
  fs.writeFileSync(path.join(folder, 'audit.json'), JSON.stringify(report, null, 2) + '\n');
}
console.log(JSON.stringify({ passed: report.passed, counts: report.counts, findings: report.findings, missing: report.missing, branchesInspected: branches.length }, null, 2));
