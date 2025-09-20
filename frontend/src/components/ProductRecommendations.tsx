import { useState, useEffect } from 'react'
import { aiApi } from '../api'

interface Recommendation {
  product: {
    id: number
    name: string
    price: number
    stock: number
  }
  similarity_score: number
  recommendation_reason: string
}

interface ProductRecommendationsProps {
  productId: number
  limit?: number
  title?: string
}

export default function ProductRecommendations({ 
  productId, 
  limit = 5, 
  title = "Productos Recomendados" 
}: ProductRecommendationsProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (productId) {
      loadRecommendations()
    }
  }, [productId, limit])

  const loadRecommendations = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await aiApi.getRecommendations(productId, limit)
      setRecommendations(response.data.recommendations)
    } catch (err) {
      setError('Error cargando recomendaciones')
      console.error('Error loading recommendations:', err)
    } finally {
      setLoading(false)
    }
  }

  const getSimilarityColor = (score: number) => {
    if (score > 0.7) return 'text-green-600'
    if (score > 0.5) return 'text-yellow-600'
    return 'text-orange-600'
  }

  const getSimilarityLabel = (score: number) => {
    if (score > 0.7) return 'Muy similar'
    if (score > 0.5) return 'Similar'
    if (score > 0.3) return 'Relacionado'
    return 'Poco relacionado'
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-sm text-gray-600 mt-2">Generando recomendaciones con IA...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
        <div className="text-center text-red-600">
          <p>{error}</p>
          <button 
            onClick={loadRecommendations}
            className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Reintentar
          </button>
        </div>
      </div>
    )
  }

  if (recommendations.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
        <p className="text-gray-500 text-center">No hay recomendaciones disponibles</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        <span className="text-sm text-gray-500">
          {recommendations.length} recomendación{recommendations.length !== 1 ? 'es' : ''}
        </span>
      </div>

      <div className="space-y-3">
        {recommendations.map((rec, index) => (
          <div
            key={index}
            className="p-3 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{rec.product.name}</h4>
                <p className="text-sm text-gray-600">
                  Precio: ${rec.product.price} | Stock: {rec.product.stock}
                </p>
                {rec.recommendation_reason && (
                  <p className="text-xs text-blue-600 mt-1">
                    💡 {rec.recommendation_reason}
                  </p>
                )}
              </div>
              <div className="text-right ml-4">
                <div className={`text-sm font-medium ${getSimilarityColor(rec.similarity_score)}`}>
                  {Math.round(rec.similarity_score * 100)}%
                </div>
                <div className="text-xs text-gray-500">
                  {getSimilarityLabel(rec.similarity_score)}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 text-xs text-gray-500 text-center">
        🤖 Recomendaciones generadas por inteligencia artificial
      </div>
    </div>
  )
}
