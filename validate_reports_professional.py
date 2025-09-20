"""
Validación Profesional del Módulo de Reportes
=============================================
Script completo para validar todos los aspectos del sistema de reportes
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

class ReportsValidator:
    """Validador profesional del módulo de reportes"""
    
    def __init__(self):
        self.results = {
            'server_health': False,
            'endpoints_available': [],
            'endpoints_failed': [],
            'data_quality': {},
            'performance': {}
        }
    
    def validate_server_health(self):
        """Validar salud del servidor"""
        print("🏥 VALIDANDO SALUD DEL SERVIDOR")
        print("-" * 50)
        
        try:
            response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Servidor funcionando correctamente")
                print(f"   Status: {data.get('status')}")
                print(f"   Database: {data.get('database')}")
                print(f"   Version: {data.get('version')}")
                self.results['server_health'] = True
                return True
            else:
                print(f"❌ Servidor con problemas: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Servidor no responde: {e}")
            return False
    
    def validate_reports_endpoints(self):
        """Validar todos los endpoints de reportes"""
        print(f"\n📊 VALIDANDO ENDPOINTS DE REPORTES")
        print("-" * 50)
        
        # Endpoints a validar
        endpoints = [
            # Endpoints de prueba (sin auth)
            {'url': '/api/v1/reports/test/health', 'name': 'Health Check', 'auth': False},
            {'url': '/api/v1/reports/test/sales', 'name': 'Ventas Test', 'auth': False},
            {'url': '/api/v1/reports/test/inventory', 'name': 'Inventario Test', 'auth': False},
            {'url': '/api/v1/reports/test/dashboard', 'name': 'Dashboard Test', 'auth': False},
            
            # Endpoints principales (públicos por ahora)
            {'url': '/api/v1/reports/sales', 'name': 'Ventas Principal', 'auth': False},
            {'url': '/api/v1/reports/inventory', 'name': 'Inventario Principal', 'auth': False},
            {'url': '/api/v1/reports/dashboard', 'name': 'Dashboard Principal', 'auth': False},
            {'url': '/api/v1/reports/products/performance', 'name': 'Rendimiento Productos', 'auth': False},
            {'url': '/api/v1/reports/export/sales/csv', 'name': 'Exportar CSV', 'auth': False}
        ]
        
        for endpoint in endpoints:
            print(f"\n🧪 Validando: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            
            try:
                start_time = datetime.now()
                response = requests.get(f"{BASE_URL}{endpoint['url']}", timeout=10)
                end_time = datetime.now()
                
                response_time = (end_time - start_time).total_seconds()
                
                print(f"   📊 Status: {response.status_code}")
                print(f"   ⏱️ Tiempo: {response_time:.2f}s")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get('success'):
                            print(f"   ✅ FUNCIONANDO - {data.get('message', 'OK')}")
                            
                            # Validar calidad de datos
                            if 'data' in data:
                                self.validate_data_quality(endpoint['name'], data['data'])
                            
                            self.results['endpoints_available'].append(endpoint['name'])
                            self.results['performance'][endpoint['name']] = response_time
                        else:
                            print(f"   ⚠️ Respuesta con error: {data.get('error')}")
                            self.results['endpoints_failed'].append(endpoint['name'])
                    except json.JSONDecodeError:
                        print(f"   ❌ Respuesta no es JSON válido")
                        self.results['endpoints_failed'].append(endpoint['name'])
                        
                elif response.status_code == 401:
                    print(f"   🔐 Requiere autenticación (esperado)")
                    self.results['endpoints_available'].append(f"{endpoint['name']} (Auth Required)")
                    
                elif response.status_code == 404:
                    print(f"   ❌ Endpoint no encontrado")
                    self.results['endpoints_failed'].append(endpoint['name'])
                    
                else:
                    print(f"   ❌ Error {response.status_code}")
                    self.results['endpoints_failed'].append(endpoint['name'])
                    
            except Exception as e:
                print(f"   💥 Error de conexión: {e}")
                self.results['endpoints_failed'].append(endpoint['name'])
    
    def validate_data_quality(self, endpoint_name, data):
        """Validar calidad de los datos retornados"""
        quality_score = 0
        issues = []
        
        # Verificar estructura básica
        if isinstance(data, dict):
            quality_score += 25
            
            # Verificar summary
            if 'summary' in data:
                quality_score += 25
                summary = data['summary']
                
                # Verificar métricas numéricas
                numeric_fields = ['total_sales', 'total_revenue', 'total_products']
                for field in numeric_fields:
                    if field in summary and isinstance(summary[field], (int, float)):
                        quality_score += 10
                    elif field in summary:
                        issues.append(f"Campo {field} no es numérico")
            
            # Verificar datos de lista
            list_fields = ['sales', 'products', 'categories']
            for field in list_fields:
                if field in data and isinstance(data[field], (list, dict)):
                    quality_score += 10
        else:
            issues.append("Estructura de datos no es un diccionario")
        
        self.results['data_quality'][endpoint_name] = {
            'score': min(quality_score, 100),
            'issues': issues
        }
        
        if quality_score >= 80:
            print(f"   📈 Calidad de datos: EXCELENTE ({quality_score}%)")
        elif quality_score >= 60:
            print(f"   📊 Calidad de datos: BUENA ({quality_score}%)")
        else:
            print(f"   📉 Calidad de datos: NECESITA MEJORA ({quality_score}%)")
            if issues:
                print(f"   ⚠️ Problemas: {', '.join(issues)}")
    
    def generate_report(self):
        """Generar reporte final de validación"""
        print(f"\n🎯 REPORTE FINAL DE VALIDACIÓN")
        print("=" * 60)
        
        # Estado general
        total_endpoints = len(self.results['endpoints_available']) + len(self.results['endpoints_failed'])
        success_rate = len(self.results['endpoints_available']) / total_endpoints * 100 if total_endpoints > 0 else 0
        
        print(f"📊 RESUMEN EJECUTIVO:")
        print(f"   - Salud del servidor: {'✅ OK' if self.results['server_health'] else '❌ FALLO'}")
        print(f"   - Endpoints funcionando: {len(self.results['endpoints_available'])}")
        print(f"   - Endpoints con problemas: {len(self.results['endpoints_failed'])}")
        print(f"   - Tasa de éxito: {success_rate:.1f}%")
        
        if self.results['endpoints_available']:
            print(f"\n✅ ENDPOINTS FUNCIONANDO:")
            for endpoint in self.results['endpoints_available']:
                perf = self.results['performance'].get(endpoint, 0)
                print(f"   - {endpoint} ({perf:.2f}s)")
        
        if self.results['endpoints_failed']:
            print(f"\n❌ ENDPOINTS CON PROBLEMAS:")
            for endpoint in self.results['endpoints_failed']:
                print(f"   - {endpoint}")
        
        # Calidad de datos
        if self.results['data_quality']:
            print(f"\n📈 CALIDAD DE DATOS:")
            for endpoint, quality in self.results['data_quality'].items():
                score = quality['score']
                status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
                print(f"   {status} {endpoint}: {score}%")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        
        if success_rate >= 90:
            print("   🎉 Sistema en excelente estado")
            print("   🚀 Listo para producción")
        elif success_rate >= 70:
            print("   ⚠️ Sistema funcional con mejoras menores pendientes")
            print("   🔧 Revisar endpoints fallidos")
        else:
            print("   ❌ Sistema necesita atención inmediata")
            print("   🚨 Revisar configuración y dependencias")
        
        return success_rate >= 70

def main():
    """Función principal de validación"""
    print("🎯 VALIDACIÓN PROFESIONAL DEL MÓDULO DE REPORTES")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Sistema: Sistema POS Sabrositas v2.0.0")
    
    validator = ReportsValidator()
    
    # Ejecutar validaciones
    server_ok = validator.validate_server_health()
    
    if server_ok:
        validator.validate_reports_endpoints()
        system_ok = validator.generate_report()
        
        if system_ok:
            print(f"\n🎊 VALIDACIÓN EXITOSA - SISTEMA LISTO PARA USO")
            return True
        else:
            print(f"\n⚠️ VALIDACIÓN CON PROBLEMAS - REQUIERE ATENCIÓN")
            return False
    else:
        print(f"\n❌ SERVIDOR NO DISPONIBLE - VERIFICAR CONFIGURACIÓN")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
