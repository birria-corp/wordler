// Wordler service worker.
// Network-first: the app shell (index.html), version.json, past-answers.json.
// Cache-first: icons and other static assets.
const VERSION = 'v1.5';
const CACHE = `wordler-${VERSION}`;
const PRECACHE = ['./', './index.html', './manifest.json', './version.json',
  './icon-192.png', './icon-512.png', './icon-maskable-512.png'];
const NETWORK_FIRST = /(\/|\/index\.html|\/version\.json|\/past-answers\.json)$/;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;

  // Cache key ignores query strings so cache-busting params don't pile up entries.
  const key = url.origin + url.pathname;

  if (req.mode === 'navigate' || NETWORK_FIRST.test(url.pathname)) {
    e.respondWith(
      fetch(req)
        .then(res => {
          if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(key, copy)); }
          return res;
        })
        .catch(() => caches.match(key).then(r => r || caches.match('./index.html')))
    );
    return;
  }

  e.respondWith(
    caches.match(key).then(cached => cached || fetch(req).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(key, copy)); }
      return res;
    }))
  );
});
