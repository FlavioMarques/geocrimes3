self.addEventListener('install', event => {
    event.waitUntil(
        caches.open('static-cache-v1').then(cache => {
            return cache.addAll([
                '/',
                '/app.py',
                '/index.html',
                '/manifest.json',
                '/assets/icon-192x192.png',
                '/assets/icon-512x512.png',
                'https://cdn.jsdelivr.net/npm/@stlite/mountable@0.34.0/build/stlite.css',
                'https://cdn.jsdelivr.net/npm/@stlite/mountable@0.34.0/build/stlite.js'
            ]);
        })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        })
    );
});
