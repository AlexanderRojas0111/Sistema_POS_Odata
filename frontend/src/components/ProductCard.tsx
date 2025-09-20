import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, Minus, ShoppingCart, Star, Flame, Sparkles } from 'lucide-react';
import { useEnhancedCart, usePriceFormatter } from '../context/EnhancedCartContext';

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

interface ProductCardProps {
  product: Product;
  index?: number;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, index = 0 }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const { addToCart, getItemQuantity, updateQuantity } = useEnhancedCart();
  const { formatPrice } = usePriceFormatter();

  const quantity = getItemQuantity(product.id);
  const hasItem = quantity > 0;

  const handleAddToCart = () => {
    addToCart(product, 1);
  };

  const handleUpdateQuantity = (newQuantity: number) => {
    if (newQuantity <= 0) {
      updateQuantity(product.id, 0);
    } else {
      updateQuantity(product.id, newQuantity);
    }
  };

const getCategoryColor = (category: string) => {
  const colors = {
    'Sencillas': 'bg-green-100 text-green-800',
    'Clásicas': 'bg-yellow-100 text-yellow-800',
    'Premium': 'bg-orange-100 text-orange-800',
    'Bebidas Frías': 'bg-blue-100 text-blue-800',
    'Bebidas Calientes': 'bg-red-100 text-red-800'
  };
  return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800';
};

  const getCategoryIcon = (category: string) => {
    if (category === 'Premium') return <Sparkles className="w-4 h-4" />;
    if (category === 'Bebidas Frías') return <Star className="w-4 h-4" />;
    if (category === 'Bebidas Calientes') return <Star className="w-4 h-4" />;
    return <Star className="w-4 h-4" />;
  };

  return (
    <motion.div
      className="card card-hover group"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      whileHover={{ scale: 1.02 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      {/* Imagen del producto */}
      <div className="relative h-48 bg-gradient-to-br from-sabrositas-neutral-light to-gray-200 overflow-hidden">
        {/* Placeholder para imagen */}
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            className="text-6xl"
            animate={isHovered ? { scale: 1.1, rotate: 5 } : { scale: 1, rotate: 0 }}
            transition={{ duration: 0.3 }}
          >
            🥞
          </motion.div>
        </div>

        {/* Badges */}
        <div className="absolute top-3 left-3 flex flex-col space-y-2">
          {product.popular && (
            <motion.div
              className="bg-sabrositas-accent text-white px-2 py-1 rounded-full text-xs font-semibold flex items-center space-x-1"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2 }}
            >
              <Star className="w-3 h-3" />
              <span>Popular</span>
            </motion.div>
          )}
          {product.new && (
            <motion.div
              className="bg-sabrositas-success text-white px-2 py-1 rounded-full text-xs font-semibold"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3 }}
            >
              Nuevo
            </motion.div>
          )}
          {product.spicy && (
            <motion.div
              className="bg-red-500 text-white px-2 py-1 rounded-full text-xs font-semibold flex items-center space-x-1"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.4 }}
            >
              <Flame className="w-3 h-3" />
              <span>Picante</span>
            </motion.div>
          )}
        </div>

        {/* Categoría */}
        <div className="absolute top-3 right-3">
          <div className={`${getCategoryColor(product.category)} px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1`}>
            {getCategoryIcon(product.category)}
            <span>{product.category}</span>
          </div>
        </div>

        {/* Overlay de hover */}
        <motion.div
          className="absolute inset-0 bg-sabrositas-primary/80 flex items-center justify-center opacity-0"
          animate={{ opacity: isHovered ? 1 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <motion.button
            onClick={() => setShowDetails(true)}
            className="text-white font-semibold px-4 py-2 rounded-lg border-2 border-white hover:bg-white hover:text-sabrositas-primary transition-colors duration-300"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Ver Detalles
          </motion.button>
        </motion.div>
      </div>

      {/* Contenido de la tarjeta */}
      <div className="p-6">
        {/* Nombre y precio */}
        <div className="mb-4">
          <h3 className="text-xl font-bold text-sabrositas-neutral-dark mb-2 group-hover:text-sabrositas-primary transition-colors duration-300">
            {product.name}
          </h3>
          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold gradient-text">
              {formatPrice(product.price)}
            </span>
            <div className="flex items-center space-x-1 text-yellow-500">
              <Star className="w-4 h-4 fill-current" />
              <span className="text-sm font-medium">4.8</span>
            </div>
          </div>
        </div>

        {/* Descripción */}
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
          {product.description}
        </p>

        {/* Ingredientes */}
        <div className="mb-4">
          <div className="flex flex-wrap gap-1">
            {product.ingredients.slice(0, 3).map((ingredient, idx) => (
              <span
                key={idx}
                className="bg-sabrositas-neutral-light text-sabrositas-neutral-dark px-2 py-1 rounded-full text-xs"
              >
                {ingredient}
              </span>
            ))}
            {product.ingredients.length > 3 && (
              <span className="text-xs text-gray-500 px-2 py-1">
                +{product.ingredients.length - 3} más
              </span>
            )}
          </div>
        </div>

        {/* Controles del carrito */}
        <div className="flex items-center justify-between">
          {!hasItem ? (
            <motion.button
              onClick={handleAddToCart}
              className="btn-primary flex items-center space-x-2 w-full justify-center"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <ShoppingCart className="w-4 h-4" />
              <span>Agregar</span>
            </motion.button>
          ) : (
            <div className="flex items-center space-x-3 w-full">
              <motion.button
                onClick={() => handleUpdateQuantity(quantity - 1)}
                className="w-10 h-10 bg-sabrositas-neutral-light hover:bg-gray-200 rounded-lg flex items-center justify-center transition-colors duration-300"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <Minus className="w-4 h-4 text-sabrositas-neutral-dark" />
              </motion.button>

              <span className="flex-1 text-center font-semibold text-sabrositas-neutral-dark">
                {quantity}
              </span>

              <motion.button
                onClick={() => handleUpdateQuantity(quantity + 1)}
                className="w-10 h-10 bg-sabrositas-primary hover:bg-sabrositas-accent text-white rounded-lg flex items-center justify-center transition-colors duration-300"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <Plus className="w-4 h-4" />
              </motion.button>
            </div>
          )}
        </div>
      </div>

      {/* Modal de detalles (simplificado) */}
      {showDetails && (
        <motion.div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={() => setShowDetails(false)}
        >
          <motion.div
            className="bg-white rounded-2xl max-w-md w-full p-6"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-2xl font-bold text-sabrositas-neutral-dark mb-4">
              {product.name}
            </h3>
            
            <p className="text-gray-600 mb-4">
              {product.description}
            </p>

            <div className="mb-4">
              <h4 className="font-semibold text-sabrositas-neutral-dark mb-2">
                Ingredientes:
              </h4>
              <div className="flex flex-wrap gap-2">
                {product.ingredients.map((ingredient, idx) => (
                  <span
                    key={idx}
                    className="bg-sabrositas-neutral-light text-sabrositas-neutral-dark px-3 py-1 rounded-full text-sm"
                  >
                    {ingredient}
                  </span>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold gradient-text">
                {formatPrice(product.price)}
              </span>
              <button
                onClick={() => {
                  handleAddToCart();
                  setShowDetails(false);
                }}
                className="btn-primary"
              >
                Agregar al Carrito
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default ProductCard;
