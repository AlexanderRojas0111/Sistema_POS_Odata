#!/usr/bin/env python3
"""
Script de validación para verificar que todas las mejoras están implementadas correctamente
"""

import os
import sys
import json
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Any

class ImprovementValidator:
    """Validador de mejoras implementadas"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            'ux_ui': {},
            'testing': {},
            'documentation': {},
            'optimization': {}
        }
    
    def validate_ux_ui_improvements(self) -> Dict[str, Any]:
        """Valida mejoras de UX/UI"""
        print("🔍 Validando mejoras de UX/UI...")
        
        results = {
            'package_json': False,
            'posbox_component': False,
            'product_scanner': False,
            'ticket_component': False,
            'navbar_component': False,
            'theme_configuration': False,
            'responsive_design': False
        }
        
        # Verificar package.json
        package_json_path = self.project_root / 'frontend' / 'package.json'
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                required_deps = [
                    '@mui/material', '@mui/icons-material', '@emotion/react',
                    'react-router-dom', 'axios', 'date-fns'
                ]
                
                missing_deps = [dep for dep in required_deps if dep not in package_data.get('dependencies', {})]
                results['package_json'] = len(missing_deps) == 0
                
                if missing_deps:
                    print(f"  ❌ Dependencias faltantes: {missing_deps}")
                else:
                    print("  ✅ package.json configurado correctamente")
                    
            except Exception as e:
                print(f"  ❌ Error leyendo package.json: {e}")
        
        # Verificar componentes mejorados
        components_to_check = [
            ('frontend/src/components/PosBox.js', 'posbox_component'),
            ('frontend/src/components/ProductScanner.js', 'product_scanner'),
            ('frontend/src/components/Ticket.js', 'ticket_component'),
            ('frontend/src/components/Navbar.js', 'navbar_component')
        ]
        
        for component_path, result_key in components_to_check:
            full_path = self.project_root / component_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar características de Material-UI
                    has_mui_imports = '@mui/material' in content or '@mui/icons-material' in content
                    has_styled_components = 'styled(' in content
                    has_responsive_design = 'sx=' in content or 'useTheme' in content
                    
                    results[result_key] = has_mui_imports and has_styled_components
                    
                    if results[result_key]:
                        print(f"  ✅ {component_path} mejorado correctamente")
                    else:
                        print(f"  ❌ {component_path} necesita mejoras")
                        
                except Exception as e:
                    print(f"  ❌ Error leyendo {component_path}: {e}")
            else:
                print(f"  ❌ {component_path} no encontrado")
        
        # Verificar configuración de tema
        app_js_path = self.project_root / 'frontend/src/App.js'
        if app_js_path.exists():
            try:
                with open(app_js_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_theme_provider = 'ThemeProvider' in content
                has_theme_config = 'createTheme' in content
                has_css_baseline = 'CssBaseline' in content
                
                results['theme_configuration'] = has_theme_provider and has_theme_config and has_css_baseline
                
                if results['theme_configuration']:
                    print("  ✅ Configuración de tema implementada")
                else:
                    print("  ❌ Configuración de tema incompleta")
                    
            except Exception as e:
                print(f"  ❌ Error verificando tema: {e}")
        
        # Verificar diseño responsive
        responsive_indicators = ['xs=', 'sm=', 'md=', 'lg=', 'xl=']
        responsive_count = 0
        
        for component_path, _ in components_to_check:
            full_path = self.project_root / component_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for indicator in responsive_indicators:
                        if indicator in content:
                            responsive_count += 1
                            break
                            
                except Exception:
                    pass
        
        results['responsive_design'] = responsive_count >= 2
        if results['responsive_design']:
            print("  ✅ Diseño responsive implementado")
        else:
            print("  ❌ Diseño responsive necesita mejoras")
        
        return results
    
    def validate_testing_improvements(self) -> Dict[str, Any]:
        """Valida mejoras de testing"""
        print("🧪 Validando mejoras de testing...")
        
        results = {
            'frontend_tests': False,
            'api_integration_tests': False,
            'performance_tests': False,
            'test_coverage': False
        }
        
        # Verificar tests de frontend
        frontend_test_path = self.project_root / 'tests' / 'test_frontend_components.py'
        if frontend_test_path.exists():
            try:
                with open(frontend_test_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_test_cases = 'class TestFrontendComponents' in content
                has_posbox_tests = 'test_posbox' in content
                has_cart_tests = 'test_cart' in content
                has_semantic_tests = 'test_semantic' in content
                
                results['frontend_tests'] = has_test_cases and has_posbox_tests and has_cart_tests
                
                if results['frontend_tests']:
                    print("  ✅ Tests de frontend implementados")
                else:
                    print("  ❌ Tests de frontend incompletos")
                    
            except Exception as e:
                print(f"  ❌ Error verificando tests de frontend: {e}")
        
        # Verificar tests de integración de API
        api_test_path = self.project_root / 'tests' / 'test_api_integration.py'
        if api_test_path.exists():
            try:
                with open(api_test_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_api_tests = 'class TestAPIIntegration' in content
                has_health_check = 'test_api_health_check' in content
                has_endpoint_tests = 'test_products_api_endpoints' in content
                has_error_handling = 'test_api_error_handling' in content
                
                results['api_integration_tests'] = has_api_tests and has_health_check and has_endpoint_tests
                
                if results['api_integration_tests']:
                    print("  ✅ Tests de integración de API implementados")
                else:
                    print("  ❌ Tests de integración de API incompletos")
                    
            except Exception as e:
                print(f"  ❌ Error verificando tests de API: {e}")
        
        # Verificar tests de rendimiento
        perf_test_path = self.project_root / 'tests' / 'test_performance.py'
        if perf_test_path.exists():
            try:
                with open(perf_test_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_perf_tests = 'class TestPerformance' in content
                has_response_time = 'test_api_response_time' in content
                has_concurrent_tests = 'test_concurrent_requests' in content
                has_memory_tests = 'test_memory_usage' in content
                
                results['performance_tests'] = has_perf_tests and has_response_time and has_concurrent_tests
                
                if results['performance_tests']:
                    print("  ✅ Tests de rendimiento implementados")
                else:
                    print("  ❌ Tests de rendimiento incompletos")
                    
            except Exception as e:
                print(f"  ❌ Error verificando tests de rendimiento: {e}")
        
        # Verificar cobertura de tests
        test_files = [
            'tests/test_frontend_components.py',
            'tests/test_api_integration.py',
            'tests/test_performance.py'
        ]
        
        existing_tests = sum(1 for test_file in test_files if (self.project_root / test_file).exists())
        results['test_coverage'] = existing_tests >= 2
        
        if results['test_coverage']:
            print("  ✅ Cobertura de tests adecuada")
        else:
            print("  ❌ Cobertura de tests insuficiente")
        
        return results
    
    def validate_documentation_improvements(self) -> Dict[str, Any]:
        """Valida mejoras de documentación"""
        print("📚 Validando mejoras de documentación...")
        
        results = {
            'user_manual': False,
            'api_documentation': False,
            'technical_docs': False,
            'code_comments': False
        }
        
        # Verificar manual de usuario
        manual_path = self.project_root / 'docs' / 'user' / 'MANUAL.md'
        if manual_path.exists():
            try:
                with open(manual_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_pos_section = 'Punto de Venta (POS)' in content
                has_inventory_section = 'Gestión de Inventario' in content
                has_search_section = 'Búsqueda Inteligente' in content
                has_troubleshooting = 'Solución de Problemas' in content
                
                results['user_manual'] = has_pos_section and has_inventory_section and has_search_section
                
                if results['user_manual']:
                    print("  ✅ Manual de usuario completo")
                else:
                    print("  ❌ Manual de usuario incompleto")
                    
            except Exception as e:
                print(f"  ❌ Error verificando manual de usuario: {e}")
        
        # Verificar documentación de API
        api_doc_path = self.project_root / 'docs' / 'technical' / 'API_DOCUMENTATION.md'
        if api_doc_path.exists():
            try:
                with open(api_doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_auth_section = 'Autenticación' in content
                has_api_v1 = 'API v1' in content
                has_api_v2 = 'API v2' in content
                has_error_codes = 'Códigos de Error' in content
                has_examples = 'Ejemplos de Uso' in content
                
                results['api_documentation'] = has_auth_section and has_api_v1 and has_api_v2 and has_error_codes
                
                if results['api_documentation']:
                    print("  ✅ Documentación de API completa")
                else:
                    print("  ❌ Documentación de API incompleta")
                    
            except Exception as e:
                print(f"  ❌ Error verificando documentación de API: {e}")
        
        # Verificar documentación técnica
        tech_docs = [
            'docs/technical/CANVAS.md'
        ]
        
        existing_tech_docs = sum(1 for doc in tech_docs if (self.project_root / doc).exists())
        results['technical_docs'] = existing_tech_docs >= 1
        
        if results['technical_docs']:
            print("  ✅ Documentación técnica disponible")
        else:
            print("  ❌ Documentación técnica faltante")
        
        # Verificar comentarios en código
        code_files = [
            'app/core/security.py',
            'app/core/cache.py',
            'frontend/src/components/PosBox.js'
        ]
        
        commented_files = 0
        for code_file in code_files:
            file_path = self.project_root / code_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar si tiene comentarios significativos
                    if '"""' in content or '#' in content:
                        commented_files += 1
                        
                except Exception:
                    pass
        
        results['code_comments'] = commented_files >= 2
        
        if results['code_comments']:
            print("  ✅ Código bien documentado")
        else:
            print("  ❌ Código necesita más comentarios")
        
        return results
    
    def validate_optimization_improvements(self) -> Dict[str, Any]:
        """Valida mejoras de optimización"""
        print("⚡ Validando mejoras de optimización...")
        
        results = {
            'security_manager': False,
            'cache_manager': False,
            'input_validation': False,
            'error_handling': False,
            'performance_optimization': False
        }
        
        # Verificar gestor de seguridad
        security_path = self.project_root / 'app' / 'core' / 'security.py'
        if security_path.exists():
            try:
                with open(security_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_security_class = 'class SecurityManager' in content
                has_input_validation = 'validate_input' in content
                has_rate_limiting = 'check_rate_limit' in content
                has_password_validation = 'validate_password' in content
                has_sql_injection_check = 'check_sql_injection' in content
                
                results['security_manager'] = has_security_class and has_input_validation and has_rate_limiting
                
                if results['security_manager']:
                    print("  ✅ Gestor de seguridad implementado")
                else:
                    print("  ❌ Gestor de seguridad incompleto")
                    
            except Exception as e:
                print(f"  ❌ Error verificando gestor de seguridad: {e}")
        
        # Verificar gestor de caché
        cache_path = self.project_root / 'app' / 'core' / 'cache.py'
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_cache_class = 'class CacheManager' in content
                has_cache_decorators = 'def cached(' in content
                has_cache_invalidation = 'invalidate_related' in content
                has_cache_stats = 'get_stats' in content
                
                results['cache_manager'] = has_cache_class and has_cache_decorators and has_cache_invalidation
                
                if results['cache_manager']:
                    print("  ✅ Gestor de caché implementado")
                else:
                    print("  ❌ Gestor de caché incompleto")
                    
            except Exception as e:
                print(f"  ❌ Error verificando gestor de caché: {e}")
        
        # Verificar validación de entrada
        results['input_validation'] = results['security_manager']  # Depende del gestor de seguridad
        
        # Verificar manejo de errores
        error_handling_indicators = [
            'try:', 'except:', 'logger.error', 'jsonify'
        ]
        
        error_handling_count = 0
        for indicator in error_handling_indicators:
            if indicator in content:
                error_handling_count += 1
        
        results['error_handling'] = error_handling_count >= 2
        
        if results['error_handling']:
            print("  ✅ Manejo de errores implementado")
        else:
            print("  ❌ Manejo de errores necesita mejoras")
        
        # Verificar optimizaciones de rendimiento
        perf_indicators = [
            'cached(', 'cache_invalidate(', 'rate_limit(',
            'get_or_set', 'optimize_cache'
        ]
        
        perf_count = 0
        for indicator in perf_indicators:
            if indicator in content:
                perf_count += 1
        
        results['performance_optimization'] = perf_count >= 2
        
        if results['performance_optimization']:
            print("  ✅ Optimizaciones de rendimiento implementadas")
        else:
            print("  ❌ Optimizaciones de rendimiento necesarias")
        
        return results
    
    def run_validation(self) -> Dict[str, Any]:
        """Ejecuta toda la validación"""
        print("🚀 Iniciando validación de mejoras implementadas...")
        print("=" * 60)
        
        # Validar cada área de mejora
        self.results['ux_ui'] = self.validate_ux_ui_improvements()
        print()
        
        self.results['testing'] = self.validate_testing_improvements()
        print()
        
        self.results['documentation'] = self.validate_documentation_improvements()
        print()
        
        self.results['optimization'] = self.validate_optimization_improvements()
        print()
        
        # Generar resumen
        self.generate_summary()
        
        return self.results
    
    def generate_summary(self):
        """Genera resumen de la validación"""
        print("=" * 60)
        print("📊 RESUMEN DE VALIDACIÓN")
        print("=" * 60)
        
        total_checks = 0
        passed_checks = 0
        
        for area, checks in self.results.items():
            print(f"\n🔹 {area.upper().replace('_', ' ')}:")
            area_passed = 0
            area_total = len(checks)
            
            for check_name, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check_name.replace('_', ' ').title()}")
                if passed:
                    area_passed += 1
            
            total_checks += area_total
            passed_checks += area_passed
            
            percentage = (area_passed / area_total) * 100 if area_total > 0 else 0
            print(f"  Progreso: {area_passed}/{area_total} ({percentage:.1f}%)")
        
        # Resumen general
        print("\n" + "=" * 60)
        overall_percentage = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        print(f"🎯 PROGRESO GENERAL: {passed_checks}/{total_checks} ({overall_percentage:.1f}%)")
        
        if overall_percentage >= 80:
            print("🎉 ¡Excelente! El sistema está listo para producción")
        elif overall_percentage >= 60:
            print("👍 Buen progreso. Algunas mejoras menores necesarias")
        else:
            print("⚠️  Se necesitan más mejoras antes de producción")
        
        print("=" * 60)
    
    def save_results(self, filename: str = 'validation_results.json'):
        """Guarda los resultados de la validación"""
        results_file = self.project_root / filename
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Resultados guardados en: {results_file}")
        except Exception as e:
            print(f"\n❌ Error guardando resultados: {e}")

def main():
    """Función principal"""
    validator = ImprovementValidator()
    results = validator.run_validation()
    validator.save_results()
    
    # Retornar código de salida basado en el progreso
    total_checks = sum(len(checks) for checks in results.values())
    passed_checks = sum(sum(checks.values()) for checks in results.values())
    
    if total_checks > 0:
        progress = passed_checks / total_checks
        if progress >= 0.8:
            sys.exit(0)  # Éxito
        elif progress >= 0.6:
            sys.exit(1)  # Advertencia
        else:
            sys.exit(2)  # Error

if __name__ == '__main__':
    main() 