import { useAuth } from './authSimple'
import { api, aiApi } from './api'
import { useState, useEffect } from 'react'
import AISearch from './components/AISearch'
import ProductRecommendations from './components/ProductRecommendations'
import ErrorBoundary from './components/ErrorBoundary'

interface DashboardData {
  health: any
  products: any[]
  users: any[]
  aiStats: any
}

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        const [health, products, users, aiStats] = await Promise.all([
          api.request('/api/v1/health'),
          api.request('/api/v1/products'),
          user?.role === 'admin' || user?.role === 'manager' || user?.role === 'super_admin' || user?.role === 'global_admin' || user?.role === 'store_admin' || user?.role === 'tech_admin'
            ? api.request('/api/v1/users')
            : Promise.resolve([]),
          aiApi.getAIStats().catch(() => ({}))
        ])
        setData({ health, products, users, aiStats })
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error al cargar datos')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [user?.role])

  const getMenuItems = () => {
    const baseItems = [
      { path: '/', label: 'Dashboard', icon: '🏠' },
      { path: '/analytics', label: 'Analytics IA', icon: '📊' },
      { path: '/products', label: 'Productos', icon: '📦' },
      { path: '/ai-search', label: 'Búsqueda IA', icon: '🤖' }
    ]
    
    if (user?.role === 'admin' || user?.role === 'manager' || user?.role === 'super_admin' || user?.role === 'global_admin' || user?.role === 'store_admin' || user?.role === 'tech_admin') {
      baseItems.push({ path: '/users', label: 'Usuarios', icon: '👥' })
      baseItems.push({ path: '/reports', label: 'Reportes', icon: '📊' })
    }
    
    if (user?.role === 'admin' || user?.role === 'super_admin' || user?.role === 'tech_admin') {
      baseItems.push({ path: '/admin', label: 'Administración', icon: '⚙️' })
    }
    
    return baseItems
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Reintentar
          </button>
        </div>
      </div>
    )
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Sistema POS O'Data</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Bienvenido, <strong>{user?.username}</strong> ({user?.role})
              </span>
              <button
                onClick={logout}
                className="bg-red-600 text-white px-4 py-2 rounded text-sm hover:bg-red-700"
              >
                Cerrar Sesión
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <nav className="w-64 bg-white shadow-sm min-h-screen">
          <div className="p-4">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Menú</h2>
            <ul className="space-y-2">
              {getMenuItems().map((item) => (
                <li key={item.path}>
                  <a
                    href={item.path}
                    className="flex items-center space-x-3 px-3 py-2 rounded text-gray-700 hover:bg-gray-100"
                  >
                    <span className="text-xl">{item.icon}</span>
                    <span>{item.label}</span>
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Dashboard v2.0 con IA</h2>
            
            {/* Búsqueda IA */}
            <div className="mb-8">
              <AISearch 
                placeholder="Buscar productos con inteligencia artificial..."
                onProductSelect={(product) => console.log('Producto seleccionado:', product)}
              />
            </div>
            
            {/* Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <span className="text-2xl">✅</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Estado del Sistema</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {data?.health?.status === 'healthy' ? 'Activo' : 'Inactivo'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <span className="text-2xl">📦</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Productos</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {data?.products?.length || 0}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <span className="text-2xl">👥</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Usuarios</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {data?.users?.length || 0}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <span className="text-2xl">🤖</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">IA Activa</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {data?.aiStats?.models?.tfidf?.is_trained ? 'Sí' : 'No'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Data Tables */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Products Table */}
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Productos Recientes</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Nombre
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Precio
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Stock
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {data?.products?.slice(0, 5).map((product, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {product.name || product.nombre || 'Sin nombre'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${product.price || product.precio || 0}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {product.stock || product.cantidad || 0}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Users Table */}
              {(user?.role === 'admin' || user?.role === 'manager' || user?.role === 'super_admin' || user?.role === 'global_admin' || user?.role === 'store_admin' || user?.role === 'tech_admin') && (
                <div className="bg-white rounded-lg shadow">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-medium text-gray-900">Usuarios del Sistema</h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Usuario
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Rol
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Estado
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {data?.users?.slice(0, 5).map((user, index) => (
                          <tr key={index}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {user.username || user.usuario || 'Sin usuario'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                {user.role || user.rol || 'cashier'}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                Activo
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Recomendaciones IA */}
              {data?.products && data.products.length > 0 && (
                <div className="lg:col-span-1">
                  <ProductRecommendations 
                    productId={data?.products?.[0]?.id || data?.products?.[0]?.product_id}
                    limit={3}
                    title="Recomendaciones IA"
                  />
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </ErrorBoundary>
  )
}
