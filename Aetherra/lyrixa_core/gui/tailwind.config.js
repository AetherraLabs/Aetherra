/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            animation: {
                'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            fontFamily: {
                'mono': ['Courier New', 'monospace'],
            },
            colors: {
                'aetherra-green': '#00ff88',
                'aetherra-cyan': '#00ffff',
            }
        },
    },
    plugins: [],
}
