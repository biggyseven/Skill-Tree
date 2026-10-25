import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
  build: {
    outDir: resolve(__dirname, '../../static/lab'),
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'main.js',
        chunkFileNames: 'chunks/[name]-[hash].js',
        assetFileNames: (info) => {
          if (info.name === 'style.css' || info.name?.endsWith('.css')) return 'main.css';
          return 'assets/[name]-[hash][extname]';
        },
      },
    },
  },
});
