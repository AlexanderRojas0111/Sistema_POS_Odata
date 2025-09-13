"""
Support Ticket Model - Sistema POS Sabrositas
============================================
Modelo para gestión de tickets de soporte.
"""

from app import db
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

class SupportTicket(db.Model):
    """Modelo de ticket de soporte"""
    
    __tablename__ = 'support_tickets'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    ticket_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Información del ticket
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    category = db.Column(db.String(50), nullable=False)  # technical, billing, general, feature_request
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    
    # Usuario y asignación
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Información de contacto
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    messages = db.relationship('SupportMessage', backref='ticket', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        """Constructor con validaciones"""
        # Generar número de ticket
        self.ticket_number = self._generate_ticket_number()
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_ticket_number(self) -> str:
        """Generar número de ticket único"""
        # Formato: TK + Año + Mes + Secuencial (ej: TK2025010001)
        now = datetime.utcnow()
        prefix = f"TK{now.year}{now.month:02d}"
        
        # Buscar último número de la serie
        last_ticket = SupportTicket.query.filter(
            SupportTicket.ticket_number.like(f"{prefix}%")
        ).order_by(SupportTicket.ticket_number.desc()).first()
        
        if last_ticket:
            last_number = int(last_ticket.ticket_number[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'ticket_number': self.ticket_number,
            'subject': self.subject,
            'description': self.description,
            'priority': self.priority,
            'category': self.category,
            'status': self.status,
            'user_id': self.user_id,
            'assigned_to': self.assigned_to,
            'contact_name': self.contact_name,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'messages_count': len(self.messages) if self.messages else 0
        }
    
    def __repr__(self) -> str:
        return f'<SupportTicket {self.ticket_number}: {self.subject}>'

class SupportMessage(db.Model):
    """Modelo de mensaje de soporte"""
    
    __tablename__ = 'support_messages'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'), nullable=False)
    
    # Contenido del mensaje
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, file, system
    is_internal = db.Column(db.Boolean, default=False)
    
    # Usuario que envió el mensaje
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_email = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, ticket_id: int, **kwargs):
        """Constructor con validaciones"""
        self.ticket_id = ticket_id
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'message': self.message,
            'message_type': self.message_type,
            'is_internal': self.is_internal,
            'user_id': self.user_id,
            'sender_name': self.sender_name,
            'sender_email': self.sender_email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<SupportMessage {self.id}: {self.message[:50]}...>'

class SupportChat(db.Model):
    """Modelo de chat de soporte en tiempo real"""
    
    __tablename__ = 'support_chats'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Información del chat
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Estado del chat
    status = db.Column(db.String(20), default='waiting')  # waiting, active, ended
    priority = db.Column(db.String(20), default='medium')
    
    # Información de contacto
    visitor_name = db.Column(db.String(100), nullable=True)
    visitor_email = db.Column(db.String(100), nullable=True)
    visitor_phone = db.Column(db.String(20), nullable=True)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    messages = db.relationship('ChatMessage', backref='chat', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        """Constructor con validaciones"""
        # Asignar campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'user_id': self.user_id,
            'agent_id': self.agent_id,
            'status': self.status,
            'priority': self.priority,
            'visitor_name': self.visitor_name,
            'visitor_email': self.visitor_email,
            'visitor_phone': self.visitor_phone,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'messages_count': len(self.messages) if self.messages else 0
        }
    
    def __repr__(self) -> str:
        return f'<SupportChat {self.uuid}: {self.status}>'

class ChatMessage(db.Model):
    """Modelo de mensaje de chat"""
    
    __tablename__ = 'chat_messages'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('support_chats.id'), nullable=False)
    
    # Contenido del mensaje
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, file, system
    sender_type = db.Column(db.String(20), nullable=False)  # user, agent, system
    
    # Usuario que envió el mensaje
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    sender_name = db.Column(db.String(100), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, chat_id: int, **kwargs):
        """Constructor con validaciones"""
        self.chat_id = chat_id
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'message': self.message,
            'message_type': self.message_type,
            'sender_type': self.sender_type,
            'user_id': self.user_id,
            'sender_name': self.sender_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<ChatMessage {self.id}: {self.message[:30]}...>'
