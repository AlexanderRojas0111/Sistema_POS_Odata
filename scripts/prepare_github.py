#!/usr/bin/env python3
"""
Script para preparar el proyecto Sistema POS Odata para GitHub
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Ejecutar comando y manejar errores"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando: {command}")
        print(f"Error: {e.stderr}")
        return None

def check_git_status():
    """Verificar si estamos en un repositorio Git"""
    if not os.path.exists('.git'):
        print("❌ No se encontró un repositorio Git")
        return False
    return True

def initialize_git():
    """Inicializar repositorio Git si no existe"""
    if not os.path.exists('.git'):
        print("🔧 Inicializando repositorio Git...")
        run_command("git init")
        run_command("git add .")
        run_command('git commit -m "feat: Initial commit - Sistema POS Odata"')
        print("✅ Repositorio Git inicializado")
    else:
        print("✅ Repositorio Git ya existe")

def create_branches():
    """Crear ramas principales"""
    branches = ['main', 'develop']
    current_branch = run_command("git branch --show-current")
    
    for branch in branches:
        if branch != current_branch:
            print(f"🌿 Creando rama: {branch}")
            run_command(f"git checkout -b {branch}")
    
    # Volver a la rama principal
    run_command("git checkout main")

def setup_remote(remote_url):
    """Configurar repositorio remoto"""
    print(f"🔗 Configurando repositorio remoto: {remote_url}")
    run_command(f"git remote add origin {remote_url}")
    run_command("git branch -M main")
    print("✅ Repositorio remoto configurado")

def create_github_files():
    """Crear archivos específicos de GitHub"""
    
    # CONTRIBUTING.md
    contributing_content = """# 🤝 Guía de Contribución

## Cómo Contribuir

### 1. Fork del Repositorio
- Haz fork del repositorio en GitHub
- Clona tu fork localmente

### 2. Crear Rama de Feature
```bash
git checkout -b feature/nueva-funcionalidad
```

### 3. Desarrollar
- Escribe código limpio y bien documentado
- Sigue las convenciones del proyecto
- Añade tests para nuevas funcionalidades

### 4. Commit
```bash
git add .
git commit -m "feat: Agregar nueva funcionalidad"
```

### 5. Push y Pull Request
```bash
git push origin feature/nueva-funcionalidad
```

### 6. Crear Pull Request
- Ve a GitHub y crea un Pull Request
- Describe claramente los cambios
- Espera la revisión del equipo

## Convenciones

### Commits
Usa [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Documentación
- `style:` Formato de código
- `refactor:` Refactorización
- `test:` Tests
- `chore:` Tareas de mantenimiento

### Código
- Python: PEP 8
- JavaScript: ESLint + Prettier
- Tests obligatorios para nuevas funcionalidades
- Documentación en español

## Estructura del Proyecto

```
Sistema_POS_Odata/
├── app/           # Backend Flask
├── frontend/      # Frontend React
├── docs/          # Documentación
├── scripts/       # Scripts de utilidad
└── tests/         # Tests automatizados
```

## Contacto

- 📧 Email: soporte@odata.com
- 💬 Discord: [Servidor Odata](https://discord.gg/odata)
- 🐛 Issues: [GitHub Issues](https://github.com/odata/sistema-pos/issues)

¡Gracias por contribuir! 🚀
"""
    
    with open('CONTRIBUTING.md', 'w', encoding='utf-8') as f:
        f.write(contributing_content)
    
    # CHANGELOG.md
    changelog_content = """# 📋 Changelog

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
"""
    
    with open('CHANGELOG.md', 'w', encoding='utf-8') as f:
        f.write(changelog_content)
    
    # SECURITY.md
    security_content = """# 🔒 Política de Seguridad

## Reportar una Vulnerabilidad

Si descubres una vulnerabilidad de seguridad en el Sistema POS Odata, por favor sigue estos pasos:

### 1. **NO** crear un issue público
- Las vulnerabilidades de seguridad deben ser reportadas de forma privada
- No publiques detalles en GitHub Issues o en foros públicos

### 2. Contacto Privado
Envía un email a: **security@odata.com**

### 3. Información Requerida
Incluye en tu reporte:
- Descripción detallada de la vulnerabilidad
- Pasos para reproducir el problema
- Impacto potencial
- Sugerencias de mitigación (si las tienes)

### 4. Respuesta
- Recibirás confirmación en 24-48 horas
- Mantendremos comunicación durante la investigación
- Te notificaremos cuando se publique el fix

## Versiones Soportadas

| Versión | Soportada          |
| ------- | ------------------ |
| 2.x.x   | ✅ Sí              |
| 1.x.x   | ❌ No              |

## Mejores Prácticas de Seguridad

### Para Desarrolladores
- Nunca committear credenciales o secrets
- Usar variables de entorno para configuraciones sensibles
- Validar todas las entradas de usuario
- Mantener dependencias actualizadas
- Seguir principios de seguridad por defecto

### Para Usuarios
- Mantener el sistema actualizado
- Usar contraseñas fuertes
- Habilitar autenticación de dos factores
- Revisar logs regularmente
- Hacer backups frecuentes

## Historial de Vulnerabilidades

### 2024-01-15
- **CVE-2024-XXXX**: Vulnerabilidad en autenticación JWT
  - **Estado**: Parcheado en v2.0.1
  - **Impacto**: Bajo
  - **Solución**: Actualizar a la última versión

## Agradecimientos

Gracias a todos los investigadores de seguridad que han reportado vulnerabilidades de forma responsable.

---

**Equipo de Seguridad de Odata**
"""
    
    with open('SECURITY.md', 'w', encoding='utf-8') as f:
        f.write(security_content)
    
    print("✅ Archivos de GitHub creados")

def main():
    """Función principal"""
    print("🚀 Preparando Sistema POS Odata para GitHub...")
    
    # Verificar Git
    if not check_git_status():
        initialize_git()
    
    # Crear archivos de GitHub
    create_github_files()
    
    # Crear ramas
    create_branches()
    
    # Preguntar por URL remota
    remote_url = input("\n🔗 Ingresa la URL del repositorio de GitHub (o presiona Enter para saltar): ").strip()
    
    if remote_url:
        setup_remote(remote_url)
        print(f"\n📤 Para subir a GitHub, ejecuta:")
        print(f"git push -u origin main")
        print(f"git push -u origin develop")
    
    print("\n✅ Proyecto preparado para GitHub!")
    print("\n📋 Próximos pasos:")
    print("1. Crear repositorio en GitHub")
    print("2. Configurar secrets en GitHub (DOCKER_USERNAME, DOCKER_PASSWORD)")
    print("3. Configurar environments (staging, production)")
    print("4. Habilitar GitHub Actions")
    print("5. Configurar branch protection rules")

if __name__ == "__main__":
    main()
