from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from dataclasses import dataclass, asdict
import uuid

@dataclass
class MCPContext:
    """Contexto compartido entre modelos"""
    session_id: str
    user_id: Optional[str]
    timestamp: str
    metadata: Dict[str, Any]
    
    @classmethod
    def create(cls, user_id: Optional[str] = None, metadata: Dict[str, Any] = None):
        return cls(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata or {}
        )

@dataclass
class MCPMessage:
    """Mensaje del protocolo MCP"""
    message_id: str
    source_model: str
    target_model: str
    context: MCPContext
    content: Dict[str, Any]
    created_at: str
    
    @classmethod
    def create(cls, source_model: str, target_model: str, 
               context: MCPContext, content: Dict[str, Any]):
        return cls(
            message_id=str(uuid.uuid4()),
            source_model=source_model,
            target_model=target_model,
            context=context,
            content=content,
            created_at=datetime.utcnow().isoformat()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'context': asdict(self.context)
        }

class MCPProtocol:
    def __init__(self):
        self.message_history: List[MCPMessage] = []
    
    def create_message(self, source_model: str, target_model: str,
                      content: Dict[str, Any], context: Optional[MCPContext] = None) -> MCPMessage:
        """Crea un nuevo mensaje MCP"""
        if context is None:
            context = MCPContext.create()
            
        message = MCPMessage.create(
            source_model=source_model,
            target_model=target_model,
            context=context,
            content=content
        )
        
        self.message_history.append(message)
        return message
    
    def get_session_history(self, session_id: str) -> List[MCPMessage]:
        """Obtiene el historial de mensajes para una sesión"""
        return [
            msg for msg in self.message_history
            if msg.context.session_id == session_id
        ]
    
    def get_model_messages(self, model_id: str) -> List[MCPMessage]:
        """Obtiene todos los mensajes relacionados con un modelo"""
        return [
            msg for msg in self.message_history
            if msg.source_model == model_id or msg.target_model == model_id
        ]
    
    def clear_history(self, session_id: Optional[str] = None) -> None:
        """Limpia el historial de mensajes"""
        if session_id:
            self.message_history = [
                msg for msg in self.message_history
                if msg.context.session_id != session_id
            ]
        else:
            self.message_history.clear() 