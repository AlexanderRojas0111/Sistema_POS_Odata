import React, { useState, useEffect } from 'react'
import { Download, FileSpreadsheet, TrendingUp, Package, DollarSign, BarChart3 } from 'lucide-react'
import '../styles/accessibility.css'

interface ReportData {
  success: boolean
  data: any
  message: string
}

interface SalesAnalytics {
  summary: {
    total_sales: number
    total_revenue: number
    average_sale: number
    growth_rate: number
    period: {
      start: string
      end: string
      days: number
      group_by: string
    }
  }
  analytics: {
    temporal_breakdown: Array<{
      period: string
      sales: number
      revenue: number
      percentage: number
    }>
    payment_methods: Array<{
      method: string
      count: number
      total: number
      percentage: number
    }>
    top_sellers: Array<{
      seller: string
      sales: number
      revenue: number
    }>
  }
  charts?: any
}

interface InventoryAnalytics {
  summary: {
    total_products: number
    total_stock_units: number
    total_inventory_value: number
    categories_count: number
    alerts_count: {
      low_stock: number
      out_of_stock: number
      overstock: number
    }
  }
  categories_analysis: Array<{
    category: string
    product_count: number
    total_stock: number
    total_value: number
    low_stock_items: number
    out_of_stock_items: number
    percentage_of_total: number
  }>
  stock_alerts: {
    low_stock: Array<any>
    out_of_stock: Array<any>
    overstock: Array<any>
  }
  recommendations: Array<{
    type: string
    priority: string
    message: string
  }>
}

export const ReportsEnhanced: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'sales' | 'inventory' | 'dashboard'>('sales')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Filtros
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [groupBy, setGroupBy] = useState('day')
  
  // Datos
  const [salesData, setSalesData] = useState<SalesAnalytics | null>(null)
  const [inventoryData, setInventoryData] = useState<InventoryAnalytics | null>(null)
  const [dashboardData, setDashboardData] = useState<any>(null)

  // Configurar fechas por defecto
  useEffect(() => {
    const today = new Date()
    const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
    
    setEndDate(today.toISOString().split('T')[0])
    setStartDate(thirtyDaysAgo.toISOString().split('T')[0])
  }, [])

  const fetchSalesAnalytics = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
        group_by: groupBy,
        charts: 'true'
      })
      
      const response = await fetch(`http://localhost:8000/api/v1/reports-enhanced/sales/analytics?${params}`)
      const data: ReportData = await response.json()
      
      if (data.success) {
        setSalesData(data.data)
      } else {
        setError('Error cargando datos de ventas')
      }
    } catch (err) {
      setError('Error de conexión')
      console.error('Error fetching sales analytics:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchInventoryAnalytics = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        details: 'true'
      })
      
      const response = await fetch(`http://localhost:8000/api/v1/reports-enhanced/inventory/analytics?${params}`)
      const data: ReportData = await response.json()
      
      if (data.success) {
        setInventoryData(data.data)
      } else {
        setError('Error cargando datos de inventario')
      }
    } catch (err) {
      setError('Error de conexión')
      console.error('Error fetching inventory analytics:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchDashboard = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/reports-enhanced/dashboard/comprehensive')
      const data: ReportData = await response.json()
      
      if (data.success) {
        setDashboardData(data.data)
      } else {
        setError('Error cargando dashboard')
      }
    } catch (err) {
      setError('Error de conexión')
      console.error('Error fetching dashboard:', err)
    } finally {
      setLoading(false)
    }
  }

  const exportToExcel = async (type: 'sales' | 'inventory') => {
    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate
      })
      
      const response = await fetch(`http://localhost:8000/api/v1/reports-enhanced/export/${type}/excel?${params}`)
      const data = await response.json()
      
      if (data.success) {
        // Crear y descargar archivo
        const blob = new Blob([data.data.file_content], { 
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
        })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = data.data.filename
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        setError('Error exportando archivo')
      }
    } catch (err) {
      setError('Error de conexión al exportar')
      console.error('Error exporting to Excel:', err)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('es-CO').format(num)
  }

  useEffect(() => {
    if (activeTab === 'sales') {
      fetchSalesAnalytics()
    } else if (activeTab === 'inventory') {
      fetchInventoryAnalytics()
    } else if (activeTab === 'dashboard') {
      fetchDashboard()
    }
  }, [activeTab, startDate, endDate, groupBy])

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Reportes Avanzados
          </h1>
          <p className="text-gray-600">
            Análisis detallado y exportación a Excel del sistema POS
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'sales', label: 'Ventas', icon: TrendingUp },
                { id: 'inventory', label: 'Inventario', icon: Package },
                { id: 'dashboard', label: 'Dashboard', icon: BarChart3 }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Filtros */}
        {activeTab === 'sales' && (
          <div className="bg-white p-4 rounded-lg shadow-sm mb-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label htmlFor="startDateOriginal" className="block text-sm font-medium text-gray-700 mb-1">
                  Fecha Inicio
                </label>
                <input
                  id="startDateOriginal"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label="Seleccionar fecha de inicio para el reporte"
                  title="Selecciona la fecha de inicio para filtrar los datos"
                />
              </div>
              <div>
                <label htmlFor="endDateOriginal" className="block text-sm font-medium text-gray-700 mb-1">
                  Fecha Fin
                </label>
                <input
                  id="endDateOriginal"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label="Seleccionar fecha de fin para el reporte"
                  title="Selecciona la fecha de fin para filtrar los datos"
                />
              </div>
              <div>
                <label htmlFor="groupByOriginal" className="block text-sm font-medium text-gray-700 mb-1">
                  Agrupar por
                </label>
                <select
                  id="groupByOriginal"
                  value={groupBy}
                  onChange={(e) => setGroupBy(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label="Seleccionar criterio de agrupación de datos"
                  title="Selecciona cómo agrupar los datos del reporte"
                >
                  <option value="day">Día</option>
                  <option value="hour">Hora</option>
                  <option value="week">Semana</option>
                  <option value="month">Mes</option>
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={fetchSalesAnalytics}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Cargando...' : 'Actualizar'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Contenido */}
        {activeTab === 'sales' && salesData && (
          <div className="space-y-6">
            {/* Resumen */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <DollarSign className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Ventas Totales</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatNumber(salesData.summary.total_sales)}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Ingresos</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(salesData.summary.total_revenue)}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <BarChart3 className="w-6 h-6 text-yellow-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Promedio</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(salesData.summary.average_sale)}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Crecimiento</p>
                    <p className={`text-2xl font-bold ${salesData.summary.growth_rate >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {salesData.summary.growth_rate >= 0 ? '+' : ''}{salesData.summary.growth_rate.toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Exportar */}
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">Exportar Datos</h3>
                <button
                  onClick={() => exportToExcel('sales')}
                  className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
                >
                  <FileSpreadsheet className="w-4 h-4" />
                  <span>Exportar a Excel</span>
                </button>
              </div>
            </div>

            {/* Métodos de Pago */}
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Análisis por Método de Pago</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Método
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Transacciones
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Total
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Porcentaje
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {salesData.analytics.payment_methods.map((method, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {method.method}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatNumber(method.count)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatCurrency(method.total)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {method.percentage.toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Top Vendedores */}
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Top Vendedores</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Vendedor
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Ventas
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Ingresos
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {salesData.analytics.top_sellers.map((seller, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {seller.seller}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatNumber(seller.sales)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatCurrency(seller.revenue)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'inventory' && inventoryData && (
          <div className="space-y-6">
            {/* Resumen de Inventario */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Package className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Productos</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatNumber(inventoryData.summary.total_products)}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <DollarSign className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Valor Total</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(inventoryData.summary.total_inventory_value)}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <Package className="w-6 h-6 text-yellow-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Stock Bajo</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {inventoryData.summary.alerts_count.low_stock}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <div className="flex items-center">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <Package className="w-6 h-6 text-red-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Sin Stock</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {inventoryData.summary.alerts_count.out_of_stock}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Exportar */}
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">Exportar Inventario</h3>
                <button
                  onClick={() => exportToExcel('inventory')}
                  className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
                >
                  <FileSpreadsheet className="w-4 h-4" />
                  <span>Exportar a Excel</span>
                </button>
              </div>
            </div>

            {/* Alertas */}
            {inventoryData.recommendations.length > 0 && (
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Alertas y Recomendaciones</h3>
                <div className="space-y-3">
                  {inventoryData.recommendations.map((rec, index) => (
                    <div
                      key={index}
                      className={`p-4 rounded-lg border-l-4 ${
                        rec.priority === 'high'
                          ? 'bg-red-50 border-red-400'
                          : rec.priority === 'medium'
                          ? 'bg-yellow-50 border-yellow-400'
                          : 'bg-blue-50 border-blue-400'
                      }`}
                    >
                      <p className={`font-medium ${
                        rec.priority === 'high'
                          ? 'text-red-800'
                          : rec.priority === 'medium'
                          ? 'text-yellow-800'
                          : 'text-blue-800'
                      }`}>
                        {rec.message}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Análisis por Categoría */}
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Análisis por Categoría</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Categoría
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Productos
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Stock
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Valor
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        % Total
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {inventoryData.categories_analysis.map((category, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {category.category}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatNumber(category.product_count)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatNumber(category.total_stock)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatCurrency(category.total_value)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {category.percentage_of_total.toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'dashboard' && dashboardData && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Métricas del día */}
              <div className="bg-white p-6 rounded-lg shadow-sm">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Hoy</h3>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">
                    Ventas: <span className="font-bold">{formatNumber(dashboardData.period_comparison.today.sales)}</span>
                  </p>
                  <p className="text-sm text-gray-600">
                    Ingresos: <span className="font-bold">{formatCurrency(dashboardData.period_comparison.today.revenue)}</span>
                  </p>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Ayer</h3>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">
                    Ventas: <span className="font-bold">{formatNumber(dashboardData.period_comparison.yesterday.sales)}</span>
                  </p>
                  <p className="text-sm text-gray-600">
                    Ingresos: <span className="font-bold">{formatCurrency(dashboardData.period_comparison.yesterday.revenue)}</span>
                  </p>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Esta Semana</h3>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">
                    Ventas: <span className="font-bold">{formatNumber(dashboardData.period_comparison.week.sales)}</span>
                  </p>
                  <p className="text-sm text-gray-600">
                    Ingresos: <span className="font-bold">{formatCurrency(dashboardData.period_comparison.week.revenue)}</span>
                  </p>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-sm">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Este Mes</h3>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">
                    Ventas: <span className="font-bold">{formatNumber(dashboardData.period_comparison.month.sales)}</span>
                  </p>
                  <p className="text-sm text-gray-600">
                    Ingresos: <span className="font-bold">{formatCurrency(dashboardData.period_comparison.month.revenue)}</span>
                  </p>
                </div>
              </div>
            </div>

            {/* Inventario */}
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Resumen de Inventario</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <p className="text-sm text-gray-600">Total Productos</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatNumber(dashboardData.inventory_overview.total_products)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Valor Total</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(dashboardData.inventory_overview.total_value)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Alertas de Stock</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboardData.inventory_overview.low_stock_alerts}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2 text-gray-600">Cargando datos...</span>
          </div>
        )}
      </div>
    </div>
  )
}
