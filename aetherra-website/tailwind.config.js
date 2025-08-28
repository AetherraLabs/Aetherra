module.exports = {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}"
    ],
    theme: {
        extend: {
            colors: {
                bg: '#101014',
                surface: '#18181c',
                aether: '#7c3aed',
                soft: '#a3a3ff',
            },
            boxShadow: {
                glow: '0 0 16px 2px #7c3aed55',
            },
        },
    },
    plugins: [],
};
