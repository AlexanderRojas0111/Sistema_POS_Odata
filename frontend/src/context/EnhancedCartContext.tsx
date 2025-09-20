import React, { createContext, useContext, useReducer, useEffect } from 'react';
import type { ReactNode } from 'react';
import { cartService } from '../services/cartService';
import type { Cart} from '../services/cartService';

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

type CartAction =
  | { type: 'SET_CART'; payload: Cart }
  | { type: 'ADD_ITEM'; payload: { product: Product; quantity: number } }
  | { type: 'REMOVE_ITEM'; payload: { productId: string } }
  | { type: 'UPDATE_QUANTITY'; payload: { productId: string; quantity: number } }
  | { type: 'CLEAR_CART' }
  | { type: 'TOGGLE_CART' }
  | { type: 'OPEN_CART' }
  | { type: 'CLOSE_CART' };

interface CartState extends Cart {
  isOpen: boolean;
}

interface CartContextType {
  state: CartState;
  dispatch: React.Dispatch<CartAction>;
  addToCart: (product: Product, quantity?: number) => void;
  removeFromCart: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
  toggleCart: () => void;
  createSale: (paymentMethod?: string, notes?: string) => Promise<any>;
  validateStock: () => Promise<{ valid: boolean; errors: string[] }>;
  getItemQuantity: (productId: string) => number;
  getTotalPrice: () => number;
  getTotalItems: () => number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

const cartReducer = (state: CartState, action: CartAction): CartState => {
  switch (action.type) {
    case 'SET_CART':
      return {
        ...action.payload,
        isOpen: state.isOpen
      };
    case 'ADD_ITEM': {
      const updatedCart = cartService.addToCart(action.payload.product, action.payload.quantity);
      return {
        ...updatedCart,
        isOpen: state.isOpen
      };
    }
    case 'REMOVE_ITEM': {
      const updatedCart = cartService.removeFromCart(action.payload.productId);
      return {
        ...updatedCart,
        isOpen: state.isOpen
      };
    }
    case 'UPDATE_QUANTITY': {
      const updatedCart = cartService.updateQuantity(action.payload.productId, action.payload.quantity);
      return {
        ...updatedCart,
        isOpen: state.isOpen
      };
    }
    case 'CLEAR_CART':
      return {
        ...cartService.clearCart(),
        isOpen: state.isOpen
      };
    case 'TOGGLE_CART':
      return {
        ...state,
        isOpen: !state.isOpen
      };
    case 'OPEN_CART':
      return {
        ...state,
        isOpen: true
      };
    case 'CLOSE_CART':
      return {
        ...state,
        isOpen: false
      };
    default:
      return state;
  }
};

const initialState: CartState = {
  items: [],
  total: 0,
  itemCount: 0,
  isOpen: false
};

export const EnhancedCartProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(cartReducer, initialState);

  // Cargar carrito del localStorage al inicializar
  useEffect(() => {
    const savedCart = cartService.getCart();
    dispatch({ type: 'SET_CART', payload: savedCart });
  }, []);

  const addToCart = (product: Product, quantity: number = 1) => {
    dispatch({ type: 'ADD_ITEM', payload: { product, quantity } });
    // Abrir carrito automáticamente al agregar un producto
    dispatch({ type: 'OPEN_CART' });
  };

  const removeFromCart = (productId: string) => {
    dispatch({ type: 'REMOVE_ITEM', payload: { productId } });
  };

  const updateQuantity = (productId: string, quantity: number) => {
    dispatch({ type: 'UPDATE_QUANTITY', payload: { productId, quantity } });
  };

  const clearCart = () => {
    dispatch({ type: 'CLEAR_CART' });
  };

  const toggleCart = () => {
    dispatch({ type: 'TOGGLE_CART' });
  };

  const createSale = async (paymentMethod: string = 'cash', notes?: string) => {
    try {
      const result = await cartService.createSale(paymentMethod, notes);
      // El carrito se limpia automáticamente en el servicio
      dispatch({ type: 'CLEAR_CART' });
      return result;
    } catch (error) {
      console.error('Error creando venta:', error);
      throw error;
    }
  };

  const validateStock = async () => {
    try {
      return await cartService.validateStock();
    } catch (error) {
      console.error('Error validando stock:', error);
      return { valid: false, errors: ['Error al validar stock'] };
    }
  };

  const getItemQuantity = (productId: string): number => {
    const item = state.items.find(item => item.id === productId);
    return item ? item.quantity : 0;
  };

  const getTotalPrice = (): number => {
    return state.total;
  };

  const getTotalItems = (): number => {
    return state.itemCount;
  };

  const value = {
    state,
    dispatch,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    toggleCart,
    createSale,
    validateStock,
    getItemQuantity,
    getTotalPrice,
    getTotalItems
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};

export const useEnhancedCart = () => {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useEnhancedCart must be used within an EnhancedCartProvider');
  }
  return context;
};

// Hook para formatear precios
export const usePriceFormatter = () => {
  const formatPrice = (price: number): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  return { formatPrice };
};
