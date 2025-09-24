/**
 * Hook de Rendimiento - Sistema POS Sabrositas
 * ============================================
 * Hook para optimización de rendimiento y métricas
 */

import { useEffect, useRef, useCallback, useState } from 'react';

interface PerformanceMetrics {
  renderTime: number;
  memoryUsage?: number;
  componentName: string;
  timestamp: number;
}

interface PerformanceConfig {
  enableMetrics: boolean;
  logToConsole: boolean;
  sendToBackend: boolean;
  threshold: number; // ms
}

const defaultConfig: PerformanceConfig = {
  enableMetrics: process.env.NODE_ENV === 'development',
  logToConsole: process.env.NODE_ENV === 'development',
  sendToBackend: true,
  threshold: 16 // 60fps threshold
};

export const usePerformance = (
  componentName: string,
  config: Partial<PerformanceConfig> = {}
) => {
  const finalConfig = { ...defaultConfig, ...config };
  const renderStartTime = useRef<number>(0);
  const renderCount = useRef<number>(0);
  const [metrics, setMetrics] = useState<PerformanceMetrics[]>([]);

  // Medir tiempo de render
  const startRender = useCallback(() => {
    if (finalConfig.enableMetrics) {
      renderStartTime.current = performance.now();
    }
  }, [finalConfig.enableMetrics]);

  const endRender = useCallback(() => {
    if (finalConfig.enableMetrics && renderStartTime.current > 0) {
      const renderTime = performance.now() - renderStartTime.current;
      renderCount.current += 1;

      const metric: PerformanceMetrics = {
        renderTime,
        componentName,
        timestamp: Date.now(),
        memoryUsage: (performance as any).memory?.usedJSHeapSize
      };

      setMetrics(prev => [...prev.slice(-9), metric]); // Mantener solo últimas 10

      // Log si excede threshold
      if (renderTime > finalConfig.threshold) {
        if (finalConfig.logToConsole) {
          console.warn(`🐌 Slow render in ${componentName}: ${renderTime.toFixed(2)}ms`);
        }
      }

      // Enviar métricas al backend
      if (finalConfig.sendToBackend && renderTime > finalConfig.threshold) {
        sendMetricsToBackend(metric);
      }
    }
  }, [componentName, finalConfig]);

  // Enviar métricas al backend
  const sendMetricsToBackend = useCallback(async (metric: PerformanceMetrics) => {
    try {
      await fetch('/api/v1/monitoring/performance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          component: metric.componentName,
          renderTime: metric.renderTime,
          memoryUsage: metric.memoryUsage,
          timestamp: metric.timestamp
        })
      });
    } catch (error) {
      console.warn('Failed to send performance metrics:', error);
    }
  }, []);

  // Obtener estadísticas
  const getStats = useCallback(() => {
    if (metrics.length === 0) return null;

    const renderTimes = metrics.map(m => m.renderTime);
    const avgRenderTime = renderTimes.reduce((a, b) => a + b, 0) / renderTimes.length;
    const maxRenderTime = Math.max(...renderTimes);
    const minRenderTime = Math.min(...renderTimes);

    return {
      renderCount: renderCount.current,
      avgRenderTime: Math.round(avgRenderTime * 100) / 100,
      maxRenderTime: Math.round(maxRenderTime * 100) / 100,
      minRenderTime: Math.round(minRenderTime * 100) / 100,
      slowRenders: renderTimes.filter(t => t > finalConfig.threshold).length
    };
  }, [metrics, finalConfig.threshold]);

  return {
    startRender,
    endRender,
    metrics,
    getStats,
    renderCount: renderCount.current
  };
};

// Hook para lazy loading
export const useLazyLoading = <T>(
  importFn: () => Promise<T>,
  deps: any[] = []
) => {
  const [Component, setComponent] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const loadComponent = useCallback(async () => {
    if (Component || loading) return;

    setLoading(true);
    setError(null);

    try {
      const module = await importFn();
      setComponent(module);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [Component, loading, importFn]);

  useEffect(() => {
    loadComponent();
  }, deps);

  return { Component, loading, error, retry: loadComponent };
};

// Hook para memoización inteligente
export const useSmartMemo = <T>(
  factory: () => T,
  deps: any[],
  options: {
    maxAge?: number; // ms
    maxSize?: number;
  } = {}
) => {
  const cache = useRef<Map<string, { value: T; timestamp: number }>>(new Map());
  const { maxAge = 5000, maxSize = 100 } = options;

  return useCallback(() => {
    const key = JSON.stringify(deps);
    const now = Date.now();
    const cached = cache.current.get(key);

    // Verificar si el cache es válido
    if (cached && (now - cached.timestamp) < maxAge) {
      return cached.value;
    }

    // Limpiar cache si es muy grande
    if (cache.current.size >= maxSize) {
      const oldestKey = cache.current.keys().next().value;
      cache.current.delete(oldestKey);
    }

    // Crear nuevo valor
    const value = factory();
    cache.current.set(key, { value, timestamp: now });

    return value;
  }, deps);
};

// Hook para debounce inteligente
export const useSmartDebounce = <T>(
  value: T,
  delay: number,
  options: {
    leading?: boolean;
    trailing?: boolean;
    maxWait?: number;
  } = {}
) => {
  const { leading = false, trailing = true, maxWait } = options;
  const [debouncedValue, setDebouncedValue] = useState(value);
  const timeoutRef = useRef<NodeJS.Timeout>();
  const maxTimeoutRef = useRef<NodeJS.Timeout>();
  const lastCallTime = useRef<number>(0);

  useEffect(() => {
    const now = Date.now();
    const timeSinceLastCall = now - lastCallTime.current;

    // Leading edge
    if (leading && timeSinceLastCall >= delay) {
      setDebouncedValue(value);
      lastCallTime.current = now;
    }

    // Clear existing timeouts
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    if (maxTimeoutRef.current) {
      clearTimeout(maxTimeoutRef.current);
    }

    // Trailing edge
    if (trailing) {
      timeoutRef.current = setTimeout(() => {
        setDebouncedValue(value);
        lastCallTime.current = Date.now();
      }, delay);
    }

    // Max wait
    if (maxWait && timeSinceLastCall >= maxWait) {
      setDebouncedValue(value);
      lastCallTime.current = now;
    }

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (maxTimeoutRef.current) clearTimeout(maxTimeoutRef.current);
    };
  }, [value, delay, leading, trailing, maxWait]);

  return debouncedValue;
};

// Hook para throttling
export const useThrottle = <T>(
  value: T,
  limit: number,
  options: {
    leading?: boolean;
    trailing?: boolean;
  } = {}
) => {
  const { leading = true, trailing = false } = options;
  const [throttledValue, setThrottledValue] = useState(value);
  const lastRan = useRef<number>(0);

  useEffect(() => {
    const now = Date.now();

    if (leading && (now - lastRan.current) >= limit) {
      setThrottledValue(value);
      lastRan.current = now;
    } else if (trailing) {
      const timeout = setTimeout(() => {
        setThrottledValue(value);
        lastRan.current = Date.now();
      }, limit - (now - lastRan.current));

      return () => clearTimeout(timeout);
    }
  }, [value, limit, leading, trailing]);

  return throttledValue;
};

// Hook para intersection observer (lazy loading de imágenes)
export const useIntersectionObserver = (
  options: IntersectionObserverInit = {}
) => {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [hasIntersected, setHasIntersected] = useState(false);
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting);
        if (entry.isIntersecting && !hasIntersected) {
          setHasIntersected(true);
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options
      }
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [options, hasIntersected]);

  return { ref, isIntersecting, hasIntersected };
};

// Hook para virtual scrolling
export const useVirtualScroll = <T>(
  items: T[],
  itemHeight: number,
  containerHeight: number,
  overscan: number = 5
) => {
  const [scrollTop, setScrollTop] = useState(0);

  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );

  const visibleItems = items.slice(startIndex, endIndex + 1);
  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;

  return {
    visibleItems,
    totalHeight,
    offsetY,
    startIndex,
    endIndex,
    setScrollTop
  };
};
