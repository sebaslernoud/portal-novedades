/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// En Docker el backend se llama "backend"; corriendo fuera de Docker, usar API_URL=http://localhost:5000.
const API_URL = process.env.API_URL ?? 'http://backend:5000';
// Con Docker en Windows (y macOS) los cambios en la carpeta montada no generan eventos dentro del
// contenedor: sin polling, Vite no recarga. El compose lo activa; corriendo fuera de Docker no hace falta.
const USAR_POLLING = process.env.VITE_WATCH_POLLING === '1';

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: { '/api': API_URL },
    watch: USAR_POLLING ? { usePolling: true, interval: 300 } : undefined,
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/setupTests.ts'],
  },
});
