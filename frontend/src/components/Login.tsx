import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../authSimple';
import { 
  Building2, 
  Lock, 
  User, 
  Eye, 
  EyeOff, 
  ArrowRight,
  Shield,
  Users,
  DollarSign,
  BarChart3
} from 'lucide-react';

const Login: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirigir si ya está autenticado
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await login(formData.username, formData.password);
      navigate('/dashboard');
    } catch (err) {
      setError('Credenciales inválidas. Por favor, inténtalo de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const systemCredentials = [
    { role: 'SuperAdmin', username: 'superadmin', password: 'SuperAdmin123!', icon: Shield, color: 'bg-red-600' },
    { role: 'Global Admin', username: 'globaladmin', password: 'Global123!', icon: Users, color: 'bg-blue-600' },
    { role: 'Store Admin', username: 'storeadmin1', password: 'Store123!', icon: BarChart3, color: 'bg-green-600' },
    { role: 'Tech Admin', username: 'techadmin', password: 'TechAdmin123!', icon: DollarSign, color: 'bg-purple-600' }
  ];

  const fillCredentials = (username: string, password: string) => {
    setFormData({ username, password });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-amber-50 flex">
      {/* Panel izquierdo - Información del sistema */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 to-blue-800 text-white p-12 flex-col justify-center">
        <div className="max-w-md">
          <div className="flex items-center mb-8">
            <Building2 className="h-12 w-12 mr-4" />
            <div>
              <h1 className="text-3xl font-bold">Sistema POS</h1>
              <p className="text-blue-200">Sabrositas Enterprise</p>
            </div>
          </div>
          
          <h2 className="text-2xl font-semibold mb-4">
            Solución Empresarial Completa
          </h2>
          
          <p className="text-blue-100 mb-8 leading-relaxed">
            Sistema de punto de venta integral con gestión de nómina, cartera, 
            cotizaciones y análisis avanzado para tu negocio.
          </p>

          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center space-x-3">
              <Shield className="h-5 w-5 text-blue-300" />
              <span className="text-sm">Seguridad Avanzada</span>
            </div>
            <div className="flex items-center space-x-3">
              <BarChart3 className="h-5 w-5 text-blue-300" />
              <span className="text-sm">Reportes en Tiempo Real</span>
            </div>
            <div className="flex items-center space-x-3">
              <Users className="h-5 w-5 text-blue-300" />
              <span className="text-sm">Gestión de Usuarios</span>
            </div>
            <div className="flex items-center space-x-3">
              <DollarSign className="h-5 w-5 text-blue-300" />
              <span className="text-sm">Control Financiero</span>
            </div>
          </div>
        </div>
      </div>

      {/* Panel derecho - Formulario de login */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Logo móvil */}
          <div className="lg:hidden flex items-center justify-center mb-8">
            <div className="flex items-center">
              <Building2 className="h-10 w-10 text-blue-600 mr-3" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Sistema POS</h1>
                <p className="text-gray-600">Sabrositas Enterprise</p>
              </div>
            </div>
          </div>

          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Bienvenido de vuelta
            </h2>
            <p className="text-gray-600">
              Inicia sesión para acceder al sistema
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Usuario
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={handleInputChange}
                  className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ingresa tu usuario"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Contraseña
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  className="block w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Ingresa tu contraseña"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center items-center px-4 py-3 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              ) : (
                <>
                  Iniciar Sesión
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </button>
          </form>

          {/* Credenciales del Sistema */}
          <div className="mt-8">
            <h3 className="text-sm font-medium text-gray-700 mb-4 text-center">
              Credenciales del Sistema
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {systemCredentials.map((cred, index) => (
                <button
                  key={index}
                  onClick={() => fillCredentials(cred.username, cred.password)}
                  className="flex items-center p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className={`w-8 h-8 ${cred.color} rounded-full flex items-center justify-center mr-3`}>
                    <cred.icon className="h-4 w-4 text-white" />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-900">{cred.role}</div>
                    <div className="text-xs text-gray-500">{cred.username}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Información adicional */}
          <div className="mt-8 text-center">
            <p className="text-xs text-gray-500">
              Sistema POS Sabrositas v2.0.0 - Enterprise Edition
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
