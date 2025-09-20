/**
 * Service Worker - Sistema POS Sabrositas
 * Funcionalidad offline, cache de recursos y sincronización
 */

const CACHE_NAME = 'pos-sabrositas-v1.0.0';
const STATIC_CACHE = 'static-v1';
const DATA_CACHE = 'data-v1';
const OFFLINE_URL = '/offline.html';

// Recursos estáticos para cachear
const STATIC_FILES = [
  '/',
  '/login',
  '/analytics',
  '/sales',
  '/products',
  '/offline.html',
  '/manifest.json',
  // CSS y JS se cachearán automáticamente por Vite
];

// URLs de API que se pueden cachear
const CACHEABLE_APIS = [
  '/api/v1/products',
  '/api/v1/analytics/dashboard',
  '/api/v1/health'
];

// Instalación del Service Worker
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker');
  
  event.waitUntil(
    Promise.all([
      // Cache de archivos estáticos
      caches.open(STATIC_CACHE).then((cache) => {
        console.log('[SW] Caching static files');
        return cache.addAll(STATIC_FILES);
      }),
      
      // Cache de datos iniciales
      caches.open(DATA_CACHE).then((cache) => {
        console.log('[SW] Preparing data cache');
        return cache.put('/offline-indicator', new Response('offline'));
      })
    ])
  );
  
  // Activar inmediatamente
  self.skipWaiting();
});

// Activación del Service Worker
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker');
  
  event.waitUntil(
    Promise.all([
      // Limpiar caches antiguos
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DATA_CACHE) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      
      // Tomar control de todas las pestañas
      self.clients.claim()
    ])
  );
});

// Interceptar peticiones de red
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Solo interceptar peticiones del mismo origen
  if (url.origin !== location.origin) {
    return;
  }
  
  // Estrategias de cache según el tipo de recurso
  if (request.method === 'GET') {
    if (url.pathname.startsWith('/api/')) {
      // APIs - Network First con fallback a cache
      event.respondWith(handleApiRequest(request));
    } else if (request.destination === 'document') {
      // HTML - Network First con fallback a cache y offline
      event.respondWith(handleDocumentRequest(request));
    } else {
      // Recursos estáticos - Cache First
      event.respondWith(handleStaticRequest(request));
    }
  } else if (request.method === 'POST' && url.pathname.startsWith('/api/')) {
    // POST APIs - Intentar network, si falla guardar para sync
    event.respondWith(handlePostRequest(request));
  }
});

// Manejo de peticiones a APIs
async function handleApiRequest(request) {
  const url = new URL(request.url);
  
  try {
    // Intentar petición de red primero
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Si es una API cacheable, guardar en cache
      if (CACHEABLE_APIS.some(api => url.pathname.startsWith(api))) {
        const cache = await caches.open(DATA_CACHE);
        cache.put(request, networkResponse.clone());
      }
      return networkResponse;
    }
    
    throw new Error('Network response not ok');
  } catch (error) {
    console.log('[SW] Network failed for API, trying cache:', url.pathname);
    
    // Buscar en cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      // Agregar header para indicar que viene del cache
      const response = cachedResponse.clone();
      response.headers.set('X-Served-By', 'sw-cache');
      return response;
    }
    
    // Si no hay cache, devolver error estructurado
    return new Response(
      JSON.stringify({
        error: 'Sin conexión',
        message: 'Los datos no están disponibles offline',
        offline: true
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: {
          'Content-Type': 'application/json',
          'X-Served-By': 'sw-offline'
        }
      }
    );
  }
}

// Manejo de peticiones de documentos HTML
async function handleDocumentRequest(request) {
  try {
    // Intentar red primero
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cachear la respuesta
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    
    throw new Error('Network response not ok');
  } catch (error) {
    console.log('[SW] Network failed for document, trying cache');
    
    // Buscar en cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Página offline como último recurso
    return caches.match(OFFLINE_URL);
  }
}

// Manejo de recursos estáticos
async function handleStaticRequest(request) {
  // Cache First para recursos estáticos
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
    console.log('[SW] Failed to fetch static resource:', request.url);
    
    // Para imágenes, devolver placeholder
    if (request.destination === 'image') {
      return new Response(
        '<svg width="200" height="150" xmlns="http://www.w3.org/2000/svg"><rect width="200" height="150" fill="#f3f4f6"/><text x="50%" y="50%" text-anchor="middle" fill="#6b7280">Sin conexión</text></svg>',
        { headers: { 'Content-Type': 'image/svg+xml' } }
      );
    }
    
    throw error;
  }
}

// Manejo de peticiones POST (para sync en background)
async function handlePostRequest(request) {
  try {
    // Intentar enviar inmediatamente
    const response = await fetch(request);
    
    if (response.ok) {
      return response;
    }
    
    throw new Error('Network response not ok');
  } catch (error) {
    console.log('[SW] POST request failed, queuing for background sync');
    
    // Clonar request para guardar
    const requestClone = request.clone();
    const body = await requestClone.text();
    
    // Guardar en IndexedDB para background sync
    await saveRequestForSync({
      url: request.url,
      method: request.method,
      headers: Object.fromEntries(request.headers.entries()),
      body: body,
      timestamp: Date.now()
    });
    
    // Registrar background sync
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
      await self.registration.sync.register('background-sync');
    }
    
    // Devolver respuesta indicando que se guardó para sync
    return new Response(
      JSON.stringify({
        success: false,
        message: 'Guardado para sincronizar cuando haya conexión',
        queued: true,
        timestamp: Date.now()
      }),
      {
        status: 202,
        statusText: 'Accepted',
        headers: {
          'Content-Type': 'application/json',
          'X-Served-By': 'sw-sync-queue'
        }
      }
    );
  }
}

// Background Sync para peticiones pendientes
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync event:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(syncPendingRequests());
  }
});

// Sincronizar peticiones pendientes
async function syncPendingRequests() {
  try {
    const pendingRequests = await getPendingRequests();
    
    for (const request of pendingRequests) {
      try {
        const response = await fetch(request.url, {
          method: request.method,
          headers: request.headers,
          body: request.body
        });
        
        if (response.ok) {
          console.log('[SW] Successfully synced request:', request.url);
          await removeRequestFromSync(request.timestamp);
          
          // Notificar al cliente sobre el éxito
          notifyClients({
            type: 'sync-success',
            url: request.url,
            timestamp: request.timestamp
          });
        }
      } catch (error) {
        console.log('[SW] Failed to sync request:', request.url, error);
      }
    }
  } catch (error) {
    console.error('[SW] Error in syncPendingRequests:', error);
  }
}

// Funciones de IndexedDB para background sync
async function saveRequestForSync(request) {
  return new Promise((resolve, reject) => {
    const dbRequest = indexedDB.open('pos-sync-db', 1);
    
    dbRequest.onerror = () => reject(dbRequest.error);
    dbRequest.onsuccess = () => {
      const db = dbRequest.result;
      const transaction = db.transaction(['requests'], 'readwrite');
      const store = transaction.objectStore('requests');
      
      store.add(request);
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    };
    
    dbRequest.onupgradeneeded = (event) => {
      const db = event.target.result;
      const store = db.createObjectStore('requests', { keyPath: 'timestamp' });
      store.createIndex('url', 'url', { unique: false });
    };
  });
}

async function getPendingRequests() {
  return new Promise((resolve, reject) => {
    const dbRequest = indexedDB.open('pos-sync-db', 1);
    
    dbRequest.onerror = () => reject(dbRequest.error);
    dbRequest.onsuccess = () => {
      const db = dbRequest.result;
      
      // Verificar que el object store existe
      if (!db.objectStoreNames.contains('requests')) {
        console.log('[SW] Object store "requests" no existe, retornando array vacío');
        resolve([]);
        return;
      }
      
      const transaction = db.transaction(['requests'], 'readonly');
      const store = transaction.objectStore('requests');
      const getAllRequest = store.getAll();
      
      getAllRequest.onsuccess = () => resolve(getAllRequest.result);
      getAllRequest.onerror = () => reject(getAllRequest.error);
    };
  });
}

async function removeRequestFromSync(timestamp) {
  return new Promise((resolve, reject) => {
    const dbRequest = indexedDB.open('pos-sync-db', 1);
    
    dbRequest.onerror = () => reject(dbRequest.error);
    dbRequest.onsuccess = () => {
      const db = dbRequest.result;
      
      // Verificar que el object store existe
      if (!db.objectStoreNames.contains('requests')) {
        console.log('[SW] Object store "requests" no existe, no se puede eliminar');
        resolve();
        return;
      }
      
      const transaction = db.transaction(['requests'], 'readwrite');
      const store = transaction.objectStore('requests');
      
      store.delete(timestamp);
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    };
  });
}

// Notificar a los clientes
function notifyClients(message) {
  self.clients.matchAll().then(clients => {
    clients.forEach(client => {
      client.postMessage(message);
    });
  });
}

// Manejo de mensajes desde el cliente
self.addEventListener('message', (event) => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'skip-waiting':
      self.skipWaiting();
      break;
      
    case 'get-cache-info':
      getCacheInfo().then(info => {
        event.ports[0].postMessage(info);
      });
      break;
      
    case 'clear-cache':
      clearAllCaches().then(() => {
        event.ports[0].postMessage({ success: true });
      });
      break;
  }
});

// Información del cache
async function getCacheInfo() {
  const cacheNames = await caches.keys();
  const info = {};
  
  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    info[cacheName] = keys.length;
  }
  
  return info;
}

// Limpiar todos los caches
async function clearAllCaches() {
  const cacheNames = await caches.keys();
  await Promise.all(
    cacheNames.map(cacheName => caches.delete(cacheName))
  );
}

console.log('[SW] Service Worker loaded successfully');
