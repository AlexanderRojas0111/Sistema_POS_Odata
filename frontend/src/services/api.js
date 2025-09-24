import axios from 'axios';

// Configuración base de la API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Crear instancia de axios con configuración base
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token de autenticación
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas y errores
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Manejar errores de autenticación
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    
    // Manejar errores de red
    if (!error.response) {
      console.error('Error de red:', error.message);
      return Promise.reject(new Error('Error de conexión. Verifique su conexión a internet.'));
    }
    
    // Manejar errores del servidor
    const errorMessage = error.response?.data?.message || error.response?.data?.error || 'Error del servidor';
    console.error('Error de API:', errorMessage);
    
    return Promise.reject(new Error(errorMessage));
  }
);

// Funciones helper para las APIs
export const productAPI = {
  // Obtener productos
  getProducts: (params = {}) => api.get('/api/v1/products/', { params }),
  
  // Obtener producto por ID
  getProduct: (id) => api.get(`/api/v1/products/${id}`),
  
  // Crear producto
  createProduct: (data) => api.post('/api/v1/products/', data),
  
  // Actualizar producto
  updateProduct: (id, data) => api.put(`/api/v1/products/${id}`, data),
  
  // Eliminar producto
  deleteProduct: (id) => api.delete(`/api/v1/products/${id}`),
  
  // Búsqueda semántica
  semanticSearch: (query, params = {}) => 
    api.get('/api/v2/search/semantic', { params: { q: query, ...params } }),
  
  // Búsqueda híbrida
  hybridSearch: (query, params = {}) => 
    api.get('/api/v2/search/hybrid', { params: { q: query, ...params } }),
};

export const salesAPI = {
  // Obtener ventas
  getSales: (params = {}) => api.get('/api/v1/sales/', { params }),
  
  // Obtener venta por ID
  getSale: (id) => api.get(`/api/v1/sales/${id}`),
  
  // Crear venta
  createSale: (data) => api.post('/api/v1/sales/', data),
  
  // Actualizar venta
  updateSale: (id, data) => api.put(`/api/v1/sales/${id}`, data),
  
  // Eliminar venta
  deleteSale: (id) => api.delete(`/api/v1/sales/${id}`),
  
  // Obtener reportes de ventas
  getSalesReport: (params = {}) => api.get('/api/v1/sales/report', { params }),
};

export const inventoryAPI = {
  // Obtener inventario
  getInventory: (params = {}) => api.get('/api/v1/inventory/', { params }),
  
  // Obtener item de inventario por ID
  getInventoryItem: (id) => api.get(`/api/v1/inventory/${id}`),
  
  // Actualizar inventario
  updateInventory: (id, data) => api.put(`/api/v1/inventory/${id}`, data),
  
  // Agregar movimiento de inventario
  addMovement: (data) => api.post('/api/v1/inventory/movements', data),
  
  // Obtener movimientos de inventario
  getMovements: (params = {}) => api.get('/api/v1/inventory/movements', { params }),
  
  // Obtener reportes de inventario
  getInventoryReport: (params = {}) => api.get('/api/v1/inventory/report', { params }),
};

export const customerAPI = {
  // Obtener clientes
  getCustomers: (params = {}) => api.get('/api/v1/customers/', { params }),
  
  // Obtener cliente por ID
  getCustomer: (id) => api.get(`/api/v1/customers/${id}`),
  
  // Crear cliente
  createCustomer: (data) => api.post('/api/v1/customers/', data),
  
  // Actualizar cliente
  updateCustomer: (id, data) => api.put(`/api/v1/customers/${id}`, data),
  
  // Eliminar cliente
  deleteCustomer: (id) => api.delete(`/api/v1/customers/${id}`),
};

export const userAPI = {
  // Login
  login: (credentials) => api.post('/api/v1/auth/login', credentials),
  
  // Logout
  logout: () => api.post('/api/v1/auth/logout'),
  
  // Obtener perfil del usuario
  getProfile: () => api.get('/api/v1/auth/profile'),
  
  // Actualizar perfil
  updateProfile: (data) => api.put('/api/v1/auth/profile', data),
  
  // Obtener usuarios
  getUsers: (params = {}) => api.get('/api/v1/users/', { params }),
  
  // Crear usuario
  createUser: (data) => api.post('/api/v1/users/', data),
  
  // Actualizar usuario
  updateUser: (id, data) => api.put(`/api/v1/users/${id}`, data),
  
  // Eliminar usuario
  deleteUser: (id) => api.delete(`/api/v1/users/${id}`),
};

export const agentsAPI = {
  // Obtener estado de agentes
  getAgentsStatus: () => api.get('/api/v2/agents/status'),
  
  // Ejecutar tarea de agente
  executeAgentTask: (agentId, task) => api.post(`/api/v2/agents/${agentId}/tasks`, task),
  
  // Obtener logs de agentes
  getAgentLogs: (params = {}) => api.get('/api/v2/agents/logs', { params }),
};

// Función para manejar errores de forma consistente
export const handleAPIError = (error) => {
  if (error.response) {
    // Error del servidor
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return `Error de validación: ${data.message || 'Datos inválidos'}`;
      case 401:
        return 'No autorizado. Inicie sesión nuevamente.';
      case 403:
        return 'Acceso denegado. No tiene permisos para esta acción.';
      case 404:
        return 'Recurso no encontrado.';
      case 422:
        return `Error de validación: ${data.message || 'Datos inválidos'}`;
      case 500:
        return 'Error interno del servidor. Intente más tarde.';
      default:
        return data.message || 'Error desconocido';
    }
  } else if (error.request) {
    // Error de red
    return 'Error de conexión. Verifique su conexión a internet.';
  } else {
    // Error de configuración
    return error.message || 'Error desconocido';
  }
};

// Función para validar respuestas exitosas
export const validateResponse = (response) => {
  if (response.status >= 200 && response.status < 300) {
    return response.data;
  }
  throw new Error('Respuesta inválida del servidor');
};

export default api; 