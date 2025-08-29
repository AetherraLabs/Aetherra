(function () {
    function setupCopy() {
        try {
            document.querySelectorAll('pre').forEach((pre) => {
                if (pre.querySelector('.copy-btn')) return;
                const btn = document.createElement('button');
                btn.className = 'copy-btn';
                btn.textContent = 'Copy';
                btn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    const code = pre.innerText || pre.textContent || '';
                    try { await navigator.clipboard.writeText(code); btn.textContent = 'Copied'; setTimeout(() => btn.textContent = 'Copy', 1200); } catch { btn.textContent = 'Fail'; setTimeout(() => btn.textContent = 'Copy', 1200); }
                });
                pre.appendChild(btn);
            });
        } catch { }
    }

    function injectTopNav() {
        try {
            if (document.querySelector('.sec-topnav')) return;
            const nav = document.createElement('nav');
            nav.className = 'sec-topnav';
            nav.innerHTML = [
                '<div class="nav-inner">',
                '  <a class="brand" href="/">Aetherra</a>',
                '  <div class="links">',
                '    <a href="/sections/developers.html">Developers</a>',
                '    <a href="/sections/runtime-cli.html">Runtime & CLI</a>',
                '    <a href="/sections/aether-language.html">.aether</a>',
                '    <a href="/sections/plugin-sdk.html">Plugin SDK</a>',
                '    <a href="/sections/ops-security.html">Ops & Security</a>',
                '    <a href="/sections/api-registry.html">API Registry</a>',
                '    <a href="/sections/tutorials-recipes.html">Tutorials</a>',
                '    <a href="/sections/researchers.html">Researchers</a>',
                '  </div>',
                '</div>'
            ].join('');
            document.body.insertBefore(nav, document.body.firstChild);
            // Add a small offset so content isn't tight against nav
            const main = document.querySelector('main');
            if (main) {
                const cur = parseInt(getComputedStyle(main).marginTop || '0', 10) || 0;
                if (cur < 24) main.style.marginTop = (cur + 24) + 'px';
            }
        } catch { }
    }

    function start() { injectTopNav(); setupCopy(); }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
