/**
 * Lazy Component - Sistema POS Sabrositas
 * ======================================
 * Componente para lazy loading con optimizaciones de rendimiento
 */

import React, { Suspense, lazy } from 'react';
import type { ComponentType, ReactNode } from 'react';
import { useIntersectionObserver } from '../hooks/usePerformance';
import './LazyComponent.css';

interface LazyComponentProps {
  importFn: () => Promise<{ default: ComponentType<any> }>;
  fallback?: ReactNode;
  placeholder?: ReactNode;
  threshold?: number;
  rootMargin?: string;
  [key: string]: any;
}

const DefaultFallback: React.FC = () => (
  <div className="lazy-component-loading">
    <div className="lazy-component-spinner rounded-full h-8 w-8 border-b-2 border-sabrositas-primary"></div>
    <span className="ml-2 text-gray-600">Cargando...</span>
  </div>
);

const DefaultPlaceholder: React.FC = () => (
  <div className="lazy-component-placeholder">
    <div className="lazy-skeleton h-4 w-3/4 mb-4"></div>
    <div className="lazy-skeleton h-4 w-1/2 mb-4"></div>
    <div className="lazy-skeleton h-4 w-5/6"></div>
  </div>
);

export const LazyComponent: React.FC<LazyComponentProps> = ({
  importFn,
  fallback = <DefaultFallback />,
  placeholder = <DefaultPlaceholder />,
  threshold = 0.1,
  rootMargin = '50px',
  ...props
}) => {
  const { ref, hasIntersected } = useIntersectionObserver<HTMLDivElement>({
    threshold,
    rootMargin
  });

  const LazyLoadedComponent = hasIntersected ? lazy(importFn) : null;

  return (
    <div ref={ref}>
      {hasIntersected ? (
        <Suspense fallback={fallback}>
          {LazyLoadedComponent && <LazyLoadedComponent {...props} />}
        </Suspense>
      ) : (
        placeholder
      )}
    </div>
  );
};

// Componente para lazy loading de imágenes
interface LazyImageProps {
  src: string;
  alt: string;
  placeholder?: string;
  className?: string;
  onLoad?: () => void;
  onError?: () => void;
}

export const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  placeholder = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PC9zdmc+',
  className = '',
  onLoad,
  onError
}) => {
  const { ref, hasIntersected } = useIntersectionObserver<HTMLDivElement>({
    threshold: 0.1,
    rootMargin: '50px'
  });

  const [imageLoaded, setImageLoaded] = React.useState(false);
  const [imageError, setImageError] = React.useState(false);

  const handleLoad = () => {
    setImageLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    setImageError(true);
    onError?.();
  };

  return (
    <div ref={ref} className={`relative overflow-hidden ${className}`}>
      {hasIntersected ? (
        <>
          {!imageLoaded && !imageError && (
            <img
              src={placeholder}
              alt=""
              className="absolute inset-0 w-full h-full object-cover blur-sm lazy-image-placeholder"
            />
          )}
          <img
            src={src}
            alt={alt}
            onLoad={handleLoad}
            onError={handleError}
            className={`w-full h-full object-cover transition-opacity duration-300 ${
              imageLoaded ? 'opacity-100' : 'opacity-0'
            }`}
          />
          {imageError && (
            <div className="absolute inset-0 lazy-image-error">
              <span>Error al cargar imagen</span>
            </div>
          )}
        </>
      ) : (
        <img
          src={placeholder}
          alt=""
          className="w-full h-full object-cover lazy-image-placeholder"
        />
      )}
    </div>
  );
};

// Componente para lazy loading de listas
interface LazyListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => ReactNode;
  itemHeight?: number;
  containerHeight?: number;
  overscan?: number;
  className?: string;
}

export const LazyList = <T,>({
  items,
  renderItem,
  itemHeight = 100,
  containerHeight = 400,
  overscan = 5,
  className = ''
}: LazyListProps<T>) => {
  const [scrollTop, setScrollTop] = React.useState(0);
  const containerRef = React.useRef<HTMLDivElement>(null);

  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );

  const visibleItems = items.slice(startIndex, endIndex + 1);
  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  };

  // Aplicar estilos dinámicos usando useEffect
  React.useEffect(() => {
    if (containerRef.current) {
      const container = containerRef.current;
      const content = container.querySelector('.virtual-scroll-content') as HTMLElement;
      const transform = container.querySelector('.virtual-scroll-transform') as HTMLElement;
      
      if (content) {
        content.style.height = `${totalHeight}px`;
      }
      
      if (transform) {
        transform.style.transform = `translateY(${offsetY}px)`;
      }
      
      // Aplicar altura a los items
      const items = container.querySelectorAll('.virtual-scroll-item');
      items.forEach((item) => {
        (item as HTMLElement).style.height = `${itemHeight}px`;
      });
    }
  }, [totalHeight, offsetY, itemHeight]);

  // Aplicar altura del contenedor usando useEffect
  React.useEffect(() => {
    if (containerRef.current) {
      containerRef.current.style.height = `${containerHeight}px`;
    }
  }, [containerHeight]);

  return (
    <div
      ref={containerRef}
      className={`overflow-auto virtual-scroll-container ${className}`}
      onScroll={handleScroll}
    >
      <div className="relative virtual-scroll-content">
        <div className="absolute top-0 left-0 right-0 virtual-scroll-transform">
          {visibleItems.map((item, index) => (
            <div
              key={startIndex + index}
              className="virtual-scroll-item"
            >
              {renderItem(item, startIndex + index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Hook para preload de componentes
export const usePreload = () => {
  const preloadedComponents = React.useRef<Set<string>>(new Set());

  const preload = React.useCallback((importFn: () => Promise<any>, key: string) => {
    if (preloadedComponents.current.has(key)) {
      return Promise.resolve();
    }

    return importFn().then(() => {
      preloadedComponents.current.add(key);
    });
  }, []);

  const isPreloaded = React.useCallback((key: string) => {
    return preloadedComponents.current.has(key);
  }, []);

  return { preload, isPreloaded };
};

// Componente para code splitting por rutas
interface RouteLazyProps {
  path: string;
  importFn: () => Promise<{ default: ComponentType<any> }>;
  fallback?: ReactNode;
}

export const RouteLazy: React.FC<RouteLazyProps> = ({
  path,
  importFn,
  fallback = <DefaultFallback />
}) => {
  const LazyComponent = React.useMemo(() => lazy(importFn), [importFn]);

  return (
    <Suspense fallback={fallback}>
      <LazyComponent />
    </Suspense>
  );
};

// Componente para lazy loading de módulos
interface ModuleLazyProps {
  moduleName: string;
  importFn: () => Promise<any>;
  fallback?: ReactNode;
  onLoad?: (module: any) => void;
  onError?: (error: Error) => void;
}

export const ModuleLazy: React.FC<ModuleLazyProps> = ({
  moduleName,
  importFn,
  fallback = <DefaultFallback />,
  onLoad,
  onError
}) => {
  const [module, setModule] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<Error | null>(null);

  React.useEffect(() => {
    setLoading(true);
    setError(null);

    importFn()
      .then((loadedModule) => {
        setModule(loadedModule);
        onLoad?.(loadedModule);
      })
      .catch((err) => {
        setError(err);
        onError?.(err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [importFn, onLoad, onError]);

  if (loading) return <>{fallback}</>;
  if (error) return <div>Error loading {moduleName}: {error.message}</div>;
  if (!module) return null;

  return <>{module.default ? <module.default /> : null}</>;
};
