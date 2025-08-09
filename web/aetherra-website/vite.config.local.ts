import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Local development configuration
// Use this for local testing with relative paths
export default defineConfig({
    plugins: [react()],
    base: './', // Relative base for local development
    build: {
        outDir: '../docs',
        emptyOutDir: true
    }
})
