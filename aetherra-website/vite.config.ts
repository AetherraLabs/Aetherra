import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
    plugins: [react()],
    base: '/',
    build: {
        outDir: '../docs',
        // Important: do not wipe docs/ (it contains hand-written system docs)
        emptyOutDir: false,
        modulePreload: true
    }
})
