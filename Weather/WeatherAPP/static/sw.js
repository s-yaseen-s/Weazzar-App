const CACHE = 'weazzar-v1';

const PRECACHE = [
    '/',
    '/about',
    '/contact',
    '/privacy',
    '/static/style.css',
    '/static/manifest.json',
    '/static/icons/icon.svg',
];

// Install: pre-cache static shell
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE).then(cache => cache.addAll(PRECACHE))
    );
    self.skipWaiting();
});

// Activate: delete stale caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// Fetch strategy
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    // Always go to network for API calls and weather POST
    if (url.pathname.startsWith('/api/') || url.pathname === '/weather') {
        event.respondWith(fetch(event.request));
        return;
    }

    // Cache-first for static assets
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(event.request).then(cached => {
                if (cached) return cached;
                return fetch(event.request).then(res => {
                    const clone = res.clone();
                    caches.open(CACHE).then(c => c.put(event.request, clone));
                    return res;
                });
            })
        );
        return;
    }

    // Network-first for pages, fall back to cache when offline
    event.respondWith(
        fetch(event.request)
            .then(res => {
                const clone = res.clone();
                caches.open(CACHE).then(c => c.put(event.request, clone));
                return res;
            })
            .catch(() => caches.match(event.request))
    );
});
