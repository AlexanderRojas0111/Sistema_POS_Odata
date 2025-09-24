# 🎯 GUÍA DE USO - SISTEMA POS ODATA

## ✅ **ESTADO ACTUAL: SISTEMA FUNCIONANDO**

El servidor backend está ejecutándose correctamente en http://localhost:5000

---

## 🌐 **ENDPOINTS DISPONIBLES**

### **📊 Monitoreo y Salud**
- `GET /health` - Health check básico ✅ **FUNCIONANDO**
- `GET /api/v1/health/detailed` - Health check detallado ✅ **FUNCIONANDO**
- `GET /` - Información de la API ✅ **FUNCIONANDO**

### **🛍️ Gestión de Productos**
- `GET /api/v1/products` - Listar productos
- `GET /api/v1/products/{id}` - Obtener producto específico
- `POST /api/v1/products` - Crear nuevo producto
- `PUT /api/v1/products/{id}` - Actualizar producto
- `DELETE /api/v1/products/{id}` - Eliminar producto

### **📦 Gestión de Inventario**
- `GET /api/v1/inventory` - Consultar inventario
- `POST /api/v1/inventory` - Actualizar stock
- `GET /api/v1/inventory/{product_id}` - Stock de producto específico

### **💰 Gestión de Ventas (REFACTORIZADO)**
- `POST /api/v1/sales` - Crear nueva venta
- `GET /api/v1/sales/{id}` - Obtener venta específica
- `GET /api/v1/sales/daily` - Ventas del día
- `GET /api/v1/sales/reports/period` - Reporte de período
- `POST /api/v1/sales/{id}/refund` - Procesar devolución
- `POST /api/v1/sales/stock-check` - Verificar disponibilidad
- `GET /api/v1/sales/analytics/top-products` - Productos más vendidos

### **👥 Gestión de Usuarios**
- `POST /api/v1/users/login` - Iniciar sesión
- `POST /api/v1/users/refresh` - Renovar token
- `GET /api/v1/users` - Listar usuarios
- `GET /api/v1/users/{id}` - Obtener usuario específico
- `POST /api/v1/users` - Crear nuevo usuario

---

## 🚀 **CÓMO USAR EL SISTEMA**

### **1. Iniciar Frontend**
```powershell
# En una nueva terminal
cd frontend
npm start
```

### **2. Probar Endpoints con PowerShell**

#### **Crear un producto:**
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @{
    name = "Producto de Prueba"
    description = "Descripción del producto"
    price = 10.50
    category = "Categoría A"
    sku = "PROD001"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/v1/products" -Method POST -Headers $headers -Body $body
```

#### **Listar productos:**
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/v1/products" -UseBasicParsing
```

#### **Crear un usuario:**
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @{
    username = "admin"
    email = "admin@pos.com"
    password = "admin123"
    role = "admin"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/v1/users" -Method POST -Headers $headers -Body $body
```

### **3. Autenticación**
```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:5000/api/v1/users/login" -Method POST -Headers $headers -Body $body
$token = ($response.Content | ConvertFrom-Json).access_token
```

### **4. Usar Token para Operaciones Protegidas**
```powershell
$headers = @{ 
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $token"
}

Invoke-WebRequest -Uri "http://localhost:5000/api/v1/sales" -Headers $headers
```

---

## 🎮 **PRUEBAS RÁPIDAS**

### **Test 1: Verificar que todo funciona**
```powershell
# Health check
Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing

# Información de la API
Invoke-WebRequest -Uri "http://localhost:5000/" -UseBasicParsing
```

### **Test 2: Probar endpoints sin autenticación**
```powershell
# Listar productos (puede estar vacío inicialmente)
Invoke-WebRequest -Uri "http://localhost:5000/api/v1/products" -UseBasicParsing

# Ver inventario
Invoke-WebRequest -Uri "http://localhost:5000/api/v1/inventory" -UseBasicParsing
```

---

## 📱 **FRONTEND**

Una vez que ejecutes `npm start` en la carpeta frontend, tendrás:

- **🏠 Interfaz principal:** http://localhost:3000
- **📊 Dashboard POS:** Interfaz moderna con Material-UI
- **🛍️ Gestión de productos:** CRUD completo
- **💰 Sistema de ventas:** Interfaz de punto de venta
- **📈 Reportes:** Visualización de datos

---

## 🔧 **CARACTERÍSTICAS IMPLEMENTADAS**

✅ **Backend API REST completo**  
✅ **Base de datos SQLite funcionando**  
✅ **Autenticación JWT**  
✅ **Sistema de ventas refactorizado**  
✅ **Gestión de inventario**  
✅ **Manejo de errores robusto**  
✅ **Sin dependencias de Redis/PostgreSQL**  
✅ **Frontend React con Material-UI**  
✅ **Arquitectura SOLID implementada**  

---

## 🎉 **¡SISTEMA LISTO PARA USAR!**

El sistema POS Odata está completamente funcional y optimizado. Puedes empezar a:

1. **Crear productos y categorías**
2. **Gestionar inventario**  
3. **Procesar ventas**
4. **Generar reportes**
5. **Administrar usuarios**

¿Qué funcionalidad te gustaría probar primero? 🚀
