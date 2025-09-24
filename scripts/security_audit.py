#!/usr/bin/env python3
"""
Script de Auditoría de Seguridad - Sistema POS O'data
====================================================

Realiza una auditoría completa de seguridad del sistema,
identificando vulnerabilidades y recomendando mejoras.

Versión: 2.0.0
Autor: Sistema POS Odata Team
"""

import os
import sys
import re
import hashlib
import secrets
from pathlib import Path
from typing import List, Dict, Any, Tuple
import subprocess
import json

# Agregar el directorio padre al path para imports
sys.path.append(str(Path(__file__).parent.parent))

class SecurityAuditor:
    """Auditor de seguridad para el sistema POS"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.issues = []
        self.recommendations = []
        self.score = 100
        
    def log_issue(self, severity: str, category: str, description: str, file_path: str = None):
        """Registra un problema de seguridad"""
        issue = {
            'severity': severity,
            'category': category,
            'description': description,
            'file': file_path,
            'impact': self._get_severity_impact(severity)
        }
        self.issues.append(issue)
        self.score -= issue['impact']
    
    def log_recommendation(self, category: str, description: str, priority: str = 'medium'):
        """Registra una recomendación de mejora"""
        self.recommendations.append({
            'category': category,
            'description': description,
            'priority': priority
        })
    
    def _get_severity_impact(self, severity: str) -> int:
        """Obtiene el impacto numérico de la severidad"""
        impacts = {
            'critical': 25,
            'high': 15,
            'medium': 10,
            'low': 5,
            'info': 2
        }
        return impacts.get(severity.lower(), 5)
    
    def check_environment_variables(self):
        """Verifica la configuración de variables de entorno"""
        print("🔍 Verificando variables de entorno...")
        
        env_example = self.project_root / 'env.example'
        env_file = self.project_root / '.env'
        
        if not env_file.exists():
            self.log_issue('medium', 'config', 
                          'Archivo .env no encontrado. Usando configuración por defecto.')
            return
        
        # Verificar claves secretas
        with open(env_file, 'r') as f:
            content = f.read()
            
            # Verificar SECRET_KEY
            if 'dev-secret-key' in content or 'change-in-production' in content:
                self.log_issue('critical', 'secrets', 
                              'SECRET_KEY usando valor por defecto. CAMBIAR INMEDIATAMENTE.')
            
            # Verificar JWT_SECRET_KEY
            if 'jwt-secret-key' in content:
                self.log_issue('critical', 'secrets', 
                              'JWT_SECRET_KEY usando valor por defecto. CAMBIAR INMEDIATAMENTE.')
            
            # Verificar contraseñas por defecto
            default_passwords = ['password', '123456', 'admin', 'postgres']
            for pwd in default_passwords:
                if pwd in content.lower():
                    self.log_issue('high', 'credentials', 
                                  f'Posible contraseña por defecto detectada: {pwd}')
    
    def check_file_permissions(self):
        """Verifica permisos de archivos sensibles"""
        print("🔍 Verificando permisos de archivos...")
        
        sensitive_files = [
            '.env',
            'instance/pos_odata_dev.db',
            'logs/app.log'
        ]
        
        for file_path in sensitive_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                # En Windows, los permisos son diferentes
                if os.name == 'nt':
                    # Verificación básica para Windows
                    if full_path.stat().st_size > 0:
                        self.log_recommendation('permissions', 
                                              f'Verificar permisos de {file_path} manualmente en Windows')
                else:
                    # Verificación para sistemas Unix
                    mode = oct(full_path.stat().st_mode)[-3:]
                    if mode != '600':
                        self.log_issue('medium', 'permissions', 
                                      f'Archivo {file_path} tiene permisos {mode}. Recomendado: 600')
    
    def check_dependencies_vulnerabilities(self):
        """Verifica vulnerabilidades en dependencias"""
        print("🔍 Verificando vulnerabilidades en dependencias...")
        
        try:
            # Intentar usar safety para verificar vulnerabilidades
            result = subprocess.run(['pip', 'show', 'safety'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log_recommendation('dependencies', 
                                      'Instalar "safety" para verificar vulnerabilidades: pip install safety')
                return
            
            # Ejecutar safety check
            result = subprocess.run(['safety', 'check'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0 and 'vulnerabilities found' in result.stdout:
                self.log_issue('high', 'dependencies', 
                              'Vulnerabilidades encontradas en dependencias. Ejecutar: safety check')
        
        except FileNotFoundError:
            self.log_recommendation('dependencies', 
                                  'Instalar herramientas de auditoría: pip install safety bandit')
    
    def check_sql_injection_patterns(self):
        """Busca patrones potenciales de inyección SQL"""
        print("🔍 Verificando patrones de inyección SQL...")
        
        dangerous_patterns = [
            r'f".*SELECT.*{.*}"',
            r'f".*INSERT.*{.*}"',
            r'f".*UPDATE.*{.*}"',
            r'f".*DELETE.*{.*}"',
            r'\.format\(.*\).*SELECT',
            r'%.*SELECT',
        ]
        
        python_files = list(self.project_root.glob('**/*.py'))
        
        for file_path in python_files:
            if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for pattern in dangerous_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            self.log_issue('high', 'sql_injection', 
                                          f'Patrón potencial de inyección SQL en {file_path}')
            except Exception:
                continue
    
    def check_hardcoded_secrets(self):
        """Busca secretos hardcodeados en el código"""
        print("🔍 Verificando secretos hardcodeados...")
        
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']{8,}["\']', 'password'),
            (r'api_key\s*=\s*["\'][^"\']{20,}["\']', 'api_key'),
            (r'secret_key\s*=\s*["\'][^"\']{20,}["\']', 'secret_key'),
            (r'token\s*=\s*["\'][^"\']{20,}["\']', 'token'),
            (r'["\'][A-Za-z0-9+/]{40,}={0,2}["\']', 'base64_token'),
        ]
        
        python_files = list(self.project_root.glob('**/*.py'))
        
        for file_path in python_files:
            if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for pattern, secret_type in secret_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            # Filtrar falsos positivos
                            for match in matches:
                                if not any(fp in match.lower() for fp in 
                                         ['example', 'test', 'dummy', 'placeholder', 'change']):
                                    self.log_issue('critical', 'hardcoded_secrets', 
                                                  f'Posible {secret_type} hardcodeado en {file_path}')
            except Exception:
                continue
    
    def check_cors_configuration(self):
        """Verifica la configuración de CORS"""
        print("🔍 Verificando configuración CORS...")
        
        config_file = self.project_root / 'app' / 'core' / 'config.py'
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                content = f.read()
                
                if "'*'" in content or '"*"' in content:
                    self.log_issue('high', 'cors', 
                                  'CORS configurado con wildcard (*). Especificar dominios exactos.')
                
                if 'CORS_ORIGINS' not in content:
                    self.log_issue('medium', 'cors', 
                                  'Configuración CORS no encontrada en config.py')
    
    def check_rate_limiting(self):
        """Verifica la configuración de rate limiting"""
        print("🔍 Verificando configuración de rate limiting...")
        
        init_file = self.project_root / 'app' / '__init__.py'
        
        if init_file.exists():
            with open(init_file, 'r') as f:
                content = f.read()
                
                if 'RATELIMIT_ENABLED = False' in content:
                    self.log_issue('medium', 'rate_limiting', 
                                  'Rate limiting deshabilitado en desarrollo. Habilitar para producción.')
                
                if 'Flask-Limiter' not in content and 'Limiter' not in content:
                    self.log_issue('high', 'rate_limiting', 
                                  'Rate limiting no configurado. Implementar para prevenir ataques.')
    
    def generate_secure_keys(self) -> Dict[str, str]:
        """Genera claves secretas seguras"""
        return {
            'SECRET_KEY': secrets.token_urlsafe(64),
            'JWT_SECRET_KEY': secrets.token_urlsafe(64),
            'CSRF_SECRET_KEY': secrets.token_urlsafe(32)
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Genera el reporte final de auditoría"""
        
        # Calcular estadísticas
        severity_counts = {}
        category_counts = {}
        
        for issue in self.issues:
            severity = issue['severity']
            category = issue['category']
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Determinar nivel de seguridad
        if self.score >= 90:
            security_level = "EXCELENTE"
            color = "🟢"
        elif self.score >= 75:
            security_level = "BUENO"
            color = "🟡"
        elif self.score >= 50:
            security_level = "REGULAR"
            color = "🟠"
        else:
            security_level = "CRÍTICO"
            color = "🔴"
        
        return {
            'score': max(0, self.score),
            'security_level': security_level,
            'color': color,
            'total_issues': len(self.issues),
            'total_recommendations': len(self.recommendations),
            'severity_breakdown': severity_counts,
            'category_breakdown': category_counts,
            'issues': self.issues,
            'recommendations': self.recommendations,
            'secure_keys': self.generate_secure_keys()
        }
    
    def run_full_audit(self) -> Dict[str, Any]:
        """Ejecuta la auditoría completa"""
        print("🔐 INICIANDO AUDITORÍA DE SEGURIDAD")
        print("=" * 50)
        
        # Ejecutar todas las verificaciones
        self.check_environment_variables()
        self.check_file_permissions()
        self.check_dependencies_vulnerabilities()
        self.check_sql_injection_patterns()
        self.check_hardcoded_secrets()
        self.check_cors_configuration()
        self.check_rate_limiting()
        
        return self.generate_report()

def print_report(report: Dict[str, Any]):
    """Imprime el reporte de auditoría de forma legible"""
    
    print("\n" + "=" * 60)
    print(f"🔐 REPORTE DE AUDITORÍA DE SEGURIDAD")
    print("=" * 60)
    
    print(f"\n📊 PUNTUACIÓN GENERAL: {report['score']}/100 {report['color']}")
    print(f"🛡️  NIVEL DE SEGURIDAD: {report['security_level']}")
    
    print(f"\n📈 RESUMEN:")
    print(f"   • Total de problemas: {report['total_issues']}")
    print(f"   • Total de recomendaciones: {report['total_recommendations']}")
    
    if report['severity_breakdown']:
        print(f"\n⚠️  PROBLEMAS POR SEVERIDAD:")
        for severity, count in report['severity_breakdown'].items():
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢', 'info': '🔵'}.get(severity, '⚪')
            print(f"   {emoji} {severity.upper()}: {count}")
    
    if report['category_breakdown']:
        print(f"\n📋 PROBLEMAS POR CATEGORÍA:")
        for category, count in report['category_breakdown'].items():
            print(f"   • {category.replace('_', ' ').title()}: {count}")
    
    if report['issues']:
        print(f"\n🚨 PROBLEMAS DETECTADOS:")
        for i, issue in enumerate(report['issues'], 1):
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(issue['severity'], '⚪')
            print(f"\n   {i}. {emoji} [{issue['severity'].upper()}] {issue['category'].replace('_', ' ').title()}")
            print(f"      {issue['description']}")
            if issue['file']:
                print(f"      📁 Archivo: {issue['file']}")
    
    if report['recommendations']:
        print(f"\n💡 RECOMENDACIONES:")
        for i, rec in enumerate(report['recommendations'], 1):
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rec['priority'], '🟡')
            print(f"\n   {i}. {priority_emoji} [{rec['priority'].upper()}] {rec['category'].replace('_', ' ').title()}")
            print(f"      {rec['description']}")
    
    print(f"\n🔑 CLAVES SECRETAS SEGURAS GENERADAS:")
    print("   (Usar estas claves en tu archivo .env)")
    print("   " + "-" * 50)
    for key, value in report['secure_keys'].items():
        print(f"   {key}={value}")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    if report['score'] < 50:
        print("   1. 🚨 URGENTE: Solucionar problemas críticos y de alta severidad")
        print("   2. 🔧 Implementar las recomendaciones de alta prioridad")
        print("   3. 🔄 Ejecutar nueva auditoría después de los cambios")
    elif report['score'] < 75:
        print("   1. 🔧 Implementar recomendaciones de seguridad")
        print("   2. 🔍 Revisar configuraciones de producción")
        print("   3. 📋 Establecer proceso de auditoría regular")
    else:
        print("   1. ✅ Mantener buenas prácticas de seguridad")
        print("   2. 🔄 Auditorías regulares (mensual)")
        print("   3. 📚 Mantenerse actualizado con mejores prácticas")
    
    print("\n" + "=" * 60)

def main():
    """Función principal"""
    auditor = SecurityAuditor()
    report = auditor.run_full_audit()
    print_report(report)
    
    # Guardar reporte en archivo JSON
    report_file = auditor.project_root / 'security_audit_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n💾 Reporte guardado en: {report_file}")
    
    # Código de salida basado en la puntuación
    if report['score'] < 50:
        sys.exit(2)  # Crítico
    elif report['score'] < 75:
        sys.exit(1)  # Advertencia
    else:
        sys.exit(0)  # OK

if __name__ == "__main__":
    main()
