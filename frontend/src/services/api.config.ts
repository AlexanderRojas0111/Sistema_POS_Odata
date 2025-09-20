/**
 * API Configuration - Sistema Sabrositas POS
 * ==========================================
 * Configuración robusta para integración con backend MySQL
 */

// Configuración base de la API
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:9000',
  version: import.meta.env.VITE_API_VERSION || 'v1',
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
  
  // Configuración multi-tienda
  multistore: {
    enabled: import.meta.env.VITE_MULTISTORE_ENABLED === 'true',
    defaultStoreId: parseInt(import.meta.env.VITE_DEFAULT_STORE_ID || '1'),
    syncInterval: parseInt(import.meta.env.VITE_SYNC_INTERVAL || '30000')
  },
  
  // Configuración de autenticación
  auth: {
    tokenKey: import.meta.env.VITE_JWT_STORAGE_KEY || 'sabrositas_auth_token',
    sessionTimeout: parseInt(import.meta.env.VITE_SESSION_TIMEOUT || '480')
  },
  
  // Configuración de UI
  ui: {
    currency: import.meta.env.VITE_CURRENCY || 'COP',
    taxRate: parseFloat(import.meta.env.VITE_TAX_RATE || '0.19'),
    language: import.meta.env.VITE_DEFAULT_LANGUAGE || 'es'
  }
};

// Endpoints de la API
export const API_ENDPOINTS = {
  // Autenticación
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    LOGOUT: '/api/v1/auth/logout',
    REFRESH: '/api/v1/auth/refresh',
    PROFILE: '/api/v1/auth/profile'
  },
  
  // Productos
  PRODUCTS: {
    LIST: '/api/v1/products',
    DETAIL: (id: number) => `/api/v1/products/${id}`,
    CREATE: '/api/v1/products',
    UPDATE: (id: number) => `/api/v1/products/${id}`,
    DELETE: (id: number) => `/api/v1/products/${id}`,
    SEARCH: '/api/v1/products/search'
  },
  
  // Ventas
  SALES: {
    LIST: '/api/v1/sales',
    CREATE: '/api/v1/sales',
    DETAIL: (id: number) => `/api/v1/sales/${id}`,
    CANCEL: (id: number) => `/api/v1/sales/${id}/cancel`
  },
  
  // Tiendas (Multi-sede)
  STORES: {
    LIST: '/api/v1/stores',
    DETAIL: (id: number) => `/api/v1/stores/${id}`,
    CREATE: '/api/v1/stores',
    UPDATE: (id: number) => `/api/v1/stores/${id}`,
    INVENTORY: (id: number) => `/api/v1/stores/${id}/inventory`,
    METRICS: (id: number) => `/api/v1/stores/${id}/metrics`,
    SYNC: (id: number) => `/api/v1/stores/${id}/sync`
  },
  
  // Sincronización
  SYNC: {
    STATUS: '/api/v1/sync/status',
    ALL_STORES: '/api/v1/sync/stores',
    STORE: (id: number) => `/api/v1/sync/stores/${id}`,
    HEALTH: '/api/v1/sync/health'
  },
  
  // Inventario Centralizado
  INVENTORY: {
    GLOBAL_SUMMARY: '/api/v1/inventory/global-summary',
    PRODUCT_DISTRIBUTION: (id: number) => `/api/v1/inventory/product/${id}/distribution`,
    REBALANCING_SUGGESTIONS: '/api/v1/inventory/rebalancing/suggestions',
    ALERTS: '/api/v1/inventory/alerts',
    RECONCILIATION: '/api/v1/inventory/reconciliation',
    TRENDS: '/api/v1/inventory/trends'
  },
  
  // Transferencias
  TRANSFERS: {
    LIST: '/api/v1/transfers',
    CREATE: '/api/v1/transfers',
    APPROVE: (id: number) => `/api/v1/transfers/${id}/approve`,
    SHIP: (id: number) => `/api/v1/transfers/${id}/ship`,
    RECEIVE: (id: number) => `/api/v1/transfers/${id}/receive`
  },
  
  // Reportes
  REPORTS: {
    SALES: '/api/v1/reports/sales',
    INVENTORY: '/api/v1/reports/inventory',
    PERFORMANCE: '/api/v1/reports/performance'
  },
  
  // Sistema
  SYSTEM: {
    HEALTH: '/api/v1/health',
    METRICS: '/api/v1/metrics'
  }
};

// Configuración de headers por defecto
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'X-Client': 'Sabrositas-Frontend',
  'X-Version': '2.0.0'
};

// Configuración de retry para requests
export const RETRY_CONFIG = {
  maxRetries: 3,
  retryDelay: 1000,
  retryCondition: (error: any) => {
    return error.response?.status >= 500 || error.code === 'NETWORK_ERROR';
  }
};

// Configuración de cache
export const CACHE_CONFIG = {
  enabled: import.meta.env.VITE_ENABLE_CACHE === 'true',
  duration: parseInt(import.meta.env.VITE_CACHE_DURATION || '300000'), // 5 minutos
  keys: {
    PRODUCTS: 'sabrositas_products',
    STORES: 'sabrositas_stores',
    USER_PROFILE: 'sabrositas_user_profile'
  }
};
