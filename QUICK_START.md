# 🚀 Guía de Inicio Rápido - Sistema POS O'data

Esta guía te ayudará a configurar y ejecutar el Sistema POS O'data en tu entorno de desarrollo.

## 📋 Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.9+**
- **Node.js 14+**
- **npm** (viene con Node.js)
- **Docker** (opcional, para servicios externos)
- **Git**

## ⚡ Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd Sistema_POS_Odata
```

### 2. Configuración automática
```bash
# En Windows (PowerShell)
chmod +x scripts/setup_development.sh
./scripts/setup_development.sh

# En Linux/Mac
chmod +x scripts/setup_development.sh
./scripts/setup_development.sh
```

### 3. Configuración manual (si la automática falla)

#### Backend
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.development .env
# Editar .env según tu configuración

# Inicializar base de datos
python scripts/init_db.py
python scripts/load_sample_data.py
```

#### Frontend
```bash
cd frontend
npm install --legacy-peer-deps
cd ..
```

## 🏃‍♂️ Ejecutar el Sistema

### Opción 1: Con Docker (Recomendado)
```bash
# Iniciar todos los servicios
docker-compose up -d

# Verificar que todo esté funcionando
docker-compose ps
```

### Opción 2: Desarrollo local
```bash
# Terminal 1 - Backend
source venv/bin/activate  # o venv\Scripts\activate en Windows
python app/main.py

# Terminal 2 - Frontend
cd frontend
npm start
```

## 🌐 Acceso al Sistema

Una vez ejecutado, puedes acceder a:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Grafana**: http://localhost:3000 (monitoreo)
- **Prometheus**: http://localhost:9090 (métricas)

## 👤 Usuarios de Prueba

El sistema viene con usuarios predefinidos:

- **Administrador**: admin@example.com / admin123
- **Empleado**: employee@example.com / employee123

## 🔧 Verificación de Salud

Para verificar que todo esté funcionando correctamente:

```bash
python scripts/health_check.py
```

## 📚 Funcionalidades Principales

### Gestión de Productos
- Crear, editar, eliminar productos
- Gestión de inventario
- Códigos de barras y QR

### Ventas
- Proceso de venta rápido
- Escáner de códigos
- Generación de tickets
- Reportes de ventas

### Usuarios y Seguridad
- Autenticación JWT
- Roles y permisos
- Gestión de usuarios

### Características Avanzadas
- Búsqueda semántica (IA)
- Agentes inteligentes
- Monitoreo en tiempo real

## 🛠️ Solución de Problemas

### Error: Puerto ya en uso
```bash
# Cambiar puerto del backend
export FLASK_RUN_PORT=5001
python app/main.py

# Cambiar puerto del frontend
cd frontend
PORT=3001 npm start
```

### Error: Base de datos no conecta
```bash
# Verificar que PostgreSQL esté corriendo
# En Windows: Servicios > PostgreSQL
# En Linux: sudo systemctl status postgresql

# Crear base de datos manualmente
createdb pos_odata_dev
```

### Error: Dependencias de Python
```bash
# Actualizar pip
pip install --upgrade pip

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error: Dependencias de Node.js
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

## 📖 Documentación Completa

- **Manual de Usuario**: `docs/user/MANUAL.md`
- **Documentación Técnica**: `docs/technical/`
- **API Documentation**: `docs/technical/API_DOCUMENTATION.md`

## 🤝 Contribuir

1. Fork el repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'feat: Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📞 Soporte

Si tienes problemas:

1. Revisar la documentación en `docs/`
2. Ejecutar `python scripts/health_check.py`
3. Revisar logs en `logs/`
4. Crear un issue en el repositorio

---

**¡Listo! 🎉 Tu Sistema POS O'data está funcionando.** 