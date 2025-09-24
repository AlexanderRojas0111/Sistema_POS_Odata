## v2.0.2-enterprise-r1 (2025-09-24)

### Resumen
- Alineación completa de versiones internas y documentación a `v2.0.2-enterprise`.
- Creación de rama `release/v2.0.2-enterprise` y tag anotado `v2.0.2-enterprise-r1`.

### Cambios
- app/__init__.py: APP_VERSION y versiones de endpoints `health`, `ai-test` e `index`.
- app/core/__init__.py: __version__ actualizado.
- app/api/__init__.py: __version__ actualizado.
- VERSION.md: versión actual a `2.0.2-enterprise` y registro de cambios.
- README.md: título actualizado a `v2.0.2-enterprise`.

### Artefactos
- Tag: v2.0.2-enterprise-r1
- Rama de release: release/v2.0.2-enterprise

### Commit base
- ce60f15 chore(version): alinear a v2.0.2-enterprise en código y docs

# 📋 Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Sistema de búsqueda semántica con IA
- Agentes inteligentes para monitoreo de inventario
- Protocolo de comunicación MCP
- Dashboard interactivo con métricas en tiempo real
- Sistema de autenticación JWT avanzado
- API RESTful completa (v1 y v2)
- Frontend React con Material-UI
- Monitoreo con Prometheus y Grafana
- Containerización con Docker
- CI/CD con GitHub Actions

### Changed
- Migración a Flask 3.1.1
- Actualización a React 19.1.1
- Mejoras en la arquitectura del sistema
- Optimización de dependencias

### Fixed
- Correcciones de seguridad
- Mejoras en el rendimiento
- Bug fixes varios

## [2.0.0] - 2024-01-15

### Added
- Versión inicial del Sistema POS Odata
- Funcionalidades básicas de POS
- Gestión de inventario
- Sistema de ventas
- Reportes básicos

---

## Tipos de Cambios

- **Added** para nuevas funcionalidades
- **Changed** para cambios en funcionalidades existentes
- **Deprecated** para funcionalidades que serán removidas
- **Removed** para funcionalidades removidas
- **Fixed** para correcciones de bugs
- **Security** para vulnerabilidades de seguridad
