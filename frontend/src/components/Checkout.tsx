import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CreditCard, 
  Banknote, 
  Smartphone, 
  CheckCircle, 
  AlertCircle,
  X,
  ShoppingBag,
  User,
  Receipt
} from 'lucide-react';
import { useEnhancedCart } from '../context/EnhancedCartContext';
import { usePriceFormatter } from '../context/EnhancedCartContext';

interface CheckoutProps {
  isOpen: boolean;
  onClose: () => void;
}

const Checkout: React.FC<CheckoutProps> = ({ isOpen, onClose }) => {
  const { state, createSale, validateStock } = useEnhancedCart();
  const { formatPrice } = usePriceFormatter();
  
  const [paymentMethod, setPaymentMethod] = useState<'cash' | 'card' | 'digital'>('cash');
  const [customerName, setCustomerName] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [notes, setNotes] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [saleResult, setSaleResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'details' | 'payment' | 'confirmation'>('details');

  const paymentMethods = [
    {
      id: 'cash' as const,
      name: 'Efectivo',
      icon: Banknote,
      description: 'Pago en efectivo'
    },
    {
      id: 'card' as const,
      name: 'Tarjeta',
      icon: CreditCard,
      description: 'Pago con tarjeta'
    },
    {
      id: 'digital' as const,
      name: 'Digital',
      icon: Smartphone,
      description: 'Pago digital'
    }
  ];

  const handleProcessSale = async () => {
    if (state.items.length === 0) {
      setError('El carrito está vacío');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      // Validar stock antes de procesar
      const stockValidation = await validateStock();
      if (!stockValidation.valid) {
        setError(`Error de stock: ${stockValidation.errors.join(', ')}`);
        setIsProcessing(false);
        return;
      }

      // Crear la venta
      const result = await createSale(paymentMethod, notes);
      setSaleResult(result);
      setStep('confirmation');
      
    } catch (err: any) {
      setError(err.message || 'Error al procesar la venta');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClose = () => {
    if (step === 'confirmation') {
      // Reset form
      setStep('details');
      setCustomerName('');
      setCustomerEmail('');
      setCustomerPhone('');
      setNotes('');
      setPaymentMethod('cash');
      setSaleResult(null);
      setError(null);
    }
    onClose();
  };

  const handleNextStep = () => {
    if (step === 'details') {
      setStep('payment');
    } else if (step === 'payment') {
      handleProcessSale();
    }
  };

  const handlePrevStep = () => {
    if (step === 'payment') {
      setStep('details');
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
        onClick={(e) => e.target === e.currentTarget && handleClose()}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white rounded-2xl shadow-amber-lg max-w-2xl w-full max-h-[90vh] overflow-hidden"
        >
          {/* Header */}
          <div className="bg-gradient-amber text-white p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <ShoppingBag className="w-6 h-6" />
                <div>
                  <h2 className="text-2xl font-bold">Checkout</h2>
                  <p className="text-amber-100">
                    {step === 'details' && 'Información del cliente'}
                    {step === 'payment' && 'Método de pago'}
                    {step === 'confirmation' && 'Confirmación de venta'}
                  </p>
                </div>
              </div>
              <button
                onClick={handleClose}
                className="text-white hover:text-amber-200 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Progress Steps */}
          <div className="px-6 py-4 bg-gray-50">
            <div className="flex items-center justify-between">
              {['details', 'payment', 'confirmation'].map((stepName, index) => (
                <div key={stepName} className="flex items-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                    step === stepName 
                      ? 'bg-sabrositas-primary text-white' 
                      : step === 'confirmation' && saleResult
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-300 text-gray-600'
                  }`}>
                    {step === 'confirmation' && saleResult ? (
                      <CheckCircle className="w-4 h-4" />
                    ) : (
                      index + 1
                    )}
                  </div>
                  <div className="ml-2 text-sm font-medium text-gray-700 capitalize">
                    {stepName === 'details' && 'Cliente'}
                    {stepName === 'payment' && 'Pago'}
                    {stepName === 'confirmation' && 'Confirmar'}
                  </div>
                  {index < 2 && (
                    <div className={`w-8 h-0.5 mx-4 ${
                      step === 'confirmation' && saleResult 
                        ? 'bg-green-500' 
                        : 'bg-gray-300'
                    }`} />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="p-6 max-h-[60vh] overflow-y-auto">
            <AnimatePresence mode="wait">
              {/* Step 1: Customer Details */}
              {step === 'details' && (
                <motion.div
                  key="details"
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  exit={{ x: 20, opacity: 0 }}
                  className="space-y-6"
                >
                  <div className="flex items-center space-x-3 mb-6">
                    <User className="w-6 h-6 text-sabrositas-primary" />
                    <h3 className="text-xl font-bold text-gray-900">Información del Cliente</h3>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nombre del Cliente *
                      </label>
                      <input
                        type="text"
                        value={customerName}
                        onChange={(e) => setCustomerName(e.target.value)}
                        className="input-field"
                        placeholder="Ingresa el nombre del cliente"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Teléfono
                      </label>
                      <input
                        type="tel"
                        value={customerPhone}
                        onChange={(e) => setCustomerPhone(e.target.value)}
                        className="input-field"
                        placeholder="Número de teléfono"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      value={customerEmail}
                      onChange={(e) => setCustomerEmail(e.target.value)}
                      className="input-field"
                      placeholder="correo@ejemplo.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Notas adicionales
                    </label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      className="input-field"
                      rows={3}
                      placeholder="Notas especiales para la orden..."
                    />
                  </div>
                </motion.div>
              )}

              {/* Step 2: Payment Method */}
              {step === 'payment' && (
                <motion.div
                  key="payment"
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  exit={{ x: 20, opacity: 0 }}
                  className="space-y-6"
                >
                  <div className="flex items-center space-x-3 mb-6">
                    <CreditCard className="w-6 h-6 text-sabrositas-primary" />
                    <h3 className="text-xl font-bold text-gray-900">Método de Pago</h3>
                  </div>

                  <div className="grid grid-cols-1 gap-4">
                    {paymentMethods.map((method) => {
                      const Icon = method.icon;
                      return (
                        <button
                          key={method.id}
                          onClick={() => setPaymentMethod(method.id)}
                          className={`p-4 rounded-xl border-2 transition-all duration-300 ${
                            paymentMethod === method.id
                              ? 'border-sabrositas-primary bg-amber-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <div className="flex items-center space-x-4">
                            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                              paymentMethod === method.id
                                ? 'bg-sabrositas-primary text-white'
                                : 'bg-gray-100 text-gray-600'
                            }`}>
                              <Icon className="w-6 h-6" />
                            </div>
                            <div className="text-left">
                              <h4 className="font-semibold text-gray-900">{method.name}</h4>
                              <p className="text-sm text-gray-600">{method.description}</p>
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>

                  {/* Order Summary */}
                  <div className="bg-gray-50 rounded-xl p-4">
                    <h4 className="font-semibold text-gray-900 mb-3">Resumen del Pedido</h4>
                    <div className="space-y-2">
                      {state.items.map((item) => (
                        <div key={item.id} className="flex justify-between text-sm">
                          <span className="text-gray-600">
                            {item.product.name} x{item.quantity}
                          </span>
                          <span className="font-medium">{formatPrice(item.total)}</span>
                        </div>
                      ))}
                    </div>
                    <div className="border-t pt-2 mt-3">
                      <div className="flex justify-between font-bold text-lg">
                        <span>Total:</span>
                        <span className="text-sabrositas-primary">{formatPrice(state.total)}</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Step 3: Confirmation */}
              {step === 'confirmation' && saleResult && (
                <motion.div
                  key="confirmation"
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  exit={{ x: 20, opacity: 0 }}
                  className="text-center space-y-6"
                >
                  <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                    <CheckCircle className="w-10 h-10 text-green-600" />
                  </div>
                  
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">¡Venta Exitosa!</h3>
                    <p className="text-gray-600">La venta se ha procesado correctamente</p>
                  </div>

                  <div className="bg-gray-50 rounded-xl p-4 text-left">
                    <div className="flex items-center space-x-2 mb-3">
                      <Receipt className="w-5 h-5 text-sabrositas-primary" />
                      <h4 className="font-semibold">Detalles de la Venta</h4>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Número de Venta:</span>
                        <span className="font-medium">#{saleResult.id}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Cliente:</span>
                        <span className="font-medium">{saleResult.user_name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total:</span>
                        <span className="font-medium">{formatPrice(saleResult.total)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Método de Pago:</span>
                        <span className="font-medium capitalize">{saleResult.payment_method}</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-3"
              >
                <AlertCircle className="w-5 h-5 text-red-600" />
                <p className="text-red-800">{error}</p>
              </motion.div>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 bg-gray-50 border-t flex justify-between">
            {step !== 'confirmation' && (
              <button
                onClick={step === 'payment' ? handlePrevStep : handleClose}
                className="btn-secondary"
              >
                {step === 'payment' ? 'Anterior' : 'Cancelar'}
              </button>
            )}
            
            <div className="flex space-x-3">
              {step === 'details' && (
                <button
                  onClick={handleNextStep}
                  disabled={!customerName.trim()}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Continuar
                </button>
              )}
              
              {step === 'payment' && (
                <button
                  onClick={handleProcessSale}
                  disabled={isProcessing}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  {isProcessing ? (
                    <>
                      <div className="spinner w-4 h-4"></div>
                      <span>Procesando...</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4" />
                      <span>Confirmar Venta</span>
                    </>
                  )}
                </button>
              )}
              
              {step === 'confirmation' && (
                <button
                  onClick={handleClose}
                  className="btn-primary"
                >
                  Finalizar
                </button>
              )}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default Checkout;
