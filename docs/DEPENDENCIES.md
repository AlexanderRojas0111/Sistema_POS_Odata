# 📦 Dependencias del Sistema POS Odata

## 📋 Resumen de Archivos

### Backend (Python)
- **`requirements.txt`** - Dependencias completas (desarrollo + producción)
- **`requirements.production.txt`** - Dependencias mínimas para producción

### Frontend (React)
- **`frontend/package.json`** - Dependencias de Node.js actualizadas

## 🐍 Dependencias de Python

### Core Framework
- **Flask 3.1.1** - Framework web principal
- **Flask-SQLAlchemy 3.1.1** - ORM para base de datos
- **Flask-Migrate 4.1.0** - Migraciones de base de datos
- **Flask-JWT-Extended 4.7.1** - Autenticación JWT
- **Flask-CORS 6.0.1** - Soporte CORS
- **Flask-Bcrypt 1.0.1** - Encriptación de contraseñas

### Base de Datos
- **psycopg2-binary 2.9.10** - Driver PostgreSQL
- **SQLAlchemy 2.0.42** - ORM principal
- **alembic 1.16.4** - Migraciones
- **pgvector 0.4.1** - Soporte para vectores

### Cache y Cola de Mensajes
- **redis 6.4.0** - Cache y sesiones
- **celery 5.5.3** - Tareas asíncronas

### Seguridad
- **bcrypt 4.3.0** - Hash de contraseñas
- **cryptography 45.0.6** - Encriptación
- **PyJWT 2.10.1** - Tokens JWT
- **python-jose 3.5.0** - JWT avanzado
- **passlib 1.7.4** - Gestión de contraseñas

### Validación de Datos
- **pydantic 2.11.7** - Validación y serialización
- **marshmallow 4.0.0** - Serialización

### HTTP y API
- **requests 2.32.4** - Cliente HTTP
- **httpx 0.28.1** - Cliente HTTP asíncrono
- **aiohttp 3.12.15** - Servidor HTTP asíncrono

### Inteligencia Artificial
- **langchain 0.3.27** - Framework de IA
- **langchain-core 0.3.74** - Core de LangChain
- **transformers 4.55.0** - Modelos de IA
- **sentence-transformers 5.1.0** - Embeddings
- **torch 2.8.0** - PyTorch
- **scikit-learn 1.6.1** - Machine Learning
- **numpy 2.0.2** - Computación numérica
- **pandas 2.3.1** - Análisis de datos

### Hugging Face
- **huggingface-hub 0.34.4** - Hub de modelos
- **tokenizers 0.21.4** - Tokenización
- **safetensors 0.6.2** - Tensores seguros

### Utilidades
- **python-dotenv 1.1.1** - Variables de entorno
- **python-dateutil 2.9.0** - Manejo de fechas
- **pytz 2025.2** - Zonas horarias
- **click 8.1.8** - CLI
- **rich 14.1.0** - Terminal enriquecida

### Monitoreo
- **prometheus_client 0.22.1** - Métricas
- **psutil 7.0.0** - Monitoreo del sistema

### Desarrollo (Opcional)
- **pytest 8.4.1** - Testing
- **pytest-cov 6.2.1** - Cobertura de tests
- **coverage 7.10.3** - Cobertura
- **black 25.1.0** - Formateo de código
- **flake8 7.3.0** - Linting

### Procesamiento
- **Pillow 11.3.0** - Procesamiento de imágenes
- **orjson 3.11.1** - JSON rápido
- **PyYAML 6.0.2** - YAML

## ⚛️ Dependencias de React

### Core
- **React 19.1.1** - Framework principal
- **React DOM 19.1.1** - DOM de React
- **React Scripts 5.0.1** - Scripts de desarrollo

### UI Framework
- **Material-UI 7.3.1** - Componentes UI
- **Emotion 11.12.1** - CSS-in-JS
- **MUI Icons 7.3.1** - Iconos
- **MUI Data Grid 8.10.0** - Tablas avanzadas
- **MUI Date Pickers 8.10.0** - Selectores de fecha

### Estado y Navegación
- **Redux Toolkit 2.8.2** - Gestión de estado
- **React Redux 9.2.0** - Integración Redux
- **React Router 7.8.0** - Enrutamiento
- **React Query 3.39.3** - Gestión de datos

### Utilidades
- **Axios 1.7.9** - Cliente HTTP
- **Date-fns 4.1.0** - Manejo de fechas
- **Recharts 3.1.2** - Gráficos
- **jsPDF 3.0.1** - Generación de PDFs
- **React ZXing 2.0.0** - Escáner de códigos

### Testing
- **Testing Library 16.3.0** - Testing de componentes
- **Jest DOM 6.6.4** - Matchers de DOM
- **User Event 14.6.1** - Eventos de usuario

### Desarrollo
- **TypeScript 5.7.2** - Tipado estático
- **ESLint 9.33.0** - Linting
- **Prettier 3.4.2** - Formateo

## 🚀 Instalación

### Backend
```bash
# Desarrollo (con herramientas de testing)
pip install -r requirements.txt

# Producción (mínimo)
pip install -r requirements.production.txt
```

### Frontend
```bash
cd frontend
npm install
```

## 📊 Estadísticas

- **Total dependencias Python**: 45+ paquetes
- **Total dependencias Node.js**: 25+ paquetes
- **Tamaño aproximado**: ~2GB (incluyendo PyTorch)
- **Tiempo de instalación**: 5-10 minutos

## 🔄 Actualización

### Automática
```bash
python scripts/update_dependencies.py
```

### Manual
```bash
# Python
pip install --upgrade -r requirements.txt

# Node.js
cd frontend
npm update
```

## ⚠️ Notas Importantes

1. **PyTorch**: Instalado en versión CPU por defecto. Para GPU, instalar versión específica.
2. **Dependencias de IA**: Pueden requerir mucho espacio en disco (~1.5GB).
3. **Compatibilidad**: Todas las versiones son compatibles entre sí.
4. **Seguridad**: Dependencias actualizadas con parches de seguridad.

## 🛠️ Troubleshooting

### Conflictos de Dependencias
```bash
# Limpiar cache
pip cache purge
npm cache clean --force

# Reinstalar
pip install -r requirements.txt --force-reinstall
```

### Problemas de Memoria
```bash
# Instalar sin dependencias de IA
pip install -r requirements.production.txt
```

### Versiones Específicas
```bash
# Verificar versiones instaladas
pip list
npm list
```
