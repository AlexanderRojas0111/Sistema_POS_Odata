import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRole }) => {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user?.role !== requiredRole) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg max-w-md">
            <h3 className="font-bold">Acceso Denegado</h3>
            <p className="text-sm mt-2">
              No tienes permisos para acceder a esta sección.
            </p>
            <p className="text-xs mt-1">
              Rol requerido: {requiredRole} | Tu rol: {user?.role}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;
