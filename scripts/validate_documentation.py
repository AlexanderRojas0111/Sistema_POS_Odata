#!/usr/bin/env python3
"""
Validador de documentación y scripts
Sistema POS O'Data v2.0.0
"""

import os
import sys
from pathlib import Path
import re

class DocumentationValidator:
    def __init__(self):
        self.issues = []
        self.warnings = []
        
    def check_documentation_files(self):
        """Verificar archivos de documentación"""
        print('🔍 VERIFICANDO DOCUMENTACIÓN')
        print('-' * 40)
        
        required_docs = [
            ('README.md', 'Documentación principal del proyecto'),
            ('EMAIL_SETUP.md', 'Configuración de email'),
            ('SECURITY_YAML_GUIDE.md', 'Guía de seguridad YAML'),
            ('TYPESCRIPT_CLEANUP_REPORT.md', 'Reporte de limpieza TypeScript')
        ]
        
        for doc_file, description in required_docs:
            if os.path.exists(doc_file):
                # Verificar que no esté vacío
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if len(content) > 100:  # Al menos 100 caracteres
                    print(f'✅ {doc_file} - {description}')
                else:
                    self.warnings.append(f'{doc_file} parece estar vacío o incompleto')
                    print(f'⚠️ {doc_file} - Incompleto')
            else:
                self.issues.append(f'Falta documentación: {doc_file}')
                print(f'❌ {doc_file} - FALTANTE')
    
    def check_scripts_functionality(self):
        """Verificar funcionalidad de scripts"""
        print('\n🔍 VERIFICANDO SCRIPTS')
        print('-' * 40)
        
        scripts_dir = Path('scripts')
        if not scripts_dir.exists():
            self.issues.append('Directorio scripts/ no existe')
            return
        
        python_scripts = list(scripts_dir.glob('*.py'))
        
        for script in python_scripts:
            try:
                with open(script, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificaciones básicas
                has_main = 'if __name__ == ' in content
                has_docstring = '"""' in content or "'''" in content
                has_imports = 'import ' in content
                
                issues_found = []
                if not has_main:
                    issues_found.append('sin función main')
                if not has_docstring:
                    issues_found.append('sin docstring')
                if not has_imports and len(content) > 100:
                    issues_found.append('sin imports')
                
                if issues_found:
                    self.warnings.append(f'{script.name}: {", ".join(issues_found)}')
                    print(f'⚠️ {script.name} - {", ".join(issues_found)}')
                else:
                    print(f'✅ {script.name} - Script bien estructurado')
                    
            except Exception as e:
                self.issues.append(f'Error leyendo {script.name}: {str(e)}')
                print(f'❌ {script.name} - Error: {str(e)}')
    
    def check_readme_completeness(self):
        """Verificar completitud del README principal"""
        print('\n🔍 VERIFICANDO README PRINCIPAL')
        print('-' * 40)
        
        if not os.path.exists('README.md'):
            self.issues.append('README.md principal no existe')
            return
        
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_sections = [
            ('# ', 'Título principal'),
            ('## ', 'Secciones organizadas'),
            ('install', 'Instrucciones de instalación'),
            ('usage', 'Instrucciones de uso'),
        ]
        
        missing_sections = []
        for pattern, description in required_sections:
            if pattern.lower() not in content.lower():
                missing_sections.append(description)
        
        if missing_sections:
            self.warnings.append(f'README.md falta: {", ".join(missing_sections)}')
            print(f'⚠️ README.md - Faltan secciones: {", ".join(missing_sections)}')
        else:
            print('✅ README.md - Completo')
    
    def check_frontend_documentation(self):
        """Verificar documentación del frontend"""
        print('\n🔍 VERIFICANDO DOCUMENTACIÓN FRONTEND')
        print('-' * 40)
        
        frontend_readme = 'frontend/README.md'
        if os.path.exists(frontend_readme):
            with open(frontend_readme, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if len(content.strip()) > 50:
                print('✅ frontend/README.md - Presente y con contenido')
            else:
                self.warnings.append('frontend/README.md está vacío o incompleto')
                print('⚠️ frontend/README.md - Incompleto')
        else:
            self.warnings.append('Falta frontend/README.md')
            print('⚠️ frontend/README.md - FALTANTE')
    
    def generate_documentation_report(self):
        """Generar reporte de documentación"""
        print('\n' + '=' * 60)
        print('📚 REPORTE DE VALIDACIÓN DE DOCUMENTACIÓN')
        print('=' * 60)
        
        if self.issues:
            print(f'\n❌ PROBLEMAS CRÍTICOS ({len(self.issues)}):')
            for issue in self.issues:
                print(f'   • {issue}')
        
        if self.warnings:
            print(f'\n⚠️ ADVERTENCIAS ({len(self.warnings)}):')
            for warning in self.warnings:
                print(f'   • {warning}')
        
        if not self.issues and not self.warnings:
            print('\n🎉 ¡Documentación en excelente estado!')
        
        # Calcular puntuación
        total_issues = len(self.issues) + len(self.warnings)
        if total_issues == 0:
            doc_score = 'A+ (Excelente)'
        elif total_issues <= 2:
            doc_score = 'A (Muy Bueno)'
        elif total_issues <= 5:
            doc_score = 'B (Bueno)'
        else:
            doc_score = 'C (Necesita Mejoras)'
        
        print(f'\n🎯 PUNTUACIÓN DOCUMENTACIÓN: {doc_score}')
        print('=' * 60)
        
        return len(self.issues) == 0

def main():
    """Función principal"""
    print('🚀 VALIDANDO DOCUMENTACIÓN Y SCRIPTS')
    print('=' * 60)
    
    validator = DocumentationValidator()
    
    # Ejecutar validaciones
    validator.check_documentation_files()
    validator.check_scripts_functionality()
    validator.check_readme_completeness()
    validator.check_frontend_documentation()
    
    # Generar reporte
    is_complete = validator.generate_documentation_report()
    
    return 0 if is_complete else 1

if __name__ == '__main__':
    sys.exit(main())
