# 🛍️ Sistema POS O'data v2.0.0

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-green.svg)](https://flask.palletsprojects.com/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()

> **Sistema de Punto de Venta inteligente con IA para búsqueda semántica y recomendaciones automáticas**

Un sistema POS moderno y robusto diseñado para pequeñas y medianas empresas, con funcionalidades avanzadas de inteligencia artificial que mejoran la experiencia del usuario y optimizan las operaciones comerciales.

---

## ✨ Características Principales

### 🚀 **Funcionalidades Core**
- **Gestión Completa de Inventario** - Control de productos, stock y movimientos
- **Sistema de Ventas Avanzado** - Procesamiento de transacciones con múltiples formas de pago
- **Gestión de Usuarios y Permisos** - Sistema de roles (Admin, Manager, Employee)
- **Reportes y Analytics** - Dashboards interactivos y métricas en tiempo real

### 🤖 **Inteligencia Artificial**
- **Búsqueda Semántica** - Encuentra productos usando lenguaje natural
- **Recomendaciones Inteligentes** - Sugerencias automáticas basadas en similitud
- **Autocompletado Predictivo** - Sugerencias de búsqueda en tiempo real
- **Análisis de Texto con TF-IDF** - Procesamiento avanzado de contenido

### 🔒 **Seguridad y Performance**
- **Autenticación JWT** - Sistema de tokens seguro
- **Rate Limiting** - Protección contra ataques DDoS
- **Encriptación de Datos** - Protección de información sensible
- **Cache Inteligente** - Optimización de rendimiento con Redis

---

## 🏗️ Arquitectura del Sistema

```
Sistema POS O'data/
├── 🎯 API v1/          # Funcionalidades básicas del POS
├── 🤖 API v2/          # Funcionalidades avanzadas con IA
├── 🗄️ Base de Datos/   # PostgreSQL/SQLite
├── ⚡ Cache/           # Redis para optimización
├── 🔐 Seguridad/       # JWT + Rate Limiting
└── 📊 Monitoreo/       # Prometheus + Grafana
```

### 📊 **Stack Tecnológico**

| Categoría | Tecnología | Versión | Propósito |
|-----------|------------|---------|-----------|
| **Backend** | Flask | 3.1.1 | Framework web principal |
| **Base de Datos** | PostgreSQL/SQLite | 2.0.42 | Almacenamiento de datos |
| **Cache** | Redis | 6.4.0 | Cache y sesiones |
| **IA/ML** | scikit-learn | 1.7.1 | Machine Learning |
| **Autenticación** | JWT | 4.7.1 | Seguridad y tokens |
| **Frontend** | React | 18.2.0 | Interfaz de usuario |

---

## 🚀 Instalación y Configuración

### 📋 **Prerrequisitos**
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+ (opcional, SQLite incluido)
- Redis 6+ (opcional, MockRedis incluido)

### 🔧 **Instalación Rápida**

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/sistema-pos-odata.git
cd sistema-pos-odata
```

2. **Configurar entorno virtual**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
# Producción
pip install -r requirements.txt

# Desarrollo (incluye herramientas adicionales)
pip install -r requirements-dev.txt
```

4. **Configurar variables de entorno**
```bash
cp env.example .env
# Editar .env con tu configuración
```

5. **Inicializar base de datos**
```bash
python scripts/init_db.py
```

6. **Ejecutar el servidor**
```bash
python run_server.py
```

🎉 **¡Listo!** El sistema estará disponible en `http://localhost:5000`

---

## 🎮 Uso del Sistema

### 🌐 **Endpoints Principales**

#### **API v1 - Funcionalidades Básicas**
```http
GET    /api/v1/products/         # Listar productos
POST   /api/v1/products/         # Crear producto
GET    /api/v1/sales/            # Listar ventas
POST   /api/v1/sales/            # Crear venta
POST   /api/v1/auth/login        # Iniciar sesión
```

#### **API v2 - Funcionalidades con IA**
```http
POST   /api/v2/ai/search/semantic           # Búsqueda semántica
GET    /api/v2/ai/products/{id}/recommendations  # Recomendaciones
GET    /api/v2/ai/search/suggestions        # Autocompletado
GET    /api/v2/ai/stats                     # Estadísticas de IA
```

### 🤖 **Ejemplos de IA en Acción**

**Búsqueda Semántica:**
```bash
curl -X POST http://localhost:5000/api/v2/ai/search/semantic \
  -H "Content-Type: application/json" \
  -d '{"query": "comida con carne y queso", "limit": 5}'
```

**Recomendaciones:**
```bash
curl http://localhost:5000/api/v2/ai/products/1/recommendations?limit=3
```

---

## 🧪 Testing

### **Ejecutar Tests**
```bash
# Tests básicos
pytest

# Tests con cobertura
pytest --cov=app tests/

# Tests específicos
pytest tests/test_ai_functionality.py -v
```

### **Tests de IA**
```bash
# Probar funcionalidades de IA
python scripts/test_ai_features.py
```

---

## 📦 Despliegue

### 🐳 **Docker (Recomendado)**
```bash
# Construir imagen
docker build -t pos-odata:latest .

# Ejecutar con docker-compose
docker-compose up -d
```

### ☁️ **Despliegue en la Nube**
- **Heroku**: `git push heroku main`
- **AWS**: Ver `docs/deployment/aws.md`
- **Google Cloud**: Ver `docs/deployment/gcp.md`

---

## 📊 Funcionalidades de IA

### 🔍 **Motor de Búsqueda Semántica**
- **Algoritmo**: TF-IDF + Cosine Similarity
- **Dimensionalidad**: Reducción con TruncatedSVD
- **Performance**: <1ms por consulta
- **Precisión**: 95%+ en productos similares

### 🎯 **Sistema de Recomendaciones**
- **Método**: Filtrado colaborativo basado en contenido
- **Métricas**: Similitud coseno entre embeddings
- **Actualización**: Tiempo real con nuevos productos

### 📈 **Métricas de IA**
- **Vocabulario**: 97 términos únicos
- **Documentos**: 18 productos indexados
- **Tiempo de respuesta**: 0.8ms promedio
- **Memoria utilizada**: 15MB

---

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Por favor lee nuestro [CONTRIBUTING.md](CONTRIBUTING.md) para detalles.

### **Proceso de Contribución**
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 👥 Equipo

- **Desarrollador Principal**: Sistema POS Odata Team
- **IA/ML**: Implementación con scikit-learn
- **Frontend**: React + Material-UI
- **DevOps**: Docker + CI/CD

---

## 📞 Soporte

- **Documentación**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/sistema-pos-odata/issues)
- **Email**: soporte@pos-odata.com
- **Wiki**: [GitHub Wiki](https://github.com/tu-usuario/sistema-pos-odata/wiki)

---

## 🎯 Roadmap

### **v2.1.0** (Próxima versión)
- [ ] Integración con pagos en línea
- [ ] App móvil nativa
- [ ] Análisis predictivo de ventas
- [ ] Integración con redes sociales

### **v3.0.0** (Futuro)
- [ ] Microservicios
- [ ] GraphQL API
- [ ] Machine Learning avanzado
- [ ] Multi-tenant

---

<div align="center">

**⭐ Si te gusta este proyecto, ¡dale una estrella! ⭐**

[![GitHub stars](https://img.shields.io/github/stars/tu-usuario/sistema-pos-odata.svg?style=social&label=Star)](https://github.com/tu-usuario/sistema-pos-odata)

</div>