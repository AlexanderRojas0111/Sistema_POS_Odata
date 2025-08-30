# 🧪 Framework de Pruebas Automatizadas - Sistema POS O'data v2.0.0

## 📋 **DESCRIPCIÓN**

Framework completo de pruebas automatizadas para el Sistema POS O'data, desarrollado por un ingeniero de software senior. Incluye pruebas de backend, frontend, base de datos, integración y rendimiento.

## 🏗️ **ARQUITECTURA DE PRUEBAS**

```
tests/
├── backend/           # Pruebas del backend Flask
├── frontend/          # Pruebas del frontend React
├── database/          # Pruebas de base de datos SQLite
├── integration/       # Pruebas de integración completa
├── performance/       # Pruebas de rendimiento
└── README.md         # Este archivo
```

## 🚀 **REQUISITOS PREVIOS**

### **Dependencias Python:**
```bash
pip install pytest pytest-html pytest-xdist requests selenium playwright pytest-playwright pytest-cov
```

### **Navegadores Playwright:**
```bash
playwright install
```

### **Sistema en Ejecución:**
- ✅ Backend Flask corriendo en `http://127.0.0.1:8000`
- ✅ Frontend React corriendo en `http://localhost:3000`
- ✅ Base de datos SQLite operativa

## 🧪 **EJECUCIÓN DE PRUEBAS**

### **1. Ejecutar Todas las Pruebas:**
```bash
pytest tests/ -v --html=reports/test_report.html --self-contained-html
```

### **2. Ejecutar Pruebas por Categoría:**

#### **Backend:**
```bash
pytest tests/backend/ -v -m backend
```

#### **Frontend:**
```bash
pytest tests/frontend/ -v -m frontend
```

#### **Base de Datos:**
```bash
pytest tests/database/ -v -m database
```

#### **Integración:**
```bash
pytest tests/integration/ -v -m integration
```

#### **Rendimiento:**
```bash
pytest tests/performance/ -v -m performance
```

### **3. Ejecutar Pruebas Específicas:**
```bash
# Solo pruebas de health check
pytest tests/backend/test_api_backend.py::TestBackendHealth -v

# Solo pruebas de rendimiento
pytest tests/performance/test_system_performance.py::TestSystemPerformance::test_backend_response_time_under_500ms -v
```

### **4. Ejecutar con Cobertura:**
```bash
pytest tests/ --cov=app --cov-report=html:reports/coverage --cov-report=term-missing
```

### **5. Ejecutar en Paralelo:**
```bash
pytest tests/ -n auto --dist=loadfile
```

## 📊 **TIPOS DE PRUEBAS**

### **🔧 Backend (Flask)**
- ✅ Health check endpoint (`/health`)
- ✅ API v1 endpoints (`/api/v1/productos`, `/api/v1/ventas`, `/api/v1/usuarios`)
- ✅ API v2 endpoints (`/api/v2/ai/*`)
- ✅ Validación de headers CORS
- ✅ Manejo de errores
- ✅ Tiempo de respuesta < 500ms

### **🗄️ Base de Datos (SQLite)**
- ✅ Conexión y operaciones CRUD
- ✅ Estructura de tablas
- ✅ Integridad de datos
- ✅ Transacciones
- ✅ Rendimiento de consultas

### **🎨 Frontend (React)**
- ✅ Carga de aplicación
- ✅ Navegación entre vistas
- ✅ Componentes Material-UI
- ✅ Responsive design
- ✅ Accesibilidad básica
- ✅ Sin errores de consola

### **🔗 Integración**
- ✅ Comunicación frontend-backend
- ✅ Flujo completo de ventas
- ✅ Creación de productos desde UI
- ✅ Funcionalidades de IA
- ✅ Gestión de usuarios

### **📈 Rendimiento**
- ✅ Tiempo de respuesta < 500ms
- ✅ Requests concurrentes
- ✅ Uso de memoria
- ✅ Rendimiento de base de datos

## 🎯 **CASOS DE PRUEBA CLAVE**

### **1. Health Check del Sistema**
```bash
pytest tests/backend/test_api_backend.py::TestBackendHealth::test_health_endpoint_responds_200 -v
```

### **2. Rendimiento del Backend**
```bash
pytest tests/performance/test_system_performance.py::TestSystemPerformance::test_backend_response_time_under_500ms -v
```

### **3. Operaciones de Base de Datos**
```bash
pytest tests/database/test_database_operations.py::TestDatabaseOperations::test_insert_and_query_producto -v
```

### **4. Integración Frontend-Backend**
```bash
pytest tests/integration/test_full_stack_integration.py::TestFullStackIntegration::test_create_product_from_frontend_to_database -v
```

## 📁 **ESTRUCTURA DE ARCHIVOS**

### **Backend Tests:**
- `test_api_backend.py` - Pruebas de API Flask

### **Database Tests:**
- `test_database_operations.py` - Operaciones CRUD y estructura

### **Frontend Tests:**
- `test_frontend_react.py` - Pruebas de React con Playwright

### **Integration Tests:**
- `test_full_stack_integration.py` - Pruebas de integración completa

### **Performance Tests:**
- `test_system_performance.py` - Pruebas de rendimiento y carga

## 🔧 **CONFIGURACIÓN AVANZADA**

### **Archivo pytest.ini:**
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --html=reports/test_report.html
    --self-contained-html
    --cov=app
    --cov-report=html:reports/coverage
    --cov-report=term-missing
    --cov-fail-under=80
```

### **Marcadores de Pruebas:**
- `@pytest.mark.slow` - Pruebas lentas
- `@pytest.mark.integration` - Pruebas de integración
- `@pytest.mark.frontend` - Pruebas de frontend
- `@pytest.mark.backend` - Pruebas de backend
- `@pytest.mark.database` - Pruebas de base de datos
- `@pytest.mark.performance` - Pruebas de rendimiento

## 📊 **REPORTES Y RESULTADOS**

### **Reporte HTML:**
```bash
pytest tests/ --html=reports/test_report.html --self-contained-html
```
**Ubicación:** `reports/test_report.html`

### **Reporte de Cobertura:**
```bash
pytest tests/ --cov=app --cov-report=html:reports/coverage
```
**Ubicación:** `reports/coverage/index.html`

### **Reporte en Consola:**
```bash
pytest tests/ -v --tb=short
```

## 🚨 **SOLUCIÓN DE PROBLEMAS**

### **Error: "Module not found"**
```bash
pip install -r requirements.txt
pip install pytest pytest-html pytest-xdist requests selenium playwright pytest-playwright pytest-cov
```

### **Error: "Playwright browsers not found"**
```bash
playwright install
```

### **Error: "Frontend not responding"**
- Verificar que React esté corriendo en `http://localhost:3000`
- Verificar que no haya errores de compilación

### **Error: "Backend not responding"**
- Verificar que Flask esté corriendo en `http://127.0.0.1:8000`
- Verificar logs del servidor

### **Error: "Database connection failed"**
- Verificar que `pos_odata_dev.db` existe
- Verificar permisos de archivo

## 📈 **MÉTRICAS DE CALIDAD**

### **Cobertura de Código:**
- **Objetivo:** > 80%
- **Comando:** `pytest --cov=app --cov-fail-under=80`

### **Tiempo de Respuesta:**
- **Backend:** < 500ms
- **Frontend:** < 3000ms
- **Base de Datos:** < 100ms

### **Tasa de Éxito:**
- **Objetivo:** 100%
- **Tolerancia:** 95% (para pruebas de integración)

## 🔄 **INTEGRACIÓN CONTINUA**

### **GitHub Actions:**
```yaml
- name: Run Tests
  run: |
    pip install -r requirements.txt
    playwright install
    pytest tests/ --cov=app --cov-report=xml
```

### **Pre-commit Hooks:**
```bash
pre-commit install
pre-commit run --all-files
```

## 📞 **SOPORTE**

### **Para problemas técnicos:**
1. Verificar que todas las dependencias estén instaladas
2. Verificar que el sistema esté corriendo
3. Revisar logs de pytest y del sistema
4. Ejecutar pruebas individuales para aislar el problema

### **Para nuevas funcionalidades:**
1. Crear pruebas unitarias primero
2. Implementar la funcionalidad
3. Ejecutar todas las pruebas
4. Verificar cobertura de código

---

**Desarrollado por:** Ingeniero de Software Senior  
**Versión:** 2.0.0  
**Última actualización:** Agosto 2025
