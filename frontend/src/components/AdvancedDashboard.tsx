/**
 * Dashboard Avanzado - Sistema POS Sabrositas
 * Componente principal con gráficos en tiempo real e insights de IA
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, TrendingDown, DollarSign, ShoppingCart, 
  Users, Package, AlertCircle, Brain, Zap,
  RefreshCw, Eye
} from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';
import toast from 'react-hot-toast';
import {
  SalesTrendChart,
  TopProductsChart,
  PaymentMethodsChart,
  RevenueChart,
  MetricCard,
  PerformanceChart
} from './ModernCharts';
// Tipos
interface DashboardMetrics {
  period: {
    start_date: string;
    end_date: string;
    days: number;
  };
  basic_metrics: {
    total_sales: number;
    total_revenue: number;
    average_sale: number;
    revenue_change: number;
    sales_change: number;
    products_sold: number;
  };
  sales_timeline: Array<{
    date: string;
    sales: number;
    revenue: number;
    day_name: string;
  }>;
  top_products: Array<{
    id: number;
    name: string;
    category: string;
    total_sold: number;
    total_revenue: number;
    times_sold: number;
  }>;
  payment_analysis: Array<{
    method: string;
    name: string;
    icon: string;
    total_sales: number;
    total_revenue: number;
    percentage: number;
  }>;
  category_analysis: Array<{
    category: string;
    total_sold: number;
    total_revenue: number;
    percentage: number;
    color: string;
  }>;
  ai_insights: {
    recommendations: Array<{
      type: string;
      message: string;
      confidence: number;
      product_id?: number;
    }>;
    predictions: {
      next_week_sales: number;
      estimated_revenue: number;
      confidence: number;
    };
    trends: Array<{
      type: string;
      message: string;
      impact: string;
    }>;
  };
  performance_metrics: {
    peak_hours: Array<{
      hour: number;
      sales: number;
      avg_amount: number;
    }>;
    product_rotation: number;
    avg_items_per_sale: number;
    customer_satisfaction_score: number;
  };
  last_updated: string;
}

const AdvancedDashboard: React.FC = () => {
  // Estados
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [periodDays, setPeriodDays] = useState(7);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedView, setSelectedView] = useState<'overview' | 'sales' | 'products' | 'ai'>('overview');
  
  // Hook de tema (comentado por ahora para evitar errores)
  // const { actualTheme } = useTheme();

  // Cargar datos del dashboard
  const fetchDashboardData = async (days: number = periodDays) => {
    try {
      setRefreshing(true);
      
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/analytics/dashboard?period_days=${days}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Error al cargar datos del dashboard');
      }

      const data = await response.json();
      setMetrics(data.data);
      setError(null);
      
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err instanceof Error ? err.message : 'Error desconocido');
      toast.error('Error al cargar el dashboard');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // Efecto para cargar datos iniciales
  useEffect(() => {
    fetchDashboardData();
    
    // Auto-refresh cada 5 minutos
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  // Manejar cambio de período
  const handlePeriodChange = (days: number) => {
    setPeriodDays(days);
    fetchDashboardData(days);
  };

  // Formatear moneda
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount);
  };

  // Formatear porcentaje
  const formatPercentage = (value: number) => {
    const sign = value > 0 ? '+' : '';
    return `${sign}${value.toFixed(1)}%`;
  };

  // Componente de métrica
  const MetricCard: React.FC<{
    title: string;
    value: string | number;
    change?: number;
    icon: React.ReactNode;
    color: string;
    subtitle?: string;
  }> = ({ title, value, change, icon, color, subtitle }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white rounded-xl shadow-lg p-6 border-l-4 border-${color}-500`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {subtitle && (
            <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`p-3 bg-${color}-100 rounded-full`}>
          <div className={`text-${color}-600`}>
            {icon}
          </div>
        </div>
      </div>
      
      {change !== undefined && (
        <div className="flex items-center mt-4">
          {change > 0 ? (
            <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
          ) : (
            <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
          )}
          <span className={`text-sm font-medium ${change > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatPercentage(change)}
          </span>
          <span className="text-sm text-gray-500 ml-1">vs período anterior</span>
        </div>
      )}
    </motion.div>
  );

  // Componente de insight de IA
  const AIInsightCard: React.FC<{
    insight: {
      type: string;
      message: string;
      confidence: number;
    };
  }> = ({ insight }) => {
    // Mapear niveles de confianza a clases CSS
    const getConfidenceClass = (confidence: number) => {
      const percentage = Math.round(confidence * 100);
      if (percentage >= 90) return 'w-11/12';
      if (percentage >= 80) return 'w-4/5';
      if (percentage >= 70) return 'w-3/4';
      if (percentage >= 60) return 'w-3/5';
      if (percentage >= 50) return 'w-1/2';
      if (percentage >= 40) return 'w-2/5';
      if (percentage >= 30) return 'w-1/3';
      if (percentage >= 20) return 'w-1/5';
      return 'w-1/12';
    };
    
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-200"
      >
        <div className="flex items-start space-x-3">
          <div className="p-2 bg-purple-100 rounded-full">
            <Brain className="h-4 w-4 text-purple-600" />
          </div>
          <div className="flex-1">
            <p className="text-sm text-gray-800">{insight.message}</p>
            <div className="flex items-center mt-2">
              <div className="flex-1 bg-gray-200 rounded-full h-2 relative">
                <div
                  className={`bg-purple-500 h-2 rounded-full transition-all duration-300 ${getConfidenceClass(insight.confidence)}`}
                />
              </div>
              <span className="text-xs text-gray-600 ml-2">
                {Math.round(insight.confidence * 100)}% confianza
              </span>
            </div>
          </div>
        </div>
      </motion.div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500"></div>
        <span className="ml-3 text-gray-600">Cargando dashboard avanzado...</span>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-red-800 mb-2">Error al cargar dashboard</h3>
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={() => fetchDashboardData()}
          className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
        >
          Reintentar
        </button>
      </div>
    );
  }

  const paymentMethodsData = metrics.payment_analysis.map(method => ({
    method: method.method || method.name,
    name: method.name || method.method,
    count: method.total_sales,
    total: method.total_revenue,
    percentage: method.percentage
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard Avanzado</h1>
          <p className="text-gray-600 mt-1">
            Análisis con IA • Última actualización: {format(parseISO(metrics.last_updated), 'PPp', { locale: es })}
          </p>
        </div>
        
        <div className="flex items-center space-x-3 mt-4 sm:mt-0">
          {/* Selector de período */}
          <select
            value={periodDays}
            onChange={(e) => handlePeriodChange(Number(e.target.value))}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            title="Seleccionar período de análisis"
            aria-label="Seleccionar período de análisis"
          >
            <option value={7}>Últimos 7 días</option>
            <option value={30}>Últimos 30 días</option>
            <option value={90}>Últimos 90 días</option>
          </select>
          
          {/* Botón de refresh */}
          <button
            onClick={() => fetchDashboardData()}
            disabled={refreshing}
            className="flex items-center space-x-2 bg-amber-600 hover:bg-amber-700 disabled:bg-amber-400 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Actualizar</span>
          </button>
        </div>
      </div>

      {/* Navegación de vistas */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {[
          { id: 'overview', name: 'Resumen', icon: Eye },
          { id: 'sales', name: 'Ventas', icon: TrendingUp },
          { id: 'products', name: 'Productos', icon: Package },
          { id: 'ai', name: 'IA Insights', icon: Brain }
        ].map((view) => (
          <button
            key={view.id}
            onClick={() => setSelectedView(view.id as any)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedView === view.id
                ? 'bg-white text-amber-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <view.icon className="h-4 w-4" />
            <span>{view.name}</span>
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {selectedView === 'overview' && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            {/* Métricas principales */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="Ventas Totales"
                value={metrics.basic_metrics.total_sales}
                change={metrics.basic_metrics.sales_change}
                icon={<ShoppingCart className="h-6 w-6" />}
                color="blue"
                subtitle={`${metrics.basic_metrics.products_sold} productos vendidos`}
              />
              
              <MetricCard
                title="Ingresos"
                value={formatCurrency(metrics.basic_metrics.total_revenue)}
                change={metrics.basic_metrics.revenue_change}
                icon={<DollarSign className="h-6 w-6" />}
                color="green"
              />
              
              <MetricCard
                title="Venta Promedio"
                value={formatCurrency(metrics.basic_metrics.average_sale)}
                icon={<TrendingUp className="h-6 w-6" />}
                color="amber"
              />
              
              <MetricCard
                title="Satisfacción"
                value={`${metrics.performance_metrics.customer_satisfaction_score}/5`}
                icon={<Users className="h-6 w-6" />}
                color="purple"
                subtitle="Score de clientes"
              />
            </div>

            {/* Gráfico de ventas en el tiempo - Moderno */}
            <SalesTrendChart data={metrics.sales_timeline} />

            {/* Análisis de métodos de pago - Moderno */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <PaymentMethodsChart data={paymentMethodsData} />

              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Categorías Más Vendidas
                </h3>
                <div className="space-y-3">
                  {metrics.category_analysis.slice(0, 5).map((category) => {
                    // Mapear colores a clases CSS
                    const getColorClass = (color: string) => {
                      const colorMap: Record<string, string> = {
                        '#10b981': 'bg-green-500',
                        '#f59e0b': 'bg-amber-500', 
                        '#8b5cf6': 'bg-purple-500',
                        '#3b82f6': 'bg-blue-500',
                        '#ef4444': 'bg-red-500',
                        '#6b7280': 'bg-gray-500'
                      };
                      return colorMap[color] || 'bg-gray-500';
                    };
                    
                    return (
                      <div key={category.category} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`w-4 h-4 rounded-full ${getColorClass(category.color)}`} />
                          <span className="text-sm font-medium text-gray-900">
                            {category.category}
                          </span>
                          </div>
                        <div className="text-right">
                          <p className="text-sm font-semibold text-gray-900">
                            {formatCurrency(category.total_revenue)}
                          </p>
                          <p className="text-xs text-gray-500">
                            {category.total_sold} unidades
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Productos Más Vendidos - Moderno */}
            <TopProductsChart data={metrics.top_products} />
          </motion.div>
        )}

        {selectedView === 'ai' && (
          <motion.div
            key="ai"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            {/* Predicciones de IA */}
            <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center space-x-3 mb-4">
                <Brain className="h-8 w-8" />
                <h3 className="text-xl font-bold">Predicciones de IA</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <p className="text-purple-100 text-sm">Ventas Próxima Semana</p>
                  <p className="text-2xl font-bold">{metrics.ai_insights.predictions.next_week_sales}</p>
                  <p className="text-purple-200 text-sm">
                    Confianza: {Math.round(metrics.ai_insights.predictions.confidence * 100)}%
                  </p>
                </div>
                <div>
                  <p className="text-purple-100 text-sm">Ingresos Estimados</p>
                  <p className="text-2xl font-bold">
                    {formatCurrency(metrics.ai_insights.predictions.estimated_revenue)}
                  </p>
                  <p className="text-purple-200 text-sm">Basado en tendencias actuales</p>
                </div>
              </div>
            </div>

            {/* Recomendaciones */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Recomendaciones Inteligentes
              </h3>
              <div className="space-y-4">
                {metrics.ai_insights.recommendations.map((rec, index) => (
                  <AIInsightCard key={index} insight={rec} />
                ))}
              </div>
            </div>

            {/* Tendencias */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Tendencias Identificadas
              </h3>
              <div className="space-y-3">
                {metrics.ai_insights.trends.map((trend, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                    <Zap className={`h-5 w-5 mt-0.5 ${
                      trend.impact === 'positive' ? 'text-green-500' : 'text-red-500'
                    }`} />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{trend.message}</p>
                      <span className={`inline-block px-2 py-1 text-xs rounded-full mt-1 ${
                        trend.impact === 'positive' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {trend.impact === 'positive' ? 'Positivo' : 'Negativo'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AdvancedDashboard;
