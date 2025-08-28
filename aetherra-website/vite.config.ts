import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/',
  build: {
    outDir: '../docs',
  // Important: do not wipe docs/ (it contains hand-written system docs)
  emptyOutDir: false
  }
})
