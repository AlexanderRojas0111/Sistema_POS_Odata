#!/usr/bin/env python3
"""
Tests de Seguridad Avanzados - O'Data v2.0.0
============================================

Script para tests de SQL Injection, XSS, CSRF, Rate Limiting, etc.

Autor: Sistema POS Odata
Versión: 2.0.0
"""

import os
import sys
import time
import json
import requests
import argparse
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any
import logging
import re


@dataclass
class SecurityTestResult:
    """Resultado de un test de seguridad"""
    test_name: str
    endpoint: str
    payload: str
    success: bool
    vulnerability_found: bool
    severity: str
    description: str
    response_code: int = None
    response_time: float = None
    details: str = None


class SecurityTester:
    """Clase para tests de seguridad"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results: List[SecurityTestResult] = []
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Token de autenticación (se obtendrá dinámicamente)
        self.auth_token = None
    
    def authenticate(self, username: str = "admin", password: str = "admin123") -> bool:
        """Autenticarse en el sistema"""
        try:
            auth_data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=auth_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                self.logger.info("✅ Autenticación exitosa")
                return True
            else:
                self.logger.warning("⚠️  No se pudo autenticar, continuando sin token")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error en autenticación: {e}")
            return False
    
    def test_sql_injection(self) -> List[SecurityTestResult]:
        """Test de SQL Injection"""
        self.logger.info("🛡️  Iniciando tests de SQL Injection")
        
        # Payloads comunes de SQL Injection
        sql_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users;--",
            "' OR '1'='1' /*",
            "admin'--",
            "admin' #",
            "admin'/*",
            "' or 1=1#",
            "' or 1=1--",
            "' or 1=1/*",
            "') or '1'='1--",
            "') or ('1'='1--"
        ]
        
        # Endpoints vulnerables potenciales
        test_endpoints = [
            ('/api/v1/search/products', 'GET', 'q'),
            ('/api/v1/search/sales', 'GET', 'user_id'),
            ('/api/v1/search/users', 'GET', 'q'),
            ('/api/v1/auth/login', 'POST', 'username')
        ]
        
        results = []
        
        for endpoint, method, param in test_endpoints:
            self.logger.info(f"🎯 Testing SQL Injection en: {endpoint}")
            
            for payload in sql_payloads:
                start_time = time.time()
                vulnerability_found = False
                
                try:
                    if method == 'GET':
                        response = self.session.get(
                            f"{self.base_url}{endpoint}",
                            params={param: payload},
                            timeout=10
                        )
                    else:  # POST
                        data = {param: payload}
                        response = self.session.post(
                            f"{self.base_url}{endpoint}",
                            json=data,
                            headers={'Content-Type': 'application/json'},
                            timeout=10
                        )
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    # Indicadores de SQL Injection
                    sql_indicators = [
                        "sql syntax",
                        "mysql_fetch",
                        "ora-",
                        "postgresql",
                        "sqlite",
                        "syntax error",
                        "quoted string not properly terminated",
                        "unclosed quotation mark"
                    ]
                    
                    response_text = response.text.lower()
                    for indicator in sql_indicators:
                        if indicator in response_text:
                            vulnerability_found = True
                            break
                    
                    # También verificar códigos de respuesta anómalos
                    if response.status_code == 500 and "sql" in response_text:
                        vulnerability_found = True
                    
                    severity = "HIGH" if vulnerability_found else "LOW"
                    
                    results.append(SecurityTestResult(
                        test_name="SQL Injection",
                        endpoint=endpoint,
                        payload=payload,
                        success=True,
                        vulnerability_found=vulnerability_found,
                        severity=severity,
                        description=f"SQL Injection test con payload: {payload[:50]}...",
                        response_code=response.status_code,
                        response_time=response_time,
                        details=response_text[:200] if vulnerability_found else None
                    ))
                    
                except Exception as e:
                    results.append(SecurityTestResult(
                        test_name="SQL Injection",
                        endpoint=endpoint,
                        payload=payload,
                        success=False,
                        vulnerability_found=False,
                        severity="UNKNOWN",
                        description=f"Error en test: {str(e)}",
                        details=str(e)
                    ))
        
        self.logger.info(f"✅ Tests de SQL Injection completados: {len(results)} tests")
        return results
    
    def test_xss(self) -> List[SecurityTestResult]:
        """Test de Cross-Site Scripting (XSS)"""
        self.logger.info("🛡️  Iniciando tests de XSS")
        
        # Payloads comunes de XSS
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=\"javascript:alert('XSS')\"></iframe>",
            "<body onload=alert('XSS')>",
            "<div onclick=alert('XSS')>Click me</div>",
            "';alert('XSS');//",
            "\"><script>alert('XSS')</script>",
            "<script>document.cookie='XSS'</script>"
        ]
        
        # Endpoints que podrían reflejar input
        test_endpoints = [
            ('/api/v1/search/products', 'GET', 'q'),
            ('/api/v1/search/sales', 'GET', 'q'),
            ('/api/v1/search/users', 'GET', 'q')
        ]
        
        results = []
        
        for endpoint, method, param in test_endpoints:
            self.logger.info(f"🎯 Testing XSS en: {endpoint}")
            
            for payload in xss_payloads:
                start_time = time.time()
                vulnerability_found = False
                
                try:
                    if method == 'GET':
                        response = self.session.get(
                            f"{self.base_url}{endpoint}",
                            params={param: payload},
                            timeout=10
                        )
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    # Verificar si el payload se refleja sin escapar
                    if payload in response.text:
                        vulnerability_found = True
                    
                    # Verificar headers de seguridad
                    security_headers = [
                        'X-Content-Type-Options',
                        'X-Frame-Options',
                        'X-XSS-Protection',
                        'Content-Security-Policy'
                    ]
                    
                    missing_headers = [
                        header for header in security_headers 
                        if header not in response.headers
                    ]
                    
                    severity = "HIGH" if vulnerability_found else "MEDIUM" if missing_headers else "LOW"
                    
                    results.append(SecurityTestResult(
                        test_name="XSS",
                        endpoint=endpoint,
                        payload=payload,
                        success=True,
                        vulnerability_found=vulnerability_found,
                        severity=severity,
                        description=f"XSS test con payload: {payload[:50]}...",
                        response_code=response.status_code,
                        response_time=response_time,
                        details=f"Headers faltantes: {missing_headers}" if missing_headers else None
                    ))
                    
                except Exception as e:
                    results.append(SecurityTestResult(
                        test_name="XSS",
                        endpoint=endpoint,
                        payload=payload,
                        success=False,
                        vulnerability_found=False,
                        severity="UNKNOWN",
                        description=f"Error en test: {str(e)}",
                        details=str(e)
                    ))
        
        self.logger.info(f"✅ Tests de XSS completados: {len(results)} tests")
        return results
    
    def test_csrf(self) -> List[SecurityTestResult]:
        """Test de Cross-Site Request Forgery (CSRF)"""
        self.logger.info("🛡️  Iniciando tests de CSRF")
        
        # Endpoints que modifican datos
        test_endpoints = [
            '/api/v1/auth/register',
            '/api/v1/auth/login'
        ]
        
        results = []
        
        for endpoint in test_endpoints:
            self.logger.info(f"🎯 Testing CSRF en: {endpoint}")
            
            start_time = time.time()
            
            try:
                # Test sin CSRF token
                test_data = {
                    "username": "testuser",
                    "password": "testpass",
                    "email": "test@example.com"
                }
                
                response = self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=test_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                response_time = (time.time() - start_time) * 1000
                
                # Verificar si hay protección CSRF
                csrf_protected = False
                
                # Verificar headers de CSRF
                if 'X-CSRF-Token' in response.headers:
                    csrf_protected = True
                
                # Verificar cookies SameSite
                for cookie in response.cookies:
                    if hasattr(cookie, 'same_site') and cookie.same_site:
                        csrf_protected = True
                
                vulnerability_found = not csrf_protected
                severity = "MEDIUM" if vulnerability_found else "LOW"
                
                results.append(SecurityTestResult(
                    test_name="CSRF",
                    endpoint=endpoint,
                    payload="No CSRF token",
                    success=True,
                    vulnerability_found=vulnerability_found,
                    severity=severity,
                    description="Test de protección CSRF",
                    response_code=response.status_code,
                    response_time=response_time,
                    details="Sin protección CSRF detectada" if vulnerability_found else "Protección CSRF presente"
                ))
                
            except Exception as e:
                results.append(SecurityTestResult(
                    test_name="CSRF",
                    endpoint=endpoint,
                    payload="No CSRF token",
                    success=False,
                    vulnerability_found=False,
                    severity="UNKNOWN",
                    description=f"Error en test: {str(e)}",
                    details=str(e)
                ))
        
        self.logger.info(f"✅ Tests de CSRF completados: {len(results)} tests")
        return results
    
    def test_rate_limiting(self) -> List[SecurityTestResult]:
        """Test de Rate Limiting"""
        self.logger.info("🛡️  Iniciando tests de Rate Limiting")
        
        # Endpoints para testear rate limiting
        test_endpoints = [
            '/api/v1/auth/login',
            '/api/v1/stats/system',
            '/api/v1/search/products'
        ]
        
        results = []
        
        for endpoint in test_endpoints:
            self.logger.info(f"🎯 Testing Rate Limiting en: {endpoint}")
            
            # Hacer muchos requests rápidamente
            rate_limit_hit = False
            requests_made = 0
            
            start_time = time.time()
            
            for i in range(200):  # Intentar 200 requests
                try:
                    if endpoint == '/api/v1/auth/login':
                        response = self.session.post(
                            f"{self.base_url}{endpoint}",
                            json={"username": "test", "password": "test"},
                            headers={'Content-Type': 'application/json'},
                            timeout=5
                        )
                    else:
                        response = self.session.get(
                            f"{self.base_url}{endpoint}",
                            timeout=5
                        )
                    
                    requests_made += 1
                    
                    # Verificar si se activó rate limiting
                    if response.status_code == 429:
                        rate_limit_hit = True
                        break
                    
                    time.sleep(0.01)  # Pequeña pausa
                    
                except Exception as e:
                    break
            
            total_time = time.time() - start_time
            
            vulnerability_found = not rate_limit_hit
            severity = "MEDIUM" if vulnerability_found else "LOW"
            
            results.append(SecurityTestResult(
                test_name="Rate Limiting",
                endpoint=endpoint,
                payload=f"{requests_made} requests in {total_time:.2f}s",
                success=True,
                vulnerability_found=vulnerability_found,
                severity=severity,
                description="Test de rate limiting",
                response_code=429 if rate_limit_hit else 200,
                response_time=total_time * 1000,
                details=f"Rate limit {'activado' if rate_limit_hit else 'NO activado'} después de {requests_made} requests"
            ))
        
        self.logger.info(f"✅ Tests de Rate Limiting completados: {len(results)} tests")
        return results
    
    def test_authentication(self) -> List[SecurityTestResult]:
        """Test de vulnerabilidades de autenticación"""
        self.logger.info("🛡️  Iniciando tests de autenticación")
        
        results = []
        
        # Test 1: Bypass de autenticación
        auth_bypass_payloads = [
            {"username": "admin", "password": ""},
            {"username": "", "password": "admin"},
            {"username": "admin' OR '1'='1", "password": "anything"},
            {"username": "admin", "password": "admin' OR '1'='1"}
        ]
        
        for payload in auth_bypass_payloads:
            start_time = time.time()
            
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                response_time = (time.time() - start_time) * 1000
                
                # Si se autentica con credenciales inválidas, es una vulnerabilidad
                vulnerability_found = response.status_code == 200
                severity = "HIGH" if vulnerability_found else "LOW"
                
                results.append(SecurityTestResult(
                    test_name="Authentication Bypass",
                    endpoint="/api/v1/auth/login",
                    payload=str(payload),
                    success=True,
                    vulnerability_found=vulnerability_found,
                    severity=severity,
                    description="Test de bypass de autenticación",
                    response_code=response.status_code,
                    response_time=response_time
                ))
                
            except Exception as e:
                results.append(SecurityTestResult(
                    test_name="Authentication Bypass",
                    endpoint="/api/v1/auth/login",
                    payload=str(payload),
                    success=False,
                    vulnerability_found=False,
                    severity="UNKNOWN",
                    description=f"Error en test: {str(e)}",
                    details=str(e)
                ))
        
        # Test 2: JWT Token manipulation
        if self.auth_token:
            # Intentar manipular el token JWT
            manipulated_tokens = [
                self.auth_token[:-5] + "XXXXX",  # Cambiar firma
                "Bearer invalid_token",
                "Bearer " + self.auth_token.replace('.', 'X'),  # Corromper token
                ""  # Token vacío
            ]
            
            for token in manipulated_tokens:
                start_time = time.time()
                
                try:
                    headers = {'Authorization': token} if token else {}
                    response = self.session.get(
                        f"{self.base_url}/api/v1/auth/me",
                        headers=headers,
                        timeout=10
                    )
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    # Si acepta tokens inválidos, es una vulnerabilidad
                    vulnerability_found = response.status_code == 200
                    severity = "HIGH" if vulnerability_found else "LOW"
                    
                    results.append(SecurityTestResult(
                        test_name="JWT Token Manipulation",
                        endpoint="/api/v1/auth/me",
                        payload=token[:50] + "..." if len(token) > 50 else token,
                        success=True,
                        vulnerability_found=vulnerability_found,
                        severity=severity,
                        description="Test de manipulación de token JWT",
                        response_code=response.status_code,
                        response_time=response_time
                    ))
                    
                except Exception as e:
                    results.append(SecurityTestResult(
                        test_name="JWT Token Manipulation",
                        endpoint="/api/v1/auth/me",
                        payload=token,
                        success=False,
                        vulnerability_found=False,
                        severity="UNKNOWN",
                        description=f"Error en test: {str(e)}",
                        details=str(e)
                    ))
        
        # Test 3: Session fixation
        try:
            # Intentar fijar una sesión
            custom_session_id = "FIXED_SESSION_12345"
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": "admin", "password": "admin123"},
                headers={'Cookie': f'session={custom_session_id}'},
                timeout=10
            )
            
            vulnerability_found = custom_session_id in response.headers.get('Set-Cookie', '')
            severity = "MEDIUM" if vulnerability_found else "LOW"
            
            results.append(SecurityTestResult(
                test_name="Session Fixation",
                endpoint="/api/v1/auth/login",
                payload=custom_session_id,
                success=True,
                vulnerability_found=vulnerability_found,
                severity=severity,
                description="Test de session fixation",
                response_code=response.status_code
            ))
            
        except Exception as e:
            results.append(SecurityTestResult(
                test_name="Session Fixation",
                endpoint="/api/v1/auth/login",
                payload=custom_session_id,
                success=False,
                vulnerability_found=False,
                severity="UNKNOWN",
                description=f"Error en test: {str(e)}",
                details=str(e)
            ))
        
        self.logger.info(f"✅ Tests de autenticación completados: {len(results)} tests")
        return results
    
    def test_authorization(self) -> List[SecurityTestResult]:
        """Test de vulnerabilidades de autorización"""
        self.logger.info("🛡️  Iniciando tests de autorización")
        
        results = []
        
        # Test 1: Acceso a recursos de otros usuarios
        protected_endpoints = [
            '/api/v1/stats/business',
            '/api/v1/reports/sales/summary',
            '/api/v1/search/users'
        ]
        
        for endpoint in protected_endpoints:
            start_time = time.time()
            
            try:
                # Intentar acceder sin autenticación
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    headers={},  # Sin headers de autenticación
                    timeout=10
                )
                
                response_time = (time.time() - start_time) * 1000
                
                # Si permite acceso sin autenticación, es una vulnerabilidad
                vulnerability_found = response.status_code == 200
                severity = "HIGH" if vulnerability_found else "LOW"
                
                results.append(SecurityTestResult(
                    test_name="Authorization Bypass",
                    endpoint=endpoint,
                    payload="No authentication",
                    success=True,
                    vulnerability_found=vulnerability_found,
                    severity=severity,
                    description="Test de bypass de autorización",
                    response_code=response.status_code,
                    response_time=response_time
                ))
                
            except Exception as e:
                results.append(SecurityTestResult(
                    test_name="Authorization Bypass",
                    endpoint=endpoint,
                    payload="No authentication",
                    success=False,
                    vulnerability_found=False,
                    severity="UNKNOWN",
                    description=f"Error en test: {str(e)}",
                    details=str(e)
                ))
        
        # Test 2: Modificación de recursos de otros usuarios
        if self.auth_token:
            modification_tests = [
                ('/api/v1/auth/register', 'POST', {"username": "hacker", "password": "hack123", "email": "hack@test.com"}),
            ]
            
            for endpoint, method, data in modification_tests:
                start_time = time.time()
                
                try:
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json=data,
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    # Analizar respuesta
                    vulnerability_found = response.status_code == 200
                    severity = "MEDIUM" if vulnerability_found else "LOW"
                    
                    results.append(SecurityTestResult(
                        test_name="Unauthorized Modification",
                        endpoint=endpoint,
                        payload=str(data),
                        success=True,
                        vulnerability_found=vulnerability_found,
                        severity=severity,
                        description="Test de modificación no autorizada",
                        response_code=response.status_code,
                        response_time=response_time
                    ))
                    
                except Exception as e:
                    results.append(SecurityTestResult(
                        test_name="Unauthorized Modification",
                        endpoint=endpoint,
                        payload=str(data),
                        success=False,
                        vulnerability_found=False,
                        severity="UNKNOWN",
                        description=f"Error en test: {str(e)}",
                        details=str(e)
                    ))
        
        self.logger.info(f"✅ Tests de autorización completados: {len(results)} tests")
        return results
    
    def generate_security_report(self, all_results: List[SecurityTestResult], 
                               output_file: str = None) -> str:
        """Generar reporte de seguridad"""
        # Calcular estadísticas
        total_tests = len(all_results)
        successful_tests = sum(1 for r in all_results if r.success)
        vulnerabilities_found = sum(1 for r in all_results if r.vulnerability_found)
        
        # Agrupar por severidad
        severity_counts = {
            'HIGH': sum(1 for r in all_results if r.severity == 'HIGH'),
            'MEDIUM': sum(1 for r in all_results if r.severity == 'MEDIUM'),
            'LOW': sum(1 for r in all_results if r.severity == 'LOW'),
            'UNKNOWN': sum(1 for r in all_results if r.severity == 'UNKNOWN')
        }
        
        # Calcular score de seguridad
        security_score = max(0, 100 - (severity_counts['HIGH'] * 20 + severity_counts['MEDIUM'] * 10 + severity_counts['LOW'] * 2))
        
        report = {
            'test_summary': {
                'timestamp': datetime.now().isoformat(),
                'base_url': self.base_url,
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'vulnerabilities_found': vulnerabilities_found,
                'security_score': security_score
            },
            'severity_breakdown': severity_counts,
            'detailed_results': [
                {
                    'test_name': r.test_name,
                    'endpoint': r.endpoint,
                    'payload': r.payload,
                    'vulnerability_found': r.vulnerability_found,
                    'severity': r.severity,
                    'description': r.description,
                    'response_code': r.response_code,
                    'response_time': r.response_time,
                    'details': r.details
                } for r in all_results
            ],
            'recommendations': []
        }
        
        # Generar recomendaciones
        if severity_counts['HIGH'] > 0:
            report['recommendations'].append("🚨 CRÍTICO: Se encontraron vulnerabilidades de alta severidad. Corrección inmediata requerida.")
        
        if severity_counts['MEDIUM'] > 0:
            report['recommendations'].append("⚠️  Se encontraron vulnerabilidades de severidad media. Revisar y corregir.")
        
        if vulnerabilities_found == 0:
            report['recommendations'].append("✅ No se encontraron vulnerabilidades evidentes en los tests realizados.")
        
        report['recommendations'].extend([
            "🔒 Implementar headers de seguridad (CSP, HSTS, etc.)",
            "🛡️  Configurar rate limiting adecuado",
            "🔐 Validar y sanitizar todas las entradas",
            "📝 Implementar logging de seguridad detallado",
            "🔄 Realizar tests de seguridad regularmente"
        ])
        
        # Guardar reporte
        report_json = json.dumps(report, indent=2, ensure_ascii=False)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_json)
            self.logger.info(f"📄 Reporte guardado en: {output_file}")
        
        return report_json
    
    def run_comprehensive_security_test(self) -> List[SecurityTestResult]:
        """Ejecutar suite completa de tests de seguridad"""
        self.logger.info("🚀 Iniciando suite completa de tests de seguridad")
        self.logger.info("=" * 60)
        
        all_results = []
        
        # Autenticarse primero
        self.authenticate()
        
        # 1. Tests de SQL Injection
        self.logger.info("1️⃣  SQL Injection Tests")
        sql_results = self.test_sql_injection()
        all_results.extend(sql_results)
        
        # 2. Tests de XSS
        self.logger.info("2️⃣  XSS Tests")
        xss_results = self.test_xss()
        all_results.extend(xss_results)
        
        # 3. Tests de CSRF
        self.logger.info("3️⃣  CSRF Tests")
        csrf_results = self.test_csrf()
        all_results.extend(csrf_results)
        
        # 4. Tests de Rate Limiting
        self.logger.info("4️⃣  Rate Limiting Tests")
        rate_limit_results = self.test_rate_limiting()
        all_results.extend(rate_limit_results)
        
        # 5. Tests de Autenticación
        self.logger.info("5️⃣  Authentication Tests")
        auth_results = self.test_authentication()
        all_results.extend(auth_results)
        
        # 6. Tests de Autorización
        self.logger.info("6️⃣  Authorization Tests")
        authz_results = self.test_authorization()
        all_results.extend(authz_results)
        
        self.logger.info("✅ Suite completa de tests de seguridad completada")
        return all_results


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Tests de Seguridad para O'Data POS v2.0.0"
    )
    
    parser.add_argument(
        '--url',
        default='http://localhost:8000',
        help='URL base del servidor (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--test-type',
        choices=['sql', 'xss', 'csrf', 'rate-limit', 'auth', 'authz', 'comprehensive'],
        default='comprehensive',
        help='Tipo de test a ejecutar'
    )
    
    parser.add_argument(
        '--output',
        help='Archivo de salida para el reporte'
    )
    
    args = parser.parse_args()
    
    # Crear tester
    tester = SecurityTester(args.url)
    
    # Ejecutar test según el tipo
    if args.test_type == 'sql':
        results = tester.test_sql_injection()
    elif args.test_type == 'xss':
        results = tester.test_xss()
    elif args.test_type == 'csrf':
        results = tester.test_csrf()
    elif args.test_type == 'rate-limit':
        results = tester.test_rate_limiting()
    elif args.test_type == 'auth':
        results = tester.test_authentication()
    elif args.test_type == 'authz':
        results = tester.test_authorization()
    else:  # comprehensive
        results = tester.run_comprehensive_security_test()
    
    # Generar reporte
    output_file = args.output or f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report = tester.generate_security_report(results, output_file)
    
    # Mostrar resumen
    vulnerabilities = sum(1 for r in results if r.vulnerability_found)
    high_severity = sum(1 for r in results if r.severity == 'HIGH')
    
    print("\n" + "=" * 60)
    print("🛡️  RESUMEN DE SEGURIDAD")
    print("=" * 60)
    print(f"Total de tests: {len(results)}")
    print(f"Vulnerabilidades encontradas: {vulnerabilities}")
    print(f"Vulnerabilidades críticas: {high_severity}")
    
    if high_severity > 0:
        print("🚨 ATENCIÓN: Se encontraron vulnerabilidades críticas!")
    elif vulnerabilities > 0:
        print("⚠️  Se encontraron algunas vulnerabilidades menores")
    else:
        print("✅ No se encontraron vulnerabilidades evidentes")
    
    print(f"\n📄 Reporte completo guardado en: {output_file}")
    print("✅ Tests de seguridad completados!")


if __name__ == "__main__":
    main()
