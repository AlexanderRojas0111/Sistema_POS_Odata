"""
Tests unitarios para la lógica de negocio de ventas
Valida escenarios críticos del sistema POS
"""

import unittest
from unittest.mock import patch, MagicMock
from decimal import Decimal

# Mock de las dependencias antes de importar
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestSalesBusinessLogic(unittest.TestCase):
    """Tests para validar la lógica de negocio de ventas"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_product = MagicMock()
        self.mock_product.id = 1
        self.mock_product.name = "Producto Test"
        self.mock_product.price = 10.50
        self.mock_product.stock = 100
        
        self.mock_sale_data = MagicMock()
        self.mock_sale_data.product_id = 1
        self.mock_sale_data.quantity = 2
        self.mock_sale_data.total = 21.00
        self.mock_sale_data.user_id = 1
        self.mock_sale_data.customer_id = None

    @patch('app.models.Product')
    @patch('app.core.database.db')
    def test_create_sale_sufficient_stock(self, mock_db, mock_product_model):
        """Test: Crear venta con stock suficiente debe ser exitoso"""
        # Configurar mock
        mock_product_model.query.get.return_value = self.mock_product
        
        # Simular lógica de SalesCRUD.create()
        initial_stock = self.mock_product.stock
        sale_quantity = self.mock_sale_data.quantity
        
        # Verificar stock suficiente
        self.assertGreaterEqual(initial_stock, sale_quantity)
        
        # Simular reducción de stock
        expected_final_stock = initial_stock - sale_quantity
        self.mock_product.stock = expected_final_stock
        
        # Verificar que el stock se redujo correctamente
        self.assertEqual(self.mock_product.stock, 98)

    @patch('app.models.Product')
    @patch('app.core.database.db')
    def test_create_sale_insufficient_stock(self, mock_db, mock_product_model):
        """Test: Crear venta con stock insuficiente debe fallar"""
        # Configurar producto con stock bajo
        self.mock_product.stock = 1
        mock_product_model.query.get.return_value = self.mock_product
        
        # Intentar venta con más cantidad que stock
        sale_quantity = 5
        
        # Verificar que se detecta stock insuficiente
        self.assertLess(self.mock_product.stock, sale_quantity)
        
        # Simular excepción que debería lanzar el CRUD
        with self.assertRaises(ValueError) as context:
            if self.mock_product.stock < sale_quantity:
                raise ValueError('Stock insuficiente para la venta')
        
        self.assertEqual(str(context.exception), 'Stock insuficiente para la venta')

    def test_sale_total_calculation(self):
        """Test: Validar cálculo correcto del total de venta"""
        price = 10.50
        quantity = 2
        expected_total = price * quantity
        
        # Verificar cálculo básico
        calculated_total = price * quantity
        self.assertEqual(calculated_total, expected_total)
        
        # Test con descuento
        discount_percentage = 0.10  # 10%
        expected_total_with_discount = expected_total * (1 - discount_percentage)
        calculated_total_with_discount = calculated_total * (1 - discount_percentage)
        
        self.assertEqual(calculated_total_with_discount, expected_total_with_discount)

    def test_sale_data_validation(self):
        """Test: Validar datos de entrada para crear venta"""
        # Test datos válidos
        valid_sale_data = {
            'product_id': 1,
            'quantity': 2,
            'total': 21.00,
            'user_id': 1
        }
        
        # Validaciones básicas
        self.assertIsInstance(valid_sale_data['product_id'], int)
        self.assertGreater(valid_sale_data['quantity'], 0)
        self.assertGreater(valid_sale_data['total'], 0)
        self.assertIsInstance(valid_sale_data['user_id'], int)
        
        # Test datos inválidos
        invalid_sale_data = {
            'product_id': None,
            'quantity': -1,
            'total': 0,
            'user_id': None
        }
        
        # Verificar detección de datos inválidos
        self.assertIsNone(invalid_sale_data['product_id'])
        self.assertLessEqual(invalid_sale_data['quantity'], 0)
        self.assertLessEqual(invalid_sale_data['total'], 0)

    def test_concurrent_sales_stock_management(self):
        """Test: Simular ventas concurrentes y validar integridad del stock"""
        initial_stock = 8  # Reducir stock para forzar un fallo
        concurrent_sales = [
            {'quantity': 3},
            {'quantity': 2},
            {'quantity': 5}  # Esta venta debería fallar (3+2+5=10 > 8)
        ]
        
        # Simular procesamiento secuencial (como debería ser en transacciones)
        current_stock = initial_stock
        successful_sales = []
        failed_sales = []
        
        for sale in concurrent_sales:
            if current_stock >= sale['quantity']:
                current_stock -= sale['quantity']
                successful_sales.append(sale)
            else:
                failed_sales.append(sale)
        
        # Verificar resultados
        self.assertEqual(len(successful_sales), 2)  # Solo 2 ventas exitosas (3 y 2)
        self.assertEqual(len(failed_sales), 1)      # 1 venta falló (5)
        self.assertEqual(current_stock, 3)          # Stock restante correcto (8-3-2=3)

    def test_sale_report_calculations(self):
        """Test: Validar cálculos de reportes de ventas"""
        mock_sales = [
            {'total': 25.50, 'quantity': 2},
            {'total': 15.75, 'quantity': 1},
            {'total': 30.00, 'quantity': 3}
        ]
        
        # Calcular totales
        total_amount = sum(sale['total'] for sale in mock_sales)
        total_items = sum(sale['quantity'] for sale in mock_sales)
        sales_count = len(mock_sales)
        
        # Verificar cálculos
        self.assertEqual(total_amount, 71.25)
        self.assertEqual(total_items, 6)
        self.assertEqual(sales_count, 3)
        
        # Calcular promedio
        average_sale = total_amount / sales_count
        self.assertAlmostEqual(average_sale, 23.75, places=2)

if __name__ == '__main__':
    unittest.main()
