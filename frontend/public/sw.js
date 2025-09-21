/**
 * Service Worker Simplificado - Sistema POS Sabrositas
 * Versión simplificada para desarrollo
 */

const CACHE_NAME = 'pos-sabrositas-dev-v1';

// Instalación del Service Worker
self.addEventListener('install', (event) => {
  console.log('[SW] Service Worker instalado');
  self.skipWaiting();
});

// Activación del Service Worker
self.addEventListener('activate', (event) => {
  console.log('[SW] Service Worker activado');
  event.waitUntil(self.clients.claim());
});

// Interceptar peticiones de red
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Solo interceptar peticiones del mismo origen
  if (url.origin !== location.origin) {
    return;
  }
  
  // Para desarrollo, simplemente pasar las peticiones sin cache
  if (request.method === 'GET') {
    event.respondWith(
      fetch(request).catch(() => {
        console.log('[SW] Network failed for', request.url);
        // Retornar una respuesta básica para evitar errores
        return new Response('Network error', {
          status: 503,
          statusText: 'Service Unavailable',
          headers: new Headers({
            'Content-Type': 'text/plain'
          })
        });
      })
    );
  }
});

// Manejar mensajes del cliente
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
