import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Filter, Grid, List, X } from 'lucide-react';
import { products, categories, getProductsByCategory, searchProducts } from '../data/products';
import ProductCard from './ProductCard';

// Definir el tipo Product localmente para evitar problemas de importación
interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category: 'Sencillas' | 'Clásicas' | 'Premium' | 'Bebidas Frías' | 'Bebidas Calientes';
  ingredients: string[];
  image: string;
  popular?: boolean;
  new?: boolean;
  spicy?: boolean;
}

interface MenuSectionProps {
  onProductClick?: (product: Product) => void;
}

const MenuSection: React.FC<MenuSectionProps> = ({ onProductClick: _onProductClick }) => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'price' | 'category'>('name');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = useState(false);

  // Filtrar y ordenar productos
  const filteredProducts = useMemo(() => {
    let filtered = selectedCategory === 'all' 
      ? products 
      : getProductsByCategory(selectedCategory);

    if (searchQuery.trim()) {
      filtered = searchProducts(searchQuery);
    }

    // Ordenar productos
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'price':
          return a.price - b.price;
        case 'category':
          return a.category.localeCompare(b.category);
        case 'name':
        default:
          return a.name.localeCompare(b.name);
      }
    });

    return filtered;
  }, [selectedCategory, searchQuery, sortBy]);

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    setSearchQuery(''); // Limpiar búsqueda al cambiar categoría
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (query.trim()) {
      setSelectedCategory('all'); // Mostrar todos los productos en búsqueda
    }
  };

  const clearFilters = () => {
    setSelectedCategory('all');
    setSearchQuery('');
    setSortBy('name');
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <section id="menu" className="section-padding bg-white">
      <div className="container-custom">
        {/* Header de la sección */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-4xl md:text-5xl font-bold gradient-text mb-4">
            Nuestro Menú
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Descubre nuestras 18 arepas cuadradas únicas, cada una con su personalidad especial. 
            Desde las más sencillas hasta las más premium.
          </p>
        </motion.div>

        {/* Barra de búsqueda y filtros */}
        <motion.div
          className="bg-sabrositas-neutral-light rounded-2xl p-6 mb-8"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="flex flex-col lg:flex-row gap-4 items-center justify-between">
            {/* Búsqueda */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Buscar arepas por nombre o ingredientes..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="input-field pl-10"
              />
              {searchQuery && (
                <button
                  onClick={() => handleSearch('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  title="Limpiar búsqueda"
                  aria-label="Limpiar búsqueda"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>

            {/* Controles */}
            <div className="flex items-center space-x-4">
              {/* Botón de filtros móvil */}
              <motion.button
                onClick={() => setShowFilters(!showFilters)}
                className="lg:hidden btn-secondary flex items-center space-x-2"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Filter className="w-4 h-4" />
                <span>Filtros</span>
              </motion.button>

              {/* Ordenar */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'name' | 'price' | 'category')}
                className="input-field w-auto"
                title="Ordenar productos"
                aria-label="Ordenar productos por criterio"
              >
                <option value="name">Ordenar por nombre</option>
                <option value="price">Ordenar por precio</option>
                <option value="category">Ordenar por categoría</option>
              </select>

              {/* Vista */}
              <div className="flex items-center space-x-2">
                <motion.button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-lg transition-colors duration-300 ${
                    viewMode === 'grid' 
                      ? 'bg-sabrositas-primary text-white' 
                      : 'bg-white text-gray-600 hover:bg-gray-100'
                  }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Grid className="w-5 h-5" />
                </motion.button>
                <motion.button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-lg transition-colors duration-300 ${
                    viewMode === 'list' 
                      ? 'bg-sabrositas-primary text-white' 
                      : 'bg-white text-gray-600 hover:bg-gray-100'
                  }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <List className="w-5 h-5" />
                </motion.button>
              </div>
            </div>
          </div>

          {/* Filtros móviles */}
          <AnimatePresence>
            {showFilters && (
              <motion.div
                className="lg:hidden mt-4 pt-4 border-t border-gray-200"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="flex flex-wrap gap-2">
                  {categories.map((category) => (
                    <motion.button
                      key={category.id}
                      onClick={() => handleCategoryChange(category.id)}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-colors duration-300 ${
                        selectedCategory === category.id
                          ? 'bg-sabrositas-primary text-white'
                          : 'bg-white text-gray-600 hover:bg-gray-100'
                      }`}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {category.name} ({category.count})
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar de categorías (Desktop) */}
          <motion.div
            className="lg:w-64 flex-shrink-0"
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <div className="hidden lg:block bg-white rounded-2xl shadow-soft p-6 sticky top-24">
              <h3 className="text-lg font-semibold text-sabrositas-neutral-dark mb-4">
                Categorías
              </h3>
              <div className="space-y-2">
                {categories.map((category) => (
                  <motion.button
                    key={category.id}
                    onClick={() => handleCategoryChange(category.id)}
                    className={`w-full text-left px-4 py-3 rounded-xl transition-all duration-300 ${
                      selectedCategory === category.id
                        ? 'bg-sabrositas-primary text-white shadow-soft'
                        : 'text-gray-600 hover:bg-sabrositas-neutral-light hover:text-sabrositas-primary'
                    }`}
                    whileHover={{ x: 5 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{category.name}</span>
                      <span className={`text-sm ${
                        selectedCategory === category.id ? 'text-white/80' : 'text-gray-400'
                      }`}>
                        {category.count}
                      </span>
                    </div>
                  </motion.button>
                ))}
              </div>

              {/* Limpiar filtros */}
              {(selectedCategory !== 'all' || searchQuery) && (
                <motion.button
                  onClick={clearFilters}
                  className="w-full mt-4 px-4 py-2 text-sm text-sabrositas-accent hover:text-sabrositas-primary transition-colors duration-300"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Limpiar filtros
                </motion.button>
              )}
            </div>
          </motion.div>

          {/* Grid de productos */}
          <div className="flex-1">
            {/* Resultados */}
            <motion.div
              className="mb-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              <p className="text-gray-600">
                {filteredProducts.length === 0 ? (
                  'No se encontraron productos'
                ) : (
                  `Mostrando ${filteredProducts.length} de ${products.length} productos`
                )}
              </p>
            </motion.div>

            {/* Productos */}
            <AnimatePresence mode="wait">
              {filteredProducts.length === 0 ? (
                <motion.div
                  className="text-center py-12"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <div className="text-6xl mb-4">🔍</div>
                  <h3 className="text-xl font-semibold text-gray-600 mb-2">
                    No se encontraron productos
                  </h3>
                  <p className="text-gray-500 mb-4">
                    Intenta con otros términos de búsqueda o explora nuestras categorías
                  </p>
                  <button
                    onClick={clearFilters}
                    className="btn-primary"
                  >
                    Ver todo el menú
                  </button>
                </motion.div>
              ) : (
                <motion.div
                  key={`${selectedCategory}-${searchQuery}-${sortBy}-${viewMode}`}
                  className={viewMode === 'grid' 
                    ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6'
                    : 'space-y-4'
                  }
                  variants={containerVariants}
                  initial="hidden"
                  animate="visible"
                >
                  {filteredProducts.map((product, index) => (
                    <motion.div
                      key={product.id}
                      variants={itemVariants}
                      className={viewMode === 'list' ? 'w-full' : ''}
                    >
                      <ProductCard 
                        product={product} 
                        index={index}
                      />
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
};

export default MenuSection;
