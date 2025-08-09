/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'aetherra-green': '#00ff88',
                'aetherra-dark': '#0a0a0a',
            },
            fontFamily: {
                'jetbrains': ['JetBrains Mono', 'monospace'],
            }
        },
    },
    plugins: [],
}
