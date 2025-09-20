/**
 * Hook PWA - Sistema POS Sabrositas
 * Manejo de Service Worker, instalación PWA y funcionalidad offline
 */

import { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';

interface PWAState {
  isOnline: boolean;
  isInstallable: boolean;
  isInstalled: boolean;
  isUpdateAvailable: boolean;
  syncInProgress: boolean;
  pendingSyncs: number;
}

interface PWAActions {
  installApp: () => Promise<void>;
  updateApp: () => Promise<void>;
  syncPendingData: () => Promise<void>;
  clearCache: () => Promise<void>;
  getCacheInfo: () => Promise<Record<string, number>>;
}

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

export const usePWA = (): PWAState & PWAActions => {
  // Estados
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isUpdateAvailable, setIsUpdateAvailable] = useState(false);
  const [syncInProgress, setSyncInProgress] = useState(false);
  const [pendingSyncs, setPendingSyncs] = useState(0);
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [registration, setRegistration] = useState<ServiceWorkerRegistration | null>(null);

  // Registrar Service Worker
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      registerServiceWorker();
    }
  }, []);

  // Escuchar eventos de conexión
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      toast.success('🟢 Conexión restaurada');
      syncPendingData();
    };

    const handleOffline = () => {
      setIsOnline(false);
      toast.error('🔴 Sin conexión - Modo offline activado');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Escuchar evento de instalación PWA
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setIsInstallable(true);
    };

    const handleAppInstalled = () => {
      setIsInstalled(true);
      setIsInstallable(false);
      setDeferredPrompt(null);
      toast.success('🎉 App instalada correctamente');
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  // Verificar si ya está instalada
  useEffect(() => {
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
    }
  }, []);

  // Registrar Service Worker
  const registerServiceWorker = async () => {
    try {
      const reg = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      });

      setRegistration(reg);

      // Escuchar actualizaciones
      reg.addEventListener('updatefound', () => {
        const newWorker = reg.installing;
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              setIsUpdateAvailable(true);
              toast.success('🔄 Actualización disponible', {
                duration: 6000,
                icon: '🆕'
              });
            }
          });
        }
      });

      // Escuchar mensajes del Service Worker
      navigator.serviceWorker.addEventListener('message', (event) => {
        const { type, data: _data } = event.data;
        
        switch (type) {
          case 'sync-success':
            toast.success('✅ Datos sincronizados');
            updatePendingSyncs();
            break;
            
          case 'sync-error':
            toast.error('❌ Error en sincronización');
            break;
            
          case 'cache-updated':
            toast.success('💾 Cache actualizado');
            break;
        }
      });

      console.log('Service Worker registrado correctamente');
      
      // Obtener número de syncs pendientes
      updatePendingSyncs();

    } catch (error) {
      console.error('Error registrando Service Worker:', error);
      toast.error('Error configurando modo offline');
    }
  };

  // Actualizar contador de syncs pendientes
  const updatePendingSyncs = useCallback(async () => {
    try {
      const dbRequest = indexedDB.open('pos-sync-db', 1);
      
      dbRequest.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains('requests')) {
          const store = db.createObjectStore('requests', { keyPath: 'timestamp' });
          store.createIndex('url', 'url', { unique: false });
        }
      };
      
      dbRequest.onsuccess = () => {
        const db = dbRequest.result;
        
        // Verificar que el object store existe
        if (!db.objectStoreNames.contains('requests')) {
          setPendingSyncs(0);
          return;
        }
        
        const transaction = db.transaction(['requests'], 'readonly');
        const store = transaction.objectStore('requests');
        const countRequest = store.count();
        
        countRequest.onsuccess = () => {
          setPendingSyncs(countRequest.result);
        };
        
        countRequest.onerror = () => {
          setPendingSyncs(0);
        };
      };
      
      dbRequest.onerror = () => {
        setPendingSyncs(0);
      };
    } catch (error) {
      console.error('Error obteniendo syncs pendientes:', error);
      setPendingSyncs(0);
    }
  }, []);

  // Instalar aplicación
  const installApp = useCallback(async () => {
    if (!deferredPrompt) {
      toast.error('La instalación no está disponible');
      return;
    }

    try {
      await deferredPrompt.prompt();
      const choiceResult = await deferredPrompt.userChoice;
      
      if (choiceResult.outcome === 'accepted') {
        toast.success('🎉 Instalando aplicación...');
      } else {
        toast('Instalación cancelada', { icon: 'ℹ️' });
      }
      
      setDeferredPrompt(null);
      setIsInstallable(false);
      
    } catch (error) {
      console.error('Error instalando app:', error);
      toast.error('Error en la instalación');
    }
  }, [deferredPrompt]);

  // Actualizar aplicación
  const updateApp = useCallback(async () => {
    if (!registration || !registration.waiting) {
      toast.error('No hay actualizaciones disponibles');
      return;
    }

    try {
      // Enviar mensaje al Service Worker para que se active
      registration.waiting.postMessage({ type: 'skip-waiting' });
      
      // Recargar la página
      setTimeout(() => {
        window.location.reload();
      }, 1000);
      
      toast.success('🔄 Actualizando aplicación...');
      
    } catch (error) {
      console.error('Error actualizando app:', error);
      toast.error('Error en la actualización');
    }
  }, [registration]);

  // Sincronizar datos pendientes
  const syncPendingData = useCallback(async () => {
    if (!registration || syncInProgress) return;

    try {
      setSyncInProgress(true);
      
      // Registrar background sync
      if ('sync' in registration) {
        await (registration as any).sync.register('background-sync');
        toast('🔄 Sincronizando datos...', { icon: '🔄' });
      }
      
      // Actualizar contador
      setTimeout(updatePendingSyncs, 2000);
      
    } catch (error) {
      console.error('Error sincronizando:', error);
      toast.error('Error en sincronización');
    } finally {
      setSyncInProgress(false);
    }
  }, [registration, syncInProgress, updatePendingSyncs]);

  // Limpiar cache
  const clearCache = useCallback(async () => {
    if (!registration) {
      toast.error('Service Worker no disponible');
      return;
    }

    try {
      const channel = new MessageChannel();
      
      return new Promise<void>((resolve, reject) => {
        channel.port1.onmessage = (event) => {
          if (event.data.success) {
            toast.success('🗑️ Cache limpiado');
            resolve();
          } else {
            reject(new Error('Error limpiando cache'));
          }
        };

        registration.active?.postMessage(
          { type: 'clear-cache' },
          [channel.port2]
        );
      });

    } catch (error) {
      console.error('Error limpiando cache:', error);
      toast.error('Error limpiando cache');
    }
  }, [registration]);

  // Obtener información del cache
  const getCacheInfo = useCallback(async (): Promise<Record<string, number>> => {
    if (!registration) {
      return {};
    }

    try {
      const channel = new MessageChannel();
      
      return new Promise<Record<string, number>>((resolve, reject) => {
        channel.port1.onmessage = (event) => {
          resolve(event.data);
        };

        setTimeout(() => {
          reject(new Error('Timeout obteniendo info del cache'));
        }, 5000);

        registration.active?.postMessage(
          { type: 'get-cache-info' },
          [channel.port2]
        );
      });

    } catch (error) {
      console.error('Error obteniendo cache info:', error);
      return {};
    }
  }, [registration]);

  return {
    // Estados
    isOnline,
    isInstallable,
    isInstalled,
    isUpdateAvailable,
    syncInProgress,
    pendingSyncs,
    
    // Acciones
    installApp,
    updateApp,
    syncPendingData,
    clearCache,
    getCacheInfo
  };
};
