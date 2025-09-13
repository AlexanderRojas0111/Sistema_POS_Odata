import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  ShoppingCart, 
  Users, 
  Package, 
  DollarSign, 
  TrendingUp, 
  TrendingDown,
  Eye,
  Plus,
  BarChart3,
  PieChart,
  Activity
} from 'lucide-react';

interface DashboardStats {
  totalSales: number;
  totalRevenue: number;
  totalProducts: number;
  totalUsers: number;
  todaySales: number;
  todayRevenue: number;
  lowStockProducts: number;
  activeUsers: number;
}

interface RecentSale {
  id: number;
  user_name: string;
  total: number;
  created_at: string;
  items_count: number;
}

interface TopProduct {
  id: number;
  name: string;
  sales_count: number;
  revenue: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentSales, setRecentSales] = useState<RecentSale[]>([]);
  const [topProducts, setTopProducts] = useState<TopProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<'today' | 'week' | 'month'>('today');

  // Obtener token de autenticación
  const getAuthToken = () => {
    return localStorage.getItem('token');
  };

  // Cargar estadísticas del dashboard
  const loadDashboardStats = async () => {
    try {
      const token = getAuthToken();
      if (!token) {
        setError('No autorizado. Por favor, inicia sesión.');
        return;
      }

      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Cargar estadísticas de ventas
      const salesResponse = await fetch('http://localhost:8000/api/v1/sales/stats', {
        headers
      });

      // Cargar estadísticas de productos
      const productsResponse = await fetch('http://localhost:8000/api/v1/products/stats', {
        headers
      });

      // Cargar estadísticas de usuarios
      const usersResponse = await fetch('http://localhost:8000/api/v1/users/stats', {
        headers
      });

      if (salesResponse.ok && productsResponse.ok && usersResponse.ok) {
        const salesData = await salesResponse.json();
        const productsData = await productsResponse.json();
        const usersData = await usersResponse.json();

        // Combinar estadísticas
        const dashboardStats: DashboardStats = {
          totalSales: salesData.data?.total_sales || 0,
          totalRevenue: salesData.data?.total_revenue || 0,
          totalProducts: productsData.data?.total_products || 0,
          totalUsers: usersData.data?.total_users || 0,
          todaySales: salesData.data?.today_sales || 0,
          todayRevenue: salesData.data?.today_revenue || 0,
          lowStockProducts: productsData.data?.low_stock_count || 0,
          activeUsers: usersData.data?.active_users || 0
        };

        setStats(dashboardStats);
      }

      // Cargar ventas recientes
      const recentSalesResponse = await fetch('http://localhost:8000/api/v1/sales?limit=5', {
        headers
      });

      if (recentSalesResponse.ok) {
        const recentSalesData = await recentSalesResponse.json();
        setRecentSales(recentSalesData.data?.sales || []);
      }

    } catch (err) {
      console.error('Error cargando estadísticas:', err);
      setError('Error cargando estadísticas del dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardStats();
  }, [selectedPeriod]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.href = '/login'}
            className="btn-primary"
          >
            Ir al Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard POS</h1>
              <p className="text-gray-600 mt-1">Panel de control Sabrositas</p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value as any)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sabrositas-primary focus:border-transparent"
              >
                <option value="today">Hoy</option>
                <option value="week">Esta semana</option>
                <option value="month">Este mes</option>
              </select>
              <button
                onClick={loadDashboardStats}
                className="btn-primary flex items-center space-x-2"
              >
                <Activity className="w-4 h-4" />
                <span>Actualizar</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl shadow-amber p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Ventas Totales</p>
                <p className="text-3xl font-bold text-gray-900">{stats?.totalSales || 0}</p>
                <p className="text-sm text-green-600 flex items-center mt-1">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  +12% vs mes anterior
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-amber rounded-xl flex items-center justify-center">
                <ShoppingCart className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-xl shadow-amber p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Ingresos Totales</p>
                <p className="text-3xl font-bold text-gray-900">
                  {formatCurrency(stats?.totalRevenue || 0)}
                </p>
                <p className="text-sm text-green-600 flex items-center mt-1">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  +8% vs mes anterior
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-amber rounded-xl flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-xl shadow-amber p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Productos</p>
                <p className="text-3xl font-bold text-gray-900">{stats?.totalProducts || 0}</p>
                <p className="text-sm text-orange-600 flex items-center mt-1">
                  <Package className="w-4 h-4 mr-1" />
                  {stats?.lowStockProducts || 0} bajo stock
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-amber rounded-xl flex items-center justify-center">
                <Package className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-xl shadow-amber p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Usuarios</p>
                <p className="text-3xl font-bold text-gray-900">{stats?.totalUsers || 0}</p>
                <p className="text-sm text-blue-600 flex items-center mt-1">
                  <Users className="w-4 h-4 mr-1" />
                  {stats?.activeUsers || 0} activos
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-amber rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>
        </div>

        {/* Charts and Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Sales */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-xl shadow-amber p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-gray-900">Ventas Recientes</h3>
              <button className="text-sabrositas-primary hover:text-sabrositas-accent flex items-center space-x-1">
                <Eye className="w-4 h-4" />
                <span>Ver todas</span>
              </button>
            </div>
            <div className="space-y-4">
              {recentSales.length > 0 ? (
                recentSales.map((sale, index) => (
                  <div key={sale.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-gradient-amber rounded-lg flex items-center justify-center">
                        <span className="text-white font-bold text-sm">#{sale.id}</span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{sale.user_name}</p>
                        <p className="text-sm text-gray-600">{sale.items_count} productos</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-gray-900">{formatCurrency(sale.total)}</p>
                      <p className="text-sm text-gray-600">{formatDate(sale.created_at)}</p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <ShoppingCart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No hay ventas recientes</p>
                </div>
              )}
            </div>
          </motion.div>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-xl shadow-amber p-6"
          >
            <h3 className="text-xl font-bold text-gray-900 mb-6">Acciones Rápidas</h3>
            <div className="grid grid-cols-2 gap-4">
              <button className="p-4 bg-gradient-amber text-white rounded-lg hover:shadow-amber-lg transition-all duration-300 transform hover:-translate-y-1">
                <Plus className="w-6 h-6 mx-auto mb-2" />
                <p className="font-medium">Nueva Venta</p>
              </button>
              <button className="p-4 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-all duration-300 transform hover:-translate-y-1">
                <Package className="w-6 h-6 mx-auto mb-2" />
                <p className="font-medium">Agregar Producto</p>
              </button>
              <button className="p-4 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-all duration-300 transform hover:-translate-y-1">
                <Users className="w-6 h-6 mx-auto mb-2" />
                <p className="font-medium">Gestionar Usuarios</p>
              </button>
              <button className="p-4 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-all duration-300 transform hover:-translate-y-1">
                <BarChart3 className="w-6 h-6 mx-auto mb-2" />
                <p className="font-medium">Ver Reportes</p>
              </button>
            </div>
          </motion.div>
        </div>

        {/* Today's Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-8 bg-white rounded-xl shadow-amber p-6"
        >
          <h3 className="text-xl font-bold text-gray-900 mb-6">Resumen del Día</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <ShoppingCart className="w-8 h-8 text-green-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900">{stats?.todaySales || 0}</p>
              <p className="text-gray-600">Ventas Hoy</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <DollarSign className="w-8 h-8 text-blue-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(stats?.todayRevenue || 0)}
              </p>
              <p className="text-gray-600">Ingresos Hoy</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Package className="w-8 h-8 text-orange-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900">{stats?.lowStockProducts || 0}</p>
              <p className="text-gray-600">Productos Bajo Stock</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
