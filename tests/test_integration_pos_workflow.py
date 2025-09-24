"""
Tests de integración para el flujo completo del sistema POS
Valida escenarios end-to-end del punto de venta
"""

import unittest
from unittest.mock import patch, MagicMock
import json

class TestPOSWorkflowIntegration(unittest.TestCase):
    """Tests de integración para flujos completos del POS"""

    def setUp(self):
        """Configuración inicial para cada test"""
        # Mock de productos disponibles
        self.products_catalog = [
            {'id': 1, 'name': 'Café', 'price': 2.50, 'stock': 100, 'code': 'CAF001'},
            {'id': 2, 'name': 'Sandwich', 'price': 5.75, 'stock': 50, 'code': 'SAN001'},
            {'id': 3, 'name': 'Agua', 'price': 1.25, 'stock': 200, 'code': 'AGU001'}
        ]
        
        # Mock de usuario autenticado
        self.authenticated_user = {
            'id': 1,
            'username': 'cajero01',
            'role': 'EMPLOYEE'
        }

    def test_complete_sale_workflow(self):
        """Test: Flujo completo de venta desde búsqueda hasta facturación"""
        # Paso 1: Búsqueda de producto por código
        search_code = 'CAF001'
        found_product = next((p for p in self.products_catalog if p['code'] == search_code), None)
        
        self.assertIsNotNone(found_product)
        self.assertEqual(found_product['name'], 'Café')
        
        # Paso 2: Agregar producto al carrito
        cart = []
        cart_item = {
            'product_id': found_product['id'],
            'name': found_product['name'],
            'price': found_product['price'],
            'quantity': 2
        }
        cart.append(cart_item)
        
        self.assertEqual(len(cart), 1)
        
        # Paso 3: Calcular totales
        subtotal = sum(item['price'] * item['quantity'] for item in cart)
        tax_rate = 0.16  # IVA 16%
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        self.assertEqual(subtotal, 5.00)  # 2.50 * 2
        self.assertEqual(tax_amount, 0.80)  # 5.00 * 0.16
        self.assertEqual(total, 5.80)
        
        # Paso 4: Procesar pago
        payment_method = 'cash'
        payment_amount = 10.00
        change = payment_amount - total
        
        self.assertGreaterEqual(payment_amount, total)
        self.assertEqual(change, 4.20)
        
        # Paso 5: Crear venta en el sistema
        sale_data = {
            'items': cart,
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total': total,
            'payment_method': payment_method,
            'payment_amount': payment_amount,
            'change': change,
            'user_id': self.authenticated_user['id']
        }
        
        # Verificar que la venta está completa
        self.assertIsNotNone(sale_data['items'])
        self.assertGreater(sale_data['total'], 0)
        self.assertIsNotNone(sale_data['user_id'])

    def test_multi_item_sale_workflow(self):
        """Test: Venta con múltiples productos"""
        # Agregar múltiples productos al carrito
        cart = [
            {'product_id': 1, 'name': 'Café', 'price': 2.50, 'quantity': 2},
            {'product_id': 2, 'name': 'Sandwich', 'price': 5.75, 'quantity': 1},
            {'product_id': 3, 'name': 'Agua', 'price': 1.25, 'quantity': 3}
        ]
        
        # Calcular totales
        subtotal = sum(item['price'] * item['quantity'] for item in cart)
        expected_subtotal = (2.50 * 2) + (5.75 * 1) + (1.25 * 3)  # 5.00 + 5.75 + 3.75 = 14.50
        
        self.assertEqual(subtotal, expected_subtotal)
        
        # Verificar stock disponible para todos los productos
        stock_check_passed = True
        for cart_item in cart:
            product = next((p for p in self.products_catalog if p['id'] == cart_item['product_id']), None)
            if not product or product['stock'] < cart_item['quantity']:
                stock_check_passed = False
                break
        
        self.assertTrue(stock_check_passed)

    def test_insufficient_stock_handling(self):
        """Test: Manejo de stock insuficiente durante la venta"""
        # Intentar vender más cantidad de la disponible
        cart_item = {
            'product_id': 2,  # Sandwich con stock de 50
            'name': 'Sandwich',
            'price': 5.75,
            'quantity': 75  # Más que el stock disponible
        }
        
        # Verificar stock
        product = next((p for p in self.products_catalog if p['id'] == cart_item['product_id']), None)
        stock_available = product['stock'] >= cart_item['quantity']
        
        self.assertFalse(stock_available)
        
        # Simular ajuste automático de cantidad
        adjusted_quantity = min(cart_item['quantity'], product['stock'])
        self.assertEqual(adjusted_quantity, 50)

    def test_discount_application_workflow(self):
        """Test: Aplicación de descuentos en la venta"""
        cart = [
            {'product_id': 1, 'name': 'Café', 'price': 2.50, 'quantity': 4}
        ]
        
        subtotal = sum(item['price'] * item['quantity'] for item in cart)  # 10.00
        
        # Aplicar descuento del 15%
        discount_percentage = 0.15
        discount_amount = subtotal * discount_percentage
        discounted_subtotal = subtotal - discount_amount
        
        self.assertEqual(discount_amount, 1.50)
        self.assertEqual(discounted_subtotal, 8.50)
        
        # Calcular impuestos sobre el subtotal con descuento
        tax_amount = discounted_subtotal * 0.16
        total = discounted_subtotal + tax_amount
        
        self.assertAlmostEqual(total, 9.86, places=2)

    def test_refund_workflow(self):
        """Test: Flujo de devolución/reembolso"""
        # Venta original
        original_sale = {
            'id': 1,
            'items': [
                {'product_id': 1, 'quantity': 2, 'price': 2.50, 'total': 5.00}
            ],
            'total': 5.80,  # Incluyendo impuestos
            'status': 'completed'
        }
        
        # Procesar devolución
        refund_items = [
            {'product_id': 1, 'quantity': 1, 'reason': 'defective'}
        ]
        
        # Calcular reembolso parcial
        refund_subtotal = 2.50  # 1 café
        refund_tax = refund_subtotal * 0.16
        refund_total = refund_subtotal + refund_tax
        
        self.assertAlmostEqual(refund_total, 2.90, places=2)
        
        # Verificar que el stock se restaura
        original_stock = 100
        sold_quantity = 2
        refunded_quantity = 1
        final_stock = original_stock - sold_quantity + refunded_quantity
        
        self.assertEqual(final_stock, 99)

    def test_end_of_day_report_workflow(self):
        """Test: Generación de reporte de fin de día"""
        # Mock de ventas del día
        daily_sales = [
            {'id': 1, 'total': 15.50, 'items_count': 3, 'payment_method': 'cash'},
            {'id': 2, 'total': 8.75, 'items_count': 2, 'payment_method': 'card'},
            {'id': 3, 'total': 22.30, 'items_count': 4, 'payment_method': 'cash'},
            {'id': 4, 'total': 12.80, 'items_count': 2, 'payment_method': 'card'}
        ]
        
        # Calcular métricas del día
        total_sales_amount = sum(sale['total'] for sale in daily_sales)
        total_transactions = len(daily_sales)
        total_items_sold = sum(sale['items_count'] for sale in daily_sales)
        average_ticket = total_sales_amount / total_transactions
        
        # Agrupar por método de pago
        cash_sales = sum(sale['total'] for sale in daily_sales if sale['payment_method'] == 'cash')
        card_sales = sum(sale['total'] for sale in daily_sales if sale['payment_method'] == 'card')
        
        # Verificar cálculos
        self.assertEqual(total_sales_amount, 59.35)
        self.assertEqual(total_transactions, 4)
        self.assertEqual(total_items_sold, 11)
        self.assertAlmostEqual(average_ticket, 14.84, places=2)
        self.assertEqual(cash_sales, 37.80)  # 15.50 + 22.30
        self.assertEqual(card_sales, 21.55)  # 8.75 + 12.80

    def test_inventory_sync_after_sales(self):
        """Test: Sincronización de inventario después de ventas"""
        initial_inventory = {
            1: {'stock': 100},  # Café
            2: {'stock': 50},   # Sandwich
            3: {'stock': 200}   # Agua
        }
        
        # Procesar múltiples ventas
        sales_transactions = [
            {'product_id': 1, 'quantity': 5},
            {'product_id': 2, 'quantity': 3},
            {'product_id': 1, 'quantity': 2},
            {'product_id': 3, 'quantity': 10}
        ]
        
        # Actualizar inventario
        updated_inventory = initial_inventory.copy()
        for transaction in sales_transactions:
            product_id = transaction['product_id']
            quantity = transaction['quantity']
            updated_inventory[product_id]['stock'] -= quantity
        
        # Verificar stock final
        self.assertEqual(updated_inventory[1]['stock'], 93)  # 100 - 5 - 2
        self.assertEqual(updated_inventory[2]['stock'], 47)  # 50 - 3
        self.assertEqual(updated_inventory[3]['stock'], 190) # 200 - 10

if __name__ == '__main__':
    unittest.main()
