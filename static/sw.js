const CACHE = 'quina-ia-v1';

const STATIC = [
    '/',
    '/static/style.css',
    '/static/manifest.json',
    '/static/icons/icon-192.svg',
    '/static/icons/icon-512.svg',
    '/manifest.json'
];

// ── Instalar: pre-cache dos assets estáticos ─────────────────────
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE).then(cache => cache.addAll(STATIC))
    );
    self.skipWaiting();
});

// ── Ativar: limpar caches antigos ────────────────────────────────
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// ── Fetch ────────────────────────────────────────────────────────
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // API: network-first, fallback offline JSON
    if (url.pathname === '/gerar' || url.pathname === '/historico') {
        event.respondWith(
            fetch(request).catch(() =>
                new Response(
                    url.pathname === '/gerar'
                        ? JSON.stringify({ erro: 'Sem conexão. Conecte-se à internet.' })
                        : JSON.stringify([]),
                    { headers: { 'Content-Type': 'application/json' } }
                )
            )
        );
        return;
    }

    // Static: cache-first, depois network
    event.respondWith(
        caches.match(request).then(cached => {
            if (cached) return cached;
            return fetch(request).then(response => {
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE).then(c => c.put(request, clone));
                }
                return response;
            });
        })
    );
});
