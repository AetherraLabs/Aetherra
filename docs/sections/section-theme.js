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
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', setupCopy); else setupCopy();
})();
