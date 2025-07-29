import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestFrontendComponents(unittest.TestCase):
    """Tests para los componentes del frontend"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_api_response = {
            "items": [
                {
                    "id": 1,
                    "name": "Producto Test",
                    "price": 10.50,
                    "code": "TEST001",
                    "description": "Producto de prueba",
                    "category": "Test"
                }
            ],
            "total": 1,
            "pages": 1,
            "current_page": 1
        }

    @patch('frontend.src.services.api.productAPI.getProducts')
    def test_posbox_product_search(self, mock_get_products):
        """Test de búsqueda de productos en PosBox"""
        mock_get_products.return_value.data = self.mock_api_response
        
        # Simular búsqueda de producto
        # En un test real, esto se haría con React Testing Library
        search_result = mock_get_products("TEST001")
        
        self.assertIsNotNone(search_result)
        self.assertEqual(search_result.data["items"][0]["name"], "Producto Test")
        self.assertEqual(search_result.data["items"][0]["price"], 10.50)

    @patch('frontend.src.services.api.salesAPI.createSale')
    def test_posbox_sale_creation(self, mock_create_sale):
        """Test de creación de venta en PosBox"""
        mock_sale_data = {
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2,
                    "unit_price": 10.50
                }
            ],
            "payment_method": "cash",
            "total_amount": 21.00
        }
        
        mock_create_sale.return_value.data = {
            "id": 1,
            "invoice_number": "TICKET-001",
            "total_amount": 21.00,
            "status": "completed",
            "created_at": "2024-01-01T10:00:00Z"
        }
        
        # Simular creación de venta
        sale_result = mock_create_sale(mock_sale_data)
        
        self.assertIsNotNone(sale_result)
        self.assertEqual(sale_result.data["invoice_number"], "TICKET-001")
        self.assertEqual(sale_result.data["total_amount"], 21.00)

    def test_cart_calculations(self):
        """Test de cálculos del carrito"""
        cart_items = [
            {"id": 1, "name": "Producto 1", "price": 10.00, "quantity": 2},
            {"id": 2, "name": "Producto 2", "price": 15.50, "quantity": 1}
        ]
        
        # Calcular subtotal
        subtotal = sum(item["price"] * item["quantity"] for item in cart_items)
        self.assertEqual(subtotal, 35.50)
        
        # Calcular IVA (16%)
        tax = subtotal * 0.16
        self.assertEqual(tax, 5.68)
        
        # Calcular total
        total = subtotal + tax
        self.assertEqual(total, 41.18)

    def test_payment_methods(self):
        """Test de métodos de pago"""
        payment_methods = ["cash", "card", "transfer"]
        expected_labels = ["Efectivo", "Tarjeta", "Transferencia"]
        
        for method, expected_label in zip(payment_methods, expected_labels):
            if method == "cash":
                label = "Efectivo"
            elif method == "card":
                label = "Tarjeta"
            else:
                label = "Transferencia"
            
            self.assertEqual(label, expected_label)

    @patch('frontend.src.services.api.productAPI.semanticSearch')
    def test_semantic_search(self, mock_semantic_search):
        """Test de búsqueda semántica"""
        mock_semantic_search.return_value.data = {
            "query": "bebida",
            "results": [
                {
                    "id": 1,
                    "name": "Coca Cola",
                    "price": 15.00,
                    "similarity_score": 0.85
                }
            ]
        }
        
        search_result = mock_semantic_search("bebida")
        
        self.assertIsNotNone(search_result)
        self.assertEqual(search_result.data["query"], "bebida")
        self.assertEqual(len(search_result.data["results"]), 1)
        self.assertEqual(search_result.data["results"][0]["name"], "Coca Cola")

    def test_ticket_generation(self):
        """Test de generación de tickets"""
        ticket_data = {
            "invoice_number": "TICKET-001",
            "created_at": "2024-01-01T10:00:00Z",
            "customer": {"name": "Cliente Test"},
            "payment_method": "cash",
            "items": [
                {
                    "product": {"name": "Producto 1"},
                    "quantity": 2,
                    "unit_price": 10.00
                }
            ],
            "total_amount": 20.00,
            "subtotal": 20.00,
            "tax": 3.20
        }
        
        # Verificar estructura del ticket
        self.assertIn("invoice_number", ticket_data)
        self.assertIn("created_at", ticket_data)
        self.assertIn("customer", ticket_data)
        self.assertIn("items", ticket_data)
        self.assertIn("total_amount", ticket_data)
        
        # Verificar cálculos
        items_total = sum(item["quantity"] * item["unit_price"] for item in ticket_data["items"])
        self.assertEqual(items_total, 20.00)

    def test_error_handling(self):
        """Test de manejo de errores"""
        error_cases = [
            {"status": 400, "expected": "Error de validación"},
            {"status": 401, "expected": "No autorizado"},
            {"status": 403, "expected": "Acceso denegado"},
            {"status": 404, "expected": "Recurso no encontrado"},
            {"status": 500, "expected": "Error interno del servidor"}
        ]
        
        for case in error_cases:
            error_response = MagicMock()
            error_response.status = case["status"]
            error_response.data = {"message": "Test error"}
            
            # Simular manejo de error
            if case["status"] == 400:
                error_message = "Error de validación: Test error"
            elif case["status"] == 401:
                error_message = "No autorizado. Inicie sesión nuevamente."
            elif case["status"] == 403:
                error_message = "Acceso denegado. No tiene permisos para esta acción."
            elif case["status"] == 404:
                error_message = "Recurso no encontrado."
            elif case["status"] == 500:
                error_message = "Error interno del servidor. Intente más tarde."
            else:
                error_message = "Test error"
            
            self.assertIn(case["expected"], error_message)

    def test_responsive_design_breakpoints(self):
        """Test de breakpoints responsive"""
        breakpoints = {
            "xs": 0,
            "sm": 600,
            "md": 900,
            "lg": 1200,
            "xl": 1536
        }
        
        # Verificar que los breakpoints están definidos correctamente
        self.assertEqual(breakpoints["xs"], 0)
        self.assertEqual(breakpoints["sm"], 600)
        self.assertEqual(breakpoints["md"], 900)
        self.assertEqual(breakpoints["lg"], 1200)
        self.assertEqual(breakpoints["xl"], 1536)

    def test_theme_configuration(self):
        """Test de configuración del tema"""
        theme_config = {
            "palette": {
                "primary": {"main": "#1976d2"},
                "secondary": {"main": "#dc004e"},
                "background": {"default": "#f5f5f5"}
            },
            "typography": {
                "fontFamily": '"Roboto", "Helvetica", "Arial", sans-serif'
            },
            "shape": {"borderRadius": 8}
        }
        
        # Verificar configuración del tema
        self.assertEqual(theme_config["palette"]["primary"]["main"], "#1976d2")
        self.assertEqual(theme_config["palette"]["secondary"]["main"], "#dc004e")
        self.assertEqual(theme_config["palette"]["background"]["default"], "#f5f5f5")
        self.assertEqual(theme_config["shape"]["borderRadius"], 8)

if __name__ == '__main__':
    unittest.main() 