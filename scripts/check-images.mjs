/** Audit model photos, rights, responsive derivatives and content hashes. */
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { ROOT, readCatalog, readImageRights } from './lib/catalog.mjs';
import { hasImageRights } from '../src/utils/imageRights.js';

const guitars = readCatalog();
const rights = readImageRights();
const dir = path.join(ROOT, 'src/assets/guitars');
const imageExtension = /\.(webp|jpe?g|png|avif)$/i;
let errors = 0;
const approved = [];
const registered = new Set();
const fail = (message) => { errors++; console.log(`✗ ${message}`); };
for (const [id, photos] of Object.entries(rights)) {
  if (!guitars.some((guitar) => guitar.id === id)) fail(`Unknown model ID: ${id}`);
  for (const photo of photos) {
    const validRights = hasImageRights(photo, id);
    if (!validRights) fail(`Missing or invalid rights/model-match record: ${id}/${photo.file}`);
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
    if (validRights && validFiles) approved.push({ id, photo });
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
console.log(`\nRights-documented photos: ${approved.length}; models: ${modelIds.size}/${guitars.length}`);
console.log(`Responsive derivatives: ${approved.reduce((sum, { photo }) => sum + (photo.variants?.length ?? 0), 0)}`);
console.log(`Placeholders: ${missing.length} models (content gaps, not a failed file load)`);
for (const { id, photo } of approved) console.log(`✓ ${id}: ${photo.author}, ${photo.license}; source and SHA-256 recorded`);
for (const guitar of missing) console.log(`- Missing: ${guitar.brand} ${guitar.name} (${guitar.id})`);
if (process.argv.includes('--write')) {
  fs.writeFileSync(path.join(ROOT, 'MISSING_IMAGES.md'), [
    '# Missing guitar photos', '', `${missing.length} of ${guitars.length} models still require rights-documented, matching photos. Existing placeholders remain in use.`, '',
    '## Accepted images', '', ...approved.map(({ id, photo }) => `- ${id}: ${photo.author} — [${photo.license}](${photo.licenseUrl}), [source](${photo.sourceUrl}). ${photo.changes}`), '',
    '## Add a photo', '', 'Use a photo of the correct model/variant with established reuse rights. Record author, source, license URL, check date, model-match note, transformations, file dimensions and SHA-256 in `src/data/catalog/imageRights.json`. Place responsive versions in the model’s `responsive/` folder so they do not become duplicate gallery angles. Run `npm run images:check`; unregistered files remain unpublished.', '',
    '## Models still missing photos', '', '| Model | Stable ID |', '|---|---|', ...missing.map((guitar) => `| ${guitar.brand} ${guitar.name} | ${guitar.id} |`), '',
  ].join('\n'));
  console.log('Updated MISSING_IMAGES.md');
}
console.log(errors ? `${errors} rights/file integrity problem(s).` : 'Rights records and file integrity checks passed.');
process.exitCode = errors ? 1 : 0;
