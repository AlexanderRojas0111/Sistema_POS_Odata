"""
WhatsApp Service - Sistema POS Sabrositas
========================================
Servicio para envío de mensajes por WhatsApp.
"""

import requests
import json
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Servicio de WhatsApp Business API"""
    
    def __init__(self):
        self.api_url = "https://graph.facebook.com/v18.0"
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')
        
    def send_message(self, to_phone: str, message: str, message_type: str = 'text') -> bool:
        """Enviar mensaje por WhatsApp"""
        try:
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Limpiar número de teléfono
            clean_phone = self._clean_phone_number(to_phone)
            
            data = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": message_type
            }
            
            if message_type == 'text':
                data["text"] = {"body": message}
            elif message_type == 'template':
                data["template"] = message
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"Mensaje WhatsApp enviado exitosamente a {clean_phone}")
                return True
            else:
                logger.error(f"Error enviando mensaje WhatsApp: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando mensaje WhatsApp: {str(e)}")
            return False
    
    def _clean_phone_number(self, phone: str) -> str:
        """Limpiar y formatear número de teléfono"""
        # Remover caracteres no numéricos
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Agregar código de país si no tiene
        if not clean_phone.startswith('57'):  # Código de Colombia
            clean_phone = '57' + clean_phone
        
        return clean_phone
    
    def send_order_confirmation(self, customer_phone: str, customer_name: str, 
                              order_number: str, total_amount: float) -> bool:
        """Enviar confirmación de pedido por WhatsApp"""
        message = f"""
        🎉 ¡Hola {customer_name}!
        
        Tu pedido ha sido confirmado:
        
        📋 Número de Pedido: {order_number}
        💰 Total: ${total_amount:,.2f}
        
        Estaremos preparando tu pedido y te notificaremos cuando esté listo.
        
        ¡Gracias por elegir Sabrositas! 🍽️
        """
        
        return self.send_message(customer_phone, message)
    
    def send_invoice_notification(self, customer_phone: str, customer_name: str, 
                                invoice_number: str) -> bool:
        """Enviar notificación de factura por WhatsApp"""
        message = f"""
        📄 ¡Hola {customer_name}!
        
        Tu factura electrónica está lista:
        
        🧾 Número: {invoice_number}
        
        Puedes descargarla desde el sistema o te la enviamos por email.
        
        ¡Gracias por tu compra! 💰
        """
        
        return self.send_message(customer_phone, message)
    
    def send_support_notification(self, customer_phone: str, customer_name: str, 
                                ticket_number: str) -> bool:
        """Enviar notificación de ticket de soporte por WhatsApp"""
        message = f"""
        🎫 ¡Hola {customer_name}!
        
        Hemos recibido tu solicitud de soporte:
        
        📋 Ticket: {ticket_number}
        
        Nuestro equipo te contactará pronto para ayudarte.
        
        ¡Gracias por contactarnos! 🤝
        """
        
        return self.send_message(customer_phone, message)
    
    def send_promotion(self, customer_phone: str, customer_name: str, 
                      promotion_text: str, promotion_code: str) -> bool:
        """Enviar promoción por WhatsApp"""
        message = f"""
        🎉 ¡Hola {customer_name}!
        
        ¡Tenemos una oferta especial para ti!
        
        {promotion_text}
        
        🔑 Código: {promotion_code}
        
        ¡No te la pierdas! 🍽️
        """
        
        return self.send_message(customer_phone, message)
    
    def handle_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar webhook de WhatsApp"""
        try:
            # Procesar mensaje entrante
            entry = webhook_data.get('entry', [])
            
            for entry_item in entry:
                changes = entry_item.get('changes', [])
                
                for change in changes:
                    if change.get('field') == 'messages':
                        value = change.get('value', {})
                        messages = value.get('messages', [])
                        
                        for message in messages:
                            self._process_incoming_message(message)
            
            return {'status': 'success'}
            
        except Exception as e:
            logger.error(f"Error procesando webhook WhatsApp: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _process_incoming_message(self, message: Dict[str, Any]):
        """Procesar mensaje entrante"""
        try:
            from_phone = message.get('from')
            message_text = message.get('text', {}).get('body', '')
            message_id = message.get('id')
            
            logger.info(f"Mensaje WhatsApp recibido de {from_phone}: {message_text}")
            
            # Aquí se puede implementar lógica para procesar mensajes
            # como comandos, consultas de estado, etc.
            
        except Exception as e:
            logger.error(f"Error procesando mensaje WhatsApp: {str(e)}")

# Instancia global del servicio
whatsapp_service = WhatsAppService()
