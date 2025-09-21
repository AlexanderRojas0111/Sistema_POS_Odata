import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import QRCode from 'react-qr-code';
import { X, Smartphone, CreditCard, RefreshCw, CheckCircle } from 'lucide-react';

interface QRPaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  amount: number;
  paymentMethod: string;
  onPaymentConfirmed: () => void;
}

interface PaymentQRData {
  amount: number;
  currency: 'COP';
  payment_method: string;
  merchant: string;
  transaction_id: string;
  timestamp: string;
  qr_data: string;
}

const QRPaymentModal: React.FC<QRPaymentModalProps> = ({
  isOpen,
  onClose,
  amount,
  paymentMethod,
  onPaymentConfirmed
}) => {
  const [paymentData, setPaymentData] = useState<PaymentQRData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState<'pending' | 'processing' | 'completed' | 'failed'>('pending');
  const [countdown, setCountdown] = useState(300); // 5 minutos

  // Generar datos de pago QR usando la API del backend
  const generatePaymentQR = async () => {
    setIsLoading(true);
    
    try {
      // Obtener token de autenticación
      const authUser = localStorage.getItem('auth:user');
      const token = authUser ? JSON.parse(authUser).token : null;
      
      if (!token) {
        throw new Error('No hay token de autenticación');
      }
      
      // Llamar a la API del backend para generar QR
      const response = await fetch('http://localhost:8000/api/v1/qr-payments/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          amount: amount,
          payment_method: paymentMethod,
          merchant_name: 'Sistema POS Sabrositas'
        })
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || 'Error generando QR');
      }
      
      const result = await response.json();
      const qrData: PaymentQRData = {
        amount: result.data.amount,
        currency: 'COP',
        payment_method: result.data.payment_method,
        merchant: result.data.merchant_name,
        transaction_id: result.data.transaction_id,
        timestamp: result.data.created_at,
        qr_data: result.data.qr_data
      };
      
      setPaymentData(qrData);
      setPaymentStatus('pending');
      setCountdown(300);
      
    } catch (error) {
      console.error('Error generando QR:', error);
      alert('Error generando código QR: ' + (error instanceof Error ? error.message : String(error)));
    } finally {
      setIsLoading(false);
    }
  };

  // Verificar estado de pago usando la API del backend
  const checkPaymentStatus = async () => {
    if (!paymentData) return;
    
    setPaymentStatus('processing');
    
    try {
      // Obtener token de autenticación
      const authUser = localStorage.getItem('auth:user');
      const token = authUser ? JSON.parse(authUser).token : null;
      
      if (!token) {
        throw new Error('No hay token de autenticación');
      }
      
      // Llamar a la API del backend para verificar pago
      const response = await fetch(`http://localhost:8000/api/v1/qr-payments/verify/${paymentData.transaction_id}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error?.message || 'Error verificando pago');
      }
      
      const result = await response.json();
      const paymentStatus = result.data.status;
      
      if (paymentStatus === 'completed') {
        setPaymentStatus('completed');
        setTimeout(() => {
          onPaymentConfirmed();
          onClose();
        }, 2000);
      } else if (paymentStatus === 'failed' || paymentStatus === 'expired') {
        setPaymentStatus('failed');
      } else {
        setPaymentStatus('pending');
      }
      
    } catch (error) {
      console.error('Error verificando pago:', error);
      setPaymentStatus('failed');
    }
  };

  // Countdown timer
  useEffect(() => {
    if (countdown > 0 && paymentStatus === 'pending') {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else if (countdown === 0 && paymentStatus === 'pending') {
      setPaymentStatus('failed');
    }
  }, [countdown, paymentStatus]);

  // Generar QR cuando se abre el modal
  useEffect(() => {
    if (isOpen && !paymentData) {
      generatePaymentQR();
    }
  }, [isOpen]);

  const getPaymentMethodInfo = () => {
    switch (paymentMethod) {
      case 'nequi_qr':
        return {
          name: 'Nequi QR',
          icon: '📱',
          instructions: 'Escanee el código QR con la app de Nequi y confirme el pago',
          color: 'bg-purple-500'
        };
      case 'daviplata_qr':
        return {
          name: 'Daviplata QR',
          icon: '🟣',
          instructions: 'Escanee el código QR con la app de Daviplata y confirme el pago',
          color: 'bg-purple-600'
        };
      case 'qr_generic':
        return {
          name: 'Pago QR Genérico',
          icon: '📲',
          instructions: 'Escanee el código QR con su app bancaria favorita',
          color: 'bg-blue-500'
        };
      default:
        return {
          name: 'Pago QR',
          icon: '📲',
          instructions: 'Escanee el código QR para realizar el pago',
          color: 'bg-blue-500'
        };
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const paymentInfo = getPaymentMethodInfo();

  return (
    <AnimatePresence>
      {isOpen && (
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
              {/* Header */}
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center space-x-2">
                  <Smartphone className="h-6 w-6 text-blue-500" />
                  <h3 className="text-lg font-semibold">Pago con QR</h3>
                </div>
                <button
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                  title="Cerrar modal"
                  aria-label="Cerrar modal"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              {/* Payment Method Info */}
              <div className={`${paymentInfo.color} text-white p-4 rounded-lg mb-4`}>
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{paymentInfo.icon}</span>
                  <div>
                    <h4 className="font-semibold">{paymentInfo.name}</h4>
                    <p className="text-sm opacity-90">
                      ${amount.toLocaleString()} COP
                    </p>
                  </div>
                </div>
              </div>

              {/* QR Code */}
              <div className="text-center mb-4">
                {isLoading ? (
                  <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                  </div>
                ) : paymentData ? (
                  <div className="bg-white p-4 rounded-lg border-2 border-gray-200 inline-block">
                    <QRCode
                      value={paymentData.qr_data}
                      size={200}
                      level="M"
                    />
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-gray-500">
                    Error generando QR
                  </div>
                )}
              </div>

              {/* Instructions */}
              <div className="bg-gray-50 p-4 rounded-lg mb-4">
                <p className="text-sm text-gray-700 text-center">
                  {paymentInfo.instructions}
                </p>
              </div>

              {/* Status */}
              {paymentData && (
                <div className="mb-4">
                  {paymentStatus === 'pending' && (
                    <div className="text-center">
                      <div className="flex items-center justify-center space-x-2 text-orange-600 mb-2">
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        <span className="text-sm font-medium">Esperando pago...</span>
                      </div>
                      <div className="text-xs text-gray-500">
                        Tiempo restante: {formatTime(countdown)}
                      </div>
                    </div>
                  )}
                  
                  {paymentStatus === 'processing' && (
                    <div className="text-center">
                      <div className="flex items-center justify-center space-x-2 text-blue-600 mb-2">
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        <span className="text-sm font-medium">Verificando pago...</span>
                      </div>
                    </div>
                  )}
                  
                  {paymentStatus === 'completed' && (
                    <div className="text-center">
                      <div className="flex items-center justify-center space-x-2 text-green-600 mb-2">
                        <CheckCircle className="h-4 w-4" />
                        <span className="text-sm font-medium">¡Pago confirmado!</span>
                      </div>
                      <p className="text-xs text-gray-500">
                        Procesando venta...
                      </p>
                    </div>
                  )}
                  
                  {paymentStatus === 'failed' && (
                    <div className="text-center">
                      <div className="flex items-center justify-center space-x-2 text-red-600 mb-2">
                        <X className="h-4 w-4" />
                        <span className="text-sm font-medium">Pago falló o expiró</span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Actions */}
              <div className="flex space-x-3">
                <button
                  onClick={onClose}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
                
                {paymentStatus === 'pending' && (
                  <button
                    onClick={checkPaymentStatus}
                    className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    Verificar Pago
                  </button>
                )}
                
                {paymentStatus === 'failed' && (
                  <button
                    onClick={generatePaymentQR}
                    className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    Generar Nuevo QR
                  </button>
                )}
              </div>

              {/* Transaction Info */}
              {paymentData && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="text-xs text-gray-500 space-y-1">
                    <div>ID: {paymentData.transaction_id}</div>
                    <div>Hora: {new Date(paymentData.timestamp).toLocaleTimeString()}</div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default QRPaymentModal;
