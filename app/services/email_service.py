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
