# Sistema POS O'Data Enterprise v2.0.0

## 🌟 **Sistema de Punto de Venta Avanzado - Las Arepas Cuadradas**

Sistema POS completo desarrollado con tecnologías modernas para la gestión integral de puntos de venta, inventario y reportes empresariales.

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

---

## 🛠️ **Stack Tecnológico**

### **Backend**
- **Python 3.9+** - Lenguaje principal
- **Flask** - Framework web
- **SQLAlchemy** - ORM para base de datos
- **SQLite/PostgreSQL** - Base de datos
- **JWT** - Autenticación
- **Pydantic** - Validación de datos

### **Frontend**
- **React 18** - Framework de interfaz
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **Tailwind CSS** - Framework de estilos
- **React Router** - Navegación
- **Axios** - Cliente HTTP

### **DevOps y Despliegue**
- **Docker** - Containerización
- **PowerShell** - Scripts de automatización
- **Git** - Control de versiones
- **Nginx** - Servidor web (producción)

---

## 📋 **Requisitos del Sistema**

### **Mínimos**
- Python 3.9 o superior
- Node.js 16 o superior
- 4GB RAM
- 10GB espacio en disco
- Windows 10/11, macOS, o Linux

### **Recomendados**
- Python 3.11+
- Node.js 18+
- 8GB RAM
- 20GB espacio en disco
- SSD para mejor rendimiento

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
- Health check: http://localhost:8000/api/v1/health
- Métricas: http://localhost:8000/api/v1/system/stats

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
python -m pytest tests/
```

### **Frontend**
```bash
cd frontend
npm test
```

### **Calidad de Código**
```bash
# Backend
flake8 app/
radon cc app/ -a -nc

# Frontend
cd frontend
npm run lint
```

---

## 📚 **Documentación**

- [Guía de Uso Rápido](GUIA_USO_RAPIDO.md)
- [Configuración de Email](EMAIL_SETUP.md)
- [Guía de Seguridad](SECURITY_YAML_GUIDE.md)
- [Sistema de Despliegue Automático](README_AUTO_DEPLOY.md)

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
- [ ] Reportes avanzados con gráficos
- [ ] App móvil para Android/iOS
- [ ] Integración con proveedores

### **v2.2.0** (Futuro)
- [ ] Inteligencia artificial para recomendaciones
- [ ] Sistema de fidelización
- [ ] Integración con e-commerce
- [ ] Análisis predictivo

---

**⭐ Si este proyecto te resulta útil, no olvides darle una estrella en GitHub!**

---

*Desarrollado con ❤️ por Las Arepas Cuadradas*