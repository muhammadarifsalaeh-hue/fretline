import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [react()],
  resolve: {
    // ใช้ '@/...' แทน '../../...' เพื่อให้ import อ่านง่าย
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
});
