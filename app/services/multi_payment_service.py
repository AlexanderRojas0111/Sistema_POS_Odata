"""
Multi Payment Service - Sistema POS O'Data
==========================================
Servicio para manejar pagos múltiples en ventas.
"""

from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from app.models.multi_payment import MultiPayment, PaymentDetail
from app.models.sale import Sale
from app import db
import logging

logger = logging.getLogger(__name__)

class MultiPaymentService:
    """Servicio para manejar pagos múltiples"""
    
    def __init__(self):
        self.payment_methods = {
            'cash': '💵 Efectivo',
            'card': '💳 Tarjeta',
            'nequi': '📱 Nequi',
            'nequi_qr': '📱 Nequi QR',
            'daviplata': '🟣 Daviplata',
            'daviplata_qr': '🟣 Daviplata QR',
            'qr_generic': '📲 QR Genérico',
            'tullave': '🔑 tu llave',
            'bancolombia': '🏦 Bancolombia',
            'bbva': '🏦 BBVA',
            'davivienda': '🏦 Davivienda',
            'efecty': '🏪 Efecty',
            'baloto': '🎰 Baloto',
            'gana': '🎰 Gana'
        }
    
    def get_available_payment_methods(self) -> Dict[str, str]:
        """Obtener métodos de pago disponibles"""
        return self.payment_methods.copy()
    
    def create_multi_payment(self, sale_id: int, user_id: int, total_amount: Decimal, notes: str = None) -> MultiPayment:
        """Crear un nuevo pago múltiple"""
        try:
            # Verificar que la venta existe
            sale = Sale.query.get(sale_id)
            if not sale:
                raise ValueError(f"Venta con ID {sale_id} no encontrada")
            
            # Crear el pago múltiple
            multi_payment = MultiPayment(
                sale_id=sale_id,
                user_id=user_id,
                total_amount=total_amount,
                notes=notes
            )
            
            db.session.add(multi_payment)
            db.session.flush()  # Para obtener el ID
            
            # Actualizar la venta
            sale.is_multi_payment = True
            sale.multi_payment_id = multi_payment.id
            
            db.session.commit()
            
            logger.info(f"Pago múltiple creado: {multi_payment.id} para venta {sale_id}")
            return multi_payment
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creando pago múltiple: {str(e)}")
            raise
    
    def add_payment(self, multi_payment_id: int, payment_method: str, amount: Decimal, 
                   reference: str = None, **kwargs) -> PaymentDetail:
        """Agregar un pago al pago múltiple"""
        try:
            multi_payment = MultiPayment.query.get(multi_payment_id)
            if not multi_payment:
                raise ValueError(f"Pago múltiple con ID {multi_payment_id} no encontrado")
            
            # Validar método de pago
            if payment_method not in self.payment_methods:
                raise ValueError(f"Método de pago '{payment_method}' no válido")
            
            # Agregar el detalle de pago
            payment_detail = multi_payment.add_payment_detail(
                payment_method=payment_method,
                amount=amount,
                reference=reference,
                **kwargs
            )
            
            db.session.commit()
            
            logger.info(f"Pago agregado: {payment_method} ${amount} al pago múltiple {multi_payment_id}")
            return payment_detail
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error agregando pago: {str(e)}")
            raise
    
    def remove_payment(self, multi_payment_id: int, payment_detail_id: int) -> bool:
        """Remover un pago del pago múltiple"""
        try:
            multi_payment = MultiPayment.query.get(multi_payment_id)
            if not multi_payment:
                raise ValueError(f"Pago múltiple con ID {multi_payment_id} no encontrado")
            
            success = multi_payment.remove_payment_detail(payment_detail_id)
            if success:
                db.session.commit()
                logger.info(f"Pago removido: {payment_detail_id} del pago múltiple {multi_payment_id}")
            
            return success
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removiendo pago: {str(e)}")
            raise
    
    def get_payment_summary(self, multi_payment_id: int) -> Dict[str, Any]:
        """Obtener resumen de un pago múltiple"""
        try:
            multi_payment = MultiPayment.query.get(multi_payment_id)
            if not multi_payment:
                raise ValueError(f"Pago múltiple con ID {multi_payment_id} no encontrado")
            
            return multi_payment.get_payment_summary()
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de pago: {str(e)}")
            raise
    
    def validate_payment_combination(self, payments: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Validar una combinación de pagos"""
        try:
            total_amount = Decimal('0')
            total_paid = Decimal('0')
            
            for payment in payments:
                amount = Decimal(str(payment['amount']))
                method = payment['method']
                
                if amount <= 0:
                    return False, f"El monto para {method} debe ser mayor a 0"
                
                if method not in self.payment_methods:
                    return False, f"Método de pago '{method}' no válido"
                
                total_paid += amount
            
            if 'total_amount' in payments[0]:  # Si viene el total de la venta
                total_amount = Decimal(str(payments[0]['total_amount']))
                if total_paid > total_amount:
                    return False, f"El total pagado (${total_paid}) excede el total de la venta (${total_amount})"
            
            return True, "Validación exitosa"
            
        except Exception as e:
            return False, f"Error en validación: {str(e)}"
    
    def suggest_payment_combinations(self, total_amount: Decimal, available_cash: Decimal = Decimal('0')) -> List[Dict[str, Any]]:
        """Sugerir combinaciones de pago comunes"""
        suggestions = []
        
        # Convertir a float para cálculos
        total = float(total_amount)
        cash = float(available_cash)
        
        # Sugerencia 1: Solo efectivo si hay suficiente
        if cash >= total:
            suggestions.append({
                'name': 'Solo Efectivo',
                'payments': [{'method': 'cash', 'amount': total}],
                'description': 'Pago completo en efectivo'
            })
        
        # Sugerencia 2: Efectivo + Nequi (50/50)
        if total > 10000:  # Solo para montos mayores
            half = total / 2
            suggestions.append({
                'name': 'Efectivo + Nequi',
                'payments': [
                    {'method': 'cash', 'amount': half},
                    {'method': 'nequi', 'amount': half}
                ],
                'description': 'Pago dividido entre efectivo y Nequi'
            })
        
        # Sugerencia 3: Efectivo + Tarjeta
        if total > 20000:  # Solo para montos mayores
            cash_part = min(total * 0.7, cash)  # Máximo 70% en efectivo
            card_part = total - cash_part
            suggestions.append({
                'name': 'Efectivo + Tarjeta',
                'payments': [
                    {'method': 'cash', 'amount': cash_part},
                    {'method': 'card', 'amount': card_part}
                ],
                'description': 'Mayoría en efectivo, resto en tarjeta'
            })
        
        # Sugerencia 4: Efectivo + Daviplata
        if total > 15000:
            cash_part = min(total * 0.6, cash)
            daviplata_part = total - cash_part
            suggestions.append({
                'name': 'Efectivo + Daviplata',
                'payments': [
                    {'method': 'cash', 'amount': cash_part},
                    {'method': 'daviplata', 'amount': daviplata_part}
                ],
                'description': 'Efectivo disponible + Daviplata'
            })
        
        return suggestions
    
    def calculate_change(self, total_amount: Decimal, payments: List[Dict[str, Any]]) -> Decimal:
        """Calcular el cambio a entregar"""
        total_paid = Decimal('0')
        
        for payment in payments:
            if payment['method'] == 'cash':
                total_paid += Decimal(str(payment['amount']))
        
        change = total_paid - total_amount
        return max(change, Decimal('0'))  # No puede ser negativo
    
    def get_payment_method_info(self, method: str) -> Dict[str, Any]:
        """Obtener información detallada de un método de pago"""
        info = {
            'cash': {
                'name': '💵 Efectivo',
                'description': 'Pago en efectivo',
                'requires_reference': False,
                'requires_phone': False,
                'requires_bank': False,
                'allows_change': True
            },
            'card': {
                'name': '💳 Tarjeta',
                'description': 'Pago con tarjeta de crédito/débito',
                'requires_reference': True,
                'requires_phone': False,
                'requires_bank': True,
                'allows_change': False
            },
            'nequi': {
                'name': '📱 Nequi',
                'description': 'Pago con Nequi',
                'requires_reference': True,
                'requires_phone': True,
                'requires_bank': False,
                'allows_change': False
            },
            'nequi_qr': {
                'name': '📱 Nequi QR',
                'description': 'Pago con Nequi mediante QR',
                'requires_reference': True,
                'requires_phone': False,
                'requires_bank': False,
                'allows_change': False
            },
            'daviplata': {
                'name': '🟣 Daviplata',
                'description': 'Pago con Daviplata',
                'requires_reference': True,
                'requires_phone': True,
                'requires_bank': False,
                'allows_change': False
            },
            'daviplata_qr': {
                'name': '🟣 Daviplata QR',
                'description': 'Pago con Daviplata mediante QR',
                'requires_reference': True,
                'requires_phone': False,
                'requires_bank': False,
                'allows_change': False
            },
            'qr_generic': {
                'name': '📲 QR Genérico',
                'description': 'Pago con código QR genérico',
                'requires_reference': True,
                'requires_phone': False,
                'requires_bank': False,
                'allows_change': False
            },
            'tullave': {
                'name': '🔑 tu llave',
                'description': 'Pago con tu llave',
                'requires_reference': True,
                'requires_phone': False,
                'requires_bank': False,
                'allows_change': False
            }
        }
        
        return info.get(method, {
            'name': f'🔧 {method.title()}',
            'description': f'Pago con {method}',
            'requires_reference': True,
            'requires_phone': False,
            'requires_bank': False,
            'allows_change': False
        })
