# Documentación Técnica de APIs - Sistema POS con IA

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Autenticación](#autenticación)
3. [API v1 - Funcionalidades Tradicionales](#api-v1---funcionalidades-tradicionales)
4. [API v2 - Funcionalidades de IA](#api-v2---funcionalidades-de-ia)
5. [Códigos de Error](#códigos-de-error)
6. [Rate Limiting](#rate-limiting)
7. [Ejemplos de Uso](#ejemplos-de-uso)
8. [SDKs y Librerías](#sdks-y-librerías)

---

## 🎯 Introducción

El Sistema POS con IA expone dos versiones de APIs:

- **API v1**: Funcionalidades tradicionales de POS e inventario
- **API v2**: Funcionalidades avanzadas con inteligencia artificial

### Base URLs

```
Desarrollo: http://localhost:5000
Producción: https://api.sistemapos.com
```

### Formatos de Respuesta

Todas las respuestas están en formato JSON con la siguiente estructura:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operación exitosa",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### Headers Requeridos

```
Content-Type: application/json
Authorization: Bearer <token> (para endpoints protegidos)
```

---

## 🔐 Autenticación

### Login

**POST** `/api/v1/auth/login`

```json
{
  "username": "usuario@ejemplo.com",
  "password": "contraseña123"
}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "usuario@ejemplo.com",
      "name": "Usuario Ejemplo",
      "role": "admin"
    }
  }
}
```

### Refresh Token

**POST** `/api/v1/auth/refresh`

```json
{
  "refresh_token": "refresh_token_here"
}
```

### Logout

**POST** `/api/v1/auth/logout`

Requiere token de autenticación.

---

## 📦 API v1 - Funcionalidades Tradicionales

### Productos

#### Listar Productos

**GET** `/api/v1/products/`

**Parámetros:**
- `page` (int): Número de página (default: 1)
- `per_page` (int): Productos por página (default: 10)
- `category` (string): Filtrar por categoría
- `search` (string): Búsqueda por nombre o código

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "code": "PROD001",
        "name": "Coca Cola 600ml",
        "description": "Bebida refrescante",
        "price": 15.50,
        "category": "Bebidas",
        "stock": 50,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
      }
    ],
    "total": 100,
    "pages": 10,
    "current_page": 1
  }
}
```

#### Obtener Producto

**GET** `/api/v1/products/{id}`

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "code": "PROD001",
    "name": "Coca Cola 600ml",
    "description": "Bebida refrescante",
    "price": 15.50,
    "category": "Bebidas",
    "stock": 50,
    "metadata": {
      "brand": "Coca Cola",
      "size": "600ml"
    }
  }
}
```

#### Crear Producto

**POST** `/api/v1/products/`

```json
{
  "code": "PROD002",
  "name": "Pepsi 600ml",
  "description": "Bebida refrescante",
  "price": 14.50,
  "category": "Bebidas",
  "stock": 30,
  "metadata": {
    "brand": "Pepsi",
    "size": "600ml"
  }
}
```

#### Actualizar Producto

**PUT** `/api/v1/products/{id}`

```json
{
  "name": "Pepsi 600ml - Actualizado",
  "price": 15.00,
  "stock": 25
}
```

#### Eliminar Producto

**DELETE** `/api/v1/products/{id}`

### Ventas

#### Listar Ventas

**GET** `/api/v1/sales/`

**Parámetros:**
- `page` (int): Número de página
- `per_page` (int): Ventas por página
- `date_from` (string): Fecha desde (YYYY-MM-DD)
- `date_to` (string): Fecha hasta (YYYY-MM-DD)
- `status` (string): Estado de la venta

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "invoice_number": "TICKET-001",
        "customer": {
          "id": 1,
          "name": "Cliente Ejemplo"
        },
        "user": {
          "id": 1,
          "name": "Vendedor Ejemplo"
        },
        "total_amount": 45.50,
        "payment_method": "cash",
        "status": "completed",
        "items": [
          {
            "id": 1,
            "product": {
              "id": 1,
              "name": "Coca Cola 600ml"
            },
            "quantity": 2,
            "unit_price": 15.50,
            "total": 31.00
          }
        ],
        "created_at": "2024-01-01T10:00:00Z"
      }
    ],
    "total": 50,
    "pages": 5,
    "current_page": 1
  }
}
```

#### Crear Venta

**POST** `/api/v1/sales/`

```json
{
  "customer_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "unit_price": 15.50
    }
  ],
  "payment_method": "cash",
  "total_amount": 31.00
}
```

#### Obtener Venta

**GET** `/api/v1/sales/{id}`

### Inventario

#### Listar Inventario

**GET** `/api/v1/inventory/`

**Parámetros:**
- `low_stock` (boolean): Solo productos con stock bajo
- `category` (string): Filtrar por categoría

#### Actualizar Stock

**PUT** `/api/v1/inventory/{id}`

```json
{
  "quantity": 25,
  "movement_type": "adjustment",
  "notes": "Ajuste de inventario"
}
```

#### Movimientos de Inventario

**GET** `/api/v1/inventory/movements`

**POST** `/api/v1/inventory/movements`

```json
{
  "product_id": 1,
  "quantity": 10,
  "movement_type": "in",
  "notes": "Entrada de mercancía"
}
```

### Clientes

#### Listar Clientes

**GET** `/api/v1/customers/`

#### Crear Cliente

**POST** `/api/v1/customers/`

```json
{
  "name": "Cliente Ejemplo",
  "email": "cliente@ejemplo.com",
  "phone": "+52 55 1234 5678",
  "address": "Dirección del cliente"
}
```

### Usuarios

#### Listar Usuarios

**GET** `/api/v1/users/`

#### Crear Usuario

**POST** `/api/v1/users/`

```json
{
  "username": "nuevo@usuario.com",
  "password": "contraseña123",
  "name": "Nuevo Usuario",
  "role": "seller"
}
```

---

## 🤖 API v2 - Funcionalidades de IA

### Búsqueda Semántica

#### Búsqueda Semántica Simple

**GET** `/api/v2/search/semantic`

**Parámetros:**
- `q` (string): Query de búsqueda
- `limit` (int): Número máximo de resultados (default: 10)

**Ejemplo:**
```
GET /api/v2/search/semantic?q=bebida refrescante&limit=5
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "query": "bebida refrescante",
    "results": [
      {
        "id": 1,
        "name": "Coca Cola 600ml",
        "price": 15.50,
        "similarity_score": 0.85,
        "category": "Bebidas"
      },
      {
        "id": 2,
        "name": "Pepsi 600ml",
        "price": 14.50,
        "similarity_score": 0.82,
        "category": "Bebidas"
      }
    ],
    "total_results": 2,
    "processing_time": 0.15
  }
}
```

#### Búsqueda Híbrida

**GET** `/api/v2/search/hybrid`

**Parámetros:**
- `q` (string): Query de búsqueda
- `category` (string): Filtrar por categoría
- `min_price` (float): Precio mínimo
- `max_price` (float): Precio máximo
- `in_stock` (boolean): Solo productos en stock
- `limit` (int): Número máximo de resultados

**Ejemplo:**
```
GET /api/v2/search/hybrid?q=bebida&category=Bebidas&min_price=10&max_price=20&in_stock=true
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "query": "bebida",
    "filters": {
      "category": "Bebidas",
      "price_range": [10.0, 20.0],
      "in_stock": true
    },
    "results": [
      {
        "id": 1,
        "name": "Coca Cola 600ml",
        "price": 15.50,
        "stock": 50,
        "semantic_score": 0.85,
        "keyword_score": 0.90,
        "final_score": 0.87
      }
    ],
    "total_results": 1,
    "processing_time": 0.25
  }
}
```

### Agentes Inteligentes

#### Estado de Agentes

**GET** `/api/v2/agents/status`

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "inventory_agent": {
      "status": "active",
      "last_check": "2024-01-01T10:00:00Z",
      "alerts_count": 3,
      "performance": {
        "accuracy": 0.95,
        "response_time": 0.12
      }
    },
    "sales_agent": {
      "status": "active",
      "last_check": "2024-01-01T10:00:00Z",
      "recommendations_count": 5,
      "performance": {
        "accuracy": 0.88,
        "response_time": 0.08
      }
    }
  }
}
```

#### Ejecutar Tarea de Agente

**POST** `/api/v2/agents/{agent_id}/tasks`

```json
{
  "task_type": "check_low_stock",
  "parameters": {
    "threshold": 5
  }
}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "task_id": "task_123",
    "status": "completed",
    "result": {
      "low_stock_products": [
        {
          "id": 1,
          "name": "Producto A",
          "current_stock": 3,
          "recommended_order": 20
        }
      ],
      "total_alerts": 1
    },
    "execution_time": 0.45
  }
}
```

#### Logs de Agentes

**GET** `/api/v2/agents/logs`

**Parámetros:**
- `agent_id` (string): ID del agente
- `level` (string): Nivel de log (info, warning, error)
- `date_from` (string): Fecha desde
- `date_to` (string): Fecha hasta

### Embeddings

#### Generar Embedding

**POST** `/api/v2/embeddings/generate`

```json
{
  "text": "bebida refrescante",
  "model": "sentence-transformers"
}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "text": "bebida refrescante",
    "embedding": [0.123, 0.456, ...],
    "model": "sentence-transformers",
    "dimensions": 768
  }
}
```

#### Comparar Embeddings

**POST** `/api/v2/embeddings/compare`

```json
{
  "text1": "bebida refrescante",
  "text2": "refresco cola",
  "model": "sentence-transformers"
}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "similarity_score": 0.85,
    "text1_embedding": [0.123, 0.456, ...],
    "text2_embedding": [0.124, 0.457, ...]
  }
}
```

---

## ❌ Códigos de Error

### Códigos HTTP

| Código | Descripción |
|--------|-------------|
| 200 | OK - Operación exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - No autenticado |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no encontrado |
| 422 | Unprocessable Entity - Validación fallida |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error - Error del servidor |

### Estructura de Error

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Los datos proporcionados son inválidos",
    "details": {
      "field": "price",
      "issue": "El precio debe ser mayor a 0"
    }
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### Códigos de Error Específicos

| Código | Descripción |
|--------|-------------|
| `AUTHENTICATION_FAILED` | Credenciales inválidas |
| `TOKEN_EXPIRED` | Token de autenticación expirado |
| `INSUFFICIENT_PERMISSIONS` | Permisos insuficientes |
| `PRODUCT_NOT_FOUND` | Producto no encontrado |
| `INSUFFICIENT_STOCK` | Stock insuficiente |
| `INVALID_PAYMENT_METHOD` | Método de pago inválido |
| `SEARCH_QUERY_TOO_SHORT` | Query de búsqueda muy corta |
| `AGENT_NOT_AVAILABLE` | Agente no disponible |
| `EMBEDDING_GENERATION_FAILED` | Error generando embedding |

---

## ⏱️ Rate Limiting

### Límites por Endpoint

| Endpoint | Límite | Ventana |
|----------|--------|---------|
| `/api/v1/products/` | 100 requests | 1 minuto |
| `/api/v1/sales/` | 50 requests | 1 minuto |
| `/api/v2/search/*` | 30 requests | 1 minuto |
| `/api/v2/agents/*` | 20 requests | 1 minuto |

### Headers de Rate Limiting

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Respuesta de Rate Limit Excedido

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Has excedido el límite de requests",
    "retry_after": 60
  }
}
```

---

## 💡 Ejemplos de Uso

### JavaScript/Node.js

```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Login
const login = async (username, password) => {
  try {
    const response = await api.post('/api/v1/auth/login', {
      username,
      password
    });
    
    const token = response.data.data.token;
    api.defaults.headers.Authorization = `Bearer ${token}`;
    
    return response.data;
  } catch (error) {
    console.error('Error de login:', error.response.data);
  }
};

// Búsqueda semántica
const searchProducts = async (query) => {
  try {
    const response = await api.get('/api/v2/search/semantic', {
      params: { q: query, limit: 10 }
    });
    
    return response.data.data.results;
  } catch (error) {
    console.error('Error de búsqueda:', error.response.data);
  }
};

// Crear venta
const createSale = async (saleData) => {
  try {
    const response = await api.post('/api/v1/sales/', saleData);
    return response.data.data;
  } catch (error) {
    console.error('Error creando venta:', error.response.data);
  }
};
```

### Python

```python
import requests
import json

class POSClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        if token:
            self.session.headers['Authorization'] = f'Bearer {token}'
    
    def login(self, username, password):
        response = self.session.post(f'{self.base_url}/api/v1/auth/login', json={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data['data']['token']
            self.session.headers['Authorization'] = f'Bearer {token}'
            return data
        else:
            raise Exception(f'Login failed: {response.text}')
    
    def search_products(self, query, limit=10):
        response = self.session.get(f'{self.base_url}/api/v2/search/semantic', params={
            'q': query,
            'limit': limit
        })
        
        if response.status_code == 200:
            return response.json()['data']['results']
        else:
            raise Exception(f'Search failed: {response.text}')
    
    def create_sale(self, sale_data):
        response = self.session.post(f'{self.base_url}/api/v1/sales/', json=sale_data)
        
        if response.status_code == 201:
            return response.json()['data']
        else:
            raise Exception(f'Sale creation failed: {response.text}')

# Uso
client = POSClient('http://localhost:5000')
client.login('usuario@ejemplo.com', 'password123')

# Búsqueda semántica
products = client.search_products('bebida refrescante')
print(f'Encontrados {len(products)} productos')

# Crear venta
sale_data = {
    'items': [
        {'product_id': 1, 'quantity': 2, 'unit_price': 15.50}
    ],
    'payment_method': 'cash',
    'total_amount': 31.00
}
sale = client.create_sale(sale_data)
print(f'Venta creada: {sale["invoice_number"]}')
```

### cURL

```bash
# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "usuario@ejemplo.com", "password": "password123"}'

# Búsqueda semántica
curl -X GET "http://localhost:5000/api/v2/search/semantic?q=bebida&limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Crear venta
curl -X POST http://localhost:5000/api/v1/sales/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 2, "unit_price": 15.50}
    ],
    "payment_method": "cash",
    "total_amount": 31.00
  }'
```

---

## 📚 SDKs y Librerías

### JavaScript/Node.js

```bash
npm install @sistemapos/client
```

```javascript
import { POSClient } from '@sistemapos/client';

const client = new POSClient({
  baseURL: 'http://localhost:5000',
  apiKey: 'your_api_key'
});

// Uso
const products = await client.products.search('bebida');
const sale = await client.sales.create(saleData);
```

### Python

```bash
pip install sistemapos-client
```

```python
from sistemapos import POSClient

client = POSClient(
    base_url='http://localhost:5000',
    api_key='your_api_key'
)

# Uso
products = client.products.search('bebida')
sale = client.sales.create(sale_data)
```

### PHP

```bash
composer require sistemapos/php-client
```

```php
use SistemaPOS\POSClient;

$client = new POSClient([
    'base_url' => 'http://localhost:5000',
    'api_key' => 'your_api_key'
]);

// Uso
$products = $client->products->search('bebida');
$sale = $client->sales->create($saleData);
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/pos_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your_jwt_secret
JWT_ACCESS_TOKEN_EXPIRES=3600

# IA
AI_MODEL_PATH=/path/to/models
EMBEDDING_DIMENSIONS=768

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Configuración de Logs

```python
# logging.conf
[loggers]
pos_api=INFO
pos_ai=DEBUG
pos_agents=INFO

[handlers]
console=StreamHandler
file=RotatingFileHandler

[formatters]
detailed=Formatter
```

---

## 📞 Soporte Técnico

### Contacto

- **Email**: api-support@sistemapos.com
- **Documentación**: https://docs.sistemapos.com
- **GitHub**: https://github.com/sistemapos/api
- **Discord**: https://discord.gg/sistemapos

### Estado del Servicio

- **Status Page**: https://status.sistemapos.com
- **Uptime**: 99.9%
- **Response Time**: < 200ms promedio

---

*Última actualización: Enero 2024*
*Versión de la API: v1.2.0* 