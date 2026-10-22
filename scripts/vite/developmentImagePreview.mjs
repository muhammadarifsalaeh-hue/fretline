import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';

const PUBLIC_MODULE = 'virtual:fretline-development-image-preview';
const PRIVATE_MODULE = '\0' + PUBLIC_MODULE;
const MODEL_ID = 'yamaha-pacifica-612viifm';
const ROUTE_PREFIX = '/__fretline_development_preview__/';
const IMAGES = [
  { id: 'black', file: '01-black.jpg', label: 'Black', hex: '#252527' },
  { id: 'red', file: '02-red.jpg', label: 'Red', hex: '#a02a24' },
  { id: 'blue-teal', file: '03-blue-teal.jpg', label: 'Blue / Teal', hex: '#237c89' },
  { id: 'all-colors', file: '04-all-colors.jpg', label: 'All colors', labelKey: 'imagePreview.allColors' },
];

/** Read JPEG frame dimensions without changing, decoding or re-encoding bytes. */
function jpegDimensions(bytes) {
  if (bytes.readUInt16BE(0) !== 0xffd8) throw new Error('Development gallery files must be JPEG originals.');
  const frames = new Set([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf]);
  for (let offset = 2; offset + 8 < bytes.length;) {
    if (bytes[offset] !== 0xff) break;
    if (bytes[offset + 1] === 0xff) { offset++; continue; }
    const marker = bytes[offset + 1];
    const length = bytes.readUInt16BE(offset + 2);
    if (frames.has(marker)) return { width: bytes.readUInt16BE(offset + 7), height: bytes.readUInt16BE(offset + 5) };
    if (length < 2) break;
    offset += length + 2;
  }
  throw new Error('Cannot read development JPEG dimensions.');
}

/** The rights-unverified illustration is never a catalog photo or a build asset. */
export function developmentImagePreview({ enabled, root }) {
  let metadata = null;
  const files = new Map();
  if (enabled) {
    const originalsAvailable = IMAGES.every(({ file }) => fs.existsSync(path.join(root, '.local-preview', MODEL_ID, file)));
    // A fresh Codespace has no private assets. It can still start and let the
    // owner select the originals locally in their browser, without an upload.
    const images = originalsAvailable ? IMAGES.map(({ file, hex, ...image }) => {
      const filename = path.join(root, '.local-preview', MODEL_ID, file);
      if (!fs.existsSync(filename)) throw new Error(`Development gallery file missing: ${filename}. Supply the original attachment; no image is downloaded automatically.`);
      const bytes = fs.readFileSync(filename);
      const dimensions = jpegDimensions(bytes);
      const sha256 = createHash('sha256').update(bytes).digest('hex');
      const src = `${ROUTE_PREFIX}${MODEL_ID}/${image.id}/${sha256.slice(0, 20)}.jpg`;
      files.set(src, bytes);
      return { ...image, src, ...dimensions, sha256, colorId: hex ? image.id : null };
    }) : [];
    metadata = {
      guitarId: MODEL_ID, images,
      colors: IMAGES.filter((image) => image.hex).map(({ id, label, hex }) => ({ id, name: label, hex, imageId: id })),
      aiEdited: true, productPhotoVerified: false, originalImageRightsVerified: false,
      modelMatchVerified: false, officialColorNamesVerified: false, source: 'User-supplied attachments',
      use: 'Development preview only; never licensed catalog photos',
    };
  }
  return {
    name: 'fretline-development-image-preview',
    resolveId(id) { if (id === PUBLIC_MODULE) return PRIVATE_MODULE; },
    load(id) {
      if (id === PRIVATE_MODULE) return `export default ${JSON.stringify(metadata)};`;
    },
    configureServer(server) {
      server.middlewares.use((request, response, next) => {
        const pathname = new URL(request.url ?? '/', 'http://localhost').pathname;
        if (!pathname.startsWith(ROUTE_PREFIX)) return next();
        response.setHeader('Cache-Control', 'no-store');
        response.setHeader('X-Robots-Tag', 'noindex, nofollow, noarchive');
        const bytes = files.get(pathname);
        if (!bytes) {
          response.statusCode = 404; response.end('Development illustration unavailable'); return;
        }
        if (!['GET', 'HEAD'].includes(request.method)) {
          response.statusCode = 405; response.setHeader('Allow', 'GET, HEAD'); response.end(); return;
        }
        response.setHeader('Content-Type', 'image/jpeg');
        response.setHeader('X-Content-Type-Options', 'nosniff');
        response.setHeader('Content-Length', bytes.length);
        response.end(request.method === 'HEAD' ? undefined : bytes);
      });
    },
  };
}
