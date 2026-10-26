import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';

const PUBLIC_MODULE = 'virtual:fretline-yamaha-import-preview';
const PRIVATE_MODULE = '\0' + PUBLIC_MODULE;
const ROUTE_PREFIX = '/__fretline_yamaha_import_preview__/';
const PREVIEW_ROOT = 'docs/yamaha-import/preview-assets';
const CREDIT = 'ภาพจากไฟล์ผู้ใช้ — ใช้ตรวจแบบเฉพาะ Development Preview; สิทธิ์เผยแพร่และความตรงรุ่นยังไม่ยืนยัน';
const MIME_TYPES = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp' };

/** Opt-in local review of supplied illustrations. Never emits a production asset. */
export function yamahaImportPreview({ enabled, root }) {
  const models = {};
  const files = new Map();
  if (enabled) {
    const manifest = JSON.parse(fs.readFileSync(path.join(root, 'docs/yamaha-import/preview-manifest.json'), 'utf8'));
    if (manifest.schemaVersion !== 1 || !Array.isArray(manifest.models)) throw new Error('Invalid Yamaha preview manifest.');
    const folder = path.resolve(root, PREVIEW_ROOT);
    for (const model of manifest.models) {
      const id = model.guitarId;
      if (!/^yamaha-[a-z0-9]+(?:-[a-z0-9]+)*$/.test(id) || models[id]) throw new Error('Invalid or duplicate Yamaha preview model ID.');
      if (model.licenseVerified !== false || model.modelMatchVerified !== false) throw new Error(`Unverified artwork must retain its provenance: ${id}`);
      const provenance = {
        source: model.source, archive: model.archive, archiveSha256: model.archiveSha256,
        use: model.use, licenseVerified: false, originalImageRightsVerified: false,
        modelMatchVerified: false, officialColorNamesVerified: false, rightsStatus: model.rightsStatus,
      };
      const images = model.images.map((image) => {
        if (path.basename(image.file) !== image.file || !MIME_TYPES[path.extname(image.file).toLowerCase()]) throw new Error(`Invalid Yamaha preview filename: ${id}`);
        const filename = path.resolve(folder, id, image.file);
        if (!filename.startsWith(folder + path.sep)) throw new Error('Yamaha preview path escapes its folder.');
        const bytes = fs.readFileSync(filename);
        const sha256 = createHash('sha256').update(bytes).digest('hex');
        if (sha256 !== image.sha256 || bytes.length !== image.bytes || !(image.width > 0 && image.height > 0)) throw new Error(`Yamaha preview integrity check failed: ${id}/${image.file}`);
        const src = `${ROUTE_PREFIX}${id}/${sha256}/${encodeURIComponent(image.file)}`;
        if (files.has(src)) throw new Error('Duplicate Yamaha preview image route.');
        files.set(src, { bytes, type: MIME_TYPES[path.extname(image.file).toLowerCase()] });
        return {
          id: image.id, file: image.file, src, label: image.label, alt: image.alt,
          width: image.width, height: image.height, sha256, kind: 'illustration',
          credit: CREDIT, aiGenerated: image.aiGenerated, aiGenerationPossible: image.aiGenerationPossible,
          provenance: { ...provenance, originalFile: image.originalFile, changes: image.changes },
        };
      });
      models[id] = { guitarId: id, images, provenance };
    }
  }
  return {
    name: 'fretline-yamaha-import-preview',
    resolveId(id) { if (id === PUBLIC_MODULE) return PRIVATE_MODULE; },
    load(id) { if (id === PRIVATE_MODULE) return `export default ${JSON.stringify(models)};`; },
    transformIndexHtml() {
      if (enabled) return [{ tag: 'meta', attrs: { name: 'robots', content: 'noindex, nofollow, noarchive' }, injectTo: 'head' }];
    },
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        if (enabled) response.setHeader('X-Robots-Tag', 'noindex, nofollow, noarchive');
        const pathname = new URL(request.url ?? '/', 'http://localhost').pathname;
        if (!pathname.startsWith(ROUTE_PREFIX)) return next();
        response.setHeader('Cache-Control', 'no-store');
        response.setHeader('X-Robots-Tag', 'noindex, nofollow, noarchive');
        response.setHeader('X-Content-Type-Options', 'nosniff');
        const file = files.get(pathname);
        if (!file) { response.statusCode = 404; response.end('Yamaha development illustration unavailable'); return; }
        if (!['GET', 'HEAD'].includes(request.method)) {
          response.statusCode = 405; response.setHeader('Allow', 'GET, HEAD'); response.end(); return;
        }
        response.setHeader('Content-Type', file.type);
        response.setHeader('Content-Length', file.bytes.length);
        response.end(request.method === 'HEAD' ? undefined : file.bytes);
      });
    },
  };
}
