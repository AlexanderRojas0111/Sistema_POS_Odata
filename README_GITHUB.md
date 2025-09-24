# Sistema POS O'data

## 🚀 Sistema de Punto de Venta Avanzado con IA

[![CI/CD Pipeline](https://github.com/tu-usuario/Sistema_POS_Odata/workflows/Code%20Quality%20Check/badge.svg)](https://github.com/tu-usuario/Sistema_POS_Odata/actions)
[![Python](https://img.shields.io/badge/Python-3.13.7-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.1-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)

### ✨ Características Principales

- 🧠 **IA Integrada**: Búsqueda semántica y recomendaciones inteligentes
- 🔐 **Autenticación JWT**: Sistema de seguridad robusto
- 📊 **Dashboard Avanzado**: Métricas y análisis en tiempo real
- 🛒 **Gestión Completa**: Productos, ventas, inventario y usuarios
- 🌐 **API REST**: v1 y v2 con documentación completa
- 🐳 **Docker Ready**: Despliegue containerizado
- 📱 **PWA**: Aplicación web progresiva

### 🏗️ Arquitectura

```
Sistema_POS_Odata/
├── app/                 # Backend Flask
├── frontend/           # Frontend React
├── scripts/            # Scripts de automatización
├── tests/              # Tests unitarios e integración
├── docs/               # Documentación
└── .github/workflows/  # CI/CD GitHub Actions
```

### 🚀 Inicio Rápido

#### Backend
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python run_server.py
```

#### Frontend
```bash
cd Sistema_POS_Odata_nuevo/frontend/
npm install
npm start
```

### 📊 Estado del Proyecto

**Última actualización**: 2025-09-22

- ✅ Backend Flask completamente funcional
- ✅ Frontend React con TypeScript
- ✅ CI/CD configurado con GitHub Actions
- ✅ Dependencias actualizadas (marshmallow 4.0.1)
- ✅ Reportes de calidad automatizados
- ✅ Tests y linting configurados

### 🛠️ Desarrollo

```bash
# Generar reporte de calidad
python scripts/generate_quality_report.py

# Ejecutar tests
pytest tests/ -v

# Linting
flake8 app/ scripts/

# Validar frontend
python scripts/validate_frontend.py
```

### 📈 Métricas de Calidad

El proyecto incluye análisis automático de:
- 🔍 **Linting** con flake8
- 🔒 **Seguridad** con bandit
- 🧪 **Testing** con pytest
- 📝 **Cobertura** de código
- 🎯 **TypeScript** strict mode

### 🤝 Contribución

1. Fork del proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Crear Pull Request

### 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

### 🔗 Enlaces Útiles

- [Documentación API](docs/technical/API_DOCUMENTATION.md)
- [Guía de Despliegue](DEPLOYMENT_GUIDE.md)
- [Manual de Usuario](docs/user/MANUAL.md)
- [Reportes de Calidad](reports/)

---

**Desarrollado con ❤️ para optimizar la gestión de puntos de venta**
