#!/usr/bin/env python3
"""
Auditoría de seguridad del sistema
Sistema POS O'Data v2.0.0
"""

import os
import re
import sys
from pathlib import Path
import hashlib
import json

class SecurityAuditor:
    def __init__(self):
        self.vulnerabilities = []
        self.warnings = []
        self.recommendations = []
        
    def check_environment_files(self):
        """Verificar archivos de variables de entorno"""
        print('🔍 VERIFICANDO ARCHIVOS DE ENTORNO')
        print('-' * 40)
        
        # Archivos que deben existir
        required_files = ['env.example']
        # Archivos que NO deben estar en repositorio
        sensitive_files = ['.env', '.env.local', '.env.production']
        
        for file in required_files:
            if os.path.exists(file):
                print(f'✅ {file} - Presente')
            else:
                self.vulnerabilities.append(f'Falta archivo de ejemplo: {file}')
                print(f'❌ {file} - FALTANTE')
        
        for file in sensitive_files:
            if os.path.exists(file):
                self.warnings.append(f'Archivo sensible encontrado: {file}')
                print(f'⚠️ {file} - ENCONTRADO (verificar .gitignore)')
            else:
                print(f'✅ {file} - No encontrado (correcto)')
    
    def check_hardcoded_secrets(self):
        """Buscar secretos hardcodeados"""
        print('\n🔍 BUSCANDO SECRETOS HARDCODEADOS')
        print('-' * 40)
        
        patterns = [
            (r'password\s*=\s*["\'][^"\']{3,}["\']', 'Contraseña hardcodeada'),
            (r'secret\s*=\s*["\'][^"\']{10,}["\']', 'Secreto hardcodeado'),
            (r'api_key\s*=\s*["\'][^"\']{10,}["\']', 'API Key hardcodeada'),
            (r'token\s*=\s*["\'][^"\']{10,}["\']', 'Token hardcodeado')
        ]
        
        files_to_check = [
            'main.py',
            'app/config.py',
            'docker-compose.yml',
            'docker-compose.production.yml'
        ]
        
        secrets_found = 0
        for filepath in files_to_check:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern, description in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        self.vulnerabilities.append(f'{filepath}: {description}')
                        secrets_found += 1
                        print(f'❌ {filepath} - {description}')
        
        if secrets_found == 0:
            print('✅ No se encontraron secretos hardcodeados')
    
    def check_file_permissions(self):
        """Verificar permisos de archivos sensibles"""
        print('\n🔍 VERIFICANDO PERMISOS DE ARCHIVOS')
        print('-' * 40)
        
        sensitive_files = ['.env', 'env.example', 'scripts/setup_secure_environment.py']
        
        for filepath in sensitive_files:
            if os.path.exists(filepath):
                stat = os.stat(filepath)
                permissions = oct(stat.st_mode)[-3:]
                
                if filepath.endswith('.env'):
                    if permissions != '600':
                        self.warnings.append(f'{filepath}: Permisos inseguros ({permissions}), debería ser 600')
                        print(f'⚠️ {filepath} - Permisos: {permissions} (debería ser 600)')
                    else:
                        print(f'✅ {filepath} - Permisos seguros: {permissions}')
                else:
                    print(f'ℹ️ {filepath} - Permisos: {permissions}')
    
    def check_docker_security(self):
        """Verificar configuraciones de seguridad en Docker"""
        print('\n🔍 VERIFICANDO SEGURIDAD DOCKER')
        print('-' * 40)
        
        docker_files = ['docker-compose.yml', 'docker-compose.production.yml', 'docker-compose.enterprise.yml']
        
        security_issues = 0
        for filepath in docker_files:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar puertos expuestos a 0.0.0.0
                if re.search(r'0\.0\.0\.0:', content):
                    self.warnings.append(f'{filepath}: Puertos expuestos a todas las interfaces')
                    security_issues += 1
                
                # Verificar uso de :latest
                if ':latest' in content:
                    self.warnings.append(f'{filepath}: Uso de imagen :latest')
                    security_issues += 1
                
                # Verificar variables de entorno
                if re.search(r'=\s*[^$\n]{10,}', content):
                    env_vars = re.findall(r'(\w+)=([^$\n\s]{10,})', content)
                    for var, value in env_vars:
                        if any(keyword in var.lower() for keyword in ['password', 'secret', 'key']):
                            self.vulnerabilities.append(f'{filepath}: Variable {var} hardcodeada')
                            security_issues += 1
        
        if security_issues == 0:
            print('✅ Configuraciones Docker seguras')
        else:
            print(f'⚠️ {security_issues} problemas de seguridad encontrados')
    
    def check_dependencies(self):
        """Verificar dependencias conocidas con vulnerabilidades"""
        print('\n🔍 VERIFICANDO DEPENDENCIAS')
        print('-' * 40)
        
        # Verificar requirements.txt
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
            
            # Dependencias con versiones específicas conocidas por vulnerabilidades
            vulnerable_packages = {
                'flask<2.0': 'Flask versión vulnerable',
                'requests<2.25': 'Requests versión vulnerable', 
                'sqlalchemy<1.4': 'SQLAlchemy versión vulnerable'
            }
            
            for package, issue in vulnerable_packages.items():
                if package.split('<')[0] in requirements:
                    version_pattern = f"{package.split('<')[0]}==(.*)"
                    match = re.search(version_pattern, requirements)
                    if match:
                        version = match.group(1)
                        min_version = package.split('<')[1]
                        if version < min_version:
                            self.warnings.append(f'Dependencia vulnerable: {package.split("<")[0]} {version}')
            
            print('✅ Verificación de dependencias completada')
        else:
            self.warnings.append('Archivo requirements.txt no encontrado')
    
    def generate_security_report(self):
        """Generar reporte de seguridad"""
        print('\n' + '=' * 60)
        print('🔒 REPORTE DE AUDITORÍA DE SEGURIDAD')
        print('=' * 60)
        
        if self.vulnerabilities:
            print(f'\n❌ VULNERABILIDADES CRÍTICAS ({len(self.vulnerabilities)}):')
            for vuln in self.vulnerabilities:
                print(f'   • {vuln}')
        
        if self.warnings:
            print(f'\n⚠️ ADVERTENCIAS DE SEGURIDAD ({len(self.warnings)}):')
            for warning in self.warnings:
                print(f'   • {warning}')
        
        if not self.vulnerabilities and not self.warnings:
            print('\n🎉 ¡No se encontraron problemas de seguridad!')
        
        # Recomendaciones generales
        print(f'\n💡 RECOMENDACIONES DE SEGURIDAD:')
        recommendations = [
            'Usar variables de entorno para todos los secretos',
            'Implementar autenticación de dos factores',
            'Configurar HTTPS en producción',
            'Implementar rate limiting en APIs',
            'Realizar auditorías de seguridad regulares',
            'Mantener dependencias actualizadas',
            'Usar contenedores con usuarios no-root',
            'Implementar logging de seguridad'
        ]
        
        for i, rec in enumerate(recommendations, 1):
            print(f'   {i}. {rec}')
        
        # Calcular puntuación de seguridad
        total_issues = len(self.vulnerabilities) + len(self.warnings)
        if total_issues == 0:
            security_score = 'A+ (Excelente)'
        elif total_issues <= 2:
            security_score = 'A (Muy Bueno)'
        elif total_issues <= 5:
            security_score = 'B (Bueno)'
        elif total_issues <= 10:
            security_score = 'C (Regular)'
        else:
            security_score = 'D (Necesita Mejoras)'
        
        print(f'\n🎯 PUNTUACIÓN DE SEGURIDAD: {security_score}')
        print('=' * 60)
        
        return total_issues == 0

def main():
    """Función principal"""
    print('🚀 INICIANDO AUDITORÍA DE SEGURIDAD')
    print('=' * 60)
    
    auditor = SecurityAuditor()
    
    # Ejecutar todas las verificaciones
    auditor.check_environment_files()
    auditor.check_hardcoded_secrets()
    auditor.check_file_permissions()
    auditor.check_docker_security()
    auditor.check_dependencies()
    
    # Generar reporte final
    is_secure = auditor.generate_security_report()
    
    return 0 if is_secure else 1

if __name__ == '__main__':
    sys.exit(main())