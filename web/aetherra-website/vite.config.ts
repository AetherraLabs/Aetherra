import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    base: '/Aetherra/', // GitHub Pages base path for repository
    build: {
        outDir: '../../docs',
        emptyOutDir: true
    }
})
