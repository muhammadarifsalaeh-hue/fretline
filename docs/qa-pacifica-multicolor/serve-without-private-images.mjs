/** Same application/config, with an empty private image directory like Codespaces. */
import { createServer } from 'vite';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import config from '../../vite.config.js';
import { developmentImagePreview } from '../../scripts/vite/developmentImagePreview.mjs';

const root = fileURLToPath(new URL('../..', import.meta.url));
const empty = fs.mkdtempSync(path.join(os.tmpdir(), 'fretline-browser-intake-'));
const options = config({ command: 'serve', mode: 'pacifica-preview' });
const server = await createServer({ ...options, configFile: false, root, mode: 'pacifica-preview',
  plugins: [...options.plugins.filter((p) => p.name !== 'fretline-development-image-preview'), developmentImagePreview({ enabled: true, root: empty })],
  server: { ...options.server, host: '127.0.0.1', port: 5174, strictPort: true },
});
await server.listen();
console.log('Empty-private-images QA server ready at http://127.0.0.1:5174');
for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, async () => {
  await server.close(); fs.rmdirSync(empty); process.exit(0);
});
