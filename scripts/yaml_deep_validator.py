#!/usr/bin/env python3
"""
Validador profundo de archivos YAML
Sistema POS O'Data v2.0.0 - Análisis exhaustivo
"""

import yaml
import os
import re
import sys
from typing import Dict, List, Any, Optional

class YAMLDeepValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suggestions = []
        
    def validate_docker_compose_deep(self, filepath: str, config: Dict[str, Any]):
        """Validación profunda de Docker Compose"""
        print(f"🔍 Análisis profundo: {filepath}")
        
        # Verificar versión de Docker Compose
        version = config.get('version', '')
        if version and version < '3.7':
            self.warnings.append(f"{filepath}: Versión {version} es antigua, considere actualizar a 3.8+")
            
        services = config.get('services', {})
        
        for service_name, service_config in services.items():
            self._validate_service_config(filepath, service_name, service_config)
            
    def _validate_service_config(self, filepath: str, service_name: str, service_config: Dict[str, Any]):
        """Validar configuración individual de servicio"""
        
        # Verificar imágenes con :latest
        image = service_config.get('image', '')
        if image and ':latest' in image:
            self.warnings.append(f"{filepath}: Servicio {service_name} usa imagen :latest (no recomendado para producción)")
            
        # Verificar recursos limitados en producción
        if 'production' in filepath.lower() or 'enterprise' in filepath.lower():
            deploy = service_config.get('deploy', {})
            resources = deploy.get('resources', {})
            if not resources:
                self.suggestions.append(f"{filepath}: Considere añadir límites de recursos para {service_name} en producción")
                
        # Verificar variables de entorno sensibles
        self._check_sensitive_environment_vars(filepath, service_name, service_config)
        
        # Verificar puertos expuestos
        self._check_exposed_ports(filepath, service_name, service_config)
        
        # Verificar volúmenes de datos para bases de datos
        self._check_database_volumes(filepath, service_name, service_config)
        
        # Verificar configuraciones de restart
        restart = service_config.get('restart', '')
        if not restart and 'production' in filepath.lower():
            self.warnings.append(f"{filepath}: Servicio {service_name} sin política de reinicio en producción")
            
        # Verificar healthchecks
        if service_name.lower() in ['postgres', 'postgresql', 'redis', 'nginx', 'app'] and 'healthcheck' not in service_config:
            self.warnings.append(f"{filepath}: Servicio crítico {service_name} sin healthcheck")
            
    def _check_sensitive_environment_vars(self, filepath: str, service_name: str, service_config: Dict[str, Any]):
        """Verificar variables de entorno sensibles"""
        environment = service_config.get('environment', [])
        
        if isinstance(environment, list):
            for env_var in environment:
                if isinstance(env_var, str) and '=' in env_var:
                    var_name, var_value = env_var.split('=', 1)
                    sensitive_keywords = ['password', 'secret', 'key', 'token']
                    
                    if any(keyword in var_name.lower() for keyword in sensitive_keywords):
                        # Verificar si está usando variables de entorno
                        if not var_value.startswith('${') and var_value not in ['', 'changeme', 'password']:
                            self.errors.append(f"{filepath}: Variable sensible {var_name} hardcodeada en {service_name}")
                            
        elif isinstance(environment, dict):
            for var_name, var_value in environment.items():
                sensitive_keywords = ['password', 'secret', 'key', 'token']
                if any(keyword in var_name.lower() for keyword in sensitive_keywords):
                    if isinstance(var_value, str) and not var_value.startswith('${'):
                        if var_value not in ['', 'changeme', 'password']:
                            self.errors.append(f"{filepath}: Variable sensible {var_name} hardcodeada en {service_name}")
                            
    def _check_exposed_ports(self, filepath: str, service_name: str, service_config: Dict[str, Any]):
        """Verificar puertos expuestos"""
        ports = service_config.get('ports', [])
        
        if ports and 'production' in filepath.lower():
            for port in ports:
                if isinstance(port, str):
                    if port.startswith('0.0.0.0:') or not ':' in port:
                        self.warnings.append(f"{filepath}: Puerto {port} expuesto a todas las interfaces en {service_name}")
                        
    def _check_database_volumes(self, filepath: str, service_name: str, service_config: Dict[str, Any]):
        """Verificar volúmenes de datos para bases de datos"""
        volumes = service_config.get('volumes', [])
        
        # Excluir exporters y servicios de monitoreo
        if 'exporter' in service_name.lower() or 'monitor' in service_name.lower():
            return
            
        database_services = ['postgres', 'postgresql', 'redis', 'mongodb', 'mysql', 'mariadb']
        is_database = any(db in service_name.lower() for db in database_services) and 'exporter' not in service_name.lower()
        
        if is_database:
            has_data_volume = False
            data_paths = ['/data', '/var/lib', 'postgres_data', 'redis_data', '/var/lib/postgresql', '/var/lib/redis']
            
            for volume in volumes:
                if isinstance(volume, str):
                    if any(path in volume for path in data_paths):
                        has_data_volume = True
                        break
                        
            if not has_data_volume:
                self.errors.append(f"{filepath}: Servicio de base de datos {service_name} sin volumen persistente")
                
    def validate_prometheus_deep(self, filepath: str, config: Dict[str, Any]):
        """Validación profunda de Prometheus"""
        print(f"🔍 Análisis Prometheus: {filepath}")
        
        # Verificar configuración global
        global_config = config.get('global', {})
        scrape_interval = global_config.get('scrape_interval', '')
        
        if scrape_interval:
            if re.match(r'^[0-9]+s$', scrape_interval):
                interval_seconds = int(scrape_interval[:-1])
                if interval_seconds < 10:
                    self.warnings.append(f"{filepath}: Intervalo de scrape muy bajo ({scrape_interval}), puede causar alta carga")
                elif interval_seconds > 60:
                    self.suggestions.append(f"{filepath}: Intervalo de scrape alto ({scrape_interval}), considere reducir para mejor granularidad")
                    
        # Verificar jobs duplicados
        scrape_configs = config.get('scrape_configs', [])
        job_names = []
        
        for job in scrape_configs:
            job_name = job.get('job_name')
            if job_name:
                if job_name in job_names:
                    self.errors.append(f"{filepath}: Job duplicado: {job_name}")
                job_names.append(job_name)
                
                # Verificar targets
                static_configs = job.get('static_configs', [])
                for static_config in static_configs:
                    targets = static_config.get('targets', [])
                    for target in targets:
                        if isinstance(target, str):
                            if 'localhost' in target and 'enterprise' in filepath.lower():
                                self.warnings.append(f"{filepath}: Target localhost en {job_name} puede no funcionar en contenedores")
                                
    def validate_alertmanager_deep(self, filepath: str, config: Dict[str, Any]):
        """Validación profunda de Alertmanager"""
        print(f"🔍 Análisis Alertmanager: {filepath}")
        
        # Verificar configuración de route
        route = config.get('route', {})
        if not route:
            self.errors.append(f"{filepath}: Falta configuración de route")
            return
            
        # Verificar receivers
        receivers = config.get('receivers', [])
        if not receivers:
            self.errors.append(f"{filepath}: Falta configuración de receivers")
            return
            
        # Verificar que todos los receivers referenciados existen
        receiver_names = {receiver.get('name') for receiver in receivers if receiver.get('name')}
        
        def check_receiver_references(route_config):
            receiver = route_config.get('receiver')
            if receiver and receiver not in receiver_names:
                self.errors.append(f"{filepath}: Receiver '{receiver}' referenciado pero no definido")
                
            routes = route_config.get('routes', [])
            for sub_route in routes:
                check_receiver_references(sub_route)
                
        check_receiver_references(route)
        
        # Verificar configuraciones de email
        for receiver in receivers:
            email_configs = receiver.get('email_configs', [])
            for email_config in email_configs:
                if not email_config.get('to'):
                    self.warnings.append(f"{filepath}: Configuración de email sin destinatario en receiver '{receiver.get('name')}'")
                    
    def validate_file_deep(self, filepath: str):
        """Validar archivo específico"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                
            if config is None:
                self.warnings.append(f"{filepath}: Archivo YAML vacío")
                return
                
            # Determinar tipo de archivo y aplicar validación específica
            if 'docker-compose' in filepath:
                self.validate_docker_compose_deep(filepath, config)
            elif 'prometheus' in filepath and filepath.endswith('.yml'):
                if 'scrape_configs' in config:
                    self.validate_prometheus_deep(filepath, config)
            elif 'alertmanager' in filepath:
                self.validate_alertmanager_deep(filepath, config)
            else:
                print(f"✅ {filepath} - Validación básica completada")
                
        except yaml.YAMLError as e:
            self.errors.append(f"{filepath}: Error de sintaxis YAML: {str(e)}")
        except Exception as e:
            self.errors.append(f"{filepath}: Error al procesar: {str(e)}")
            
    def generate_fixes_script(self):
        """Generar script de correcciones automáticas"""
        if not self.errors and not self.warnings:
            return None
            
        fixes_script = []
        fixes_script.append("#!/bin/bash")
        fixes_script.append("# Script de correcciones automáticas para archivos YAML")
        fixes_script.append("# Generado automáticamente")
        fixes_script.append("")
        
        # Aquí se pueden añadir correcciones automáticas específicas
        for error in self.errors:
            if "hardcodeada" in error:
                fixes_script.append(f"# TODO: Corregir variable hardcodeada - {error}")
            elif "sin volumen persistente" in error:
                fixes_script.append(f"# TODO: Añadir volumen persistente - {error}")
                
        return "\n".join(fixes_script)
        
    def print_detailed_report(self):
        """Imprimir reporte detallado"""
        print("\n" + "="*80)
        print("📋 REPORTE DETALLADO DE VALIDACIÓN YAML")
        print("="*80)
        
        if self.errors:
            print(f"\n❌ ERRORES CRÍTICOS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
                
        if self.warnings:
            print(f"\n⚠️ ADVERTENCIAS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
                
        if self.suggestions:
            print(f"\n💡 SUGERENCIAS DE MEJORA ({len(self.suggestions)}):")
            for i, suggestion in enumerate(self.suggestions, 1):
                print(f"   {i}. {suggestion}")
                
        if not self.errors and not self.warnings and not self.suggestions:
            print("\n🎉 ¡Todas las configuraciones YAML están en excelente estado!")
            
        print(f"\n📊 RESUMEN FINAL:")
        print(f"   • Errores críticos: {len(self.errors)}")
        print(f"   • Advertencias: {len(self.warnings)}")
        print(f"   • Sugerencias: {len(self.suggestions)}")
        
        # Generar recomendaciones
        if self.errors or self.warnings:
            print(f"\n🔧 RECOMENDACIONES:")
            print(f"   1. Corregir errores críticos antes del despliegue")
            print(f"   2. Revisar advertencias para mejorar seguridad")
            print(f"   3. Implementar sugerencias para optimización")
            
        print("="*80)

def main():
    """Función principal"""
    validator = YAMLDeepValidator()
    
    # Lista de archivos YAML críticos
    yaml_files = [
        'docker-compose.yml',
        'docker-compose.production.yml',
        'docker-compose.enterprise.yml',
        'monitoring/docker-compose.yml',
        'monitoring/prometheus.yml',
        'monitoring/prometheus/prometheus.yml',
        'monitoring/alertmanager/alertmanager.yml',
        'monitoring/loki-config.yml'
    ]
    
    print("🚀 INICIANDO VALIDACIÓN PROFUNDA DE CONFIGURACIONES YAML")
    print("="*80)
    
    files_processed = 0
    for yaml_file in yaml_files:
        if os.path.exists(yaml_file):
            validator.validate_file_deep(yaml_file)
            files_processed += 1
        else:
            print(f"⚠️ {yaml_file} - Archivo no encontrado")
            
    print(f"\n📁 Archivos procesados: {files_processed}")
    
    # Mostrar reporte
    validator.print_detailed_report()
    
    # Generar script de correcciones si es necesario
    fixes_script = validator.generate_fixes_script()
    if fixes_script:
        with open('scripts/yaml_fixes.sh', 'w') as f:
            f.write(fixes_script)
        print(f"\n🔧 Script de correcciones generado: scripts/yaml_fixes.sh")
    
    # Retornar código de error si hay errores críticos
    return len(validator.errors)

if __name__ == "__main__":
    sys.exit(main())
