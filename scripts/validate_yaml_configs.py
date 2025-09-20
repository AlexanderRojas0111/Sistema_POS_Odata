#!/usr/bin/env python3
"""
Script de validación avanzada para archivos YAML
Sistema POS O'Data v2.0.0
"""

import yaml
import sys
import os
from typing import Dict, List, Any
import re

class YAMLConfigValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_docker_compose(self, filepath: str, config: Dict[str, Any]) -> bool:
        """Validar configuración de Docker Compose"""
        print(f"🔍 Validando configuración Docker Compose: {filepath}")
        
        # Verificar versión
        if 'version' not in config:
            self.errors.append(f"{filepath}: Falta especificar la versión de Docker Compose")
            return False
            
        version = config['version']
        if not re.match(r'^3\.[0-9]+$', version):
            self.warnings.append(f"{filepath}: Versión {version} puede no ser compatible con todas las características")
            
        # Verificar servicios
        if 'services' not in config:
            self.errors.append(f"{filepath}: No se encontraron servicios definidos")
            return False
            
        services = config['services']
        for service_name, service_config in services.items():
            # Verificar imagen o build
            if 'image' not in service_config and 'build' not in service_config:
                self.errors.append(f"{filepath}: Servicio '{service_name}' debe tener 'image' o 'build'")
                
            # Verificar healthchecks para servicios críticos
            critical_services = ['postgres', 'redis', 'app', 'pos-app', 'sabrositas-app']
            if any(critical in service_name.lower() for critical in critical_services):
                if 'healthcheck' not in service_config:
                    self.warnings.append(f"{filepath}: Servicio crítico '{service_name}' debería tener healthcheck")
                    
            # Verificar restart policy
            if 'restart' not in service_config:
                self.warnings.append(f"{filepath}: Servicio '{service_name}' debería tener política de reinicio")
                
        return True
        
    def validate_prometheus_config(self, filepath: str, config: Dict[str, Any]) -> bool:
        """Validar configuración de Prometheus"""
        print(f"🔍 Validando configuración Prometheus: {filepath}")
        
        # Verificar configuración global
        if 'global' not in config:
            self.warnings.append(f"{filepath}: Falta configuración global")
            
        # Verificar scrape_configs
        if 'scrape_configs' not in config:
            self.errors.append(f"{filepath}: Falta configuración de scrape_configs")
            return False
            
        scrape_configs = config['scrape_configs']
        job_names = set()
        
        for job in scrape_configs:
            if 'job_name' not in job:
                self.errors.append(f"{filepath}: Job sin nombre definido")
                continue
                
            job_name = job['job_name']
            if job_name in job_names:
                self.errors.append(f"{filepath}: Job name duplicado: {job_name}")
            job_names.add(job_name)
            
            if 'static_configs' not in job and 'consul_configs' not in job:
                self.warnings.append(f"{filepath}: Job '{job_name}' sin configuración de targets")
                
        return True
        
    def validate_alertmanager_config(self, filepath: str, config: Dict[str, Any]) -> bool:
        """Validar configuración de Alertmanager"""
        print(f"🔍 Validando configuración Alertmanager: {filepath}")
        
        # Verificar route
        if 'route' not in config:
            self.errors.append(f"{filepath}: Falta configuración de route")
            return False
            
        # Verificar receivers
        if 'receivers' not in config:
            self.errors.append(f"{filepath}: Falta configuración de receivers")
            return False
            
        receivers = config['receivers']
        receiver_names = set()
        
        for receiver in receivers:
            if 'name' not in receiver:
                self.errors.append(f"{filepath}: Receiver sin nombre")
                continue
                
            receiver_name = receiver['name']
            if receiver_name in receiver_names:
                self.errors.append(f"{filepath}: Receiver name duplicado: {receiver_name}")
            receiver_names.add(receiver_name)
            
        return True
        
    def validate_file(self, filepath: str) -> bool:
        """Validar un archivo YAML específico"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                
            if config is None:
                self.warnings.append(f"{filepath}: Archivo YAML vacío")
                return True
                
            # Validaciones específicas por tipo de archivo
            if 'docker-compose' in filepath:
                return self.validate_docker_compose(filepath, config)
            elif 'prometheus' in filepath and 'scrape_configs' in config:
                return self.validate_prometheus_config(filepath, config)
            elif 'alertmanager' in filepath:
                return self.validate_alertmanager_config(filepath, config)
            else:
                print(f"✅ {filepath} - Sintaxis YAML válida")
                return True
                
        except yaml.YAMLError as e:
            self.errors.append(f"{filepath}: Error de sintaxis YAML: {e}")
            return False
        except Exception as e:
            self.errors.append(f"{filepath}: Error al procesar archivo: {e}")
            return False
            
    def validate_all_files(self, yaml_files: List[str]) -> bool:
        """Validar todos los archivos YAML"""
        success = True
        
        for yaml_file in yaml_files:
            if os.path.exists(yaml_file):
                if not self.validate_file(yaml_file):
                    success = False
            else:
                self.warnings.append(f"{yaml_file}: Archivo no encontrado")
                
        return success
        
    def print_report(self):
        """Imprimir reporte de validación"""
        print("\n" + "="*60)
        print("📋 REPORTE DE VALIDACIÓN YAML")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERRORES ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
                
        if self.warnings:
            print(f"\n⚠️ ADVERTENCIAS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
                
        if not self.errors and not self.warnings:
            print("\n🎉 ¡Todos los archivos YAML están correctamente configurados!")
            
        print(f"\n📊 RESUMEN:")
        print(f"   • Errores: {len(self.errors)}")
        print(f"   • Advertencias: {len(self.warnings)}")
        print("="*60)

def main():
    """Función principal"""
    validator = YAMLConfigValidator()
    
    yaml_files = [
        'docker-compose.yml',
        'docker-compose.production.yml', 
        'docker-compose.enterprise.yml',
        '.pre-commit-config.yaml',
        'monitoring/docker-compose.yml',
        'monitoring/prometheus.yml',
        'monitoring/prometheus/prometheus.yml',
        'monitoring/loki-config.yml',
        'monitoring/alertmanager/alertmanager.yml',
        'monitoring/blackbox/blackbox.yml',
        'monitoring/prometheus/rules/alerts.yml',
        'monitoring/grafana/datasources/prometheus.yml'
    ]
    
    print("🚀 Iniciando validación avanzada de archivos YAML...")
    print("="*60)
    
    success = validator.validate_all_files(yaml_files)
    validator.print_report()
    
    return 0 if success and not validator.errors else 1

if __name__ == "__main__":
    sys.exit(main())
