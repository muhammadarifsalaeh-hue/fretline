/**
 * ตรวจข้อมูลกีตาร์ทั้งหมด (18 รุ่นตัวอย่าง + extraGuitars.json) และรายงานความคืบหน้าสู่เป้าหมาย
 *   npm run catalog:check                 # เป้าหมายเริ่มต้น 200 รุ่น
 *   npm run catalog:check -- --target=200 --strict   # --strict: ไม่ถึงเป้าหมายถือว่าไม่ผ่าน
 * ออกด้วยรหัส 1 เมื่อมีข้อมูลผิดรูปแบบหรือรุ่นซ้ำ
 */
import { TARGET_DEFAULT, findDuplicates, photoStats, readExtras, readSampleGuitars, validateGuitar } from './lib/catalog.mjs';

const arg = (name) => process.argv.find((a) => a.startsWith(`--${name}=`))?.split('=')[1];
const target = Number(arg('target') ?? TARGET_DEFAULT);
const strict = process.argv.includes('--strict');

const samples = readSampleGuitars();
const extras = readExtras();
const all = [...samples, ...extras];

let errors = 0;
extras.forEach((g, i) => {
  const errs = validateGuitar(g);
  if (errs.length) {
    errors += errs.length;
    console.log(`✗ extraGuitars.json #${i + 1} (${g.id ?? 'no id'})`);
    errs.forEach((m) => console.log(`    - ${m}`));
  }
});
findDuplicates(all).forEach((m) => {
  errors++;
  console.log(`✗ ${m}`);
});

const verified = extras.filter((g) => g.status === 'verified').length;
const partial = extras.filter((g) => g.status === 'partial').length;
const noPrice = extras.filter((g) => g.price == null).length;
const photos = photoStats(all.map((g) => g.id));
const gap = Math.max(0, target - all.length);

console.log('\n=== Catalog report ===');
console.log(`Total models        : ${all.length} / ${target}   (${gap} to go)`);
console.log(`  built-in samples  : ${samples.length}   (unverified sample data)`);
console.log(`  imported          : ${extras.length}   (verified: ${verified}, partial: ${partial}, sample: ${extras.length - verified - partial})`);
console.log(`Fully verified      : ${verified}`);
console.log(`Partially verified  : ${partial}   (source-backed, some fields unknown)`);
console.log(`Price on request    : ${noPrice}`);
console.log(`Real photos         : ${photos.withPhotos} models`);
console.log(`Placeholder (no photo): ${photos.placeholders} models`);
console.log(errors ? `\n${errors} problem(s) found.\n` : '\nNo data problems found.\n');

process.exit(errors || (strict && gap > 0) ? 1 : 0);
