/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// En Docker el backend se llama "backend"; corriendo fuera de Docker, usar API_URL=http://localhost:5000.
const API_URL = process.env.API_URL ?? 'http://backend:5000';

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: { '/api': API_URL },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/setupTests.ts'],
  },
});
