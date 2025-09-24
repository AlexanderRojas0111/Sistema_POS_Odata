# Sistema POS O'data v2.0.0

Bienvenido a la documentación oficial del **Sistema POS O'data**, una solución moderna y completa de Punto de Venta con funcionalidades avanzadas de Inteligencia Artificial.

## 🚀 Características Principales

### Sistema POS Completo
- **Gestión de Productos**: CRUD completo con categorías y stock
- **Sistema de Ventas**: Procesamiento de transacciones multi-producto
- **Gestión de Usuarios**: Sistema de roles y permisos
- **Reportes y Analytics**: Dashboards interactivos

### Inteligencia Artificial
- **Búsqueda Semántica**: Encuentra productos usando lenguaje natural
- **Recomendaciones Inteligentes**: Sugerencias automáticas
- **Autocompletado Predictivo**: Búsqueda en tiempo real
- **Análisis con TF-IDF**: Procesamiento avanzado de texto

## 📚 Documentación

### Para Desarrolladores
- [Guía de Instalación](installation.md)
- [API Reference](api.md)
- [Arquitectura del Sistema](architecture.md)
- [Guía de Contribución](../CONTRIBUTING.md)

### Para Usuarios
- [Manual de Usuario](user-guide.md)
- [Preguntas Frecuentes](faq.md)
- [Troubleshooting](troubleshooting.md)

### Despliegue
- [Guía de Despliegue](../DEPLOYMENT_GUIDE.md)
- [Configuración Docker](docker.md)
- [Configuración de Producción](production.md)

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Backend** | Flask | 3.1.1 |
| **Base de Datos** | PostgreSQL/SQLite | 15+/3.x |
| **Cache** | Redis | 6.4.0 |
| **IA/ML** | scikit-learn | 1.7.1 |
| **Frontend** | React | 18.2.0 |
| **Containerización** | Docker | 20+ |

## 🚀 Inicio Rápido

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/sistema-pos-odata.git
cd sistema-pos-odata

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno
python scripts/setup_secure_env.py development

# Inicializar base de datos
python scripts/init_db.py

# Ejecutar servidor
python run_server.py
```

## 📊 Estado del Proyecto

[![Build Status](https://github.com/tu-usuario/sistema-pos-odata/workflows/CI/badge.svg)](https://github.com/tu-usuario/sistema-pos-odata/actions)
[![Coverage](https://codecov.io/gh/tu-usuario/sistema-pos-odata/branch/main/graph/badge.svg)](https://codecov.io/gh/tu-usuario/sistema-pos-odata)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor lee nuestra [Guía de Contribución](../CONTRIBUTING.md) para detalles sobre cómo contribuir al proyecto.

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/sistema-pos-odata/issues)
- **Documentación**: [GitHub Wiki](https://github.com/tu-usuario/sistema-pos-odata/wiki)
- **Email**: soporte@pos-odata.com

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](../LICENSE) para más detalles.

---

<div align="center">

**Desarrollado con ❤️ por Sistema POS Odata Team**

</div>
