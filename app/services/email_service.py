"""
Email Service - Sistema POS Sabrositas
=====================================
Servicio para envío de emails de soporte y notificaciones.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import logging
import os
from datetime import datetime
from jinja2 import Template

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio de envío de emails"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.from_name = os.getenv('FROM_NAME', 'Sistema POS Sabrositas')
        
    def send_email(self, to_email: str, subject: str, body: str, 
                   is_html: bool = False, attachments: List[str] = None) -> bool:
        """Enviar email"""
        try:
            # Crear mensaje
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.from_name} <{self.email_user}>"
            message['To'] = to_email
            message['Subject'] = subject
            
            # Agregar cuerpo del mensaje
            if is_html:
                message.attach(MIMEText(body, 'html'))
            else:
                message.attach(MIMEText(body, 'plain'))
            
            # Agregar archivos adjuntos
            if attachments:
                for attachment_path in attachments:
                    self._attach_file(message, attachment_path)
            
            # Crear conexión segura y enviar email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_user, self.email_password)
                server.sendmail(self.email_user, to_email, message.as_string())
            
            logger.info(f"Email enviado exitosamente a {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {str(e)}")
            return False
    
    def _attach_file(self, message: MIMEMultipart, file_path: str):
        """Agregar archivo adjunto al mensaje"""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(file_path)}'
            )
            message.attach(part)
            
        except Exception as e:
            logger.error(f"Error agregando archivo adjunto: {str(e)}")
    
    def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Enviar email de bienvenida"""
        subject = "¡Bienvenido a Sistema POS Sabrositas!"
        
        body = f"""
        Hola {user_name},
        
        ¡Bienvenido a Sistema POS Sabrositas!
        
        Tu cuenta ha sido creada exitosamente. Ahora puedes acceder al sistema con tus credenciales.
        
        Si tienes alguna pregunta o necesitas ayuda, no dudes en contactarnos.
        
        Saludos,
        Equipo de Soporte - Sistema POS Sabrositas
        """
        
        return self.send_email(user_email, subject, body)
    
    def send_support_ticket_email(self, ticket_number: str, user_email: str, 
                                user_name: str, subject: str) -> bool:
        """Enviar email de confirmación de ticket"""
        email_subject = f"Ticket de Soporte Creado: {ticket_number}"
        
        body = f"""
        Hola {user_name},
        
        Hemos recibido tu solicitud de soporte:
        
        Ticket: {ticket_number}
        Asunto: {subject}
        
        Nuestro equipo de soporte revisará tu solicitud y te contactará pronto.
        
        Puedes consultar el estado de tu ticket en cualquier momento.
        
        Saludos,
        Equipo de Soporte - Sistema POS Sabrositas
        """
        
        return self.send_email(user_email, email_subject, body)
    
    def send_ticket_update_email(self, ticket_number: str, user_email: str, 
                               user_name: str, update_message: str) -> bool:
        """Enviar email de actualización de ticket"""
        email_subject = f"Actualización de Ticket: {ticket_number}"
        
        body = f"""
        Hola {user_name},
        
        Hemos actualizado tu ticket de soporte:
        
        Ticket: {ticket_number}
        
        Actualización:
        {update_message}
        
        Si tienes más preguntas, puedes responder a este email.
        
        Saludos,
        Equipo de Soporte - Sistema POS Sabrositas
        """
        
        return self.send_email(user_email, email_subject, body)
    
    def send_invoice_email(self, user_email: str, user_name: str, 
                          invoice_number: str, invoice_pdf_path: str) -> bool:
        """Enviar factura por email"""
        subject = f"Factura Electrónica: {invoice_number}"
        
        body = f"""
        Hola {user_name},
        
        Adjunto encontrará su factura electrónica:
        
        Número de Factura: {invoice_number}
        
        Esta factura es válida fiscalmente y ha sido enviada a la DIAN.
        
        Gracias por su compra.
        
        Saludos,
        Sistema POS Sabrositas
        """
        
        return self.send_email(user_email, subject, body, attachments=[invoice_pdf_path])
    
    def send_sale_invoice(self, sale_data: Dict[str, Any]) -> bool:
        """Enviar factura de venta por email"""
        try:
            customer_email = sale_data.get('customer_email')
            if not customer_email:
                logger.warning("No se puede enviar factura: email del cliente no proporcionado")
                return False
            
            # MODO SIMULACIÓN: Si no hay credenciales reales, simular envío exitoso
            if not self.email_user or not self.email_password or self.email_password == 'demo-password':
                logger.info(f"MODO SIMULACIÓN: Factura 'enviada' a {customer_email}")
                logger.info(f"  📋 ID Venta: {sale_data.get('id', 'N/A')}")
                logger.info(f"  👤 Cliente: {sale_data.get('customer_name', 'Cliente')}")
                logger.info(f"  💰 Total: ${sale_data.get('total_amount', 0):,.0f}")
                logger.info(f"  💳 Método: {sale_data.get('payment_method', 'N/A')}")
                return True
            
            # Cargar plantilla HTML
            template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'invoice_email.html')
            
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
            except FileNotFoundError:
                logger.error(f"Plantilla de factura no encontrada: {template_path}")
                return False
            
            # Preparar datos para la plantilla
            payment_icons = {
                'cash': '💵',
                'card': '💳', 
                'nequi': '📱',
                'daviplata': '🟣',
                'tullave': '🔑'
            }
            
            payment_names = {
                'cash': 'Efectivo',
                'card': 'Tarjeta',
                'nequi': 'Nequi',
                'daviplata': 'Daviplata', 
                'tullave': 'tu llave'
            }
            
            template_data = {
                'sale_number': sale_data.get('sale_number', 'N/A'),
                'sale_date': sale_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'customer_name': sale_data.get('customer_name', 'Cliente'),
                'customer_phone': sale_data.get('customer_phone', 'N/A'),
                'payment_icon': payment_icons.get(sale_data.get('payment_method', 'cash'), '💵'),
                'payment_method_name': payment_names.get(sale_data.get('payment_method', 'cash'), 'Efectivo'),
                'items': sale_data.get('items', []),
                'subtotal': sale_data.get('subtotal', 0),
                'tax_amount': sale_data.get('tax_amount', 0),
                'tax_rate': sale_data.get('tax_rate', 0),
                'discount_amount': sale_data.get('discount_amount', 0),
                'total_amount': sale_data.get('total_amount', 0),
                'notes': sale_data.get('notes', '')
            }
            
            # Renderizar plantilla (simple replace para evitar dependencia de Jinja2)
            html_body = template_content
            for key, value in template_data.items():
                if key == 'items':
                    # Renderizar items manualmente
                    items_html = ""
                    for item in value:
                        items_html += f"""
                        <tr>
                            <td>{item.get('name', 'N/A')}</td>
                            <td>{item.get('quantity', 0)}</td>
                            <td>${item.get('unit_price', 0):,.0f}</td>
                            <td>${item.get('total', 0):,.0f}</td>
                        </tr>
                        """
                    html_body = html_body.replace('{% for item in items %}', '').replace('{% endfor %}', '')
                    html_body = html_body.replace(
                        '<tr>\n                        <td>{{ item.name }}</td>\n                        <td>{{ item.quantity }}</td>\n                        <td>${{ "{:,.0f}".format(item.unit_price) }}</td>\n                        <td>${{ "{:,.0f}".format(item.total) }}</td>\n                    </tr>',
                        items_html
                    )
                else:
                    html_body = html_body.replace('{{ ' + key + ' }}', str(value))
            
            # Limpiar condicionales simples
            if template_data['tax_amount'] <= 0:
                html_body = html_body.replace('{% if tax_amount > 0 %}', '<!--').replace('{% endif %}', '-->')
            else:
                html_body = html_body.replace('{% if tax_amount > 0 %}', '').replace('{% endif %}', '')
                
            if template_data['discount_amount'] <= 0:
                html_body = html_body.replace('{% if discount_amount > 0 %}', '<!--').replace('{% endif %}', '-->')
            else:
                html_body = html_body.replace('{% if discount_amount > 0 %}', '').replace('{% endif %}', '')
                
            if not template_data['notes']:
                html_body = html_body.replace('{% if notes %}', '<!--').replace('{% endif %}', '-->')
            else:
                html_body = html_body.replace('{% if notes %}', '').replace('{% endif %}', '')
            
            # Formatear números
            html_body = html_body.replace('{{ "{:,.0f}".format(subtotal) }}', f"{template_data['subtotal']:,.0f}")
            html_body = html_body.replace('{{ "{:,.0f}".format(tax_amount) }}', f"{template_data['tax_amount']:,.0f}")
            html_body = html_body.replace('{{ "{:,.0f}".format(discount_amount) }}', f"{template_data['discount_amount']:,.0f}")
            html_body = html_body.replace('{{ "{:,.0f}".format(total_amount) }}', f"{template_data['total_amount']:,.0f}")
            
            # Enviar email
            subject = f"🥟 Factura Sabrositas - Venta #{template_data['sale_number']}"
            
            success = self.send_email(
                to_email=customer_email,
                subject=subject,
                body=html_body,
                is_html=True
            )
            
            if success:
                logger.info(f"Factura enviada exitosamente a {customer_email} para venta {template_data['sale_number']}")
            else:
                logger.error(f"Error enviando factura a {customer_email} para venta {template_data['sale_number']}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error en send_sale_invoice: {str(e)}")
            return False
    
    def send_system_notification(self, admin_emails: List[str], 
                               notification_type: str, message: str) -> bool:
        """Enviar notificación del sistema a administradores"""
        subject = f"Notificación del Sistema: {notification_type}"
        
        body = f"""
        Notificación del Sistema POS Sabrositas
        
        Tipo: {notification_type}
        Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Mensaje:
        {message}
        
        Esta es una notificación automática del sistema.
        """
        
        success_count = 0
        for admin_email in admin_emails:
            if self.send_email(admin_email, subject, body):
                success_count += 1
        
        return success_count > 0

# Instancia global del servicio
email_service = EmailService()
