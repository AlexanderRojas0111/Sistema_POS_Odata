# 🏪 Sistema POS Odata - Versión Producción v2.0

Sistema de Punto de Venta (POS) empresarial optimizado, robusto y listo para producción. Arquitectura de microservicios con Flask y PostgreSQL.

## ✅ Características Principales

- **Backend Optimizado**: Flask + SQLAlchemy + PostgreSQL 15
- **Arquitectura de Servicios**: SOLID principles y clean code
- **Seguridad Avanzada**: JWT + Rate Limiting + Security Headers
- **Cache Inteligente**: Redis con TTL y invalidación automática
- **Monitoreo**: Health checks y logging estructurado
- **Containerización**: Docker multi-stage optimizado
- **Listo para Producción**: Configuración hardened y escalable

## 🛠️ Requisitos del Sistema

### Mínimos
- **Python**: 3.13.0+
- **RAM**: 4GB mínimo
- **Disco**: 10GB libre
- **Sistema Operativo**: Windows 10+, Linux, macOS

### Recomendados
- **RAM**: 16GB
- **Disco**: 50GB SSD
- **CPU**: 4+ cores
- **Docker** + Docker Compose

## 📦 Instalación Rápida

### 1. Clonar el Repositorio
```bash
git clone https://github.com/odata/sistema-pos-odata.git
cd sistema-pos-odata
```

### 2. Despliegue Automático (RECOMENDADO)
```bash
# Despliegue completo en producción
python scripts/deploy_system.py --environment production

# Despliegue en desarrollo
python scripts/deploy_system.py --environment development
```

### 3. Instalación Manual
```bash
# Instalar dependencias de producción
python scripts/install_dependencies.py production

# Instalar dependencias de desarrollo
python scripts/install_dependencies.py dev
```

## 🔍 Validación del Sistema

```bash
# Verificar estado del sistema
python scripts/validate_dependencies.py

# Verificar servicios Docker
docker-compose ps
```

## 🐳 Despliegue con Docker

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

## 🌍 Configuración

### Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp env.example .env

# Configurar variables principales
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@host:5432/db_name
REDIS_URL=redis://host:6379/0
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

### Generar Claves Seguras
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## 📊 Monitoreo

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **API**: http://localhost:5000

## 📁 Estructura del Proyecto

```
Sistema_POS_Odata/
├── app/                    # Aplicación principal Flask
├── frontend/              # Frontend React
├── scripts/               # Scripts de automatización
├── docker-compose.yml     # Configuración Docker
├── requirements.txt       # Dependencias principales
├── requirements.production.txt  # Dependencias de producción
├── requirements.dev.txt   # Herramientas de desarrollo
└── env.example           # Variables de entorno
```

## 🚨 Solución de Problemas

### Problemas Comunes

#### 1. Puerto 5000 ocupado
```bash
# Cambiar puerto en .env
FLASK_RUN_PORT=5001
```

#### 2. Dependencias no encontradas
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

#### 3. Error de base de datos
```bash
# Verificar servicios
docker-compose ps db
docker-compose logs db
```

## 📋 Checklist de Despliegue

- [ ] Verificar Python 3.13+
- [ ] Tener Docker instalado
- [ ] Configurar variables de entorno
- [ ] Generar claves secretas
- [ ] Ejecutar script de despliegue
- [ ] Verificar servicios corriendo
- [ ] Probar endpoints de la API

## 📚 Documentación

- [Guía de Despliegue](DEPLOYMENT_README.md) - Instrucciones detalladas
- [API Documentation](docs/technical/API_DOCUMENTATION.md) - Documentación de la API
- [User Manual](docs/user/MANUAL.md) - Manual de usuario

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/odata/sistema-pos-odata/issues)
- **Wiki**: [Documentación del Proyecto](https://github.com/odata/sistema-pos-odata/wiki)
- **Discussions**: [Comunidad](https://github.com/odata/sistema-pos-odata/discussions)

## 📝 Scripts Disponibles

- `scripts/validate_dependencies.py` - Validación del sistema
- `scripts/install_dependencies.py` - Instalación automática
- `scripts/deploy_system.py` - Despliegue completo
- `scripts/health_check.py` - Verificación de salud

## 🎉 ¡SISTEMA LISTO!

El Sistema POS Odata está **completamente preparado** para ser desplegado.

### 🚀 Comando de Despliegue Rápido
```bash
python scripts/deploy_system.py --environment production
```

---

**¡El sistema está listo para funcionar en producción! 🎯**

