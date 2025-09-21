# 🥟 Sistema POS Sabrositas v2.0.0

## 🎯 Las Arepas Cuadradas - Sistema Enterprise

**Sistema de Punto de Venta completo y optimizado para Sabrositas, especializado en la venta de Arepas Cuadradas con arquitectura enterprise, IA integrada y tecnologías modernas.**

---

## 🚀 **Características Principales**

### ✨ **Funcionalidades Core**
- 🛒 **Sistema de Ventas** completo con carrito inteligente
- 📦 **Gestión de Inventario** en tiempo real
- 👥 **Gestión de Usuarios** con roles y permisos avanzados
- 📊 **Dashboard Analytics** con métricas en vivo
- 💰 **Control Financiero** y reportes detallados
- 🔐 **Seguridad Enterprise** con JWT y rate limiting

### 🤖 **Inteligencia Artificial v2.0**
- 🔍 **Búsqueda Semántica** de productos con TF-IDF
- 📈 **Análisis Predictivo** de ventas
- 🎯 **Recomendaciones Inteligentes** basadas en ML
- 📊 **Insights Automáticos** para optimización
- 🧠 **Procesamiento de Lenguaje Natural** en español
- 🎨 **Sugerencias Inteligentes** de productos

### 🐍 **Python 3.13 - Última Tecnología**
- ⚡ **Rendimiento mejorado** hasta 15% más rápido
- 🔒 **Seguridad avanzada** con nuevas características
- 🧠 **Mejor gestión de memoria** para aplicaciones IA
- 🔧 **Herramientas de debugging** mejoradas
- 📊 **Mejor soporte para async/await** y concurrencia
- 🚀 **Optimizaciones del intérprete** para mejor performance

### 🏗️ **Arquitectura Enterprise**
- 🐍 **Backend:** Python 3.13 + Flask 3.1 + SQLAlchemy 2.0
- ⚛️ **Frontend:** React 18 + TypeScript 5.8 + Vite 7.1
- 🗄️ **Base de Datos:** SQLite (desarrollo) / PostgreSQL 16 (producción)
- 🚀 **Cache:** Redis 7.2 para optimización y rate limiting
- 🐳 **Containerización:** Docker multi-stage optimizado
- 📊 **Monitoreo:** Prometheus + Grafana + Loki + AlertManager
- 🤖 **IA:** TF-IDF + Scikit-learn + NLTK para búsqueda semántica

---

## 📋 **Catálogo de Productos**

### 🥟 **18 Arepas Cuadradas Sabrositas**

#### 🏷️ **Sencillas** (3 productos) - $7,000 - $10,000
- **LA FÁCIL** - Queso, mucho queso! - $7,000
- **LA CONSENTIDA** - Bocadillo con queso - $8,000
- **LA SENCILLA** - Jamón con queso - $9,000

#### 🏷️ **Clásicas** (10 productos) - $10,500 - $14,500
- **LA COQUETA** - Jamón, piña y queso - $11,000
- **LA SUMISA** - Pollo, maíz tierno y queso - $11,500
- **LA COMPINCHE** - Carne desmechada, maduro al horno y queso - $12,000
- **LA SEXY** - Pollo, champiñón y queso - $12,000
- **LA SOLTERA** - Carne, maíz tierno y queso - $12,500
- **LA CREÍDA** - Pollo, salchicha y queso - $13,000
- **LA INFIEL** - Pollo, carne y queso - $13,000
- **LA GOMELA** - Carne, salchicha y queso - $13,500
- **LA CAPRICHOSA** - Carne desmechada, pollo, huevo y queso - $14,000
- **LA CHURRA** - Carne, chorizo santarrosano y queso - $14,500

#### 🏷️ **Premium** (5 productos) - $15,000+
- **LA PATRONA** - Chicharrón, carne desmechada, maduro al horno y queso - $15,000
- **LA DIFÍCIL** - Carne, chorizo, jalapeño y queso - $15,000
- **LA DIVA** - Carne, pollo, champiñón, salchicha y queso - $16,000
- **LA PICANTE** - Costilla BBQ, maíz tierno, tocineta, queso y ají - $17,000
- **LA TÓXICA** - Costilla BBQ, carne, chorizo, maíz tierno y queso - $18,000

---

## 🛠️ **Instalación y Configuración**

### 📋 **Requisitos del Sistema**
- 🐍 **Python 3.13+** (Recomendado: Python 3.13.0 o superior)
- 🟢 **Node.js 18+** (Recomendado: Node.js 20 LTS)
- 🐳 **Docker** (opcional, recomendado para producción)
- 💾 **8GB RAM mínimo** (16GB recomendado para IA)
- 💿 **5GB espacio libre** (para logs, backups y modelos IA)
- 🖥️ **Sistema Operativo:** Windows 10/11, Linux, macOS

### ⚡ **Inicio Rápido**

#### 🐳 **Opción 1: Docker (Recomendado)**
```powershell
# Iniciar con Docker
.\docker-start.ps1

# O manualmente
docker compose up -d --build
```

#### 🔧 **Opción 2: Manual (Python 3.13)**
```powershell
# 1. Verificar Python 3.13
python --version  # Debe ser 3.13.0 o superior

# 2. Crear entorno virtual Python 3.13
python -m venv venv_python313
.\venv_python313\Scripts\Activate.ps1

# 3. Actualizar pip y instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements-python313.txt

# 4. Inicializar base de datos y datos
python initialize_complete_system.py

# 5. Iniciar backend
python main.py

# 6. Frontend (nueva terminal)
cd frontend
npm install
npm run dev
```

#### 🚀 **Opción 3: Script Automatizado**
```powershell
# Inicio completo del sistema
.\start_sabrositas.ps1
```

---

## 🌐 **URLs del Sistema**

| Servicio | URL | Estado |
|----------|-----|--------|
| **Frontend** | http://localhost:5173 | ✅ Activo |
| **Backend API** | http://localhost:8000 | ✅ Activo |
| **Health Check** | http://localhost:8000/api/v1/health | ✅ Activo |
| **API Docs** | http://localhost:8000/api/v1/ | ✅ Disponible |

---

## 👥 **Credenciales del Sistema**

| Rol | Usuario | Contraseña | Nivel de Acceso |
|-----|---------|------------|----------------|
| **SuperAdmin** | `superadmin` | `SuperAdmin123!` | Control total del sistema |
| **Global Admin** | `globaladmin` | `Global123!` | Administración global |
| **Store Admin** | `storeadmin1` | `Store123!` | Administración de tienda |
| **Tech Admin** | `techadmin` | `TechAdmin123!` | Administración técnica |

---

## 🏗️ **Arquitectura del Sistema**

### 🐍 **Backend (Python 3.13 + Flask)**
```
app/
├── 📁 api/v1/          # API REST v1.0 (21 endpoints)
├── 📁 api/v2/          # API v2.0 con IA
├── 📁 services/        # 18 servicios de negocio
├── 📁 models/          # 18 modelos de datos
├── 📁 repositories/    # 6 repositorios
├── 📁 middleware/      # 5 middlewares de seguridad
└── 📁 security/        # Utilidades de seguridad
```

### ⚛️ **Frontend (React 18 + TypeScript)**
```
frontend/src/
├── 📁 components/      # 29 componentes React
├── 📁 services/        # Servicios API
├── 📁 context/         # Context providers
├── 📁 types/           # Definiciones TypeScript
└── 📁 styles/          # Estilos Tailwind CSS
```

### 🐳 **Docker**
- **Dockerfile** - Imagen principal (Python 3.13 Alpine)
- **Dockerfile.enterprise** - Multi-stage build optimizado
- **docker-compose.yml** - Orquestación completa

---

## 📊 **APIs Disponibles**

### 🔌 **API v1.0 (REST)**
- **Autenticación:** `/api/v1/auth/`
- **Productos:** `/api/v1/products/`
- **Ventas:** `/api/v1/sales/`
- **Usuarios:** `/api/v1/users/`
- **Inventario:** `/api/v1/inventory/`
- **Dashboard:** `/api/v1/dashboard/`

### 🤖 **API v2.0 (IA)**
- **Búsqueda IA:** `/api/v2/ai/search`
- **Recomendaciones:** `/api/v2/ai/recommend`
- **Analytics:** `/api/v2/ai/analytics`

---

## 🔒 **Seguridad**

### 🛡️ **Características de Seguridad**
- ✅ **Autenticación JWT** con refresh tokens
- ✅ **Rate Limiting** por IP y usuario
- ✅ **CORS** configurado correctamente
- ✅ **Headers de Seguridad** (CSP, HSTS, etc.)
- ✅ **Validación de Entrada** en todos los endpoints
- ✅ **Logging de Auditoría** completo

### 👥 **Sistema de Roles**
- **SuperAdmin:** Control total del sistema
- **Tech Admin:** Configuración técnica y desarrollo
- **Global Admin:** Administración de todas las tiendas
- **Store Admin:** Administración de tienda específica

---

## 📈 **Monitoreo y Observabilidad**

### 📊 **Stack de Monitoreo**
- **Prometheus:** Métricas del sistema
- **Grafana:** Dashboards visuales
- **Loki:** Agregación de logs
- **AlertManager:** Alertas automáticas

### 📝 **Logging**
- **Structured Logging:** JSON format
- **Audit Trail:** Registro de todas las acciones
- **Error Tracking:** Captura automática de errores
- **Performance Metrics:** Tiempos de respuesta

---

## 🧪 **Testing y Calidad**

### ✅ **Cobertura de Testing**
- **Unit Tests:** pytest + coverage
- **Integration Tests:** API testing
- **Frontend Tests:** Jest + React Testing Library
- **E2E Tests:** Playwright

### 📊 **Métricas de Calidad**
- **Code Coverage:** >90%
- **Code Quality:** SonarQube
- **Performance:** Lighthouse scores
- **Security:** OWASP compliance

---

## 🚀 **Deployment y DevOps**

### 🐳 **Containerización**
```bash
# Desarrollo
docker compose up -d

# Producción
docker compose -f docker-compose.production.yml up -d

# Enterprise
docker compose -f docker-compose.enterprise.yml up -d
```

### 🔄 **CI/CD**
- **GitHub Actions:** Automated testing
- **Docker Hub:** Container registry
- **Automated Deployment:** Production ready

---

## 📚 **Documentación Adicional**

- 📖 **[Guía Docker](DOCKER.md)** - Configuración y despliegue con Docker
- 🔧 **[API Documentation](docs/API.md)** - Documentación completa de APIs
- 🏗️ **[Architecture Guide](docs/ARCHITECTURE.md)** - Guía de arquitectura
- 🔒 **[Security Guide](docs/SECURITY.md)** - Guía de seguridad

---

## 🤝 **Contribución**

### 📋 **Guía de Contribución**
1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Add nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### 🎯 **Estándares de Código**
- **Python:** PEP 8, Black formatter
- **TypeScript:** ESLint + Prettier
- **Docker:** Best practices
- **Git:** Conventional commits

---

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 📞 **Soporte**

### 🆘 **Obtener Ayuda**
- 📧 **Email:** soporte@sabrositas.com
- 💬 **Chat:** Sistema de soporte integrado
- 📖 **Documentación:** Completa y actualizada
- 🐛 **Issues:** GitHub Issues para bugs

---

## 🎉 **¡Gracias por elegir Sistema POS Sabrositas!**

### 🏆 **Logros del Proyecto**
- ✅ **100% Funcional** para venta de Arepas Cuadradas
- ✅ **Arquitectura Enterprise** robusta y escalable
- ✅ **IA Integrada** para optimización de ventas
- ✅ **Seguridad de Clase Mundial** implementada
- ✅ **Documentación Completa** y mantenida
- ✅ **Testing Comprehensivo** con alta cobertura

### 🥟 **¡Listo para vender las mejores Arepas Cuadradas!**

---

**© 2024 Sistema POS Sabrositas v2.0.0 - Las Arepas Cuadradas Enterprise Edition**