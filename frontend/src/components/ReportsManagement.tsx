/**
 * Gestión de Reportes Robusta - Sistema POS Sabrositas
 * Componente robusto que funciona con la infraestructura existente
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  FileText, Download, Calendar, TrendingUp, 
  Package, DollarSign, Coffee, RefreshCw, AlertCircle
} from 'lucide-react';
import { format, subDays } from 'date-fns';
import { es } from 'date-fns/locale';
import toast from 'react-hot-toast';
import {
  ResponsiveContainer, XAxis, YAxis, CartesianGrid,
  Tooltip, BarChart, Bar, AreaChart, Area
} from 'recharts';

// Tipos simplificados
interface ReportData {
  report_info?: {
    type: string;
    start_date: string;
    end_date: string;
    generated_at: string;
  };
  summary?: any;
  [key: string]: any;
}

interface DateRange {
  start: Date;
  end: Date;
}

const ReportsManagement: React.FC = () => {
  // Estados principales
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
    {
      id: 'sales',
      name: 'Reporte de Ventas',
      description: 'Análisis de ventas por período',
      icon: TrendingUp,
      color: 'bg-green-500'
    },
    {
      id: 'inventory',
      name: 'Reporte de Inventario',
      description: 'Estado actual del inventario',
      icon: Package,
      color: 'bg-blue-500'
    },
    {
      id: 'cash_flow',
      name: 'Flujo de Caja',
      description: 'Ingresos y balance',
      icon: DollarSign,
      color: 'bg-emerald-500'
    },
    {
      id: 'products',
      name: 'Rendimiento de Productos',
      description: 'Productos más vendidos',
      icon: Coffee,
      color: 'bg-amber-500'
    }
  ];

  // Cargar reporte inicial
  useEffect(() => {
    generateReport();
  }, [selectedReport]);

  const generateReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Usar endpoints que funcionan sin autenticación
      const API_BASE = '/api/v1/reports-final';
      
      let endpoint = '';
      const startDate = format(dateRange.start, 'yyyy-MM-dd');
      const endDate = format(dateRange.end, 'yyyy-MM-dd');
      
      // Construir endpoint según tipo usando la API que funciona
      switch (selectedReport) {
        case 'sales':
          endpoint = `${API_BASE}/sales?start_date=${startDate}&end_date=${endDate}&details=true`;
          break;
        case 'inventory':
          endpoint = `${API_BASE}/inventory?details=true`;
          break;
        case 'cash_flow':
          endpoint = `${API_BASE}/dashboard`;
          break;
        case 'products':
          endpoint = `${API_BASE}/products/performance?days=30&limit=20`;
          break;
        default:
          endpoint = `${API_BASE}/dashboard`;
      }
      
      // Los nuevos endpoints no requieren autenticación
      const response = await fetch(endpoint, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        setReportData(result.data);
        toast.success('Reporte generado exitosamente');
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
      // Usar endpoint de exportación que funciona
      const API_BASE = '/api/v1/reports-final';
      
      // Usar endpoint de exportación que funciona
      const startDate = format(dateRange.start, 'yyyy-MM-dd');
      const endDate = format(dateRange.end, 'yyyy-MM-dd');
      
      const response = await fetch(`${API_BASE}/export/sales?start_date=${startDate}&end_date=${endDate}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${selectedReport}_${format(new Date(), 'yyyyMMdd_HHmmss')}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        toast.success('Reporte descargado exitosamente');
      } else {
        toast.error('Error exportando reporte');
      }
      
    } catch (error) {
      console.error('Error exporting:', error);
      toast.error('Error exportando reporte');
    }
  };

  const renderSummaryCards = () => {
    if (!reportData?.summary) return null;

    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {Object.entries(reportData.summary).map(([key, value]) => (
          <div key={key} className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
            <div className="text-2xl font-bold text-amber-600">
              {typeof value === 'number' ? 
                (key.includes('revenue') || key.includes('total_amount') || key.includes('income') ? 
                  `$${value.toLocaleString()}` : 
                  value.toLocaleString()) : 
                String(value)}
            </div>
            <div className="text-sm text-gray-600 capitalize">
              {key.replace(/_/g, ' ')}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderChart = () => {
    if (!reportData) return null;

    // Gráfico para ventas diarias
    if (selectedReport === 'sales' && reportData.daily_sales) {
      return (
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Ventas Diarias</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={reportData.daily_sales}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(date) => format(new Date(date), 'dd/MM')}
              />
              <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />
              <Tooltip 
                labelFormatter={(date) => format(new Date(date), 'PPP', { locale: es })}
                formatter={(value: any) => [`$${value.toLocaleString()}`, 'Ingresos']}
              />
              <Area 
                type="monotone" 
                dataKey="revenue" 
                stroke="#f59e0b" 
                fill="#fef3c7" 
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      );
    }

    // Gráfico para productos top
    if (selectedReport === 'products' && reportData.top_products) {
      const chartData = reportData.top_products.slice(0, 5);
      return (
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top 5 Productos</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis />
              <Tooltip />
              <Bar dataKey="total_sold" fill="#f59e0b" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestión de Reportes</h1>
          <p className="text-gray-600 mt-1">Análisis y exportación de datos empresariales</p>
        </div>
        
        <div className="flex flex-col md:flex-row gap-3">
          {/* Selector de fechas */}
          <div className="flex items-center space-x-2 bg-white rounded-lg border border-gray-300 px-3 py-2">
            <Calendar className="h-4 w-4 text-gray-500" />
            <input
              type="date"
              value={format(dateRange.start, 'yyyy-MM-dd')}
              onChange={(e) => setDateRange({
                ...dateRange,
                start: new Date(e.target.value)
              })}
              className="border-none outline-none text-sm"
              title="Fecha de inicio del reporte"
              aria-label="Fecha de inicio del reporte"
            />
            <span className="text-gray-400">-</span>
            <input
              type="date"
              value={format(dateRange.end, 'yyyy-MM-dd')}
              onChange={(e) => setDateRange({
                ...dateRange,
                end: new Date(e.target.value)
              })}
              className="border-none outline-none text-sm"
              title="Fecha de fin del reporte"
              aria-label="Fecha de fin del reporte"
            />
          </div>
          
          {/* Botones de acción */}
          <button
            onClick={generateReport}
            disabled={loading}
            className="bg-amber-600 hover:bg-amber-700 disabled:bg-amber-400 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
            title="Actualizar reporte"
            aria-label="Actualizar reporte"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Actualizar</span>
          </button>
          
          <button
            onClick={exportToCsv}
            disabled={loading || !reportData}
            className="bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
            title="Exportar a CSV"
            aria-label="Exportar a CSV"
          >
            <Download className="h-4 w-4" />
            <span>CSV</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar - Tipos de reportes */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Tipos de Reportes</h2>
            
            <div className="space-y-2">
              {reportTypes.map((type) => {
                const Icon = type.icon;
                return (
                  <motion.button
                    key={type.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setSelectedReport(type.id)}
                    className={`w-full text-left p-4 rounded-lg border transition-all ${
                      selectedReport === type.id
                        ? 'border-amber-500 bg-amber-50 text-amber-700'
                        : 'border-gray-200 hover:border-amber-300 hover:bg-gray-50'
                    }`}
                    title={`Seleccionar ${type.name}`}
                    aria-label={`Seleccionar ${type.name}`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${type.color} text-white`}>
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-medium">{type.name}</h3>
                        <p className="text-xs text-gray-600 mt-1">{type.description}</p>
                      </div>
                    </div>
                  </motion.button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Contenido principal */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-xl shadow-lg p-6">
            {/* Header del reporte */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                {(() => {
                  const config = reportTypes.find(r => r.id === selectedReport);
                  const Icon = config?.icon || FileText;
                  return (
                    <>
                      <div className={`p-3 rounded-lg ${config?.color || 'bg-gray-500'} text-white`}>
                        <Icon className="h-6 w-6" />
                      </div>
                      <div>
                        <h2 className="text-xl font-semibold text-gray-900">
                          {config?.name || 'Reporte'}
                        </h2>
                        <p className="text-sm text-gray-600">
                          {format(dateRange.start, 'PPP', { locale: es })} - {format(dateRange.end, 'PPP', { locale: es })}
                        </p>
                      </div>
                    </>
                  );
                })()}
              </div>
            </div>

            {/* Contenido del reporte */}
            {loading && (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
                <span className="ml-3 text-gray-600">Generando reporte...</span>
              </div>
            )}

            {error && (
              <div className="flex items-center justify-center h-64">
                <div className="text-center">
                  <AlertCircle className="h-16 w-16 mx-auto mb-4 text-red-300" />
                  <p className="text-red-600 font-medium">{error}</p>
                  <button
                    onClick={generateReport}
                    className="mt-4 bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded-lg"
                  >
                    Reintentar
                  </button>
                </div>
              </div>
            )}

            {!loading && !error && !reportData && (
              <div className="text-center text-gray-500 py-12">
                <FileText className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <p>Selecciona un tipo de reporte para comenzar</p>
              </div>
            )}

            {!loading && !error && reportData && (
              <div className="space-y-6">
                {/* Resumen con tarjetas */}
                {renderSummaryCards()}
                
                {/* Gráfico */}
                {renderChart()}
                
                {/* Tabla de datos */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-3">Datos del Reporte</h4>
                  <div className="max-h-96 overflow-y-auto">
                    <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                      {JSON.stringify(reportData, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Accesos rápidos */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { 
            name: 'Ventas de Hoy', 
            action: () => {
              setDateRange({ start: new Date(), end: new Date() });
              setSelectedReport('sales');
            }
          },
          { 
            name: 'Ventas de la Semana', 
            action: () => {
              setDateRange({ start: subDays(new Date(), 7), end: new Date() });
              setSelectedReport('sales');
            }
          },
          { 
            name: 'Inventario Actual', 
            action: () => setSelectedReport('inventory')
          },
          { 
            name: 'Top Productos', 
            action: () => setSelectedReport('products')
          }
        ].map((quick, index) => (
          <button
            key={index}
            onClick={quick.action}
            className="bg-white rounded-lg border border-gray-200 p-4 text-left hover:border-amber-300 hover:bg-amber-50 transition-colors"
            title={`Acceso rápido: ${quick.name}`}
            aria-label={`Acceso rápido: ${quick.name}`}
          >
            <div className="font-medium text-gray-900">{quick.name}</div>
            <div className="text-sm text-gray-600 mt-1">Acceso rápido</div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ReportsManagement;