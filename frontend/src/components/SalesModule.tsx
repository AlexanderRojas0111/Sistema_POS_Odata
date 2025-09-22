import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../authSimple';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShoppingCart, 
  Plus, 
  Minus, 
  Trash2, 
  Search, 
  Receipt,
  CheckCircle,
  AlertCircle,
  Smartphone
} from 'lucide-react';
import QRPaymentModal from './QRPaymentModal';
import MultiPaymentModal from './MultiPaymentModal';

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  stock: number;
  image?: string;
}

interface CartItem {
  product: Product;
  quantity: number;
  subtotal: number;
}

interface Customer {
  name: string;
  phone: string;
  email: string;
  address: string;
}

const SalesModule: React.FC = () => {
  const { user } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  const [showCheckout, setShowCheckout] = useState(false);
  const [showQRPayment, setShowQRPayment] = useState(false);
  const [showMultiPayment, setShowMultiPayment] = useState(false);
  const [customer, setCustomer] = useState<Customer>({
    name: '',
    phone: '',
    email: '',
    address: ''
  });
  const [paymentMethod, setPaymentMethod] = useState('nequi');
  const [saleNotes, setSaleNotes] = useState('');
  const [multiPayments, setMultiPayments] = useState<any[]>([]);
  const [isMultiPaymentMode, setIsMultiPaymentMode] = useState(false);

  // Categorías de productos con contadores dinámicos
  const categories = useMemo(() => [
    { id: 'all', name: 'Todas', count: products.length },
    { id: 'sencillas', name: 'Sencillas', count: products.filter(p => p.category === 'sencillas').length },
    { id: 'clasicas', name: 'Clásicas', count: products.filter(p => p.category === 'clasicas').length },
    { id: 'premium', name: 'Premium', count: products.filter(p => p.category === 'premium').length },
    { id: 'bebidas_frias', name: 'Bebidas Frías', count: products.filter(p => p.category === 'bebidas_frias').length },
    { id: 'bebidas_calientes', name: 'Bebidas Calientes', count: products.filter(p => p.category === 'bebidas_calientes').length }
  ], [products]);

  // Cargar productos desde la API
  useEffect(() => {
    const loadProducts = async () => {
      try {
        setIsLoading(true);
        const response = await fetch('http://localhost:8000/api/v1/products?per_page=100');
        if (response.ok) {
          const data = await response.json();
          const productsData = data.data.products.map((product: any) => ({
            id: product.id.toString(),
            name: product.name,
            description: product.description || '',
            price: parseFloat(product.price),
            category: product.category,
            stock: product.stock || 0,
            image: product.image || '/images/default-arepa.jpg'
          }));
          setProducts(productsData);
          setFilteredProducts(productsData);
          
          // Actualizar contadores de categorías
          categories.forEach(cat => {
            if (cat.id === 'all') {
              cat.count = productsData.length;
            } else {
              cat.count = productsData.filter((p: Product) => p.category === cat.id).length;
            }
          });
        }
      } catch (error) {
        console.error('Error cargando productos:', error);
        // Datos de ejemplo si la API falla
        const exampleProducts: Product[] = [
          {
            id: '1',
            name: 'LA PATRONA',
            description: 'Chicharrón, carne desmechada, maduro al horno y queso',
            price: 15000,
            category: 'premium',
            stock: 10
          },
          {
            id: '2',
            name: 'LA FÁCIL',
            description: 'Queso, mucho queso!',
            price: 7000,
            category: 'sencillas',
            stock: 15
          },
          {
            id: '3',
            name: 'LA COMPINCHE',
            description: 'Carne desmechada, maduro al horno y queso',
            price: 12000,
            category: 'clasicas',
            stock: 8
          }
        ];
        setProducts(exampleProducts);
        setFilteredProducts(exampleProducts);
      } finally {
        setIsLoading(false);
      }
    };

    loadProducts();
  }, []);

  // Filtrar productos
  useEffect(() => {
    let filtered = products;

    // Filtrar por búsqueda
    if (searchQuery) {
      filtered = filtered.filter(product =>
        product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        product.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filtrar por categoría
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(product => product.category === selectedCategory);
    }

    setFilteredProducts(filtered);
  }, [products, searchQuery, selectedCategory]);

  // Agregar producto al carrito
  const addToCart = (product: Product) => {
    if (product.stock <= 0) {
      alert('Producto sin stock disponible');
      return;
    }

    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.product.id === product.id);
      if (existingItem) {
        if (existingItem.quantity >= product.stock) {
          alert('No hay suficiente stock disponible');
          return prevCart;
        }
        return prevCart.map(item =>
          item.product.id === product.id
            ? { ...item, quantity: item.quantity + 1, subtotal: (item.quantity + 1) * item.product.price }
            : item
        );
      } else {
        return [...prevCart, {
          product,
          quantity: 1,
          subtotal: product.price
        }];
      }
    });
  };

  // Actualizar cantidad en carrito
  const updateQuantity = (productId: string, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }

    const product = products.find(p => p.id === productId);
    if (product && quantity > product.stock) {
      alert('No hay suficiente stock disponible');
      return;
    }

    setCart(prevCart =>
      prevCart.map(item =>
        item.product.id === productId
          ? { ...item, quantity, subtotal: quantity * item.product.price }
          : item
      )
    );
  };

  // Remover producto del carrito
  const removeFromCart = (productId: string) => {
    setCart(prevCart => prevCart.filter(item => item.product.id !== productId));
  };

  // Limpiar carrito
  const clearCart = () => {
    setCart([]);
    setIsMultiPaymentMode(false);
    setMultiPayments([]);
    setPaymentMethod('nequi');
  };

  // Calcular totales
  const subtotal = cart.reduce((sum, item) => sum + item.subtotal, 0);
  const tax = subtotal * 0.19; // IVA 19%
  const total = subtotal + tax;

  // Manejar pagos múltiples
  const handleMultiPaymentConfirm = (payments: any[], changeAmount: number) => {
    setMultiPayments(payments);
    setIsMultiPaymentMode(true);
    setShowMultiPayment(false);
    
    // Actualizar el método de pago principal para mostrar "Múltiples"
    setPaymentMethod('multi_payment');
  };

  // Procesar venta
  const processSale = async () => {
    if (cart.length === 0) {
      alert('El carrito está vacío');
      return;
    }

    if (!customer.name.trim()) {
      alert('Por favor ingrese el nombre del cliente');
      return;
    }

    try {
      if (!user) {
        alert('Debe estar autenticado para realizar ventas');
        return;
      }

      // Solución robusta: usar username si no hay ID disponible
      const saleData = {
        // No enviar user_id - el backend lo extraerá del token JWT automáticamente
        customer_name: customer.name,
        customer_phone: customer.phone,
        customer_email: customer.email,
        customer_address: customer.address,
        payment_method: isMultiPaymentMode ? 'multi_payment' : paymentMethod,
        notes: saleNotes,
        items: cart.map(item => ({
          product_id: parseInt(item.product.id),
          quantity: item.quantity,
          unit_price: item.product.price
        })),
        // Agregar datos de pagos múltiples si aplica
        multi_payments: isMultiPaymentMode ? multiPayments : undefined
      };

      const response = await fetch('http://localhost:8000/api/v1/sales', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`, // Agregar token de autenticación
        },
        body: JSON.stringify(saleData)
      });

      if (response.ok) {
        const result = await response.json();
        // Solución robusta: manejar diferentes estructuras de respuesta
        const saleId = result.data?.id || result.data?.sale?.id || result.id || 'N/A';
        alert(`¡Venta procesada exitosamente! ID: ${saleId}`);
        clearCart();
        setShowCheckout(false);
        setCustomer({ name: '', phone: '', email: '', address: '' });
        setSaleNotes('');
      } else {
        const error = await response.json();
        const errorMessage = error.error?.message || error.message || 'Error desconocido';
        alert(`Error procesando la venta: ${errorMessage}`);
      }
    } catch (error) {
      console.error('Error procesando venta:', error);
      alert('Error procesando la venta. Intente nuevamente.');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <ShoppingCart className="h-8 w-8 text-amber-500" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Módulo de Ventas</h1>
                <p className="text-sm text-gray-500">Sistema POS Sabrositas - Cajero</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-gray-500">Total en carrito</p>
                <p className="text-2xl font-bold text-amber-600">${total.toLocaleString()}</p>
              </div>
              <button
                onClick={() => setShowCheckout(true)}
                disabled={cart.length === 0}
                className="bg-amber-500 text-white px-6 py-2 rounded-lg hover:bg-amber-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <Receipt className="h-5 w-5" />
                <span>Procesar Venta</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Panel de Productos */}
          <div className="lg:col-span-2">
            {/* Filtros */}
            <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <input
                      type="text"
                      placeholder="Buscar productos..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div className="flex space-x-2">
                  {categories.map(category => (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategory(category.id)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        selectedCategory === category.id
                          ? 'bg-amber-500 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {category.name} ({category.count})
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Lista de Productos */}
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {filteredProducts.map(product => (
                <motion.div
                  key={product.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow"
                >
                  <div className="p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-semibold text-gray-900 text-sm">{product.name}</h3>
                      <span className="text-xs text-gray-500">Stock: {product.stock}</span>
                    </div>
                    <p className="text-xs text-gray-600 mb-3 line-clamp-2">{product.description}</p>
                    <div className="flex justify-between items-center">
                      <span className="text-lg font-bold text-amber-600">${product.price.toLocaleString()}</span>
                      <button
                        onClick={() => addToCart(product)}
                        disabled={product.stock <= 0}
                        className="bg-amber-500 text-white px-3 py-1 rounded text-xs hover:bg-amber-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
                      >
                        <Plus className="h-3 w-3" />
                        <span>Agregar</span>
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {filteredProducts.length === 0 && (
              <div className="text-center py-12">
                <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No se encontraron productos</p>
              </div>
            )}
          </div>

          {/* Panel del Carrito */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border sticky top-4">
              <div className="p-4 border-b">
                <div className="flex justify-between items-center">
                  <h3 className="font-semibold text-gray-900">Carrito de Ventas</h3>
                  <span className="text-sm text-gray-500">{cart.length} items</span>
                </div>
              </div>

              <div className="p-4 max-h-96 overflow-y-auto">
                {cart.length === 0 ? (
                  <div className="text-center py-8">
                    <ShoppingCart className="h-12 w-12 text-gray-300 mx-auto mb-2" />
                    <p className="text-gray-500 text-sm">Carrito vacío</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {cart.map(item => (
                      <motion.div
                        key={item.product.id}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-center space-x-3 p-2 bg-gray-50 rounded-lg"
                      >
                        <div className="flex-1">
                          <h4 className="font-medium text-sm text-gray-900">{item.product.name}</h4>
                          <p className="text-xs text-gray-500">${item.product.price.toLocaleString()} c/u</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => updateQuantity(item.product.id, item.quantity - 1)}
                            className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center hover:bg-gray-300"
                            aria-label="Disminuir cantidad"
                            title="Disminuir cantidad"
                          >
                            <Minus className="h-3 w-3" />
                          </button>
                          <span className="w-8 text-center text-sm font-medium">{item.quantity}</span>
                          <button
                            onClick={() => updateQuantity(item.product.id, item.quantity + 1)}
                            className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center hover:bg-gray-300"
                            aria-label="Aumentar cantidad"
                            title="Aumentar cantidad"
                          >
                            <Plus className="h-3 w-3" />
                          </button>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium">${item.subtotal.toLocaleString()}</p>
                          <button
                            onClick={() => removeFromCart(item.product.id)}
                            className="text-red-500 hover:text-red-700"
                            aria-label="Eliminar producto del carrito"
                            title="Eliminar producto del carrito"
                          >
                            <Trash2 className="h-3 w-3" />
                          </button>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>

              {cart.length > 0 && (
                <div className="p-4 border-t bg-gray-50">
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Subtotal:</span>
                      <span>${subtotal.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>IVA (19%):</span>
                      <span>${tax.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between font-bold text-lg border-t pt-2">
                      <span>Total:</span>
                      <span>${total.toLocaleString()}</span>
                    </div>
                    
                    {/* Información de pagos múltiples */}
                    {isMultiPaymentMode && multiPayments.length > 0 && (
                      <div className="border-t pt-2 mt-2">
                        <div className="text-xs text-blue-600 font-medium mb-1">
                          💳 Pagos Múltiples Configurados:
                        </div>
                        <div className="space-y-1">
                          {multiPayments.map((payment, index) => (
                            <div key={index} className="flex justify-between text-xs">
                              <span>{payment.method === 'cash' ? '💵' : payment.method === 'nequi' ? '📱' : payment.method === 'daviplata' ? '🟣' : '💳'} {payment.method}:</span>
                              <span>${payment.amount.toLocaleString()}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Modal de Checkout */}
      <AnimatePresence>
        {showCheckout && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Procesar Venta</h3>
                  <button
                    onClick={() => setShowCheckout(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ×
                  </button>
                </div>

                <div className="space-y-4">
                  {/* Información del Cliente */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Información del Cliente
                    </label>
                    <div className="space-y-3">
                      <input
                        type="text"
                        placeholder="Nombre completo *"
                        value={customer.name}
                        onChange={(e) => setCustomer({...customer, name: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                        required
                      />
                      <input
                        type="tel"
                        placeholder="Teléfono"
                        value={customer.phone}
                        onChange={(e) => setCustomer({...customer, phone: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                      />
                      <input
                        type="email"
                        placeholder="Email"
                        value={customer.email}
                        onChange={(e) => setCustomer({...customer, email: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                      />
                      <input
                        type="text"
                        placeholder="Dirección"
                        value={customer.address}
                        onChange={(e) => setCustomer({...customer, address: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  {/* Método de Pago */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Método de Pago
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      <select
                        value={paymentMethod}
                        onChange={(e) => {
                          if (e.target.value === 'multi_payment') {
                            setShowMultiPayment(true);
                          } else {
                            setIsMultiPaymentMode(false);
                            setMultiPayments([]);
                            setPaymentMethod(e.target.value);
                          }
                        }}
                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                        aria-label="Seleccionar método de pago"
                      >
                        <option value="cash">💵 Efectivo</option>
                        <option value="card">💳 Tarjeta</option>
                        <option value="nequi">📱 Nequi</option>
                        <option value="nequi_qr">📱 Nequi QR</option>
                        <option value="daviplata">🟣 Daviplata</option>
                        <option value="daviplata_qr">🟣 Daviplata QR</option>
                        <option value="qr_generic">📲 QR Genérico</option>
                        <option value="tullave">🔑 tu llave</option>
                        <option value="multi_payment">💳 Pagos Múltiples</option>
                      </select>
                      <button
                        onClick={() => setShowMultiPayment(true)}
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
                      >
                        💳 Pagos Múltiples
                      </button>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Selecciona un método simple o usa pagos múltiples para combinar varios métodos
                    </p>
                  </div>

                  {/* Notas */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Notas de la Venta
                    </label>
                    <textarea
                      placeholder="Notas adicionales..."
                      value={saleNotes}
                      onChange={(e) => setSaleNotes(e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                    />
                  </div>

                  {/* Resumen */}
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <h4 className="font-medium mb-2">Resumen de la Venta</h4>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span>Items: {cart.length}</span>
                        <span>${subtotal.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>IVA:</span>
                        <span>${tax.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between font-bold border-t pt-1">
                        <span>Total:</span>
                        <span>${total.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>

                  {/* Botones */}
                  <div className="flex space-x-3 pt-4">
                    <button
                      onClick={() => setShowCheckout(false)}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                    >
                      Cancelar
                    </button>
                    {paymentMethod.includes('_qr') || paymentMethod === 'qr_generic' ? (
                      <button
                        onClick={() => {
                          setShowCheckout(false);
                          setShowQRPayment(true);
                        }}
                        className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center justify-center space-x-2"
                      >
                        <Smartphone className="h-4 w-4" />
                        <span>Pagar con QR</span>
                      </button>
                    ) : (
                      <button
                        onClick={processSale}
                        className="flex-1 px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 flex items-center justify-center space-x-2"
                      >
                        <CheckCircle className="h-4 w-4" />
                        <span>Procesar Venta</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modal de Pago QR */}
      <QRPaymentModal
        isOpen={showQRPayment}
        onClose={() => setShowQRPayment(false)}
        amount={total}
        paymentMethod={paymentMethod}
        onPaymentConfirmed={() => {
          // Procesar la venta después de confirmar el pago QR
          processSale();
        }}
      />

      {/* Modal de Pagos Múltiples */}
      <MultiPaymentModal
        isOpen={showMultiPayment}
        onClose={() => setShowMultiPayment(false)}
        totalAmount={total}
        onConfirm={handleMultiPaymentConfirm}
      />
    </div>
  );
};

export default SalesModule;
