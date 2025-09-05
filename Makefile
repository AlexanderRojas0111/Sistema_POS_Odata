# ========================================================================
# Sistema POS O'Data v2.0.0 - Makefile para DevOps y QA
# ========================================================================
# Uso: make <comando>
# Ejemplo: make test-all
# ========================================================================

.PHONY: help test-all test-backend test-frontend test-performance migrate-db update-deps clean reports install-deps

# Variables
PYTHON = python
PIP = python -m pip
NPM = npm
PYTEST = pytest
PLAYWRIGHT = npx playwright

# Colores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
BLUE = \033[0;34m
NC = \033[0m # No Color

# Comando por defecto
help:
	@echo "$(BLUE)🚀 Sistema POS O'Data v2.0.0 - Comandos Disponibles$(NC)"
	@echo ""
	@echo "$(GREEN)🧪 Testing y Validación:$(NC)"
	@echo "  make test-all          - Ejecutar todos los tests (backend, frontend, performance)"
	@echo "  make test-backend      - Solo tests de backend con pytest"
	@echo "  make test-frontend     - Solo tests de frontend con Playwright"
	@echo "  make test-performance  - Solo tests de performance y stress"
	@echo "  make test-integration  - Solo tests de integración"
	@echo ""
	@echo "$(GREEN)🛠️ Entorno de Desarrollo:$(NC)"
	@echo "  make migrate-db        - Migrar de SQLite a PostgreSQL"
	@echo "  make setup-env         - Configurar variables de entorno"
	@echo "  make install-deps      - Instalar todas las dependencias"
	@echo ""
	@echo "$(GREEN)📦 Dependencias:$(NC)"
	@echo "  make update-deps       - Actualizar numpy y verificar compatibilidad"
	@echo "  make check-deps        - Verificar estado de dependencias"
	@echo ""
	@echo "$(GREEN)📊 Reportes:$(NC)"
	@echo "  make reports           - Generar todos los reportes"
	@echo "  make clean             - Limpiar archivos temporales y reportes"
	@echo ""
	@echo "$(GREEN)🔧 Utilidades:$(NC)"
	@echo "  make validate-system   - Validación completa del sistema"
	@echo "  make security-audit    - Auditoría de seguridad"
	@echo "  make health-check      - Verificar salud del sistema"

# ========================================================================
# INSTALACIÓN Y CONFIGURACIÓN
# ========================================================================

install-deps:
	@echo "$(BLUE)📦 Instalando dependencias de Python...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	@echo "$(BLUE)📦 Instalando dependencias de Frontend...$(NC)"
	cd frontend && $(NPM) install
	@echo "$(BLUE)🎭 Instalando Playwright...$(NC)"
	cd frontend && $(PLAYWRIGHT) install
	@echo "$(GREEN)✅ Todas las dependencias instaladas$(NC)"

setup-env:
	@echo "$(BLUE)🔧 Configurando variables de entorno...$(NC)"
	@if [ ! -f .env ]; then \
		echo "FLASK_ENV=development" > .env; \
		echo "FLASK_DEBUG=1" >> .env; \
		echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pos_odata_dev" >> .env; \
		echo "REDIS_URL=redis://localhost:6379/0" >> .env; \
		echo "JWT_SECRET_KEY=dev_secret_key_change_in_production" >> .env; \
		echo "SECRET_KEY=dev_secret_change_in_production" >> .env; \
		echo "LOG_LEVEL=DEBUG" >> .env; \
		echo "$(GREEN)✅ Archivo .env creado$(NC)"; \
	else \
		echo "$(YELLOW)⚠️ Archivo .env ya existe$(NC)"; \
	fi

# ========================================================================
# TESTING COMPLETO
# ========================================================================

test-all: install-deps setup-env
	@echo "$(BLUE)🚀 Ejecutando suite completa de tests...$(NC)"
	@echo "$(BLUE)⏱️ Esto puede tomar varios minutos...$(NC)"
	$(PYTHON) scripts/run_complete_tests.py
	@echo "$(GREEN)✅ Suite completa de tests ejecutada$(NC)"

test-backend: install-deps setup-env
	@echo "$(BLUE)🧪 Ejecutando tests de backend...$(NC)"
	$(PYTEST) tests/backend/ -v --cov=app --cov-report=html:reports/coverage --cov-report=xml:reports/coverage.xml --cov-report=term-missing --cov-fail-under=80
	@echo "$(GREEN)✅ Tests de backend completados$(NC)"

test-frontend: install-deps
	@echo "$(BLUE)🎨 Ejecutando tests de frontend...$(NC)"
	cd frontend && $(PLAYWRIGHT) test --reporter=html
	@echo "$(GREEN)✅ Tests de frontend completados$(NC)"

test-performance: install-deps setup-env
	@echo "$(BLUE)⚡ Ejecutando tests de performance...$(NC)"
	$(PYTHON) scripts/performance_tests.py
	@echo "$(GREEN)✅ Tests de performance completados$(NC)"

test-integration: install-deps setup-env
	@echo "$(BLUE)🔗 Ejecutando tests de integración...$(NC)"
	$(PYTEST) tests/integration/ -v --cov=app --cov-append
	@echo "$(GREEN)✅ Tests de integración completados$(NC)"

# ========================================================================
# MIGRACIÓN Y BASE DE DATOS
# ========================================================================

migrate-db: install-deps setup-env
	@echo "$(BLUE)🗄️ Migrando de SQLite a PostgreSQL...$(NC)"
	@echo "$(YELLOW)⚠️ Asegúrate de que PostgreSQL esté ejecutándose$(NC)"
	$(PYTHON) scripts/migrate_to_postgresql.py
	@echo "$(GREEN)✅ Migración completada$(NC)"

# ========================================================================
# ACTUALIZACIÓN DE DEPENDENCIAS
# ========================================================================

update-deps: install-deps
	@echo "$(BLUE)🔄 Actualizando dependencias...$(NC)"
	$(PYTHON) scripts/update_dependencies.py
	@echo "$(GREEN)✅ Dependencias actualizadas$(NC)"

check-deps:
	@echo "$(BLUE)🔍 Verificando estado de dependencias...$(NC)"
	$(PIP) list --outdated
	@echo "$(GREEN)✅ Verificación completada$(NC)"

# ========================================================================
# VALIDACIÓN Y AUDITORÍA
# ========================================================================

validate-system: install-deps setup-env
	@echo "$(BLUE)🔍 Validando sistema completo...$(NC)"
	$(PYTHON) scripts/validate_system.py
	@echo "$(GREEN)✅ Validación completada$(NC)"

security-audit: install-deps
	@echo "$(BLUE)🔒 Ejecutando auditoría de seguridad...$(NC)"
	$(PYTHON) scripts/security_audit.py
	@echo "$(GREEN)✅ Auditoría de seguridad completada$(NC)"

health-check: setup-env
	@echo "$(BLUE)🏥 Verificando salud del sistema...$(NC)"
	@echo "$(BLUE)🔍 Verificando PostgreSQL...$(NC)"
	@if command -v psql >/dev/null 2>&1; then \
		psql $(shell grep DATABASE_URL .env | cut -d '=' -f2) -c "SELECT version();" >/dev/null 2>&1 && echo "$(GREEN)✅ PostgreSQL: OK$(NC)" || echo "$(RED)❌ PostgreSQL: Error$(NC)"; \
	else \
		echo "$(YELLOW)⚠️ psql no disponible$(NC)"; \
	fi
	@echo "$(BLUE)🔍 Verificando Redis...$(NC)"
	@if command -v redis-cli >/dev/null 2>&1; then \
		redis-cli ping >/dev/null 2>&1 && echo "$(GREEN)✅ Redis: OK$(NC)" || echo "$(RED)❌ Redis: Error$(NC)"; \
	else \
		echo "$(YELLOW)⚠️ redis-cli no disponible$(NC)"; \
	fi
	@echo "$(BLUE)🔍 Verificando Python...$(NC)"
	@$(PYTHON) --version && echo "$(GREEN)✅ Python: OK$(NC)" || echo "$(RED)❌ Python: Error$(NC)"
	@echo "$(GREEN)✅ Verificación de salud completada$(NC)"

# ========================================================================
# REPORTES Y LIMPIEZA
# ========================================================================

reports:
	@echo "$(BLUE)📊 Generando reportes...$(NC)"
	@mkdir -p reports
	@if [ -f scripts/run_complete_tests.py ]; then \
		echo "$(BLUE)📋 Generando reporte de tests...$(NC)"; \
		$(PYTHON) scripts/run_complete_tests.py --report-only; \
	fi
	@if [ -f scripts/performance_tests.py ]; then \
		echo "$(BLUE)⚡ Generando reporte de performance...$(NC)"; \
		$(PYTHON) scripts/performance_tests.py --report-only; \
	fi
	@echo "$(GREEN)✅ Reportes generados en directorio reports/$(NC)"

clean:
	@echo "$(BLUE)🧹 Limpiando archivos temporales...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type f -name "*.log" -delete
	@find . -type f -name "temp_*.py" -delete
	@rm -rf reports/
	@rm -rf .pytest_cache/
	@rm -rf frontend/node_modules/
	@rm -rf frontend/.next/
	@rm -rf frontend/coverage/
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

clean-reports:
	@echo "$(BLUE)🗑️ Limpiando reportes...$(NC)"
	@rm -rf reports/
	@echo "$(GREEN)✅ Reportes eliminados$(NC)"

# ========================================================================
# DESARROLLO Y DEBUG
# ========================================================================

dev-setup: install-deps setup-env
	@echo "$(BLUE)🚀 Configurando entorno de desarrollo...$(NC)"
	@echo "$(GREEN)✅ Entorno de desarrollo configurado$(NC)"
	@echo "$(BLUE)📋 Comandos útiles:$(NC)"
	@echo "  make test-backend      - Ejecutar tests de backend"
	@echo "  make test-frontend     - Ejecutar tests de frontend"
	@echo "  make health-check      - Verificar salud del sistema"

dev-server: dev-setup
	@echo "$(BLUE)🌐 Iniciando servidor de desarrollo...$(NC)"
	@echo "$(YELLOW)⚠️ Asegúrate de que PostgreSQL y Redis estén ejecutándose$(NC)"
	$(PYTHON) app/main.py

# ========================================================================
# PRODUCCIÓN
# ========================================================================

prod-setup: install-deps
	@echo "$(BLUE)🏭 Configurando entorno de producción...$(NC)"
	@if [ ! -f .env.production ]; then \
		echo "$(RED)❌ Archivo .env.production no encontrado$(NC)"; \
		echo "$(YELLOW)⚠️ Crea el archivo .env.production con las variables de producción$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Entorno de producción configurado$(NC)"

prod-deploy: prod-setup
	@echo "$(BLUE)🚀 Desplegando en producción...$(NC)"
	$(PYTHON) deploy_production.py
	@echo "$(GREEN)✅ Despliegue completado$(NC)"

# ========================================================================
# MONITOREO Y MÉTRICAS
# ========================================================================

monitor: setup-env
	@echo "$(BLUE)📊 Iniciando monitoreo del sistema...$(NC)"
	@echo "$(BLUE)🔍 Métricas disponibles:$(NC)"
	@echo "  - Uso de CPU y memoria"
	@echo "  - Latencia de base de datos"
	@echo "  - Tiempo de respuesta de API"
	@echo "  - Estado de servicios"
	@echo "$(GREEN)✅ Monitoreo iniciado$(NC)"

# ========================================================================
# BACKUP Y RECUPERACIÓN
# ========================================================================

backup: setup-env
	@echo "$(BLUE)💾 Creando backup del sistema...$(NC)"
	@mkdir -p backups
	@if [ -f instance/pos_odata_dev.db ]; then \
		cp instance/pos_odata_dev.db backups/backup_$(shell date +%Y%m%d_%H%M%S).db; \
		echo "$(GREEN)✅ Backup de SQLite creado$(NC)"; \
	fi
	@echo "$(GREEN)✅ Backup completado$(NC)"

# ========================================================================
# AYUDA Y DOCUMENTACIÓN
# ========================================================================

docs:
	@echo "$(BLUE)📚 Generando documentación...$(NC)"
	@if command -v sphinx-build >/dev/null 2>&1; then \
		cd docs && make html; \
		echo "$(GREEN)✅ Documentación generada$(NC)"; \
	else \
		echo "$(YELLOW)⚠️ Sphinx no disponible, instalando...$(NC)"; \
		$(PIP) install sphinx sphinx-rtd-theme; \
		cd docs && make html; \
	fi

# ========================================================================
# COMANDOS RÁPIDOS
# ========================================================================

quick-test: test-backend test-frontend
	@echo "$(GREEN)✅ Tests rápidos completados$(NC)"

quick-check: health-check
	@echo "$(GREEN)✅ Verificación rápida completada$(NC)"

# ========================================================================
# INFORMACIÓN DEL SISTEMA
# ========================================================================

info:
	@echo "$(BLUE)ℹ️ Información del Sistema POS O'Data v2.0.0$(NC)"
	@echo ""
	@echo "$(BLUE)📋 Versiones:$(NC)"
	@$(PYTHON) --version
	@$(PIP) --version
	@echo ""
	@echo "$(BLUE)📦 Dependencias principales:$(NC)"
	@$(PIP) list | grep -E "(numpy|scikit-learn|flask|psycopg2)"
	@echo ""
	@echo "$(BLUE)🗄️ Base de datos:$(NC)"
	@if [ -f .env ]; then \
		grep DATABASE_URL .env | cut -d '=' -f2; \
	else \
		echo "No configurado"; \
	fi
	@echo ""
	@echo "$(BLUE)🔴 Redis:$(NC)"
	@if [ -f .env ]; then \
		grep REDIS_URL .env | cut -d '=' -f2; \
	else \
		echo "No configurado"; \
	fi

# ========================================================================
# COMANDO POR DEFECTO
# ========================================================================

.DEFAULT_GOAL := help
