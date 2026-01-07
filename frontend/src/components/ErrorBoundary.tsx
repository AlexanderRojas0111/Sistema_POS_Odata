/**
 * Error Boundary - Sistema POS Sabrositas
 * ======================================
 * Componente para capturar y manejar errores de React
 */

import React, { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Generar ID único para el error
    const errorId = `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    return {
      hasError: true,
      error,
      errorId
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log del error
    console.error('Error Boundary caught an error:', error, errorInfo);
    
    // Actualizar estado con información del error
    this.setState({
      error,
      errorInfo
    });

    // Llamar callback personalizado si existe
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Enviar error a servicio de monitoreo (si está disponible)
    this.reportError(error, errorInfo);
  }

  private reportError = (error: Error, errorInfo: ErrorInfo) => {
    // Enviar error al backend para logging
    try {
      fetch('/api/v1/monitoring/error', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          error: {
            message: error.message,
            stack: error.stack,
            name: error.name
          },
          errorInfo: {
            componentStack: errorInfo.componentStack
          },
          errorId: this.state.errorId,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          url: window.location.href
        })
      }).catch(err => {
        console.warn('Failed to report error to backend:', err);
      });
    } catch (err) {
      console.warn('Failed to report error:', err);
    }
  };

  private handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    });
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  private handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Si hay un fallback personalizado, usarlo
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Renderizar UI de error por defecto
      return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
          <div className="sm:mx-auto sm:w-full sm:max-w-md">
            <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
              {/* Icono de error */}
              <div className="flex justify-center">
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                  <AlertTriangle className="h-6 w-6 text-red-600" />
                </div>
              </div>

              {/* Título */}
              <div className="mt-6 text-center">
                <h2 className="text-2xl font-bold text-gray-900">
                  ¡Oops! Algo salió mal
                </h2>
                <p className="mt-2 text-sm text-gray-600">
                  Ha ocurrido un error inesperado en la aplicación
                </p>
              </div>

              {/* Detalles del error (solo en desarrollo) */}
              {import.meta.env.MODE === 'development' && this.state.error && (
                <div className="mt-6 bg-red-50 border border-red-200 rounded-md p-4">
                  <div className="flex">
                    <Bug className="h-5 w-5 text-red-400" />
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">
                        Detalles del Error (Desarrollo)
                      </h3>
                      <div className="mt-2 text-sm text-red-700">
                        <p><strong>Error:</strong> {this.state.error.message}</p>
                        <p><strong>ID del Error:</strong> {this.state.errorId}</p>
                        {this.state.error.stack && (
                          <details className="mt-2">
                            <summary className="cursor-pointer font-medium">
                              Stack Trace
                            </summary>
                            <pre className="mt-2 text-xs overflow-auto max-h-32">
                              {this.state.error.stack}
                            </pre>
                          </details>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Acciones */}
              <div className="mt-6 space-y-3">
                <button
                  onClick={this.handleRetry}
                  className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Intentar de nuevo
                </button>

                <button
                  onClick={this.handleGoHome}
                  className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <Home className="h-4 w-4 mr-2" />
                  Ir al inicio
                </button>

                <button
                  onClick={this.handleReload}
                  className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Recargar página
                </button>
              </div>

              {/* Información adicional */}
              <div className="mt-6 text-center">
                <p className="text-xs text-gray-500">
                  Si el problema persiste, contacta al administrador del sistema
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  ID del Error: {this.state.errorId}
                </p>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Hook para usar Error Boundary en componentes funcionales
export const useErrorHandler = () => {
  const [error, setError] = React.useState<Error | null>(null);

  const resetError = React.useCallback(() => {
    setError(null);
  }, []);

  const captureError = React.useCallback((error: Error) => {
    setError(error);
  }, []);

  React.useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);

  return { captureError, resetError };
};

// Componente de error personalizado para casos específicos
export const ErrorFallback: React.FC<{
  error: Error;
  resetError: () => void;
  errorId?: string;
}> = ({ error, resetError, errorId }) => {
  return (
    <div className="bg-red-50 border border-red-200 rounded-md p-4">
      <div className="flex">
        <AlertTriangle className="h-5 w-5 text-red-400" />
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800">
            Error en el componente
          </h3>
          <div className="mt-2 text-sm text-red-700">
            <p>{error.message}</p>
            {errorId && (
              <p className="mt-1 text-xs text-red-600">
                ID: {errorId}
              </p>
            )}
          </div>
          <div className="mt-3">
            <button
              onClick={resetError}
              className="text-sm font-medium text-red-800 hover:text-red-700"
            >
              Intentar de nuevo
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ErrorBoundary;
