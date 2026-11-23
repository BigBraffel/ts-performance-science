/* Offline-Unterstützung. Online: immer zuerst aus dem Netz (neuester Stand) und die Kopie im Speicher erneuern.
   Offline: aus dem Speicher. „Offline speichern“ lädt alle Dateien auf einmal in den Speicher. */
const CACHE = "fs-v8";
self.addEventListener("install", (e) => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", "logo-ts.png", "data/mythen.json"]))); self.skipWaiting(); });
self.addEventListener("activate", (e) => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))); self.clients.claim(); });
self.addEventListener("fetch", (e) => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;
  e.respondWith(fetch(e.request, { cache: "no-cache" }).then(r => { if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); } return r; })
    .catch(() => caches.match(e.request, { ignoreSearch: true }).then(r => r || caches.match("index.html"))));
});
self.addEventListener("message", (e) => {
  if (e.data?.type !== "alles-speichern") return;
  e.waitUntil(caches.open(CACHE).then(async c => {
    let ok = 0;
    for (const url of e.data.urls) { try { const r = await fetch(url, { cache: "no-cache" }); if (r.ok) { await c.put(url, r); ok++; } } catch (err) {} }
    e.source.postMessage({ type: "gespeichert", ok, total: e.data.urls.length });
  }));
});
