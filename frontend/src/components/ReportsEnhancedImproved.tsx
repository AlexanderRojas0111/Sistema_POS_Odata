import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { 
  Download, 
  FileSpreadsheet, 
  TrendingUp, 
  Package, 
  DollarSign, 
  BarChart3,
  Calendar,
  RefreshCw,
  CreditCard,
  Banknote,
  Smartphone,
  Wallet,
  AlertTriangle,
  CheckCircle,
  Clock,
  Users
} from 'lucide-react'
import '../styles/accessibility.css'

interface ReportData {
  success: boolean
  data: any
  message: string
}

interface PaymentMethodInfo {
  name: string
  icon: React.ComponentType<any>
  description: string
  color: string
  bgColor: string
}

// Información detallada de métodos de pago
const PAYMENT_METHODS_INFO: Record<string, PaymentMethodInfo> = {
  'cash': {
    name: 'Efectivo',
    icon: Banknote,
    description: 'Pagos en billetes y monedas físicas',
    color: 'text-green-600',
    bgColor: 'bg-green-50'
  },
  'Efectivo': {
    name: 'Efectivo',
    icon: Banknote,
    description: 'Pagos en billetes y monedas físicas',
    color: 'text-green-600',
    bgColor: 'bg-green-50'
  },
  'multi_payment': {
    name: 'Pago Múltiple',
    icon: CreditCard,
    description: 'Combinación de múltiples métodos de pago',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50'
  },
  'Tarjeta Débito': {
    name: 'Tarjeta Débito',
    icon: CreditCard,
    description: 'Pagos con tarjeta débito bancaria',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50'
  },
  'Tarjeta Crédito': {
    name: 'Tarjeta Crédito',
    icon: CreditCard,
    description: 'Pagos con tarjeta de crédito',
    color: 'text-purple-600',
    bgColor: 'bg-purple-50'
  },
  'Transferencia': {
    name: 'Transferencia',
    icon: Banknote,
    description: 'Transferencias bancarias electrónicas',
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50'
  },
  'nequi': {
    name: 'Nequi',
    icon: Smartphone,
    description: 'Pagos a través de la app Nequi',
    color: 'text-pink-600',
    bgColor: 'bg-pink-50'
  },
  'Nequi': {
    name: 'Nequi',
    icon: Smartphone,
    description: 'Pagos a través de la app Nequi',
    color: 'text-pink-600',
    bgColor: 'bg-pink-50'
  },
  'daviplata': {
    name: 'Daviplata',
    icon: Smartphone,
    description: 'Pagos a través de Daviplata',
    color: 'text-orange-600',
    bgColor: 'bg-orange-50'
  },
  'Daviplata': {
    name: 'Daviplata',
    icon: Smartphone,
    description: 'Pagos a través de Daviplata',
    color: 'text-orange-600',
    bgColor: 'bg-orange-50'
  },
  'PSE': {
    name: 'PSE',
    icon: Banknote,
    description: 'Pagos Seguros en Línea (PSE)',
    color: 'text-teal-600',
    bgColor: 'bg-teal-50'
  },
  'QR': {
    name: 'Código QR',
    icon: Smartphone,
    description: 'Pagos mediante código QR',
    color: 'text-cyan-600',
    bgColor: 'bg-cyan-50'
  }
}

export const ReportsEnhancedImproved: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'sales' | 'inventory' | 'dashboard'>('dashboard')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Filtros con valores inteligentes por defecto
  const [dateRange, setDateRange] = useState<'today' | 'yesterday' | 'week' | 'month' | 'custom'>('today')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [groupBy, setGroupBy] = useState('day')
  
  // Datos
  const [salesData, setSalesData] = useState<any>(null)
  const [inventoryData, setInventoryData] = useState<any>(null)
  const [dashboardData, setDashboardData] = useState<any>(null)

  // Configurar fechas inteligentes
  const getIntelligentDates = (range: string) => {
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    
    switch (range) {
      case 'today':
        return {
          start: today.toISOString().split('T')[0],
          end: today.toISOString().split('T')[0]
        }
      case 'yesterday':
        return {
          start: yesterday.toISOString().split('T')[0],
          end: yesterday.toISOString().split('T')[0]
        }
      case 'week':
        const weekAgo = new Date(today)
        weekAgo.setDate(weekAgo.getDate() - 7)
        return {
          start: weekAgo.toISOString().split('T')[0],
          end: today.toISOString().split('T')[0]
        }
      case 'month':
        const monthAgo = new Date(today)
        monthAgo.setDate(monthAgo.getDate() - 30)
        return {
          start: monthAgo.toISOString().split('T')[0],
          end: today.toISOString().split('T')[0]
        }
      default:
        return { start: startDate, end: endDate }
    }
  }

  // Configurar fechas por defecto
  useEffect(() => {
    const dates = getIntelligentDates(dateRange)
    setStartDate(dates.start)
    setEndDate(dates.end)
  }, [dateRange])

  const fetchSalesAnalytics = useCallback(async () => {
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
  }, [startDate, endDate, groupBy])

  const fetchInventoryAnalytics = useCallback(async () => {
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
  }, [])

  const fetchDashboard = useCallback(async () => {
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
  }, [])

  const exportToExcel = async (type: 'sales' | 'inventory') => {
    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate
      })
      
      const response = await fetch(`http://localhost:8000/api/v1/reports-enhanced/export/${type}/excel?${params}`)
      const data = await response.json()
      
      if (data.success) {
        // Simular descarga (en un caso real, el backend enviaría el archivo)
        alert(`Archivo Excel generado: ${data.data.filename}`)
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

  // Función helper para obtener clase de progreso basada en porcentaje
  const getProgressClass = (percentage: number) => {
    const rounded = Math.round(percentage / 5) * 5 // Redondear a múltiplos de 5
    const clamped = Math.min(Math.max(rounded, 0), 100) // Asegurar que esté entre 0 y 100
    return `progress-${clamped}`
  }

  // Función helper para atributos ARIA
  const getAriaValues = (percentage: number) => ({
    valuenow: Math.min(percentage, 100),
    valuemin: 0,
    valuemax: 100
  })

  const getTabAriaSelected = (isSelected: boolean) => isSelected

  const getPerformanceIndicator = (value: number, type: 'growth' | 'sales' | 'revenue') => {
    if (type === 'growth') {
      if (value > 10) return { text: 'Excelente', color: 'text-green-600', bg: 'bg-green-50' }
      if (value > 0) return { text: 'Bueno', color: 'text-blue-600', bg: 'bg-blue-50' }
      if (value > -10) return { text: 'Regular', color: 'text-yellow-600', bg: 'bg-yellow-50' }
      return { text: 'Necesita Atención', color: 'text-red-600', bg: 'bg-red-50' }
    }
    return { text: 'Normal', color: 'text-gray-600', bg: 'bg-gray-50' }
  }

  const getPaymentMethodInfo = useCallback((methodName: string) => {
    return PAYMENT_METHODS_INFO[methodName] || {
      name: methodName,
      icon: Wallet,
      description: 'Método de pago',
      color: 'text-gray-600',
      bgColor: 'bg-gray-50'
    }
  }, [])

  // Memoizar datos computados para mejor rendimiento
  const dashboardMetrics = useMemo(() => {
    if (!dashboardData) return null
    
    return {
      totalMethods: dashboardData.payment_methods_today?.length || 0,
      mostUsedMethod: dashboardData.payment_methods_today?.reduce((max: any, current: any) => 
        current.transactions > max.transactions ? current : max
      )?.method || 'N/A',
      highestValueMethod: dashboardData.payment_methods_today?.reduce((max: any, current: any) => 
        current.total > max.total ? current : max
      )?.method || 'N/A'
    }
  }, [dashboardData])

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
        {/* Header Mejorado */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                📊 Centro de Reportes
              </h1>
              <p className="text-gray-600">
                Análisis inteligente y exportación de datos del sistema POS
              </p>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Clock className="w-4 h-4" />
              <span>Última actualización: {new Date().toLocaleTimeString('es-CO')}</span>
            </div>
          </div>
        </div>

        {/* Tabs Mejorados */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8" role="tablist" aria-label="Navegación de reportes">
              {[
                { id: 'dashboard', label: 'Dashboard Principal', icon: BarChart3, color: 'blue' },
                { id: 'sales', label: 'Análisis de Ventas', icon: TrendingUp, color: 'green' },
                { id: 'inventory', label: 'Estado de Inventario', icon: Package, color: 'purple' }
              ].map((tab) => {
                const isTabSelected = activeTab === tab.id;
                return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-2 py-3 px-4 border-b-2 font-medium text-sm rounded-t-lg transition-all focus:outline-none focus:ring-2 focus:ring-${tab.color}-500 focus:ring-offset-2 ${
                    isTabSelected
                      ? `border-${tab.color}-500 text-${tab.color}-600 bg-${tab.color}-50`
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                  aria-label={`${tab.label} - ${isTabSelected ? 'Pestaña activa' : 'Hacer clic para cambiar a esta pestaña'}`}
                  title={`${tab.label} - ${isTabSelected ? 'Pestaña actualmente activa' : 'Hacer clic para ver esta sección'}`}
                  role="tab"
                  aria-selected={isTabSelected}
                  aria-controls={`${tab.id}-panel`}
                  id={`${tab.id}-tab`}
                >
                  <tab.icon className="w-5 h-5" />
                  <span>{tab.label}</span>
                </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Filtros Inteligentes */}
        {activeTab === 'sales' && (
          <div className="bg-white p-6 rounded-lg shadow-sm mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Calendar className="w-5 h-5 mr-2" />
                Filtros de Fecha
              </h3>
              <button
                type="button"
                onClick={fetchSalesAnalytics}
                disabled={loading}
                className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                aria-label={loading ? "Actualizando datos..." : "Actualizar datos del reporte"}
                title={loading ? "Actualizando datos..." : "Hacer clic para actualizar los datos del reporte"}
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>{loading ? 'Actualizando...' : 'Actualizar'}</span>
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label htmlFor="dateRange" className="block text-sm font-medium text-gray-700 mb-2">
                  Período
                </label>
                <select
                  id="dateRange"
                  value={dateRange}
                  onChange={(e) => setDateRange(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label="Seleccionar período de tiempo"
                  title="Selecciona el período de tiempo para los reportes"
                >
                  <option value="today">Hoy</option>
                  <option value="yesterday">Ayer</option>
                  <option value="week">Última Semana</option>
                  <option value="month">Último Mes</option>
                  <option value="custom">Personalizado</option>
                </select>
              </div>
              
              {dateRange === 'custom' && (
                <>
                  <div>
                    <label htmlFor="startDate" className="block text-sm font-medium text-gray-700 mb-2">
                      Fecha Inicio
                    </label>
                    <input
                      id="startDate"
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      aria-label="Seleccionar fecha de inicio"
                      title="Selecciona la fecha de inicio para el reporte"
                    />
                  </div>
                  <div>
                    <label htmlFor="endDate" className="block text-sm font-medium text-gray-700 mb-2">
                      Fecha Fin
                    </label>
                    <input
                      id="endDate"
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      aria-label="Seleccionar fecha de fin"
                      title="Selecciona la fecha de fin para el reporte"
                    />
                  </div>
                </>
              )}
              
              <div>
                <label htmlFor="groupBy" className="block text-sm font-medium text-gray-700 mb-2">
                  Agrupar por
                </label>
                <select
                  id="groupBy"
                  value={groupBy}
                  onChange={(e) => setGroupBy(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label="Seleccionar agrupación de datos"
                  title="Selecciona cómo agrupar los datos del reporte"
                >
                  <option value="day">Día</option>
                  <option value="hour">Hora</option>
                  <option value="week">Semana</option>
                  <option value="month">Mes</option>
                </select>
              </div>
            </div>
            
            {dateRange !== 'custom' && (
              <div className="mt-4 p-3 bg-blue-50 rounded-md">
                <p className="text-sm text-blue-800">
                  <strong>Período seleccionado:</strong> {startDate} a {endDate}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-red-400 mr-2" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Dashboard Principal Mejorado */}
        {activeTab === 'dashboard' && dashboardData && (
          <div id="dashboard-panel" className="space-y-6" role="tabpanel" aria-labelledby="dashboard-tab" tabIndex={0}>
            {/* Métricas Principales */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Hoy */}
              <div className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-blue-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Ventas de Hoy</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatNumber(dashboardData.period_comparison.today.sales)}
                    </p>
                    <p className="text-sm text-green-600 font-medium">
                      {formatCurrency(dashboardData.period_comparison.today.revenue)}
                    </p>
                  </div>
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-blue-600" />
                  </div>
                </div>
              </div>

              {/* Ayer */}
              <div className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-gray-400">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Ventas de Ayer</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatNumber(dashboardData.period_comparison.yesterday.sales)}
                    </p>
                    <p className="text-sm text-gray-600">
                      {formatCurrency(dashboardData.period_comparison.yesterday.revenue)}
                    </p>
                  </div>
                  <div className="p-3 bg-gray-100 rounded-lg">
                    <Clock className="w-6 h-6 text-gray-600" />
                  </div>
                </div>
              </div>

              {/* Esta Semana */}
              <div className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-green-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Esta Semana</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatNumber(dashboardData.period_comparison.week.sales)}
                    </p>
                    <p className="text-sm text-green-600 font-medium">
                      {formatCurrency(dashboardData.period_comparison.week.revenue)}
                    </p>
                  </div>
                  <div className="p-3 bg-green-100 rounded-lg">
                    <BarChart3 className="w-6 h-6 text-green-600" />
                  </div>
                </div>
              </div>

              {/* Este Mes */}
              <div className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-purple-500">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Este Mes</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {formatNumber(dashboardData.period_comparison.month.sales)}
                    </p>
                    <p className="text-sm text-purple-600 font-medium">
                      {formatCurrency(dashboardData.period_comparison.month.revenue)}
                    </p>
                  </div>
                  <div className="p-3 bg-purple-100 rounded-lg">
                    <DollarSign className="w-6 h-6 text-purple-600" />
                  </div>
                </div>
              </div>
            </div>

            {/* Resumen Rápido de Métodos de Pago */}
            <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <CreditCard className="w-5 h-5 mr-2 text-blue-600" />
                Distribución de Métodos de Pago
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {dashboardData.payment_methods_today?.map((payment: any, index: number) => {
                  const methodInfo = getPaymentMethodInfo(payment.method)
                  const IconComponent = methodInfo.icon
                  const percentage = dashboardData.period_comparison.today.revenue > 0 
                    ? (payment.total / dashboardData.period_comparison.today.revenue) * 100 
                    : 0
                  
                  return (
                    <div key={index} className={`p-4 rounded-lg ${methodInfo.bgColor} border-l-4 ${
                      percentage >= 50 ? 'border-green-500' :
                      percentage >= 25 ? 'border-blue-500' :
                      percentage >= 10 ? 'border-yellow-500' : 'border-gray-400'
                    }`}>
                      <div className="flex items-center mb-2">
                        <IconComponent className={`w-6 h-6 ${methodInfo.color} mr-2`} />
                        <span className={`font-semibold ${methodInfo.color}`}>
                          {methodInfo.name}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className={`text-2xl font-bold ${
                          percentage >= 50 ? 'text-green-600' :
                          percentage >= 25 ? 'text-blue-600' :
                          percentage >= 10 ? 'text-yellow-600' : 'text-gray-600'
                        }`}>
                          {percentage.toFixed(1)}%
                        </div>
                        <div className="text-sm text-gray-600">
                          {formatCurrency(payment.total)}
                        </div>
                        <div className="text-xs text-gray-500">
                          {formatNumber(payment.transactions)} transacciones
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Métodos de Pago - Tabla Detallada */}
            {dashboardData.payment_methods_today && dashboardData.payment_methods_today.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                      <CreditCard className="w-5 h-5 mr-2 text-blue-600" />
                      Tabla Detallada de Métodos de Pago
                    </h3>
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-gray-600 bg-white px-3 py-1 rounded-full">
                        {dashboardData.payment_methods_today.length} métodos activos
                      </span>
                      <span className="text-sm text-blue-600 font-medium">
                        Total: {formatCurrency(dashboardData.period_comparison.today.revenue)}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200" role="table" aria-label="Tabla de métodos de pago utilizados hoy">
                    <caption className="sr-only">Tabla que muestra los métodos de pago utilizados hoy con sus respectivas métricas</caption>
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" scope="col">
                          Método de Pago
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" scope="col">
                          Descripción
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" scope="col">
                          Transacciones
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" scope="col">
                          Monto Total
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" scope="col">
                          Promedio por Transacción
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" scope="col">
                          Participación %
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {dashboardData.payment_methods_today.map((payment: any, index: number) => {
                        const methodInfo = getPaymentMethodInfo(payment.method)
                        const IconComponent = methodInfo.icon
                        const averagePerTransaction = payment.total / payment.transactions
                        const percentage = dashboardData.period_comparison.today.revenue > 0 
                          ? (payment.total / dashboardData.period_comparison.today.revenue) * 100 
                          : 0
                        
                        return (
                          <tr key={index} className="hover:bg-gray-50 transition-colors">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className={`flex items-center p-3 rounded-lg ${methodInfo.bgColor}`}>
                                <IconComponent className={`w-5 h-5 ${methodInfo.color} mr-3`} />
                                <div>
                                  <div className={`font-medium ${methodInfo.color}`}>
                                    {methodInfo.name}
                                  </div>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <p className="text-sm text-gray-600">{methodInfo.description}</p>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-center">
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                {formatNumber(payment.transactions)}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-center">
                              <span className="text-sm font-semibold text-gray-900">
                                {formatCurrency(payment.total)}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-center">
                              <span className="text-sm text-gray-600">
                                {formatCurrency(averagePerTransaction)}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-center">
                              <div className="flex items-center justify-center space-x-3">
                                <div className="progress-bar-medium">
                                  <div 
                                    className={`progress-fill ${getProgressClass(percentage)}`}
                                    role="progressbar"
                                    {...getAriaValues(percentage)}
                                    aria-label={`${percentage.toFixed(1)}% de participación`}
                                  ></div>
                                </div>
                                <div className="flex flex-col items-center">
                                  <span className={`text-lg font-bold ${
                                    percentage >= 50 ? 'text-green-600' :
                                    percentage >= 25 ? 'text-blue-600' :
                                    percentage >= 10 ? 'text-yellow-600' : 'text-gray-600'
                                  }`}>
                                    {percentage.toFixed(1)}%
                                  </span>
                                  <span className="text-xs text-gray-500">
                                    {percentage >= 50 ? 'Principal' :
                                     percentage >= 25 ? 'Importante' :
                                     percentage >= 10 ? 'Moderado' : 'Menor'}
                                  </span>
                                </div>
                              </div>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
                
                {/* Resumen de Métodos de Pago */}
                <div className="px-6 py-4 bg-gradient-to-r from-gray-50 to-blue-50 border-t border-gray-200">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="text-center p-3 bg-white rounded-lg shadow-sm">
                      <p className="text-sm text-gray-600 mb-1">Total de Métodos</p>
                      <p className="text-xl font-bold text-blue-600">
                        {dashboardMetrics?.totalMethods || 0}
                      </p>
                    </div>
                    <div className="text-center p-3 bg-white rounded-lg shadow-sm">
                      <p className="text-sm text-gray-600 mb-1">Método Principal</p>
                      <p className="text-lg font-semibold text-green-600">
                        {dashboardData.payment_methods_today?.reduce((max: any, current: any) => 
                          current.total > max.total ? current : max
                        )?.method || 'N/A'}
                      </p>
                    </div>
                    <div className="text-center p-3 bg-white rounded-lg shadow-sm">
                      <p className="text-sm text-gray-600 mb-1">Más Transacciones</p>
                      <p className="text-lg font-semibold text-purple-600">
                        {dashboardMetrics?.mostUsedMethod || 'N/A'}
                      </p>
                    </div>
                    <div className="text-center p-3 bg-white rounded-lg shadow-sm">
                      <p className="text-sm text-gray-600 mb-1">Promedio por Transacción</p>
                      <p className="text-lg font-semibold text-orange-600">
                        {formatCurrency(
                          dashboardData.payment_methods_today?.reduce((sum: number, method: any) => 
                            sum + (method.total / method.transactions), 0
                          ) / (dashboardData.payment_methods_today?.length || 1)
                        )}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Inventario y Alertas */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Estado del Inventario */}
              <div className="bg-white p-6 rounded-xl shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Package className="w-5 h-5 mr-2" />
                  Estado del Inventario
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Total de Productos</span>
                    <span className="font-semibold">{formatNumber(dashboardData.inventory_overview.total_products)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Valor Total del Inventario</span>
                    <span className="font-semibold text-green-600">
                      {formatCurrency(dashboardData.inventory_overview.total_value)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Alertas de Stock</span>
                    <span className={`font-semibold ${dashboardData.inventory_overview.low_stock_alerts > 0 ? 'text-red-600' : 'text-green-600'}`}>
                      {dashboardData.inventory_overview.low_stock_alerts}
                    </span>
                  </div>
                </div>
              </div>

              {/* Top Vendedores */}
              {dashboardData.top_sellers_today && dashboardData.top_sellers_today.length > 0 && (
                <div className="bg-white p-6 rounded-xl shadow-sm">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Users className="w-5 h-5 mr-2" />
                    Top Vendedores - Hoy
                  </h3>
                  <div className="space-y-3">
                    {dashboardData.top_sellers_today.slice(0, 5).map((seller: any, index: number) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                            <span className="text-sm font-medium text-blue-600">#{index + 1}</span>
                          </div>
                          <span className="font-medium text-gray-900">{seller.seller}</span>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-semibold text-gray-900">
                            {formatCurrency(seller.revenue)}
                          </p>
                          <p className="text-xs text-gray-500">{seller.sales} ventas</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Exportar Dashboard */}
            <div className="bg-white p-4 rounded-lg shadow-sm">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">Exportar Datos del Dashboard</h3>
                <div className="flex space-x-2">
                  <button
                    type="button"
                    onClick={() => exportToExcel('sales')}
                    className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                    aria-label="Exportar datos de ventas a Excel"
                    title="Hacer clic para descargar un archivo Excel con los datos de ventas"
                  >
                    <FileSpreadsheet className="w-4 h-4" />
                    <span>Exportar Ventas</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => exportToExcel('inventory')}
                    className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
                    aria-label="Exportar datos de inventario a Excel"
                    title="Hacer clic para descargar un archivo Excel con los datos de inventario"
                  >
                    <FileSpreadsheet className="w-4 h-4" />
                    <span>Exportar Inventario</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Análisis de Ventas Mejorado */}
        {activeTab === 'sales' && salesData && (
          <div id="sales-panel" className="space-y-6" role="tabpanel" aria-labelledby="sales-tab" tabIndex={0}>
            {/* Resumen Visual Mejorado */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 rounded-xl text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100">Total de Ventas</p>
                    <p className="text-3xl font-bold">{formatNumber(salesData.summary.total_sales)}</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-blue-200" />
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-green-500 to-green-600 p-6 rounded-xl text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-100">Ingresos Totales</p>
                    <p className="text-3xl font-bold">{formatCurrency(salesData.summary.total_revenue)}</p>
                  </div>
                  <DollarSign className="w-8 h-8 text-green-200" />
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-6 rounded-xl text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-100">Venta Promedio</p>
                    <p className="text-3xl font-bold">{formatCurrency(salesData.summary.average_sale)}</p>
                  </div>
                  <BarChart3 className="w-8 h-8 text-purple-200" />
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-6 rounded-xl text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-orange-100">Crecimiento</p>
                    <p className="text-3xl font-bold">
                      {salesData.summary.growth_rate >= 0 ? '+' : ''}{salesData.summary.growth_rate.toFixed(1)}%
                    </p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-orange-200" />
                </div>
              </div>
            </div>

            {/* Métodos de Pago Detallados */}
            {salesData.analytics.payment_methods && (
              <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                    <CreditCard className="w-5 h-5 mr-2" />
                    Análisis Detallado de Métodos de Pago
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Desglose completo de cómo pagaron los clientes en el período seleccionado
                  </p>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Método de Pago
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Descripción
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Transacciones
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Monto Total
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Promedio por Venta
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Participación
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {salesData.analytics.payment_methods.map((payment: any, index: number) => {
                        const methodInfo = getPaymentMethodInfo(payment.method)
                        const IconComponent = methodInfo.icon
                        const averagePerSale = payment.total / payment.count
                        
                        return (
                          <tr key={index} className="hover:bg-gray-50 transition-colors">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className={`flex items-center p-3 rounded-lg ${methodInfo.bgColor}`}>
                                <IconComponent className={`w-5 h-5 ${methodInfo.color} mr-3`} />
                                <div>
                                  <div className={`font-medium ${methodInfo.color}`}>
                                    {methodInfo.name}
                                  </div>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <p className="text-sm text-gray-600">{methodInfo.description}</p>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-center">
                              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                                {formatNumber(payment.count)}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-center">
                              <span className="text-lg font-semibold text-gray-900">
                                {formatCurrency(payment.total)}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-center">
                              <span className="text-sm text-gray-600">
                                {formatCurrency(averagePerSale)}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-center">
                              <div className="flex items-center justify-center">
                                <div className="progress-bar-medium">
                                  <div 
                                    className={`progress-fill ${getProgressClass(payment.percentage)}`}
                                    role="progressbar"
                                    {...getAriaValues(payment.percentage)}
                                    aria-label={`${payment.percentage.toFixed(1)}% de participación`}
                                  ></div>
                                </div>
                                <span className="text-sm font-medium text-gray-900 min-w-[50px]">
                                  {payment.percentage.toFixed(1)}%
                                </span>
                              </div>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
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
