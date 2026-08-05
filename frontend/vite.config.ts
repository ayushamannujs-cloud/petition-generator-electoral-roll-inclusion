import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Bind 0.0.0.0 so other devices on the LAN can reach the dev server.
    host: true,
    // Keep /api relative in dev too, so the same code path works in dev and prod.
    proxy: { "/api": "http://localhost:2026" },
  },
})
