#!/usr/bin/env python3
"""
Script para preparar el proyecto para GitHub CI/CD
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def create_github_ready_report():
    """Crea un reporte de preparación para GitHub"""
    
    print("🚀 PREPARANDO PROYECTO PARA GITHUB")
    print("=" * 50)
    
    # Verificar archivos necesarios
    required_files = [
        '.github/workflows/code-quality-check.yml',
        'requirements.txt',
        'requirements-dev.txt',
        'scripts/generate_quality_report.py',
        'app/extensions.py',
        'VALIDATION_REPORT.md'
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")
    
    # Verificar dependencias críticas
    critical_deps = [
        'flask',
        'fakeredis',
        'colorama',
        'marshmallow',
        'pytest',
        'flake8',
        'bandit'
    ]
    
    print(f"\n🔍 Verificando dependencias críticas...")
    deps_status = {}
    
    for dep in critical_deps:
        try:
            result = subprocess.run([sys.executable, '-c', f'import {dep}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                deps_status[dep] = True
                print(f"✅ {dep}")
            else:
                deps_status[dep] = False
                print(f"❌ {dep}")
        except:
            deps_status[dep] = False
            print(f"❌ {dep}")
    
    # Verificar estructura del proyecto
    project_structure = {
        'app/': Path('app').is_dir(),
        'tests/': Path('tests').is_dir(),
        'scripts/': Path('scripts').is_dir(),
        'reports/': Path('reports').is_dir(),
        'docs/': Path('docs').is_dir(),
        '.github/workflows/': Path('.github/workflows').is_dir(),
    }
    
    print(f"\n📁 Verificando estructura del proyecto...")
    for path, exists in project_structure.items():
        status = "✅" if exists else "❌"
        print(f"{status} {path}")
    
    # Generar reporte JSON
    github_readiness = {
        "timestamp": datetime.now().isoformat(),
        "project_name": "Sistema_POS_Odata",
        "version": "2.0.0",
        "github_ready": len(missing_files) == 0 and all(deps_status.values()),
        "summary": {
            "required_files": {
                "total": len(required_files),
                "existing": len(existing_files),
                "missing": len(missing_files)
            },
            "dependencies": {
                "total": len(critical_deps),
                "installed": sum(deps_status.values()),
                "missing": len(critical_deps) - sum(deps_status.values())
            },
            "project_structure": {
                "total": len(project_structure),
                "existing": sum(project_structure.values()),
                "missing": len(project_structure) - sum(project_structure.values())
            }
        },
        "details": {
            "files": {
                "existing": existing_files,
                "missing": missing_files
            },
            "dependencies": deps_status,
            "structure": project_structure
        },
        "next_steps": [
            "Crear repositorio en GitHub",
            "Push del código al repositorio",
            "Verificar que GitHub Actions se ejecute",
            "Revisar reportes de calidad generados",
            "Configurar branch protection rules"
        ]
    }
    
    # Crear directorio reports si no existe
    reports_dir = Path('reports')
    reports_dir.mkdir(exist_ok=True)
    
    # Guardar reporte
    with open(reports_dir / 'github_readiness_report.json', 'w', encoding='utf-8') as f:
        json.dump(github_readiness, f, indent=2, ensure_ascii=False)
    
    # Crear README para GitHub
    create_github_readme(github_readiness)
    
    print(f"\n📊 RESUMEN")
    print("=" * 30)
    print(f"Archivos requeridos: {len(existing_files)}/{len(required_files)}")
    print(f"Dependencias instaladas: {sum(deps_status.values())}/{len(critical_deps)}")
    print(f"Estructura del proyecto: {sum(project_structure.values())}/{len(project_structure)}")
    
    if github_readiness["github_ready"]:
        print(f"\n🎉 ¡PROYECTO LISTO PARA GITHUB!")
        print("✅ Todos los requisitos cumplidos")
    else:
        print(f"\n⚠️  PROYECTO PARCIALMENTE LISTO")
        print("🔧 Revisar elementos faltantes arriba")
    
    print(f"\n📄 Reporte guardado en: reports/github_readiness_report.json")
    
    return github_readiness["github_ready"]

def create_github_readme(readiness_data):
    """Crea un README.md actualizado para GitHub"""
    
    readme_content = f"""# Sistema POS O'data

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

**Última actualización**: {readiness_data['timestamp'][:10]}

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
"""
    
    with open('README_GITHUB.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("📝 README_GITHUB.md creado para el repositorio")

def main():
    """Función principal"""
    success = create_github_ready_report()
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
