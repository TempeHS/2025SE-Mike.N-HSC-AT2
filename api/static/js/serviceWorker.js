const assets = [
  "/",
  "static/css/style.css",
  "static/css/bootstrap.min.css",
  "static/css/prism.css",
  "static/css/prism-okaidia.min.css",
  "static/js/bootstrap.bundle.min.js",
  "static/js/prism.min.js",
  "static/js/prism-javascript.min.js",
  "static/js/prism-python.min.js",
  "static/js/app.js",
  "static/js/prism.js",
  "static/js/textarea_tabs.js",
  "static/images/logo.png",
  "static/images/favicon.jpg",
  "static/icons/icon-128x128.png",
  "static/icons/icon-192x192.png",
  "static/icons/icon-384x384.png",
  "static/icons/icon-512x512.png",
  "static/icons/desktop_screenshot.png",
  "static/icons/mobile_screenshot.png",
  "static/manifest.json",
];

const CATALOGUE_ASSETS = "catalogue-assets";

self.addEventListener("install", (installEvt) => {
  installEvt.waitUntil(
    caches
      .open(CATALOGUE_ASSETS)
      .then((cache) => {
        console.log("Caching assets");
        return cache.addAll(assets);
      })
      .then(self.skipWaiting())
      .catch((e) => {
        console.log(e);
      })
  );
});

self.addEventListener("activate", (evt) => {
  evt.waitUntil(
    caches
      .keys()
      .then((keyList) => {
        return Promise.all(
          keyList.map((key) => {
            if (key !== CATALOGUE_ASSETS) {
              console.log("Removing old cache:", key);
              return caches.delete(key);
            }
          })
        );
      })
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (evt) => {
  evt.respondWith(
    fetch(evt.request).catch(() => {
      return caches.open(CATALOGUE_ASSETS).then((cache) => {
        return cache.match(evt.request);
      });
    })
  );
});

const urlsToCache = [
  "/get_api_key",
  "/static/js/get_api_key.js",
  "/static/icons/icon-192x192.png",
  "/static/icons/icon-512x512.png",
  "/static/css/styles.css",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
