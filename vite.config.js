import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';
import { developmentImagePreview } from './scripts/vite/developmentImagePreview.mjs';

export default defineConfig(({ command, mode }) => ({
  plugins: [react(), developmentImagePreview({
    enabled: command === 'serve' && mode === 'pacifica-preview',
    root: fileURLToPath(new URL('.', import.meta.url)),
  })],
  server: {
    fs: { deny: ['.env', '.env.*', '*.{crt,pem}', '**/.git/**', '**/.local-preview/**'] },
  },
  resolve: {
    // ใช้ '@/...' แทน '../../...' เพื่อให้ import อ่านง่าย
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  build: {
    rollupOptions: {
      output: {
        // Cache catalog facts separately from the UI and framework as data grows.
        manualChunks(id) {
          if (id.includes('/node_modules/')) return 'vendor';
          if (id.includes('/src/data/catalog/') && id.endsWith('.json')) return 'guitar-catalog';
        },
      },
    },
  },
}));
