#!/usr/bin/env python3
"""
Script de Verificación para GitHub - Sistema POS O'data
======================================================

Verifica que el proyecto esté completamente listo para ser subido a GitHub
como un producto terminado y profesional.

Versión: 2.0.0
Autor: Sistema POS Odata Team
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any

class GitHubReadinessChecker:
    """Verificador de preparación para GitHub"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.score = 100
        self.issues = []
        self.recommendations = []
        
    def log_issue(self, category: str, severity: str, description: str, impact: int = 5):
        """Registra un problema encontrado"""
        self.issues.append({
            'category': category,
            'severity': severity,
            'description': description,
            'impact': impact
        })
        self.score -= impact
        
        emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
        print(f"   {emoji} [{severity.upper()}] {description}")
    
    def log_success(self, category: str, description: str):
        """Registra un éxito"""
        print(f"   ✅ {description}")
    
    def log_recommendation(self, description: str, priority: str = 'medium'):
        """Registra una recomendación"""
        self.recommendations.append({
            'description': description,
            'priority': priority
        })
    
    def check_essential_files(self):
        """Verifica archivos esenciales para GitHub"""
        print("📁 Verificando archivos esenciales...")
        
        essential_files = {
            'README.md': 'critical',
            'LICENSE': 'high', 
            'requirements.txt': 'critical',
            '.gitignore': 'high',
            'DEPLOYMENT_GUIDE.md': 'medium',
            'CONTRIBUTING.md': 'medium',
            'CHANGELOG.md': 'low'
        }
        
        for file_name, severity in essential_files.items():
            file_path = self.project_root / file_name
            if file_path.exists():
                self.log_success('files', f"{file_name} presente")
            else:
                impact = {'critical': 20, 'high': 15, 'medium': 10, 'low': 5}[severity]
                self.log_issue('files', severity, f"Archivo {file_name} faltante", impact)
    
    def check_readme_quality(self):
        """Verifica la calidad del README"""
        print("\n📖 Verificando calidad del README...")
        
        readme_path = self.project_root / 'README.md'
        if not readme_path.exists():
            self.log_issue('readme', 'critical', "README.md no existe", 25)
            return
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Verificar elementos esenciales
            required_sections = [
                ('# ', 'Título principal'),
                ('## ', 'Secciones organizadas'),
                ('```', 'Ejemplos de código'),
                ('http', 'Enlaces o URLs'),
                ('![', 'Badges o imágenes'),
                ('##', 'Múltiples secciones')
            ]
            
            for pattern, description in required_sections:
                if pattern in content:
                    self.log_success('readme', f"{description} presente")
                else:
                    self.log_issue('readme', 'medium', f"{description} faltante en README", 5)
            
            # Verificar longitud
            if len(content) > 2000:
                self.log_success('readme', "README completo y detallado")
            else:
                self.log_issue('readme', 'medium', "README demasiado corto", 10)
    
    def check_code_structure(self):
        """Verifica la estructura del código"""
        print("\n🏗️ Verificando estructura del código...")
        
        required_dirs = [
            'app',
            'app/core',
            'app/models', 
            'app/api',
            'scripts',
            'tests'
        ]
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.log_success('structure', f"Directorio {dir_name}/ presente")
            else:
                self.log_issue('structure', 'medium', f"Directorio {dir_name}/ faltante", 8)
        
        # Verificar archivos __init__.py
        python_dirs = ['app', 'app/core', 'app/models', 'app/api', 'tests']
        for dir_name in python_dirs:
            init_file = self.project_root / dir_name / '__init__.py'
            if init_file.exists():
                self.log_success('structure', f"__init__.py en {dir_name}")
            else:
                self.log_issue('structure', 'low', f"__init__.py faltante en {dir_name}", 3)
    
    def check_security_files(self):
        """Verifica archivos de seguridad"""
        print("\n🔒 Verificando configuración de seguridad...")
        
        # Verificar .gitignore
        gitignore_path = self.project_root / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                security_patterns = [
                    '.env',
                    '*.log',
                    '__pycache__',
                    '*.pyc',
                    'instance/',
                    'venv'
                ]
                
                for pattern in security_patterns:
                    if pattern in content:
                        self.log_success('security', f"Patrón {pattern} en .gitignore")
                    else:
                        self.log_issue('security', 'high', f"Patrón {pattern} faltante en .gitignore", 10)
        
        # Verificar que archivos sensibles no estén presentes
        sensitive_files = ['.env', '*.db', '*.log', 'config_local.py']
        for pattern in sensitive_files:
            files = list(self.project_root.glob(pattern))
            if files:
                for file in files:
                    self.log_issue('security', 'critical', f"Archivo sensible presente: {file.name}", 15)
            else:
                self.log_success('security', f"Sin archivos sensibles: {pattern}")
    
    def check_documentation_completeness(self):
        """Verifica la completitud de la documentación"""
        print("\n📚 Verificando documentación...")
        
        doc_files = [
            ('DEPLOYMENT_GUIDE.md', 'Guía de despliegue'),
            ('SISTEMA_OPTIMIZADO_FINAL.md', 'Resumen del proyecto'),
            ('requirements.txt', 'Dependencias'),
            ('requirements-dev.txt', 'Dependencias de desarrollo')
        ]
        
        for file_name, description in doc_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                self.log_success('docs', f"{description} presente")
            else:
                self.log_issue('docs', 'medium', f"{description} faltante", 8)
    
    def check_docker_readiness(self):
        """Verifica preparación para Docker"""
        print("\n🐳 Verificando configuración Docker...")
        
        docker_files = [
            ('Dockerfile', 'Dockerfile principal'),
            ('Dockerfile.optimized', 'Dockerfile optimizado'),
            ('docker-compose.yml', 'Configuración de servicios'),
            ('.dockerignore', 'Exclusiones de Docker')
        ]
        
        for file_name, description in docker_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                self.log_success('docker', f"{description} presente")
            else:
                self.log_issue('docker', 'medium', f"{description} faltante", 5)
    
    def check_testing_setup(self):
        """Verifica configuración de testing"""
        print("\n🧪 Verificando configuración de testing...")
        
        # Verificar directorio tests
        tests_dir = self.project_root / 'tests'
        if tests_dir.exists():
            test_files = list(tests_dir.glob('test_*.py'))
            if test_files:
                self.log_success('testing', f"{len(test_files)} archivos de test encontrados")
            else:
                self.log_issue('testing', 'medium', "No se encontraron archivos de test", 10)
        else:
            self.log_issue('testing', 'high', "Directorio tests/ no existe", 15)
        
        # Verificar configuración de pytest
        pytest_files = ['pytest.ini', 'pyproject.toml', 'setup.cfg']
        pytest_found = any((self.project_root / f).exists() for f in pytest_files)
        
        if pytest_found:
            self.log_success('testing', "Configuración de pytest presente")
        else:
            self.log_issue('testing', 'low', "Configuración de pytest faltante", 5)
    
    def check_project_metadata(self):
        """Verifica metadatos del proyecto"""
        print("\n📊 Verificando metadatos del proyecto...")
        
        # Verificar que hay archivos Python
        python_files = list(self.project_root.glob('**/*.py'))
        if len(python_files) > 10:
            self.log_success('metadata', f"{len(python_files)} archivos Python encontrados")
        else:
            self.log_issue('metadata', 'high', f"Solo {len(python_files)} archivos Python", 15)
        
        # Verificar scripts útiles
        scripts_dir = self.project_root / 'scripts'
        if scripts_dir.exists():
            scripts = list(scripts_dir.glob('*.py'))
            if len(scripts) >= 3:
                self.log_success('metadata', f"{len(scripts)} scripts de utilidad")
            else:
                self.log_issue('metadata', 'medium', "Pocos scripts de utilidad", 8)
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Genera el reporte final"""
        
        # Determinar estado general
        if self.score >= 90:
            status = "EXCELENTE - LISTO PARA GITHUB"
            emoji = "🟢"
            recommendation = "¡Proyecto completamente listo para GitHub!"
        elif self.score >= 75:
            status = "BUENO - CASI LISTO"
            emoji = "🟡"
            recommendation = "Resolver problemas menores antes de subir a GitHub"
        elif self.score >= 50:
            status = "REGULAR - NECESITA TRABAJO"
            emoji = "🟠"
            recommendation = "Completar documentación y resolver problemas"
        else:
            status = "CRÍTICO - NO LISTO"
            emoji = "🔴"
            recommendation = "Trabajo significativo requerido antes de GitHub"
        
        return {
            'score': max(0, self.score),
            'status': status,
            'emoji': emoji,
            'recommendation': recommendation,
            'total_issues': len(self.issues),
            'critical_issues': len([i for i in self.issues if i['severity'] == 'critical']),
            'issues': self.issues,
            'recommendations': self.recommendations
        }
    
    def run_complete_check(self) -> Dict[str, Any]:
        """Ejecuta la verificación completa"""
        print("🔍 VERIFICACIÓN DE PREPARACIÓN PARA GITHUB")
        print("=" * 60)
        
        self.check_essential_files()
        self.check_readme_quality()
        self.check_code_structure()
        self.check_security_files()
        self.check_documentation_completeness()
        self.check_docker_readiness()
        self.check_testing_setup()
        self.check_project_metadata()
        
        return self.generate_final_report()

def print_final_report(report: Dict[str, Any]):
    """Imprime el reporte final"""
    
    print("\n" + "=" * 70)
    print("🎯 REPORTE FINAL - PREPARACIÓN PARA GITHUB")
    print("=" * 70)
    
    print(f"\n📊 ESTADO GENERAL: {report['status']} {report['emoji']}")
    print(f"📈 PUNTUACIÓN: {report['score']}/100")
    print(f"💡 RECOMENDACIÓN: {report['recommendation']}")
    
    print(f"\n📋 RESUMEN:")
    print(f"   • Total de problemas: {report['total_issues']}")
    print(f"   • Problemas críticos: {report['critical_issues']}")
    
    if report['issues']:
        print(f"\n🚨 PROBLEMAS A RESOLVER:")
        for i, issue in enumerate(report['issues'], 1):
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(issue['severity'], '⚪')
            print(f"   {i}. {emoji} [{issue['severity'].upper()}] {issue['description']}")
    
    if report['recommendations']:
        print(f"\n💡 RECOMENDACIONES:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec['description']}")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    if report['score'] >= 90:
        print("   1. 🎉 ¡Proyecto listo para GitHub!")
        print("   2. 🚀 Crear repositorio y hacer push inicial")
        print("   3. 📝 Configurar GitHub Pages si es necesario")
        print("   4. 🏷️ Crear release v2.0.0")
    elif report['score'] >= 75:
        print("   1. 🔧 Resolver problemas menores identificados")
        print("   2. 📚 Completar documentación faltante")
        print("   3. 🔄 Ejecutar verificación nuevamente")
        print("   4. 🚀 Proceder con GitHub cuando esté listo")
    else:
        print("   1. 🚨 Resolver problemas críticos primero")
        print("   2. 📋 Completar archivos esenciales faltantes")
        print("   3. 🔒 Verificar configuración de seguridad")
        print("   4. 🔄 Ejecutar verificación completa nuevamente")
    
    print("\n" + "=" * 70)

def main():
    """Función principal"""
    checker = GitHubReadinessChecker()
    report = checker.run_complete_check()
    print_final_report(report)
    
    # Guardar reporte
    report_file = checker.project_root / 'github_readiness_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n💾 Reporte guardado en: {report_file}")
    
    # Código de salida
    if report['score'] >= 90:
        print("\n🎉 ¡PROYECTO LISTO PARA GITHUB! 🎉")
        sys.exit(0)
    elif report['score'] >= 75:
        print("\n⚠️  Proyecto casi listo - resolver problemas menores")
        sys.exit(1)
    else:
        print("\n❌ Proyecto necesita más trabajo antes de GitHub")
        sys.exit(2)

if __name__ == "__main__":
    main()
