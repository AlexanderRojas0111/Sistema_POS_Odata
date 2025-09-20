/**
 * API Client - Sistema Sabrositas POS
 * ===================================
 * Cliente HTTP robusto para integración con backend MySQL
 */

import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { API_CONFIG, DEFAULT_HEADERS, RETRY_CONFIG, CACHE_CONFIG } from './api.config';

// Tipos para respuestas de la API
export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
  error?: string;
  timestamp?: string;
}

export interface PaginatedResponse<T = any> {
  data: T[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

class ApiClient {
  private client: AxiosInstance;
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private retryCount: Map<string, number> = new Map();

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.baseURL,
      timeout: API_CONFIG.timeout,
      headers: DEFAULT_HEADERS
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Agregar token de autenticación si existe
        const token = this.getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Agregar store_id si está configurado para multi-tienda
        if (API_CONFIG.multistore.enabled) {
          const storeId = this.getCurrentStoreId();
          if (storeId) {
            config.headers['X-Store-ID'] = storeId.toString();
          }
        }

        // Logging en desarrollo
        if (import.meta.env.DEV) {
          console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
        }

        return config;
      },
      (error) => {
        console.error('❌ Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Logging en desarrollo
        if (import.meta.env.DEV) {
          console.log(`✅ API Response: ${response.status} ${response.config.url}`);
        }

        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        // Manejo de errores de autenticación
        if (error.response?.status === 401) {
          this.handleAuthError();
          return Promise.reject(error);
        }

        // Retry logic para errores de servidor
        if (this.shouldRetry(error) && !originalRequest._retry) {
          originalRequest._retry = true;
          
          const retryKey = `${originalRequest.method}-${originalRequest.url}`;
          const currentRetries = this.retryCount.get(retryKey) || 0;
          
          if (currentRetries < RETRY_CONFIG.maxRetries) {
            this.retryCount.set(retryKey, currentRetries + 1);
            
            await this.delay(RETRY_CONFIG.retryDelay * (currentRetries + 1));
            
            console.log(`🔄 Retrying request: ${retryKey} (attempt ${currentRetries + 1})`);
            return this.client(originalRequest);
          }
        }

        // Logging de errores
        console.error('❌ API Error:', {
          status: error.response?.status,
          message: error.response?.data?.message || error.message,
          url: error.config?.url
        });

        return Promise.reject(error);
      }
    );
  }

  private shouldRetry(error: any): boolean {
    return RETRY_CONFIG.retryCondition(error);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private getAuthToken(): string | null {
    try {
      return localStorage.getItem(API_CONFIG.auth.tokenKey);
    } catch {
      return null;
    }
  }

  private getCurrentStoreId(): number | null {
    try {
      const storeId = localStorage.getItem('current_store_id');
      return storeId ? parseInt(storeId) : API_CONFIG.multistore.defaultStoreId;
    } catch {
      return API_CONFIG.multistore.defaultStoreId;
    }
  }

  private handleAuthError(): void {
    // Limpiar token y redirigir al login
    localStorage.removeItem(API_CONFIG.auth.tokenKey);
    localStorage.removeItem('current_store_id');
    
    // Emitir evento para que la app maneje la redirección
    window.dispatchEvent(new CustomEvent('auth:expired'));
  }

  // Métodos de cache
  private getCacheKey(url: string, params?: any): string {
    const paramString = params ? JSON.stringify(params) : '';
    return `${url}${paramString}`;
  }

  private getFromCache<T>(key: string): T | null {
    if (!CACHE_CONFIG.enabled) return null;

    const cached = this.cache.get(key);
    if (!cached) return null;

    const isExpired = Date.now() - cached.timestamp > CACHE_CONFIG.duration;
    if (isExpired) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  private setCache<T>(key: string, data: T): void {
    if (!CACHE_CONFIG.enabled) return;

    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  // Métodos HTTP principales
  public async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const cacheKey = this.getCacheKey(url, config?.params);
    
    // Intentar obtener del cache primero
    const cached = this.getFromCache<ApiResponse<T>>(cacheKey);
    if (cached) {
      console.log(`📦 Cache hit: ${url}`);
      return cached;
    }

    try {
      const response: AxiosResponse<ApiResponse<T>> = await this.client.get(url, config);
      
      // Guardar en cache si es exitoso
      if (response.data.status === 'success') {
        this.setCache(cacheKey, response.data);
      }
      
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  public async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await this.client.post(url, data, config);
      
      // Invalidar cache relacionado
      this.invalidateCache(url);
      
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  public async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await this.client.put(url, data, config);
      
      // Invalidar cache relacionado
      this.invalidateCache(url);
      
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  public async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await this.client.delete(url, config);
      
      // Invalidar cache relacionado
      this.invalidateCache(url);
      
      return response.data;
    } catch (error: any) {
      throw this.handleError(error);
    }
  }

  private invalidateCache(url: string): void {
    // Invalidar cache relacionado con la URL
    const keysToDelete: string[] = [];
    
    for (const [key] of this.cache) {
      if (key.includes(url.split('?')[0])) {
        keysToDelete.push(key);
      }
    }
    
    keysToDelete.forEach(key => this.cache.delete(key));
  }

  private handleError(error: any): Error {
    if (error.response) {
      // Error de respuesta del servidor
      const message = error.response.data?.message || error.response.data?.error || `HTTP ${error.response.status}`;
      return new Error(message);
    } else if (error.request) {
      // Error de red
      return new Error('Error de conexión. Verifica tu conexión a internet.');
    } else {
      // Error de configuración
      return new Error(error.message || 'Error desconocido');
    }
  }

  // Métodos específicos para Sabrositas POS
  public async getProducts(storeId?: number): Promise<ApiResponse<PaginatedResponse<any>>> {
    const params = storeId ? { store_id: storeId } : {};
    return this.get('/api/v1/products', { params });
  }

  public async getStores(): Promise<ApiResponse<any>> {
    return this.get('/api/v1/stores');
  }

  public async getSyncStatus(storeId?: number): Promise<ApiResponse<any>> {
    const params = storeId ? { store_id: storeId } : {};
    return this.get('/api/v1/sync/status', { params });
  }

  public async getInventoryAlerts(): Promise<ApiResponse<any>> {
    return this.get('/api/v1/inventory/alerts');
  }

  // Métodos de utilidad
  public clearCache(): void {
    this.cache.clear();
    console.log('🧹 Cache cleared');
  }

  public setAuthToken(token: string): void {
    localStorage.setItem(API_CONFIG.auth.tokenKey, token);
  }

  public removeAuthToken(): void {
    localStorage.removeItem(API_CONFIG.auth.tokenKey);
  }

  public setCurrentStore(storeId: number): void {
    localStorage.setItem('current_store_id', storeId.toString());
    this.clearCache(); // Limpiar cache al cambiar de tienda
  }

  // Health check específico
  public async healthCheck(): Promise<boolean> {
    try {
      const response = await this.get('/api/v1/health');
      return response.status === 'success';
    } catch {
      return false;
    }
  }

  // Test de conectividad MySQL
  public async testMySQLConnection(): Promise<boolean> {
    try {
      const response = await this.get('/api/v1/health');
      return response.data?.database === 'connected';
    } catch {
      return false;
    }
  }
}

// Instancia singleton del cliente API
export const apiClient = new ApiClient();

// Hook personalizado para React
export const useApiClient = () => {
  return apiClient;
};

// Tipos exportados
