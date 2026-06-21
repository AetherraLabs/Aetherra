import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
    plugins: [react()],
    server: {
        port: 3000,
        host: true,
        proxy: {
            // REST API calls  →  FastAPI at 8888
            '/api': {
                target: 'http://localhost:8888',
                changeOrigin: true,
            },
            // WebSocket  →  FastAPI at 8888
            '/ws': {
                target: 'ws://localhost:8888',
                ws: true,
                changeOrigin: true,
            },
        },
    },
})
