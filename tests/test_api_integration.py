import unittest
import requests
import json
import time
from unittest.mock import patch, MagicMock

class TestAPIIntegration(unittest.TestCase):
    """Tests de integración para las APIs del sistema"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.base_url = "http://localhost:5000"
        self.api_v1_base = f"{self.base_url}/api/v1"
        self.api_v2_base = f"{self.base_url}/api/v2"
        
        # Datos de prueba
        self.test_product = {
            "code": "TEST001",
            "name": "Producto de Prueba",
            "description": "Producto para testing",
            "price": 15.50,
            "category": "Test"
        }
        
        self.test_sale = {
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2,
                    "unit_price": 15.50
                }
            ],
            "payment_method": "cash",
            "total_amount": 31.00
        }

    def test_api_health_check(self):
        """Test de verificación de salud de la API"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.RequestException:
            # Si la API no está corriendo, el test pasa pero con advertencia
            self.skipTest("API no disponible para testing")

    def test_products_api_endpoints(self):
        """Test de endpoints de productos"""
        # Test GET /api/v1/products/
        try:
            response = requests.get(f"{self.api_v1_base}/products/", timeout=5)
            self.assertIn(response.status_code, [200, 404])  # 404 si no hay productos
            
            if response.status_code == 200:
                data = response.json()
                self.assertIn("items", data)
                self.assertIn("total", data)
        except requests.exceptions.RequestException:
            self.skipTest("API de productos no disponible")

    def test_sales_api_endpoints(self):
        """Test de endpoints de ventas"""
        # Test GET /api/v1/sales/
        try:
            response = requests.get(f"{self.api_v1_base}/sales/", timeout=5)
            self.assertIn(response.status_code, [200, 404])  # 404 si no hay ventas
            
            if response.status_code == 200:
                data = response.json()
                self.assertIn("items", data)
        except requests.exceptions.RequestException:
            self.skipTest("API de ventas no disponible")

    def test_semantic_search_api(self):
        """Test de búsqueda semántica"""
        try:
            response = requests.get(
                f"{self.api_v2_base}/search/semantic",
                params={"q": "bebida"},
                timeout=10
            )
            self.assertIn(response.status_code, [200, 400, 404])
            
            if response.status_code == 200:
                data = response.json()
                self.assertIn("query", data)
                self.assertIn("results", data)
        except requests.exceptions.RequestException:
            self.skipTest("API de búsqueda semántica no disponible")

    def test_hybrid_search_api(self):
        """Test de búsqueda híbrida"""
        try:
            response = requests.get(
                f"{self.api_v2_base}/search/hybrid",
                params={
                    "q": "producto",
                    "category": "Test",
                    "min_price": 10,
                    "max_price": 50
                },
                timeout=10
            )
            self.assertIn(response.status_code, [200, 400, 404])
            
            if response.status_code == 200:
                data = response.json()
                self.assertIn("query", data)
                self.assertIn("results", data)
                self.assertIn("filters", data)
        except requests.exceptions.RequestException:
            self.skipTest("API de búsqueda híbrida no disponible")

    def test_agents_api_status(self):
        """Test de estado de agentes"""
        try:
            response = requests.get(f"{self.api_v2_base}/agents/status", timeout=5)
            self.assertIn(response.status_code, [200, 404])
            
            if response.status_code == 200:
                data = response.json()
                self.assertIsInstance(data, dict)
        except requests.exceptions.RequestException:
            self.skipTest("API de agentes no disponible")

    def test_api_error_handling(self):
        """Test de manejo de errores de la API"""
        # Test de endpoint inexistente
        try:
            response = requests.get(f"{self.base_url}/api/nonexistent", timeout=5)
            self.assertEqual(response.status_code, 404)
        except requests.exceptions.RequestException:
            self.skipTest("API no disponible para testing de errores")

    def test_api_response_format(self):
        """Test de formato de respuesta de la API"""
        try:
            response = requests.get(f"{self.api_v1_base}/products/", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar estructura de respuesta paginada
                if "items" in data:
                    self.assertIsInstance(data["items"], list)
                    self.assertIsInstance(data["total"], int)
                    self.assertIsInstance(data["pages"], int)
                    self.assertIsInstance(data["current_page"], int)
        except requests.exceptions.RequestException:
            self.skipTest("API no disponible para testing de formato")

    def test_api_cors_headers(self):
        """Test de headers CORS"""
        try:
            response = requests.get(f"{self.api_v1_base}/products/", timeout=5)
            
            # Verificar headers CORS
            self.assertIn("Access-Control-Allow-Origin", response.headers)
            self.assertIn("Access-Control-Allow-Methods", response.headers)
        except requests.exceptions.RequestException:
            self.skipTest("API no disponible para testing de CORS")

    def test_api_rate_limiting(self):
        """Test de rate limiting"""
        try:
            # Hacer múltiples requests rápidos
            responses = []
            for i in range(5):
                response = requests.get(f"{self.api_v1_base}/products/", timeout=5)
                responses.append(response.status_code)
                time.sleep(0.1)  # Pequeña pausa entre requests
            
            # Verificar que no todos los requests fallan por rate limiting
            successful_requests = sum(1 for status in responses if status in [200, 404])
            self.assertGreater(successful_requests, 0)
        except requests.exceptions.RequestException:
            self.skipTest("API no disponible para testing de rate limiting")

    def test_api_content_type(self):
        """Test de content type de las respuestas"""
        try:
            response = requests.get(f"{self.api_v1_base}/products/", timeout=5)
            
            # Verificar content type
            content_type = response.headers.get("Content-Type", "")
            self.assertIn("application/json", content_type)
        except requests.exceptions.RequestException:
            self.skipTest("API no disponible para testing de content type")

    def test_api_timeout_handling(self):
        """Test de manejo de timeouts"""
        try:
            # Request con timeout muy corto
            response = requests.get(f"{self.api_v1_base}/products/", timeout=0.001)
            # Si llega aquí, el request fue exitoso (aunque improbable con timeout tan corto)
            self.assertIsInstance(response.status_code, int)
        except requests.exceptions.Timeout:
            # Timeout esperado
            pass
        except requests.exceptions.RequestException:
            self.skipTest("API no disponible para testing de timeout")

    def test_api_authentication_headers(self):
        """Test de headers de autenticación"""
        try:
            # Request sin token
            response = requests.get(f"{self.api_v1_base}/products/", timeout=5)
            
            # Para endpoints públicos, debería funcionar sin token
            self.assertIn(response.status_code, [200, 404])
            
            # Request con token inválido
            headers = {"Authorization": "Bearer invalid_token"}
            response_with_token = requests.get(
                f"{self.api_v1_base}/products/", 
                headers=headers, 
                timeout=5
            )
            
            # Debería funcionar igual para endpoints públicos
            self.assertIn(response_with_token.status_code, [200, 404])
        except requests.exceptions.RequestException:
            self.skipTest("API no disponible para testing de autenticación")

    def test_api_query_parameters(self):
        """Test de parámetros de query"""
        try:
            # Test con parámetros de paginación
            response = requests.get(
                f"{self.api_v1_base}/products/",
                params={"page": 1, "per_page": 10},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.assertIn("current_page", data)
                self.assertIn("pages", data)
        except requests.exceptions.RequestException:
            self.skipTest("API no disponible para testing de parámetros")

    def test_api_error_response_format(self):
        """Test de formato de respuesta de error"""
        try:
            # Intentar acceder a un endpoint que requiere autenticación
            response = requests.post(f"{self.api_v1_base}/products/", timeout=5)
            
            if response.status_code in [401, 403, 400]:
                data = response.json()
                # Verificar estructura de error
                self.assertIn("error", data)
                self.assertIn("message", data)
        except requests.exceptions.RequestException:
            self.skipTest("API no disponible para testing de errores")

if __name__ == '__main__':
    unittest.main() 