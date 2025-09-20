/**
 * Gestión de Reportes Corregida - Sistema POS Sabrositas
 * Versión que funciona con los endpoints reparados
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Download, RefreshCw, BarChart3, Package, TrendingUp, DollarSign, AlertCircle } from 'lucide-react';
import { format, subDays } from 'date-fns';
import { es } from 'date-fns/locale';
import toast from 'react-hot-toast';
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  PieChart, Pie, Cell} from 'recharts';
import { useTheme } from '../context/ThemeContext';

interface ReportData {
  summary?: any;
  sales_metrics?: any;
  inventory_metrics?: any;
  analytics?: any;
  products?: any[];
  [key: string]: any;
}

interface DateRange {
  start: Date;
  end: Date;
}

const ReportsManagementFixed: React.FC = () => {
  // Estados
  const [selectedReport, setSelectedReport] = useState<string>('sales');
  const [dateRange, setDateRange] = useState<DateRange>({
    start: subDays(new Date(), 30),
    end: new Date()
  });
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Configuración de reportes
  const reportTypes = [
    { id: 'sales', name: 'Ventas', icon: DollarSign, color: 'text-green-600' },
    { id: 'inventory', name: 'Inventario', icon: Package, color: 'text-blue-600' },
    { id: 'dashboard', name: 'Dashboard', icon: BarChart3, color: 'text-purple-600' },
    { id: 'products', name: 'Productos', icon: TrendingUp, color: 'text-orange-600' }
  ];

  // API Base - Usar endpoints que funcionan
  const API_BASE = '/api/v1/reports-final';

  const generateReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let endpoint = '';
      const startDate = format(dateRange.start, 'yyyy-MM-dd');
      const endDate = format(dateRange.end, 'yyyy-MM-dd');
      
      // Construir endpoint según tipo
      switch (selectedReport) {
        case 'sales':
          endpoint = `${API_BASE}/sales?start_date=${startDate}&end_date=${endDate}&details=true`;
          break;
        case 'inventory':
          endpoint = `${API_BASE}/inventory?details=true`;
          break;
        case 'dashboard':
          endpoint = `${API_BASE}/dashboard`;
          break;
        case 'products':
          endpoint = `${API_BASE}/products/performance?days=30&limit=20`;
          break;
        default:
          endpoint = `${API_BASE}/dashboard`;
      }
      
      const response = await fetch(endpoint);
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setReportData(result.data);
          toast.success(result.message || 'Reporte generado exitosamente');
        } else {
          setError(result.error || 'Error en la respuesta');
          toast.error(result.error || 'Error generando reporte');
        }
      } else {
        const errorData = await response.json().catch(() => ({ error: 'Error desconocido' }));
        setError(errorData.error || `Error ${response.status}`);
        toast.error(errorData.error || 'Error generando reporte');
      }
      
    } catch (error) {
      console.error('Error generating report:', error);
      setError('Error de conexión');
      toast.error('Error de conexión al servidor');
    } finally {
      setLoading(false);
    }
  };

  const exportToCsv = async () => {
    try {
      const startDate = format(dateRange.start, 'yyyy-MM-dd');
      const endDate = format(dateRange.end, 'yyyy-MM-dd');
      
      const response = await fetch(`${API_BASE}/export/sales?start_date=${startDate}&end_date=${endDate}`);
      
      if (response.ok) {
        const result = await response.json();
        if (result.success && result.data.csv_content) {
          // Crear blob con el contenido CSV
          const blob = new Blob([result.data.csv_content], { type: 'text/csv;charset=utf-8;' });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.style.display = 'none';
          a.href = url;
          a.download = result.data.filename || `reporte_${format(new Date(), 'yyyy-MM-dd')}.csv`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
          toast.success(`✅ Exportado: ${result.data.records_count} registros`);
        } else {
          toast.error('Error en el formato de exportación');
        }
      } else {
        toast.error('Error exportando reporte');
      }
    } catch (err) {
      console.error('Error exporting:', err);
      toast.error('Error de conexión al exportar');
    }
  };

  // Cargar reporte inicial
  useEffect(() => {
    generateReport();
  }, [selectedReport, dateRange]);

  // Funciones de renderizado
  const renderSalesChart = () => {
    if (!reportData?.analytics?.daily_breakdown) return null;

    const chartData = Object.entries(reportData.analytics.daily_breakdown).map(([date, data]: [string, any]) => ({
      date: format(new Date(date), 'dd/MM', { locale: es }),
      ventas: data.count,
      ingresos: data.total
    }));

    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
          Tendencia de Ventas
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="ingresos" stackId="1" stroke="#f59e0b" fill="#fbbf24" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderPaymentMethodsChart = () => {
    if (!reportData?.analytics?.payment_methods) return null;

    const chartData = Object.entries(reportData.analytics.payment_methods).map(([method, data]: [string, any]) => ({
      name: method,
      value: data.total,
      count: data.count
    }));

    const COLORS = ['#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ef4444'];

    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
          Métodos de pago
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${((percent as number) * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, _index) => (
                <Cell key={`cell-${_index}`} fill={COLORS[_index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value: any) => [`$${value.toLocaleString()}`, 'Total']} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderSummaryCards = () => {
    const summary = reportData?.summary || reportData?.sales_metrics || {};
    
    const cards = [
      {
        title: 'Total Ventas',
        value: summary.total_sales || summary.today?.count || 0,
        icon: BarChart3,
        color: 'text-blue-600 dark:text-blue-400',
        bgColor: 'bg-blue-50 dark:bg-blue-900/20',
        titleColor: 'text-blue-800 dark:text-blue-200',
        valueColor: 'text-blue-900 dark:text-blue-100'
      },
      {
        title: 'Ingresos',
        value: `$${(summary.total_revenue || summary.today?.total || 0).toLocaleString()}`,
        icon: DollarSign,
        color: 'text-green-600 dark:text-green-400',
        bgColor: 'bg-green-50 dark:bg-green-900/20',
        titleColor: 'text-green-800 dark:text-green-200',
        valueColor: 'text-green-900 dark:text-green-100'
      },
      {
        title: 'Promedio',
        value: `$${(summary.average_sale || 0).toLocaleString()}`,
        icon: TrendingUp,
        color: 'text-purple-600 dark:text-purple-400',
        bgColor: 'bg-purple-50 dark:bg-purple-900/20',
        titleColor: 'text-purple-800 dark:text-purple-200',
        valueColor: 'text-purple-900 dark:text-purple-100'
      },
      {
        title: 'Productos',
        value: reportData?.inventory_metrics?.total_products || summary.total_products || 0,
        icon: Package,
        color: 'text-orange-600 dark:text-orange-400',
        bgColor: 'bg-orange-50 dark:bg-orange-900/20',
        titleColor: 'text-orange-800 dark:text-orange-200',
        valueColor: 'text-orange-900 dark:text-orange-100'
      }
    ];

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {cards.map((card, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`${card.bgColor} p-6 rounded-lg shadow-sm`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm font-medium ${card.titleColor}`}>
                  {card.title}
                </p>
                <p className={`text-2xl font-bold ${card.valueColor}`}>
                  {card.value}
                </p>
              </div>
              <card.icon className={`h-8 w-8 ${card.color}`} />
            </div>
          </motion.div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              📊 Reportes del Sistema
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Análisis y estadísticas de tu negocio
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Selector de tipo de reporte */}
            <select
              value={selectedReport}
              onChange={(e) => setSelectedReport(e.target.value)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                         bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                         focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              title="Seleccionar tipo de reporte"
              aria-label="Seleccionar tipo de reporte"
            >
              {reportTypes.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </select>

            {/* Selector de fechas */}
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-gray-500" />
              <input
                type="date"
                value={format(dateRange.start, 'yyyy-MM-dd')}
                onChange={(e) => setDateRange({
                  ...dateRange,
                  start: new Date(e.target.value)
                })}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                title="Fecha de inicio"
                aria-label="Fecha de inicio"
              />
              <span className="text-gray-500">-</span>
              <input
                type="date"
                value={format(dateRange.end, 'yyyy-MM-dd')}
                onChange={(e) => setDateRange({
                  ...dateRange,
                  end: new Date(e.target.value)
                })}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                title="Fecha de fin"
                aria-label="Fecha de fin"
              />
            </div>

            {/* Botones de acción */}
            <button
              onClick={generateReport}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 
                         text-white rounded-lg transition-colors disabled:opacity-50"
              title="Generar reporte"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Generando...' : 'Actualizar'}
            </button>

            <button
              onClick={exportToCsv}
              disabled={loading || !reportData}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 
                         text-white rounded-lg transition-colors disabled:opacity-50"
              title="Exportar a CSV"
            >
              <Download className="h-4 w-4" />
              Exportar CSV
            </button>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 
                     rounded-lg p-4"
        >
          <div className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <p className="text-red-800 dark:text-red-200">{error}</p>
          </div>
        </motion.div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center gap-3">
            <RefreshCw className="h-6 w-6 animate-spin text-amber-600" />
            <span className="text-gray-600 dark:text-gray-300">Generando reporte...</span>
          </div>
        </div>
      )}

      {/* Contenido del reporte */}
      {!loading && reportData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Tarjetas de resumen */}
          {renderSummaryCards()}

          {/* Gráficos */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {selectedReport === 'sales' && (
              <>
                {renderSalesChart()}
                {renderPaymentMethodsChart()}
              </>
            )}
            
            {selectedReport === 'inventory' && reportData.categories && (
              <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm lg:col-span-2">
                <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                  Inventario por Categorías
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(reportData.categories).map(([category, data]: [string, any]) => (
                    <div key={category} className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
                      <h4 className="font-medium text-gray-900 dark:text-white">{category}</h4>
                      <p className="text-sm text-gray-700 dark:text-gray-200">
                        {data.product_count} productos
                      </p>
                      <p className="text-sm text-gray-700 dark:text-gray-200">
                        {data.total_stock} unidades
                      </p>
                      <p className="text-sm font-medium text-green-700 dark:text-green-400">
                        ${(data.total_value || 0).toLocaleString()}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedReport === 'products' && reportData.products && (
              <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm lg:col-span-2">
                <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                  Productos Más Vendidos
                </h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead>
                      <tr className="border-b border-gray-200 dark:border-gray-700">
                        <th className="text-left py-2 text-gray-800 dark:text-gray-100 font-semibold">Producto</th>
                        <th className="text-left py-2 text-gray-800 dark:text-gray-100 font-semibold">Categoría</th>
                        <th className="text-right py-2 text-gray-800 dark:text-gray-100 font-semibold">Vendidos</th>
                        <th className="text-right py-2 text-gray-800 dark:text-gray-100 font-semibold">Ingresos</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reportData.products.slice(0, 10).map((product: any, index: number) => (
                        <tr key={index} className="border-b border-gray-100 dark:border-gray-700">
                          <td className="py-2 text-gray-800 dark:text-gray-100 font-medium">{product.name}</td>
                          <td className="py-2 text-gray-700 dark:text-gray-200">{product.category}</td>
                          <td className="py-2 text-right text-gray-800 dark:text-gray-100 font-medium">
                            {product.quantity_sold}
                          </td>
                          <td className="py-2 text-right text-green-700 dark:text-green-400 font-semibold">
                            ${(product.revenue || 0).toLocaleString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          {/* Información adicional */}
          {reportData && (
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
              <p className="text-sm text-gray-700 dark:text-gray-200 font-medium">
                📊 Reporte generado exitosamente • 
                {selectedReport === 'sales' && reportData.summary && (
                  ` ${reportData.summary.total_sales} ventas • $${reportData.summary.total_revenue?.toLocaleString()}`
                )}
                {selectedReport === 'inventory' && reportData.summary && (
                  ` ${reportData.summary.total_products} productos • $${reportData.summary.total_inventory_value?.toLocaleString()}`
                )}
                {selectedReport === 'dashboard' && reportData.sales_metrics && (
                  ` ${reportData.sales_metrics.today.count} ventas hoy • $${reportData.sales_metrics.today.total?.toLocaleString()}`
                )}
              </p>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default ReportsManagementFixed;
