import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Plus, Minus, Trash2, ShoppingBag, Phone, MessageCircle, CreditCard } from 'lucide-react';
import { useEnhancedCart, usePriceFormatter } from '../context/EnhancedCartContext';
import Checkout from './Checkout';

interface CartSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const CartSidebar: React.FC<CartSidebarProps> = ({ isOpen, onClose }) => {
  const { state: cartState, updateQuantity, removeFromCart, clearCart } = useEnhancedCart();
  const { formatPrice } = usePriceFormatter();
  const [isProcessing, setIsProcessing] = useState(false);
  const [showCheckout, setShowCheckout] = useState(false);

  const handleQuantityChange = (productId: string, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
    } else {
      updateQuantity(productId, newQuantity);
    }
  };

  const handleRemoveItem = (productId: string) => {
    removeFromCart(productId);
  };

  const handleClearCart = () => {
    clearCart();
  };

  const handleCheckout = () => {
    setShowCheckout(true);
  };

  const handleWhatsAppCheckout = async () => {
    setIsProcessing(true);
    
    // Simular procesamiento
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Generar mensaje de WhatsApp
    const orderMessage = generateWhatsAppMessage();
    const whatsappUrl = `https://wa.me/573134531128?text=${encodeURIComponent(orderMessage)}`;
    
    // Abrir WhatsApp
    window.open(whatsappUrl, '_blank');
    
    setIsProcessing(false);
  };

  const generateWhatsAppMessage = (): string => {
    let message = '🍽️ *PEDIDO SABROSITAS*\n\n';
    message += '¡Hola! Me gustaría hacer el siguiente pedido:\n\n';
    
    cartState.items.forEach((item, index) => {
      message += `${index + 1}. *${item.product.name}*\n`;
      message += `   Cantidad: ${item.quantity}\n`;
      message += `   Precio: ${formatPrice(item.product.price)}\n`;
      message += `   Subtotal: ${formatPrice(item.product.price * item.quantity)}\n\n`;
    });
    
    message += `💰 *TOTAL: ${formatPrice(cartState.total)}*\n\n`;
    message += 'Por favor confirmar disponibilidad y tiempo de entrega.\n';
    message += '¡Gracias! 😊';
    
    return message;
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
    hidden: { opacity: 0, x: 20 },
    visible: { opacity: 1, x: 0 }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <React.Fragment key="cart-sidebar">
          {/* Overlay */}
          <motion.div
            key="overlay"
            className="fixed inset-0 bg-black/50 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Sidebar */}
          <motion.div
            key="sidebar"
            className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-large z-50 flex flex-col"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'tween', duration: 0.3 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-sabrositas-primary to-sabrositas-accent rounded-xl flex items-center justify-center">
                  <ShoppingBag className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-sabrositas-neutral-dark">
                    Mi Pedido
                  </h2>
                  <p className="text-sm text-gray-500">
                    {cartState.itemCount} {cartState.itemCount === 1 ? 'producto' : 'productos'}
                  </p>
                </div>
              </div>
              <motion.button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-300"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <X className="w-6 h-6 text-gray-500" />
              </motion.button>
            </div>

            {/* Contenido */}
            <div className="flex-1 overflow-y-auto">
              {cartState.items.length === 0 ? (
                <motion.div
                  className="flex flex-col items-center justify-center h-full p-6 text-center"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                >
                  <div className="w-24 h-24 bg-sabrositas-neutral-light rounded-full flex items-center justify-center mb-4">
                    <ShoppingBag className="w-12 h-12 text-gray-400" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-600 mb-2">
                    Tu carrito está vacío
                  </h3>
                  <p className="text-gray-500 mb-6">
                    Agrega algunas arepas deliciosas para comenzar tu pedido
                  </p>
                  <motion.button
                    onClick={onClose}
                    className="btn-primary"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Explorar Menú
                  </motion.button>
                </motion.div>
              ) : (
                <motion.div
                  className="p-6"
                  variants={containerVariants}
                  initial="hidden"
                  animate="visible"
                >
                  {/* Lista de productos */}
                  <div className="space-y-4 mb-6">
                    {cartState.items.map((item) => (
                      <motion.div
                        key={item.product.id}
                        className="bg-sabrositas-neutral-light rounded-xl p-4"
                        variants={itemVariants}
                        layout
                      >
                        <div className="flex items-start space-x-3">
                          {/* Imagen del producto */}
                          <div className="w-16 h-16 bg-gradient-to-br from-sabrositas-primary/20 to-sabrositas-accent/20 rounded-lg flex items-center justify-center flex-shrink-0">
                            <span className="text-2xl">🥞</span>
                          </div>

                          {/* Información del producto */}
                          <div className="flex-1 min-w-0">
                            <h4 className="font-semibold text-sabrositas-neutral-dark truncate">
                              {item.product.name}
                            </h4>
                            <p className="text-sm text-gray-500 mb-2">
                              {formatPrice(item.product.price)} c/u
                            </p>

                            {/* Controles de cantidad */}
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-2">
                                <motion.button
                                  onClick={() => handleQuantityChange(item.product.id, item.quantity - 1)}
                                  className="w-8 h-8 bg-white rounded-lg flex items-center justify-center text-sabrositas-primary hover:bg-gray-100 transition-colors duration-300"
                                  whileHover={{ scale: 1.1 }}
                                  whileTap={{ scale: 0.9 }}
                                >
                                  <Minus className="w-4 h-4" />
                                </motion.button>
                                
                                <span className="w-8 text-center font-semibold text-sabrositas-neutral-dark">
                                  {item.quantity}
                                </span>
                                
                                <motion.button
                                  onClick={() => handleQuantityChange(item.product.id, item.quantity + 1)}
                                  className="w-8 h-8 bg-sabrositas-primary rounded-lg flex items-center justify-center text-white hover:bg-sabrositas-accent transition-colors duration-300"
                                  whileHover={{ scale: 1.1 }}
                                  whileTap={{ scale: 0.9 }}
                                >
                                  <Plus className="w-4 h-4" />
                                </motion.button>
                              </div>

                              <div className="flex items-center space-x-2">
                                <span className="font-bold text-sabrositas-neutral-dark">
                                  {formatPrice(item.product.price * item.quantity)}
                                </span>
                                <motion.button
                                  onClick={() => handleRemoveItem(item.product.id)}
                                  className="p-1 text-red-500 hover:bg-red-50 rounded-lg transition-colors duration-300"
                                  whileHover={{ scale: 1.1 }}
                                  whileTap={{ scale: 0.9 }}
                                >
                                  <Trash2 className="w-4 h-4" />
                                </motion.button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>

                  {/* Botón limpiar carrito */}
                  {cartState.items.length > 1 && (
                    <motion.button
                      onClick={handleClearCart}
                      className="w-full py-3 text-sm text-red-500 hover:bg-red-50 rounded-xl transition-colors duration-300 mb-6"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      Limpiar carrito
                    </motion.button>
                  )}
                </motion.div>
              )}
            </div>

            {/* Footer con total y checkout */}
            {cartState.items.length > 0 && (
              <motion.div
                className="border-t border-gray-200 p-6 bg-white"
                initial={{ y: 100 }}
                animate={{ y: 0 }}
                transition={{ duration: 0.3 }}
              >
                {/* Resumen del total */}
                <div className="mb-6">
                  <div className="flex items-center justify-between text-lg font-semibold text-sabrositas-neutral-dark mb-2">
                    <span>Total:</span>
                    <span className="text-2xl gradient-text">
                      {formatPrice(cartState.total)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500">
                    Incluye {cartState.itemCount} {cartState.itemCount === 1 ? 'producto' : 'productos'}
                  </p>
                </div>

                {/* Botones de acción */}
                <div className="space-y-3">
                  <motion.button
                    onClick={handleCheckout}
                    className="w-full btn-primary flex items-center justify-center space-x-2 py-4 text-lg"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <CreditCard className="w-5 h-5" />
                    <span>Checkout POS</span>
                  </motion.button>
                  
                  <motion.button
                    onClick={handleWhatsAppCheckout}
                    disabled={isProcessing}
                    className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-300 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    whileHover={{ scale: isProcessing ? 1 : 1.02 }}
                    whileTap={{ scale: isProcessing ? 1 : 0.98 }}
                  >
                    {isProcessing ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        <span>Procesando...</span>
                      </>
                    ) : (
                      <>
                        <MessageCircle className="w-5 h-5" />
                        <span>Pedir por WhatsApp</span>
                      </>
                    )}
                  </motion.button>

                  <motion.a
                    href="tel:+573134531128"
                    className="w-full btn-secondary flex items-center justify-center space-x-2 py-4 text-lg"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Phone className="w-5 h-5" />
                    <span>Llamar ahora</span>
                  </motion.a>
                </div>

                {/* Información adicional */}
                <div className="mt-4 text-center">
                  <p className="text-xs text-gray-500">
                    Tiempo promedio de entrega: 15-30 minutos
                  </p>
                </div>
              </motion.div>
            )}
          </motion.div>

          {/* Checkout Modal */}
          <Checkout 
            isOpen={showCheckout} 
            onClose={() => setShowCheckout(false)} 
          />
        </React.Fragment>
      )}
    </AnimatePresence>
  );
};

export default CartSidebar;
