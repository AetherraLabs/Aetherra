// Enhanced Aetherra Project Service Worker
// Provides offline support and caching for the AI-native development environment website

const CACHE_NAME = 'aetherra-v2.0.0';
const STATIC_CACHE = 'aetherra-static-v2.0.0';
const DYNAMIC_CACHE = 'aetherra-dynamic-v2.0.0';

// Core files to cache for offline functionality
const CORE_FILES = [
    '/',
    '/index-enhanced.html',
    '/styles-enhanced.css',
    '/script-enhanced.js',
    '/manifest.json',
    '/favicon.svg',
    '/favicon.ico'
];

// Additional assets to cache
const STATIC_ASSETS = [
    // External fonts
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap'
];

// Network-first resources
const NETWORK_FIRST = [
    'https://api.github.com/',
    'https://fonts.googleapis.com/',
    'https://fonts.gstatic.com/'
];

// Cache-first resources
const CACHE_FIRST = [
    '/favicon.svg',
    '/favicon.ico',
    '/manifest.json'
];

// =============================================================================
// SERVICE WORKER INSTALLATION
// =============================================================================

self.addEventListener('install', event => {
    console.log('🚀 Aetherra Service Worker installing...');

    event.waitUntil(
        caches.open(STATIC_CACHE).then(cache => {
            console.log('[DISC] Caching core files...');
            return cache.addAll(CORE_FILES);
        }).then(() => {
            console.log('✅ Aetherra Service Worker installed successfully');
            return self.skipWaiting();
        }).catch(err => {
            console.error('❌ Service Worker installation failed:', err);
        })
    );
});

// =============================================================================
// SERVICE WORKER ACTIVATION
// =============================================================================

self.addEventListener('activate', event => {
    console.log('🔄 Aetherra Service Worker activating...');

    event.waitUntil(
        Promise.all([
            // Clean up old caches
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log(`🗑️ Deleting old cache: ${cacheName}`);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),

            // Take control of all clients
            self.clients.claim()
        ]).then(() => {
            console.log('✅ Aetherra Service Worker activated');
        })
    );
});

// =============================================================================
// FETCH EVENT HANDLING
// =============================================================================

self.addEventListener('fetch', event => {
    const { request } = event;

    // Skip non-HTTP requests
    if (!request.url.startsWith('http')) {
        return;
    }

    // Skip POST requests
    if (request.method !== 'GET') {
        return;
    }

    // Apply different caching strategies based on resource type
    if (NETWORK_FIRST.some(pattern => request.url.includes(pattern))) {
        event.respondWith(networkFirst(request));
    } else if (CACHE_FIRST.some(pattern => request.url.includes(pattern))) {
        event.respondWith(cacheFirst(request));
    } else if (request.destination === 'document') {
        event.respondWith(documentStrategy(request));
    } else {
        event.respondWith(genericStrategy(request));
    }
});

// =============================================================================
// CACHING STRATEGIES
// =============================================================================

// Network first strategy (for dynamic content)
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);

        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);
        return cachedResponse || new Response('Offline', { status: 503 });
    }
}

// Cache first strategy (for static assets)
async function cacheFirst(request) {
    const cachedResponse = await caches.match(request);

    if (cachedResponse) {
        return cachedResponse;
    }

    try {
        const networkResponse = await fetch(request);

        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        throw error;
    }
}

// Document strategy (for HTML pages)
async function documentStrategy(request) {
    try {
        const networkResponse = await fetch(request);

        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
            return networkResponse;
        }
    } catch (error) {
        // Network failed, try cache
    }

    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }

    // Fallback to enhanced index
    return caches.match('/index-enhanced.html') ||
        caches.match('/') ||
        new Response(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Aetherra - Offline</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                            background: linear-gradient(135deg, #0891b2, #8b5cf6);
                            color: white;
                            text-align: center;
                            padding: 2rem;
                            margin: 0;
                            min-height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            flex-direction: column;
                        }
                        .logo { font-size: 3rem; margin-bottom: 1rem; }
                        .title { font-size: 2rem; margin-bottom: 1rem; }
                        .message { font-size: 1.2rem; opacity: 0.9; }
                    </style>
                </head>
                <body>
                    <div class="logo">⚡</div>
                    <div class="title">Aetherra Project</div>
                    <div class="message">You're currently offline. Please check your internet connection.</div>
                </body>
                </html>
            `, {
            headers: { 'Content-Type': 'text/html' }
        });
}

// Generic strategy (for other resources)
async function genericStrategy(request) {
    try {
        const networkResponse = await fetch(request);

        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);
        return cachedResponse || new Response('Resource unavailable offline', { status: 503 });
    }
}

console.log('🚀 Aetherra Service Worker loaded - Ready for AI-native development!');
