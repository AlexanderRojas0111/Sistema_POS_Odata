/**
 * PWA Install Banner - Sistema POS Sabrositas
 * Banner para instalar la aplicación como PWA
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Download, X, Smartphone, Wifi, WifiOff, 
  RefreshCw, Trash2, Info 
} from 'lucide-react';
import { usePWA } from '../hooks/usePWA';

const PWAInstallBanner: React.FC = () => {
  const {
    isOnline,
    isInstallable,
    isInstalled,
    isUpdateAvailable,
    syncInProgress,
    pendingSyncs,
    installApp,
    updateApp,
    syncPendingData,
    clearCache
  } = usePWA();

  const [showBanner, setShowBanner] = useState(true);
  const [showDetails, setShowDetails] = useState(false);

  // No mostrar si ya está instalada o no es instalable
  if (isInstalled && !isUpdateAvailable && pendingSyncs === 0) {
    return null;
  }

  return (
    <AnimatePresence>
      {showBanner && (
        <motion.div
          initial={{ opacity: 0, y: -100 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -100 }}
          className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg"
        >
          <div className="max-w-7xl mx-auto px-4 py-3">
            <div className="flex items-center justify-between">
              {/* Contenido principal */}
              <div className="flex items-center space-x-4">
                {/* Icono de estado */}
                <div className="flex-shrink-0">
                  {!isOnline ? (
                    <WifiOff className="h-6 w-6" />
                  ) : isUpdateAvailable ? (
                    <RefreshCw className="h-6 w-6" />
                  ) : (
                    <Smartphone className="h-6 w-6" />
                  )}
                </div>

                {/* Mensaje */}
                <div className="flex-1">
                  {!isOnline ? (
                    <div>
                      <p className="font-semibold">Modo Offline Activado</p>
                      <p className="text-sm opacity-90">
                        Funcionalidad limitada disponible
                        {pendingSyncs > 0 && (
                          <span className="ml-2 bg-red-500 text-white px-2 py-1 rounded-full text-xs">
                            {pendingSyncs} pendientes
                          </span>
                        )}
                      </p>
                    </div>
                  ) : isUpdateAvailable ? (
                    <div>
                      <p className="font-semibold">Actualización Disponible</p>
                      <p className="text-sm opacity-90">
                        Nueva versión lista para instalar
                      </p>
                    </div>
                  ) : isInstallable ? (
                    <div>
                      <p className="font-semibold">¡Instala POS Sabrositas!</p>
                      <p className="text-sm opacity-90">
                        Acceso rápido, modo offline y mejor rendimiento
                      </p>
                    </div>
                  ) : null}
                </div>
              </div>

              {/* Botones de acción */}
              <div className="flex items-center space-x-2">
                {!isOnline && pendingSyncs > 0 && (
                  <button
                    onClick={syncPendingData}
                    disabled={syncInProgress}
                    className="flex items-center space-x-1 bg-white bg-opacity-20 hover:bg-opacity-30 px-3 py-1 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                  >
                    <RefreshCw className={`h-4 w-4 ${syncInProgress ? 'animate-spin' : ''}`} />
                    <span>Sincronizar</span>
                  </button>
                )}

                {isUpdateAvailable && (
                  <button
                    onClick={updateApp}
                    className="flex items-center space-x-1 bg-white bg-opacity-20 hover:bg-opacity-30 px-3 py-1 rounded-lg text-sm font-medium transition-colors"
                  >
                    <RefreshCw className="h-4 w-4" />
                    <span>Actualizar</span>
                  </button>
                )}

                {isInstallable && (
                  <button
                    onClick={installApp}
                    className="flex items-center space-x-1 bg-white bg-opacity-20 hover:bg-opacity-30 px-3 py-1 rounded-lg text-sm font-medium transition-colors"
                  >
                    <Download className="h-4 w-4" />
                    <span>Instalar</span>
                  </button>
                )}

                {/* Botón de detalles */}
                <button
                  onClick={() => setShowDetails(!showDetails)}
                  className="p-1 hover:bg-white hover:bg-opacity-20 rounded transition-colors"
                  title="Ver detalles del estado PWA"
                  aria-label="Ver detalles del estado PWA"
                >
                  <Info className="h-4 w-4" />
                </button>

                {/* Botón cerrar */}
                <button
                  onClick={() => setShowBanner(false)}
                  className="p-1 hover:bg-white hover:bg-opacity-20 rounded transition-colors"
                  title="Cerrar banner PWA"
                  aria-label="Cerrar banner PWA"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Panel de detalles */}
            <AnimatePresence>
              {showDetails && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-3 pt-3 border-t border-white border-opacity-20"
                >
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    {/* Estado de conexión */}
                    <div className="flex items-center space-x-2">
                      <Wifi className={`h-4 w-4 ${isOnline ? 'text-green-200' : 'text-red-200'}`} />
                      <span>
                        Estado: {isOnline ? 'Conectado' : 'Sin conexión'}
                      </span>
                    </div>

                    {/* Sincronización pendiente */}
                    {pendingSyncs > 0 && (
                      <div className="flex items-center space-x-2">
                        <RefreshCw className="h-4 w-4 text-yellow-200" />
                        <span>
                          {pendingSyncs} operación{pendingSyncs !== 1 ? 'es' : ''} pendiente{pendingSyncs !== 1 ? 's' : ''}
                        </span>
                      </div>
                    )}

                    {/* Funciones offline */}
                    <div className="text-xs opacity-80">
                      ✅ Ver productos • ✅ Crear ventas • ✅ Analytics básicos
                    </div>
                  </div>

                  {/* Botones adicionales */}
                  <div className="flex items-center space-x-2 mt-3">
                    <button
                      onClick={clearCache}
                      className="flex items-center space-x-1 bg-white bg-opacity-10 hover:bg-opacity-20 px-2 py-1 rounded text-xs transition-colors"
                    >
                      <Trash2 className="h-3 w-3" />
                      <span>Limpiar Cache</span>
                    </button>

                    {isOnline && (
                      <button
                        onClick={syncPendingData}
                        disabled={syncInProgress}
                        className="flex items-center space-x-1 bg-white bg-opacity-10 hover:bg-opacity-20 px-2 py-1 rounded text-xs transition-colors disabled:opacity-50"
                      >
                        <RefreshCw className={`h-3 w-3 ${syncInProgress ? 'animate-spin' : ''}`} />
                        <span>Forzar Sync</span>
                      </button>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default PWAInstallBanner;
