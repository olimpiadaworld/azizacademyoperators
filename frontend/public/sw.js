const CACHE_VERSION = 'aziz-academy-crm-v13'
const APP_SHELL = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/favicon.svg',
  '/aziz-academy-blue-a-logo.png',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/icons/icon-maskable-512.png',
  '/icons/apple-touch-icon.png',
]

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_VERSION)

    // Bitta fayl vaqtincha ochilmasa ham service worker butunlay yiqilmasin.
    await Promise.allSettled(
      APP_SHELL.map(async (url) => {
        const response = await fetch(url, { cache: 'reload' })
        if (response.ok) await cache.put(url, response)
      }),
    )

    await self.skipWaiting()
  })())
})

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys()
    await Promise.all(
      keys
        .filter((key) => key !== CACHE_VERSION)
        .map((key) => caches.delete(key)),
    )
    await self.clients.claim()
  })())
})

self.addEventListener('fetch', (event) => {
  const request = event.request
  if (request.method !== 'GET') return

  const url = new URL(request.url)
  if (url.origin !== self.location.origin) return
  if (url.pathname.startsWith('/api/')) return

  if (request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const response = await fetch(request)
        if (response.ok) {
          const cache = await caches.open(CACHE_VERSION)
          await cache.put('/index.html', response.clone())
        }
        return response
      } catch {
        return await caches.match('/index.html')
          || await caches.match('/')
          || new Response('Internet aloqasi mavjud emas.', {
            status: 503,
            headers: { 'Content-Type': 'text/plain; charset=utf-8' },
          })
      }
    })())
    return
  }

  event.respondWith((async () => {
    const cached = await caches.match(request)

    try {
      const response = await fetch(request)
      if (response.ok) {
        const cache = await caches.open(CACHE_VERSION)
        await cache.put(request, response.clone())
      }
      return response
    } catch {
      return cached || new Response('', { status: 504 })
    }
  })())
})
