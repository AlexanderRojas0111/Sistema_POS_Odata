// Definir el tipo Product localmente para evitar problemas de importación
interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category: 'Sencillas' | 'Clásicas' | 'Premium' | 'Dulces' | 'Picantes';
  ingredients: string[];
  image: string;
  popular?: boolean;
  new?: boolean;
  spicy?: boolean;
}

export interface CartItem {
  id: string;
  product: Product;
  quantity: number;
  price: number;
  total: number;
}

export interface Cart {
  items: CartItem[];
  total: number;
  itemCount: number;
}

export interface SaleItem {
  product_id: number;
  quantity: number;
  price: number;
  total: number;
}

export interface CreateSaleRequest {
  user_id: string;
  items: SaleItem[];
  total: number;
  payment_method: string;
  notes?: string;
}

export interface SaleResponse {
  id: number;
  user_name: string;
  total: number;
  created_at: string;
  items: SaleItem[];
  payment_method: string;
  status: string;
}

class CartService {
  private baseUrl = 'http://localhost:8000/api/v1';
  
  // Obtener token de autenticación
  private getAuthToken(): string | null {
    return localStorage.getItem('token');
  }

  // Headers de autenticación
  private getHeaders(): HeadersInit {
    const token = this.getAuthToken();
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  // Obtener carrito del localStorage
  getCart(): Cart {
    try {
      const cartData = localStorage.getItem('sabrositas_cart');
      if (cartData) {
        return JSON.parse(cartData);
      }
    } catch (error) {
      console.error('Error al cargar carrito:', error);
    }
    
    return {
      items: [],
      total: 0,
      itemCount: 0
    };
  }

  // Guardar carrito en localStorage
  private saveCart(cart: Cart): void {
    try {
      localStorage.setItem('sabrositas_cart', JSON.stringify(cart));
    } catch (error) {
      console.error('Error al guardar carrito:', error);
    }
  }

  // Agregar producto al carrito
  addToCart(product: Product, quantity: number = 1): Cart {
    const cart = this.getCart();
    const existingItem = cart.items.find(item => item.id === product.id);

    if (existingItem) {
      existingItem.quantity += quantity;
      existingItem.total = existingItem.quantity * existingItem.price;
    } else {
      const newItem: CartItem = {
        id: product.id,
        product,
        quantity,
        price: product.price,
        total: product.price * quantity
      };
      cart.items.push(newItem);
    }

    // Recalcular totales
    cart.total = cart.items.reduce((sum, item) => sum + item.total, 0);
    cart.itemCount = cart.items.reduce((sum, item) => sum + item.quantity, 0);

    this.saveCart(cart);
    return cart;
  }

  // Remover producto del carrito
  removeFromCart(productId: string): Cart {
    const cart = this.getCart();
    cart.items = cart.items.filter(item => item.id !== productId);
    
    // Recalcular totales
    cart.total = cart.items.reduce((sum, item) => sum + item.total, 0);
    cart.itemCount = cart.items.reduce((sum, item) => sum + item.quantity, 0);

    this.saveCart(cart);
    return cart;
  }

  // Actualizar cantidad de producto
  updateQuantity(productId: string, quantity: number): Cart {
    const cart = this.getCart();
    const item = cart.items.find(item => item.id === productId);

    if (item) {
      if (quantity <= 0) {
        return this.removeFromCart(productId);
      }
      
      item.quantity = quantity;
      item.total = item.quantity * item.price;
      
      // Recalcular totales
      cart.total = cart.items.reduce((sum, item) => sum + item.total, 0);
      cart.itemCount = cart.items.reduce((sum, item) => sum + item.quantity, 0);

      this.saveCart(cart);
    }

    return cart;
  }

  // Limpiar carrito
  clearCart(): Cart {
    const emptyCart: Cart = {
      items: [],
      total: 0,
      itemCount: 0
    };
    this.saveCart(emptyCart);
    return emptyCart;
  }

  // Validar stock de productos
  async validateStock(): Promise<{ valid: boolean; errors: string[] }> {
    const cart = this.getCart();
    const errors: string[] = [];

    try {
      // Verificar stock para cada producto
      for (const item of cart.items) {
        const response = await fetch(`${this.baseUrl}/products/${item.product.id}`, {
          headers: this.getHeaders()
        });

        if (response.ok) {
          const productData = await response.json();
          const product = productData.data;
          
          if (product.stock < item.quantity) {
            errors.push(`${item.product.name}: Stock disponible ${product.stock}, solicitado ${item.quantity}`);
          }
        } else {
          errors.push(`${item.product.name}: No se pudo verificar stock`);
        }
      }
    } catch (error) {
      console.error('Error validando stock:', error);
      errors.push('Error al validar stock de productos');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  // Crear venta
  async createSale(paymentMethod: string = 'cash', notes?: string): Promise<SaleResponse> {
    const token = this.getAuthToken();
    if (!token) {
      throw new Error('No autorizado. Por favor, inicia sesión.');
    }

    const cart = this.getCart();
    if (cart.items.length === 0) {
      throw new Error('El carrito está vacío');
    }

    // Validar stock antes de crear la venta
    const stockValidation = await this.validateStock();
    if (!stockValidation.valid) {
      throw new Error(`Error de stock: ${stockValidation.errors.join(', ')}`);
    }

    // Obtener información del usuario actual
    const userResponse = await fetch(`${this.baseUrl}/users/me`, {
      headers: this.getHeaders()
    });

    if (!userResponse.ok) {
      throw new Error('No se pudo obtener información del usuario');
    }

    const userData = await userResponse.json();
    const userId = userData.data.username || userData.data.id;

    // Preparar items para la venta
    const saleItems: SaleItem[] = cart.items.map(item => ({
      product_id: parseInt(item.product.id),
      quantity: item.quantity,
      price: item.price,
      total: item.total
    }));

    // Crear request de venta
    const saleRequest: CreateSaleRequest = {
      user_id: userId,
      items: saleItems,
      total: cart.total,
      payment_method: paymentMethod,
      notes
    };

    // Enviar venta al backend
    const response = await fetch(`${this.baseUrl}/sales`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(saleRequest)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `Error del servidor: ${response.status}`);
    }

    const saleData = await response.json();
    
    // Limpiar carrito después de venta exitosa
    this.clearCart();

    return saleData.data;
  }

  // Obtener historial de ventas
  async getSalesHistory(limit: number = 10): Promise<SaleResponse[]> {
    try {
      const response = await fetch(`${this.baseUrl}/sales?limit=${limit}`, {
        headers: this.getHeaders()
      });

      if (!response.ok) {
        throw new Error(`Error del servidor: ${response.status}`);
      }

      const data = await response.json();
      return data.data?.sales || [];
    } catch (error) {
      console.error('Error obteniendo historial de ventas:', error);
      throw error;
    }
  }

  // Obtener detalles de una venta
  async getSaleDetails(saleId: number): Promise<SaleResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/sales/${saleId}`, {
        headers: this.getHeaders()
      });

      if (!response.ok) {
        throw new Error(`Error del servidor: ${response.status}`);
      }

      const data = await response.json();
      return data.data;
    } catch (error) {
      console.error('Error obteniendo detalles de venta:', error);
      throw error;
    }
  }
}

export const cartService = new CartService();
