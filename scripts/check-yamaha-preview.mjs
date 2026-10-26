import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { resolveConfig } from 'vite';
import { yamahaImportPreview } from './vite/yamahaImportPreview.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MODULE = '\0virtual:fretline-yamaha-import-preview';
const PREFIX = '/__fretline_yamaha_import_preview__/';
const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/yamaha-import/preview-manifest.json'), 'utf8'));
const parse = (plugin) => JSON.parse(plugin.load(MODULE).replace(/^export default /, '').slice(0, -1));
let checks = 0;
const check = (name, fn) => { fn(); checks++; console.log(`PASS ${name}`); };
const plugin = yamahaImportPreview({ enabled: true, root: ROOT });
const models = parse(plugin);
const images = Object.values(models).flatMap((model) => model.images);
check('18 accessible archives, 18 stable model IDs and 20 distinct original files', () => {
  assert.equal(manifest.intendedArchiveCount, 19); assert.equal(manifest.accessibleArchiveCount, 18);
  assert.equal(Object.keys(models).length, 18); assert.equal(images.length, 20);
  assert.equal(new Set(images.map((image) => image.src)).size, 20);
  assert.deepEqual(models['yamaha-fg800'].images.map((image) => image.label.split(' — ')[0]), ['Natural', 'Black', 'Sunburst']);
});
check('uploaded files keep their original SHA-256, byte counts and true dimensions', () => {
  for (const model of manifest.models) for (const image of model.images) {
    const bytes = fs.readFileSync(path.join(ROOT, 'docs/yamaha-import/preview-assets', model.guitarId, image.file));
    const original = manifest.archives.find((archive) => archive.archive === model.archive).files.find((file) => file.path.endsWith('/' + image.originalFile));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), image.sha256);
    assert.equal(bytes.length, image.bytes); assert.equal(image.sha256, original.sha256);
    assert.equal(image.width, model.guitarId === 'yamaha-fs830' ? 1000 : 1254);
    assert.equal(image.height, image.width);
  }
});
check('rights and product accuracy are explicitly unverified, with true creation notes', () => {
  for (const model of Object.values(models)) {
    assert.equal(model.provenance.licenseVerified, false); assert.equal(model.provenance.modelMatchVerified, false);
    assert.equal(model.provenance.originalImageRightsVerified, false); assert.equal(model.provenance.officialColorNamesVerified, false);
    for (const image of model.images) {
      assert.equal(image.kind, 'illustration'); assert.match(image.credit, /Development Preview/);
      assert.match(image.credit, /ยังไม่ยืนยัน/); assert.equal(image.attribution, undefined);
    }
  }
  assert.equal(models['yamaha-fg800'].images.every((image) => image.aiGenerated === true), true);
  assert.equal(models['yamaha-fg840'].images[0].aiGenerated, true);
  assert.equal(models['yamaha-fg850'].images[0].aiGenerated, true);
  assert.equal(models['yamaha-fsx830c'].images[0].aiGenerated, null);
  assert.equal(models['yamaha-fs830'].images[0].aiGenerationPossible, true);
});
let handler;
plugin.configureServer({ middlewares: { use(fn) { handler = fn; } } });
function request(url, method = 'GET') {
  const response = { statusCode: 200, headers: {}, setHeader(key, value) { this.headers[key] = value; }, end(body) { this.body = body; } };
  handler({ url, method }, response, () => { response.next = true; });
  return response;
}
check('all 20 preview image routes return original bytes, real MIME type and review-only headers', () => {
  for (const image of images) {
    const response = request(image.src);
    assert.equal(response.statusCode, 200); assert.ok(Buffer.isBuffer(response.body));
    assert.equal(createHash('sha256').update(response.body).digest('hex'), image.sha256);
    assert.equal(response.headers['Content-Type'], image.file.endsWith('.png') ? 'image/png' : image.file.endsWith('.webp') ? 'image/webp' : 'image/jpeg');
    assert.equal(response.headers['Cache-Control'], 'no-store');
    assert.equal(response.headers['X-Content-Type-Options'], 'nosniff');
    assert.match(response.headers['X-Robots-Tag'], /noindex/);
  }
});
check('HEAD is bodyless and non-reading methods are rejected', () => {
  for (const image of images) {
    assert.equal(request(image.src, 'HEAD').body, undefined);
    for (const method of ['POST', 'PUT', 'DELETE', 'PATCH']) {
      const response = request(image.src, method);
      assert.equal(response.statusCode, 405); assert.equal(response.headers.Allow, 'GET, HEAD');
    }
  }
});
check('only exact hash-bound model/file routes load; unknown paths cannot expose a file', () => {
  for (const url of [PREFIX + 'missing.png', images[0].src.replace(images[0].sha256, '0'.repeat(64)), images[0].src.replace('yamaha-fsx830c', 'yamaha-fgx830c'), PREFIX + '%2e%2e%2f.env']) assert.equal(request(url).statusCode, 404);
  assert.equal(request('/catalog').next, true);
  assert.match(request('/catalog').headers['X-Robots-Tag'], /noindex/);
});
check('enabled development pages receive an explicit robots exclusion', () => {
  const tags = plugin.transformIndexHtml();
  assert.equal(tags[0].attrs.name, 'robots'); assert.match(tags[0].attrs.content, /noindex/);
});
check('disabled preview does not read source files, emit assets or change ordinary page indexing', () => {
  const disabled = yamahaImportPreview({ enabled: false, root: '/a/path/that/does/not/exist' });
  assert.deepEqual(parse(disabled), {}); assert.equal(disabled.transformIndexHtml(), undefined);
  let offHandler; disabled.configureServer({ middlewares: { use(fn) { offHandler = fn; } } });
  const response = { headers: {}, setHeader(key, value) { this.headers[key] = value; }, end(body) { this.body = body; } };
  offHandler({ url: images[0].src, method: 'GET' }, response, () => { response.next = true; });
  assert.equal(response.statusCode, 404); assert.equal(response.next, undefined);
});
for (const mode of ['production', 'yamaha-preview', 'pacifica-preview']) {
  const config = await resolveConfig({ mode, logLevel: 'silent' }, 'build');
  check(`build mode ${mode} always has an empty Yamaha image module`, () => {
    assert.deepEqual(parse(config.plugins.find((entry) => entry.name === plugin.name)), {});
  });
}
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'fretline-yamaha-preview-test-'));
try {
  fs.mkdirSync(path.join(temporary, 'docs/yamaha-import'), { recursive: true });
  const writeManifest = (value) => fs.writeFileSync(path.join(temporary, 'docs/yamaha-import/preview-manifest.json'), JSON.stringify(value));
  check('path traversal and false rights approval in a manifest fail closed', () => {
    const fixture = { schemaVersion: 1, models: [{ ...manifest.models[0], images: [{ ...manifest.models[0].images[0], file: '../escape.png' }] }] };
    writeManifest(fixture); assert.throws(() => yamahaImportPreview({ enabled: true, root: temporary }), /filename/);
    writeManifest({ schemaVersion: 1, models: [{ ...manifest.models[0], licenseVerified: true }] });
    assert.throws(() => yamahaImportPreview({ enabled: true, root: temporary }), /provenance/);
  });
  check('altered image bytes fail the original integrity binding', () => {
    const model = manifest.models[0];
    const destination = path.join(temporary, 'docs/yamaha-import/preview-assets', model.guitarId);
    fs.mkdirSync(destination, { recursive: true }); fs.writeFileSync(path.join(destination, model.images[0].file), 'altered');
    writeManifest({ schemaVersion: 1, models: [model] });
    assert.throws(() => yamahaImportPreview({ enabled: true, root: temporary }), /integrity/);
  });
} finally { fs.rmSync(temporary, { recursive: true, force: true }); }
console.log(`${checks} Yamaha development preview isolation/integrity checks passed.`);
