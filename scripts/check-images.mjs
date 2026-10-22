/** Audit registered photos and user-supplied project artwork without conflating their provenance. */
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { ROOT, readCatalog, readImageRights, readProjectArtwork } from './lib/catalog.mjs';
import { hasImageRights } from '../src/utils/imageRights.js';

const guitars = readCatalog();
const rights = readImageRights();
const artwork = readProjectArtwork();
const dir = path.join(ROOT, 'src/assets/guitars');
const imageExtension = /\.(webp|jpe?g|png|avif)$/i;
let errors = 0;
const approved = [];
const registered = new Set();
const fail = (message) => { errors++; console.log(`✗ ${message}`); };
const collections = [
  ...Object.entries(rights).map(([id, photos]) => ({ id, photos, kind: 'licensed-photo' })),
  ...Object.entries(artwork).map(([id, record]) => ({ id, photos: record.images, kind: 'project-artwork' })),
];
for (const { id, photos, kind } of collections) {
  if (!guitars.some((guitar) => guitar.id === id)) fail(`Unknown model ID: ${id}`);
  if (kind === 'project-artwork' && (artwork[id].guitarId !== id || artwork[id].usage !== 'user-requested-project-use')) fail(`Invalid project artwork registration: ${id}`);
  for (const photo of photos) {
    const validRecord = kind === 'project-artwork' || hasImageRights(photo, id);
    if (!validRecord) fail(`Missing or invalid photo record: ${id}/${photo.file}`);
    let validFiles = true;
    for (const file of [photo, ...(photo.variants ?? [])]) {
      const name = `${id}/${file.file}`;
      registered.add(name);
      const fullPath = path.resolve(dir, name);
      if (!fullPath.startsWith(dir + path.sep) || !imageExtension.test(file.file) || !fs.existsSync(fullPath)) { fail(`Missing/invalid file: ${name}`); validFiles = false; continue; }
      const hash = createHash('sha256').update(fs.readFileSync(fullPath)).digest('hex');
      if (hash !== file.sha256) { fail(`Image changed without updating review/hash: ${name}`); validFiles = false; }
      if (!(file.width > 0 && file.height > 0)) { fail(`Missing dimensions: ${name}`); validFiles = false; }
    }
    if (validRecord && validFiles) approved.push({ id, photo, kind });
  }
}
function walk(folder) {
  if (!fs.existsSync(folder)) return;
  for (const entry of fs.readdirSync(folder, { withFileTypes: true })) {
    const fullPath = path.join(folder, entry.name);
    if (entry.isDirectory()) walk(fullPath);
    else if (imageExtension.test(entry.name)) {
      const name = path.relative(dir, fullPath).split(path.sep).join('/');
      if (!registered.has(name)) fail(`Unregistered image is not published: ${name}`);
    }
  }
}
walk(dir);
const modelIds = new Set(approved.map((item) => item.id));
const missing = guitars.filter((guitar) => !modelIds.has(guitar.id));
const licensedPhotos = approved.filter(({ kind }) => kind === 'licensed-photo');
const projectImages = approved.filter(({ kind }) => kind === 'project-artwork');
console.log(`\nRights-documented photos: ${licensedPhotos.length}`);
console.log(`User-supplied project illustrations: ${projectImages.length}`);
console.log(`Models with registered images: ${modelIds.size}/${guitars.length}`);
console.log(`Responsive derivatives: ${approved.reduce((sum, { photo }) => sum + (photo.variants?.length ?? 0), 0)}`);
console.log(`Placeholders: ${missing.length} models (content gaps, not a failed file load)`);
for (const { id, photo } of licensedPhotos) console.log(`✓ ${id}: ${photo.author}, ${photo.license}; source and SHA-256 recorded`);
for (const { id, photo } of projectImages) console.log(`✓ ${id}/${photo.file}: user-supplied project artwork; original SHA-256 recorded`);
for (const guitar of missing) console.log(`- Missing: ${guitar.brand} ${guitar.name} (${guitar.id})`);
if (process.argv.includes('--write')) {
  fs.writeFileSync(path.join(ROOT, 'MISSING_IMAGES.md'), [
    '# Missing guitar images', '', `${missing.length} of ${guitars.length} models still use placeholders. ${licensedPhotos.length} licensed photographs and ${projectImages.length} user-supplied project illustrations are registered.`, '',
    '## Licensed photographs', '', ...licensedPhotos.map(({ id, photo }) => `- ${id}: ${photo.author} — [${photo.license}](${photo.licenseUrl}), [source](${photo.sourceUrl}). ${photo.changes}`), '',
    '## User-supplied project artwork', '', ...projectImages.map(({ id, photo }) => `- ${id}/${photo.file}: ${photo.label}. Supplied by the user for this project; AI editing retained in metadata, not represented as a verified product photograph or a verified license.`), '',
    '## Add an image', '', 'Licensed photographs use `src/data/catalog/imageRights.json`. User-supplied artwork requested for the project uses `src/data/catalog/projectArtwork.json`, with its original source, editing history, dimensions and SHA-256. The two records are separate; project use is not license verification. Place responsive versions in the model’s `responsive/` folder so they do not become duplicate gallery angles. Run `npm run images:check`; unregistered files remain unpublished.', '',
    '## Models still missing photos', '', '| Model | Stable ID |', '|---|---|', ...missing.map((guitar) => `| ${guitar.brand} ${guitar.name} | ${guitar.id} |`), '',
  ].join('\n'));
  console.log('Updated MISSING_IMAGES.md');
}
console.log(errors ? `${errors} image registration/file integrity problem(s).` : 'Image registration and file integrity checks passed.');
process.exitCode = errors ? 1 : 0;
