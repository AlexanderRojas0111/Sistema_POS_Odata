# 🏪 Sistema POS O'data v2.0.0

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://reactjs.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3.x-lightgrey.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Sistema de Punto de Venta (POS) moderno y robusto con funcionalidades de Inteligencia Artificial, desarrollado con Flask y React.**

## 🚀 **CARACTERÍSTICAS PRINCIPALES**

### **🔧 Backend (Flask)**
- ✅ **API RESTful** con versionado (v1 y v2)
- ✅ **Autenticación JWT** con roles y permisos
- ✅ **Base de datos SQLite** con SQLAlchemy ORM
- ✅ **Funcionalidades de IA** con scikit-learn y TF-IDF
- ✅ **Búsqueda semántica** de productos
- ✅ **Recomendaciones inteligentes**
- ✅ **Validación de datos** con Marshmallow/Pydantic
- ✅ **Manejo de errores** robusto
- ✅ **Logging** estructurado
- ✅ **Rate limiting** y seguridad CORS

### **🎨 Frontend (React)**
- ✅ **Material-UI** para interfaz moderna
- ✅ **Responsive design** para móviles y tablets
- ✅ **Navegación intuitiva** entre módulos
- ✅ **Gestión de productos** con CRUD completo
- ✅ **Sistema de ventas** con carrito de compras
- ✅ **Gestión de usuarios** y roles
- ✅ **Dashboard** con métricas en tiempo real
- ✅ **Búsqueda avanzada** con IA

### **🤖 Inteligencia Artificial**
- ✅ **Búsqueda semántica** de productos
- ✅ **Recomendaciones** basadas en historial
- ✅ **Clasificación automática** de categorías
- ✅ **Análisis de sentimientos** en comentarios
- ✅ **Predicción de demanda** de productos
- ✅ **Optimización de inventario**

### **🧪 Testing & Calidad**
- ✅ **Framework de pruebas** completo con pytest
- ✅ **Pruebas automatizadas** de backend, frontend y BD
- ✅ **Pruebas de integración** end-to-end
- ✅ **Pruebas de rendimiento** (< 500ms)
- ✅ **Cobertura de código** > 80%
- ✅ **CI/CD** ready para GitHub Actions

## 🏗️ **ARQUITECTURA DEL SISTEMA**

```
Sistema_POS_Odata/
├── app/                    # Backend Flask
│   ├── api/               # APIs v1 y v2
│   ├── core/              # Configuración y seguridad
│   ├── models/            # Modelos de base de datos
│   ├── services/          # Lógica de negocio
│   └── utils/             # Utilidades y helpers
├── frontend/              # Frontend React
│   ├── src/               # Código fuente
│   ├── components/        # Componentes reutilizables
│   └── pages/             # Páginas principales
├── tests/                 # Framework de pruebas
│   ├── backend/           # Pruebas del backend
│   ├── frontend/          # Pruebas del frontend
│   ├── database/          # Pruebas de BD
│   ├── integration/       # Pruebas de integración
│   └── performance/       # Pruebas de rendimiento
├── docs/                  # Documentación
├── scripts/               # Scripts de despliegue
└── requirements.txt       # Dependencias Python
```

## 🚀 **INSTALACIÓN Y DESPLIEGUE**

### **Requisitos Previos**
- Python 3.13+ (recomendado 3.13.4)
- Node.js 18+
- npm o yarn
- Git

### **1. Clonar el Repositorio**
```bash
git clone https://github.com/tu-usuario/Sistema_POS_Odata.git
cd Sistema_POS_Odata
```

### **2. Configurar Backend**
```bash
# Crear entorno virtual
python -m venv venv_pos
venv_pos\Scripts\activate  # Windows
source venv_pos/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
copy env.example .env
# Editar .env con tus configuraciones

# Inicializar base de datos
python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.models import db; db.create_all()"
```

### **3. Configurar Frontend**
```bash
cd frontend
npm install
npm start
```

### **4. Ejecutar el Sistema**
```bash
# Terminal 1: Backend
python run_server_8000.py

# Terminal 2: Frontend
cd frontend
npm start
```

## 🌐 **ACCESO AL SISTEMA**

- **Backend API:** http://127.0.0.1:8000
- **Frontend:** http://localhost:3000
- **Documentación API:** http://127.0.0.1:8000/docs
- **Health Check:** http://127.0.0.1:8000/health

## 🧪 **EJECUTAR PRUEBAS**

### **Ejecutar Todas las Pruebas**
```bash
python run_tests.py --all
```

### **Pruebas por Categoría**
```bash
# Solo backend
python run_tests.py --backend

# Solo frontend
python run_tests.py --frontend

# Solo base de datos
python run_tests.py --database

# Solo integración
python run_tests.py --integration

# Solo rendimiento
python run_tests.py --performance
```

### **Con Cobertura y Reportes**
```bash
python run_tests.py --coverage --html
```

## 📊 **ENDPOINTS DE LA API**

### **API v1 - Funcionalidades Básicas**
- `GET /api/v1/productos/` - Listar productos
- `POST /api/v1/productos/` - Crear producto
- `GET /api/v1/ventas/` - Listar ventas
- `POST /api/v1/ventas/` - Crear venta
- `GET /api/v1/usuarios/` - Listar usuarios
- `POST /api/v1/usuarios/` - Crear usuario

### **API v2 - Funcionalidades de IA**
- `GET /api/v2/` - Información de la API
- `POST /api/v2/ai/search` - Búsqueda semántica
- `POST /api/v2/ai/recommendations` - Recomendaciones
- `POST /api/v2/ai/embeddings` - Generar embeddings

### **Endpoints del Sistema**
- `GET /health` - Estado del sistema
- `GET /docs` - Documentación de la API

## 🔐 **AUTENTICACIÓN Y SEGURIDAD**

### **Roles de Usuario**
- **ADMIN:** Acceso completo al sistema
- **MANAGER:** Gestión de productos y ventas
- **EMPLOYEE:** Operaciones básicas de venta
- **CASHIER:** Solo ventas y consultas

### **Seguridad Implementada**
- ✅ **JWT Tokens** con expiración
- ✅ **Bcrypt** para hash de contraseñas
- ✅ **Rate Limiting** para prevenir abusos
- ✅ **CORS** configurado para frontend
- ✅ **Headers de seguridad** (HSTS, CSP, etc.)
- ✅ **Validación de entrada** robusta

## 📈 **MÉTRICAS Y MONITOREO**

### **Rendimiento**
- **Backend:** < 500ms por request
- **Frontend:** < 3000ms de carga
- **Base de datos:** < 100ms por consulta

### **Calidad del Código**
- **Cobertura:** > 80%
- **Pruebas:** 100% de funcionalidades críticas
- **Documentación:** 100% de APIs documentadas

## 🛠️ **TECNOLOGÍAS UTILIZADAS**

### **Backend**
- **Flask 3.1.1** - Framework web
- **SQLAlchemy 2.0.42** - ORM
- **Flask-JWT-Extended** - Autenticación
- **Marshmallow** - Serialización
- **scikit-learn** - Machine Learning
- **NumPy/SciPy** - Computación científica

### **Frontend**
- **React 18.2.0** - Biblioteca de UI
- **Material-UI** - Componentes de diseño
- **React Router** - Navegación
- **Axios** - Cliente HTTP
- **React Hook Form** - Formularios

### **Base de Datos**
- **SQLite** - Base de datos local
- **Alembic** - Migraciones
- **SQLAlchemy** - ORM y consultas

### **Testing**
- **pytest** - Framework de pruebas
- **Playwright** - Testing de frontend
- **pytest-cov** - Cobertura de código

## 📚 **DOCUMENTACIÓN ADICIONAL**

- [Guía de Usuario](docs/USER_GUIDE.md)
- [Manual de Desarrollador](docs/DEVELOPER_GUIDE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Guía de Despliegue](docs/DEPLOYMENT_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 **CONTRIBUCIÓN**

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### **Estándares de Código**
- Seguir PEP 8 para Python
- Usar ESLint para JavaScript/React
- Escribir pruebas para nuevas funcionalidades
- Mantener cobertura de código > 80%

## 📄 **LICENCIA**

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 **AUTORES**

- **Desarrollador Principal:** [Tu Nombre]
- **Contribuidores:** [Lista de contribuidores]

## 🙏 **AGRADECIMIENTOS**

- Flask y su comunidad
- React y Material-UI
- scikit-learn y la comunidad de ML
- Todos los contribuidores del proyecto

## 📞 **SOPORTE**

- **Issues:** [GitHub Issues](https://github.com/tu-usuario/Sistema_POS_Odata/issues)
- **Discusiones:** [GitHub Discussions](https://github.com/tu-usuario/Sistema_POS_Odata/discussions)
- **Email:** tu-email@ejemplo.com

## 🔄 **ROADMAP**

### **v2.1.0 (Próxima versión)**
- [ ] Dashboard avanzado con gráficos
- [ ] Sistema de notificaciones en tiempo real
- [ ] Integración con pasarelas de pago
- [ ] App móvil nativa

### **v2.2.0**
- [ ] Machine Learning avanzado
- [ ] Análisis predictivo de ventas
- [ ] Integración con redes sociales
- [ ] Sistema de fidelización

---

**⭐ Si este proyecto te gusta, dale una estrella en GitHub!**

**🔄 Última actualización:** Agosto 2025  
**🚀 Versión:** 2.0.0  
**🐍 Python:** 3.13+  
**⚛️ React:** 18.2.0