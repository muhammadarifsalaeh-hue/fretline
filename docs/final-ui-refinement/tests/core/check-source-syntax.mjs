/** Parse source without emitting build artifacts or changing original checks. */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { transformSync } from 'esbuild';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../..');
const walk = (folder) => fs.readdirSync(folder, { withFileTypes: true }).flatMap((entry) => {
  const file = path.join(folder, entry.name);
  return entry.isDirectory() ? walk(file) : [file];
});
const files = [...walk(path.join(ROOT, 'src')), ...walk(path.join(ROOT, 'scripts')),
  ...['vite.config.js', 'tailwind.config.js', 'postcss.config.js'].map((file) => path.join(ROOT, file))]
  .filter((file) => /\.(?:jsx?|mjs)$/.test(file)).sort();
for (const file of files) {
  transformSync(fs.readFileSync(file, 'utf8'), {
    sourcefile: path.relative(ROOT, file), loader: file.endsWith('.jsx') ? 'jsx' : 'js',
    logLevel: 'silent',
  });
}
console.log(`PASS esbuild syntax parsing: ${files.length} JavaScript/JSX modules`);
