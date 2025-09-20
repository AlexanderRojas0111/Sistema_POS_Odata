import { useState, useEffect } from 'react'
import { aiApi } from '../api'

interface SearchResult {
  product: {
    id: number
    name: string
    price: number
    stock: number
  }
  similarity_score: number
  matched_terms: string[]
}

interface AISearchProps {
  onProductSelect?: (product: any) => void
  placeholder?: string
}

export default function AISearch({ onProductSelect, placeholder = "Buscar productos..." }: AISearchProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)

  // Obtener sugerencias mientras el usuario escribe
  useEffect(() => {
    if (query.length >= 2) {
      const timeoutId = setTimeout(async () => {
        try {
          const response = await aiApi.getSearchSuggestions(query, 5)
          setSuggestions(response.data.suggestions)
        } catch (error) {
          console.error('Error getting suggestions:', error)
        }
      }, 300)
      return () => clearTimeout(timeoutId)
    } else {
      setSuggestions([])
    }
  }, [query])

  const handleSearch = async (searchQuery: string = query) => {
    if (!searchQuery.trim()) return

    setLoading(true)
    try {
      const response = await aiApi.semanticSearch(searchQuery, 10)
      setResults(response.data.results)
      setShowSuggestions(false)
    } catch (error) {
      console.error('Error searching:', error)
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion)
    handleSearch(suggestion)
  }

  const handleProductClick = (product: any) => {
    if (onProductSelect) {
      onProductSelect(product)
    }
  }

  return (
    <div className="relative w-full">
      {/* Barra de búsqueda */}
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          onFocus={() => setShowSuggestions(true)}
          placeholder={placeholder}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        
        {/* Botón de búsqueda */}
        <button
          onClick={() => handleSearch()}
          disabled={loading}
          className="absolute right-2 top-1/2 transform -translate-y-1/2 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '🔍' : '🔍'}
        </button>
      </div>

      {/* Sugerencias */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {suggestions.map((suggestion, index) => (
            <div
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              className="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b border-gray-100 last:border-b-0"
            >
              <span className="text-gray-600">💡</span>
              <span className="ml-2">{suggestion}</span>
            </div>
          ))}
        </div>
      )}

      {/* Resultados de búsqueda */}
      {results.length > 0 && (
        <div className="mt-4 space-y-2">
          <h3 className="text-lg font-semibold text-gray-800">
            Resultados de búsqueda semántica ({results.length})
          </h3>
          <div className="space-y-2">
            {results.map((result, index) => (
              <div
                key={index}
                onClick={() => handleProductClick(result.product)}
                className="p-3 bg-white border border-gray-200 rounded-lg hover:shadow-md cursor-pointer transition-shadow"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{result.product.name}</h4>
                    <p className="text-sm text-gray-600">
                      Precio: ${result.product.price} | Stock: {result.product.stock}
                    </p>
                    {result.matched_terms.length > 0 && (
                      <p className="text-xs text-blue-600 mt-1">
                        Términos coincidentes: {result.matched_terms.join(', ')}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-medium text-green-600">
                      {Math.round(result.similarity_score * 100)}% similitud
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Estado de carga */}
      {loading && (
        <div className="mt-4 text-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-sm text-gray-600 mt-2">Buscando con IA...</p>
        </div>
      )}
    </div>
  )
}
