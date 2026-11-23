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

    function injectDocsNavigation() {
        const addMainOffset = (px) => {
            try {
                const main = document.querySelector('main');
                if (!main) return;
                const cur = parseInt(getComputedStyle(main).marginTop || '0', 10) || 0;
                if (cur < px) main.style.marginTop = (px) + 'px';
            } catch { }
        };
        // Documentation navigation is independent of the company homepage.
        try {
            if (document.querySelector('.sec-topnav')) return;
            const nav = document.createElement('nav');
            nav.className = 'sec-topnav';
            nav.innerHTML = [
                '<div class="nav-inner">',
                '  <a class="brand" href="/sections/hub.html">Aetherra</a>',
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

    function injectBreadcrumb() {
        try {
            if (document.querySelector('.sec-breadcrumb')) return;
            const main = document.querySelector('main');
            if (!main) return;
            const nav = document.createElement('div');
            nav.className = 'sec-breadcrumb';
            nav.innerHTML = '<a href="/sections/hub.html">Docs</a> / <span>Section</span>';
            // Place before the hero if present, else at top of main
            const hero = main.querySelector('.sec-hero');
            if (hero && hero.parentNode === main) main.insertBefore(nav, hero);
            else main.insertBefore(nav, main.firstChild);
        } catch { }
    }

    function fixLegalEntity() {
        try {
            const scopes = [document.querySelector('footer'), document.querySelector('.site-footer-cloned'), document.body];
            scopes.filter(Boolean).forEach(scope => {
                const walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT);
                const nodes = [];
                while (walker.nextNode()) nodes.push(walker.currentNode);
                nodes.forEach(n => { if (n.nodeValue && /Aetherra\s+Labs(?!,\s*LLC)/.test(n.nodeValue)) n.nodeValue = n.nodeValue.replace(/Aetherra\s+Labs(?!,\s*LLC)/g, 'Aetherra Labs, LLC'); });
            });
        } catch { }
    }

    function start() { injectDocsNavigation(); injectBreadcrumb(); setupCopy(); fixLegalEntity(); }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
