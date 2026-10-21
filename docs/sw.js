/* Prepkram service worker: keeps the app shell available offline.
   Only same-origin files are cached. Firebase, Google sign-in and fonts always go straight to the network. */
const CACHE = 'abhyashify-v11';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icon.svg', 'icon-192.png', 'icon-512.png', 'icon-maskable-512.png', 'apple-touch-icon.png', 'fonts/archivo-wdth.woff2', 'fonts/atkinson-400.woff2', 'fonts/atkinson-600.woff2', 'fonts/atkinson-700.woff2', 'fonts/devanagari-wght.woff2'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  // Pages: try the network first so updates arrive, fall back to the saved copy when offline.
  if (req.mode === 'navigate') {
    // Only the app itself is saved as the offline shell. The About and exam pages are ordinary web pages:
    // they must never overwrite the saved app, or going offline would open the wrong page.
    const scope = new URL(self.registration.scope);
    const isApp = url.pathname === scope.pathname || url.pathname === scope.pathname + 'index.html';
    e.respondWith(fetch(req).then(r => { if (isApp && r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put('index.html', copy)); } return r; })
      .catch(() => (isApp ? caches.match('index.html') : caches.match(req).then(hit => hit || caches.match('index.html')))));
    return;
  }
  // The offline voice engine is large and never changes between releases: saved copy first, no background refresh.
  if (url.pathname.includes('/voice/runtime/')) {
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => { if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); } return r; })));
    return;
  }
  // Everything else: saved copy first, refresh in the background.
  e.respondWith(caches.match(req).then(hit => {
    const net = fetch(req).then(r => { if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); } return r; }).catch(() => hit);
    return hit || net;
  }));
});

// Tapping a study-block banner brings the app forward (or opens it).
self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(cs => {
    for (const c of cs) { if ('focus' in c) return c.focus(); }
    return self.clients.openWindow('./');
  }));
});
