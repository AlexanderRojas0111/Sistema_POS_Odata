import React, { useEffect } from 'react';
import { useEnhancedCart } from '../context/EnhancedCartContext';

interface CartUpdaterProps {
  onCartUpdate: (itemCount: number) => void;
}

const CartUpdater: React.FC<CartUpdaterProps> = ({ onCartUpdate }) => {
  const { getTotalItems } = useEnhancedCart();

  useEffect(() => {
    const updateCartCount = () => {
      onCartUpdate(getTotalItems());
    };

    // Actualizar inmediatamente
    updateCartCount();

    // Escuchar cambios en localStorage para sincronizar entre pestañas
    const handleStorageChange = () => {
      updateCartCount();
    };

    window.addEventListener('storage', handleStorageChange);
    
    // Actualizar cada segundo para sincronizar
    const interval = setInterval(updateCartCount, 1000);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, [getTotalItems, onCartUpdate]);

  return null; // Este componente no renderiza nada
};

export default CartUpdater;
