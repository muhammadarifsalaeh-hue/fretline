/** Validate the effective catalog, including reviewed overrides for legacy IDs. */
import { TARGET_DEFAULT, findDuplicates, photoStats, readArchive, readPolicy, readPhase7, readCatalog, readExtras, readReviewed, readSampleGuitars, validateGuitar } from './lib/catalog.mjs';

const arg = (name) => process.argv.find((value) => value.startsWith(`--${name}=`))?.split('=')[1];
const target = Number(arg('target') ?? TARGET_DEFAULT);
const strict = process.argv.includes('--strict');
const legacy = readSampleGuitars();
const extras = readExtras();
const reviewed = readReviewed();
const archive = readArchive();
const policy = readPolicy();
const added = readPhase7();
const all = readCatalog();
let errors = 0;
for (const guitar of all) {
  const problems = validateGuitar(guitar);
  for (const problem of problems) { errors++; console.log(`✗ ${guitar.id}: ${problem}`); }
}
for (const message of findDuplicates([...all, ...archive])) { errors++; console.log(`✗ ${message}`); }
for (const id of Object.keys(reviewed)) if (![...all, ...archive].some((guitar) => guitar.id === id)) { errors++; console.log(`✗ Reviewed record has no catalog/archive ID: ${id}`); }
// Exact counts are a release requirement, not an optional minimum threshold.
const brandCounts = all.reduce((counts, guitar) => counts.set(guitar.brand, (counts.get(guitar.brand) ?? 0) + 1), new Map());
if (all.length !== policy.target) { errors++; console.log(`✗ Expected exactly ${policy.target} active models; found ${all.length}`); }
if (brandCounts.size !== policy.brands.length) { errors++; console.log(`✗ Expected ${policy.brands.length} active brands; found ${brandCounts.size}`); }
for (const brand of policy.brands) if (brandCounts.get(brand) !== policy.modelsPerBrand) { errors++; console.log(`✗ ${brand}: expected ${policy.modelsPerBrand}, found ${brandCounts.get(brand) ?? 0}`); }
for (const guitar of all) if (policy.archivedIds.includes(guitar.id)) { errors++; console.log(`✗ Archive leaked into active catalog: ${guitar.id}`); }
for (const id of policy.archivedIds) if (!archive.some((guitar) => guitar.id === id && guitar.source?.url && guitar.previousPublishedSnapshot)) { errors++; console.log(`✗ Missing complete archive backup: ${id}`); }
const verified = all.filter((guitar) => guitar.status === 'verified').length;
const partial = all.filter((guitar) => guitar.status === 'partial').length;
const photos = photoStats(all.map((guitar) => guitar.id));
const gap = Math.max(0, target - all.length);
console.log('\n=== Effective catalog report ===');
console.log(`Total models        : ${all.length} / ${target} (${gap} to go)`);
console.log(`Brands              : ${new Set(all.map((guitar) => guitar.brand)).size}`);
console.log(`Legacy stable IDs   : ${legacy.length} (${legacy.filter((guitar) => reviewed[guitar.id]).length} reviewed overrides)`);
console.log(`Imported stable IDs : ${extras.length}`);
console.log(`Phase 7 additions   : ${added.length}`);
console.log(`Archived (not counted): ${archive.length}`);
for (const [brand, total] of [...brandCounts].sort(([a], [b]) => a.localeCompare(b))) console.log(`  ${brand.padEnd(12)}: ${total} / ${policy.modelsPerBrand}`);
console.log(`Sample              : ${all.length - verified - partial}`);
console.log(`Fully verified      : ${verified}`);
console.log(`Partially verified  : ${partial}`);
console.log(`Price on request    : ${all.filter((guitar) => guitar.price == null).length}`);
console.log(`Verified reviews    : ${all.filter((guitar) => guitar.rating?.verified).length}`);
console.log(`Models with images  : ${photos.withPhotos}`);
console.log(`Placeholder models  : ${photos.placeholders}`);
console.log(errors ? `\n${errors} problem(s) found.` : '\nNo data problems found. Unknown fields remain unknown.');
process.exit(errors || (strict && gap > 0) ? 1 : 0);
