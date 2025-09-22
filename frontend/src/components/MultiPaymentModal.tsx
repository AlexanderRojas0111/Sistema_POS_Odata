import React, { useState, useEffect } from 'react';

interface PaymentMethod {
  method: string;
  amount: number;
  reference?: string;
  bank_name?: string;
  card_last_four?: string;
  phone_number?: string;
  qr_code?: string;
  notes?: string;
}

interface PaymentMethodInfo {
  name: string;
  description: string;
  requires_reference: boolean;
  requires_phone: boolean;
  requires_bank: boolean;
  allows_change: boolean;
}

interface MultiPaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  totalAmount: number;
  onConfirm: (payments: PaymentMethod[], changeAmount: number) => void;
}

const MultiPaymentModal: React.FC<MultiPaymentModalProps> = ({
  isOpen,
  onClose,
  totalAmount,
  onConfirm
}) => {
  const [paymentMethods, setPaymentMethods] = useState<{[key: string]: string}>({});
  const [currentPayments, setCurrentPayments] = useState<PaymentMethod[]>([]);
  const [availableCash, setAvailableCash] = useState<number>(0);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [totalPaid, setTotalPaid] = useState<number>(0);
  const [remainingAmount, setRemainingAmount] = useState<number>(totalAmount);
  const [changeAmount, setChangeAmount] = useState<number>(0);

  // Cargar métodos de pago disponibles
  useEffect(() => {
    const loadPaymentMethods = async () => {
      try {
        const response = await fetch('/api/v1/multi-payment/methods');
        const data = await response.json();
        if (data.success) {
          setPaymentMethods(data.data);
        }
      } catch (error) {
        console.error('Error cargando métodos de pago:', error);
      }
    };

    if (isOpen) {
      loadPaymentMethods();
      loadSuggestions();
    }
  }, [isOpen, totalAmount, availableCash]);

  // Cargar sugerencias de pago
  const loadSuggestions = async () => {
    try {
      const response = await fetch('/api/v1/multi-payment/suggestions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          total_amount: totalAmount,
          available_cash: availableCash
        })
      });
      const data = await response.json();
      if (data.success) {
        setSuggestions(data.data);
      }
    } catch (error) {
      console.error('Error cargando sugerencias:', error);
    }
  };

  // Calcular totales
  useEffect(() => {
    const total = currentPayments.reduce((sum, payment) => sum + payment.amount, 0);
    setTotalPaid(total);
    setRemainingAmount(totalAmount - total);
    
    // Calcular cambio solo para pagos en efectivo
    const cashPayments = currentPayments.filter(p => p.method === 'cash');
    const cashTotal = cashPayments.reduce((sum, payment) => sum + payment.amount, 0);
    setChangeAmount(Math.max(0, cashTotal - totalAmount));
  }, [currentPayments, totalAmount]);

  // Agregar nuevo pago
  const addPayment = () => {
    setCurrentPayments([...currentPayments, {
      method: 'cash',
      amount: remainingAmount,
      reference: ''
    }]);
  };

  // Remover pago
  const removePayment = (index: number) => {
    const newPayments = currentPayments.filter((_, i) => i !== index);
    setCurrentPayments(newPayments);
  };

  // Actualizar pago
  const updatePayment = (index: number, field: string, value: any) => {
    const newPayments = [...currentPayments];
    newPayments[index] = { ...newPayments[index], [field]: value };
    setCurrentPayments(newPayments);
  };

  // Aplicar sugerencia
  const applySuggestion = (suggestion: any) => {
    setCurrentPayments(suggestion.payments);
    setShowSuggestions(false);
  };

  // Validar y confirmar
  const handleConfirm = async () => {
    if (remainingAmount > 0) {
      alert(`Falta por pagar: $${remainingAmount.toLocaleString()}`);
      return;
    }

    // Validar combinación
    try {
      const response = await fetch('/api/v1/multi-payment/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          payments: currentPayments,
          total_amount: totalAmount
        })
      });
      const data = await response.json();
      
      if (data.success && data.valid) {
        onConfirm(currentPayments, changeAmount);
        onClose();
      } else {
        alert(`Error de validación: ${data.message}`);
      }
    } catch (error) {
      console.error('Error validando pagos:', error);
      alert('Error al validar los pagos');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            💳 Pagos Múltiples
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Resumen de la venta */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-sm text-gray-600">Total Venta</div>
              <div className="text-lg font-bold text-amber-600">
                ${totalAmount.toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Total Pagado</div>
              <div className="text-lg font-bold text-green-600">
                ${totalPaid.toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Restante</div>
              <div className={`text-lg font-bold ${remainingAmount > 0 ? 'text-red-600' : 'text-green-600'}`}>
                ${remainingAmount.toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Cambio</div>
              <div className="text-lg font-bold text-blue-600">
                ${changeAmount.toLocaleString()}
              </div>
            </div>
          </div>
        </div>

        {/* Efectivo disponible */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            💵 Efectivo Disponible (Opcional)
          </label>
          <input
            type="number"
            value={availableCash}
            onChange={(e) => setAvailableCash(Number(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            placeholder="0"
          />
        </div>

        {/* Sugerencias */}
        {suggestions.length > 0 && (
          <div className="mb-6">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-semibold text-gray-800">
                💡 Sugerencias de Pago
              </h3>
              <button
                onClick={() => setShowSuggestions(!showSuggestions)}
                className="text-amber-600 hover:text-amber-700 text-sm"
              >
                {showSuggestions ? 'Ocultar' : 'Ver sugerencias'}
              </button>
            </div>
            
            {showSuggestions && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => applySuggestion(suggestion)}
                    className="p-3 border border-gray-200 rounded-lg hover:border-amber-300 hover:bg-amber-50 text-left"
                  >
                    <div className="font-medium text-gray-800">{suggestion.name}</div>
                    <div className="text-sm text-gray-600">{suggestion.description}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {suggestion.payments.map((p: any, i: number) => (
                        <span key={i}>
                          {paymentMethods[p.method]} ${p.amount.toLocaleString()}
                          {i < suggestion.payments.length - 1 ? ' + ' : ''}
                        </span>
                      ))}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Lista de pagos */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-semibold text-gray-800">
              📋 Pagos Agregados
            </h3>
            <button
              onClick={addPayment}
              className="bg-amber-500 text-white px-4 py-2 rounded-lg hover:bg-amber-600 transition-colors"
            >
              + Agregar Pago
            </button>
          </div>

          {currentPayments.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No hay pagos agregados. Haz clic en "Agregar Pago" para comenzar.
            </div>
          ) : (
            <div className="space-y-3">
              {currentPayments.map((payment, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {/* Método de pago */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Método
                      </label>
                      <select
                        value={payment.method}
                        onChange={(e) => updatePayment(index, 'method', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                        title="Seleccionar método de pago"
                        aria-label="Seleccionar método de pago"
                      >
                        {Object.entries(paymentMethods).map(([key, value]) => (
                          <option key={key} value={key}>{value}</option>
                        ))}
                      </select>
                    </div>

                    {/* Monto */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Monto
                      </label>
                      <input
                        type="number"
                        value={payment.amount}
                        onChange={(e) => updatePayment(index, 'amount', Number(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                        placeholder="0"
                      />
                    </div>

                    {/* Referencia */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Referencia
                      </label>
                      <input
                        type="text"
                        value={payment.reference || ''}
                        onChange={(e) => updatePayment(index, 'reference', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                        placeholder="Número de transacción"
                      />
                    </div>

                    {/* Acciones */}
                    <div className="flex items-end">
                      <button
                        onClick={() => removePayment(index)}
                        className="w-full bg-red-500 text-white px-3 py-2 rounded-lg hover:bg-red-600 transition-colors"
                      >
                        🗑️ Eliminar
                      </button>
                    </div>
                  </div>

                  {/* Campos adicionales según el método */}
                  {(payment.method === 'card' || payment.method === 'nequi' || payment.method === 'daviplata') && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Teléfono
                        </label>
                        <input
                          type="tel"
                          value={payment.phone_number || ''}
                          onChange={(e) => updatePayment(index, 'phone_number', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                          placeholder="3001234567"
                        />
                      </div>
                      {payment.method === 'card' && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Últimos 4 dígitos
                          </label>
                          <input
                            type="text"
                            value={payment.card_last_four || ''}
                            onChange={(e) => updatePayment(index, 'card_last_four', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                            placeholder="1234"
                            maxLength={4}
                          />
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Botones de acción */}
        <div className="flex justify-end space-x-4">
          <button
            onClick={onClose}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleConfirm}
            disabled={remainingAmount > 0}
            className={`px-6 py-2 rounded-lg transition-colors ${
              remainingAmount > 0
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-green-500 text-white hover:bg-green-600'
            }`}
          >
            ✅ Confirmar Pago
          </button>
        </div>
      </div>
    </div>
  );
};

export default MultiPaymentModal;
