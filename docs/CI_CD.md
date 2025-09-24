# CI/CD Pipeline Documentation

## 📋 Overview

El sistema POS O'data utiliza un pipeline CI/CD completo basado en GitHub Actions que automatiza pruebas, análisis de código, seguridad y despliegue.

## 🏗️ Arquitectura del Pipeline

### Workflows Principales

#### 1. **CI/CD Pipeline Principal** (`.github/workflows/ci.yml`)
- **Trigger**: Push a `main`/`develop`, Pull Requests
- **Jobs**:
  - **Tests y Coverage**: Ejecuta tests con cobertura
  - **Linting y Formato**: Black, Flake8, MyPy
  - **Análisis de Seguridad**: Safety, Bandit
  - **Frontend Tests**: Tests de React
  - **Build Docker**: Construye imagen Docker
  - **Despliegue Staging**: Despliegue automático a staging
  - **Despliegue Producción**: Despliegue automático a producción
  - **Notificaciones**: Notifica resultados

#### 2. **Pull Request Check** (`.github/workflows/pr-check.yml`)
- **Trigger**: Pull Requests
- **Jobs**:
  - **Quick Validation**: Tests rápidos y validaciones básicas
  - **Frontend Check**: Linting y tests de frontend
  - **Comment on PR**: Comenta resultados en el PR

#### 3. **CodeQL Security** (`.github/workflows/codeql.yml`)
- **Trigger**: Push, PR, Schedule (semanal)
- **Jobs**:
  - **CodeQL Analysis**: Análisis de seguridad avanzado

## 🔧 Configuración

### Variables de Entorno

```yaml
env:
  PYTHON_VERSION: '3.9'
  NODE_VERSION: '18'
```

### Servicios de Base de Datos

El pipeline incluye servicios de base de datos para testing:

```yaml
services:
  postgres:
    image: postgres:13
    env:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: test_db
    ports:
      - 5432:5432
  
  redis:
    image: redis:6
    ports:
      - 6379:6379
```

## 🧪 Tests y Coverage

### Backend Tests
```bash
pytest --cov=app --cov-report=xml --cov-report=html --cov-report=term-missing
```

### Frontend Tests
```bash
npm test -- --watchAll=false --coverage
```

### Coverage Reports
- **XML**: Para integración con herramientas externas
- **HTML**: Para visualización local
- **Terminal**: Para logs del pipeline

## 🔍 Análisis de Código

### Linting
- **Black**: Formateo de código
- **Flake8**: Análisis de estilo y errores
- **MyPy**: Verificación de tipos

### Seguridad
- **Safety**: Vulnerabilidades en dependencias
- **Bandit**: Análisis de seguridad del código
- **CodeQL**: Análisis de seguridad avanzado

## 🚀 Despliegue

### Estrategia de Despliegue

1. **Develop Branch** → **Staging Environment**
2. **Main Branch** → **Production Environment**

### Condiciones de Despliegue

```yaml
# Staging
if: github.event_name == 'push' && github.ref == 'refs/heads/develop'

# Production
if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

## 📦 Dependabot

### Configuración Automática

Dependabot está configurado para mantener actualizadas:

- **Python dependencies** (pip)
- **Node.js dependencies** (npm)
- **GitHub Actions**
- **Docker dependencies**

### Schedule
- **Frecuencia**: Semanal (Lunes 9:00 AM)
- **Límite de PRs**: 10 por ecosistema
- **Auto-assign**: Asigna automáticamente a reviewers

## 🔧 Herramientas Locales

### Pre-commit Hook

Ejecuta validaciones locales antes de cada commit:

```bash
# Hacer ejecutable
chmod +x scripts/pre-commit.sh

# Ejecutar manualmente
./scripts/pre-commit.sh
```

### Validaciones Incluidas

1. **Sintaxis Python**
2. **Formateo con Black**
3. **Linting con Flake8**
4. **Tests básicos**
5. **Análisis de seguridad**
6. **Verificación de TODOs**
7. **Tamaño de archivos**
8. **Secretos hardcodeados**

## 📊 Monitoreo y Notificaciones

### Notificaciones Automáticas

El pipeline notifica automáticamente:

- **Éxito**: Todos los checks pasaron
- **Fallo**: Algún check falló
- **PR Comments**: Resultados en Pull Requests

### Integración con Herramientas

- **Codecov**: Cobertura de código
- **Slack/Discord**: Notificaciones de equipo
- **GitHub Security**: Alertas de seguridad

## 🛠️ Troubleshooting

### Problemas Comunes

#### 1. **Tests Fallando**
```bash
# Ejecutar tests localmente
pytest tests/ -v

# Verificar configuración
python -c "from app import create_app; app = create_app('testing')"
```

#### 2. **Linting Issues**
```bash
# Formatear código
black app/ tests/

# Verificar linting
flake8 app/ tests/
```

#### 3. **Security Issues**
```bash
# Verificar vulnerabilidades
safety check

# Análisis de seguridad
bandit -r app/
```

### Logs y Debugging

- **GitHub Actions Logs**: Disponibles en la pestaña Actions
- **Artifacts**: Reportes de seguridad y coverage
- **Local Testing**: Usar pre-commit hook

## 🔄 Flujo de Trabajo

### Para Desarrolladores

1. **Crear Feature Branch**
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```

2. **Desarrollo Local**
   ```bash
   # Ejecutar pre-commit hook
   ./scripts/pre-commit.sh
   
   # Commit cambios
   git add .
   git commit -m "feat: nueva funcionalidad"
   ```

3. **Push y PR**
   ```bash
   git push origin feature/nueva-funcionalidad
   # Crear Pull Request en GitHub
   ```

4. **Revisión Automática**
   - Pipeline ejecuta validaciones
   - Comentarios automáticos en PR
   - Aprobación requerida para merge

### Para Releases

1. **Merge a Develop**
   - Tests automáticos
   - Despliegue a staging

2. **Merge a Main**
   - Tests completos
   - Build de Docker
   - Despliegue a producción

## 📈 Métricas y KPIs

### Métricas del Pipeline

- **Tiempo de ejecución**: < 15 minutos
- **Cobertura de tests**: > 80%
- **Tasa de éxito**: > 95%
- **Tiempo de respuesta**: < 5 minutos

### Monitoreo Continuo

- **Uptime**: Monitoreo de servicios
- **Performance**: Métricas de aplicación
- **Security**: Escaneo continuo de vulnerabilidades

## 🔐 Seguridad

### Buenas Prácticas

1. **Secretos**: Usar GitHub Secrets
2. **Dependencias**: Actualización automática
3. **Análisis**: Escaneo continuo
4. **Auditoría**: Logs de todas las operaciones

### Compliance

- **OWASP**: Seguimiento de mejores prácticas
- **GDPR**: Protección de datos
- **SOC2**: Estándares de seguridad

## 📚 Recursos Adicionales

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [CodeQL Documentation](https://docs.github.com/en/code-security/codeql-cli)
- [Flake8 Configuration](https://flake8.pycqa.org/en/latest/user/configuration.html)
- [Black Configuration](https://black.readthedocs.io/en/stable/usage_and_configuration/) 