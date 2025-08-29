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

    async function injectSiteHeaderOrFallback() {
        const addMainOffset = (px) => {
            try {
                const main = document.querySelector('main');
                if (!main) return;
                const cur = parseInt(getComputedStyle(main).marginTop || '0', 10) || 0;
                if (cur < px) main.style.marginTop = (px) + 'px';
            } catch { }
        };
        try {
            // Try to clone the real site header from the homepage (same-origin)
            const iframe = document.createElement('iframe');
            iframe.src = '/';
            iframe.setAttribute('aria-hidden', 'true');
            Object.assign(iframe.style, { position: 'absolute', width: '0', height: '0', border: '0', padding: '0', margin: '0', clipPath: 'inset(50%)', overflow: 'hidden' });
            const onLoad = new Promise((resolve) => { iframe.onload = resolve; });
            document.body.appendChild(iframe);
            await onLoad;
            let cloned = null;
            try {
                const idoc = iframe.contentDocument;
                if (idoc) {
                    const cand = idoc.querySelector('header.site-header, header[role="banner"], header, nav[role="navigation"], nav.site-nav');
                    if (cand) {
                        cloned = cand.cloneNode(true);
                        cloned.classList.add('site-header-cloned');
                        // Mark links so any external mappers ignore them
                        cloned.querySelectorAll('a').forEach(a => a.setAttribute('data-link-fixed', '1'));
                        document.body.insertBefore(cloned, document.body.firstChild);
                        // Add spacing under header based on computed height
                        requestAnimationFrame(() => {
                            try {
                                const h = cloned.getBoundingClientRect().height || 56;
                                addMainOffset(Math.ceil(h + 8));
                            } catch { addMainOffset(56); }
                        });
                    }
                }
            } catch { /* cross-origin or other issue */ }
            try { document.body.removeChild(iframe); } catch { }
            if (cloned) return; // success
        } catch { /* fall through */ }
        // Fallback: simple themed top nav
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
            addMainOffset(24);
        } catch { }
    }

    function start() { injectSiteHeaderOrFallback(); setupCopy(); }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
