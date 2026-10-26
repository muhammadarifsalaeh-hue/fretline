import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';
import { developmentImagePreview } from './scripts/vite/developmentImagePreview.mjs';
import { practiceSceneModule } from './scripts/vite/practiceSceneModule.mjs';
import { yamahaImportPreview } from './scripts/vite/yamahaImportPreview.mjs';

export default defineConfig(({ command, mode }) => ({
  plugins: [react(), practiceSceneModule(), developmentImagePreview({
    enabled: command === 'serve' && mode === 'pacifica-preview',
    root: fileURLToPath(new URL('.', import.meta.url)),
  }), yamahaImportPreview({
    enabled: command === 'serve' && mode === 'yamaha-preview',
    root: fileURLToPath(new URL('.', import.meta.url)),
  })],
  server: {
    fs: { deny: ['.env', '.env.*', '*.{crt,pem}', '**/.git/**', '**/.local-preview/**', '**/.yamaha-intake/**', '**/docs/yamaha-import/preview-assets/**'] },
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
          // Keep the WebGL engine out of the shared framework/Home bundle.
          if (id.includes('/node_modules/three/') || id.includes('/src/features/practice/scene/')) return 'practice-three';
          if (id.includes('/node_modules/')) return 'vendor';
          if (id.includes('/src/data/catalog/') && id.endsWith('.json')) return 'guitar-catalog';
        },
      },
    },
  },
}));
