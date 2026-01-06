# Sistema POS O'Data Enterprise v2.0.2-enterprise

## 🌟 **Sistema de Punto de Venta Avanzado - Las Arepas Cuadradas**

Sistema POS completo desarrollado con tecnologías modernas para la gestión integral de puntos de venta, inventario y reportes empresariales. **Ahora con Inteligencia Artificial, Monitoreo Avanzado y Arquitectura Empresarial Profesional.**

---

## 🚀 **Características Principales**

### 💼 **Gestión de Ventas**
- ✅ Sistema de ventas completo con múltiples métodos de pago
- ✅ Pagos múltiples (efectivo, tarjeta, transferencia, etc.)
- ✅ Cálculo automático de impuestos y descuentos
- ✅ Gestión de clientes y notas de venta
- ✅ Validación automática de stock

### 📦 **Control de Inventario**
- ✅ Gestión completa de productos
- ✅ Control de stock en tiempo real
- ✅ Alertas de stock bajo
- ✅ Movimientos de inventario automáticos
- ✅ Códigos de barras y SKU

### 📊 **Reportes y Analytics**
- ✅ Reportes de ventas detallados
- ✅ Estadísticas de productos más vendidos
- ✅ Análisis de tendencias
- ✅ Exportación de datos
- ✅ Dashboard en tiempo real

### 🔐 **Seguridad y Autenticación**
- ✅ Autenticación JWT segura
- ✅ Control de acceso basado en roles (RBAC)
- ✅ Auditoría completa de acciones
- ✅ Encriptación de datos sensibles
- ✅ Headers de seguridad

### 🤖 **Inteligencia Artificial (NUEVO)**
- ✅ Búsqueda semántica de productos
- ✅ Recomendaciones inteligentes
- ✅ Sugerencias de búsqueda automáticas
- ✅ Análisis de patrones de venta
- ✅ Sistema de IA con monitoreo avanzado

### 📊 **Monitoreo y Observabilidad (NUEVO)**
- ✅ Health checks detallados
- ✅ Métricas de rendimiento en tiempo real
- ✅ Sistema de alertas automáticas
- ✅ Rate limiting inteligente
- ✅ Logging estructurado y auditoría

---

## 🛠️ **Stack Tecnológico**

### **Backend**
- **Python 3.13** - Lenguaje principal
- **Flask** - Framework web
- **SQLAlchemy** - ORM para base de datos
- **SQLite/PostgreSQL** - Base de datos
- **JWT** - Autenticación
- **Marshmallow** - Validación robusta de datos
- **Redis** - Cache y rate limiting
- **NLTK** - Procesamiento de lenguaje natural
- **TF-IDF** - Algoritmos de IA

### **Frontend**
- **React 18** - Framework de interfaz
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **Tailwind CSS** - Framework de estilos
- **React Router** - Navegación
- **Axios** - Cliente HTTP
- **Recharts** - Gráficos avanzados
- **Framer Motion** - Animaciones
- **React DevTools** - Debugging

### **DevOps y Despliegue**
- **Docker** - Containerización
- **PowerShell** - Scripts de automatización
- **Git** - Control de versiones
- **Nginx** - Servidor web (producción)
- **GitHub Actions** - CI/CD automatizado
- **Pytest** - Testing automatizado
- **ESLint/Pylint** - Análisis de código
- **Trivy** - Security scanning

---

## 📋 **Requisitos del Sistema**

### **Mínimos**
- Python 3.13 o superior
- Node.js 18 o superior
- 8GB RAM
- 20GB espacio en disco
- Redis (para rate limiting)
- Windows 10/11, macOS, o Linux

### **Recomendados**
- Python 3.13+
- Node.js 20+
- 16GB RAM
- 50GB espacio en disco
- SSD para mejor rendimiento
- Redis Cluster (producción)

---

## 🚀 **Instalación Rápida**

### **1. Clonar el Repositorio**
```bash
git clone https://github.com/tu-usuario/sistema-pos-odata.git
cd sistema-pos-odata
```

### **2. Configurar Backend**
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Iniciar backend
python main.py
```

### **3. Configurar Frontend**
```bash
cd frontend
npm install
npm run dev
```

### **4. Acceder al Sistema**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API v2 (IA)**: http://localhost:8000/api/v2/ai/health
- **Monitoreo**: http://localhost:8000/api/v1/monitoring/health
- **Credenciales por defecto**: `admin` / `admin`

---

## 🔧 **Configuración Avanzada**

### **Variables de Entorno**
Copia `env.example` a `.env` y configura:

```env
# Base de datos
DATABASE_URL=sqlite:///instance/pos_odata.db

# JWT
JWT_SECRET_KEY=tu-clave-secreta-super-segura
JWT_ACCESS_TOKEN_EXPIRES=3600

# Email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-password

# Configuración de la aplicación
FLASK_ENV=development
DEBUG=True
```

### **Base de Datos**
El sistema soporta múltiples bases de datos:
- **SQLite** (desarrollo)
- **PostgreSQL** (producción)
- **MySQL** (alternativa)

---

## 📱 **Uso del Sistema**

### **Inicio de Sesión**
1. Accede a http://localhost:5173
2. Usa las credenciales: `admin` / `admin`
3. Cambia la contraseña en la primera sesión

### **Realizar una Venta**
1. Ve a la sección "Ventas"
2. Agrega productos al carrito
3. Configura método de pago
4. Procesa la venta

### **Gestionar Inventario**
1. Accede a "Productos"
2. Agrega/edita productos
3. Configura stock mínimo
4. Monitorea alertas

---

## 🐳 **Despliegue con Docker**

### **Desarrollo**
```bash
docker-compose up -d
```

### **Producción**
```bash
docker-compose -f docker-compose.production.yml up -d
```

---

## 📊 **Monitoreo y Logs**

### **Logs del Sistema**
- `logs/app.log` - Logs de la aplicación
- `logs/audit.log` - Logs de auditoría
- `logs/backup.log` - Logs de respaldos

### **Monitoreo**
- Health check: http://localhost:8000/api/v1/monitoring/health
- Métricas: http://localhost:8000/api/v1/monitoring/metrics
- IA Health: http://localhost:8000/api/v2/ai/health
- IA Stats: http://localhost:8000/api/v2/ai/stats
- Redis Info: http://localhost:8000/api/v1/monitoring/redis/info
- Rate Limit Info: http://localhost:8000/api/v1/monitoring/rate-limit/info

---

## 🔄 **Automatización**

### **Scripts de Despliegue**
- `final_auto_deploy.ps1` - Despliegue automático completo
- `monitor_changes.ps1` - Monitoreo de cambios
- `setup_auto_deploy.ps1` - Configuración inicial

### **Backups Automáticos**
- Respaldos diarios automáticos
- Rotación de backups
- Verificación de integridad

---

## 🧪 **Testing**

### **Backend**
```bash
# Tests API v1
python -m pytest tests/test_api.py -v --cov=app

# Tests API v2 (IA)
python -m pytest tests/test_api_v2.py -v

# Tests completos
python -m pytest tests/ -v --cov=app --cov-report=html
```

### **Frontend**
```bash
cd frontend
npm test
npm run test:coverage
```

### **Calidad de Código**
```bash
# Backend
pytest tests/ -v --cov=app
pylint app/
black app/ --check

# Frontend
cd frontend
npm run lint
npm run type-check
```

### **CI/CD**
```bash
# GitHub Actions se ejecuta automáticamente
# Incluye: linting, testing, security scanning, Docker build
```

---

## 📚 **Documentación**

- [Guía de Uso Rápido](GUIA_USO_RAPIDO.md)
- [Configuración de Email](EMAIL_SETUP.md)
- [Guía de Seguridad](SECURITY_YAML_GUIDE.md)
- [Sistema de Despliegue Automático](README_AUTO_DEPLOY.md)
- [Resumen de Implementaciones](RESUMEN_IMPLEMENTACIONES_COMPLETAS.md)
- [Validación API v2](VALIDACION_API_V2_COMPLETADA.md)
- [Mejoras Implementadas](MEJORAS_IMPLEMENTADAS.md)
- [Análisis de Salud del Sistema](ANALISIS_SALUD_SISTEMA.md)

---

## 🤝 **Contribución**

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 👥 **Equipo de Desarrollo**

**Las Arepas Cuadradas** - Enterprise Development Team

- **Desarrollador Principal**: [Tu Nombre]
- **Arquitecto de Software**: [Nombre del Arquitecto]
- **DevOps Engineer**: [Nombre del DevOps]

---

## 📞 **Soporte**

Para soporte técnico o consultas:

- 📧 Email: soporte@arepascuadradas.com
- 📱 WhatsApp: +57 300 000 0000
- 🌐 Web: https://arepascuadradas.com

---

## 🎯 **Roadmap**

### **v2.1.0** (Próxima versión)
- [ ] Integración con sistemas contables
- [ ] App móvil para Android/iOS
- [ ] Integración con proveedores
- [ ] Dashboard avanzado con métricas en tiempo real

### **v2.2.0** (Futuro)
- [ ] Sistema de fidelización
- [ ] Integración con e-commerce
- [ ] Análisis predictivo avanzado
- [ ] Machine Learning para optimización de inventario

### **✅ 2.0.2-enterprise** (ACTUAL - COMPLETADO)
- [x] Inteligencia artificial para recomendaciones
- [x] Búsqueda semántica avanzada
- [x] Sistema de monitoreo y alertas
- [x] Arquitectura empresarial robusta
- [x] CI/CD automatizado
- [x] Testing completo
- [x] Seguridad avanzada

---

**⭐ Si este proyecto te resulta útil, no olvides darle una estrella en GitHub!**

---

*Desarrollado con ❤️ por Las Arepas Cuadradas*