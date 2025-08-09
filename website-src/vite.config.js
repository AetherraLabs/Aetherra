import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
    plugins: [react()],
    build: {
        outDir: '../docs',
        emptyOutDir: true,
        rollupOptions: {
            output: {
                // Ensure consistent file naming for easier debugging
                entryFileNames: 'assets/index-[hash].js',
                chunkFileNames: 'assets/[name]-[hash].js',
                assetFileNames: 'assets/[name]-[hash].[ext]'
            }
        }
    },
    server: {
        port: 3000,
        host: true,
        open: true
    },
    // For local development and GitHub Pages deployment
    base: './'
})
