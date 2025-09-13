// Tipos compartidos para el sistema Sabrositas
// ================================================

export interface Product {
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

// Tipos para el backend
export interface BackendProduct {
  id: number;
  name: string;
  sku: string;
  description: string;
  price: number;
  cost: number;
  category: string;
  stock: number;
  min_stock: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BackendUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
  last_login: string | null;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  totalSales: number;
  totalRevenue: number;
  totalProducts: number;
  totalUsers: number;
  todaySales: number;
  todayRevenue: number;
  lowStockProducts: number;
  activeUsers: number;
}

export interface RecentSale {
  id: number;
  user_name: string;
  total: number;
  created_at: string;
  items_count: number;
}

export interface TopProduct {
  id: number;
  name: string;
  sales_count: number;
  revenue: number;
}
