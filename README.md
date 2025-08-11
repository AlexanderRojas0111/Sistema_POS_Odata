# 🚀 Sistema POS O'data

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-green.svg)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-19.1.1-blue.svg)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Sistema profesional de punto de venta (POS) que incorpora tecnologías avanzadas de **Inteligencia Artificial** para proporcionar funcionalidades inteligentes de búsqueda, automatización y análisis predictivo.

## ✨ Características Principales

### 🛒 Funcionalidades Tradicionales
- **Gestión completa de productos e inventario**
- **Sistema de ventas y facturación avanzado**
- **Gestión de usuarios y roles granulares**
- **Reportes y análisis en tiempo real**
- **Escáner de códigos de barras y QR**
- **Dashboard interactivo con métricas**

### 🤖 Características Avanzadas de IA
- **🔍 Búsqueda Semántica (RAG)**
  - Búsqueda inteligente por significado y contexto
  - Recomendaciones personalizadas de productos
  - Análisis de patrones de compra
  - Clasificación automática de productos

- **🤖 Sistema de Agentes Inteligentes (A2A)**
  - Monitoreo automático de stock con alertas predictivas
  - Optimización automática de inventario
  - Análisis de tendencias de ventas
  - Recomendaciones de reabastecimiento

- **🔗 Protocolo de Comunicación (MCP)**
  - Integración inteligente entre módulos del sistema
  - Gestión avanzada de contexto y memoria
  - Comunicación estructurada entre agentes
  - Orquestación de tareas complejas

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.9+** - Lenguaje principal
- **Flask 3.1.1** - Framework web
- **SQLAlchemy 2.0.42** - ORM
- **PostgreSQL 13+** - Base de datos principal
- **Redis 6.4.0** - Cache y sesiones
- **LangChain 0.3.27** - Framework de IA
- **PyTorch 2.8.0** - Machine Learning
- **Transformers 4.55.0** - Modelos de IA

### Frontend
- **React 19.1.1** - Framework UI
- **Material-UI 7.3.1** - Componentes
- **Redux Toolkit 2.8.2** - Gestión de estado
- **React Router 7.8.0** - Navegación
- **React Query 3.39.3** - Gestión de datos
- **TypeScript 5.7.2** - Tipado estático

### Infraestructura
- **Docker & Docker Compose** - Containerización
- **Prometheus & Grafana** - Monitoreo
- **Nginx** - Proxy reverso
- **Celery** - Tareas asíncronas

## 🚀 Instalación Rápida

### Opción 1: Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/odata/sistema-pos.git
cd Sistema_POS_Odata

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 3. Ejecutar con Docker
docker-compose up -d

# 4. Acceder al sistema
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
# Grafana: http://localhost:3001
```

### Opción 2: Desarrollo Local

```bash
# 1. Clonar el repositorio
git clone https://github.com/odata/sistema-pos.git
cd Sistema_POS_Odata

# 2. Crear entorno virtual
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/Mac
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar frontend
cd frontend
npm install
cd ..

# 5. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 6. Inicializar base de datos
flask db upgrade
python scripts/init_db.py

# 7. Ejecutar el sistema
# Terminal 1: Backend
python app/main.py

# Terminal 2: Frontend
cd frontend
npm start
```

## 📁 Estructura del Proyecto

```
Sistema_POS_Odata/
├── 📁 app/                    # Backend Flask
│   ├── 📁 api/               # Endpoints API (v1 y v2)
│   ├── 📁 core/              # Configuración central
│   ├── 📁 models/            # Modelos de datos
│   ├── 📁 services/          # Lógica de negocio
│   ├── 📁 agents/            # Agentes de IA
│   └── 📁 utils/             # Utilidades
├── 📁 frontend/              # Aplicación React
│   ├── 📁 src/
│   │   ├── 📁 components/    # Componentes React
│   │   ├── 📁 pages/         # Páginas
│   │   └── 📁 services/      # Servicios API
├── 📁 docs/                  # Documentación
├── 📁 scripts/               # Scripts de utilidad
├── 📁 tests/                 # Pruebas automatizadas
├── 📁 monitoring/            # Configuración de monitoreo
└── 📁 nginx/                 # Configuración de proxy
```

## 🔌 API Endpoints

### API v1 (Tradicional)
```http
GET    /api/v1/products          # Listar productos
POST   /api/v1/products          # Crear producto
PUT    /api/v1/products/{id}     # Actualizar producto
DELETE /api/v1/products/{id}     # Eliminar producto
GET    /api/v1/inventory         # Estado del inventario
POST   /api/v1/sales             # Registrar venta
GET    /api/v1/reports/sales     # Reportes de ventas
```

### API v2 (Inteligencia Artificial)
```http
GET    /api/v2/search/semantic   # Búsqueda semántica
GET    /api/v2/search/hybrid     # Búsqueda híbrida
GET    /api/v2/agents/status     # Estado de agentes
POST   /api/v2/agents/trigger    # Activar agente
GET    /api/v2/analytics/trends  # Análisis de tendencias
```

## 📊 Monitoreo y Métricas

### Dashboards Disponibles
- **Grafana**: `http://localhost:3001` - Métricas y alertas
- **Prometheus**: `http://localhost:9090` - Datos de monitoreo
- **Sistema**: `http://localhost:3000` - Dashboard principal

### Métricas Clave
- Rendimiento de la aplicación
- Uso de recursos del sistema
- Métricas de base de datos
- Latencia de API
- Errores y excepciones

## 🔒 Seguridad

- **🔐 Autenticación JWT** con refresh tokens
- **👥 Roles y permisos granulares**
- **🔒 Encriptación AES-256** de datos sensibles
- **🛡️ Rate limiting** y protección DDoS
- **✅ Validación estricta** de entrada
- **🚫 Protección contra XSS** y SQL Injection
- **⏰ Gestión de sesiones** con expiración
- **🚪 Bloqueo de IP** por intentos fallidos
- **📝 Auditoría completa** de acciones

## 🧪 Testing

```bash
# Ejecutar todas las pruebas
pytest

# Con cobertura
pytest --cov=app

# Pruebas específicas
pytest tests/test_api.py
pytest tests/test_frontend_components.py
```

## 📈 Roadmap

### Versión 2.1 (Próxima)
- [ ] Integración con WhatsApp Business API
- [ ] Sistema de notificaciones push
- [ ] Análisis predictivo avanzado
- [ ] Integración con proveedores

### Versión 2.2
- [ ] App móvil nativa
- [ ] Reconocimiento de voz
- [ ] Integración con contabilidad
- [ ] Módulo de CRM

## 🤝 Contribuir

1. **Fork** el repositorio
2. **Crear rama** feature: `git checkout -b feature/nueva-funcionalidad`
3. **Commit** cambios: `git commit -am 'feat: Agregar nueva funcionalidad'`
4. **Push** a la rama: `git push origin feature/nueva-funcionalidad`
5. **Crear Pull Request**

### Guías de Contribución
- Seguir convenciones de commit (Conventional Commits)
- Incluir tests para nuevas funcionalidades
- Actualizar documentación cuando sea necesario
- Revisar código antes de enviar PR

## 📞 Soporte

- **📧 Email**: soporte@odata.com
- **💬 Discord**: [Servidor Odata](https://discord.gg/odata)
- **📖 Documentación**: [docs.odata.com](https://docs.odata.com)
- **🐛 Issues**: [GitHub Issues](https://github.com/odata/sistema-pos/issues)

## 📄 Licencia

Este proyecto está licenciado bajo los términos de la **Licencia MIT** - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- **Flask** - Framework web elegante
- **React** - Biblioteca para interfaces de usuario
- **Material-UI** - Componentes de diseño
- **LangChain** - Framework de IA
- **PostgreSQL** - Base de datos robusta

---

**Desarrollado con ❤️ por el equipo de Odata**

